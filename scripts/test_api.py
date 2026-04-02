import requests
import json

# FastAPI 本地地址
URL = "http://127.0.0.1:8000/analyze"

def test_rca():
    # 模拟一个数据库报错
    payload = {
        "query": "应用无法连接到 PostgreSQL 数据库，提示 Connection Refused"
    }
    
    print(f"[*] 正在向 {URL} 发送测试请求 (超时限制: 60s)...")
    try:
        response = requests.post(URL, json=payload, timeout=60)
        if response.status_code == 200:
            result = response.json()
            print("\n--- 企业级 RCA 分析报告 (API 返回) ---")
            print(result["report"])
            
            print("\n" + "="*40)
            print(f"[+] 分析引擎: {result.get('model_engine', 'N/A')}")
            print(f"[+] 置信度评分: {result.get('confidence_score', 'N/A')}/5")
            print(f"[+] 钉钉推送状态: {'✅ 已发送' if result.get('notified') else '⏭️ 已跳过 (或失败)'}")
            print("="*40)
        else:
            print(f"[!] 请求失败，状态码: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"[!] 无法连接到服务: {e}")

if __name__ == "__main__":
    print("提示: 在运行此测试脚本前，请确保执行了 'python scripts/server.py'")
    test_rca()
