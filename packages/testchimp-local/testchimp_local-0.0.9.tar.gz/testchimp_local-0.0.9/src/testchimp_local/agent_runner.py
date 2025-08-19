import asyncio
import os
import logging
import sys
from browser_use import Agent, Controller
from browser_use.llm import ChatOpenAI
from browser_use.browser.views import BrowserStateSummary
from browser_use.agent.views import (AgentOutput)
from .datas import ScreenStateVisitResult,AgentRunnerTask,Screenshot, TestScenarioCaptureReport,Viewport,ViewportNickname,JourneyRecordingMode,ScreenStateDetail,ScreenExplorationStatus,ScreenDetail,NewLinksLLMOutput,NavigationLink,ExistingScreenStateMap,DeduplicateScenarioSuggestion,TestScenario,AgentTestResult,ScenarioTestResult,RecommendedJourneyType,CodeUnitListWithLLMMetadata,BugCountSummary,ConsoleLogEntry,BugCaptureWithLLMMetadata,JourneyExecutionResult,JourneyLogItemType,DataSource,SourceMap,LLMScreenDetailOutput,ScreenState,ExecutionStepStatus,AgentCodeUnit,BugCaptureForCategory,BugCaptureReport,CodeUnit,EndOfJourney, Bug,BugCapture,BugCategory,ExecutionStepResult,BugSeverity,AgentJourneyLog,AlternateChoice,ChoicePriority,JourneyEndStatus,JourneyExecutionStatus,JourneyLogItem,JourneyAgnotism,RecordingMetadata,ConversionResult
from typing import Callable, List, Optional, Union, Awaitable, Dict
import uuid
import json
import time
from playwright.async_api import Page
# Add these imports for helpers and models
from .openai_facade import generate_bug,detect_visual_bugs_from_image,get_agent_action_code_units,get_new_links,summarize_page,analyze_visual_issues, analyze_console_logs,analyze_request_response_pairs, convert_js_ts_playwright_to_python_steps, convert_script_to_browser_actions
from .agent_utils import extract_actions_and_selector_map,has_ui_likely_changed,get_llm_friendly_dom,calculate_bug_hash,get_bug_capture_report,VIEWPORT_PRESETS
from .web_utils import extract_navigation_links_from_page, get_normalized_url
from .datas import ExecutionStepResult, ExecutionStepStatus, JourneyLogItem, JourneyLogItemType
from .feature_facade import FeatureFacade, UpsertJourneyExecutionRequest, UploadScreenshotRequest, get_feature_facade_instance
import tempfile
import base64
from .console_watcher import ConsoleWatcher
from .network_watcher import NetworkWatcher
from .html_utils import create_stripped_dom, has_significant_ui_changes, StrippedDOM
from typing import cast
from .network_utils import clean_request_response_pair

# Monkey patch to suppress '🚀 Starting task:' log from browser_use Agent
try:
    from browser_use.agent.service import Agent
    def no_op_log_agent_run(self):
        pass
    Agent._log_agent_run = no_op_log_agent_run
except ImportError:
    pass  # browser_use not available or not installed yet

logger = logging.getLogger(__name__)

async def capture_and_upload_screenshot(browser_session, page, exploration_id, execution_id, step_id):
    """
    Takes a screenshot of the given Playwright page, saves it to a temp file, uploads it using feature_facade.upload_screenshot,
    and returns (gcp_path, local_path).
    """
    # Take screenshot and save to temp file
    if browser_session:
        await browser_session.remove_highlights()
        logger.info("Removed highlights before screenshot")
            
    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
        local_path = tmp_file.name
        await page.screenshot(path=local_path)

    # Read and base64 encode the image
    with open(local_path, "rb") as f:
        image_bytes = f.read()
        image_b64 = base64.b64encode(image_bytes).decode("utf-8")

    # Prepare and call upload_screenshot
    feature_facade = get_feature_facade_instance()
    if feature_facade is None:
        raise RuntimeError("FeatureFacade is not initialized. Call set_feature_facade before using capture_and_upload_screenshot.")
    req = UploadScreenshotRequest(
        explorationId=exploration_id,
        journeyExecutionId=execution_id,
        stepId=step_id,
        image=image_b64
    )
    resp = feature_facade.upload_screenshot(req)
    gcp_path = resp.gcpPath
    return gcp_path, local_path

class AgentRunner:
    def __init__(self, 
                 openai_api_key,
                 handle_bugs_discovered,
                 handle_screen_state_visited,
                 handle_unexplored_screens_found,
                 should_visual_analyze_screen,
                 should_visual_analyze_screenshot,
                 should_analyze_api_call,
                 report_visual_analyzed_screen,
                 report_visual_analyzed_screenshot,
                 report_analyzed_api_calls,
                 get_known_screen_states_map,
                 on_tokens_used,
                 on_credits_used,
                 get_exploration_credits_used,
                 get_release_labels):
        
        self.controller = Controller()
        self.openai_api_key = openai_api_key
        self.current_journey_execution_id: Optional[str] = None
        self.browser_context=None

        # Store all callback functions  
        self.handle_bugs_discovered = handle_bugs_discovered
        self.handle_screen_state_visited = handle_screen_state_visited
        self.handle_unexplored_screens_found = handle_unexplored_screens_found
        self.should_visual_analyze_screen = should_visual_analyze_screen
        self.should_visual_analyze_screenshot = should_visual_analyze_screenshot
        self.should_analyze_api_call = should_analyze_api_call
        self.report_visual_analyzed_screen = report_visual_analyzed_screen
        self.report_visual_analyzed_screenshot = report_visual_analyzed_screenshot
        self.report_analyzed_api_calls = report_analyzed_api_calls
        self.get_known_screen_states_map = get_known_screen_states_map
        self.on_tokens_used=on_tokens_used
        self.on_credits_used=on_credits_used
        self.get_exploration_credits_used=get_exploration_credits_used
        self.get_release_labels = get_release_labels

        self.high_bugs=0
        self.med_bugs=0
        self.low_bugs=0
        # Step recording and journey log
        self.log_items = []
        self.error=""
        self.steps = []
        self.screen_state = None
        self.current_url = None
        self.task = None  # Initialize task attribute
        self.current_state_exec_items = []
        self.browser_session = None
        self.project_id = None
        self.current_viewport = None
        self.credits_used = 0
        self.test_data_prompt=""
        self.last_user_action_millis = 0
        self.last_step_screenshot_path = None
        self.browser_state = None
        self.previous_stripped_dom = None
        self.last_console_log_record_timestamp = 0

        if self.openai_api_key:
            os.environ["OPENAI_API_KEY"] = self.openai_api_key

        self.controller.action("Capture bug")(self.capture_bug)
        # Register controller actions for report test scenario result
        # TODO

    async def capture_bug(self, bug_description: str, expectation: str,observed_behavior:str, page):
        logger.info(f"Capturing bug {bug_description} {expectation} {observed_behavior}")
        await self.capture_bug_internal(bug_description,expectation,observed_behavior,"",page)

    async def capture_bug_internal(self,bug_description:str,expectation:str,observed_behavior:str,test_scenario_id:str,page):
        try:
            aria_snapshot = await page.locator('body').aria_snapshot()
            if not aria_snapshot.strip() or not self.task:
                return
            if not self.screen_state:
                logger.info("Screen state not defined")
                return
            bug :Bug = await generate_bug(aria_snapshot, bug_description, expectation, observed_behavior)
            if(test_scenario_id):
                bug.scenario_id=test_scenario_id
            hash=calculate_bug_hash(bug)
            bug.bug_hash=hash    
            step_id = str(uuid.uuid4())
            self.last_step_screenshot_path,_=await capture_and_upload_screenshot(self.browser_session,page,self.task.exploration_id,self.current_journey_execution_id,step_id)
            log_item:JourneyLogItem=JourneyLogItem(
                id=step_id,
                itemType=JourneyLogItemType.BUG_CAPTURE,
                startTimestampMillis=int(time.time()*1000),
                endTimestampMillis=int(time.time()*1000),
                screenState=self.screen_state,
                screenshotPath=self.last_step_screenshot_path,
                viewport=self.current_viewport,
                bugCaptureReport=get_bug_capture_report([bug]))
            self.log_items.append(log_item)
            await self._update_agent_journey_log(False,False)
            logger.info(f"Captured bug {bug_description} {expectation} {observed_behavior}")

            # Insert bug to db via handle_bugs_discovered callback
            if self.handle_bugs_discovered:
                await self.handle_bugs_discovered(
                    self.screen_state,
                    self.job_id,
                    [bug]
                )
        except Exception as e:
            logger.error("Error in capture bug: %s", e)


    async def _update_agent_journey_log(self,is_completed=False,is_exception=False):
        agent_journey_log = AgentJourneyLog(
            error=self.error,
            logs=self.log_items,
            recordingMode=JourneyRecordingMode.SCREENSHOT
        )

        exec_result = JourneyExecutionResult(
            bug_count_summary=BugCountSummary(highSeverityBugs=self.high_bugs,medSeverityBugs=self.med_bugs,lowSeverityBugs=self.low_bugs)
        )        
        status=JourneyExecutionStatus.IN_PROGRESS_JOURNEY_EXECUTION
        if(is_completed):
            if(is_exception):
                status=JourneyExecutionStatus.EXCEPTION_IN_JOURNEY_EXECUTION
            else:
                status=JourneyExecutionStatus.COMPLETED_JOURNEY_EXECUTION

        feature_facade = get_feature_facade_instance()
        if feature_facade is None:
            raise RuntimeError("FeatureFacade is not initialized.")
        feature_facade.upsert_journey_execution(UpsertJourneyExecutionRequest(explorationId=self.exploration_id,
        executionId=self.current_journey_execution_id,
        agentJourneyLog=agent_journey_log,
        executionResult=exec_result,
        creditsUsedInExploration=self.get_exploration_credits_used(),
        creditsUsedInJourney=self.credits_used,
        status=status))

    async def get_active_page(self) -> Optional[Page]:
        if not self.browser_context:
            return None
        pages = self.browser_context.pages
        return pages[-1] if pages else None

    async def update_screen_state(self, screen_state: ScreenState,snapshot:str, screen_detail: Optional[LLMScreenDetailOutput] = None, source_map: Optional[SourceMap] = None,release_label:Optional[str]=None):
        if self.screen_state is None:
            screen_changed = True
        else:
            screen_changed = (
                self.screen_state.name != screen_state.name or
                self.screen_state.state != screen_state.state
        )        
        if (screen_changed):
            # Either the screen or the state has changed. Report how we got from prior state to the current state
            if self.handle_screen_state_visited:
                screenshot:Screenshot
                if(self.last_step_screenshot_path and self.current_viewport):
                    screenshot=Screenshot(url=self.last_step_screenshot_path,viewport=self.current_viewport)                
                    screen_state_visit_result: ScreenStateVisitResult = await self.handle_screen_state_visited(self.current_url,snapshot,screen_state, self.screen_state, self.current_state_exec_items,self.steps, screen_detail, screenshot if screenshot else None,source_map,release_label,self.job_id,self.task.journey_type != RecommendedJourneyType.SCENARIOS_CHECK)
                    # Create journey log item for scenario capture if test scenarios were inserted
                    if screen_state_visit_result and screen_state_visit_result.insertedTestScenarios and len(screen_state_visit_result.insertedTestScenarios) > 0:
                        test_scenario_capture_report = TestScenarioCaptureReport(scenarios=screen_state_visit_result.insertedTestScenarios)
                        log_item: JourneyLogItem = JourneyLogItem(
                            id=str(uuid.uuid4()),
                            testScenarioCaptureReport=test_scenario_capture_report,
                            itemType=JourneyLogItemType.SCENARIO_CAPTURE,
                            screenshotPath=self.last_step_screenshot_path,
                            screenState=screen_state,
                            startTimestampMillis=int(time.time() * 1000),
                            endTimestampMillis=int(time.time() * 1000)
                        )
                        self.log_items.append(log_item)
                        self._update_agent_journey_log()
            self.current_state_exec_items = []

        self.screen_state = screen_state

    async def do_initial_visit(self,page:Page):
        if(not self.task or not self.task.initial_url):
            return
        await page.goto(self.task.initial_url)
        self.credits_used=self.credits_used+1
        self.on_credits_used(1)
        self.last_user_action_millis=int(time.time()*1000) 
        agent_code_unit:AgentCodeUnit=AgentCodeUnit(description="Navigate to initial url",semanticCode=f"await page.goto('{self.task.initial_url}');")
        step_execution = ExecutionStepResult(
                codeUnit=agent_code_unit,
                status=ExecutionStepStatus.PASSED
            )
        self.current_state_exec_items.append(agent_code_unit)
        self.steps.append(agent_code_unit)

        step_id = str(uuid.uuid4())
        # No need to do the remove highlights since this is initial visit done outside of agent
        self.last_step_screenshot_path,_=await capture_and_upload_screenshot(self.browser_session,page,self.task.exploration_id,self.task.execution_id,step_id)

        log_item: JourneyLogItem = JourneyLogItem(id=step_id,
                                                    stepExecution=step_execution,
                                                    itemType=JourneyLogItemType.STEP_EXECUTION,
                                                    screenState=self.screen_state,
                                                    screenshotPath=self.last_step_screenshot_path,
                                                    startTimestampMillis=self.last_user_action_millis,
                                                    endTimestampMillis=self.last_user_action_millis,
                                                    viewport=self.current_viewport)
        self.last_user_action_millis+=1
        self.log_items.append(log_item)

        await self._update_agent_journey_log(False, False)
        await self.analyze_screen(page)
        links:List[NavigationLink]=await extract_navigation_links_from_page(page)
        if(links):
            await self.extract_navigation_links(links)        

    async def run_script_file(self, page: Page, script_path: str,config_file_path:str):
        """
        Converts a JS/TS Playwright script to Python steps and executes them on the given Playwright page.
        """
        if not script_path:
            return
        logger.info("Converting the script to python playwright for execution...")
        response = await convert_js_ts_playwright_to_python_steps(script_path,config_file_path)
        if response.result != ConversionResult.SUCCESS or not response.steps:
            logger.warning(f"Pre/Post script conversion failed. Reason: {response.failureReason}")
            return
        try:
            # Combine all steps into a single async function body
            steps_code = "\n    ".join(response.steps)
            func_code = f"async def __run_all_steps(page):\n    {steps_code}"
            exec_locals = {}
            exec(func_code, {}, exec_locals)
            await exec_locals['__run_all_steps'](page)
        except Exception as e:
            logger.error(f"Error executing script steps:\n{e}")

    async def on_strict_mode_step(self, page: Page, playwright_command: str):
        """
        Callback function called after each step in strict mode execution.
        This parallels the on_new_step functionality but works with playwright commands instead of browser_use objects.
        """
        logger.info(f"Executed playwright command in strict mode: {playwright_command}")
        
        # Always use get_active_page helper
        if self.max_credits_for_journey is not None and self.credits_used >= self.max_credits_for_journey:
            raise RuntimeError("Credits exhausted for journey")
        
        page = await self.get_active_page() if page is None else page
        if not page or getattr(page, 'url', None) == 'about:blank':
            return

        # Record the user action (simplified version for strict mode)
        await self.record_strict_mode_action(playwright_command, page)

        # Check if UI is updated using DOM comparison
        ui_updated = await self.strict_mode_ui_changed(page)
        if ui_updated:
            ui_actually_changed = await self.analyze_screen(page)
            if ui_actually_changed:
                test_location = getattr(self.task, 'test_location', None)
                screen_name = getattr(test_location, 'screenName', None) if test_location else None
                if not test_location or (screen_name == getattr(self.screen_state, 'name', None)):
                    links = await extract_navigation_links_from_page(page)
                    if links:
                        await self.extract_navigation_links(links)
        
        # Analyze console and network if not in a specific test location or matches current screen
        test_location = getattr(self.task, 'test_location', None)
        screen_name = getattr(test_location, 'screenName', None) if test_location else None
        if not test_location or (screen_name == getattr(self.screen_state, 'name', None)):
            await self.analyze_console(page)
            await self.analyze_network(page)

    async def strict_mode_ui_changed(self, page) -> bool:
        """
        Determines if the UI has changed significantly in strict mode.
        Uses DOM comparison and URL tracking to detect meaningful changes.
        """
        try:
            # Create current stripped DOM
            current_dom = await create_stripped_dom(page)
            
            # If no previous DOM, this is the first step - assume no change
            if self.previous_stripped_dom is None:
                self.previous_stripped_dom = current_dom
                return True
            
            # Check for significant changes
            has_changes = has_significant_ui_changes(self.previous_stripped_dom, current_dom)
            
            # Update previous DOM for next comparison
            self.previous_stripped_dom = current_dom
            
            return has_changes
            
        except Exception as e:
            logger.error(f"Error in strict_mode_ui_changed: {e}")
            # On error, assume no change to be safe
            return False

    async def record_strict_mode_action(self, playwright_command: str, page: Page):
        """
        Records the user action in strict mode using the playwright command.
        This is a simplified version of record_user_action for strict mode.
        """
        try:
            # Create a simple agent code unit from the playwright command
            agent_code_unit = AgentCodeUnit(
                description=f"Executed: {playwright_command}",
                semanticCode=playwright_command,
                pythonCode=playwright_command
            )
            
            self.credits_used = self.credits_used + 1
            self.on_credits_used(1)
            self.last_user_action_millis = int(time.time() * 1000)

            # Create a StepExecution object
            step_execution = ExecutionStepResult(
                codeUnit=agent_code_unit,
                status=ExecutionStepStatus.PASSED
            )
            self.current_state_exec_items.append(agent_code_unit)
            self.steps.append(agent_code_unit)
            
            # Log the step execution in JourneyLogItem
            step_id = str(uuid.uuid4())
            self.last_step_screenshot_path, local_path = await capture_and_upload_screenshot(
                self.browser_session,
                page, 
                getattr(self.task, 'exploration_id', None), 
                self.job_id, 
                step_id
            )
            log_item = JourneyLogItem(
                id=step_id,
                stepExecution=step_execution,
                itemType=JourneyLogItemType.STEP_EXECUTION,
                screenState=self.screen_state,
                screenshotPath=self.last_step_screenshot_path,
                viewport=self.current_viewport,
                startTimestampMillis=self.last_user_action_millis,
                endTimestampMillis=self.last_user_action_millis
            )
            self.last_user_action_millis += 1
            self.log_items.append(log_item)

            await self._update_agent_journey_log()
        except Exception as e:
            logger.error("Error recording strict mode action: %s", e)

    async def run_strict_mode_script(self, page: Page, run_script_path: str, config_file_path: str, enable_autocorrect: bool = True):
        """
        Executes a script in strict mode by converting it to Python Playwright command blocks
        and running each block with a shared context.
        
        Args:
            page: Playwright page object
            run_script_path: Path to the script file to execute
            config_file_path: Path to the configuration file
            enable_autocorrect: Whether to enable LLM-based command correction on failures (default: True)
        """
        logger.info(f"Converting {run_script_path} to Python playwright blocks for strict mode execution...")
        
        python_steps_response = await convert_js_ts_playwright_to_python_steps(run_script_path, config_file_path)
        
        # Log the LLM conversion result
        logger.info(f"LLM conversion result: {python_steps_response.result}")
        if python_steps_response.stepBlocks:
            logger.info(f"Converted Python steps from LLM:")
            for i, block in enumerate(python_steps_response.stepBlocks):
                for line in block:
                    logger.info(f"  {line}")
        else:
            logger.warning("No step blocks returned from LLM conversion")
        
        if python_steps_response.result != ConversionResult.SUCCESS:
            logger.error(f"Script conversion failed: {python_steps_response.failureReason}")
            raise RuntimeError(f"Script conversion failed: {python_steps_response.failureReason}")
        
        step_blocks = python_steps_response.stepBlocks or []
        if not step_blocks:
            logger.warning("No command blocks found in converted script")
            return
        
        logger.info(f"Executing {len(step_blocks)} command blocks in strict mode")

        # Shared execution context
        from playwright.async_api import expect
        import re, time, math, json, asyncio

        exec_globals = {
            "page": page,
            "asyncio": asyncio,
            "expect": expect,
            "re": re,
            "time": time,
            "math": math,
            "json": json,
            "range": range,
            "len": len,
            "str": str,
            "int": int,
            "float": float,
            "__builtins__": __builtins__,  # optional, adds all built-ins
        }

        self.previous_stripped_dom = None

        # Use fixed max_failures value of 3
        max_failures = 3
        logger.info(f"Using max_failures: {max_failures}")

        for i, block in enumerate(step_blocks):
            failures = 0
            current_block = block.copy()
            
            while failures < max_failures:
                try:
                    logger.info(f"Executing block {i + 1}/{len(step_blocks)} (attempt {failures + 1}):\n" + "\n".join(current_block))
                    block_code = "\n    ".join(current_block)
                    async_func_code = f"async def execute_block():\n    {block_code}"
                    exec(async_func_code, exec_globals)
                    await exec_globals["execute_block"]()
                    await self.on_strict_mode_step(page, block_code)
                    await asyncio.sleep(0.1)
                    break  # Success, exit retry loop
                    
                except Exception as e:
                    failures += 1
                    error_msg = str(e)
                    logger.error(f"Error executing block {i + 1} (attempt {failures}): {error_msg}")
                    logger.error(f"Commands: {current_block}")
                    
                    if failures >= max_failures:
                        logger.error(f"Max failures ({max_failures}) reached for block {i + 1}")
                        raise RuntimeError(f"Failed to execute block {i + 1} after {max_failures} attempts: {e}")
                    
                    # Try to correct the command with LLM if autocorrect is enabled
                    if enable_autocorrect:
                        logger.info(f"Attempting to correct block {i + 1} with LLM...")
                        try:
                            from .openai_facade import correct_playwright_command
                            
                            # Get aria snapshot and element ID mapping for better correction
                            aria_snapshot = await page.locator('body').aria_snapshot()
                            from .html_utils import get_element_id_mapping
                            element_id_map = await get_element_id_mapping(page)
                            
                            # Convert the entire block to a single string for correction
                            block_code = "\n".join(current_block)
                            
                            # Correct the entire block as a whole
                            corrected_block_code = await correct_playwright_command(block_code, error_msg, aria_snapshot, element_id_map)
                            logger.info(f"Corrected block: {block_code} -> {corrected_block_code}")
                            
                            # Split the corrected code back into individual commands
                            current_block = [line.strip() for line in corrected_block_code.split('\n') if line.strip()]
                            logger.info(f"Retrying block {i + 1} with corrected commands")
                            
                        except Exception as correction_error:
                            logger.error(f"Failed to correct block {i + 1}: {correction_error}")
                            # Continue with original block if correction fails
                            current_block = block.copy()
                    else:
                        logger.info(f"Autocorrect disabled, retrying with original block {i + 1}")
                        current_block = block.copy()
        
        logger.info("Strict mode script execution completed successfully")

    async def run_agent_task(self, agent_task: AgentRunnerTask, browser_context):
        self.current_journey_execution_id = agent_task.execution_id
        self.max_credits_for_journey=agent_task.max_credits_for_journey
        self.task = agent_task  # Store the task for later use
        self.bug_capture_settings=agent_task.bug_capture_settings
        self.viewport_config=agent_task.viewport_config
        self.test_data_prompt=agent_task.test_data_inputs
        self.ignored_bug_hashes=agent_task.ignored_bug_hashes
        self.exploration_id=agent_task.exploration_id
        self.job_id = agent_task.execution_id  # Set job_id for consistency
        self.browser_context=browser_context
        self.current_screen_updated_timestamp=0
        page = await self.create_page_with_initial_viewport()
        
        self.console_watcher=ConsoleWatcher(self.browser_context)
        await self.console_watcher.start()
        
        if(self.task.bug_capture_settings and DataSource.NETWORK_SOURCE in self.task.bug_capture_settings.sources):
            self.network_watcher=NetworkWatcher(self.browser_context,self.task.url_regex_to_capture)
            await self.network_watcher.start()

        # Run pre-script if provided
        pre_script_path = getattr(agent_task, 'pre_journey_script', None) or ""
        if page is not None and pre_script_path and agent_task.config_file_path:
            await self.run_script_file(page, pre_script_path,agent_task.config_file_path)

        # If run_script is present, use script-based agent run
        run_script_path = getattr(agent_task, 'run_script', None) or ""
        if run_script_path and agent_task.config_file_path:
            # Check if strict mode is enabled
            strict_mode = getattr(agent_task, 'strict_mode', False)
            
            if strict_mode:
                logger.info("Running script in strict mode - converting to Python playwright steps and executing individually")
                # Get enable_autocorrect from task config, default to True
                enable_autocorrect = getattr(agent_task, 'enable_autocorrect', None) or True
                logger.info(f"Autocorrect setting: {enable_autocorrect}")
                await self.run_strict_mode_script(page, run_script_path, agent_task.config_file_path, enable_autocorrect)
                await self._update_agent_journey_log(True, False)
            else:
                logger.info(f"Converting {run_script_path} to actions for agent...")
                agent_actions = await convert_script_to_browser_actions(run_script_path,agent_task.config_file_path)
                steps = agent_actions.steps if agent_actions.steps is not None else []
                task_str = "\n".join(steps)
                task_str = "Follow the action items listed below precisely. Objective is to follow the steps outlined exactly, and not explore. \n" + task_str
                logger.info(f"Agent will perform the following\n: {task_str}")
                
                async def script_step_callback(*args, **kwargs):
                    await self.on_new_step(*args, page=page, **kwargs)
                agent = Agent(
                    task=task_str,
                    llm=ChatOpenAI(model="gpt-4o-mini"),
                    controller=self.controller,
                    page=page,
                    register_new_step_callback=script_step_callback,
                    register_done_callback=self.on_agent_done,
                )
                self.browser_session=agent.browser_session
                await agent.run()
                await self._update_agent_journey_log(True,False)
            
            # Run post-script if provided
            post_script_path = getattr(agent_task, 'post_journey_script', None) or ""
            if page is not None and post_script_path and agent_task.config_file_path:
                await self.run_script_file(page, post_script_path,agent_task.config_file_path)
            return

        # Default: prompt-based agent run
        if page is not None:
            await self.do_initial_visit(page)

        try:
            async def new_step_callback(*args, **kwargs):
                await self.on_new_step(*args, page=page, **kwargs)

            agent = Agent(
                task=self.get_agent_task(),
                llm=ChatOpenAI(model="gpt-4o-mini"),
                controller=self.controller,
                page=page,
                register_new_step_callback=new_step_callback,
                register_done_callback=self.on_agent_done,
            )
            self.browser_session=agent.browser_session
            await agent.run()
            await self._update_agent_journey_log(True,False)
        except Exception as error:
            logger.info(f"""Error occurred {error}""")
            await self._update_agent_journey_log(True,True)
        finally:
            # Run post-script if provided
            post_script_path = getattr(agent_task, 'post_journey_script', None) or ""
            if page is not None and post_script_path and agent_task.config_file_path:
                await self.run_script_file(page, post_script_path,agent_task.config_file_path)
        return

    async def on_new_step(self, current_browser_state: BrowserStateSummary, agent_output: AgentOutput, step_index, page=None):
        # Always use get_active_page helper
        if self.max_credits_for_journey is not None and self.credits_used >= self.max_credits_for_journey:
            raise RuntimeError("Credits exhausted for journey")
        page = await self.get_active_page() if page is None else page
        if not page or getattr(page, 'url', None) == 'about:blank':
            return

        await self.record_user_action(agent_output, current_browser_state, page)

        # Check if UI is updated
        ui_updated = False
        if hasattr(self, 'browser_state'):
            ui_updated = has_ui_likely_changed(self.browser_state, current_browser_state)
        if ui_updated:
            ui_actually_changed = await self.analyze_screen(page)
            if ui_actually_changed:
                test_location = getattr(self.task, 'test_location', None)
                screen_name = getattr(test_location, 'screenName', None) if test_location else None
                if not test_location or (screen_name == getattr(self.screen_state, 'name', None)):
                    links = await extract_navigation_links_from_page(page)
                    if links:
                        await self.extract_navigation_links(links)
        # Analyze console and network if not in a specific test location or matches current screen
        test_location = getattr(self.task, 'test_location', None)
        screen_name = getattr(test_location, 'screenName', None) if test_location else None
        if not test_location or (screen_name == getattr(self.screen_state, 'name', None)):
            await self.analyze_console(page)
            await self.analyze_network(page)
        self.browser_state = current_browser_state

    async def create_page_with_initial_viewport(self):
        if not self.browser_context:
            return
        page = await self.browser_context.new_page()

        viewports = self.viewport_config.viewports if self.viewport_config and self.viewport_config.viewports else []

        if not viewports:
            # No viewport provided — default to Laptop preset
            preset = VIEWPORT_PRESETS[ViewportNickname.LAPTOP]
            width = preset["width"]
            height = preset["height"]
            await page.set_viewport_size({"width": width, "height": height})
            self.current_viewport = Viewport(
                nickname=ViewportNickname.LAPTOP,
                width=width,
                height=height
            )
            return page

        # Use the first viewport as default
        first = viewports[0]

        width = first.width
        height = first.height

        if (not width or not height) and first.nickname:
            preset = VIEWPORT_PRESETS[first.nickname]
            width = preset["width"]
            height = preset["height"]

        if width and height:
            await page.set_viewport_size({"width": width, "height": height})
            self.current_viewport = Viewport(
                nickname=first.nickname,
                width=width,
                height=height
            )
        else:
            self.current_viewport = None

        return page

    async def extract_navigation_links(self, navigation_links:List[NavigationLink]):
        screen_states_map:ExistingScreenStateMap= self.get_known_screen_states_map()
        llm_output:NewLinksLLMOutput=await get_new_links(screen_states_map,navigation_links)
        try:
            logger.info(f"Identified new unexplored pages: {llm_output.model_dump_json()}")
        except Exception as e:
            logger.error("Error parsing log: %s", e)
        screen_details = []
        if(llm_output.newScreensMap):
            for url, screen_info in llm_output.newScreensMap.items():
                if screen_info.significance is not None and screen_info.significance >= 2:
                    state_detail=ScreenStateDetail(state="")
                    screen_details.append(ScreenDetail(
                        name=screen_info.name, 
                        url=get_normalized_url(url),
                        type=screen_info.type,
                        states=[state_detail],
                        description=None,
                        displayMetadata=None,
                        explorationStatus=ScreenExplorationStatus.NOT_EXPLORED,
                        significance=screen_info.significance
                    ))
            await self.handle_unexplored_screens_found(self.screen_state,screen_details)

    async def on_agent_done(self, result):
        await self._update_agent_journey_log(True,False)
        logger.info(f"Agent completed!")

    async def record_user_action(self, agent_output: AgentOutput, current_browser_state: BrowserStateSummary, page):
        try:
            actual_actions, selector_map = extract_actions_and_selector_map(agent_output, current_browser_state)
            llm_response = await get_agent_action_code_units(actual_actions, selector_map)
            
            self.credits_used = self.credits_used + 1
            self.on_credits_used(1)
            self.last_user_action_millis = int(time.time() * 1000)

            # Create a StepExecution object with the element ID
            for agent_code_unit, action in zip(llm_response.codeUnits, actual_actions):
                agent_code_unit.agentCode = json.dumps(action.model_dump() if hasattr(action, "model_dump") else action)
                step_execution = ExecutionStepResult(
                    codeUnit=agent_code_unit,
                    status=ExecutionStepStatus.PASSED
                )
                self.current_state_exec_items.append(agent_code_unit)
                self.steps.append(agent_code_unit)
                
                # Log the step execution in JourneyLogItem
                step_id = str(uuid.uuid4())
                self.last_step_screenshot_path, local_path = await capture_and_upload_screenshot(self.browser_session,
                     page, getattr(self.task, 'exploration_id', None), self.job_id, step_id
                )
                log_item = JourneyLogItem(
                    id=step_id,
                    stepExecution=step_execution,
                    itemType=JourneyLogItemType.STEP_EXECUTION,
                    screenState=self.screen_state,
                    screenshotPath=self.last_step_screenshot_path,
                    viewport=self.current_viewport,
                    startTimestampMillis=self.last_user_action_millis,
                    endTimestampMillis=self.last_user_action_millis,
                    consoleLogs=self.console_watcher.get_console_logs_since(self.last_console_log_record_timestamp) if self.console_watcher else None
                )
                self.last_console_log_record_timestamp = self.last_user_action_millis                
                self.last_user_action_millis += 1
                self.log_items.append(log_item)

            await self._update_agent_journey_log()
        except Exception as e:
            logger.error("Error recording user action", exc_info=e)


    async def analyze_dom(self, page):
        if self.task and self.task.journey_type==RecommendedJourneyType.SCENARIOS_CHECK:
            return
        try:
            if not self.bug_capture_settings or DataSource.DOM_SOURCE not in self.bug_capture_settings.sources:
                logger.info("Not analyzing DOM since not in the data sources")
                return
            logger.info("Analyzing DOM for bugs")
            if(not self.screen_state or not self.screen_state.name):
                logger.info("Skipping DOM analysis since no screen state")
                return
            should_analyze:bool=self.should_visual_analyze_screen(self.screen_state)
            if(should_analyze):
                step_id:str=await self.start_bug_capture(DataSource.DOM_SOURCE)
                html = await get_llm_friendly_dom(page)
                llm_response: BugCaptureWithLLMMetadata = await analyze_visual_issues(html, [step.description for step in self.steps])
                bug_capture :BugCapture= llm_response.result if llm_response.result else BugCapture()
                self.on_tokens_used(llm_response.metadata.totalTokens if llm_response.metadata else 0)
                self.last_step_screenshot_path,_=await capture_and_upload_screenshot(self.browser_session,page,self.exploration_id,self.current_journey_execution_id,step_id)
                await self.end_bug_capture(step_id,bug_capture)
                self.report_visual_analyzed_screen(self.screen_state)
                await self._update_agent_journey_log(False, False)
        except Exception as e:
            logger.error("Error during DOM analysis: %s", e)
        
    async def start_bug_capture(self,analyzedDataSource:DataSource):
        step_id = str(uuid.uuid4())
        start_time=int(time.time()*1000)
        self.log_items.append(JourneyLogItem(
            id=step_id,
            startTimestampMillis=start_time,
            itemType=JourneyLogItemType.BUG_CAPTURE,
            screenState=self.screen_state,
            screenshotPath=self.last_step_screenshot_path,
            bugCaptureReport=BugCaptureReport(categoryReport=[],analyzedSource=analyzedDataSource)
        ))
        await self._update_agent_journey_log()
        return step_id

    async def end_bug_capture(self, step_id: str, bug_capture: BugCapture) -> None:
        credits_for_step = 1
        if bug_capture.analyzed_source == DataSource.DOM_SOURCE:
            credits_for_step = 2
        self.credits_used += credits_for_step
        self.on_credits_used(credits_for_step)
        for bug in bug_capture.bugs:
            bug.bug_hash = calculate_bug_hash(bug)
            bug.screen = self.screen_state.name if self.screen_state else None
            bug.screen_state=self.screen_state.state if self.screen_state and self.screen_state.state else None

        # Remove ignored bugs
        bug_capture.bugs = [
            bug for bug in bug_capture.bugs
            if not self.ignored_bug_hashes or bug.bug_hash not in self.ignored_bug_hashes
        ]

        if self.screen_state:
            new_bugs: List[Bug] = bug_capture.bugs
            if self.handle_bugs_discovered:
                new_bugs = await self.handle_bugs_discovered(
                    self.screen_state,
                    self.job_id,
                    bug_capture.bugs
                )

            for bug in new_bugs:
                if bug.severity == 3:
                    self.high_bugs += 1
                elif bug.severity == 2:
                    self.med_bugs += 1
                elif bug.severity == 1:
                    self.low_bugs += 1

            bug_capture_report = get_bug_capture_report(new_bugs)
            if bug_capture.analyzed_source:
                bug_capture_report.analyzedSource = bug_capture.analyzed_source

            log_item = next((log for log in self.log_items if log.id == step_id), None)
            if log_item:
                log_item.screenshotPath=self.last_step_screenshot_path
                log_item.bugCaptureReport = bug_capture_report
                log_item.endTimestampMillis = int(time.time() * 1000)
                if self.current_viewport:
                    log_item.viewport = self.current_viewport

            await self._update_agent_journey_log()

    async def analyze_screenshot(self, page: Page):
        if self.task and self.task.journey_type == RecommendedJourneyType.SCENARIOS_CHECK:
            return

        try:
            if not self.bug_capture_settings or DataSource.SCREENSHOT_SOURCE not in self.bug_capture_settings.sources:
                logger.info("Not analyzing Screenshot since not in the data sources")
                return

            if not self.screen_state or not self.screen_state.name:
                logger.info("Skipping Screenshot analysis since no screen state")
                return

            if not self.should_visual_analyze_screenshot(self.screen_state):
                return

            logger.info("Analyzing Screenshot for bugs")

            # Always use a non-empty list of viewports
            viewports = self.viewport_config.viewports if self.viewport_config and self.viewport_config.viewports else [
                Viewport(nickname=ViewportNickname.LAPTOP)
            ]

            def resolve_viewport(vp: Viewport) -> Optional[dict]:
                width = vp.width
                height = vp.height
                if (not width or not height) and vp.nickname:
                    preset = VIEWPORT_PRESETS.get(vp.nickname)
                    if preset:
                        width = preset["width"]
                        height = preset["height"]
                return {"width": width, "height": height} if width and height else None

            original_viewport = resolve_viewport(viewports[0])

            for i, vp in enumerate(viewports):
                size = resolve_viewport(vp)
                if not size or not isinstance(size.get("width"), int) or not isinstance(size.get("height"), int):
                    continue
                await page.set_viewport_size({"width": size["width"], "height": size["height"]})
                await page.wait_for_timeout(200)
                self.current_viewport = vp

                step_id = str(uuid.uuid4())
                self.last_user_action_millis = int(time.time() * 1000)

                if self.task and self.task.exploration_id: 
                    self.last_step_screenshot_path, local_path = await capture_and_upload_screenshot(
                        self.browser_session,
                        page,
                        getattr(self.task, 'exploration_id', None),
                        self.job_id,
                        step_id
                    )

                # If this is not the first viewport, log a resize step using the captured screenshot path
                if i > 0:
                    if vp.nickname:
                        description = f"Resize viewport to {vp.nickname.name.lower()}"
                    else:
                        description = f"Resize viewport to {size['width']}x{size['height']}"                    
                    semantic_code = f"await page.setViewportSize({{ width: {size['width']}, height: {size['height']} }});"

                    log_item = JourneyLogItem(
                        id=step_id,
                        itemType=JourneyLogItemType.STEP_EXECUTION,
                        screenState=self.screen_state,
                        screenshotPath=self.last_step_screenshot_path,
                        startTimestampMillis=self.last_user_action_millis,
                        endTimestampMillis=self.last_user_action_millis,
                        viewport=vp,
                        stepExecution=ExecutionStepResult(
                            codeUnit=AgentCodeUnit(
                                description=description,
                                semanticCode=semantic_code
                            ),
                            status=ExecutionStepStatus.PASSED
                        )
                    )
                    self.log_items.append(log_item)
                    await self._update_agent_journey_log(False, False)
                # LLM-based bug detection
                bug_capture_step_id = await self.start_bug_capture(DataSource.SCREENSHOT_SOURCE)
                llm_response: BugCaptureWithLLMMetadata = await detect_visual_bugs_from_image(local_path, size)
                bug_capture: Optional[BugCapture] = getattr(llm_response, 'result', None)
                if bug_capture is not None:
                    await self.end_bug_capture(bug_capture_step_id, bug_capture)
                self.report_visual_analyzed_screenshot(self.screen_state)

            # Restore original viewport at the end
            if original_viewport:
                await page.set_viewport_size({"width": original_viewport["width"], "height": original_viewport["height"]})
                self.current_viewport=viewports[0]

        except Exception as e:
            logger.error("Error during Screenshot analysis:", exc_info=e)

        

    async def analyze_network(self,page:Page) -> None:
        if self.task.journey_type==RecommendedJourneyType.SCENARIOS_CHECK:
            return
        try:
            # Analyze for issues using network activity
            if not self.bug_capture_settings or DataSource.NETWORK_SOURCE not in self.bug_capture_settings.sources:
                logger.info("Not analyzing Network since not in the data sources")
                return
            logger.info("Analyzing Network for bugs")
            request_response_pairs = self.network_watcher.get_network_logs_since(self.last_user_action_millis) if self.network_watcher else None

            filtered_pairs = (
                [clean_request_response_pair(pair) for pair in request_response_pairs if self.should_analyze_api_call(pair)]
                if request_response_pairs and self.should_analyze_api_call
                else []
            )[:20]

            if filtered_pairs:
                logger.info("Analyzing Network for issues")
                step_id = await self.start_bug_capture(DataSource.NETWORK_SOURCE)
                llm_result: BugCaptureWithLLMMetadata = await analyze_request_response_pairs(filtered_pairs,[step.description for step in self.steps])
                bug_capture = llm_result.result or BugCapture(bugs=[])
                await self.on_tokens_used(llm_result.metadata.totalTokens)
                await self.end_bug_capture(step_id,bug_capture)
                if self.report_analyzed_api_calls:
                    self.report_analyzed_api_calls(filtered_pairs)
        except Exception as e:
            logger.error("Error during Network analysis:",e)

    async def analyze_console(self,page:Page):
        if self.task.journey_type==RecommendedJourneyType.SCENARIOS_CHECK:
            return    
        try:
            if not self.bug_capture_settings or DataSource.CONSOLE_SOURCE not in self.bug_capture_settings.sources:
                logger.info("Not analyzing Console since not in the data sources")
                return
            logger.info("Analyzing Console for bugs")
            console_logs: List[ConsoleLogEntry] = self.console_watcher.get_console_logs_since(self.last_user_action_millis)
            if(len(console_logs)>0):
                logger.info("Found console logs")
                step_id:str=await self.start_bug_capture(DataSource.CONSOLE_SOURCE)
                llm_result: BugCaptureWithLLMMetadata = await analyze_console_logs(console_logs, [step.description for step in self.steps])
                bug_capture :BugCapture= llm_result.result or BugCapture(bugs=[])
                await self.on_tokens_used(llm_result.metadata.totalTokens)
                await self.end_bug_capture(step_id,bug_capture)
        except Exception as e:
            logger.error("Error during Console analysis:",e)


    async def analyze_screen(self, page: Page):
        if not self.task:
            return
        try:
            url_changed=False
            if self.current_url != page.url:
                url_changed=True
            self.current_url = page.url
            if(self.current_screen_updated_timestamp>(int(time.time()*1000)-500)):
                # debounce - not changing screen within 500ms
                return False
            self.current_screen_updated_timestamp=int(time.time()*1000)
            aria_snapshot = await page.locator('body').aria_snapshot()
            if(not aria_snapshot.strip()):
                return False
            screen_detail_output=await summarize_page(aria_snapshot,self.current_url,self.get_known_screen_states_map(),[step.description for step in self.steps])
            if screen_detail_output and screen_detail_output.name and screen_detail_output.state:
                screen_state = ScreenState(name=screen_detail_output.name, state=screen_detail_output.state)
                if(not self.screen_state or (self.screen_state.name!=screen_state.name or self.screen_state.state!=screen_state.state)):
                    source_map = SourceMap()
                    release_label="local_default"
                    page_snapshot=await get_llm_friendly_dom(page)
                    await self.update_screen_state(screen_state,page_snapshot, screen_detail_output, source_map,release_label)
                    # Analyze DOM for the new screen state
                    if not self.task.test_location or (self.screen_state and self.task.test_location.screenName==self.screen_state.name):
                        await self.analyze_screenshot(page)
                        await self.analyze_dom(page)
                    return True
                else:
                    return url_changed
            else:
                return url_changed
        except Exception as e:
            logger.error("Exception during screen analyze: %s", e)
            return False

    def get_agent_task(self):
        initial_url = self.task.initial_url if self.task and hasattr(self.task, "initial_url") else ""
        general_instructs=f"""
            You are a QA agent testing a webapp. 
            The site under test is: {initial_url}. Navigate to it first.\n
            Never go out of the initial domain. Do not search google etc.\n
            Do not attempt to sign up / reset password etc. since these flows typically require access to external email boxes, phone etc.
            If valid login credentials are not provided, do not assume valid credentials.
            If valid credentials are provided, assume that they do work. If you run in to login issues with valid creds, try again. It is likely that you may have missed entering values correctly or pressing the login / sign in buttons and waiting sufficient time.
            If accidentally moved out of the domain, go back.
            
            # Important controller callback functions:
                - If an unexpected behavior is observed, such as an empty list that should not be empty, a UI lacking feedback, an unexpected error message, etc. — report them with capture_bug. Only use this callback when reporting an unexpected bug - not for reporting a test scenario evaluation result. Use the report_test_scenario_result callback for that\n
                - When a test scenario is completed, report the test scenario result (whether expectation is met or not) with report_test_scenario_result.
                    Use the following enum values for result_status when calling report_test_scenario_result:
                    class ScenarioTestResult(IntEnum):
                        UNTESTED = 1
                        TESTED_WORKING = 2
                        TESTED_NOT_WORKING = 3
                        IGNORED_TEST_SCENARIO = 4

            If you are in blank page (about:blank), it is very likely that you did not navigate to the starting url. First navigate to {initial_url}.
            Use the following input values when applicable:\n {self.test_data_prompt}\n
            If you decide to abandon the exploration due to blocker bugs, do not continue the exploration. Instead, stop the agent operation.\n
        """
        
        specific_instructs=""
        if(self.task and self.task.journey_type and self.task.journey_type==RecommendedJourneyType.EXPLORATION):
            specific_instructs=f"""
                The webapp under testing has been explored before by an AI agent previously. It may be incomplete. The objective is to uncover more ground of the webapp. Below is an instruction generated by a planner agent for you to follow. Small deviations to meet the overall objective is ok.
                {self.task and self.task.journey_to_run and self.task.journey_to_run.model_dump_json()}
            """
            if(self.task.test_location):
                specific_instructs=f"""
                    The webapp under testing has been explored before by an AI agent. Now, the user wants to focus on a specific screen / state in the webapp to test. The following instructions detail how to get to the target screen state, and the testing to do on that screen. Follow the steps as outlined.
                    {self.task and self.task.journey_to_run and self.task.journey_to_run.model_dump_json()}
                """
        elif(self.task and self.task.journey_type and self.task.journey_type==RecommendedJourneyType.EXISTING_JOURNEY):
            specific_instructs=f"""
                {self.task and self.task.journey_to_run and  self.task.journey_to_run.model_dump_json()}
            """
        elif(self.task and self.task.journey_type and self.task.journey_type==RecommendedJourneyType.SCENARIOS_CHECK):
            specific_instructs=f"""
                A planner agent has taken a look at test scenarios currently untested for the webapp and has constructed a list of test scenarios to test through a traversal in the app (a user journey).

                Steps to take are as below. If the next step is a test scenario, and some actions are needed to be done to get to that state, do them before attempting the test scenario described. 
                If the next test scenario is not feasible to test due to current state of the webapp, then ignore it and move on to the next feasible one and so on.

                Journey title:{self.task and self.task.journey_to_run and self.task.journey_to_run.title}\n

                Steps to take: {self.task and self.task.journey_to_run and self.task.journey_to_run.steps}
            """
        return f"{general_instructs}\n{specific_instructs}"
    