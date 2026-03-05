"""
STM Service Unit Tests

Tests:
  1. add_message / get_trimmed_memory basics
  2. Token-aware trimming — ensures output never exceeds MAX_STM_TOKENS
  3. clear_session — wipes messages for a session
  4. Session isolation — sessions don't bleed into each other

Run from project root:
    python scripts/test_stm.py
"""

import sys
import os
import importlib.util
import types as _types

# Read MAX_STM_TOKENS directly from env
MAX_STM_TOKENS = int(os.getenv("MAX_STM_TOKENS", "1000"))

# ── Minimal mock so stm_service.py can import app.core.config cleanly ─────────
_mock_cfg = _types.ModuleType("app.core.config")
_mock_cfg.MAX_STM_TOKENS = MAX_STM_TOKENS

_mock_app      = _types.ModuleType("app")
_mock_core     = _types.ModuleType("app.core")
_mock_services = _types.ModuleType("app.services")

sys.modules["app"]              = _mock_app
sys.modules["app.core"]         = _mock_core
sys.modules["app.core.config"]  = _mock_cfg
sys.modules["app.services"]     = _mock_services

# ── Load stm_service directly from file (avoids full package import chain) ────
_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
_spec = importlib.util.spec_from_file_location(
    "app.services.stm_service",
    os.path.join(_root, "app", "services", "stm_service.py"),
)
_mod = importlib.util.module_from_spec(_spec)
sys.modules["app.services.stm_service"] = _mod
_spec.loader.exec_module(_mod)

add_message           = _mod.add_message
get_trimmed_memory    = _mod.get_trimmed_memory
clear_session         = _mod.clear_session
get_session_token_count = _mod.get_session_token_count
_count_tokens         = _mod._count_tokens

from langchain_core.messages import HumanMessage, AIMessage

PASS = "[PASS]"
FAIL = "[FAIL]"

errors = 0


def check(label: str, condition: bool):
    global errors
    status = PASS if condition else FAIL
    print(f"  {status}  {label}")
    if not condition:
        errors += 1


print("=" * 60)
print("  HR Bot — STM Service Tests")
print(f"  MAX_STM_TOKENS = {MAX_STM_TOKENS}")
print("=" * 60)

# ── Test 1: Basic add + retrieve ───────────────────────────────────────────────
print("\n[1] Basic add_message / get_trimmed_memory")
sid = "test-session-basic"
add_message(sid, HumanMessage(content="Hello"))
add_message(sid, AIMessage(content="Hi there! How can I help?"))
msgs = get_trimmed_memory(sid)
check("Returns 2 messages after 2 adds", len(msgs) == 2)
check("First message is HumanMessage", isinstance(msgs[0], HumanMessage))
check("Second message is AIMessage", isinstance(msgs[1], AIMessage))
clear_session(sid)

# ── Test 2: Token-aware trimming ───────────────────────────────────────────────
print("\n[2] Token-aware trimming")
sid = "test-session-trim"

# Add many large messages to exceed the token budget
long_text = "This is a fairly long message designed to consume tokens. " * 20
for i in range(25):
    add_message(sid, HumanMessage(content=f"[Q{i}] {long_text}"))
    add_message(sid, AIMessage(content=f"[A{i}] {long_text}"))

raw_tokens = get_session_token_count(sid)
trimmed = get_trimmed_memory(sid)
trimmed_tokens = _count_tokens(trimmed)

print(f"  Raw token count  : {raw_tokens}")
print(f"  Trimmed tokens   : {trimmed_tokens}")
print(f"  Messages kept    : {len(trimmed)} / 50")

check("Trimmed token count is within MAX_STM_TOKENS", trimmed_tokens <= MAX_STM_TOKENS)
check("Trimming removed at least some messages", len(trimmed) < 50)
check("Oldest messages dropped (last message still present)",
      trimmed[-1].content.startswith("[A24]"))
clear_session(sid)

# ── Test 3: clear_session ─────────────────────────────────────────────────────
print("\n[3] clear_session")
sid = "test-session-clear"
add_message(sid, HumanMessage(content="To be cleared"))
clear_session(sid)
msgs = get_trimmed_memory(sid)
check("Returns empty list after clear_session", len(msgs) == 0)
check("Token count is 0 after clear", get_session_token_count(sid) == 0)

# ── Test 4: Session isolation ─────────────────────────────────────────────────
print("\n[4] Session isolation")
sid_a = "test-session-A"
sid_b = "test-session-B"
add_message(sid_a, HumanMessage(content="Message for session A"))
add_message(sid_b, HumanMessage(content="Message for session B"))
msgs_a = get_trimmed_memory(sid_a)
msgs_b = get_trimmed_memory(sid_b)
check("Session A has 1 message", len(msgs_a) == 1)
check("Session B has 1 message", len(msgs_b) == 1)
check("Session A content is correct", "session A" in msgs_a[0].content)
check("Session B content is correct", "session B" in msgs_b[0].content)
clear_session(sid_a)
check("Clearing A does not affect B", len(get_trimmed_memory(sid_b)) == 1)
clear_session(sid_b)

# ── Test 5: Empty session ─────────────────────────────────────────────────────
print("\n[5] Empty session behaviour")
msgs = get_trimmed_memory("non-existent-session")
check("Returns empty list for unknown session_id", msgs == [])

# ── Results ───────────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
if errors == 0:
    print("  ALL TESTS PASSED ✅")
else:
    print(f"  {errors} TEST(S) FAILED ❌")
print("=" * 60)

sys.exit(errors)
