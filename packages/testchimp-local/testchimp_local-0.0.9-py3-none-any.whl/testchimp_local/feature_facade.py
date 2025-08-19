import os
from pathlib import Path
from dotenv import load_dotenv
import requests
from pydantic import BaseModel
from typing import Optional, List
from enum import IntEnum
import sys
import importlib.util
import logging

logger = logging.getLogger(__name__)

from .datas import ElementGroup,ScreenDetail,ScreenStateDetail,AgentJourneyLog, AppMindMap, ExplorationConfig,JourneyExecutionResult, JourneyExecutionStatus,Bug, Journey,RecommendedJourneyType, ExplorationResult, ExplorationStatus, AwareUiTest, TestScenario, AgentCodeUnit

# Import version from the local version.py file
def get_version():
    """Get version from the local version.py file"""
    try:
        # Get the path to the version.py file in the same directory
        version_file = Path(__file__).parent / "version.py"
        
        if version_file.exists():
            spec = importlib.util.spec_from_file_location("version", version_file)
            if spec and spec.loader:
                version_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(version_module)
                return version_module.__version__
        return "0.0.0"  # fallback version
    except Exception:
        return "0.0.0"  # fallback version

class VersionEvaluationResult(IntEnum):
    UNKNOWN_EVALUATION_RESULT = 0
    IS_LATEST = 1
    HAS_NEWER_VERSION = 2
    IS_UNSUPPORTED_VERSION = 3

class ClientVersionEvaluation(BaseModel):
    result: Optional[VersionEvaluationResult] = None
    helpMessage: Optional[str] = None

class OrgPlan(IntEnum):
    UNKNOWN_PLAN = 0
    TEAM_PLAN = 1
    INDIE_PLAN = 2

class OrgTier(IntEnum):
    UNKNOWN_ORG_TIER = 0
    FREE_TIER = 1
    PRO_TIER = 2

class OrgStatus(IntEnum):
    UNKNOWN_ORG_STATUS = 0
    INACTIVE_ORG = 1
    SUSPENDED_ORG = 2
    ACTIVE_ORG = 3

class AuthenticateResponse(BaseModel):
    apiKey: Optional[str] = None
    clientVersionEvaluation: Optional[ClientVersionEvaluation] = None
    orgPlan:Optional[OrgPlan]=None
    orgTier:Optional[OrgTier]=None
    orgStatus:Optional[OrgStatus]=None

# Request/Response models for the new endpoints
class RecordStartExplorationRequest(BaseModel):
    explorationId: Optional[str] = None
    environment: Optional[str] = None
    maxCredits:Optional[int]=None
    maxJourneys:Optional[int]=None
    explorationConfig:Optional[ExplorationConfig]=None


class RecordStartExplorationResponse(BaseModel):
    maxJourneys:Optional[int]=None
    maxCredits:Optional[int]=None


class InsertJourneyRequest(BaseModel):
    id: Optional[str] = None
    objective: Optional[str] = None
    description: Optional[str] = None


class InsertJourneyResponse(BaseModel):
    pass


class RecordStartJourneyExecutionRequest(BaseModel):
    explorationId: Optional[str] = None
    executionId: Optional[str] = None
    journeyId: Optional[str] = None
    maxCredits:Optional[int]=None


class RecordStartJourneyExecutionResponse(BaseModel):
    maxCredits:Optional[int]=None


class UpsertJourneyExecutionRequest(BaseModel):
    explorationId: Optional[str] = None
    executionId: Optional[str] = None
    agentJourneyLog: Optional[AgentJourneyLog] = None  # com.aware.agents.AgentJourneyLog
    executionResult: Optional[JourneyExecutionResult] = None  # com.aware.agents.JourneyExecutionResult
    status:Optional[JourneyExecutionStatus]=None
    creditsUsedInExploration:Optional[int]=None
    creditsUsedInJourney:Optional[int]=None


class UpsertJourneyExecutionResponse(BaseModel):
    pass


class RecordEndExplorationRequest(BaseModel):
    explorationId: Optional[str] = None


class RecordEndExplorationResponse(BaseModel):
    pass


class RecordEndJourneyExecutionRequest(BaseModel):
    explorationId: Optional[str] = None
    executionId: Optional[str] = None


class RecordEndJourneyExecutionResponse(BaseModel):
    pass


class InsertBugsRequest(BaseModel):
    explorationId: Optional[str] = None
    journeyId: Optional[str] = None
    bugs: Optional[List[Bug]] = None  # List[com.aware.agents.Bug]
    screenName: Optional[str] = None
    screenState: Optional[str] = None
    environment: Optional[str] = None
    appReleaseId: Optional[str] = None


class InsertBugsResponse(BaseModel):
    pass


class TestScenarioDetail(BaseModel):
    scenario: Optional[dict] = None  # com.aware.agents.TestScenario
    status: Optional[int] = None  # com.aware.scenarios.TestScenarioStatus
    id: Optional[str] = None
    testCaseId: Optional[str] = None


class UpsertMindMapRequest(BaseModel):
    mindmap: Optional[AppMindMap] = None  # com.aware.agents.AppMindMap
    environment: Optional[str] = None


class UpsertMindMapResponse(BaseModel):
    pass


class GetAppMindMapRequest(BaseModel):
    environment: Optional[str] = None


class GetAppMindMapResponse(BaseModel):
    mindMap: Optional[dict] = None  # com.aware.agents.AppMindMap


class UploadScreenshotRequest(BaseModel):
    explorationId: Optional[str] = None
    journeyExecutionId: Optional[str] = None
    stepId: Optional[str] = None
    image: Optional[str] = None  # base64 encoded image


class UploadScreenshotResponse(BaseModel):
    gcpPath: Optional[str] = None


class RecommendNextJourneyRequest(BaseModel):
    exploration_id: Optional[str] = None


class RecommendNextJourneyResponse(BaseModel):
    journey: Optional[Journey] = None
    journeyId: Optional[str] = None
    recommendationType:Optional[RecommendedJourneyType]=None


class UpdateExplorationResultRequest(BaseModel):
    exploration_id: Optional[str] = None
    result: Optional[ExplorationResult] = None  # com.aware.agents.ExplorationResult
    status: Optional[ExplorationStatus] = None  # com.aware.agents.ExplorationStatus


class UpdateExplorationResultResponse(BaseModel):
    pass


class InsertTestCasesRequest(BaseModel):
    test_cases: Optional[List['AwareUiTest']] = None  # List of com.aware.tests.AwareUiTest


class InsertTestCasesResponse(BaseModel):
    insertedIds: Optional[dict[str, str]] = None


class InsertTestScenariosRequest(BaseModel):
    test_scenarios: Optional[List[TestScenario]] = None
    pre_steps: Optional[List[AgentCodeUnit]] = None
    screen_name: Optional[str] = None
    screen_state: Optional[str] = None
    test_case_title_to_id_map: Optional[dict[str, str]] = None
    exploration_id: Optional[str] = None
    journey_execution_id: Optional[str] = None
    app_release_id: Optional[str] = None

class InsertTestScenariosResponse(BaseModel):
    createdIds: Optional[List[str]] = None
    createdTestScenarios: Optional[List[TestScenario]] = None

class GetMindMapStructureRequest(BaseModel):
    environment: Optional[str] = None

class GetMindMapStructureResponse(BaseModel):
    mindmap: Optional[AppMindMap] = None

class GetUiNodeDetailsRequest(BaseModel):
    environment: Optional[str] = None
    screen: Optional[str] = None
    state: Optional[str] = None
    elementGroup: Optional[str] = None

class GetUiNodeDetailsResponse(BaseModel):
    screenDetail: Optional[ScreenDetail] = None
    screenStateDetail: Optional[ScreenStateDetail] = None
    elementGroup: Optional[ElementGroup] = None

class AskBehaviourRequest(BaseModel):
    query: Optional[str] = None
    environment: Optional[str] = None

class AskBehaviourResponse(BaseModel):
    answer: Optional[str] = None

_feature_facade_instance = None

def set_feature_facade_instance(instance):
    global _feature_facade_instance
    _feature_facade_instance = instance

def get_feature_facade_instance():
    return _feature_facade_instance

class FeatureFacade:
    def __init__(self, env_file=".env.prod"):
        env_path = Path(__file__).parent / env_file
        load_dotenv(dotenv_path=env_path)

        self.pat = os.getenv("TESTCHIMP_PAT")
        self.project_id = os.getenv("TESTCHIMP_PROJECT_ID")
        self.email = os.getenv("TESTCHIMP_EMAIL")
        self.feature_service_url = os.getenv("FEATURESERVICE_URL")

        if not all([self.pat, self.email, self.project_id]):
            raise ValueError("TESTCHIMP_PAT, TESTCHIMP_EMAIL, and TESTCHIMP_PROJECT_ID must be set in environment.")
        if not self.feature_service_url:
            raise ValueError("Feature service url not set")

        self.session = requests.Session()
        headers = {
            "user_auth_key": self.pat,
            "user_mail": self.email,
            "Project-Id": self.project_id,
            "localagent-version": get_version()
        }
        self.session.headers.update({k: v for k, v in headers.items() if v is not None})

        # Persist org plan/tier in memory
        self.org_plan = None
        self.org_tier = None

    def authenticate(self):
        url = f"{self.feature_service_url}/localagent/authenticate"

        response = self.session.post(url, json={})  # No body needed
        if response.status_code == 401:
            logger.error("Unauthorized. Please ensure that your personal access token (TESTCHIMP_PAT), email (TESTCHIMP_EMAIL) and project id (TESTCHIMP_PROJECT_ID) environment variables are set properly")
            raise Exception("Unauthorized. Please ensure that your personal access token, email and project id environment variables are set properly")
        response.raise_for_status()

        response_data = AuthenticateResponse(**response.json())
        if not response_data.apiKey:
            raise ValueError("Authentication failed. Please check your access token is correct")

        # Store org plan/tier in memory
        self.org_plan = response_data.orgPlan
        self.org_tier = response_data.orgTier
        self.org_status = response_data.orgStatus

        return response_data

    # Example of a reusable GET method
    def get(self, endpoint: str, params: dict):
        url = f"{self.feature_service_url}{endpoint}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()

    # Example of a reusable POST method
    def post(self, endpoint: str, data: dict):
        url = f"{self.feature_service_url}{endpoint}"
        response = self.session.post(url, json=data or {})
        response.raise_for_status()
        return response.json()

    # New endpoint methods
    def record_start_exploration(self, request: RecordStartExplorationRequest) -> RecordStartExplorationResponse:
        """Record the start of an exploration session."""
        return RecordStartExplorationResponse(**self.post("/localagent/record_start_exploration", request.model_dump(exclude_none=True)))

    def insert_journey(self, request: InsertJourneyRequest) -> InsertJourneyResponse:
        """Insert a new journey."""
        return InsertJourneyResponse(**self.post("/localagent/insert_journey", request.model_dump(exclude_none=True)))

    def record_start_journey_execution(self, request: RecordStartJourneyExecutionRequest) -> RecordStartJourneyExecutionResponse:
        """Record the start of a journey execution."""
        return RecordStartJourneyExecutionResponse(**self.post("/localagent/record_start_journey_execution", request.model_dump(exclude_none=True)))

    def upsert_journey_execution(self, request: UpsertJourneyExecutionRequest) -> UpsertJourneyExecutionResponse:
        """Upsert journey execution data."""
        return UpsertJourneyExecutionResponse(**self.post("/localagent/upsert_journey_execution", request.model_dump(exclude_none=True)))

    def record_end_journey_execution(self, request: RecordEndJourneyExecutionRequest) -> RecordEndJourneyExecutionResponse:
        """Record the end of a journey execution."""
        return RecordEndJourneyExecutionResponse(**self.post("/localagent/record_end_journey_execution", request.model_dump(exclude_none=True)))

    def record_end_exploration(self, request: RecordEndExplorationRequest) -> RecordEndExplorationResponse:
        """Record the end of an exploration session."""
        return RecordEndExplorationResponse(**self.post("/localagent/record_end_exploration", request.model_dump(exclude_none=True)))

    def insert_bugs(self, request: InsertBugsRequest) -> InsertBugsResponse:
        """Insert bugs found during exploration."""
        return InsertBugsResponse(**self.post("/localagent/insert_bugs", request.model_dump(exclude_none=True)))

    def upsert_mindmap(self, request: UpsertMindMapRequest) -> UpsertMindMapResponse:
        """Upsert application mindmap."""
        return UpsertMindMapResponse(**self.post("/localagent/upsert_mindmap", request.model_dump(exclude_none=True)))

    def get_app_mindmap(self, request: GetAppMindMapRequest) -> GetAppMindMapResponse:
        """Get application mindmap."""
        return GetAppMindMapResponse(**self.post("/localagent/get_app_mindmap", request.model_dump(exclude_none=True)))

    def upload_screenshot(self, request: UploadScreenshotRequest) -> UploadScreenshotResponse:
        """Upload a screenshot."""
        return UploadScreenshotResponse(**self.post("/localagent/upload_screenshot", request.model_dump(exclude_none=True)))

    def recommend_next_journey(self, request: RecommendNextJourneyRequest) -> RecommendNextJourneyResponse:
        """Request recommendation for the next journey."""
        return RecommendNextJourneyResponse(**self.post("/localagent/recommend_next_journey", request.model_dump(exclude_none=True)))

    def update_exploration_result(self, request: UpdateExplorationResultRequest) -> UpdateExplorationResultResponse:
        """Update the result and status of an exploration."""
        return UpdateExplorationResultResponse(**self.post("/localagent/update_exploration_result", request.model_dump(exclude_none=True)))

    def insert_test_cases(self, request: InsertTestCasesRequest) -> InsertTestCasesResponse:
        """Insert test cases."""
        return InsertTestCasesResponse(**self.post("/localagent/insert_test_cases", request.model_dump(exclude_none=True)))

    def insert_test_scenarios(self, request: InsertTestScenariosRequest) -> InsertTestScenariosResponse:
        """Insert test scenarios."""
        return InsertTestScenariosResponse(**self.post("/localagent/insert_test_scenarios", request.model_dump(exclude_none=True)))

    def get_mindmap_structure(self, request: GetMindMapStructureRequest) -> GetMindMapStructureResponse:
        return GetMindMapStructureResponse(
            **self.post("/localagent/get_mindmap_structure", request.model_dump(exclude_none=True))
        )

    def get_ui_node_details(self, request: GetUiNodeDetailsRequest) -> GetUiNodeDetailsResponse:
        return GetUiNodeDetailsResponse(
            **self.post("/localagent/get_ui_node_details", request.model_dump(exclude_none=True))
        )

    def ask_behaviour(self, request: AskBehaviourRequest) -> AskBehaviourResponse:
        return AskBehaviourResponse(
            **self.post("/localagent/ask_behaviour", request.model_dump(exclude_none=True))
        )