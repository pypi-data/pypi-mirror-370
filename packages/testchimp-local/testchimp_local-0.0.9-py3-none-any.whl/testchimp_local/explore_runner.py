import time
import asyncio
import json
import os
import uuid
from typing import Optional, Dict, Any, Tuple,List,cast,Set, Union, Callable, AsyncGenerator, Awaitable
from .datas import ScreenStateVisitResult,AppMindMapSummary,AwareUiTestListLLMOutput,Bug, BugCountSummary, BugSeverity, ExplorationConfig, ExplorationResult, ExplorationStatus,NeighbourScreenState,AgentCodeUnitList,ExecutionStepResultSummary, RecommendedJourneyType,TestScenario,ScreenStateDetail,ElementSignificance, ScreenDetail,ScreenExplorationStatus,Screenshot,SourceMap,LLMScreenDetailOutput,AgentCodeUnit,ScreenStates,AppMindMap,ScreenState,LocalExplorationTask, AgentRunnerTask, PromptBasedConfig, map_viewport_nicknames, map_data_sources, ExistingScreenStateMap,RequestResponsePair
from .agent_runner import AgentRunner
from .browser_context import launch_browser_context
from .openai_facade import summarize_app_mindmap, summarize_execution_step_results,generate_test_cases
from .web_utils import get_endpoint_key,get_normalized_url,extract_navigation_links_from_page
from .agent_utils import get_screen_state_hash
from .feature_facade import FeatureFacade, OrgStatus, OrgTier, RecommendNextJourneyRequest, RecordStartExplorationRequest, RecordEndExplorationRequest, RecordStartJourneyExecutionRequest, RecordEndJourneyExecutionRequest, InsertBugsRequest, GetAppMindMapRequest, InsertJourneyRequest, UpdateExplorationResultRequest, UpsertMindMapRequest, InsertTestCasesRequest, InsertTestScenariosRequest, InsertTestScenariosResponse, get_feature_facade_instance
from collections import defaultdict
from . import config_help
import logging

logger = logging.getLogger(__name__)

class ExploreRunner:
    def __init__(self, openai_api_key: Optional[str] = None):
        self.openai_api_key = openai_api_key
        self.agent_runner: Optional[AgentRunner] = None
        self.browser_context = None
        self.exploration_id=None
        self.project_id=None
        self.app_mind_map=AppMindMap()
        self.ignored_bug_hashs=set()
        self.initial_url=""
        self.tokens_used=0
        self.credits_used=0
        self.app_release_label=None
        self.environment="QA"  # Default environment
        self.current_journey_execution_id: Optional[str] = None
        self.max_credits=50
        self.max_journeys=1
        self.remaining_credits=50
        self.remaining_journeys=1
        self.bug_count_summary=BugCountSummary()
        
        self.screen_state_bugs: dict[str, set[str]] = defaultdict(set)
        self.screen_states:dict[str,ScreenState]=defaultdict()
        self.visited_screen_states=set()
        self.visual_analyzed_screens = set()
        self.screenshot_analyzed_screens=set()
        self.analyzed_endpoints=set()
        self.known_screen_states_map=ExistingScreenStateMap()
        self.force_stopped=False

        
    async def end_exploration(self):
        """End the current exploration and record it in the backend"""
        feature_facade = get_feature_facade_instance()
        if self.exploration_id and feature_facade:
            try:
                await self.update_exploration_result(ExplorationStatus.COMPLETED_EXPLORATION)                
                request = RecordEndExplorationRequest(explorationId=self.exploration_id)
                await asyncio.to_thread(feature_facade.record_end_exploration, request)
                logger.info(f"Exploration {self.exploration_id} ended successfully")
            except Exception as e:
                logger.info(f"Error ending exploration: {e}")

    async def run_exploration(self, exploration_task: LocalExplorationTask) -> Dict[str, Any]:
        """
        Main entry point for running an exploration task
        """
        try:
            feature_facade = get_feature_facade_instance()
            if feature_facade is None:
                raise RuntimeError("FeatureFacade is not initialized. Call set_feature_facade before using ExploreRunner.")
            self.task=exploration_task
            # Authenticate and get orgTier/orgPlan
            auth_response = feature_facade.authenticate()
            org_tier = feature_facade.org_tier
            org_status=feature_facade.org_status
            if org_status == OrgStatus.INACTIVE_ORG:
                logger.error("Your free trial with TestChimp has expired. Please upgrade at: https://testchimp.io to continue")
                return {"error": "Your free trial with TestChimp has expired. Please upgrade at: https://testchimp.io to continue"}
            # Initialize exploration parameters
            self.exploration_id=exploration_task.explorationId
            self.project_id = os.getenv("TESTCHIMP_PROJECT_ID")
            self.app_release_label=exploration_task.appReleaseLabel if exploration_task.appReleaseLabel else "default"
            self.screen_release_label="default"
            self.environment = exploration_task.environment if exploration_task.environment else "QA"
    
            
            # --- FILTERING BASED ON ORG TIER ---
            filtered = False
            config = exploration_task.explorationConfig
            # Filter screenshot data source if orgTier is FREE_TIER
            if org_tier == OrgTier.FREE_TIER and config and config.bugCaptureSettings:
                before = list(config.bugCaptureSettings.sources)
                config.bugCaptureSettings.sources = [s for s in config.bugCaptureSettings.sources if getattr(s, 'name', s) != 'SCREENSHOT_SOURCE' and s != 2]
                if len(before) != len(config.bugCaptureSettings.sources):
                    logger.info("[ORG TIER: FREE] Screenshot data source is not allowed. Filtering out SCREENSHOT_SOURCE from bugCaptureSettings.sources.")
                    filtered = True
            # Filter viewports if orgTier is FREE_TIER
            if org_tier == OrgTier.FREE_TIER and config and config.viewportConfig and config.viewportConfig.viewports:
                before = list(config.viewportConfig.viewports)
                config.viewportConfig.viewports = [v for v in config.viewportConfig.viewports if (getattr(v, 'nickname', None) == 1 or getattr(v, 'nickname', None) == 'LAPTOP')]
                if len(before) != len(config.viewportConfig.viewports):
                    logger.info("[ORG TIER: FREE] Only 'laptop' viewport is allowed. Filtering out other viewports from viewportConfig.viewports.")
                    filtered = True

            # Record start of exploration
            max_credits=exploration_task.explorationConfig.maxCredits if exploration_task.explorationConfig and exploration_task.explorationConfig.maxCredits else 50
            max_journeys=exploration_task.explorationConfig.maxJourneys if exploration_task.explorationConfig and exploration_task.explorationConfig.maxJourneys else 1

            await self._record_start_exploration(max_credits,max_journeys)
            logger.info(f"EXPLORATION STARTED. YOU CAN FOLLOW THE EXPLORATION AT: https://prod.testchimp.io/exploration?id={self.exploration_id}&project_id={self.project_id}")
            
            # Fetch current mindmap from backend
            await self._fetch_app_mindmap()
            
            # Run exploration based on config type
            if exploration_task.explorationConfig and exploration_task.explorationConfig.scriptConfig:
                await self.run_script_based_exploration(exploration_task)
            elif exploration_task.explorationConfig and exploration_task.explorationConfig.promptConfig:
                self.initial_url=exploration_task.explorationConfig.promptConfig.url
                await self._run_prompt_based_exploration(exploration_task)
            else:
                raise ValueError("Only PromptBasedConfig and ScriptConfig are currently supported")

            if(self.app_mind_map.screens and self.app_mind_map.initialUrl):
                llm_result:AppMindMapSummary=await summarize_app_mindmap(self.app_mind_map)
                self.app_mind_map.appDetail=llm_result.summary or ""
                feature_facade.upsert_mindmap(UpsertMindMapRequest(mindmap=self.app_mind_map,environment=self.environment))
            return {"status":"success"}
        except Exception as e:
            logger.info(f"Error during exploration {e}")
            return {"status": "error", "message": str(e)}
        finally:
            # End exploration
            await self.end_exploration()
            
            # Cleanup
            if self.browser_context:
                await self.browser_context.close()

    def on_tokens_used(self,tokens):
        self.tokens_used=self.tokens_used + tokens

    def on_credits_used(self,credits):
        self.credits_used=self.credits_used+credits

    def get_exploration_credits_used(self):
        return self.credits_used

    async def _record_start_exploration(self,max_credits:int,max_journeys:int):
        """Record the start of exploration in the backend"""
        feature_facade = get_feature_facade_instance()
        if feature_facade and self.exploration_id:
            try:
                request = RecordStartExplorationRequest(
                    explorationId=self.exploration_id,
                    environment=self.environment,
                    maxCredits=max_credits,
                    maxJourneys=max_journeys,
                    explorationConfig=self.task.explorationConfig
                )
                response = await asyncio.to_thread(feature_facade.record_start_exploration, request)
                # Set max_credits and max_journeys from the response
                if response.maxCredits is not None:
                    self.max_credits = response.maxCredits
                    self.remaining_credits=self.max_credits
                if response.maxJourneys is not None:
                    self.max_journeys = response.maxJourneys
                    self.remaining_journeys=self.max_journeys
                logger.info(f"Exploration {self.exploration_id} started successfully")
            except Exception as e:
                    self.max_credits = 0
                    self.max_journeys=0
                    logger.info(f"Exploration {self.exploration_id} throttled")

    async def _fetch_app_mindmap(self):
        """Fetch the current app mindmap from the backend"""
        feature_facade = get_feature_facade_instance()
        if feature_facade:
            try:
                request = GetAppMindMapRequest(environment=self.environment)
                response = await asyncio.to_thread(feature_facade.get_app_mindmap, request)
                if response.mindMap:
                    # Convert the dict response to AppMindMap object
                    self.app_mind_map = AppMindMap(**response.mindMap)
                    logger.info(f"Fetched app mindmap with {len(self.app_mind_map.screens or [])} screens")
                else:
                    logger.info("No existing mindmap found, starting with empty mindmap")
            except Exception as e:
                logger.info(f"Error fetching app mindmap: {e}")

    async def _record_start_journey_execution(self, journey_id: str, execution_id: str, max_credits: int) -> Optional[int]:
        """Record the start of a journey execution"""
        feature_facade = get_feature_facade_instance()
        if feature_facade and self.exploration_id:
            try:
                request = RecordStartJourneyExecutionRequest(
                    explorationId=self.exploration_id,
                    executionId=execution_id,
                    journeyId=journey_id,
                    maxCredits=max_credits
                )
                response = await asyncio.to_thread(feature_facade.record_start_journey_execution, request)
                self.current_journey_execution_id = execution_id
                logger.info(f"Journey execution {execution_id} started successfully")
                # Return the maxCredits from the response
                return response.maxCredits if response and hasattr(response, 'maxCredits') else 0
            except Exception as e:
                logger.info(f"Error recording start of journey execution: {e}")
                return 0
        return 0

    async def _record_end_journey_execution(self, execution_id: str):
        """Record the end of a journey execution"""
        feature_facade = get_feature_facade_instance()
        if feature_facade and self.exploration_id:
            try:
                request = RecordEndJourneyExecutionRequest(
                    explorationId=self.exploration_id,
                    executionId=execution_id
                )
                await asyncio.to_thread(feature_facade.record_end_journey_execution, request)
                self.current_journey_execution_id = None
                logger.info(f"Journey execution {execution_id} ended successfully")
            except Exception as e:
                logger.info(f"Error recording end of journey execution: {e}")

    async def _setup_browser_context(self, exploration_task: LocalExplorationTask):
        """Setup browser context based on the exploration task"""
        browser_config = {}
        
        if exploration_task.browserContext:
            browser_config = {
                "mode": exploration_task.browserContext.mode.name.lower() if exploration_task.browserContext.mode else "cdp",
                "cdpUrl": exploration_task.browserContext.cdpUrl,
                "headless": exploration_task.browserContext.headless
            }
        else:
            # Default config
            browser_config = {
                "mode": "launch"
            }
        
        self.browser_context = await launch_browser_context(browser_config)
    
    async def _init_for_journey(self,exploration_task):
                    # Initialize browser context
        await self._setup_browser_context(exploration_task)
        
        # Create agent runner with the browser context and all callbacks
        self.agent_runner = AgentRunner(
            openai_api_key=self.openai_api_key,
            handle_bugs_discovered=self.handle_bugs_discovered,
            handle_screen_state_visited=self.handle_screen_state_visited,
            handle_unexplored_screens_found=self.handle_unexplored_screens_found,
            should_visual_analyze_screen=self.should_visual_analyze_screen,
            should_visual_analyze_screenshot=self.should_visual_analyze_screenshot,
            should_analyze_api_call=self.should_analyze_api_call,
            report_visual_analyzed_screen=self.report_visual_analyzed_screen,
            report_visual_analyzed_screenshot=self.report_visual_analyzed_screenshot,
            report_analyzed_api_calls=self.report_analyzed_api_calls,
            get_known_screen_states_map=self.get_known_screen_states_map,
            on_tokens_used=self.on_tokens_used,
            on_credits_used=self.on_credits_used,
            get_exploration_credits_used=self.get_exploration_credits_used,
            get_release_labels=self.get_release_labels
        )

    async def _run_prompt_based_exploration(self, exploration_task: LocalExplorationTask) -> Dict[str, Any]:
        """Run exploration using PromptBasedConfig"""
        if not exploration_task.explorationConfig or not exploration_task.explorationConfig.promptConfig:
            raise ValueError("PromptBasedConfig is required")
            
        feature_facade = get_feature_facade_instance()
        if feature_facade is None:
            raise ValueError("Feature Facade not initialized")

        prompt_config = exploration_task.explorationConfig.promptConfig
    
        all_results = []
        
        for journey_index in range(self.max_journeys):
            if(self.remaining_credits<=0):
                logger.info("Credits exhausted for this exploration")
                break
            logger.info(f"Starting journey {journey_index + 1} of {self.max_journeys}")
            response = await asyncio.to_thread(
                feature_facade.recommend_next_journey,
                RecommendNextJourneyRequest(exploration_id=self.exploration_id)
            )
            if not response or not response.journeyId or response.recommendationType==RecommendedJourneyType.END_EXPLORATION:
                logger.info("Ending exploration since no next journey suggested by planner agent")
                break;

            await self._init_for_journey(exploration_task)
            if self.agent_runner is None:
                raise RuntimeError("Agent runner not initialized")
                            
            # Generate a journey execution ID for this exploration run
            journey_execution_id = str(uuid.uuid4())
            
            requested_credits_for_journey = max(20, self.remaining_credits // self.remaining_journeys)
            journey_id=response.journeyId
            max_credits_for_journey = await self._record_start_journey_execution(journey_id, journey_execution_id, requested_credits_for_journey)
            max_credits_for_journey=min(requested_credits_for_journey,max_credits_for_journey if max_credits_for_journey else 20)
            exploration_config:ExplorationConfig=exploration_task.explorationConfig
            agent_task = AgentRunnerTask(
                exploration_id=self.exploration_id,
                execution_id=journey_execution_id,
                journey_to_run=response.journey,
                journey_type=response.recommendationType,
                initial_url=prompt_config.url,
                test_data_inputs=prompt_config.testDataPrompt,
                bug_capture_settings=exploration_config.bugCaptureSettings,
                viewport_config=exploration_config.viewportConfig,
                url_regex_to_capture=exploration_config.urlRegexToCapture,
                max_credits_for_journey=max_credits_for_journey,
                pre_journey_script=exploration_config.preJourneyScriptPath,
                post_journey_script=exploration_config.postJourneyScriptPath,
                config_file_path=exploration_task.explorationConfigFilePath
            )

            try:
                # Run the agent
                result = await self.agent_runner.run_agent_task(agent_task, self.browser_context)
                
                journey_result = {
                    "status": "success",
                    "result": result,
                    "exploration_type": "prompt_based",
                    "journey_id": journey_id,
                    "journey_execution_id": journey_execution_id,
                    "journey_index": journey_index + 1
                }
                all_results.append(journey_result)
                
            except Exception as e:
                logger.info(f"Error in journey {journey_index + 1}: {e}")
                journey_result = {
                    "status": "error",
                    "error": str(e),
                    "journey_id": journey_id,
                    "journey_execution_id": journey_execution_id,
                    "journey_index": journey_index + 1
                }
                all_results.append(journey_result)
            finally:
                # Record end of journey execution
                await self._record_end_journey_execution(journey_execution_id)
                logger.info(f"EXPLORATION COMPLETED. YOU CAN VIEW THE RESULTS AT: https://prod.testchimp.io/exploration?id={self.exploration_id}&project_id={self.project_id}")
                self.remaining_credits=self.max_credits-self.credits_used
                self.remaining_journeys=self.remaining_journeys-1
                if self.browser_context:
                    await self.browser_context.close()
        
        return {
            "status": "completed",
            "total_journeys": self.max_journeys,
            "journey_results": all_results
        }

    def update_known_screen_state_map(self) -> None:
        """
        Update the `known_screen_states` attribute by extracting all screen names
        and their associated state strings from the current app mind map.
        """
        if not self.app_mind_map or not self.app_mind_map.screens:
            self.known_screen_states_map = ExistingScreenStateMap()
            return

        screen_states_map = defaultdict(list)
        for screen in self.app_mind_map.screens:
            state_names = [state.state or "" for state in screen.states or []]
            screen_states=ScreenStates(screen=screen.name, states=state_names)
            screen_states_map[get_normalized_url(screen.url)].append(screen_states)

            self.known_screen_states_map = ExistingScreenStateMap(screenStatesMap=dict(screen_states_map))
    
    # Callback functions for agent_runner
    async def handle_bugs_discovered(self, screen_state: ScreenState, journey_execution_id: str, bugs: List[Bug]):
        """Handle bugs discovered during exploration"""
        logger.info(f"Bugs discovered: {bugs}")
        screen_state_key = f"{screen_state.name}||{screen_state.state}"        
        feature_facade = get_feature_facade_instance()
        if feature_facade and self.exploration_id and bugs:
            try:
                if screen_state_key not in self.screen_state_bugs:
                    self.screen_state_bugs[screen_state_key] = set()

                bug_set: Set[str] = self.screen_state_bugs[screen_state_key]
                new_bugs: List[Bug] = []

                for bug in bugs:
                    if not bug.bug_hash:
                        continue  # Ignore bugs without a hash

                    if bug.bug_hash not in bug_set:
                        bug_set.add(bug.bug_hash)
                        new_bugs.append(bug)
                        self.update_bug_summary(bug.severity)

                request = InsertBugsRequest(
                    explorationId=self.exploration_id,
                    journeyId=journey_execution_id,
                    bugs=new_bugs,
                    screenName=screen_state.name if screen_state else None,
                    screenState=screen_state.state if screen_state else None,
                    environment=self.environment,
                    appReleaseId=self.app_release_label
                )
                
                await asyncio.to_thread(feature_facade.insert_bugs, request)
                logger.info(f"Successfully inserted {len(bugs)} bugs to backend")
                return new_bugs
            except Exception as e:
                logger.info(f"Error inserting bugs to backend: {e}")
                return []
            finally:
                await self.update_exploration_result(ExplorationStatus.IN_PROGRESS_EXPLORATION)
    
    async def handle_screen_state_visited(
        self,
        screen_url:str,
        current_snapshot: str,
        new_screen_state: ScreenState,
        old_screen_state: Optional[ScreenState],
        current_state_code_units: List[AgentCodeUnit],
        all_code_units: List[AgentCodeUnit],
        new_screen_detail: Optional[LLMScreenDetailOutput] = None,
        screenshot: Optional[Screenshot] = None,
        source_map: Optional[SourceMap] = None,
        screen_release_label: Optional[str] = None,
        journey_execution_id: Optional[str] = None,
        write_test_scenarios: bool = True
    ) -> ScreenStateVisitResult:
        key = get_screen_state_hash(new_screen_state)
        safe_source_map = source_map or SourceMap(relatedFiles=[])

        # Ensure feature_facade is available (guaranteed to be present)
        feature_facade = get_feature_facade_instance()
        if feature_facade is None:
            raise RuntimeError("Feature facade not initialized")

        if key not in self.screen_states:
            self.screen_states[key] = new_screen_state

        if key not in self.visited_screen_states:
            self.visited_screen_states.add(key)

        if not self.app_mind_map:
            self.app_mind_map = AppMindMap(initialUrl=self.initial_url or "", screens=[], inputValueCombinations=[])
        elif not isinstance(self.app_mind_map.screens, list):
            self.app_mind_map.screens = []

        if(screen_url and not self.initial_url):
            self.initial_url=screen_url

        screen_detail = next((s for s in self.app_mind_map.screens if s.name == new_screen_state.name), None)

        if screen_detail:
            if screen_detail.explorationStatus == ScreenExplorationStatus.NOT_EXPLORED:
                updated_screen_detail = ScreenDetail(
                    name=new_screen_detail.name if new_screen_detail else new_screen_state.name,
                    url=new_screen_detail.url if new_screen_detail else '',
                    type=new_screen_detail.type if new_screen_detail else '',
                    description=new_screen_detail.description if new_screen_detail else '',
                    states=[],
                    tags=new_screen_detail.tags if new_screen_detail else [],
                    isInitialScreen=False if old_screen_state else True,
                    significance=new_screen_detail.significance if new_screen_detail else ElementSignificance.MEDIUM_SIGNIFICANCE,
                    explorationStatus=ScreenExplorationStatus.PARTIALLY_EXPLORED
                )

                # Replace screen detail by matching name
                for idx, s in enumerate(self.app_mind_map.screens):
                    if s.name == screen_detail.name:
                        self.app_mind_map.screens[idx] = updated_screen_detail
                        screen_detail = updated_screen_detail
                        break

                # Remove placeholder neighbour screen links to this screen
                for screen in self.app_mind_map.screens:
                    for state_detail in screen.states:
                        state_detail.neighbourScreens = [
                            ns for ns in state_detail.neighbourScreens
                            if not (ns.screenState is not None and ns.screenState.name == updated_screen_detail.name and ns.screenState.state == "")
                        ]
        else:
            screen_detail = ScreenDetail(
                name=new_screen_detail.name if new_screen_detail else new_screen_state.name,
                url=new_screen_detail.url if new_screen_detail else '',
                type=new_screen_detail.type if new_screen_detail else '',
                description=new_screen_detail.description if new_screen_detail else '',
                significance=new_screen_detail.significance if new_screen_detail else ElementSignificance.MEDIUM_SIGNIFICANCE,
                tags=new_screen_detail.tags if new_screen_detail else [],
                states=[],
                isInitialScreen=False if old_screen_state else True,
                explorationStatus=ScreenExplorationStatus.PARTIALLY_EXPLORED
            )
            self.app_mind_map.screens.append(screen_detail)
        
        if not isinstance(screen_detail.states, list):
            screen_detail.states = []

        state_detail = next((s for s in screen_detail.states if s.state == new_screen_state.state), None)
        insert_response = None  # Initialize insert_response variable
        if not state_detail:
            state_detail = ScreenStateDetail(
                state=new_screen_state.state,
                elementGroups=new_screen_detail.elementGroups if new_screen_detail and new_screen_detail.elementGroups else [],
                testScenarios=None,
                neighbourScreens=[],
                sourceMap=safe_source_map,
            )
            screen_detail.states.append(state_detail)
            test_scenarios:List[TestScenario]=new_screen_detail.testScenarios if new_screen_detail and new_screen_detail.testScenarios else []
            if(len(test_scenarios)>0 and write_test_scenarios):
                test_cases_llm_output:AwareUiTestListLLMOutput=await generate_test_cases(new_screen_state,test_scenarios,all_code_units,current_snapshot)
                test_case_title_to_id_map = await asyncio.to_thread(
                    feature_facade.insert_test_cases, 
                    InsertTestCasesRequest(test_cases=test_cases_llm_output.testCases)
                )

                scenario_to_code_units = {}
                if test_cases_llm_output.testCases:
                    for test_case in test_cases_llm_output.testCases:
                        if test_case.testName and test_case.testName.name:
                            scenario_to_code_units[test_case.testName.name] = test_case.codeUnits or []

                # Convert CodeUnit to AgentCodeUnit for each test scenario
                test_scenarios_with_steps = []
                for scenario in test_scenarios:
                    if scenario.title and scenario.title in scenario_to_code_units:
                        # Use the specific code units from the corresponding test case
                        code_units = scenario_to_code_units[scenario.title]
                        agent_code_units = [AgentCodeUnit(code=cu.code, description=cu.description) for cu in code_units] if code_units else []
                        scenario.steps = agent_code_units
                    else:
                        # Fallback to empty steps if no matching test case found
                        scenario.steps = []
                    test_scenarios_with_steps.append(scenario)
                
                insert_response = await asyncio.to_thread(
                    feature_facade.insert_test_scenarios,
                    InsertTestScenariosRequest(
                        test_scenarios=test_scenarios_with_steps,
                        pre_steps=all_code_units,
                        screen_name=new_screen_state.name,
                        screen_state=new_screen_state.state or "",
                        test_case_title_to_id_map=test_case_title_to_id_map.insertedIds if test_case_title_to_id_map else {},
                        exploration_id=self.exploration_id,
                        journey_execution_id=journey_execution_id,
                        app_release_id=self.app_release_label
                    )
                )
        else:
            state_detail.elementGroups = new_screen_detail.elementGroups if new_screen_detail and new_screen_detail.elementGroups else state_detail.elementGroups
            state_detail.sourceMap = safe_source_map

        # --- Screenshot handling logic ---
        if screenshot:
            if state_detail.screenshots is None:
                state_detail.screenshots = []
            # Find index of screenshot with same viewport nickname
            idx = next((i for i, s in enumerate(state_detail.screenshots)
                        if s.viewport and screenshot.viewport and s.viewport.nickname == screenshot.viewport.nickname), None)
            if idx is not None:
                # Replace existing screenshot for this viewport
                state_detail.screenshots[idx] = screenshot
            else:
                # Add new screenshot for this viewport
                state_detail.screenshots.append(screenshot)
        # --- End screenshot handling logic ---

        if old_screen_state:
            filtered_code_units = [
                AgentCodeUnit(semanticCode=cu.semanticCode, description=cu.description)
                for cu in current_state_code_units
            ]            
            step_summary : ExecutionStepResultSummary= await summarize_execution_step_results(AgentCodeUnitList(codeUnits=filtered_code_units))

            self.tokens_used += step_summary.metadata.totalTokens if step_summary.metadata and step_summary.metadata.totalTokens else 0


            old_screen_detail = next((s for s in self.app_mind_map.screens if s.name == old_screen_state.name), None)
            old_state_detail = next((s for s in old_screen_detail.states if s.state == old_screen_state.state), None) if old_screen_detail else None
            if old_state_detail:
                if not isinstance(old_state_detail.neighbourScreens, list):
                    old_state_detail.neighbourScreens = []

                # Find all existing edges between this source and the target
                existing_edges = [
                    ns for ns in old_state_detail.neighbourScreens
                    if ns.screenState and
                    ns.screenState.name == new_screen_state.name and
                    ns.screenState.state == new_screen_state.state
                ]

                # Calculate current weight for this source-target pair
                max_weight = max((n.weight if n.weight is not None else 0) for n in existing_edges) if existing_edges else 0
                new_weight = max_weight + 1

                # Update weight on all existing edges between this source-target pair
                for edge in existing_edges:
                    edge.weight = new_weight

                # Add the new edge with the shared updated weight
                current_timestamp = int(time.time() * 1000)
                old_state_detail.neighbourScreens.append(
                    NeighbourScreenState(
                        screenState=new_screen_state,
                        actionSummary="\n".join(step_summary.steps or []),
                        weight=new_weight,
                        addedTimestampMillis=current_timestamp
                    )
                )

                # Clean up if more than 3 edges now exist between this source-target pair
                self._cleanup_excess_edges(old_state_detail.neighbourScreens, new_screen_state, max_edges=3)
    
        self.update_known_screen_state_map()
        self.app_mind_map.initialUrl=self.initial_url or ""
        if feature_facade and self.app_mind_map:
            feature_facade.upsert_mindmap(UpsertMindMapRequest(mindmap=self.app_mind_map,environment=self.environment))
        await self.update_exploration_result(ExplorationStatus.IN_PROGRESS_EXPLORATION)
        
        # Return the result with the new screen state and inserted test scenarios
        inserted_test_scenarios = insert_response.createdTestScenarios if insert_response and insert_response.createdTestScenarios else []
        return ScreenStateVisitResult(
            screenState=new_screen_state,
            insertedTestScenarios=inserted_test_scenarios
        )

    
    async def update_exploration_result(self, status: ExplorationStatus) -> None:
        result = ExplorationResult(
            bugCountSummary=self.bug_count_summary,
            screenStatesAnalyzed=list(self.screen_states.values()),
            tokensUsed=self.tokens_used
        )

        feature_facade = get_feature_facade_instance()
        if feature_facade:
            await asyncio.to_thread(
                feature_facade.update_exploration_result,
                UpdateExplorationResultRequest(
                    exploration_id=self.exploration_id,
                    result=result,
                    status=status
                )
            )
        

    def update_bug_summary(self, severity: Optional[BugSeverity]) -> None:
        if not severity:
            return
        if severity == BugSeverity.HIGH_SEVERITY:
            self.bug_count_summary.highSeverityBugs = (self.bug_count_summary.highSeverityBugs or 0) + 1
        elif severity == BugSeverity.MEDIUM_SEVERITY:
            self.bug_count_summary.medSeverityBugs = (self.bug_count_summary.medSeverityBugs or 0) + 1
        elif severity == BugSeverity.LOW_SEVERITY:
            self.bug_count_summary.lowSeverityBugs = (self.bug_count_summary.lowSeverityBugs or 0) + 1

    async def handle_unexplored_screens_found(
            self,
            old_screen_state: ScreenState,
            new_screen_details: List[ScreenDetail]
        ):
            # Find the old screen and state detail
            old_screen_detail = next((s for s in self.app_mind_map.screens if s.name == old_screen_state.name), None)
            old_state_detail = next((s for s in old_screen_detail.states if s.state == old_screen_state.state), None) if old_screen_detail else None

            # Get existing screen names
            existing_screen_names = {screen.name for screen in self.app_mind_map.screens}

            # Filter new screens to only those not already in the mind map
            filtered_new_screens = [screen for screen in new_screen_details if screen.name not in existing_screen_names]


            # Add new unexplored screens to the mind map
            self.app_mind_map.screens.extend(filtered_new_screens)

            # Append neighbour screen states to the old state's neighbourScreens
            if old_state_detail:
                neighbour_links = [
                    NeighbourScreenState(
                        screenState=ScreenState(name=screen.name, state=""),
                        actionSummary="Unexplored"
                    )
                    for screen in filtered_new_screens
                ]
                old_state_detail.neighbourScreens.extend(neighbour_links)
            self.update_known_screen_state_map()
            feature_facade = get_feature_facade_instance()
            if feature_facade and self.app_mind_map:
                feature_facade.upsert_mindmap(UpsertMindMapRequest(mindmap=self.app_mind_map,environment=self.environment))

    
    def should_visual_analyze_screen(self, screen_state: ScreenState) -> bool:
        return screen_state.name not in self.visual_analyzed_screens
    
    def should_visual_analyze_screenshot(self, screen_state: ScreenState) -> bool:
        return screen_state.name not in self.screenshot_analyzed_screens
    
    def should_analyze_api_call(self, pair: RequestResponsePair) -> bool:
        # Filter TestChimp ingress calls
        if "https://ingress.testchimp.io" in pair.url:
            return False
        key = get_endpoint_key(pair.method, pair.url)
        return key not in self.analyzed_endpoints
    
    def get_release_labels(self) -> Tuple[str, str]:
        return (
            self.app_release_label or "local_default",
            self.screen_release_label or "local_default"
        )
    
    def report_visual_analyzed_screen(self, screen_state: ScreenState):
        if screen_state.name:
            self.visual_analyzed_screens.add(screen_state.name)

    def report_visual_analyzed_screenshot(self, screen_state: ScreenState):
        if screen_state.name:
            self.screenshot_analyzed_screens.add(screen_state.name)

    def report_analyzed_api_calls(self, pairs: list[RequestResponsePair]) -> None:
        for pair in pairs:
            key = get_endpoint_key(pair.method, pair.url)
            self.analyzed_endpoints.add(key)

    def get_known_screen_states_map(self) -> ExistingScreenStateMap:
        return self.known_screen_states_map

    def _cleanup_excess_edges(self,
        neighbours: List[NeighbourScreenState],
        target_screen_state: ScreenState,
        max_edges: int = 3
    ):
        matching_edges = [
            ns for ns in neighbours
            if ns.screenState and ns.screenState.name == target_screen_state.name and ns.screenState.state == target_screen_state.state
        ]

        if len(matching_edges) > max_edges:
            # Sort by timestamp (oldest first, handle missing as 0)
            sorted_edges = sorted(matching_edges, key=lambda ns: ns.addedTimestampMillis or 0)
            neighbours.remove(sorted_edges[0])

    async def run_script_based_exploration(self, exploration_task: LocalExplorationTask) -> Dict[str, Any]:
        """
        Runs script-based exploration: for each file in scriptConfig.filePaths, runs AgentRunner with run_script param.
        """
        exploration_config = getattr(exploration_task, 'explorationConfig', None)
        if not exploration_config:
            logger.info("No explorationConfig provided.")
            return {"status": "error", "message": "No explorationConfig provided."}
        feature_facade = get_feature_facade_instance()
        if feature_facade is None:
            return {"status":"error"}
        script_config = getattr(exploration_config, 'scriptConfig', None)
        if not script_config or not getattr(script_config, 'filePaths', None):
            logger.info("No script files provided in scriptConfig.")
            return {"status": "error", "message": "No script files provided in scriptConfig."}

        all_results = []
        for script_index, script_path in enumerate(script_config.filePaths):
            if self.remaining_credits <= 0:
                logger.info("Credits exhausted for this exploration")
                break
            logger.info(f"Starting script-based journey {script_index + 1} of {len(script_config.filePaths)}: {script_path}")
            # Generate a journey execution ID for this script run
            journey_execution_id = str(uuid.uuid4())
            requested_credits_for_journey = max(20, self.remaining_credits // (len(script_config.filePaths) - script_index))

            journey_id=str(uuid.uuid4())
            await asyncio.to_thread(feature_facade.insert_journey, InsertJourneyRequest(id=journey_id,objective=f"Run {script_path}",description=f"Execute the steps in {script_path}"))

            max_credits_for_journey = await self._record_start_journey_execution(journey_id, journey_execution_id, requested_credits_for_journey)
            max_credits_for_journey = min(requested_credits_for_journey, max_credits_for_journey if max_credits_for_journey else 20)
            

            agent_task = AgentRunnerTask(
                exploration_id=getattr(self, 'exploration_id', None),
                execution_id=journey_execution_id,
                run_script=script_path,
                bug_capture_settings=getattr(exploration_config, 'bugCaptureSettings', None),
                viewport_config=getattr(exploration_config, 'viewportConfig', None),
                url_regex_to_capture=getattr(exploration_config, 'urlRegexToCapture', None),
                max_credits_for_journey=max_credits_for_journey,
                pre_journey_script=getattr(exploration_config, 'preJourneyScriptPath', None),
                post_journey_script=getattr(exploration_config, 'postJourneyScriptPath', None),
                config_file_path=exploration_task.explorationConfigFilePath,
                strict_mode= getattr(script_config, 'strictMode', False)
            )

            try:
                await self._init_for_journey(exploration_task)
                if self.agent_runner is None:
                    raise RuntimeError("Agent runner not initialized")
                result = await self.agent_runner.run_agent_task(agent_task, self.browser_context)
                journey_result = {
                    "status": "success",
                    "result": result,
                    "exploration_type": "script_based",
                    "script_path": script_path,
                    "journey_execution_id": journey_execution_id,
                    "script_index": script_index + 1
                }
                all_results.append(journey_result)
            except Exception as e:
                logger.info(f"Error in script-based journey {script_index + 1}: {e}")
                journey_result = {
                    "status": "error",
                    "error": str(e),
                    "script_path": script_path,
                    "journey_execution_id": journey_execution_id,
                    "script_index": script_index + 1
                }
                all_results.append(journey_result)
            finally:
                await self._record_end_journey_execution(journey_execution_id)
                self.remaining_credits = self.max_credits - self.credits_used
                self.remaining_journeys = self.remaining_journeys - 1
                if self.browser_context:
                    await self.browser_context.close()

        return {
            "status": "completed",
            "total_scripts": len(script_config.filePaths),
            "script_results": all_results
        }

async def run_exploration_from_file(
    config_file: str,
    openai_api_key: Optional[str] = None,
    stream_bugs: bool = False,
    bug_event_callback: Optional[Callable[[dict], Awaitable[None]]] = None,
    call_id: Optional[str] = None
) -> Any:
    """
    If stream_bugs is True, yields bug events as they are found and finally yields the result (async generator).
    If stream_bugs is False, returns the final result as a dict.
    """
    if not os.path.exists(config_file):
        logger.info(config_help.file_not_found_help(config_file))
        raise FileNotFoundError(f"Config file not found: {config_file}")
    logger.info(f"File found : {config_file}")
    try:
        with open(config_file, 'r') as f:
            config_data = json.load(f)
            logger.info(f"Read {config_data}")
    except json.JSONDecodeError as e:
        logger.info(config_help.json_parse_error_help(config_file, e))
        raise
    except Exception as e:
        logger.info(config_help.generic_config_error_help(config_file, e))
        raise

    try:
        config_data = map_viewport_nicknames(config_data)
        config_data = map_data_sources(config_data)
        exploration_task = LocalExplorationTask(**config_data)
        exploration_task.explorationConfigFilePath = config_file
    except Exception as e:
        logger.info(config_help.config_validation_error_help(config_file, e))
        raise

    runner = ExploreRunner(openai_api_key)

    if stream_bugs and bug_event_callback is not None and call_id is not None:
        queue = asyncio.Queue()
        orig_handle_bugs_discovered = runner.handle_bugs_discovered
        async def mcp_handle_bugs_discovered(screen_state, journey_execution_id, bugs):
            for bug in bugs:
                event = {
                    "type": "event",
                    "event": "bug_found",
                    "id": call_id,
                    "bug": bug.__dict__ if hasattr(bug, "__dict__") else str(bug),
                    "screen_state": getattr(screen_state, "__dict__", str(screen_state)),
                    "journey_execution_id": journey_execution_id,
                    "actionItem": {
                        "title": getattr(bug, "title", getattr(bug, "name", "Bug found")),
                        "actions": [
                            {
                                "label": "Fix",
                                "method": "get_bug_fix_prompt",
                                "args": {
                                    "bug": bug.__dict__ if hasattr(bug, "__dict__") else str(bug),
                                    "screen_state": getattr(screen_state, "__dict__", str(screen_state))
                                }
                            },
                            {
                                "label": "Ignore",
                                "method": "ignore_bug",
                                "args": {
                                    "bug": bug.__dict__ if hasattr(bug, "__dict__") else str(bug),
                                    "screen_state": getattr(screen_state, "__dict__", str(screen_state))
                                }
                            }
                        ]
                    }
                }
                await bug_event_callback(event)
            return await orig_handle_bugs_discovered(screen_state, journey_execution_id, bugs)
        runner.handle_bugs_discovered = mcp_handle_bugs_discovered

        async def bug_event_yielder():
            exploration_task_coro = runner.run_exploration(exploration_task)
            exploration_task_future = asyncio.create_task(exploration_task_coro)
            bugs_done = False
            while not bugs_done or not queue.empty():
                try:
                    event = await asyncio.wait_for(queue.get(), timeout=0.1)
                    yield event
                except asyncio.TimeoutError:
                    if exploration_task_future.done():
                        bugs_done = True
            result = await exploration_task_future
            yield {"type": "result", "result": result}
        async def bug_event_callback_queue(event):
            await queue.put(event)
        return bug_event_yielder()
    else:
        return await runner.run_exploration(exploration_task) 