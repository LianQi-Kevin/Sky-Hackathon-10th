from fastapi import HTTPException, WebSocketException, status

# file status not embedded
file_notEmbedded_exception = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="file not embedded"
)

# file status not embedded
file_notEmbedded_ws_exception = WebSocketException(
    code=status.WS_1008_POLICY_VIOLATION,
    reason="file not embedded"
)

# nvapi verify failed
nvapi_verify_failed_exception = WebSocketException(
    code=status.WS_1008_POLICY_VIOLATION,
    reason="nv_api_key verify failed"
)