import logging
import json
from openai import OpenAI
from typing import List, Dict, Any, Union
from pydantic import ValidationError
import base64
from pathlib import Path
from .datas import AgentCodeUnitList,TestLocation,ConvertScriptLLMOutput,AwareUiTestListLLMOutput,ScreenState,AwareUiTest,AgentCodeUnit,NewLinksLLMOutput,NavigationLink,TestScenario,DeduplicateScenarioSuggestion,TestScenarioResultList,AppMindMapSummary,CodeUnitListWithLLMMetadata,AnalyzePageDecision,RequestResponsePair,ConsoleLogEntry,DataSource,ExecutionStepResultSummary,Bug,CodeUnit,BugCapture,ExecutionStepResult,BugCaptureWithLLMMetadata,LLMMetadata,ExistingScreenStateMap,LLMScreenDetailOutput,RecommendedNextJourney,AppMindMap,ConversionResult, PythonPlaywrightStepsResponse, ActionStepList
from enum import IntEnum
from pydantic import BaseModel
from typing import Optional
import os

logger = logging.getLogger(__name__)

async def suggest_next_journey(mind_map: AppMindMap,test_scenario_results:TestScenarioResultList,journeys_run_in_exploration: List[str],exploration_prompt: str) -> RecommendedNextJourney:
    journeys_str = "\n".join(journeys_run_in_exploration)
    prompt = f'''
        You are a planner agent for an AI QA agent. 

        # Your objective is to construct a journey for the AI QA agent to take next.

        It can be one of 3 types:
        - Either, a journey to uncover more areas in the webapp under test (an exploration).
            Prioritize this if:
                1. The mindmap is too small. Not many screens identified. A strong indication that further exploration is needed
                2. There are not many remaining untested high priority scenarios to act on
                3. If the mindmap screens are basically authorization failure related screens, or just sign in / sign up - means the prior explorations could not go beyond authentication. In that case, recommend doing a random walk exploration.
                4. If The mindmap contains key screens that are currently NOT_EXPLORED (1). This can be identified by referring to the explorationStatus field of screens (Treat PARTIALLY_EXPLORED as similar to FULLY_EXPLORED), or missing description for the screen. Refer to the below enum for values:

                class ScreenExplorationStatus(IntEnum):
                    UNKNOWN_SCREEN_EXPLORATION_STATUS=0
                    NOT_EXPLORED = 1
                    PARTIALLY_EXPLORED = 2
                    FULLY_EXPLORED = 3

                    If goal is to explore previously identified unexplored screens, in the focusPrompt, provide stepwise guidance (by using the neighbourscreen edge details) to the operator agent to visit those pages and explore.
        - Or a journey targeted at testing a specific set of test scenarios.
        - Or decide to not do another journey - potentially due to multiple blockers happening, not making any progress despite repeated efforts (eg: an empty mindmap despite prior journeys taken), or a decent number of explorations are done and not many test scenarios remain for trying out

        ## If you decide to do an exploration, then return:

        {{
            "type":"EXPLORATION",
            "journeyTitle":"<A short title for the journey>",
            "focusPrompt":"<A prompt to give the AI QA agent instructing to focus on specific areas / steps to take>"
        }}.

        ## If you decide to not do another journey, then return:

        {{
            "type":"END_EXPLORATION",
            "reason":"<Reason>"
        }}

        ## If targeting specific test scenario list:

        You should prioritize test scenarios to pick for the next journey by considering the following:
            - Priority of the test
            - When was it last tested - if too long ago compared to others - then give more weight
            - Likelihood of an AI agent being able to deterministically execute the test (if too complex for an AI agent, leave it)

        When ordering the list of scenarios to test in the next journey, think about how testing a particular scenario will affect the system state and whether a subsequent test scenario becomes infeasible (like the prior action causing the page to potentially navigate to a different screen). 
        For instance, if the page does not change based on a test action, you can try out other test scenarios on the same page after that (like trying out different invalid input combinations to see error messaging appears)

        In this mode, return a JSON response adhereing to following structure:

        {{
            "type":"SCENARIOS_CHECK",
            "journeyTitle":"<A short title for the journey to be taken>",
            "agentSteps":{{<AgentSteps json - refer below for structure>}}
        }}

        class AgentSteps(BaseModel):
            steps:list[AgentStepAdvice]=[]

        class AgentStepAdvice(BaseModel):
            # Only one of the below should be filled for a given step.
            action:Optional[str]=None # Filled only if this is an agent action to take (When NOT a test scenario verification).
            testScenario:Optional[ScenarioTestStep]=None # Filled only if this is for testing a specific scenario
            endJourney:Optional[bool]=None # Fill this only if this is the last step to do in the journey

        class ScenarioTestStep(BaseModel):
            id:Optional[str]=None
            title:Optional[str]=None
            expectedBehavior:Optional[str]=None
            screenName:Optional[str]=None
            screenState:Optional[str]=None

        Following are the inputs available for reasoning:

        - Current mind map of the app. This includes the different screens and states seen, the different element groups present in each screen state, the different user actions identified etc. It also includes how to go from one screen state to another.

        {mind_map.model_dump_json(exclude_none=True,exclude_unset=True)}

        - Test scenarios and their latest verification results (if has been tested before).

        {test_scenario_results.model_dump_json(exclude_none=True,exclude_unset=True)}

        - Focus area hint provided by the user:

        {exploration_prompt}

        - Prior journeys run in this exploration so far:

        {journeys_str}
    '''

    try:
        res = await call_llm(prompt)
        if res:
            result = json.loads(res)
            result_obj = RecommendedNextJourney(**result)
            result_obj.metadata = get_llm_metadata(len(prompt), len(res))
            return result_obj
        return RecommendedNextJourney()
    except Exception as e:
        logger.error("Failed to parse OpenAI response:", exc_info=e)
        return RecommendedNextJourney()

async def generate_test_cases(screenState:ScreenState,test_scenarios:List[TestScenario],pre_steps:List[AgentCodeUnit],snapshot:str) -> AwareUiTestListLLMOutput:
    test_scenarios_json = "\n".join(
        scenario.model_copy(update={"preSteps": None}).model_dump_json()
        for scenario in test_scenarios
    )
    pre_steps_json = "\n".join(step.model_dump_json() for step in pre_steps)
    prompt = f"""
        You are an AI UI test writing agent. An AI Exploratory test agent has been walking around the webapp, and for the current page it is in, it has come up with a few test scenarios to consider. 
        You are provided with the list of test scenarios, the steps taken by the AI agent in the webapp to get to the current screen / state, and the current page snapshot.

        # Objective: Write repeatable test scripts for the provided test scenarios.

        # Instructions

        - The steps provided are taken by an exploratory AI agent - thus some steps may not be relevant for the scenario being tested (it may have wandered around the webapp). However, the test script should contain only the necessary steps to get to the screen state where the test occurs (for instance, navigating to initial page, logging in etc.).
        - Use the provided current snapshot to write playwright commands that assert the behaviour expected by the test scenario (and any actions that need to be done in addition to the pre steps that are necessary for the test scenario. Refer to the description, title and expected behavior of the provided test scenario).
        - Ensure that all tests start by visiting the initial url, then doing steps to get to the screen where the test scenario needs to be executed, and then doing the steps necessary for the test and doing the verifications to verify the expected behaviour is met. Refer below for a good test structure example:

        1. Visit landing page
        2. Sign in
        3. Go to User search page by clicking on the menu item "User Search"
        4. Enter a valid user name: "john doe"
        5. Click on button "Search"
        6. Verify that results displayed are not empty

        In the above,
         - steps 1 throuh 3 are pre steps needed to get to the screen where the test occurs.
         - steps 4 through 5 are steps needed for running the test scenario
         - step 6 is the verification of the expected behaviour
        The output test case should consist of all of it - so that the test case becomes a standalone executable script.

        # Output

        Output a JSON adhereing to following format (a list of test cases, per each test scenario given):
        {{"testCases":[
            {{
                "testName":{{
                    "name":"<A name for the test case>",
                    "suite":"<A name for the suite of test - preferably refer the current screen>"
                }},
                "codeUnits":[{{
                    code:<valid playwright code - use semantically meaningful locators>,
                    description:<plain english short description of the code step>
                }},...],
                "l1Summary":"<Complete list of test steps, delimited with newlines>",
                "l2Summary":"<Title of the test scenario AS IS. ALWAYS make sure this is an exact match - since this will be used to correlate the test scenario with the test case>",
                "tags":[<a list of short tags to annotate this test case with such as "security","functional" etc.>]
            }}
            ...
            ]
        }}

        # Input

        Current screen and state: {screenState.model_dump_json()}

        Test scenarios:

        {test_scenarios_json}
        
        Pre steps:

        {pre_steps_json}

        current page snapshot:

        {snapshot}

    """

    try:
        res: str = await call_llm(prompt)
        if res:
            result_obj = AwareUiTestListLLMOutput(**json.loads(res))
            result_obj.metadata = get_llm_metadata(len(prompt), len(res))
            return result_obj
        return AwareUiTestListLLMOutput()
    except Exception as e:
        logger.error("Failed to parse LLM response for generate_test_cases: %s", e)
        return AwareUiTestListLLMOutput()

async def generate_bug(aria_snapshot: str, bug_description: str, expectation: str, observed_behavior: str) -> Bug:
    """
    Calls OpenAI to generate an assertion for a reported bug.

    Args:
        aria_snapshot (dict): ARIA snapshot of the page.
        bug_description (str): Description of the bug.
        expectation (str): Expected behavior.
        observed_behavior (str): Observed behavior.

    Returns:
        dict: A structured JSON object containing bug details and an assertion command.
    """
    prompt = f"""
    You are an expert in Playwright automation and web testing. Given an ARIA snapshot, a reported bug, 
    the expected behavior, and the observed behavior, generate a Playwright assertion that should 
    verify whether the issue is fixed.

    - **ARIA Snapshot:** ```{json.dumps(aria_snapshot)}```
    - **Bug Description:** {bug_description}
    - **Expected Behavior:** {expectation}
    - **Observed Behavior:** {observed_behavior}

    Use the ARIA snapshot to find the best Playwright locator for asserting this bug. 
    Return a structured JSON response in the following format:

    ```json
        {{
          "title":"A short title for the bug. This should be 1 sentence. It should be natural language.",
          "description": "Description of the violated rule. Include the specific values and references for the UI elements the bug relates to, so that the bug can be located better.",
          "category": "<Bug Category> - Refer below for acceptable values",
          "location": "Playwright locator of the offending element - provide a unique locator. use semantically meaningful playwright selector",
          "eval_command": "A Playwright command to evaluate the given rule for the locator. If the bug is fixed, this assertion should pass. Sometimes an eval command may not be feasible. If so, leave this field empty",
          "severity": 1-3 (1 being lowest, 3 being highest),
          "rule":"A short title string representing the rule that this bug is breaking eg: missing_aria_label, unreadable_text, missing_tab_index etc."
      }}
    ```
    The bug category needs to strictly one of the following values (if none matches, specify as OTHER - do not assume different categories):

  ACCESSIBILITY, SECURITY, VISUAL, PERFORMANCE, FUNCTIONAL, NETWORK, USABILITY, COMPATIBILITY, DATA_INTEGRITY, INTERACTION, LOCALIZATION, RESPONSIVENESS, LAYOUT, OTHER.

    IMPORTANT: Respond ONLY with a valid JSON object as shown above, with no additional text before or after.
    """

    try:
        res: str = await call_llm(prompt)
        if res:
            result_obj = Bug(**json.loads(res))
            return result_obj
        return Bug()
    except Exception as e:
        logger.error("Failed to parse LLM response: %s", e)
        return Bug()

async def summarize_execution_step_results(steps: AgentCodeUnitList) -> ExecutionStepResultSummary:
    prompt=f"""
        You are a support agent to an AI QA agent. The agent has done some steps.

        # Objective: Summarize the steps taken by the agent.

        # Instructions:
        
        - This summary should enable the agent to reproduce the steps in the future. Therefore, it should be written like steps (and in the instructional tone below). eg:
            1. Go to url
            2. Click on the button "Sign in"
            ...
        
        - Remove any steps unnecessary for the objective (since the agent may have "wandered around"). For instance: scroll down, wait a bit etc.
        - Remove any duplicate steps. The objective is to have a summarized list of steps.
        - Specify specific values when referring to actions - such as the text on the button that was clicked, value selected on a drop down - so that the steps can be used as guidance in the future.
            - Eg: Instead of: "click on a specific button", say "click on 'View Results' button".
        - If action is for entering an input, see if the input needs to be remembered exactly (eg: for login credentials), or saying intent makes better sense for reproducing the steps: Eg: "Enter a valid date").
        - No need to specify detailed locators in the output. The output step should have sufficient information for an agent to do that step in the future without ambiguity.
            - Good output: Click on Button with text 'Sign In'
            - Bad outputs:
                    Click on a primary button - this is bad since not enough information to reproduce the step - too much ambiguity.
                    Click on button with selector 'button#radix-trigger-login[aria-selected="true"]' - this is bad since it is too tied to current implementation. If the selectors change slightly, it will break.

        # Output format:

        Output in following JSON format:

        {{
            "steps":[
                "1. <step 1>",
                "2. <step 2>",
                ...
            ],
            "debugInfo":{{
                "promptFeedback":"<Include any feedback about how to improve this prompt to enable you to give better results in the future (if any. leave this empty if none)>",
                "inputDataFeedback":"<Include any feedback about input data improvements that can be done in the future for better results (if any. leave this empty if none)>"
            }}
        }}

        use debugInfo in the response to return feedback about how I can improve this prompt and input data in the future for better results.

        # Input

        Below are the steps taken:

        {steps.model_dump_json(exclude_none=True,exclude_unset=True)}
    """

    try:
        res: str = await call_llm(prompt)
        if res:
            result_obj = ExecutionStepResultSummary(**json.loads(res))
            result_obj.metadata = get_llm_metadata(len(prompt), len(res))
            return result_obj
        return ExecutionStepResultSummary()
    except Exception as e:
        logger.error("Failed to parse LLM response: %s", e)
        return ExecutionStepResultSummary()

async def suggest_next_journey_for_location(mind_map: AppMindMap,test_scenario_results:TestScenarioResultList,journeys_run_in_exploration: List[str],exploration_prompt: str,location:TestLocation,initial_url:str) -> RecommendedNextJourney:
    journeys_str = "\n".join(journeys_run_in_exploration)
    prompt = f'''
        You are a planner agent for an AI QA agent. 

        The user has specifically requested to focus the testing on the following location (screen, state, element group etc.):
        
        {location.model_dump_json()}

        # Your objective is to construct a journey for the AI QA agent to take next, where the agent will first get to the target test location (screen, state), and then perform the testing on that screen.

        It can be one of 3 types:
            - Either exploring previously not identified test scenarios (more free form exploration)
                1. Prioritize this if there isn't sufficient test scenarios authored for the test location
                2. Existing test scenarios are already well tested
            - Or, running already identified test scenarios for the test location.
            - Or, decide not to do another journey
                1. In case there are blockers preventing exploration - based on prior journey results
                2. Or there are no more interesting scenarios left for exploration / testing in the scope provided.

        In either case, you should analyze the mind map provided (it details screens and how to go from one screen state to another), to come up with the steps to reach the test location (screen state), from the initial screen.
        Each screen in the mindmap specifies the url (normalized). The initial screen usually has the flag is_initial_screen set to true. If not present, refer to the initial_url below, to determine the initial screen.
        Then, use the neighbour screen state transition link details to determine the plan to reach the screen state being tested.

        initial url: {initial_url}

        ## If you decide to do an exploration of new test scenarios, then return:

        {{
            "type":"EXPLORATION",
            "journeyTitle":"<A short title for the journey>",
            "focusPrompt":"<A prompt to give the AI QA agent instructing the steps to take to get to the target screen first, and the focus areas and test scenarios to consider after reaching the screen. Write in steps format>"
        }}.

        ## If you decide to not do another journey, then return:

        {{
            "type":"END_EXPLORATION",
            "reason":"<Reason>"
        }}

        ## If targeting specific test scenarios list:

        You should prioritize test scenarios to pick for the next journey by considering the following:
            - Priority of the test
            - When was it last tested - if too long ago compared to others - then give more weight
            - Likelihood of an AI agent being able to deterministically execute the test (if too complex for an AI agent, leave it)

        When ordering the list of scenarios to test in the next journey, think about how testing a particular scenario will affect the system state and whether a subsequent test scenario becomes infeasible (like the prior action causing the page to potentially navigate to a different screen). 
        For instance, if the page does not change based on a test action, you can try out other test scenarios on the same page after that (like trying out different invalid input combinations to see error messaging appears)

        In this mode, return a JSON response adhereing to following structure:

        {{
            "type":"SCENARIOS_CHECK",
            "journeyTitle":"<A short title for the journey to be taken>",
            "agentSteps":{{<AgentSteps json - refer below for structure>}}
        }}

        class AgentSteps(BaseModel):
            steps:list[AgentStepAdvice]=[]

        class AgentStepAdvice(BaseModel):
            # Only one of the below should be filled for a given step.
            action:Optional[str]=None # Filled only if this is an agent action to take (When NOT a test scenario verification).
            testScenario:Optional[ScenarioTestStep]=None # Filled only if this is for testing a specific scenario
            endJourney:Optional[bool]=None # Fill this only if this is the last step to do in the journey

        class ScenarioTestStep(BaseModel):
            id:Optional[str]=None
            title:Optional[str]=None
            expectedBehavior:Optional[str]=None
            screenName:Optional[str]=None
            screenState:Optional[str]=None

        Following are the inputs available for reasoning:

        - Current mind map of the app. This includes the different screens and states seen, the different element groups present in each screen state, the different user actions identified etc. It also includes how to go from one screen state to another.

        {mind_map.model_dump_json(exclude_none=True,exclude_unset=True)}

        - Test scenarios and their latest verification results (if has been tested before).

        {test_scenario_results.model_dump_json(exclude_none=True,exclude_unset=True)}

        - Focus area hint provided by the user:

        {exploration_prompt}

        - Prior journeys run in this exploration so far:

        {journeys_str}
    '''

    try:
        res = await call_llm(prompt)
        if res:
            result = json.loads(res)
            result_obj = RecommendedNextJourney(**result)
            result_obj.metadata = get_llm_metadata(len(prompt), len(res))
            return result_obj
        return RecommendedNextJourney()
    except Exception as e:
        logger.error("Failed to parse OpenAI response:", exc_info=e)
        return RecommendedNextJourney()    



async def summarize_page(snapshot:str,url:str,known_screen_states:ExistingScreenStateMap,prior_steps:List[str])->LLMScreenDetailOutput:
    prior_steps_str = "\n".join(prior_steps)
    prompt=f'''
        You are an expert AI QA planner for webapps, analyzing screens in the app, helping with exploration and test planning for an AI agent. You are provided the following:
        - url of the page
        - cleaned html of the current page
        - currently known screens of the webapp (and the different states each screen can be in)
        - prior steps taken in the journey so far - use relavant info from the prior steps details when determining the state of the screen (such as logged in vs not logged in, empty cart etc). Only use data that is relevant to the current screen. For instance, items added in the cart is irrelevant is the current screen is the user account page.
        
        
        ## Objective: Analyze the page and come up with a structured detailing of the screen, that will be used in building a knowledge map of the webapp and aid an AI agent to explore and test the webapp (refer output format and field comments for specific guidance on each field)
        
        # Screen naming guidance:
        You are provided with existing screen names (mapped by the normalized urls they correspond to). First, normalize the current page url. Then, check if there are existing screens for that url. If so, unless there is strong rationale to give the current screen a different name than existing, ALWAYS use an existing screen name for that normalized url.
        Note that in some SPAs, the url may not change for distinctly different screens, in which case it is fine to name it differently based on the content of the snapshot provided. But typically, prioritize picking from existing list if there are mapped screens for that normalized url.
        
        ## Inputs:

        Url: {url}

        Cleaned html:

        {snapshot}

        Known screen states:

        {known_screen_states.model_dump_json(exclude_none=True,exclude_unset=True)}

        Prior steps taken:

        {prior_steps_str}

    ## Output format: Return a valid JSON that strictly adheres to the following structure:
    
    message LLMScreenDetailOutput{{
        // A human readable name for the screen: Cart, Product listing etc. 
        // If an existing screen name fits, then use it. Only suggest a new one if an existing one doesn't match
        optional string name = 1;
    
        // A human readable name for the current state: Not logged in, Logged in, Cart Empty / Not Empty etc. if a known state describes the current state correctly, use that. Refer to prior execution steps provided to determine the current applicable state.
        optional string state = 2;
    
        // A canonical url (in case of query params / template params. eg: host/{{user}}/product_id={{product_id}}). replace the actual domain with "host"
        optional string url = 3;
    
        // Type of screen: login, product detail, listing, form, interactive, help, documentation etc.
        optional string type = 4;
    
        // a plain english short summary of the page purpose.
        optional string description = 5;
    
        // key element groups in the screen. Ensure that login is captured if present. Ensure no key element groups and elements within are not missed.
        // For lists / tables, do not iterate every item, but rather capture a single representative element for them. 
        repeated ElementGroup elementGroups = 6;
    
        // Different test scenarios feasible at this page, in this state, to consider. Verbosity: ~7-8 test scenarios for a medium complexity screen. For more complex screens, write more if necessary. For simpler screens, can write lesser.
        repeated TestScenario testScenarios = 7;

        // Significance of the screen to the overall objective of the webapp. eg: Documentation / Help might be lower significance as they are support functions. Login / Core business logic related ones would be higher significance.
        // Low significance = 1, Medium =2, High = 3
        int32 significance = 8;

        // A set of hashtags that can be used to annotate this screen with for grouping similar screens. Consider objective of screen, type of screen, type of users, user journeys the screen relates to etc. (No need to prefix with #. Eg: Documentation, Admin, Authentication etc.)
        repeated string tags=9;
    }}
    
    message TestScenario{{
        // A title for the scenario
        optional string title = 1;

        // Expected behaviour
        optional string expectedBehaviour = 2;

        // Verification code. A playwright js code snippet to validate the expected behaviour.
        optional string assertionCode = 5;

        // Steps of the test. Consider the prior steps provided. Deduplicate unnecessary steps for this test scenario. 
        // When providing steps, refer to semantically meaningful element identifiers rather than synthetic ids like element index.
        repeated AgentCodeUnit steps = 3;

        // Priority of the test scenario. 1 - lowest, 3 - highest
        optional int32 priority = 4;
    }}

    message AgentCodeUnit{{
        // A plain english short sentence describing the step (Just the step action, nothing more. Eg: "Go to initial page", "Sign in with valid credentials: 'test@example.com','pasword1'". Refer to specific values used in the step)
        string description = 1; 
        // A playwright code to execute the provided description
        string semanticCode = 2;
    }}

    message ElementGroup{{
        // A short meaningful title for this element group (eg: login form, search box)
        optional string title = 1;
        
        // Purpose of the element group
        optional string purpose = 2;
        
        // List of key elements in the group (focus on elements that matter for testing
        // such as interaction elements, result displays etc.)
        repeated Element elements = 3;
        
        // Actions that are possible in this element group. For authentication pages, avoid sign up and reset / forgot password flows (since they require interacting with email inboxes).
        //  However, login should be attempted if available.
        repeated ActionItem possibleActions = 4;
    }}
    
    message ActionItem{{
        // A title for the action (eg: "Search for products")
        optional string title = 1;
        
        // Priority of the action item. low = 1, medium = 2, high =3.
        optional int32 priority = 2;
        
        // Playwright code (can be multiple steps) to execute the action item.
        // If specific values must be entered, take in to account the provided test data if relevant.
        // If relevant test inputs are not provided, come up with sensible values based on the scenario being explored.
        // Write valid executable playwright code: eg: await page.getById ("id").
        // selectors shoukld uniquely locate the element using semantically meaningful selectors. use await page.locator('<unique locator>'). syntax.
        // Ensure uniquenes by using locator chaining, qualifiers like first(), nth().
        // Only provide code units for the elements that are visible in the current page. If the action spans multiple pages, the agent will call for actions on each page later.
        codeUnits:[{{
        code:<valid playwright code>,
        description:<plain english short description of the code step>
        }},...]
    }}
    
    message Element{{    
        // playwright selector to uniquely locate the element using semantically meaningful selectors. Use syntax like 'input[type=]...'.
        // The value should be usable in a await page.locator('locator string') statement (as the locator string).
        optional string semanticLocator=2;
        
        // text if any
        optional string text = 3;
        
        // alt text if any
        optional string altText = 4;
        
        // For each element, determine its ARIA role (explicit role attribute or implied from the tag, e.g., button, link, textbox).
        // If no explicit role is present, infer the role based on HTML semantics (e.g., <button> → button, <input type="text"> → textbox).
        optional string role = 5;
        
        // The significance of the element to the page objective. low = 1, medium =2, high = 3
        optional int32 significance = 7;
    }}
    '''
    
    try:
        res = await call_llm(prompt)
        output = get_as_llm_screen_detail_output(res)
        output.metadata=get_llm_metadata(len(prompt), len(res))
        return output
    except Exception as e:
        logger.error("Failed to call OpenAI or parse response: %s", str(e))
        return LLMScreenDetailOutput()    

async def detect_visual_bugs_from_image(image_path_str: str, viewport_dims:dict,retries_remaining: int = 1) -> BugCaptureWithLLMMetadata:
    if retries_remaining <= 0:
        return BugCaptureWithLLMMetadata()

    image_path = Path(image_path_str)
    try:
        with image_path.open("rb") as f:
            image_data = f.read()
        encoded_image = base64.b64encode(image_data).decode("utf-8")
        width = viewport_dims["width"]
        height = viewport_dims["height"]
        prompt = f"""
You are a UI quality expert specializing in detecting visual bugs and UI/UX issues from screenshots of web applications.

You will be given a screenshot image. Your task is to analyze the image and return a list of detected issues, bugs, or suggestions for improvement.
The screenshot represents a webpage rendered at a viewport of {width}px width and {height}px height.

### OBJECTIVE
Identify and report any of the following:

1. **Visual Bugs** — layout problems, broken UI elements, overlapping components, missing icons, etc.
2. **Accessibility Issues** — insufficient contrast, missing text alternatives, unreadable text, font too small, etc.
3. **Design / UX Suggestions** — UI elements that appear outdated, overly cluttered, visually inconsistent, or unpolished. (Use category: `SUGGESTION`)
4. **Responsiveness Issues** — UI that does not adapt well to different screen sizes. Look for:
	•	Elements that are cut off, cropped, or extend horizontally outside the visible viewport.
	•	Content that requires horizontal scrolling.
	•	Fixed-width containers that don't shrink on smaller screens.
	•	Overlapping or collapsed sections in narrow viewports.
	•	Text or buttons pushed out of view or misaligned.
	•	Components that are too small to interact with on mobile-like sizes.
	•	Text splitting into multiple lines vertically (e.g., S, a, v, e stacked)
	•	Labels or headings becoming unreadable due to forced wrapping
	•	Buttons expanding vertically due to narrow width
	•	In wide screens, check if elements are unnecessarily stretched, making them look bad
5. **Localization Issues** — text overflows or layout problems due to long translations or inconsistent language usage.
6. **Interaction Issues** — disabled-looking buttons that aren't labeled as such, misleading affordances, etc.
7. **Inconsistencies** — mixed font types, sizes, or spacing across UI components.
8. **Modern UX Violations** — e.g., "buttons too close together", "outdated styling", "missing hover/active states".
9. **Redundancy or Ambiguity** — e.g., multiple CTAs saying the same thing, ambiguous labels.
10. **Unclear Hierarchy** — elements that do not visually reflect their priority or grouping.

### BOUNDING BOX
For each bug or suggestion, return an approximate bounding box for where the issue occurs.

Format:
"bounding_box": {{
  "x_pct": <left position as % of image width as a float value betwen 0 - 100> ,
  "y_pct": <top position as % of image height as a float value betwen 0 - 100>,
  "width_pct": <width as % of image width as a float value betwen 0 - 100>,
  "height_pct": <height as % of image height as a float value betwen 0 - 100>
}}

If the issue is not visual (e.g., page-level suggestion), set bounding_box: null.

BUG CATEGORIES (Required)

Use one of:
ACCESSIBILITY, SECURITY, VISUAL, PERFORMANCE, FUNCTIONAL, NETWORK, USABILITY, COMPATIBILITY, DATA_INTEGRITY, INTERACTION, LOCALIZATION, RESPONSIVENESS, LAYOUT, SUGGESTION, OTHER

# OUTPUT FORMAT Return a JSON adhereing to following format:

{{
  "bugs": [
    {{
      "title": "Short 1-sentence summary of the issue",
      "description": "Detailed explanation of the problem. Include references to specific UI elements or behaviors. Be precise and helpful.",
      "category": "One of the allowed categories above",
      "bounding_box": {{
        "x_pct": 20.5,
        "y_pct": 30.7,
        "width_pct": 10.42,
        "height_pct": 20.0
      }},
      "severity": number between 1 to 3 (1 being lowest severity, 3 highest),
      "rule": "Short string summarizing the rule violated (e.g., low_contrast_text, misaligned_label)"
    }}
  ]
}}

Be comprehensive, but avoid false positives.
"""
        client = OpenAI()

        response = client.chat.completions.create(
            model="gpt-4o",
            response_format={"type": "json_object"},  # This ensures JSON output
            messages=[
                {
                    "role": "system",
                    "content": "You are a highly capable UI QA agent. Always respond in strict JSON format with only the bugs list."
                },
                {
                    "role": "user",
                    "content": prompt
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{encoded_image}"
                            }
                        }
                    ]
                }
            ],
            timeout=120
        )

        res = response.choices[0].message.content or ""
        if not res:
            return BugCaptureWithLLMMetadata()
        output = get_as_bug_capture(res)
        output.analyzed_source=DataSource.SCREENSHOT_SOURCE
        result = BugCaptureWithLLMMetadata(result=output)        
        return result

    except Exception as e:
        logger.exception("Failed to analyze image for visual bugs. Retrying...")
        return await detect_visual_bugs_from_image(str(image_path), viewport_dims, retries_remaining - 1)

async def analyze_visual_issues(html: str,steps:List[str]) -> BugCaptureWithLLMMetadata:
    json_format = '''
    {
    "bugs": [
        {
        "title":"A short title for the bug. This should be 1 sentence.",
        "description": "Description of the violated rule. Include the specific values and references for the UI elements the bug relates to, so that the bug can be located better.",
        "category": "<Bug Category> - Refer below for acceptable values",
        "location": "Playwright locator of the offending element - provide a unique locator. Use semantically meaningful Playwright selector.",
        "eval_command": "A Playwright command to evaluate the given rule for the locator. If the bug is fixed, this assertion should pass.",
        "element_synthetic_id": "If the bug is related to an element which has data-synthetic-id attribute, specify it here. Else, leave empty.",
        "severity": 1,
        "rule": "A short title string representing the rule that this bug is breaking, e.g., missing_aria_label, unreadable_text, missing_tab_index etc."
        }
    ]
    }
    '''

    missing_info = '''
    IMPORTANT: The provided HTML has been stripped of:
    - JavaScript-based dynamic behavior, so do not report bugs related to missing interactivity due to scripts.
    - Media queries and full responsiveness details, so do not report mobile-specific layout issues unless clear structural problems exist in the HTML.
    '''

    step_json = "\n".join(str(step) for step in steps)

    prompt = f'''
    You are an expert in web UI/UX and accessibility. Given the following HTML snapshot, analyze potential visual issues and return structured JSON.

    ### HTML Snapshot:
    {html}

    Identify issues related to layout, readability, interactability, understandability, visual elegance, responsiveness, and accessibility. 
    When describing bugs, be specific, refer to the elements (in a semantically meaningful way) the bug corresponds to, so that a developer can locate it to fix it.
    
    Return results in the following JSON format:

    {missing_info}

    ### Executed Steps before the page reached this DOM state (for context):
    {step_json}

    ### Response structure:
    Return a valid JSON of format below:

    {json_format}

    The bug category needs to strictly be one of the following values (if none matches, specify as OTHER - do not assume different categories):

    ACCESSIBILITY, SECURITY, VISUAL, PERFORMANCE, FUNCTIONAL, NETWORK, USABILITY, COMPATIBILITY, DATA_INTEGRITY, INTERACTION, LOCALIZATION, RESPONSIVENESS, LAYOUT, OTHER.
    '''.strip()

    try:
        res = await call_llm(prompt)
        output = get_as_bug_capture(res)
        output.analyzed_source=DataSource.DOM_SOURCE
        result = BugCaptureWithLLMMetadata(result=output)
        result.metadata=get_llm_metadata(len(prompt), len(res))
        return result
    except Exception as e:
        logger.error("Failed to call OpenAI or parse response: %s", str(e))
        return BugCaptureWithLLMMetadata()
    

async def analyze_console_logs(
    logs: List[ConsoleLogEntry],
    steps: List[ExecutionStepResult],
) -> BugCaptureWithLLMMetadata:
    try:
        step_json = "\n".join(str(step) for step in steps)

        log_lines = "\n".join(f"[{log.type.upper()}] - {log.text}" for log in logs)

        prompt = f"""
            You are an expert QA engineer AI assistant.

            Your job is to analyze browser console logs and determine if any **bugs or issues** can be identified. You are given:
            - A list of **console logs** (limited to error and warning logs).
            - A list of **Playwright code execution steps** that were run right before the logs appeared.

            You must infer whether any issues occurred during the step, based on the console logs. Focus specifically on meaningful patterns that indicate broken functionality, poor UX, or misbehavior. Prioritize the following types of issues:
                •	JavaScript runtime errors (e.g., uncaught exceptions, TypeErrors, null access)
                •	Network or API request failures (e.g., 4xx/5xx status codes, CORS issues, request timeouts)
                •	Warnings that suggest incorrect behavior, unstable UI state, or degraded experience
                •	Logs that may indicate issues that may cause performance degradation
                •	Deprecation notices or security warnings, which reflect poor engineering quality or future breakage risk

            Do not report cosmetic or harmless logs. Focus only on console messages that reveal real or likely bugs.

            Use the executed steps to **understand the user context** (e.g., clicked login, submitted form, etc.).
            When describing bugs, be specific, refer to the logs (in a semantically meaningful way) the bug refers to, so that a developer can locate it to fix it.

            Output in the following JSON format:

            {{
            "bugs": [
                {{
                "title":"A short title for the bug. This should be 1 sentence. It should be natural language.",
                "description": "Description of the violated rule",
                "category": "<Bug Category - choose from ACCESSIBILITY, SECURITY, VISUAL, PERFORMANCE, FUNCTIONAL, NETWORK, USABILITY, COMPATIBILITY, DATA_INTEGRITY, INTERACTION, LOCALIZATION, RESPONSIVENESS, LAYOUT, OTHER>",
                "severity": number between 1 to 3 (1 being lowest severity, 3 highest),
                "rule": "Short string naming the broken rule (e.g., deprecated_library_usage, bad_input_validation)"
                }}
            ]
            }}

            ### Executed Steps (for context):

            {step_json}

            ### Console Logs:
            {log_lines}

            Analyze this context and report any bugs you detect.
        """

        res = await call_llm(prompt)
        output = get_as_bug_capture(res)
        output.analyzed_source=DataSource.CONSOLE_SOURCE
        result = BugCaptureWithLLMMetadata(result=output)
        result.metadata = get_llm_metadata(len(prompt), len(res))
        return result

    except Exception as e:
        logger.error("Failed to call OpenAI or parse response: %s", str(e))
        return BugCaptureWithLLMMetadata(result=BugCapture(bugs=[]), metadata=get_llm_metadata(0, 0))
    
async def analyze_request_response_pairs(
    pairs: list[RequestResponsePair],
    steps: list[str],
) -> BugCaptureWithLLMMetadata:
    step_json = "\n".join(str(step) for step in steps)


    pairs_text = '\n'.join([
        f"""
            #{i + 1}
            Method: {pair.method}
            URL: {pair.url}
            Status: {pair.status}
            Response Time: {f"{pair.responseTimeMs / 1000:.1f}s" if pair.responseTimeMs else 'N/A'}
            Request Headers: {json.dumps(pair.requestHeaders, indent=2)}
            Response Headers: {json.dumps(pair.responseHeaders, indent=2)}
            """ for i, pair in enumerate(pairs)
        ])

    prompt = f"""
        You are an expert exploratory QA agent reviewing API activity during a web session.
        Based on the following execution steps and API request-response headers, identify potential bugs.
        When describing bugs, be specific, refer to the exact API endpoints the bug corresponds to, so that a developer can locate it to fix it.

        Execution steps:
        {step_json}

        API request/response pairs:
        {pairs_text}

        You must infer whether any bugs occurred. Focus on patterns such as:
        - Security issues (missing headers like X-Frame-Options, insecure Set-Cookie, etc.)
        - Caching misconfigurations (e.g., missing/no-cache for sensitive endpoints)
        - Suspicious CORS policies
        - Incorrect content types
        - Unexpected status codes or slow response times
        - Inconsistent auth/session behavior

        Output JSON in this format:
        {{
        "bugs": [
            {{
            "title":"A short title for the bug. This should be 1 sentence. It should be natural language.",
            "description": "Description of the violated rule",
            "category": "<Bug Category - choose from ACCESSIBILITY, SECURITY, VISUAL, PERFORMANCE, FUNCTIONAL, NETWORK, USABILITY, COMPATIBILITY, DATA_INTEGRITY, INTERACTION, LOCALIZATION, RESPONSIVENESS, LAYOUT, OTHER>",
            "location": "<url of the api call>",
            "severity": number between 1 to 3 (1 being lowest severity, 3 highest),
            "rule": "Short string naming the broken rule (e.g., gateway_error, bad_cors_policy)",
            }}
        ]
        }}
        """

    try:
        res = await call_llm(prompt)
        output = get_as_bug_capture(res)
        output.analyzed_source=DataSource.NETWORK_SOURCE
        result = BugCaptureWithLLMMetadata(result=output)
        result.metadata = get_llm_metadata(len(prompt), len(res))
        return result
    except Exception as e:
        logger.error("Failed to analyze API logs with LLM: %s", str(e))
        return BugCaptureWithLLMMetadata(result=BugCapture(bugs=[]), metadata=get_llm_metadata(0, 0))

async def get_new_links(known_screen_state_map: ExistingScreenStateMap,navigation_links:List[NavigationLink]) -> NewLinksLLMOutput:
    prompt = rf"""
    You are helping an AI QA agent map out a webapp being explored. You are provided with the known screens state map (mapping the normalized url -> screen_states).
    The agent has now discovered additional navigation links present in the webapp.

    # Objective:
    Identify new, previously unseen navigation links and name the screen they represent appropriately. The goal is to prevent duplicates for similar screens that differ only by IDs or query parameters.

    # URL Normalization Rules:
    The navigation URL should be normalized before comparing or naming.

    **Normalize as follows:**
    - Replace any UUIDs (e.g. /changelog/123e4567-e89b-12d3-a456-426614174000) with `{{id}}`
    - Replace numeric IDs or slugs in the path (e.g. /user/5678 or /blog/post-2045) with `{{id}}` or `{{slug}}`
    - Replace query parameter values with placeholders (e.g. `?q=apple` → `?q={{query}}`)
    - All URLs within current domain should start with `host/`
    - Do not include links to external domains (e.g. facebook.com)

    **Examples:**
    - `/changelog/123e4567-e89b-12d3-a456-426614174000` → `host/changelog/{{id}}`
    - `/user/12345/info` → `host/user/{{id}}/info`
    - `/search?q=test&page=2` → `host/search?q={{query}}&page={{page}}`

    # Return JSON in the following format:

    {{
    "newScreensMap": {{
        "<normalized_url>": {{
        "name": "<a suitable short name>",
        "type": "<documentation | interactive | login | ...>",
        "significance": <1-3>
        }},
        ...
    }}
    }}

    # Inputs:
    Known screen state map: 
    {known_screen_state_map.model_dump_json()}

    # Navigation links found in current page:
    {chr(10).join(link.model_dump_json() for link in navigation_links)}
    """

    try:
        res: str = await call_llm(prompt)
        if res:
            result_obj = NewLinksLLMOutput(**json.loads(res))
            result_obj.metadata = get_llm_metadata(len(prompt), len(res))
            return result_obj
        return NewLinksLLMOutput()
    except Exception as e:
        logger.error("Failed to parse LLM response for get_new_links: %s", e)
        return NewLinksLLMOutput()

async def get_agent_action_code_units(actions:List[Any],selector_map:Dict[int, Any]) -> CodeUnitListWithLLMMetadata:
    # Ensure all actions are JSON serializable
    def to_serializable(obj):
        if isinstance(obj, BaseModel):
            return obj.model_dump()
        elif isinstance(obj, dict):
            return {k: to_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [to_serializable(i) for i in obj]
        else:
            return obj

    # No need to flatten 'root' keys; actions is a list of root action model objects
    serializable_actions = to_serializable(actions)
    serializable_selector_map = to_serializable(selector_map)

    prompt = f"""
        You are an AI QA assistant. You are provided with a list of actions an AI agent took. Ignore any actions that are related to thinking, planning, writing files, or capturing initial results (such as 'write_file', 'think', 'plan', etc.). Only consider actions that directly interact with the browser, such as navigation, clicking, typing, switching tabs, scrolling, etc.
        You are provided with a selector map, that maps the indexs to the html elements.\n
        #Objective: Come up with code units for the provided browser actions. If the action has an index field, refer to the selector map to generate accurate playwright code that targets the specific element."
        
        #Instructions:

        - When filling the description field for the output code units, the objective is for an AI Agent to be able to use this description to unambiguously, and accurately execute the step in the future. Therefore:
            - Avoid being too generic.
            - Avoid being cryptic and referring obscure selectors (css / xpath etc).
            - Prefer using user visible details for referring elements and actions.
        - Ignore any actions that are not browser interactions (e.g., skip actions like 'write_file', 'think', 'plan', 'capture_initial_results', etc.).

        Examples of bad descriptions:
            - "Click on a specific dev", "Click on a button" (Since they are ambiguous)
            - "Click on the button with css selector xyz=..." (Since they are referring obscure selectors - not user friendly)

        Examples of good descriptions:
            - "Click on 'Sign in' button
            - "Enter a valid name in the text field with placeholder "Enter your name"

        #Inputs:
        
        Actions: {json.dumps(serializable_actions,indent=2)}\n
        Selector Map: {json.dumps(serializable_selector_map,indent=2)}\n
        #Output JSON in this format:\n
        {{
        "codeUnits": [
            {{
            "description": "Action description as provided. Drop index references in this. It should be a short plain english description of the action",
            "semanticCode": "A valid js playwright command to execute. The code should aim to uniquely identify the element by using combination of attributes (or ID fields if present)",
            "pythonCode":"A valid python playwright command to execute. Ensure that this is valid python code."
            }}
        ]
        }}
        """

    try:
        res: str = await call_llm(prompt)
        if res:
            result_obj = CodeUnitListWithLLMMetadata(**json.loads(res))
            result_obj.metadata = get_llm_metadata(len(prompt), len(res))
            return result_obj
        return CodeUnitListWithLLMMetadata()
    except Exception as e:
        logger.error("Failed to parse LLM response: %s", e)
        return CodeUnitListWithLLMMetadata()


async def call_llm(prompt: str, retries_remaining: int = 1) -> str:
    try:
        if retries_remaining <= 0:
            return ""
        client = OpenAI()
        response =client.chat.completions.create(
            timeout=90,
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an advanced autonomous testing agent. Always respond with valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}  # This ensures JSON output
        )

        return response.choices[0].message.content or ""
    except Exception as e:
        logger.error("Error calling LLM", exc_info=e)
        logger.info("Retrying calling LLM")
        return await call_llm(prompt, retries_remaining - 1)


def get_llm_metadata(input_length: int, output_length: int) -> LLMMetadata:
    input_tokens = input_length // 4
    output_tokens = output_length // 4
    total_tokens = input_tokens + output_tokens

    return LLMMetadata(inputTokens=input_tokens,outputTokens=output_tokens,totalTokens=total_tokens)

def get_as_bug_capture(json_string: str) -> BugCapture:
    try:
        parsed = json.loads(json_string)
        return BugCapture.model_validate(parsed)
    except (json.JSONDecodeError, ValidationError):
        return BugCapture(bugs=[])

def get_as_llm_screen_detail_output(json_string:str)->LLMScreenDetailOutput:
    try:
        parsed = json.loads(json_string)
        return LLMScreenDetailOutput.model_validate(parsed)
    except (json.JSONDecodeError, ValidationError):
        return LLMScreenDetailOutput()

async def convert_js_ts_playwright_to_python_steps(file_path: str, config_file_path: str) -> PythonPlaywrightStepsResponse:
    """
    Reads a JS/TS Playwright script file, sends it to the LLM for conversion to Python Playwright blocks,
    and returns a PythonPlaywrightStepsResponse with grouped command blocks (no assertions).
    """
    try:
        script_content = read_file_relative_to_config(file_path, config_file_path)
    except Exception as e:
        return PythonPlaywrightStepsResponse(
            stepBlocks=None,
            result=ConversionResult.FAILURE,
            failureReason=f"Failed to read file: {e}"
        )

    prompt = f'''
You are an expert in Playwright automation and Python code generation.

Given the following JavaScript or TypeScript Playwright test script, extract the **core user interaction steps only**, and convert them to valid **Python Playwright commands**.

# Instructions:
- **Group dependent commands together** into blocks (e.g., if a variable is used in step 2, define it in step 1 of the same block).
- Output should be a **list of command blocks**. Each block is a list of Python commands that can be executed sequentially.
- Do **not include assertions or test verifications** (e.g. `expect(...)`, `.toBeVisible()`, `.toBeTruthy()`).
- Keep only the **essential actions**: `goto`, `fill`, `click`, `locator` definitions, etc.
- Avoid redundant commands, use direct selectors when possible (e.g., `page.get_by_test_id('...')`).
- Output must be valid JSON and conform to this Pydantic schema:

```python
class PythonPlaywrightStepsResponse(BaseModel):
    stepBlocks: Optional[List[List[str]]]  # Each block is a self-contained list of valid Python commands
    result: Optional[ConversionResult]  # 1=SUCCESS, 2=FAILURE
    failureReason: Optional[str]

# Input script:

{script_content}

# Output format:
{{
“stepBlocks”: [
[“await page.goto(‘https://example.com’)”],
[“prompt_input = page.get_by_test_id(‘prompt-input’)”, “await prompt_input.fill(‘say hello’)”],
…
],
“result”: 1,
“failureReason”: null
}}

If conversion is not possible, output:
{{
“stepBlocks”: [],
“result”: 2,
“failureReason”: “”
}}

Respond ONLY with valid JSON. Do not add explanations.
'''

    try:
        res = await call_llm(prompt)
        if res:
            result_obj = PythonPlaywrightStepsResponse.model_validate(json.loads(res))
            return result_obj
        return PythonPlaywrightStepsResponse(result=ConversionResult.UNKNOWN_CONVERSION_RESULT)
    except Exception as e:
        logger.error("Failed to parse LLM response for convert_js_ts_playwright_to_python_steps: %s", e)
        return PythonPlaywrightStepsResponse(result=ConversionResult.FAILURE, failureReason=str(e))

def read_file_relative_to_config(file_path: str, config_file_path: str) -> str:
    """
    Reads a file, resolving file_path relative to the directory of config_file_path if not absolute.
    Returns the file content as a string.
    """
    if not os.path.isabs(file_path):
        config_dir = os.path.dirname(os.path.abspath(config_file_path))
        logger.info(f"Looking for file {file_path} relative to {config_dir}")
        file_path = os.path.join(config_dir, file_path)
    with open(file_path, 'r') as f:
        return f.read()

async def correct_playwright_command(command: str, error_message: str, aria_snapshot: str = "", element_id_map: dict = None) -> str:
    """
    Sends a failed Playwright command and its error to the LLM for correction.
    Returns the corrected command.
    """
    # Prepare element ID mapping for context
    element_context = ""
    if element_id_map:
        element_context = "**Available Elements by ID:**\n"
        for element_id, element_html in element_id_map.items():
            # Truncate element HTML to avoid token bloat
            truncated_html = element_html[:200] + "..." if len(element_html) > 200 else element_html
            element_context += f"- {element_id}: {truncated_html}\n"
    
    prompt = f'''
You are an expert in Playwright automation and Python code generation.

A Playwright command failed to execute with the following error:

**Failed Command:**
```python
{command}
```

**Error Message:**
{error_message}

**Current Page State (Aria Snapshot):**
{aria_snapshot if aria_snapshot else "Not available"}

{element_context}

Your task is to correct the command to make it work. Common issues and solutions:

1. **Python syntax errors**: Fix invalid Python syntax, missing quotes, incorrect indentation, etc.
2. **Element not found**: Use more specific selectors, wait for elements, or check if the element exists
3. **Timing issues**: Add appropriate waits or use `page.wait_for_selector()`
4. **Invalid selectors**: Use more reliable selectors like `get_by_test_id()`, `get_by_role()`, or `get_by_text()`
5. **Page navigation**: Ensure the page is loaded before interacting with elements
6. **Dynamic content**: Wait for content to load or use `page.wait_for_load_state()`
7. **Import issues**: Ensure all necessary imports are available (page, expect, etc.)

IMPORTANT: Return strictly valid Python code that can be executed without syntax errors.

Respond with a JSON object containing the corrected commands as an array. Even if it's just one command, return it as an array with one element.

**Response Format:**
{{
  "corrected_commands": [
    "await page.get_by_test_id('submit-button').click()"
  ]
}}

OR for multiple commands:
{{
  "corrected_commands": [
    "await page.wait_for_selector('[data-testid=\"submit-button\"]')",
    "await page.get_by_test_id('submit-button').click()"
  ]
}}
'''

    try:
        response = await call_llm(prompt)
        # Parse JSON response
        import json
        response_data = json.loads(response)
        
        # Handle corrected_commands array
        if "corrected_commands" in response_data and response_data["corrected_commands"]:
            # Concatenate all commands with newlines to create an executable block
            corrected_commands = response_data["corrected_commands"]
            return "\n".join(corrected_commands)
        else:
            logger.error(f"Unexpected response format or empty corrected_commands: {response}")
            return command
            
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON response: {e}")
        return command
    except Exception as e:
        logger.error(f"Failed to correct command: {e}")
        return command  # Return original command if correction fails

async def convert_script_to_browser_actions(file_path: str, config_file_path: str) -> ActionStepList:
    """
    Reads a JS/TS Playwright script file, sends it to the LLM for conversion to plain english actions.
    """
    try:
        script_content = read_file_relative_to_config(file_path, config_file_path)
    except Exception as e:
        raise RuntimeError(f"Failed to read script file: {e}")

    prompt = f'''
You are an assistant that converts Playwright JS/TS scripts into a structured list of browser actions for an autonomous agent.

Given the following Playwright script:

---
{script_content}
---

Convert the script into an array of plain english actions, where each action is a sentence describing the action in sufficiently precise detail to enable an AI agent to execute the action unambiguously:

Eg action outputs:
[
  "Go to url https://example.com",
  "Input 'tester@example.com' in the email field (selector: input[name='email'])",
  "Input 'TestPass123' in the password field (selector: input[name='password'])",
  "Click on the sign in button (selector: button[type='submit'])"
]

Only include actions that can be executed by the agent. Do not include comments or code that cannot be mapped to a browser action. Ignore assertions in the script.

Strictly respond with a JSON adhereing to the following format:

# Output format:
{{
  "steps": [
    "Go to url https://example.com",
    "Input 'tester@example.com' in the email field (selector: input[name='email'])",
    ...
  ]
}}
'''

    try:
        llm_response = await call_llm(prompt)
        return ActionStepList.model_validate_json(llm_response)
    except Exception as e:
        raise RuntimeError(f"Failed to convert script to initial actions: {e}")

async def summarize_app_mindmap(mindMap: AppMindMap) -> AppMindMapSummary:
    prompt = (
        "You are a support agent to an AI QA agent. You are provided with a mindmap about the webapp being tested. It includes the different screens found, the element groups in each, different actions possible etc. It may already include an app detail. This was written by a prior call to you to summarize previously known mindmap.\n"
        "#Objective: Analyze the mindmap and write a new summary (around 4-5 sentences maximum) of the webapp being tested - it should cover the domain, the overall purpose of the webapp etc. This summary will be utilzied by downstream test agents. Below is the mindmap:\n"
        f"{mindMap.model_dump_json(exclude_none=True,exclude_unset=True)}\n\n"
        "Provide the output in following JSON format:\n"
        '{\n  "summary": "<summary>"\n}\n'
    )

    try:
        res: str = await call_llm(prompt)
        if res:
            result_obj = AppMindMapSummary(**json.loads(res))
            result_obj.metadata = get_llm_metadata(len(prompt), len(res))
            return result_obj
        return AppMindMapSummary()
    except Exception as e:
        logger.error("Failed to parse LLM response for summarize_app_mindmap: %s", e)
        return AppMindMapSummary()
            