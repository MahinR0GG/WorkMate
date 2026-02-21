"""
Memory Service - Manages conversation history per session
TODO: Implement LangChain memory integration
      - ConversationBufferWindowMemory (recommended for HR Bot)
      - Keyed by session_id from request header
"""

# from langchain.memory import ConversationBufferWindowMemory
# session_memory_store: dict[str, ConversationBufferWindowMemory] = {}

# def get_memory(session_id: str) -> ConversationBufferWindowMemory:
#     if session_id not in session_memory_store:
#         session_memory_store[session_id] = ConversationBufferWindowMemory(k=5)
#     return session_memory_store[session_id]

# def clear_memory(session_id: str):
#     if session_id in session_memory_store:
#         del session_memory_store[session_id]
