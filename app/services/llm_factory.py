"""
LLM Factory - Returns the correct LangChain chat model based on LLM_PROVIDER config.

Current support:
  - "ollama"  →  ChatOllama  (llama3, runs locally)

Phase 2 (future):
  - "azure"   →  AzureChatOpenAI (primary) with ChatOllama as fallback
"""

from langchain_ollama import ChatOllama
from app.core.config import LLM_PROVIDER, OLLAMA_BASE_URL, OLLAMA_MODEL


def get_llm():
    """
    Factory function — returns the configured LangChain chat model.

    Swapping providers is a one-line .env change (LLM_PROVIDER=azure).
    No code changes needed anywhere else in the app.
    """
    if LLM_PROVIDER == "ollama":
        return ChatOllama(
            model=OLLAMA_MODEL,
            base_url=OLLAMA_BASE_URL,
            temperature=0.2,
        )

    # ── Phase 2 placeholder ─────────────────────────────────────────────────
    # if LLM_PROVIDER == "azure":
    #     from langchain_openai import AzureChatOpenAI
    #     from app.core.config import (
    #         AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY,
    #         AZURE_DEPLOYMENT_NAME, AZURE_API_VERSION,
    #     )
    #     azure = AzureChatOpenAI(
    #         azure_deployment=AZURE_DEPLOYMENT_NAME,
    #         azure_endpoint=AZURE_OPENAI_ENDPOINT,
    #         api_key=AZURE_OPENAI_API_KEY,
    #         api_version=AZURE_API_VERSION,
    #         temperature=0.2,
    #     )
    #     ollama_backup = ChatOllama(model=OLLAMA_MODEL, base_url=OLLAMA_BASE_URL, temperature=0.2)
    #     return azure.with_fallbacks([ollama_backup])
    # ───────────────────────────────────────────────────────────────────────

    raise ValueError(
        f"Unknown LLM_PROVIDER: '{LLM_PROVIDER}'. "
        "Set LLM_PROVIDER=ollama (or azure for Phase 2) in your .env file."
    )
