import type {UploadProgressEvent, UploadRequestOptions} from "element-plus";
import {isNil} from "lodash-es";

import {basic_url} from "@/network/basic";
import {UploadAjaxError} from "element-plus/es/components/upload/src/ajax";

// interface startedRequest {
//     nv_api_key: string;
//     client_id: string;
// }
//
// interface FileContrastRequest {
//     client_id: string;
//     standard_id: string;
//     user_file_id: string;
// }
//
// interface standardAskRequest {
//     client_id: string;
//     standard_id: string;
//     query: string;
// }
//
// interface standardInfoResponse {
//     standardList: {
//         file_id: string;
//         file_name: string;
//     }[]
// }

function getError(
    action: string,
    option: UploadRequestOptions,
    xhr: XMLHttpRequest
) {
    let msg: string
    if (xhr.response) {
        msg = `${xhr.response.error || xhr.response}`
    } else if (xhr.responseText) {
        msg = `${xhr.responseText}`
    } else {
        msg = `fail to ${option.method} ${action} ${xhr.status}`
    }

    return new UploadAjaxError(msg, xhr.status, option.method, action)
}

function getBody(xhr: XMLHttpRequest): XMLHttpRequestResponseType {
    const text = xhr.responseText || xhr.response
    if (!text) {
        return text
    }

    try {
        return JSON.parse(text)
    } catch {
        return text
    }
}

export async function fileAjaxUpload(option: UploadRequestOptions) {
    // 组装请求
    const xhr = new XMLHttpRequest();

    // CORS
    xhr.withCredentials = true

    const url = new URL(basic_url);
    url.pathname = '/upload/';

    const action: string = url.toString();

    // 构建formData
    const extra_data = option.data || {}
    const formData = new FormData();
    formData.append('file', option.file)
    formData.append('client_id', extra_data.client_id as string);
    formData.append('process', extra_data.process.toString());

    // 追踪上传进度
    if (xhr.upload) {
        xhr.upload.addEventListener('progress', (evt) => {
            const progressEvt = evt as UploadProgressEvent
            progressEvt.percent = evt.total > 0 ? (evt.loaded / evt.total) * 100 : 0
            console.debug('progressEvt:', progressEvt)
            option.onProgress(progressEvt)
        })
    }

    // 上传成功
    xhr.addEventListener('load', () => {
        if (xhr.status < 200 || xhr.status >= 300) {
            return option.onError(getError(action, option, xhr))
        }
        option.onSuccess(getBody(xhr))
    })

    // 上传失败
    xhr.addEventListener('error', () => option.onError(getError(action, option, xhr)))

    // 发送请求
    xhr.open(option.method, action, true);

    // 构建请求头
    const headers = option.headers || {}
    if (headers instanceof Headers) {
        headers.forEach((value, key) => xhr.setRequestHeader(key, value))
    } else {
        for (const [key, value] of Object.entries(headers)) {
            if (isNil(value)) continue
            xhr.setRequestHeader(key, String(value))
        }
    }

    xhr.send(formData);
    return xhr;
}