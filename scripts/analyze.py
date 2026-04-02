import sys
import asyncio
import scripts.config as config
from langchain_community.chat_models import ChatZhipuAI
from langchain_core.prompts import ChatPromptTemplate
from loguru import logger
from scripts.retrieval import get_expert_retriever, get_expert_reranker
from scripts.memory_store import get_memory_store

def get_expert_rca_prompt():
    """
    专家级根因分析专用提示词模板 (支持多轮对话)。
    """
    template = """
    你是一名顶尖的站点可靠性工程师 (SRE)，专注于复杂的生产事故排查。
    
    以下是从混合知识库中检索到的相关上下文信息（经过重排序）：
    {context}
    
    --- 之前的历史诊断记录 ---
    {history}
    
    --- 当前故障描述或更新信息 ---
    {question}
    
    请根据上述信息进行深度分析，并按以下格式提供中文报告：

    1. **现象总结**：基于当前信息描述故障现状。
    2. **深度分析**：结合知识库和历史记录，推测故障演进过程。**必须标注引用的文档名**。
    3. **排查建议**：提供精准的操作指令。
    4. **修复方案**：提供临时与长期建议。
    5. **后续行动**：如果你认为当前证据不足以定位根因，请明确列出你需要用户提供的额外数据（如：特定日志、监控截图等）。
    6. **置信度评分**：(1-5 分)，并简述理由。

    注意：如果需要更多信息，请在“后续行动”中以列表形式清晰呈现，并引导用户进行下一步。
    """
    return ChatPromptTemplate.from_template(template)

async def analyze_incident_expert(query, session_id="default"):
    """
    专家级异步根因分析逻辑：Hybrid Search + Reranking + Multi-turn Memory。
    """
    logger.info(f"开启专家级分析 (Session: {session_id}): {query[:50]}...")
    
    # 1. 内存存储加载历史
    memory = get_memory_store()
    history_list = memory.get_history(session_id)
    history_text = "\n".join([f"[{m['role'].upper()}]: {m['content'][:200]}..." for m in history_list]) if history_list else "无历史记录"

    # 2. 深度混合检索与重排序
    retriever = get_expert_retriever()
    reranker = get_expert_reranker()
    
    logger.info("[*] 正在执行混合检索及语义重排序...")
    # 初步检索
    loop = asyncio.get_event_loop()
    raw_docs = await loop.run_in_executor(None, lambda: retriever.invoke(query))
    
    # 语义重排 (取 Top 3)
    final_docs = await loop.run_in_executor(None, lambda: reranker.rerank(query, raw_docs, top_k=3))
    
    # 构造上下文
    context_list = []
    for doc in final_docs:
        source = doc.metadata.get('source', '未知文档')
        score = f"{doc.metadata.get('rerank_score', 0):.4f}"
        content = f"--- 来源: {source} (匹配分: {score}) ---\n{doc.page_content}"
        context_list.append(content)
    
    context = "\n\n".join(context_list)
    
    # 3. 初始化 LLM
    llm = ChatZhipuAI(
        model=config.MODEL_NAME,
        zhipuai_api_key=config.ZHIPUAI_API_KEY,
        temperature=0.2
    )

    # 4. 构建提示词并推理
    prompt_template = get_expert_rca_prompt()
    chain = prompt_template | llm
    
    logger.info("[*] 专家模型推理中...")
    result = await loop.run_in_executor(
        None, 
        lambda: chain.invoke({
            "context": context, 
            "history": history_text,
            "question": query
        })
    )
    
    report_content = result.content
    
    # 5. 更新会话记忆
    memory.add_message(session_id, "human", query)
    memory.add_message(session_id, "ai", report_content)
    
    logger.success(f"[✓] 专家级分析报告已生成 (Session: {session_id})。")
    return report_content

def main():
    if len(sys.argv) < 2:
        print("用法: python analyze.py \"错误描述\" [session_id]")
        return

    query = sys.argv[1]
    session_id = sys.argv[2] if len(sys.argv) > 2 else "local_test"
    
    print(f"\n--- 正在启动专家级 RCA 异步处理器 (Session: {session_id}) ---")
    report = asyncio.run(analyze_incident_expert(query, session_id))
    print("\n" + report)

if __name__ == "__main__":
    from scripts.logger import setup_logging
    setup_logging()
    main()
