# -*- coding: utf-8 -*-
import os
import requests
import json
import time
import hashlib
import base64


def generate_summary(text):
    """
    使用讯飞星火大模型生成文章摘要
    需要在仓库的 Settings > Secrets and Variables > Actions 中添加以下密钥：
    - SPARK_API_URL: API地址 (如: https://spark-api.xf-yun.com/v3.1/chat)
    - SPARK_APP_ID: 应用ID
    - SPARK_API_KEY: API密钥
    - SPARK_API_SECRET: API密钥Secret
    """
    api_url = os.environ.get("SPARK_API_URL")
    app_id = os.environ.get("SPARK_APP_ID")
    api_key = os.environ.get("SPARK_API_KEY")
    api_secret = os.environ.get("SPARK_API_SECRET")

    if not all([api_url, app_id, api_key, api_secret]):
        return ""

    domain = "generalv3"
    if "v1.1" in api_url:
        domain = "generalv1.5"
    elif "v2.1" in api_url:
        domain = "generalv2"

    prompt = """你是文章摘要生成器。请对用户提供的内容进行总结，要求：
1. 用简洁、完整的语句概括文章的主要内容
2. 直接返回纯文本，不要使用Markdown格式
3. 以"本文介绍了"开头
4. 摘要长度控制在100-200字左右
5. 捕捉文章的核心要点

请对以下内容生成摘要："""

    payload = {
        "header": {
            "app_id": app_id,
            "uid": "summary_bot"
        },
        "parameter": {
            "chat": {
                "domain": domain,
                "temperature": 0.5,
                "max_tokens": 1024
            }
        },
        "payload": {
            "message": {
                "text": [
                    {
                        "role": "system",
                        "content": prompt
                    },
                    {
                        "role": "user",
                        "content": text[:8000]
                    }
                ]
            }
        }
    }

    try:
        if api_url.startswith("wss://"):
            response = websocket_api(api_url, app_id, api_key, api_secret, payload)
        else:
            response = http_api(api_url, app_id, api_key, api_secret, payload)

        if response:
            return response
        return ""
    except Exception as e:
        print(f"生成摘要异常: {str(e)}")
        return ""


def hmac_sha256(key, content):
    """
    HMAC-SHA256加密
    """
    import hmac
    return hmac.new(key.encode('utf-8'), content.encode('utf-8'), hashlib.sha256).hexdigest()


def http_api(api_url, app_id, api_key, api_secret, payload):
    """
    HTTP方式调用星火API
    """
    date_str = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime())
    host = api_url.split('/')[2]

    signature_origin = f"host: {host}\ndate: {date_str}\nmethod: POST / HTTP/1.1"
    signature_sha = hmac_sha256(api_secret, signature_origin)
    authorization = f'api_key="{api_key}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature_sha}"'

    headers = {
        "Authorization": authorization,
        "Date": date_str,
        "Content-Type": "application/json",
        "Host": host
    }

    response = requests.post(
        url=api_url,
        headers=headers,
        data=json.dumps(payload),
        timeout=30
    )

    if response.status_code == 200:
        result = response.json()
        if result.get("header", {}).get("code") == 0:
            return result.get("payload", {}).get("choices", {}).get("text", [{}])[0].get("content", "")
        else:
            print(f"API返回错误: {result}")
            return ""
    else:
        print(f"请求失败: {response.status_code} - {response.text}")
        return ""


def websocket_api(api_url, app_id, api_key, api_secret, payload):
    """
    WebSocket方式调用星火API
    """
    try:
        import websocket

        date_str = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime())
        host = api_url.split('/')[2]

        signature_origin = f"host: {host}\ndate: {date_str}\nmethod: GET / HTTP/1.1"
        signature_sha = hmac_sha256(api_secret, signature_origin)
        authorization = f'api_key="{api_key}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature_sha}"'

        auth_url = f"{api_url}?authorization={base64.b64encode(authorization.encode('utf-8')).decode('utf-8')}&date={date_str.replace(' ', '%20')}&host={host}"

        result_text = []

        def on_message(ws, message):
            data = json.loads(message)
            if data.get("header", {}).get("code") == 0:
                text_list = data.get("payload", {}).get("choices", {}).get("text", [])
                for item in text_list:
                    result_text.append(item.get("content", ""))
            else:
                print(f"API返回错误: {data}")

        def on_error(ws, error):
            print(f"WebSocket错误: {error}")

        def on_close(ws, close_status_code, close_reason):
            pass

        def on_open(ws):
            ws.send(json.dumps(payload))

        ws = websocket.WebSocketApp(
            url=auth_url,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close,
            on_open=on_open
        )

        ws.run_forever()

        return "".join(result_text)

    except ImportError:
        print("websocket-client库未安装，尝试使用HTTP方式")
        return http_api(api_url.replace("wss://", "https://").replace("/v3.1/", "/v3/").replace("/v2.1/", "/v2/"), app_id, api_key, api_secret, payload)


if __name__ == "__main__":
    test_content = """
    GitHub Actions是一种持续集成和持续部署(CI/CD)工具，可以自动化软件开发工作流程。
    它允许开发者在GitHub仓库中直接定义工作流程，当特定事件发生时自动执行任务。
    例如，可以在每次push代码时自动运行测试、构建和部署应用程序。
    GitHub Actions使用YAML文件定义工作流程，包括触发条件、作业和步骤。
    关键概念包括：工作流(Workflow)、事件(Event)、作业(Job)、步骤(Step)和动作(Action)。
    """
    summary = generate_summary(test_content)
    print(f"生成的摘要: {summary}")
