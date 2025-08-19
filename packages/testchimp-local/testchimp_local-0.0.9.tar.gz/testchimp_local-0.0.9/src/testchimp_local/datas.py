from pydantic import BaseModel, Field
from enum import IntEnum,Enum,StrEnum
from typing import List, Optional,Set, Any
from typing import Optional, Literal, Dict
from pathlib import Path
import uuid

class ChoicePriority(IntEnum):
    UNKNOWN_CHOICE_PRIORITY = 0
    LOW_PRIORITY = 1
    MEDIUM_PRIORITY = 2
    HIGH_PRIORITY = 3

class BugBucket(IntEnum):
    UNKNOWN_BUG_BUCKET = 0
    UX_BUCKET = 1
    VISUAL_BUCKET = 4
    FUNCTIONAL_BUCKET = 5
    PERFORMANCE_BUCKET = 2
    SECURITY_BUCKET = 3

class DataSource(IntEnum):
    UNKNOWN_DATA_SOURCE = 0
    DOM_SOURCE = 1
    SCREENSHOT_SOURCE = 2
    NETWORK_SOURCE = 3
    CONSOLE_SOURCE = 4


class BugCategory(IntEnum):
    UNKNOWN_BUG_CATEGORY = 0
    OTHER = 1 # Not fitting any specified category
    ACCESSIBILITY = 2 # Accessibility issues
    SECURITY = 3 # Security vulnerabilities
    VISUAL = 4 # Visual issues such as layout concerns
    PERFORMANCE = 5  # Slow load times, unoptimized assets, memory leaks
    FUNCTIONAL = 6  # Broken buttons, incorrect form submissions, navigation issues
    NETWORK = 7  # API failures, timeout errors, incorrect responses
    USABILITY = 8  # Confusing UI, bad user experience, layout inconsistencies
    COMPATIBILITY = 9  # Issues across different browsers/devices/resolutions
    DATA_INTEGRITY = 10  # Corrupt or missing data, incorrect database states
    INTERACTION = 11  # Unresponsive UI elements, broken drag/drop, keyboard navigation issues
    LOCALIZATION = 12  # Language-specific issues, missing translations, incorrect currency formats
    RESPONSIVENESS = 13
    LAYOUT = 14

class BugStatus(IntEnum):
    UNKNOWN_BUG_STATUS=0
    ACTIVE=1
    IGNORED=2

class TestScenarioStatus(IntEnum):
    UNKNOWN_TEST_SCENARIO_STATUS=0
    ACTIVE_TEST_SCENARIO=1
    DELETED_TEST_SCENARIO=2

class BugSeverity(IntEnum):
    UNKNOWN_BUG_SEVERITY = 0
    LOW_SEVERITY = 1
    MEDIUM_SEVERITY = 2
    HIGH_SEVERITY = 3

class ExplorationStatus(IntEnum):
    UNKNOWN_EXPLORATION_STATUS = 0
    ENQUEUED_EXPLORATION = 1
    IN_PROGRESS_EXPLORATION = 2
    COMPLETED_EXPLORATION = 3
    EXCEPTION_IN_EXPLORATION = 4
    USER_ABORTED_EXPLORATION=5

class JourneyAgnotism(IntEnum):
    UNKNOWN_JOURNEY_AGNOTISM = 0
    IS_JOURNEY_AGNOSTIC = 1
    NOT_JOURNEY_AGNOSTIC = 2

class RecommendedJourneyType(StrEnum):
    UNKNOWN_RECOMMENDED_JOURNEY_TYPE="UNKNOWN_RECOMMENDED_JOURNEY_TYPE"
    EXPLORATION="EXPLORATION"
    SCENARIOS_CHECK="SCENARIOS_CHECK"
    EXISTING_JOURNEY="EXISTING_JOURNEY"
    END_EXPLORATION="END_EXPLORATION"

class JourneyExecutionStatus(IntEnum):
    UNKNOWN_JOURNEY_EXECUTION_STATUS = 0
    ENQUEUED_JOURNEY_EXECUTION = 1
    IN_PROGRESS_JOURNEY_EXECUTION = 2
    COMPLETED_JOURNEY_EXECUTION = 3
    EXCEPTION_IN_JOURNEY_EXECUTION = 4
    USER_ABORTED_JOURNEY_EXECUTION = 5

class JourneyRecordingMode(IntEnum):
    UNKNOWN_RECORDING_MODE = 0
    RRWEB_VIDEO = 1
    SCREENSHOT = 2

class ResourceType(StrEnum):
    UNKNOWN_RESOURCE_TYPE="UNKNOWN_RESOURCE_TYPE"
    ENTRY_RESOURCE="ENTRY_RESOURCE"
    NON_ENTRY_RESOURCE="NON_ENTRY_RESOURCE"
    WEBAPP_RESOURCE="WEBAPP_RESOURCE"

class AlternateChoice(BaseModel):
    description: Optional[str] = None
    priority: Optional[ChoicePriority] = None

class StepExecution(BaseModel):
    description: Optional[str] = None
    code: Optional[str] = None
    elementId:Optional[str]=None
    alternate_choices: List[AlternateChoice] = []

class BoundingBox(BaseModel):
    x:Optional[int]=None
    y:Optional[int]=None
    width:Optional[int]=None
    height:Optional[int]=None
    x_pct:Optional[float]=None
    y_pct:Optional[float]=None
    width_pct:Optional[float]=None
    height_pct:Optional[float]=None

class ConsoleLogEntry(BaseModel):
    type: str
    text: str
    timestamp: int  # in millis

class Bug(BaseModel):
    title:Optional[str]=None
    description: Optional[str] = None
    category: Optional[str] = None
    severity: Optional[BugSeverity] = None
    eval_command: Optional[str] = None
    location: Optional[str] = None
    screen:Optional[str]=None
    screen_state:Optional[str]=None
    rule:Optional[str]=None
    bounding_box:Optional[BoundingBox]=None
    element_synthetic_id:Optional[str]=None
    bug_hash:Optional[str]=None
    scenario_id:Optional[str]=None
    journey_agnotism: Optional[JourneyAgnotism] = None

class LLMMetadata(BaseModel):
    inputTokens: Optional[int] = None
    outputTokens: Optional[int] = None
    totalTokens: Optional[int] = None

class LLMDebugInfo(BaseModel):
    promptFeedback:Optional[str]=None
    inputDataFeedback:Optional[str]=None

class BugCapture(BaseModel):
    bugs: List[Bug] = []
    analyzed_source:Optional[DataSource]=None

class BugCaptureWithLLMMetadata(BaseModel):
    result:Optional[BugCapture]=None
    metadata:Optional[LLMMetadata]=None



class BugCaptureForCategory(BaseModel):
    category: Optional[str] = None
    bugs: List[Bug]

class BugCaptureReport(BaseModel):
    categoryReport: List[BugCaptureForCategory]
    analyzedSource: Optional[DataSource] = None

class JourneyConfig(BaseModel):
    test_objective_prompt: Optional[str] = None

class RecordingMetadata(BaseModel):
    session_record_api_key: Optional[str] = None
    url_regex_to_capture: Optional[str] = None
    ingress_endpoint: Optional[str] = None 



class CodeUnit(BaseModel):
    code: Optional[str] = None
    description: Optional[str] = None

    def to_dict(self):
        # Convert model to dictionary, excluding None fields
        return self.dict(exclude_none=True)


class AgentCodeUnit(BaseModel):
    syntheticCode: Optional[str]=None
    semanticCode: Optional[str]=None
    agentCode:Optional[str]=None
    pythonCode:Optional[str]=None
    description: Optional[str]=None

class Journey(BaseModel):
    title: Optional[str] = None
    steps: List[str]=[]

class ViewportNickname(IntEnum):
    UNKNOWN_VIEWPORT_NICKNAME = 0
    LAPTOP = 1
    WIDESCREEN = 2
    MOBILE = 3
    TABLET = 4
    
class Viewport(BaseModel):
    nickname:Optional[ViewportNickname]=None
    width:Optional[int]=None
    height:Optional[int]=None

class ViewportConfig(BaseModel):
    viewports:Optional[List[Viewport]]=None

class BugCaptureSettings(BaseModel):
    bugVerbosity: Optional[int] = None  # Expected range: 1–10
    sources: List[DataSource]=[]
    bugBuckets: List[BugBucket]=[]
   
class TestLocation(BaseModel):
    screenName:Optional[str]=None
    screenState:Optional[str]=None
    elementGroup:Optional[str]=None


class PromptBasedConfig(BaseModel):
    url: Optional[str] = None
    explorePrompt: Optional[str] = None
    testDataPrompt: Optional[str] = None
    location:Optional[TestLocation]=None

# LLMScreenDetailOutput

class PreSteps(BaseModel):
    codeUnits:list[AgentCodeUnit]=[]

class TestScenario(BaseModel):
    title: Optional[str] = None
    expectedBehaviour: Optional[str] = None
    # Deprecated in favour of steps
    description: Optional[str] = None 
    priority: Optional[int] = None
    preSteps:Optional[PreSteps]=None  
    steps:Optional[List[AgentCodeUnit]]=None
    assertionCode:Optional[str]=None


class ElementSignificance(IntEnum):
    UNKNOWN_SIGNIFICANCE = 0
    LOW_SIGNIFICANCE = 1
    MEDIUM_SIGNIFICANCE = 2
    HIGH_SIGNIFICANCE = 3


class ElementType(IntEnum):
    UNKNOWN_ELEMENT__TYPE = 0
    INTERACTIVE = 1
    INFO_DISPLAY = 2
    NAVIGATION = 3


class Element(BaseModel):
    syntheticLocator: Optional[str] = None
    semanticLocator: Optional[str] = None
    text: Optional[str] = None
    altText: Optional[str] = None
    role: Optional[str] = None
    type: Optional[ElementType] = None
    significance: Optional[ElementSignificance] = None


class TestPriority(IntEnum):
    UNKNOWN_PRIORITY = 0
    LOW_PRIORITY = 1
    MEDIUM_PRIORITY = 2
    HIGH_PRIORITY = 3


class ActionItem(BaseModel):
    title: Optional[str] = None
    priority: Optional[TestPriority] = None
    codeUnits: Optional[List[CodeUnit]] = None


class ElementGroup(BaseModel):
    title: Optional[str] = None
    purpose: Optional[str] = None
    elements: Optional[List[Element]] = None
    possibleActions: Optional[List[ActionItem]] = None


class BugCountSummary(BaseModel):
    highSeverityBugs: Optional[int] = None
    medSeverityBugs: Optional[int] = None
    lowSeverityBugs: Optional[int] = None

class JourneyExecutionResult(BaseModel):
    bug_count_summary: Optional[BugCountSummary] = None

class RelatedSourceFile(BaseModel):
    path: Optional[str] = None
    confidence: Optional[float] = None
    type: Optional[str] = None
    component:Optional[str]=None

class SourceMap(BaseModel):
    relatedFiles: List[RelatedSourceFile] = []

class ScreenState(BaseModel):
    name: Optional[str]=None
    state: Optional[str]=None

class ScreenStates(BaseModel):
    screen: Optional[str]=None
    states: List[str]=[]

class LLMScreenDetailOutput(BaseModel):
    name: Optional[str] = None
    state: Optional[str] = None
    url: Optional[str] = None
    type:Optional[str]=None
    description: Optional[str] = None
    elementGroups: Optional[List[ElementGroup]] = None
    testScenarios: Optional[List[TestScenario]] = None
    tags:Optional[List[str]]=None
    significance:Optional[ElementSignificance]=None
    metadata: Optional[LLMMetadata] = None    

class ExistingScreenStateMap(BaseModel):
    screenStatesMap:Dict[str, List[ScreenStates]] = {}

class NavigationLink(BaseModel):
    normalizedUrl: Optional[str] = None
    elementType: Optional[str] = None
    label: Optional[str] = None
    role: Optional[str] = None
    visible: Optional[bool] = None
    semanticDepth: Optional[int] = None
    visualDepth: Optional[int] = None
    containerType: Optional[str] = None
    area: Optional[str] = None

class TestScenarioBasedConfig(BaseModel):
    scenarioIds:Optional[List[str]]=None
    initialUrl:Optional[str]=None
    testDataPrompt:Optional[str]=None

class LocalScriptBasedConfig(BaseModel):
    filePaths:Optional[List[str]]=None
    strictMode:Optional[bool]=None

# ExplorationConfig
class ExplorationConfig(BaseModel):
    promptConfig: Optional[PromptBasedConfig] = None
    scenarioConfig: Optional[TestScenarioBasedConfig]=None
    scriptConfig:Optional[LocalScriptBasedConfig]=None
    maxCredits: Optional[int] = None
    maxJourneys: Optional[int] = None
    bugCaptureSettings: Optional[BugCaptureSettings] = None
    viewportConfig:Optional[ViewportConfig]=None
    urlRegexToCapture:Optional[str]=None
    preJourneyScriptPath:Optional[str]=None
    postJourneyScriptPath:Optional[str]=None
    # Currently unused
    playwrightConfigPath: Optional[str] = None

    
# ExplorationTask
class ExplorationTask(BaseModel):
    explorationId: Optional[str]=None
    explorationConfig: ExplorationConfig
    projectId: Optional[str]=None
    environment: Optional[str]=None
    sessionRecordApiKey: Optional[str]=None
    ingressEndpoint: Optional[str]=None
    enableTestchimpSdkOnExec: bool = False
    generateMindMap: bool=False

    
class NeighbourScreenState(BaseModel):
    screenState: Optional[ScreenState] = None
    actionSummary: Optional[str] = None
    weight:Optional[int]=None
    addedTimestampMillis:Optional[int]=None

class Screenshot(BaseModel):
    url: Optional[str] = None
    viewport: Optional[Viewport] = None


class ScreenStateDetail(BaseModel):
    state: Optional[str] = None
    elementGroups: List[ElementGroup] = []
    testScenarios: Optional[List[TestScenario]] = None
    neighbourScreens: List[NeighbourScreenState] = []
    # Deprecated in favour of screenshots.
    screenshotUrl: Optional[str] = None
    screenshots:Optional[List[Screenshot]]=None
    sourceMap: Optional[SourceMap] = None

class DisplayMetadata(BaseModel):
    x: Optional[float] = None
    y: Optional[float] = None

class ScreenExplorationStatus(IntEnum):
    UNKNOWN_SCREEN_EXPLORATION_STATUS=0
    NOT_EXPLORED=1
    PARTIALLY_EXPLORED=2
    FULLY_EXPLORED=3

class ScreenDetail(BaseModel):
    name: Optional[str] = None
    isInitialScreen:Optional[bool]=None
    url: Optional[str] = None
    type: Optional[str] = None
    states: List[ScreenStateDetail] = []
    description: Optional[str] = None
    displayMetadata: Optional[DisplayMetadata] = None
    explorationStatus:Optional[ScreenExplorationStatus]=None
    significance:Optional[ElementSignificance]=None
    tags:Optional[List[str]]=None
  

class NewLinksLLMOutput(BaseModel):
    newScreensMap:Optional[Dict[str,ScreenDetail]]=None
    metadata:Optional[LLMMetadata]=None

# AppMindMap
class InputValueCombination(BaseModel):
    input_values: Optional[Dict[str, str]] = None

class AppMindMap(BaseModel):
    screens: List[ScreenDetail] = []
    appDetail: Optional[str] = None
    inputValueCombinations: List[InputValueCombination] = []
    initialUrl: Optional[str] = None

class ExplorationResult(BaseModel):
    error: Optional[str] = None
    bugCountSummary: Optional[BugCountSummary] = None
    screenStatesAnalyzed: List[ScreenState]
    tokensUsed: Optional[int] = None

#AgentJourneyLog related items
    
class ExecutionStepStatus(IntEnum):
    UNKNOWN_EXECUTION_STATUS = 0
    PASSED = 1
    FAILED = 2


class JourneyEndStatus(IntEnum):
    UNKNOWN_JOURNEY_END_STATUS = 0
    SUCCESS = 1
    EXPECTED_BEHAVIOUR_NOT_MET = 2
    EXCEPTION_OCCURRED = 3


class JourneyLogItemType(IntEnum):
    UNKNOWN_LOG_ITEM_TYPE = 0
    STEP_EXECUTION = 1
    BUG_CAPTURE = 2
    REASONING = 3
    END_OF_JOURNEY = 4
    TEST_RESULT = 5
    SCENARIO_CAPTURE = 6

class ScenarioTestResult(IntEnum):
  UNKNOWN_TEST_SCENARIO_STATUS = 0
  UNTESTED = 1
  TESTED_WORKING = 2
  TESTED_NOT_WORKING = 3
  IGNORED_TEST_SCENARIO = 4

class AgentCodeUnitList(BaseModel):
    codeUnits:List[AgentCodeUnit]

class CodeUnitListWithLLMMetadata(BaseModel):
    codeUnits:List[AgentCodeUnit]=[]
    metadata:Optional[LLMMetadata]=None

class ExecutionStepResult(BaseModel):
    codeUnit: Optional[AgentCodeUnit]=None
    status: Optional[ExecutionStepStatus]=None
    error: Optional[str]=None


class EndOfJourney(BaseModel):
    status: Optional[JourneyEndStatus]=None
    reason: Optional[str]=None

class AgentTestResult(BaseModel):
    scenarioId:Optional[str]=None
    scenarioTitle:Optional[str]=None
    expectedBehaviour:Optional[str]=None
    observedBehaviour:Optional[str]=None
    result:Optional[ScenarioTestResult]=None
    confidence:Optional[float]=None

class ScreenStateVisitResult(BaseModel):
    screenState:Optional[ScreenState]=None
    insertedTestScenarios:Optional[List[TestScenario]]=None

class TestScenarioCaptureReport(BaseModel):
    scenarios:Optional[List[TestScenario]]=None
    
class JourneyLogItem(BaseModel):
    id: Optional[str]=None
    stepExecution: Optional[ExecutionStepResult]=None
    bugCaptureReport: Optional[BugCaptureReport]=None
    testScenarioCaptureReport: Optional[TestScenarioCaptureReport]=None
    testResult:Optional[AgentTestResult]=None
    endOfJourney: Optional[EndOfJourney]=None
    startTimestampMillis: Optional[int]=None
    endTimestampMillis: Optional[int]=None
    screenState: Optional[ScreenState]=None
    itemType: Optional[JourneyLogItemType]=None
    screenshotPath:Optional[str]=None
    viewport:Optional[Viewport]=None
    consoleLogs:Optional[List[ConsoleLogEntry]]=None


class AgentJourneyLog(BaseModel):
    sessionId: Optional[str]=None
    sessionCaptureError: Optional[str]=None
    error: Optional[str]=None
    logs: List[JourneyLogItem]=[]
    recordingMode : Optional[JourneyRecordingMode]=None



class ScenarioTestStep(BaseModel):
	id:Optional[str]=None
	title:Optional[str]=None
	expectedBehavior:Optional[str]=None
	screenName:Optional[str]=None
	screenState:Optional[str]=None

class AgentStepAdvice(BaseModel):
	action:Optional[str]=None # Filled only if this is an action step
	testScenario:Optional[ScenarioTestStep]=None # Filled only if this is for testing a specific scenario
	endJourney:Optional[bool]=None # Fill this only if this is the last step to do in the journey

class AgentSteps(BaseModel):
    steps:Optional[list[AgentStepAdvice]]=None
    
class RecommendedNextJourney(BaseModel):
    type:Optional[RecommendedJourneyType]=None
    existingJourneyId:Optional[str]=None # Only if retrying an existing journey
    reason:Optional[str]=None # Only if type is end_exploration
    focusPrompt:Optional[str]=None # Only for exploration type
    journeyTitle:Optional[str]=None # Only for scenarios_check type
    agentSteps:Optional[AgentSteps]=None # Only for scenarios_check type
    metadata:Optional[LLMMetadata]=None

class AnalyzePageDecision(BaseModel):
    shouldAnalyze: Optional[bool]=None
    
class ExecutionStepResultSummary(BaseModel):
    steps:Optional[List[str]]=None
    metadata: Optional[LLMMetadata] = None
    debugInfo:Optional[LLMDebugInfo]=None

class AppMindMapSummary(BaseModel):
    summary:Optional[str]=None
    metadata: Optional[LLMMetadata] = None

class ConvertScriptLLMOutput(BaseModel):
    script:Optional[str]=None
    is_unsafe:Optional[bool]=None
    metadata:Optional[LLMMetadata]=None

class NextActionInstruction(BaseModel):
    """
    Represents the next action to take during automated web testing.
    Supports a wide range of interactions, including clicks, typing, selections, and more.
    """
    action: Literal[
        "click", "double_click", "right_click", "hover", "type", "press_key",
        "select", "toggle_checkbox", "input", "navigate", "scroll", "drag_and_drop"
    ]
    element_locator: Optional[str] = None  # The element locator
    input_text: Optional[str] = None  # Text input (if applicable)
    key_press: Optional[str] = None  # Key to press for keyboard interactions
    dropdown_option: Optional[str] = None  # Dropdown selection value
    checkbox_state: Optional[bool] = None  # Toggle checkbox (True = check, False = uncheck)
    date_value: Optional[str] = None  # Date input value (e.g., "2025-03-25")
    navigation_url: Optional[str] = None  # URL if navigating
    scroll_amount: Optional[int] = None  # Pixels to scroll
    drag_from: Optional[str] = None  # Source element for drag-and-drop
    drag_to: Optional[str] = None  # Target element for drag-and-drop
    metadata: Optional[Dict[str, Any]] = None  # Additional metadata if needed

    def to_dict(self):
        # Convert model to dictionary, excluding None fields
        return self.dict(exclude_none=True)
    




class RequestResponsePair(BaseModel):
    url: str
    method: str
    requestHeaders: Dict[str, str]
    responseHeaders: Dict[str, str]
    status: int
    responseTimeMs: Optional[float]
    timestamp: int  # when response was received

class SimpleUserInfo(BaseModel):
    userId: Optional[str] = None
    email: Optional[str] = None
    name: Optional[str] = None

class SendExploreReportRequest(BaseModel):
    recipients:Optional[list[SimpleUserInfo]]=[]
    exploreLink: Optional[str] = None
    numScreensAnalyzed: Optional[int] = None
    bugCountSummary:Optional[BugCountSummary]=None

class SendExploreReportResponse(BaseModel):
    pass

class ExplorationNotificationMode(IntEnum):
    UNKNOWN_EXPLORATION_NOTIFICATION_MODE = 0
    NOTIFY_ALL_ORG_USERS = 1
    NOTIFY_LISTED_USERS = 2
    CALL_WEBHOOK = 3

class ExplorationNotificationType(IntEnum):
    UNKNOWN_EXPLORATION_NOTIFICATION_TYPE=0
    FIRST_EXPLORATION_NOTIFICATION=1
    NORMAL_EXPLORATION_NOTIFICATION=2
    
class ExplorationNotificationConfig(BaseModel):
    notificationMode: Optional[int] = None
    notificationType:Optional[ExplorationNotificationType]=None
    users: Optional[list[SimpleUserInfo]] = None
    webhookUrl:Optional[str]=None

class TestScenarioResultHistoryItem(BaseModel):
    testedBy:Optional[str]=None
    daysSinceTest:Optional[int]=None
    result:Optional[ScenarioTestResult]=None
    componentReleaseId:Optional[str]=None
    appReleaseId:Optional[str]=None

class TestScenarioWithResult(BaseModel):
    id:Optional[str]=None
    scenario:Optional[TestScenario]=None
    latestResult:Optional[TestScenarioResultHistoryItem]=None

class ScreenStateTestScenarioResultList(BaseModel):
    stateName:Optional[str]=None
    list:Optional[List[TestScenarioWithResult]]=[]

class ScreenTestScenarioResultList(BaseModel):
    screenName:Optional[str]=None
    stateScenarios:Optional[list[ScreenStateTestScenarioResultList]]=None

class TestScenarioResultList(BaseModel):
    screenScenarios:Optional[list[ScreenTestScenarioResultList]]=None
    
class DeduplicateScenarioSuggestion(BaseModel):
    existingScenarioId:Optional[str]=None
    newTestScenario:Optional[TestScenario]=None
    metadata:Optional[LLMMetadata]=None

class TestName(BaseModel):
    name:Optional[str]=None
    suite:Optional[str]=None

class AwareUiTest(BaseModel):
    testName:Optional[TestName]=None
    sessionId:Optional[str]=None
    codeUnits:Optional[List[CodeUnit]]=None
    l1Summary:Optional[str]=None
    l2Summary:Optional[str]=None
    tags:Optional[List[str]]=None

class AwareUiTestListLLMOutput(BaseModel):
    testCases:Optional[List[AwareUiTest]]=None
    metadata:Optional[LLMMetadata]=None

class AwareTest(BaseModel):
    ui_test:Optional[AwareUiTest]=None

class ExplorationCompletionNotifyRequest(BaseModel):
    exploration_id:Optional[str]=None
    project_id:Optional[str]=None
    status:Optional[ExplorationStatus]=None



# Local Specific Data Classes
class BrowserMode(StrEnum):
    UNKNOWN_BROWSER_MODE = "UNKNOWN_BROWSER_MODE"
    LAUNCH = "launch"
    CDP = "cdp"


class BrowserContext(BaseModel):
    mode: Optional[BrowserMode] = None
    cdpUrl: Optional[str] = None
    headless: Optional[bool] = None

class LocalExplorationTask(BaseModel):
    explorationId: str = str(uuid.uuid4())
    browserContext: Optional[BrowserContext] = None
    explorationConfig: Optional[ExplorationConfig] = None
    appReleaseLabel:Optional[str]="local_default"
    environment:Optional[str]="QA"
    explorationConfigFilePath:Optional[str]=None

class AgentRunnerTask(BaseModel):
    exploration_id:Optional[str]=None
    execution_id: str = str(uuid.uuid4())
    initial_url: Optional[str] = None
    bug_capture_settings: Optional[BugCaptureSettings] = None
    viewport_config: Optional[ViewportConfig] = None
    ignored_bug_hashes: Optional[Set[str]] = None
    journey_to_run:Optional[Journey]=None
    test_data_inputs:Optional[str]=None
    instructions_prompt:Optional[str]=None
    test_location:Optional[TestLocation]=None
    journey_type:Optional[RecommendedJourneyType]=None
    url_regex_to_capture:Optional[str]=None
    max_credits_for_journey:Optional[int]=None
    pre_journey_script:Optional[str]=None
    post_journey_script:Optional[str]=None
    # Only present if exploration is based off of script based config
    run_script:Optional[str]=None
    config_file_path:Optional[str]=None
    strict_mode:Optional[bool]=None
    enable_autocorrect:Optional[bool]=None
    journey_type:Optional[RecommendedJourneyType]=None


VIEWPORT_NICKNAME_MAP = {
    "laptop": ViewportNickname.LAPTOP,
    "widescreen": ViewportNickname.WIDESCREEN,
    "mobile": ViewportNickname.MOBILE,
    "tablet": ViewportNickname.TABLET,
}

DATA_SOURCE_MAP = {
    "dom": DataSource.DOM_SOURCE,
    "screenshot": DataSource.SCREENSHOT_SOURCE,
    "network": DataSource.NETWORK_SOURCE,
    "console": DataSource.CONSOLE_SOURCE,
}

def map_data_sources(config: dict) -> dict:
    """
    Recursively map data source strings to enum values in the config dict.
    """
    if isinstance(config, dict):
        for k, v in config.items():
            if k == "sources" and isinstance(v, list):
                mapped_sources = []
                for item in v:
                    if isinstance(item, str):
                        mapped_sources.append(DATA_SOURCE_MAP.get(item.lower(), DataSource.UNKNOWN_DATA_SOURCE))
                    elif isinstance(item, int):
                        # Convert integer values to enum values
                        if item == 1:
                            mapped_sources.append(DataSource.DOM_SOURCE)
                        elif item == 2:
                            mapped_sources.append(DataSource.SCREENSHOT_SOURCE)
                        elif item == 3:
                            mapped_sources.append(DataSource.NETWORK_SOURCE)
                        elif item == 4:
                            mapped_sources.append(DataSource.CONSOLE_SOURCE)
                        else:
                            mapped_sources.append(DataSource.UNKNOWN_DATA_SOURCE)
                    else:
                        mapped_sources.append(item)
                config[k] = mapped_sources
            else:
                config[k] = map_data_sources(v)
    elif isinstance(config, list):
        return [map_data_sources(item) for item in config]
    return config

def map_viewport_nicknames(config: dict) -> dict:
    """
    Recursively map viewport nickname strings to enum values in the config dict.
    """
    if isinstance(config, dict):
        for k, v in config.items():
            if k == "nickname" and isinstance(v, str):
                config[k] = VIEWPORT_NICKNAME_MAP.get(v.lower(), ViewportNickname.UNKNOWN_VIEWPORT_NICKNAME)
            else:
                config[k] = map_viewport_nicknames(v)
    elif isinstance(config, list):
        return [map_viewport_nicknames(item) for item in config]
    return config

class ConversionResult(IntEnum):
    UNKNOWN_CONVERSION_RESULT = 0
    SUCCESS = 1
    FAILURE = 2

class PythonPlaywrightStepsResponse(BaseModel):
    stepBlocks: Optional[List[List[str]]] = None  # each block is a list of commands
    result: Optional[ConversionResult] = None
    failureReason: Optional[str] = None

class ActionStepList(BaseModel):
    steps: Optional[List[str]] = None

class WSBaseMessage(BaseModel):
    type: str
    request_id: str
    error:Optional[str]=None

    class Config:
        arbitrary_types_allowed = True
        extra = "allow"

class GetDomSnapshotRequest(WSBaseMessage):
    type: str = "get_dom_snapshot"
    includeStyles:Optional[bool]=False

class GetDomSnapshotResponse(WSBaseMessage):
    type: str = "get_dom_snapshot"
    dom: Optional[Any]=None

class GrabScreenshotRequest(WSBaseMessage):
    type: str = "grab_screenshot"

class GrabScreenshotResponse(WSBaseMessage):
    type: str = "grab_screenshot"
    screenshotBase64: Optional[str]=None

class GetRecentConsoleLogsRequest(WSBaseMessage):
    type: str = "get_recent_console_logs"
    level: Optional[str] = None
    count: Optional[int] = None
    sinceTimestamp: Optional[int] = None

class GetRecentConsoleLogsResponse(WSBaseMessage):
    type: str = "get_recent_console_logs"
    logs: Optional[List[Any]]=None

class GetRecentRequestResponsePairsRequest(WSBaseMessage):
    type: str = "get_recent_request_response_pairs"
    count: Optional[int] = None
    sinceTimestamp: Optional[int] = None

class GetRecentRequestResponsePairsResponse(WSBaseMessage):
    type: str = "get_recent_request_response_pairs"
    pairs: Optional[List[Any]]=None

class FetchExtraInfoForContextItemRequest(WSBaseMessage):
    type: str = "fetch_extra_info_for_context_item"
    id: str

class FetchExtraInfoForContextItemResponse(WSBaseMessage):
    type: str = "fetch_extra_info_for_context_item"
    extraInfo: Dict[str, Any] = Field(default_factory=dict)

# Add more request/response models as needed for extensibility
