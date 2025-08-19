import os
from fastapi import FastAPI, Body
from pydantic import BaseModel
from typing import Optional, cast
import uvicorn

from testchimp_local.feature_facade import AskBehaviourRequest, AskBehaviourResponse, FeatureFacade, GetMindMapStructureRequest, GetMindMapStructureResponse, GetUiNodeDetailsRequest, GetUiNodeDetailsResponse
from .explore_runner import ExploreRunner, run_exploration_from_file
from dotenv import load_dotenv
import logging
from fastmcp import FastMCP
from starlette.routing import Mount
import uuid
import asyncio
from .datas import GrabScreenshotRequest, GrabScreenshotResponse, GetRecentConsoleLogsRequest, GetRecentConsoleLogsResponse, FetchExtraInfoForContextItemRequest, FetchExtraInfoForContextItemResponse, GetDomSnapshotRequest, GetDomSnapshotResponse, GetRecentRequestResponsePairsRequest, GetRecentRequestResponsePairsResponse
from .chrome_ext_bridge import setup_chrome_ext_bridge, send_ws_request
from .feature_facade import get_feature_facade_instance
import sys

logger = logging.getLogger(__name__)
mcp = FastMCP("TestChimp-Mcp")
mcp_app = mcp.http_app(path='/')

app = FastAPI(lifespan=mcp_app.lifespan)
app.mount("/mcp", mcp_app)

# Setup Chrome extension WebSocket bridge
setup_chrome_ext_bridge(app)

explore_runner: Optional[ExploreRunner] = None  # Will initialize later

# Request model for exploration
class ExplorationRequest(BaseModel):
    configFile: str

# TC Server based mcp tools

@mcp.tool(
    name="get_runtime_behaviour_graph",
    title="Get Runtime Behaviour Graph",
    description="Fetches a structural graph of the application's runtime behaviour."
)
async def get_runtime_behaviour_graph(environment: Optional[str] = None) -> dict:
    response = await _impl_get_mindmap_structure(environment)
    return response.model_dump(exclude_none=True)


@mcp.tool(
    name="get_ui_node_details",
    title="Get UI Node Details",
    description="Fetch detailed UI info for a given screen/state/element group."
)
async def get_ui_node_details(
    screen: Optional[str] = None,
    state: Optional[str] = None,
    element_group: Optional[str] = None,
    environment: Optional[str] = None
) -> dict:
    response = await _impl_get_ui_node_details(screen, state, element_group, environment)
    return response.model_dump(exclude_none=True)


@mcp.tool(
    name="ask_runtime_behaviour",
    title="Ask About Runtime Behaviour",
    description="Ask a natural language question about the application's runtime behaviour."
)
async def ask_runtime_behaviour(query: str, environment: Optional[str] = None) -> dict:
    response = await _impl_ask_runtime_behaviour(query, environment)
    return response.model_dump(exclude_none=True)

# Chrome browser based mcp tools

@mcp.tool(
    name="fetch_extra_info_for_context_item",
    title="Fetch Extra Info For Context Item",
    description="Ask the Chrome extension to fetch extra info for a context item by id."
)
async def fetch_extra_info_for_context_item(id: str) -> dict:
    return await _impl_fetch_extra_info_for_context_item(id)

@mcp.tool(
    name="get_recent_console_logs",
    title="Get Recent Console Logs",
    description="Ask the Chrome extension to get recent console logs."
)
async def get_recent_console_logs(level: Optional[str] = None, count: Optional[str] = None, since_timestamp: Optional[str] = None) -> dict:
    return await _impl_get_recent_console_logs(level, count, since_timestamp)

@mcp.tool(
    name="get_dom_snapshot",
    title="Get DOM Snapshot",
    description="Ask the Chrome extension to get the current (simplified) DOM snapshot."
)
async def get_dom_snapshot() -> dict:
    return await _impl_get_dom_snapshot(True)

@mcp.tool(
    name="get_recent_request_response_pairs",
    title="Get Recent Request/Response Pairs",
    description="Ask the Chrome extension to get recent network request/response pairs (headers)."
)
async def get_recent_request_response_pairs(count: Optional[str] = None, since_timestamp: Optional[str] = None) -> dict:
    return await _impl_get_recent_request_response_pairs(count, since_timestamp)

# Local agent HTTP endpoints

@app.post("/run_exploration")
async def run_exploration_endpoint(request: ExplorationRequest):
    if explore_runner is None:
        return {"status": "error", "message": "Explore runner not initialized"}
    
    try:
        result = await run_exploration_from_file(request.configFile, explore_runner.openai_api_key)
        return {"status": "success", "result": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# Debug mcp tools via app post

@app.post("/_debug/fetch_extra_info_for_context_item")
async def fetch_extra_info_for_context_item_http(id: str = Body(..., embed=True)):
    return await _impl_fetch_extra_info_for_context_item(id)

@app.post("/_debug/get_recent_console_logs")
async def get_recent_console_logs_http(body: GetRecentConsoleLogsRequest = Body(...)):
    return await _impl_get_recent_console_logs(
        body.level,
        str(body.count) if body.count is not None else None,
        str(body.sinceTimestamp) if body.sinceTimestamp is not None else None
    )

@app.post("/_debug/get_dom_snapshot")
async def get_dom_snapshot_http():
    return await _impl_get_dom_snapshot(True)


@app.post("/_debug/get_recent_request_response_pairs")
async def get_recent_request_response_pairs_http(body: GetRecentRequestResponsePairsRequest = Body(...)):
    return await _impl_get_recent_request_response_pairs(
        str(body.count) if body.count is not None else None,
        str(body.sinceTimestamp) if body.sinceTimestamp is not None else None
    )

@app.post("/_debug/get_ui_node_details")
async def debug_get_ui_node_details(body: GetUiNodeDetailsRequest = Body(...)):
    return await _impl_get_ui_node_details(
        body.screen, body.state, body.elementGroup, body.environment
    )

@app.post("/_debug/get_runtime_behaviour_graph")
async def debug_get_runtime_behaviour_graph(body: GetMindMapStructureRequest = Body(...)):
    return await _impl_get_mindmap_structure(body.environment)

@app.post("/_debug/ask_runtime_behaviour")
async def debug_ask_runtime_behaviour(body: AskBehaviourRequest = Body(...)):
    return await _impl_ask_runtime_behaviour(body.query if body.query else "", body.environment)

# Implementations

async def _impl_get_mindmap_structure(env: Optional[str]) -> GetMindMapStructureResponse:
    feature_facade = get_feature_facade_instance()
    if feature_facade is None:
        raise RuntimeError("FeatureFacade is not initialized.")
    request = GetMindMapStructureRequest(environment=env)
    response = await asyncio.to_thread(feature_facade.get_mindmap_structure, request)    
    return response

async def _impl_get_ui_node_details(screen: Optional[str], state: Optional[str], element_group: Optional[str], environment: Optional[str]) -> GetUiNodeDetailsResponse:
    feature_facade = get_feature_facade_instance()
    if feature_facade is None:
        raise RuntimeError("FeatureFacade is not initialized.")
    request = GetUiNodeDetailsRequest(screen=screen, state=state, elementGroup=element_group, environment=environment)
    response = await asyncio.to_thread(feature_facade.get_ui_node_details, request)
    return response

async def _impl_ask_runtime_behaviour(query: str, environment: Optional[str]) -> AskBehaviourResponse:
    feature_facade = get_feature_facade_instance()
    if feature_facade is None:
        raise RuntimeError("FeatureFacade is not initialized.")
    request = AskBehaviourRequest(query=query, environment=environment)
    response = await asyncio.to_thread(feature_facade.ask_behaviour, request)
    return response
    
async def _impl_fetch_extra_info_for_context_item(id: str) -> dict:
    req = FetchExtraInfoForContextItemRequest(request_id="", id=id)
    try:
        resp = await send_ws_request(req)
        resp = cast(FetchExtraInfoForContextItemResponse, resp)
        logger.info(f"[fetch_extra_info_for_context_item] WS response received for id={id}")
        return {"context_id": id, "extra_info": resp.extraInfo}
    except Exception as e:
        logger.error(f"[fetch_extra_info_for_context_item] Error: {e}")
        return {"error": str(e)}

async def _impl_grab_screenshot() -> dict:
    req = GrabScreenshotRequest(request_id="")
    try:
        resp = await send_ws_request(req)
        resp = cast(GrabScreenshotResponse, resp)
        logger.info(f"[grab_screenshot] WS response received: imageBase64 length={len(resp.screenshotBase64) if resp.screenshotBase64 else 0}")
        return {"image_base64": resp.screenshotBase64}
    except Exception as e:
        logger.error(f"[grab_screenshot] Error: {e}")
        return {"error": str(e)}

async def _impl_get_recent_console_logs(level: Optional[str] = None, count: Optional[str] = None, since_timestamp: Optional[str] = None) -> dict:
    try:
        count_int = int(count) if count is not None else None
        since_timestamp_int = int(since_timestamp) if since_timestamp is not None else None
    except Exception:
        return {"error": f"Invalid type for count or since_timestamp"}
    req = GetRecentConsoleLogsRequest(request_id="", type="get_recent_console_logs", level=level, count=count_int, sinceTimestamp=since_timestamp_int)
    try:
        resp = await send_ws_request(req)
        resp = cast(GetRecentConsoleLogsResponse, resp)
        logger.info(f"[get_recent_console_logs] WS response received for level={level}, count={count}, since_timestamp={since_timestamp}: logs_count={len(resp.logs) if resp.logs else 0}")
        return {"logs": resp.logs}
    except Exception as e:
        logger.error(f"[get_recent_console_logs] Error: {e}")
        return {"error": str(e)}

async def _impl_get_dom_snapshot(includeStyles:bool=False) -> dict:
    req = GetDomSnapshotRequest(request_id="",includeStyles=includeStyles)
    try:
        resp = await send_ws_request(req)
        resp = cast(GetDomSnapshotResponse, resp)
        if(resp.dom):
            logger.info(f"[get_dom_snapshot] WS response received: dom length={len(resp.dom) if resp.dom else 0}")
            return {"dom": resp.dom}
        else:
            return {"error":"Please make sure the correct tab is open and active in your browser to fetch the DOM snapshot"}
    except Exception as e:
        logger.error(f"[get_dom_snapshot] Error: {e}")
        return {"error": str(e)}

async def _impl_get_recent_request_response_pairs(count: Optional[str] = None, since_timestamp: Optional[str] = None) -> dict:
    try:
        count_int = int(count) if count is not None else None
        since_timestamp_int = int(since_timestamp) if since_timestamp is not None else None
    except Exception:
        return {"error": f"Invalid type for count or since_timestamp"}
    req = GetRecentRequestResponsePairsRequest(request_id="", type="get_recent_request_response_pairs", count=count_int, sinceTimestamp=since_timestamp_int)
    try:
        resp = await send_ws_request(req)
        resp = cast(GetRecentRequestResponsePairsResponse, resp)
        logger.info(f"[get_recent_request_response_pairs] WS response received: pairs_count={len(resp.pairs) if resp.pairs else 0}")
        return {"pairs": resp.pairs}
    except Exception as e:
        logger.error(f"[get_recent_request_response_pairs] Error: {e}")
        return {"error": str(e)}


def start_server(args, api_key, facade=None):
    global explore_runner
    
    # Ensure logging is configured (fallback if not already set up)
    root_logger = logging.getLogger()
    if not root_logger.handlers:
        # Set up basic logging if not already configured
        import time
        try:
            timestamp = int(time.time())
            log_filename = f"testchimp_run_{timestamp}.log"
            file_handler = logging.FileHandler(log_filename, mode='w')
            file_handler.setLevel(logging.INFO)
            file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
            
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.INFO)
            console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
            
            root_logger.setLevel(logging.INFO)
            root_logger.addHandler(console_handler)
            root_logger.addHandler(file_handler)
            
            print(f"\nLOG FILE: {os.path.abspath(log_filename)}\n")
            logger.info(f"Logger configured to write to {log_filename}")
        except Exception as e:
            logger.warning(f"Could not set up file logging: {e}")
    
    if facade is not None:
        # set_feature_facade(facade) # This line is removed as per the edit hint
        pass # No longer needed
    logger.info("Starting Local Agent server... (supports prompt-based and script-based exploration configs)")
    logger.info("""To trigger an exploration, run:
        curl -X POST http://localhost:43449/run_exploration \
        -H \"Content-Type: application/json\" \
        -d '{\n    \"configFile\": \"<YOUR CONFIG FILE PATH>\"\n}'
        """)
    logger.info("Refer to documentation at https://github.com/awarelabshq/testchimp-sdk/blob/main/localagent/README.md for configuration")

    from dotenv import load_dotenv
    load_dotenv(args.env)

    explore_runner = ExploreRunner(openai_api_key=api_key)

    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=args.port, reload=False)