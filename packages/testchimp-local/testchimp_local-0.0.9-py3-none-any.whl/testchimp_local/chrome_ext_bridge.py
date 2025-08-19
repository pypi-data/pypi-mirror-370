import uuid
import asyncio
from fastapi import WebSocket, WebSocketDisconnect, FastAPI
from typing import Optional, Dict, Any, Callable, Type
from .datas import (
    GetDomSnapshotResponse, GetRecentRequestResponsePairsResponse, GrabScreenshotRequest, GrabScreenshotResponse,
    GetRecentConsoleLogsRequest, GetRecentConsoleLogsResponse,
    FetchExtraInfoForContextItemRequest, FetchExtraInfoForContextItemResponse,
    WSBaseMessage
)
import json

# Global state for the Chrome extension bridge
chrome_ws: Optional[WebSocket] = None
pending_ws_requests: Dict[str, asyncio.Future] = {}

# Message type -> response model class
RESPONSE_MODELS: Dict[str, Type[WSBaseMessage]] = {
    "grab_screenshot": GrabScreenshotResponse,
    "get_recent_console_logs": GetRecentConsoleLogsResponse,
    "fetch_extra_info_for_context_item": FetchExtraInfoForContextItemResponse,
    "get_dom_snapshot":GetDomSnapshotResponse,
    "get_recent_request_response_pairs":GetRecentRequestResponsePairsResponse,
    # Add more as needed
}

def setup_chrome_ext_bridge(app: FastAPI):
    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket):
        global chrome_ws
        chrome_ws = websocket
        await websocket.accept()
        print("[chrome_ext_bridge] WebSocket connection established.")
        try:
            while True:
                data = await websocket.receive_text()
                print(f"[chrome_ext_bridge] Received WS message: {data}")
                try:
                    msg_dict = json.loads(data)
                    msg_type = msg_dict.get("type")
                    request_id = msg_dict.get("request_id")
                    print(f"[chrome_ext_bridge] Parsed type: {msg_type}, request_id: {request_id}")
                    model_cls = RESPONSE_MODELS.get(msg_type)
                    if model_cls and request_id in pending_ws_requests:
                        msg = model_cls.model_validate(msg_dict)
                        pending_ws_requests[request_id].set_result(msg)
                        print(f"[chrome_ext_bridge] Set result for request_id: {request_id}")
                    else:
                        print(f"[chrome_ext_bridge] No match for type: {msg_type}, request_id: {request_id}")
                except Exception as e:
                    print(f"[chrome_ext_bridge] Error parsing WS message: {e}")
                    continue
        except WebSocketDisconnect:
            chrome_ws = None
            # Clean up all pending requests
            for request_id, future in pending_ws_requests.items():
                if not future.done():
                    future.set_exception(RuntimeError("WebSocket disconnected before response was received"))
            pending_ws_requests.clear()
            print("[chrome_ext_bridge] WebSocket disconnected, cleaned up pending requests.")

async def send_ws_request(request_model: WSBaseMessage, timeout: float = 10.0, max_retries: int = 3, retry_delay: float = 1.0) -> WSBaseMessage:
    last_exception = None
    for attempt in range(max_retries):
        if chrome_ws is None:
            last_exception = RuntimeError("Chrome extension is not connected. Please ensure the extension is active and the browser tab is focused.")
        else:
            request_id = str(uuid.uuid4())
            request_model.request_id = request_id
            future = asyncio.get_event_loop().create_future()
            pending_ws_requests[request_id] = future
            try:
                await chrome_ws.send_text(request_model.model_dump_json())
            except Exception as e:
                del pending_ws_requests[request_id]
                last_exception = RuntimeError(f"Failed to send request to Chrome extension: {e}")
            else:
                try:
                    response = await asyncio.wait_for(future, timeout=timeout)
                    return response
                finally:
                    if request_id in pending_ws_requests:
                        del pending_ws_requests[request_id]
        # If we reach here, there was a problem; wait and retry
        if attempt < max_retries - 1:
            await asyncio.sleep(retry_delay)
    # If all retries failed, raise the last exception
    if last_exception is not None:
        raise last_exception
    else:
        raise RuntimeError("Unknown error in send_ws_request: no exception captured during retries.") 