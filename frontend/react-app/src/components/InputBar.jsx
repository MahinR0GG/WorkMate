import { useRef } from "react";

export default function InputBar({ onSend, disabled }) {
  const textareaRef = useRef(null);

  const handleSend = () => {
    const val = textareaRef.current?.value.trim();
    if (!val || disabled) return;
    onSend(val);
    textareaRef.current.value = "";
    textareaRef.current.style.height = "auto";
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleInput = (e) => {
    e.target.style.height = "auto";
    e.target.style.height = e.target.scrollHeight + "px";
  };

  return (
    <div className="input-bar">
      <textarea
        ref={textareaRef}
        rows={1}
        placeholder="Ask an HR question… (Enter to send)"
        onKeyDown={handleKeyDown}
        onInput={handleInput}
        disabled={disabled}
      />
      <button className="send-btn" onClick={handleSend} disabled={disabled} aria-label="Send">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
          <line x1="22" y1="2" x2="11" y2="13" />
          <polygon points="22 2 15 22 11 13 2 9 22 2" />
        </svg>
      </button>
    </div>
  );
}
