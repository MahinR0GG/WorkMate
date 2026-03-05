import { useEffect, useRef } from "react";
import MessageBubble from "./MessageBubble";
import TypingIndicator from "./TypingIndicator";

export default function ChatWindow({ messages, isTyping }) {
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isTyping]);

  const isEmpty = messages.length === 0 && !isTyping;

  return (
    <div className="chat-window">
      {isEmpty ? (
        <div className="empty-state">
          <div className="emoji">🤖</div>
          <h2>Ask me anything about HR</h2>
          <p>Leave policies, reimbursements, and more.</p>
        </div>
      ) : (
        <>
          {messages.map((msg) => (
            <MessageBubble key={msg.id} role={msg.role} content={msg.content} />
          ))}
          {isTyping && <TypingIndicator />}
        </>
      )}
      <div ref={bottomRef} />
    </div>
  );
}
