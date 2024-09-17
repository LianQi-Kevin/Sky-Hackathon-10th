def nvapi_verify(nvapi_key: str) -> bool:
    if not nvapi_key.startswith("nvapi-") or len(nvapi_key) != 70:
        return False
    return True
