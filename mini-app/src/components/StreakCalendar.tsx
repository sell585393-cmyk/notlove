import type { Checkin } from "../lib/supabase";

interface StreakCalendarProps {
  checkins: Checkin[];
  currentDay: number;
}

/**
 * Календарь 30 дней — показывает статус каждого дня.
 */
export function StreakCalendar({ checkins, currentDay }: StreakCalendarProps) {
  const dayStatus = new Map<number, boolean>();
  for (const ci of checkins) {
    dayStatus.set(ci.day, ci.passed);
  }

  return (
    <div className="p-4">
      <div
        className="grid gap-1"
        style={{ gridTemplateColumns: "repeat(10, 1fr)" }}
      >
        {Array.from({ length: 30 }, (_, i) => {
          const day = i + 1;
          const status = dayStatus.get(day);
          const isCurrent = day === currentDay;
          const isFuture = day > currentDay;

          let bg = "bg-[var(--panel)]"; // будущее
          let border = "border-[var(--line)]";
          let text = "text-[var(--muted)]";

          if (status === true) {
            bg = "bg-[var(--acid)]/20";
            border = "border-[var(--acid)]";
            text = "text-[var(--acid)]";
          } else if (status === false) {
            bg = "bg-[var(--red)]/20";
            border = "border-[var(--red)]";
            text = "text-[var(--red)]";
          } else if (isCurrent) {
            bg = "bg-[var(--panel)]";
            border = "border-[var(--acid)]";
            text = "text-[var(--ink)]";
          }

          return (
            <div
              key={day}
              className={`
                ${bg} ${text}
                border ${border}
                flex items-center justify-center
                aspect-square text-[8px]
                ${isCurrent ? "pulse-acid" : ""}
                ${isFuture ? "opacity-30" : ""}
              `}
            >
              {day}
            </div>
          );
        })}
      </div>
    </div>
  );
}
