import time
import hmac
import hashlib
import base64
import urllib.parse
import httpx
import scripts.config as config
from scripts.logger import logger

def generate_dingtalk_url():
    """
    生成带签名的钉钉 Webhook URL (如果配置了 Secret)。
    """
    url = config.DINGTALK_WEBHOOK
    secret = config.DINGTALK_SECRET

    if not url:
        return None

    if not secret:
        return url

    timestamp = str(round(time.time() * 1000))
    secret_enc = secret.encode('utf-8')
    string_to_sign = '{}\n{}'.format(timestamp, secret)
    string_to_sign_enc = string_to_sign.encode('utf-8')
    hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
    sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
    
    return f"{url}&timestamp={timestamp}&sign={sign}"

async def send_dingtalk_notification(report_content: str, query: str):
    """
    异步发送钉钉 Markdown 消息。
    """
    webhook_url = generate_dingtalk_url()
    if not webhook_url:
        logger.warning("[!] 钉钉 Webhook 未配置，跳过推送。")
        return

    # 构建 Markdown 内容
    markdown_text = f"### [RCA告警] 发现系统故障\n\n" \
                    f"**故障描述**: {query}\n\n" \
                    f"--- \n\n" \
                    f"{report_content}\n\n" \
                    f"> *分析引擎: GLM-4 (RAG 高级版)*"

    data = {
        "msgtype": "markdown",
        "markdown": {
            "title": "[RCA告警] 点击查看详情",
            "text": markdown_text
        }
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(webhook_url, json=data, timeout=10)
            res_json = response.json()
            if res_json.get("errcode") == 0:
                logger.success("[✓] 钉钉报告已成功推送至群聊。")
            else:
                logger.error(f"[!] 钉钉推送失败: {res_json.get('errmsg')}")
    except Exception as e:
        logger.exception(f"[!] 钉钉推送过程发生异常: {e}")

if __name__ == "__main__":
    # 简单的本地测试逻辑
    import asyncio
    asyncio.run(send_dingtalk_notification("这是一条测试 RCA 报告内容。", "测试故障描述"))
