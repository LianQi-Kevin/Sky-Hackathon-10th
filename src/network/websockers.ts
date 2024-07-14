import {basic_url} from "@/network/basic";

export function WSS_embedding(nv_api_token: string, client_id: string, file_uuid: string, status_update: (status: string) => void) {
    const sockets = new WebSocket(`${basic_url.replace("http://", "ws://")}/link/${client_id}/ws?token=${nv_api_token}`);
    sockets.onopen = () => {
        sockets.send(JSON.stringify({ type: "action", data: file_uuid }));
        console.log("Action sent via WebSocket.");
    }

    sockets.onmessage = (message) => {
        const messageData = JSON.parse(message.toString());
        console.log("Received from WebSocket:", messageData);

        if (messageData.type === "embedding") {
            if (messageData.status === 'processing') {
                console.log('文件处理中...');
                status_update('文件处理中...');
            } else if (messageData.status === 'complete') {
                console.log('文件处理完成');
                status_update('文件处理完成');
                // 可以在这里添加更多的逻辑，比如显示文件链接或者通知用户
            }
        }
    }
}