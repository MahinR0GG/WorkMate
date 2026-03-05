import { useState, useEffect, useCallback } from "react";
import { sendMessage, checkHealth } from "./api";
import ChatWindow from "./components/ChatWindow";
import InputBar from "./components/InputBar";
import SampleChips from "./components/SampleChips";
import StatusPill from "./components/StatusPill";
import "./index.css";

function getOrCreateSession() {
  let id = sessionStorage.getItem("hr_session_id");
  if (!id) {
    id = crypto.randomUUID();
    sessionStorage.setItem("hr_session_id", id);
  }
  return id;
}

export default function App() {
  const [messages, setMessages]     = useState([]);
  const [isTyping, setIsTyping]     = useState(false);
  const [online, setOnline]         = useState(null);
  const [sessionId]                 = useState(getOrCreateSession);

  // Poll health on mount
  useEffect(() => {
    checkHealth().then(setOnline);
  }, []);

  const handleSend = useCallback(async (question) => {
    if (!question.trim()) return;

    // Add user message
    setMessages((prev) => [
      ...prev,
      { id: Date.now(), role: "user", content: question },
    ]);
    setIsTyping(true);

    try {
      const answer = await sendMessage(question, sessionId);
      setMessages((prev) => [
        ...prev,
        { id: Date.now() + 1, role: "bot", content: answer },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now() + 1,
          role: "bot",
          content: `⚠️ Error: ${err.message}. Make sure the API server is running.`,
        },
      ]);
    } finally {
      setIsTyping(false);
    }
  }, [sessionId]);

  const handleClear = () => {
    setMessages([]);
    const newId = crypto.randomUUID();
    sessionStorage.setItem("hr_session_id", newId);
    window.location.reload(); // simplest way to reset sessionId state
  };

  return (
    <>
      {/* Header */}
      <header className="header">
        <div className="header-brand">
          <div className="header-icon">🤖</div>
          <div>
            <div className="header-title">HR Bot</div>
            <div className="header-sub">Leave &amp; Reimbursement assistant</div>
          </div>
        </div>
        <div className="header-actions">
          {online !== null && <StatusPill online={online} />}
          <button className="clear-btn" onClick={handleClear}>Clear chat</button>
        </div>
      </header>

      {/* Messages */}
      <ChatWindow messages={messages} isTyping={isTyping} />

      {/* Sample chips */}
      <SampleChips onSelect={handleSend} disabled={isTyping} />

      {/* Input */}
      <InputBar onSend={handleSend} disabled={isTyping} />
    </>
  );
}
