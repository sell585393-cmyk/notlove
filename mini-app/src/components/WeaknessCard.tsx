import { WEAKNESSES } from "../lib/constants";

interface WeaknessCardProps {
  weaknessId: string;
  held?: boolean; // true = держался, false = сорвался, undefined = нет данных
}

export function WeaknessCard({ weaknessId, held }: WeaknessCardProps) {
  const w = WEAKNESSES[weaknessId];
  if (!w) return null;

  let statusColor = "border-[var(--line)]";
  let statusText = "";

  if (held === true) {
    statusColor = "border-[var(--acid)]";
    statusText = "✅";
  } else if (held === false) {
    statusColor = "border-[var(--red)]";
    statusText = "❌";
  }

  return (
    <div
      className={`
        bg-[var(--panel)] border ${statusColor}
        p-3 flex items-center gap-3
      `}
    >
      <span className="text-lg">{w.emoji}</span>
      <div className="flex-1">
        <div className="text-[10px] text-[var(--ink)]">{w.label}</div>
        <div className="text-[8px] text-[var(--muted)]">{w.desc}</div>
      </div>
      {statusText && <span className="text-lg">{statusText}</span>}
    </div>
  );
}
