import sys
from pathlib import Path

# --- 必须放在最顶部：确保项目根目录在 Python 路径中 ---
BASE_DIR = Path(__file__).parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))
# --------------------------------------------------

import re
import time
import uvicorn
import scripts.config as config
from fastapi import FastAPI, HTTPException, Body, BackgroundTasks
from pydantic import BaseModel, Field
from scripts.analyze import analyze_incident_expert
from scripts.logger import setup_logging, logger
from scripts.notifier import send_dingtalk_notification
from scripts.memory_store import get_memory_store

# 初始化 FastAPI 应用
app = FastAPI(
    title="企业级专家 RCA 分析服务",
    description="提供基于 Hybrid RAG + Reranking 的深度分析 API。支持多轮对话、置信度评估及钉钉推送。",
    version="3.0.0"
)

def extract_confidence_score(report: str) -> int:
    """
    从分析报告中提取置信度评分数字。
    """
    match = re.search(r"置信度评分[^\d]*(\d)", report)
    if match:
        return int(match.group(1))
    return 1 

# 定义请求数据模型
class RCAQuery(BaseModel):
    query: str = Field(
        ..., 
        description="故障描述或追问信息",
        json_schema_extra={"example": "应用连接数据库拒绝，错误码 5432"}
    )
    session_id: str = Field(
        "default", 
        description="会话 ID，用于支持多轮排障对话",
        json_schema_extra={"example": "session_123"}
    )

# 健康检查接口
@app.get("/health", tags=["公共接口"])
async def health_check():
    return {"status": "ok", "timestamp": time.time(), "engine": "expert-v3"}

# 清除会话接口
@app.delete("/session/{session_id}", tags=["会话管理"])
async def clear_session(session_id: str):
    get_memory_store().clear(session_id)
    return {"status": "success", "message": f"Session {session_id} has been cleared"}

# 核心 RCA 分析接口
@app.post("/analyze", tags=["核心分析"], response_description="专家级 RCA 报告")
async def analyze_endpoint(background_tasks: BackgroundTasks, data: RCAQuery = Body(...)):
    """
    接收故障描述并返回专家级分析报告。支持通过 session_id 进行多轮深入排障。
    """
    logger.info(f"接收到专家级分析请求 (Session: {data.session_id}): {data.query[:50]}")
    try:
        # 1. 调用专家级 RAG 分析逻辑 (Hybrid Search + Reranking + History)
        report = await analyze_incident_expert(data.query, data.session_id)
        
        # 2. 判定是否需要推送报告
        confidence = extract_confidence_score(report)
        
        if confidence >= config.DINGTAK_CONFIDENCE_THRESHOLD:
            logger.info(f"触发钉钉自动推送 (置信度 {confidence})")
            background_tasks.add_task(send_dingtalk_notification, report, data.query)

        return {
            "session_id": data.session_id,
            "report": report,
            "status": "success",
            "confidence_score": confidence,
            "is_multiturn": True
        }
    except Exception as e:
        logger.exception(f"分析请求处理失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    setup_logging()
    # 启动服务
    uvicorn.run(app, host="0.0.0.0", port=8000, access_log=False)
