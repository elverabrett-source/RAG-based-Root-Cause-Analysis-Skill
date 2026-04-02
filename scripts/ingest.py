import os
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
import config

def main():
    print(f"[*] 正在从 {config.KNOWLEDGE_BASE_DIR} 加载文档...")
    
    # 1. 加载所有 Markdown 文档
    loader = DirectoryLoader(
        str(config.KNOWLEDGE_BASE_DIR), 
        glob="**/*.md", 
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"}
    )
    documents = loader.load()
    print(f"[+] 加载了 {len(documents)} 个文件。")

    # 2. 文本分块
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.CHUNK_SIZE, 
        chunk_overlap=config.CHUNK_OVERLAP
    )
    texts = text_splitter.split_documents(documents)
    print(f"[+] 成功将文档切分为 {len(texts)} 个分块。")

    # 3. 初始化嵌入模型 (使用本地模型)
    print(f"[*] 正在初始化嵌入模型: {config.EMBEDDING_MODEL}...")
    embeddings = HuggingFaceEmbeddings(model_name=config.EMBEDDING_MODEL)

    # 4. 创建并持久化向量数据库
    print(f"[*] 正在将分块存入向量数据库 ({config.VECTOR_DB_DIR})...")
    vector_db = Chroma.from_documents(
        documents=texts,
        embedding=embeddings,
        persist_directory=str(config.VECTOR_DB_DIR)
    )
    vector_db.persist()
    print("[✓] 知识库摄取完成！")

if __name__ == "__main__":
    main()
