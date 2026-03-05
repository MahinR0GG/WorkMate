export default function StatusPill({ online }) {
  return (
    <div className={`status-pill ${online ? "online" : "offline"}`}>
      <span className="dot" />
      {online ? "API Online" : "API Offline"}
    </div>
  );
}
