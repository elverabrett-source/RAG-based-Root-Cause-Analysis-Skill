import time
from collections import defaultdict
from loguru import logger

class MemoryStore:
    """
    轻量级内存会话管理器。
    用于存储每个 session_id 对应的对话历史和分析状态。
    """
    def __init__(self, ttl_seconds=3600):
        # 使用字典存储：session_id -> { "history": [], "last_activity": timestamp }
        self.sessions = defaultdict(lambda: {"history": [], "last_activity": time.time()})
        self.ttl = ttl_seconds

    def get_history(self, session_id):
        """
        获取指定会话的历史记录。
        """
        self._cleanup()
        session = self.sessions[session_id]
        session["last_activity"] = time.time()
        return session["history"]

    def add_message(self, session_id, role, content):
        """
        向历史记录添加一条消息。
        role: "human" 或 "ai"
        """
        session = self.sessions[session_id]
        session["history"].append({"role": role, "content": content})
        session["last_activity"] = time.time()
        
        # 保持历史记录长度在合理范围内 (例如最近 10 条)
        if len(session["history"]) > 10:
            session["history"] = session["history"][-10:]

    def clear(self, session_id):
        """
        手动清除某个会话。
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"[*] 已清除会话: {session_id}")

    def _cleanup(self):
        """
        自动清理过期的会话。
        """
        now = time.time()
        expired_ids = [
            sid for sid, data in self.sessions.items() 
            if now - data["last_activity"] > self.ttl
        ]
        for sid in expired_ids:
            del self.sessions[sid]
            logger.info(f"[*] 自动清理过期会话: {sid}")

# 单例模式
_memory_instance = MemoryStore()

def get_memory_store():
    return _memory_instance
