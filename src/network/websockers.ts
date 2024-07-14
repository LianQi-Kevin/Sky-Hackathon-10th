import { basic_url } from '@/network/basic';

// 定义一个全局变量来存储 WebSocket 实例
let globalSocket: WebSocket | null = null;

// 初始化 WebSocket 连接的函数
export function initializeWebSocket(
  nv_api_token: string,
  client_id: string,
  onMessage: Function
) {
  if (!globalSocket || globalSocket.readyState === WebSocket.CLOSED) {
    globalSocket = new WebSocket(
      `${basic_url.replace(
        'http://',
        'ws://'
      )}/link/${client_id}/ws?token=${nv_api_token}`
    );

    globalSocket.onopen = () => {
      console.log('WebSocket connection established.');
    };

    globalSocket.onmessage = (event: MessageEvent<any>) => onMessage(event);

    globalSocket.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    globalSocket.onclose = () => {
      console.log('WebSocket connection closed.');
      globalSocket = null; // Reset the global socket on close
    };
  }
  return globalSocket;
}
