import axios from 'axios';
import WebSocket from 'ws';
import fs from 'fs';

async function testUploadAndWebSocket(url: string, clientId: string, filePath: string) {
    const wsUrl = `ws://${url}/link/${clientId}/ws?token=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`;
    const websocket = new WebSocket(wsUrl);

    websocket.on('open', async () => {
        console.log("WebSocket connection established.");

        const form = new FormData();
        form.append('file', fs.createReadStream(filePath), { filename: 'test.pdf', contentType: 'application/octet-stream' });
        form.append('client_id', clientId);
        form.append('process', 'true');

        try {
            await new Promise(resolve => setTimeout(resolve, 2000));
            const response = await axios.post(`http://${url}/upload/`, form, {
                headers: {
                    ...form.getHeaders()
                }
            });
            console.log(response.data);
            console.log("HTTP request for file upload sent.");
        } catch (error) {
            console.error("Error during file upload:", error);
        }

        websocket.send(JSON.stringify({ type: "action", data: "b36565a8-efbc-4a46-af36-661fe9f63ad6" }));
        console.log("Action sent via WebSocket.");
    });

    websocket.on('message', (message) => {
        const messageData = JSON.parse(message.toString());
        console.log("Received from WebSocket:", messageData);

        if (messageData.type === "embedding" && messageData.status === "complete") {
            const fileUuid = messageData.file_uuid;
            console.log(`File upload completed with UUID: ${fileUuid}`);

            websocket.send(JSON.stringify({ type: "query", data: "如果一款电动自行车电池仓大小有余量，使得用户可以加装更大的电池，是否符合国家标准？" }));
            console.log("Query sent via WebSocket.");
        }
    });

    setTimeout(() => {
        websocket.close();
    }, 10000);
}

async function testUploadFile(url: string, clientId: string, filePath: string) {
    const form = new FormData();
    form.append('file', fs.createReadStream(filePath), { filename: 'test.pdf', contentType: 'application/octet-stream' });
    form.append('client_id', clientId);
    form.append('process', 'true');

    try {
        const response = await axios.post(`${url}/upload/`, form, {
            headers: {
                ...form.getHeaders()
            }
        });
        return response.data;
    } catch (error) {
        console.error("Error during file upload:", error);
    }
}

async function testWebSocket(url: string, clientId: string) {
    const wsUrl = `${url}/link/${clientId}/ws?token=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`;
    const websocket = new WebSocket(wsUrl);

    websocket.on('open', () => {
        websocket.send(JSON.stringify({ type: "query", data: "如果一款电动自行车电池仓大小有余量，使得用户可以加装更大的电池，是否符合国家标准？" }));
        console.log(111);
    });

    websocket.on('message', (message) => {
        console.log("Received from server:", message.toString());
    });

    setTimeout(() => {
        websocket.close();
    }, 10000);
}

async function main() {
    const serverUrl = "http://36.150.110.74:9536/";
    const clientId = "test_2";
    const filePath = "./GB1776-2018.pdf";

    await testUploadAndWebSocket(serverUrl, clientId, filePath);
}

main().catch(console.error);
