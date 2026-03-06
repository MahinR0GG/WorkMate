"""
LLM Factory - Returns the correct LangChain chat model based on LLM_PROVIDER config.

Providers:
  - "litellm"  →  ChatOpenAI pointed at LiteLLM proxy (azure/gpt-4o), Ollama as fallback
  - "ollama"   →  ChatOllama (llama3, runs locally)
"""

from langchain_ollama import ChatOllama
from app.core.config import (
    LLM_PROVIDER,
    LITELLM_BASE_URL, LITELLM_MODEL, LITELLM_API_KEY,
    OLLAMA_BASE_URL, OLLAMA_MODEL,
)


def _ollama_llm():
    return ChatOllama(
        model=OLLAMA_MODEL,
        base_url=OLLAMA_BASE_URL,
        temperature=0.2,
    )


def get_llm():
    """
    Factory function — returns the configured LangChain chat model.
    Swapping providers is a one-line .env change (LLM_PROVIDER=litellm|ollama).
    """
    if LLM_PROVIDER == "litellm":
        from langchain_openai import ChatOpenAI
        primary = ChatOpenAI(
            model=LITELLM_MODEL,
            base_url=LITELLM_BASE_URL,
            api_key=LITELLM_API_KEY,
            temperature=0.2,
        )
        fallback = _ollama_llm()
        return primary.with_fallbacks([fallback])

    if LLM_PROVIDER == "ollama":
        return _ollama_llm()

    raise ValueError(
        f"Unknown LLM_PROVIDER: '{LLM_PROVIDER}'. "
        "Set LLM_PROVIDER=litellm or LLM_PROVIDER=ollama in your .env file."
    )
