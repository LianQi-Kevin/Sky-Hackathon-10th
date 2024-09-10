from fastapi import HTTPException, WebSocketException, status

# file md5 verify error
file_md5_exception = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="file md5 verify error, please try re-upload"
)

# file md5 verify error
file_md5_ws_exception = WebSocketException(
    code=status.WS_1008_POLICY_VIOLATION,
    reason="file md5 verify error, please try re-upload"
)

# file not found
file_notFound_exception = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="file not found"
)

# file not found
file_notFound_ws_exception = WebSocketException(
    code=status.WS_1003_UNSUPPORTED_DATA,
    reason="file not found"
)

# file type not support
file_type_exception = WebSocketException(
    code=status.WS_1003_UNSUPPORTED_DATA,
    reason="file type not support, only support jpeg or png"
)