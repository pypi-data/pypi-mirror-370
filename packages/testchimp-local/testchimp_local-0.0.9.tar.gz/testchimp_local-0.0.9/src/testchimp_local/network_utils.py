from typing import Dict, List
from .datas import RequestResponsePair

important_request_headers = {
    "content-type",
    "authorization",
    "cookie",
    "user-agent",
    "accept",
    "referer",
    "origin",
}

important_response_headers = {
    "content-type",
    "cache-control",
    "pragma",
    "expires",
    "x-frame-options",
    "x-content-type-options",
    "strict-transport-security",
    "set-cookie",
    "access-control-allow-origin",
    "access-control-allow-credentials",
    "content-security-policy",
}

def clean_headers(headers: Dict[str, str], allowed_keys: set[str]) -> Dict[str, str]:
    return {
        k: ("[REDACTED]" if k.lower() == "authorization" else v)
        for k, v in headers.items()
        if k.lower() in allowed_keys
    }

def clean_request_response_pair(pair: RequestResponsePair) -> RequestResponsePair:
    pair.requestHeaders = clean_headers(pair.requestHeaders, important_request_headers)
    pair.responseHeaders = clean_headers(pair.responseHeaders, important_response_headers)
    return pair  # no deepcopy needed