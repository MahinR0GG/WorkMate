"""
Guardrails Service — lightweight pre-RAG message classifier.

Classifies the user's message into one intents:
  - "greeting_simple"    → hi / hello / hey etc.
  - "greeting_time"      → good morning / afternoon / evening
  - "greeting_wellbeing" → how are you / how's it going
  - "greeting_identity"  → who are you / what can you do
  - "off_topic"          → non-HR subjects (weather, jokes, sports, etc.)
  - "hr_query"           → pass through to the full RAG pipeline

Uses keyword/regex matching only — no LLM call, zero added latency/cost.
"""

import re
from datetime import datetime

# ── Sub-patterns ──────────────────────────────────────────────────────────────

_SIMPLE_GREETING = re.compile(
    r"^\s*(hi+|hello+|hey+|hiya|howdy|yo+|sup|what'?s up|greetings|salut|namaste|helo|hii+)\s*[\?\!\.]*\s*$",
    re.IGNORECASE,
)

_TIME_GREETING = re.compile(
    r"^\s*good\s+(morning|afternoon|evening|day|night)\s*[\?\!\.]*\s*$",
    re.IGNORECASE,
)

_WELLBEING_GREETING = re.compile(
    r"^\s*("
    r"how are (you|u|ya)"
    r"|how'?s it going|how'?s everything|how do you do"
    r"|are you (ok|okay|good|fine|doing well)"
    r"|you good\??"
    r")\s*[\?\!\.]*\s*$",
    re.IGNORECASE,
)

_IDENTITY_GREETING = re.compile(
    r"^\s*("
    r"who are you|what are you|what is your (name|purpose|role)"
    r"|tell me about yourself|introduce yourself"
    r"|what can you (do|help with|assist with)"
    r"|what do you do|how can you help"
    r"|are you a bot|are you an ai|are you human"
    r"|nice to meet you|pleased to meet you"
    r")\s*[\?\!\.]*\s*$",
    re.IGNORECASE,
)

_OFF_TOPIC = re.compile(
    r"\b("
    r"weather|temperature|forecast|rain|sunny|climate"
    r"|joke|funny|laugh|meme|riddle|prank"
    r"|recipe|cook|bake|food|restaurant|cuisine"
    r"|stock|crypto|bitcoin|ethereum|invest|trading"
    r"|football|cricket|soccer|basketball|tennis|sports|ipl|fifa"
    r"|movie|series|netflix|film|actor|director"
    r"|song|music|artist|album|concert|spotify"
    r"|code|python|javascript|debug|programming|software"
    r"|news|politics|election|president|prime minister|government"
    r"|book|novel|author|manga|comic"
    r"|travel|vacation|holiday|hotel|flight|tourism"
    r"|game|gaming|playstation|xbox|pc gaming"
    r")\b",
    re.IGNORECASE,
)


def _time_of_day() -> str:
    hour = datetime.now().hour
    if 5 <= hour < 12:
        return "morning"
    if 12 <= hour < 17:
        return "afternoon"
    return "evening"


# ── Canned responses ──────────────────────────────────────────────────────────

def _greeting_simple_response() -> str:
    return (
        "Hello there! 👋 I'm your HR assistant.\n\n"
        "I can help you with questions about your company's **Leave** and **Reimbursement** policies. "
        "Feel free to ask anything!"
    )


def _greeting_time_response() -> str:
    tod = _time_of_day()
    return (
        f"Good {tod}! ☀️ I'm your HR assistant, ready to help.\n\n"
        "Got a question about **leave policies** or **reimbursements**? "
        "I'm here for it — go ahead and ask!"
    )


def _greeting_wellbeing_response() -> str:
    return (
        "I'm doing great, thanks for asking! 😊\n\n"
        "As your HR assistant, I'm always ready to help. "
        "Do you have any questions about your **leave entitlements** or **reimbursement claims**?"
    )


def _greeting_identity_response() -> str:
    return (
        "I'm **WorkMate HR Bot** 🤖 — your AI-powered HR policy assistant.\n\n"
        "Here's what I can help you with:\n"
        "- 📋 **Leave policies** — types of leave, entitlements, how to apply\n"
        "- 💰 **Reimbursement policies** — eligible expenses, how to claim, approval process\n\n"
        "Just ask your question and I'll pull the relevant policy information for you!"
    )


def _off_topic_response() -> str:
    return (
        "I appreciate the curiosity, but that's a bit outside my lane! 😄\n\n"
        "I'm specialised in your company's **HR policies** — specifically leave and reimbursements. "
        "Is there anything on that front I can help you with?"
    )


CANNED_RESPONSE_FN = {
    "greeting_simple":    _greeting_simple_response,
    "greeting_time":      _greeting_time_response,
    "greeting_wellbeing": _greeting_wellbeing_response,
    "greeting_identity":  _greeting_identity_response,
    "off_topic":          _off_topic_response,
}


def classify(question: str) -> str:
    """
    Classify the user message.

    Returns one of:
      'greeting_simple' | 'greeting_time' | 'greeting_wellbeing' |
      'greeting_identity' | 'off_topic' | 'hr_query'
    """
    q = question.strip()

    if _SIMPLE_GREETING.match(q):
        return "greeting_simple"

    if _TIME_GREETING.match(q):
        return "greeting_time"

    if _WELLBEING_GREETING.match(q):
        return "greeting_wellbeing"

    if _IDENTITY_GREETING.match(q):
        return "greeting_identity"

    if _OFF_TOPIC.search(q):
        return "off_topic"

    return "hr_query"


def get_canned_response(intent: str) -> str:
    """Return the canned response string for a non-hr_query intent."""
    return CANNED_RESPONSE_FN[intent]()
