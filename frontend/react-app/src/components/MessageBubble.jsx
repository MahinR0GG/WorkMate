export default function MessageBubble({ role, content }) {
  return (
    <div className={`bubble-row ${role}`}>
      <div className="bubble">{content}</div>
    </div>
  );
}
