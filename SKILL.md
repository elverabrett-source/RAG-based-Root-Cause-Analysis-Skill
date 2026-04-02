# 企业级高级 RCA 根因分析技能 (Advanced)

这是一个面向企业运维团队设计的“高级技能”，利用 RAG（检索增强生成）技术，在海量排障手册和事故报告中自动定位故障根因。

## 🌟 高级特性

- **API 服务化**：基于 FastAPI 构建，可轻松集成到飞书、钉钉、Slack 等办公自动化平台。
- **引用溯源**：AI 分析结果中会明确标注参考的手册文件名，消灭建议中的“虚假信息”。
- **置信度评估**：AI 自动对分析结果进行 1-5 分的置信度评分，并在低分时引导人工干预。
- **结构化日志**：集成 Loguru 日志系统，完整记录分析链路，方便企业审计与复盘。
- **容器化就绪**：提供一键式 Docker 部署方案。

## 🚀 部署指南

### 1. 容器化部署 (推荐)
```bash
docker build -t rca-expert:v2 .
docker run -d -p 8000:8000 --env ZHIPUAI_API_KEY=你的密钥 rca-expert:v2
```

### 2. 外部 API 调用示例
- **接口地址**：`POST /analyze`
- **请求负载**：
  ```json
  {
    "query": "应用出现数据库连接超时，报错详细内容为..."
  }
  ```

## 🛠️ 知识库维护

如果要提升技能的专业性，请将企业的知识资产（Markdown 格式）存入 `data/knowledge_base/`，随后运行：
```powershell
python scripts/ingest.py
```
系统将自动重新构建向量库。

## 📁 目录说明

- `scripts/server.py`: FastAPI 服务入口。
- `scripts/analyze.py`: 核心 RAG 推理引擎。
- `scripts/logger.py`: 结构化日志模块。
- `logs/`: 存放 JSON 格式的审计日志。
- `data/`: 知识库与向量库存储。
- `Dockerfile`: 生产级部署配置。
