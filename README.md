# 🚀 企业级专家 RCA (根因分析) Skill

这是一个基于 **LangChain 0.3** 和 **Hybrid RAG** 技术的智能故障排障 Skill。它通过结合语义搜索与关键字搜索（BM25），配合重排序模型 (Reranker)，能够以“技能插件”的形式精准定位运维事故的根源。

## 🌟 核心特性
- **混合检索 (Hybrid Search)**: 结合向量数据库与 BM25，对技术术语（如错误码、IP地址）的匹配极其精准。
- **语义重排序 (Reranker)**: 使用 Cross-Encoder 模型对召回结果进行高精度二次排序，彻底消除 AI “幻觉”。
- **多轮交互推导**: 具备 Session 记忆，可针对故障现象进行连续追问，支持深层逻辑分析。
- **企业级集成**: 提供 FastAPI 异步接口，支持钉钉群机器人自动推送分析报告。

## 🛠️ 快速开始

### 1. 环境准备
```bash
pip install -r requirements.txt
```

### 2. 配置环境变量
将 `.env.template` 重命名为 `.env` 并填写您的配置：
- `ZHIPUAI_API_KEY`: 智谱 AI 的 API Key。
- `DINGTALK_WEBHOOK`: 钉钉机器人 Webhook 地址。

### 3. 初始化知识库
将您的排障文档 (Markdown 格式) 放入 `data/knowledge_base/` 目录下。

### 4. 启动服务
```bash
python scripts/server.py
```

## 📂 项目结构
- `scripts/retrieval.py`: 混合检索与重排序核心逻辑。
- `scripts/analyze.py`: 专家级分析引擎。
- `scripts/memory_store.py`: 多轮会话管理。
- `scripts/server.py`: FastAPI 服务入口。

---
> [!IMPORTANT]
> **安全提醒**: 请勿将 `.env` 文件提交至代码仓库，本仓库已内置 `.gitignore`。
