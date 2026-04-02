import requests
import time
import json

# FastAPI 地址
URL = "http://127.0.0.1:8000/analyze"
SESSION_ID = f"test_session_{int(time.time())}"

def test_expert_flow():
    print(f"=== 启动专家级多轮排障测试 (Session: {SESSION_ID}) ===\n")

    # 第一轮：初步发现现象
    payload_1 = {
        "query": "数据库连接失败，错误代码 5432，应用日志提示 Connection Refused",
        "session_id": SESSION_ID
    }
    print("[第一轮请求]: 描述初步现象...")
    resp1 = requests.post(URL, json=payload_1, timeout=90)
    if resp1.status_code == 200:
        result1 = resp1.json()
        print("\n--- 第一轮诊断报告 ---")
        print(result1["report"][:500] + "...")
    else:
        print(f"Error: {resp1.status_code}, {resp1.text}")
        return

    print("\n" + "="*40 + "\n")

    # 第二轮：追问补充信息 (模拟用户根据 AI 建议提供了进一步的排障数据)
    payload_2 = {
        "query": "我已经检查了 telnet 结果，确实不通。但是数据库服务 systemctl status 显示是 running 的。",
        "session_id": SESSION_ID
    }
    print("[第二轮请求]: 补充排障数据 (Telnet 不通, 但服务正常)...")
    resp2 = requests.post(URL, json=payload_2, timeout=90)
    if resp2.status_code == 200:
        result2 = resp2.json()
        print("\n--- 第二轮深度分析报告 (记忆了上下文) ---")
        print(result2["report"])
    else:
        print(f"Error: {resp2.status_code}, {resp2.text}")

if __name__ == "__main__":
    print("提示: 专家级分析涉及重排序模型加载，首个请求可能较慢 (约 20-30s)。")
    test_expert_flow()
