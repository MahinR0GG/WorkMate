"""
LLM Service - Handles RAG pipeline and Ollama API calls
Orchestrates embedding, search, and LLM response generation
"""

# from google import genai  # Commented out - using Ollama now
# from config import GEMINI_API_KEY
import ollama
from config import OLLAMA_BASE_URL, OLLAMA_MODEL
from services.embedding_service import get_embedding
from services.vector_service import search_similar_chunks

# Configure Ollama client
# client = genai.Client(api_key=GEMINI_API_KEY)  # Commented out - using Ollama now
# MODEL_NAME = "gemini-2.0-flash"  # Commented out - using Ollama now
ollama_client = ollama.Client(host=OLLAMA_BASE_URL)


def generate_answer(question: str) -> str:
    """
    Main RAG pipeline - generates answer using retrieved context
    
    Args:
        question: User's HR question
        
    Returns:
        Answer based on policy documents
    """
    try:
        # 1. Convert question to embedding
        query_embedding = get_embedding(question)

        # 2. Search similar chunks
        relevant_chunks = search_similar_chunks(query_embedding)

        # Handle no results
        if not relevant_chunks:
            return "I couldn't find relevant HR policy information for your question. Please contact HR for assistance."

        # 3. Build context from chunks
        context = "\n\n".join([
            f"Q: {chunk['question']}\nA: {chunk['answer']}"
            for chunk in relevant_chunks
        ])

        # 4. Create system prompt
        prompt = f"""You are a professional HR assistant.

Use ONLY the provided policy context to answer the employee's question.

POLICY CONTEXT:
{context}

EMPLOYEE QUESTION:
{question}

RESPONSE RULES:
- Answer clearly and concisely.
- Use bullet points if listing items.
- Do NOT include phrases like "Based on the provided context".
- Do NOT add assumptions or external knowledge.
- If the answer is not found in the context, say:
  "The requested information is not available in the current HR policy documents."
- Keep the tone professional and direct."""

        # 5. Call Ollama API
        response = call_llm(prompt)
        return response

    except Exception as e:
        return f"Error generating response: {str(e)}"


def call_llm(prompt: str) -> str:
    """
    Direct LLM call to Ollama
    
    Args:
        prompt: The complete prompt to send to Ollama
        
    Returns:
        Generated response text
    """
    try:
        # Ollama chat API call
        response = ollama_client.chat(
            model=OLLAMA_MODEL,
            messages=[
                {
                    'role': 'user',
                    'content': prompt
                }
            ]
        )
        return response['message']['content']
    except Exception as e:
        print(f"Error calling Ollama API: {str(e)}")
        raise
