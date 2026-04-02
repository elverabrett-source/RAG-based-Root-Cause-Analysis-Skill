import os
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 工作区根目录
BASE_DIR = Path(__file__).parent.parent

# 知识库路径
KNOWLEDGE_BASE_DIR = BASE_DIR / "data" / "knowledge_base"
# 向量数据库存储路径
VECTOR_DB_DIR = BASE_DIR / "data" / "vector_db"

# 创建目录（如果不存在）
KNOWLEDGE_BASE_DIR.mkdir(parents=True, exist_ok=True)
VECTOR_DB_DIR.mkdir(parents=True, exist_ok=True)

# 模型配置
ZHIPUAI_API_KEY = os.getenv("ZHIPUAI_API_KEY", "")
MODEL_NAME = "glm-4" # 使用智谱 GLM-4
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2" # 本地嵌入模型

# RAG 配置
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
TOP_K = 3 # 检索相关文档的数量

# 钉钉机器人配置
DINGTALK_WEBHOOK = os.getenv("DINGTALK_WEBHOOK", "")
DINGTALK_SECRET = os.getenv("DINGTALK_SECRET", "") # 加签路径，可选
DINGTAK_CONFIDENCE_THRESHOLD = 2 # 仅当置信度高于此值时进行推送
