import { useEffect, useState } from "react";
import { PixelAvatar } from "../components/PixelAvatar";
import { StreakCalendar } from "../components/StreakCalendar";
import { WeaknessCard } from "../components/WeaknessCard";
import { ARCHETYPES } from "../lib/constants";
import {
  getUser,
  getActiveChallenge,
  getCheckins,
  getUserWeaknesses,
  type User,
  type Challenge,
  type Checkin,
} from "../lib/supabase";
import { getTelegramUser, haptic } from "../lib/telegram";

export function HomePage() {
  const [user, setUser] = useState<User | null>(null);
  const [challenge, setChallenge] = useState<Challenge | null>(null);
  const [checkins, setCheckins] = useState<Checkin[]>([]);
  const [weaknesses, setWeaknesses] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      const tgUser = getTelegramUser();
      if (!tgUser) {
        setLoading(false);
        return;
      }

      const [u, ch, ws] = await Promise.all([
        getUser(tgUser.id),
        getActiveChallenge(tgUser.id),
        getUserWeaknesses(tgUser.id),
      ]);

      setUser(u);
      setChallenge(ch);
      setWeaknesses(ws);

      if (ch) {
        const ci = await getCheckins(ch.id);
        setCheckins(ci);
      }

      setLoading(false);
    }
    load();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-[var(--acid)] text-xs animate-pulse">
          ЗАГРУЗКА...
        </div>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="flex flex-col items-center justify-center h-screen p-6 text-center">
        <div className="text-[var(--acid)] text-sm mb-4">NOTLOVE</div>
        <div className="text-[var(--muted)] text-[9px] leading-relaxed">
          Начни через бота.
          <br />
          Напиши /start — и зеркало откроется.
        </div>
      </div>
    );
  }

  const archetype = ARCHETYPES[user.archetype ?? "slug"];

  return (
    <div className="min-h-screen pb-20">
      {/* Header */}
      <header className="p-4 border-b border-[var(--line)] flex items-center justify-between">
        <div>
          <div className="text-[var(--acid)] text-xs">NOTLOVE</div>
          <div className="text-[var(--muted)] text-[8px] mt-1">
            {archetype?.label ?? "—"}
          </div>
        </div>
        {challenge && (
          <div className="text-right">
            <div className="text-[var(--ink)] text-xs">
              День {challenge.day}
            </div>
            <div className="text-[var(--muted)] text-[8px] mt-1">
              Стрик: {challenge.streak}
            </div>
          </div>
        )}
      </header>

      {/* Avatar */}
      <section className="py-6">
        <PixelAvatar
          avatarUrl={user.avatar_url}
          archetype={user.archetype ?? "slug"}
          streak={challenge?.streak ?? 0}
          size={200}
        />
      </section>

      {/* Progress bar */}
      {challenge && (
        <section className="px-4 pb-4">
          <div className="progress-bar">
            <div
              className="progress-bar-fill"
              style={{ width: `${(challenge.day / 30) * 100}%` }}
            />
          </div>
          <div className="flex justify-between text-[8px] text-[var(--muted)] mt-1">
            <span>День 1</span>
            <span>День 30</span>
          </div>
        </section>
      )}

      {/* Stats */}
      {challenge && (
        <section className="px-4 pb-4 grid grid-cols-3 gap-2">
          <StatBox
            label="Стрик"
            value={challenge.streak.toString()}
            accent
          />
          <StatBox
            label="Чек-инов"
            value={challenge.total_checkins.toString()}
          />
          <StatBox
            label="Срывов"
            value={challenge.total_fails.toString()}
            danger={challenge.total_fails > 0}
          />
        </section>
      )}

      {/* Weaknesses */}
      <section className="px-4 pb-4 space-y-2">
        <div className="text-[9px] text-[var(--muted)] mb-2">СЛАБОСТИ</div>
        {weaknesses.map((wid) => {
          const todayCheckin = checkins.find((ci) => ci.day === challenge?.day);
          const held = todayCheckin?.weaknesses_held?.includes(wid);
          return <WeaknessCard key={wid} weaknessId={wid} held={held} />;
        })}
      </section>

      {/* Calendar */}
      {challenge && (
        <section className="px-4 pb-4">
          <div className="text-[9px] text-[var(--muted)] mb-2 px-4">
            КАЛЕНДАРЬ
          </div>
          <div className="bg-[var(--panel)] border border-[var(--line)]">
            <StreakCalendar
              checkins={checkins}
              currentDay={challenge.day}
            />
          </div>
        </section>
      )}
    </div>
  );
}

function StatBox({
  label,
  value,
  accent,
  danger,
}: {
  label: string;
  value: string;
  accent?: boolean;
  danger?: boolean;
}) {
  const valueColor = danger
    ? "text-[var(--red)]"
    : accent
      ? "text-[var(--acid)]"
      : "text-[var(--ink)]";

  return (
    <div className="bg-[var(--panel)] border border-[var(--line)] p-3 text-center">
      <div className={`text-sm ${valueColor}`}>{value}</div>
      <div className="text-[8px] text-[var(--muted)] mt-1">{label}</div>
    </div>
  );
}
