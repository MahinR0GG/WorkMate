const SAMPLES = [
  "How many leaves do I get per year?",
  "What is sabbatical leave?",
  "How do I submit a reimbursement claim?",
  "What is Leave Without Pay?",
  "What types of leave are available?",
  "Am I eligible for reimbursement?",
];

export default function SampleChips({ onSelect, disabled }) {
  return (
    <div className="chips-area">
      {SAMPLES.map((q) => (
        <button
          key={q}
          className="chip"
          onClick={() => onSelect(q)}
          disabled={disabled}
        >
          {q}
        </button>
      ))}
    </div>
  );
}
