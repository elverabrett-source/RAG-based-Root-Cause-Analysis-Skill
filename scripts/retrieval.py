import scripts.config as config
from typing import List
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.retrievers import BM25Retriever
from langchain_core.retrievers import BaseRetriever
from langchain_core.documents import Document
from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import CrossEncoder
from scripts.logger import logger

class SimpleEnsembleRetriever(BaseRetriever):
    """
    手动实现的混合检索融合器，解决某些环境下 langchain.retrievers 缺失的问题。
    """
    retrievers: List[BaseRetriever]
    weights: List[float]

    model_config = {
        "arbitrary_types_allowed": True,
    }

    def _get_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun = None
    ) -> List[Document]:
        all_docs = []
        # 分别调用各个检索器
        for i, retriever in enumerate(self.retrievers):
            docs = retriever.invoke(query)
            # 标记来源类型并简单加权 (此处为简化实现，主要靠后续 Reranker 精排)
            for doc in docs:
                doc.metadata["retrieval_source"] = f"retriever_{i}"
            all_docs.extend(docs)
        
        # 去重 (基于内容)
        unique_docs = []
        seen_content = set()
        for doc in all_docs:
            if doc.page_content not in seen_content:
                unique_docs.append(doc)
                seen_content.add(doc.page_content)
        
        return unique_docs

def setup_hybrid_retriever():
    """
    建立混合检索引擎：结合 BM25 和 Chroma。
    """
    logger.info("[*] 正在构建混合检索 (Hybrid Search) 引擎...")
    
    # 1. 向量检索器 (Vector)
    embeddings = HuggingFaceEmbeddings(model_name=config.EMBEDDING_MODEL)
    vector_db = Chroma(
        persist_directory=str(config.VECTOR_DB_DIR), 
        embedding_function=embeddings
    )
    vector_retriever = vector_db.as_retriever(search_kwargs={"k": 10})

    # 2. 关键词检索器 (BM25)
    loader = DirectoryLoader(
        str(config.KNOWLEDGE_BASE_DIR), 
        glob="**/*.md", 
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"}
    )
    docs = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.CHUNK_SIZE, 
        chunk_overlap=config.CHUNK_OVERLAP
    )
    all_chunks = text_splitter.split_documents(docs)
    
    if not all_chunks:
        logger.warning("[!] 知识库为空，无法构建 BM25 检索器。")
        return vector_retriever, []

    bm25_retriever = BM25Retriever.from_documents(all_chunks)
    bm25_retriever.k = 10

    # 3. 融合检索器 (使用我们手写的 SimpleEnsembleRetriever)
    ensemble_retriever = SimpleEnsembleRetriever(
        retrievers=[bm25_retriever, vector_retriever], 
        weights=[0.5, 0.5]
    )
    
    logger.success("[✓] 混合检索引擎构建完成。")
    return ensemble_retriever, all_chunks

class Reranker:
    """
    语义重排序器：使用 Cross-Encoder 模型。
    """
    def __init__(self, model_name="cross-encoder/ms-marco-MiniLM-L-6-v2"):
        logger.info(f"[*] 正在加载重排序模型: {model_name} (约占用 500MB 内存)...")
        # 兼容性导入
        try:
            self.model = CrossEncoder(model_name)
        except Exception as e:
            logger.error(f"[!] 加载重排序模型失败: {e}")
            self.model = None

    def rerank(self, query, documents, top_k=3):
        if not documents or not self.model:
            return documents[:top_k]

        pairs = [[query, doc.page_content] for doc in documents]
        scores = self.model.predict(pairs)
        
        for i, doc in enumerate(documents):
            doc.metadata["rerank_score"] = float(scores[i])
        
        sorted_docs = sorted(documents, key=lambda x: x.metadata["rerank_score"], reverse=True)
        return sorted_docs[:top_k]

_retriever_instance = None
_reranker_instance = None

def get_expert_retriever():
    global _retriever_instance
    if _retriever_instance is None:
        _retriever_instance, _ = setup_hybrid_retriever()
    return _retriever_instance

def get_expert_reranker():
    global _reranker_instance
    if _reranker_instance is None:
        _reranker_instance = Reranker()
    return _reranker_instance
