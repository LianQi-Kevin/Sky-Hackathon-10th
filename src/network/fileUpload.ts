interface startedRequest {
    nv_api_key: string;
    client_id: string;
}

interface FileContrastRequest {
    client_id: string;
    standard_id: string;
    user_file_id: string;
}

interface standardAskRequest {
    client_id: string;
    standard_id: string;
    query: string;
}

interface standardInfoResponse {
    standardList: {
        file_id: string;
        file_name: string;
    }[]
}
