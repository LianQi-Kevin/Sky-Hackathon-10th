import axios from "axios";

// export const basic_url: string = new URL("backend", window.location.href).toString();
export const basic_url: string = 'http://36.150.110.74:9536'; // 本地调试用

const basic_axios = axios.create({
  baseURL: basic_url,
  timeout: 5000,
  headers: {
    "Content-Type": "application/json",
    'Access-Control-Allow-Origin': '*'
  }
});

export default basic_axios;