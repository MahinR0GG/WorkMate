import ReactMarkdown from "react-markdown";

export default function MessageBubble({ role, content }) {
  if (role === "bot") {
    return (
      <div className="bubble-row bot">
        <div className="bubble bot-bubble">
          <ReactMarkdown>{content}</ReactMarkdown>
        </div>
      </div>
    );
  }

  return (
    <div className="bubble-row user">
      <div className="bubble">{content}</div>
    </div>
  );
}
