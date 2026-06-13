import { useState, useEffect, useRef } from "react";

/* ─── pixel font via Google Fonts ─── */
const PIXEL_FONT_URL =
  "https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap";

/* ─── colors ─── */
const C = {
  bg: "#050608",
  panel: "#191c22",
  line: "#4d584e",
  ink: "#eef1e8",
  muted: "#8b978f",
  acid: "#b9f22a",
  red: "#e64036",
  amber: "#e8a72f",
  cyan: "#41d1da",
  green0: "#0b2619",
  green1: "#1f5028",
};

/* ─── weakness data ─── */
const WEAKNESSES = [
  { id: "sleep", label: "СОН", desc: "ложишься когда придётся, встаёшь никакой", color: C.cyan, icon: "🌙" },
  { id: "feed", label: "ЛЕНТА", desc: "часы уходят в чужие жизни", color: C.acid, icon: "📱" },
  { id: "porn", label: "18+", desc: "каждый вечер одно и то же", color: C.red, icon: "🔞" },
  { id: "food", label: "ЕДА", desc: "топливо из помойки", color: C.amber, icon: "🍔" },
  { id: "gym", label: "ТЕЛО", desc: "ни разу не встал ради себя", color: C.red, icon: "🏋️" },
  { id: "money", label: "ДЕНЬГИ", desc: "тратишь на мусор, копишь на ничего", color: C.amber, icon: "💸" },
];

/* ─── CRT scanline overlay ─── */
function Scanlines() {
  return (
    <div
      className="pointer-events-none fixed inset-0 z-50"
      style={{
        background:
          "repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(0,0,0,0.15) 2px, rgba(0,0,0,0.15) 4px)",
        mixBlendMode: "multiply",
      }}
    />
  );
}

/* ─── glitch text ─── */
function GlitchText({
  children,
  className = "",
}: {
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <span className={`relative inline-block ${className}`}>
      <span className="glitch-layer glitch-r" aria-hidden="true">
        {children}
      </span>
      <span className="glitch-layer glitch-g" aria-hidden="true">
        {children}
      </span>
      {children}
    </span>
  );
}

/* ─── pixel card ─── */
function PixelCard({
  children,
  borderColor = C.line,
  className = "",
}: {
  children: React.ReactNode;
  borderColor?: string;
  className?: string;
}) {
  return (
    <div
      className={`relative ${className}`}
      style={{
        background: C.panel,
        border: `2px solid ${borderColor}`,
        boxShadow: `4px 4px 0px ${C.bg}, 2px 2px 0px rgba(0,0,0,0.5)`,
      }}
    >
      {children}
    </div>
  );
}

/* ─── weakness chip ─── */
function WeaknessChip({
  w,
  selected,
  onToggle,
}: {
  w: (typeof WEAKNESSES)[0];
  selected: boolean;
  onToggle: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onToggle}
      className="text-left transition-all duration-200 active:scale-95"
      style={{
        background: selected ? `${w.color}15` : C.panel,
        border: `2px solid ${selected ? w.color : C.line}`,
        boxShadow: selected ? `0 0 20px ${w.color}30, 4px 4px 0px ${C.bg}` : `4px 4px 0px ${C.bg}`,
        padding: "14px 16px",
      }}
    >
      <div className="flex items-center gap-3">
        <span className="text-2xl">{w.icon}</span>
        <div>
          <div
            className="font-bold tracking-wider"
            style={{ color: selected ? w.color : C.ink, fontFamily: "'Press Start 2P', monospace", fontSize: "10px" }}
          >
            {w.label}
          </div>
          <div className="text-xs mt-1" style={{ color: C.muted }}>
            {w.desc}
          </div>
        </div>
        {selected && (
          <div
            className="ml-auto w-3 h-3 rounded-sm"
            style={{ background: w.color, boxShadow: `0 0 8px ${w.color}` }}
          />
        )}
      </div>
    </button>
  );
}

/* ─── step indicator ─── */
function StepBadge({
  num,
  label,
  color,
}: {
  num: string;
  label: string;
  color: string;
}) {
  return (
    <div className="flex flex-col items-center gap-2">
      <div
        className="w-10 h-10 flex items-center justify-center font-bold"
        style={{
          background: `${color}20`,
          border: `2px solid ${color}`,
          color,
          fontFamily: "'Press Start 2P', monospace",
          fontSize: "12px",
        }}
      >
        {num}
      </div>
      <span className="text-xs text-center" style={{ color: C.muted, maxWidth: 80 }}>
        {label}
      </span>
    </div>
  );
}

/* ─── animated counter ─── */
function AnimatedNumber({ target }: { target: number }) {
  const [count, setCount] = useState(0);
  const ref = useRef<HTMLSpanElement>(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          let start = 0;
          const step = Math.ceil(target / 40);
          const interval = setInterval(() => {
            start += step;
            if (start >= target) {
              setCount(target);
              clearInterval(interval);
            } else {
              setCount(start);
            }
          }, 30);
          observer.disconnect();
        }
      },
      { threshold: 0.5 }
    );
    if (ref.current) observer.observe(ref.current);
    return () => observer.disconnect();
  }, [target]);

  return <span ref={ref}>{count.toLocaleString("ru-RU")}</span>;
}

/* ═══════════════════════════════════════════════════════════════════
   MAIN LANDING PAGE
   ═══════════════════════════════════════════════════════════════════ */
export function PublicLandingPage() {
  const [selectedWeaknesses, setSelectedWeaknesses] = useState<Set<string>>(
    new Set()
  );
  const [email, setEmail] = useState("");
  const [telegram, setTelegram] = useState("");
  const [submitted, setSubmitted] = useState(false);

  useEffect(() => {
    const link = document.createElement("link");
    link.rel = "stylesheet";
    link.href = PIXEL_FONT_URL;
    document.head.appendChild(link);
  }, []);

  const toggleWeakness = (id: string) => {
    setSelectedWeaknesses((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitted(true);
  };

  return (
    <div className="min-h-screen" style={{ background: C.bg, color: C.ink }}>
      <Scanlines />

      {/* ─── NAV ─── */}
      <nav className="fixed top-0 left-0 right-0 z-40 px-4 py-3 flex items-center justify-between" style={{ background: `${C.bg}e0`, backdropFilter: "blur(8px)", borderBottom: `1px solid ${C.line}30` }}>
        <div style={{ fontFamily: "'Press Start 2P', monospace", fontSize: "14px" }}>
          <span style={{ color: C.ink }}>NOTLOVE</span>
          <span style={{ color: C.acid }}>.</span>
          <span style={{ color: C.acid }}>ME</span>
        </div>
        <div className="hidden sm:flex gap-6 text-xs" style={{ color: C.muted }}>
          <a href="#mirror" className="hover:opacity-80 transition-opacity">проверка</a>
          <a href="#path" className="hover:opacity-80 transition-opacity">30 дней</a>
          <a href="#join" className="hover:opacity-80 transition-opacity">заявка</a>
        </div>
      </nav>

      {/* ═══ SECTION 1: HERO ═══ */}
      <section className="relative min-h-screen flex items-center justify-center overflow-hidden pt-16">
        {/* Background glow */}
        <div
          className="absolute inset-0"
          style={{
            background: `radial-gradient(ellipse 60% 50% at 50% 60%, ${C.green1}30, transparent)`,
          }}
        />

        <div className="relative z-10 max-w-6xl mx-auto px-4 py-12 grid grid-cols-1 lg:grid-cols-2 gap-8 items-center">
          {/* Left: copy */}
          <div>
            <div
              className="inline-block px-3 py-1.5 mb-6 text-xs tracking-widest"
              style={{
                border: `1px solid ${C.acid}`,
                color: C.acid,
                background: `${C.green0}80`,
                fontFamily: "'Press Start 2P', monospace",
                fontSize: "8px",
              }}
            >
              ДЛЯ ТЕХ, КТО СЕБЯ НЕ ЛЮБИТ
            </div>

            <h1 className="leading-tight mb-6">
              <span
                className="block text-3xl sm:text-4xl md:text-5xl font-black tracking-tight"
                style={{ color: C.ink }}
              >
                ТЫ НЕ СЕБЯ
              </span>
              <span
                className="block text-3xl sm:text-4xl md:text-5xl font-black tracking-tight"
                style={{ color: C.ink }}
              >
                НЕНАВИДИШЬ.
              </span>
              <span className="block h-2" />
              <GlitchText>
                <span
                  className="block text-3xl sm:text-4xl md:text-5xl font-black tracking-tight"
                  style={{ color: C.acid }}
                >
                  ТЫ НЕНАВИДИШЬ
                </span>
              </GlitchText>
              <span
                className="block text-3xl sm:text-4xl md:text-5xl font-black tracking-tight"
                style={{ color: C.ink }}
              >
                ТОГО, КЕМ СТАЛ.
              </span>
            </h1>

            <p className="text-base sm:text-lg mb-2" style={{ color: C.muted, maxWidth: 440 }}>
              Фото покажет, кого ты кормишь лентой, взрослыми сайтами и мусорной едой.
            </p>
            <p className="text-base sm:text-lg font-semibold mb-8" style={{ color: C.ink }}>
              30 дней — перестать быть им.
            </p>

            <div className="flex flex-col sm:flex-row gap-3">
              <a
                href="#mirror"
                className="inline-flex items-center justify-center px-6 py-3 font-bold text-sm tracking-wide transition-all hover:brightness-110 active:scale-95"
                style={{
                  background: C.acid,
                  color: C.bg,
                  boxShadow: `4px 4px 0px ${C.bg}, 0 0 30px ${C.acid}40`,
                }}
              >
                ПОСМОТРИ НА СЕБЯ
              </a>
              <a
                href="#join"
                className="inline-flex items-center justify-center px-6 py-3 font-bold text-sm tracking-wide transition-all hover:brightness-110 active:scale-95"
                style={{
                  background: C.panel,
                  color: C.ink,
                  border: `2px solid ${C.line}`,
                  boxShadow: `4px 4px 0px ${C.bg}`,
                }}
              >
                НАЧАТЬ 30 ДНЕЙ
              </a>
            </div>
          </div>

          {/* Right: hero video from Supabase */}
          <div className="flex justify-center lg:justify-end">
            <div className="relative hero-image-wrap">
              <div
                className="absolute -inset-4 rounded-sm hero-glow"
                style={{
                  background: `radial-gradient(ellipse at center, ${C.acid}15, transparent 70%)`,
                }}
              />
              <video
                autoPlay
                loop
                muted
                playsInline
                poster="https://wfkplqgufdaxnczvyhpn.supabase.co/storage/v1/object/public/assets/dark-mirror.webp"
                className="relative w-full max-w-[360px] sm:max-w-[420px]"
                style={{
                  border: `2px solid ${C.line}`,
                  boxShadow: `8px 8px 0px ${C.bg}, 0 0 60px ${C.green1}40`,
                }}
              >
                <source src="https://wfkplqgufdaxnczvyhpn.supabase.co/storage/v1/object/public/assets/hero-video.mp4" type="video/mp4" />
                <img
                  src="https://wfkplqgufdaxnczvyhpn.supabase.co/storage/v1/object/public/assets/dark-mirror.webp"
                  alt="Тёмное зеркало"
                  className="w-full"
                />
              </video>
            </div>
          </div>
        </div>

        {/* Scroll indicator */}
        <div className="absolute bottom-6 left-1/2 -translate-x-1/2 animate-bounce">
          <div className="w-5 h-8 border-2 rounded-full flex justify-center pt-1" style={{ borderColor: C.line }}>
            <div className="w-1 h-2 rounded-full" style={{ background: C.acid }} />
          </div>
        </div>
      </section>

      {/* ═══ SECTION 2: ТЁМНОЕ ЗЕРКАЛО ═══ */}
      <section id="mirror" className="relative py-20 sm:py-28 overflow-hidden">
        <div
          className="absolute inset-0"
          style={{
            background: `linear-gradient(180deg, ${C.bg} 0%, ${C.green0}40 50%, ${C.bg} 100%)`,
          }}
        />

        <div className="relative z-10 max-w-5xl mx-auto px-4">
          <div className="text-center mb-12">
            <div
              className="inline-block px-3 py-1 mb-4 text-xs"
              style={{
                color: C.cyan,
                border: `1px solid ${C.cyan}40`,
                background: `${C.cyan}10`,
                fontFamily: "'Press Start 2P', monospace",
                fontSize: "8px",
              }}
            >
              ТЁМНОЕ ЗЕРКАЛО
            </div>
            <h2 className="text-2xl sm:text-3xl font-black mb-4">
              Одно фото.{" "}
              <span style={{ color: C.acid }}>Вся правда.</span>
            </h2>
            <p style={{ color: C.muted }} className="max-w-lg mx-auto">
              Ты и так знаешь, что что-то не так. Мы просто покажем — что именно.
              Без жалости. Без мотивашек. Как есть.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 items-center">
            {/* Phone scan image */}
            <div className="flex justify-center">
              <img
                src="https://wfkplqgufdaxnczvyhpn.supabase.co/storage/v1/object/public/assets/phone-scan.webp"
                alt="Проверка"
                className="w-full max-w-[300px]"
                style={{
                  border: `2px solid ${C.cyan}40`,
                  boxShadow: `0 0 40px ${C.cyan}15`,
                }}
              />
            </div>

            {/* Steps */}
            <div className="space-y-4">
              {[
                { n: "01", title: "СДЕЛАЙ ФОТО", desc: "Обычное лицо. Без фильтров, без подготовки. Таким, какой ты есть.", color: C.cyan },
                { n: "02", title: "ПОЛУЧИ РАЗБОР", desc: "Алгоритм считает всё: недосып, стресс, лень. То, что ты прячешь от зеркала.", color: C.acid },
                { n: "03", title: "ВСТРЕТЬ ДВОЙНИКА", desc: "Пиксельный персонаж — слепок тебя настоящего. Каждая слабость на виду.", color: C.amber },
                { n: "04", title: "ПРОЖИВИ 30 ДНЕЙ", desc: "Каждый день — одно задание. Двойник меняется. Ты — тоже.", color: C.red },
              ].map((step) => (
                <PixelCard key={step.n} borderColor={`${step.color}60`} className="p-4">
                  <div className="flex items-start gap-3">
                    <div
                      className="flex-shrink-0 w-8 h-8 flex items-center justify-center font-bold"
                      style={{
                        color: step.color,
                        border: `1px solid ${step.color}`,
                        fontFamily: "'Press Start 2P', monospace",
                        fontSize: "10px",
                      }}
                    >
                      {step.n}
                    </div>
                    <div>
                      <div
                        className="font-bold text-xs mb-1"
                        style={{ color: step.color, fontFamily: "'Press Start 2P', monospace", fontSize: "9px" }}
                      >
                        {step.title}
                      </div>
                      <div className="text-sm" style={{ color: C.muted }}>
                        {step.desc}
                      </div>
                    </div>
                  </div>
                </PixelCard>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* ═══ SECTION 3: СЛАБОСТИ ═══ */}
      <section className="relative py-20 sm:py-28">
        <div className="max-w-4xl mx-auto px-4">
          <div className="text-center mb-10">
            <h2 className="text-2xl sm:text-3xl font-black mb-3">
              <span style={{ color: C.red }}>ЧЕСТНО</span> — С САМИМ СОБОЙ
            </h2>
            <p style={{ color: C.muted }}>
              Отметь то, что тебя разъедает. Никто не увидит. Это только между тобой и экраном.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-8">
            {WEAKNESSES.map((w) => (
              <WeaknessChip
                key={w.id}
                w={w}
                selected={selectedWeaknesses.has(w.id)}
                onToggle={() => toggleWeakness(w.id)}
              />
            ))}
          </div>

          {selectedWeaknesses.size > 0 && (
            <div
              className="text-center p-4 transition-all duration-500"
              style={{
                border: `1px solid ${C.acid}40`,
                background: `${C.acid}08`,
              }}
            >
              <p style={{ color: C.acid }} className="text-sm font-bold mb-1">
                {selectedWeaknesses.size} из 6 — уже честнее, чем вчера
              </p>
              <p style={{ color: C.muted }} className="text-xs">
                Большинство отмечают 3–4. Ты не единственный.
              </p>
            </div>
          )}
        </div>
      </section>

      {/* ═══ SECTION 4: ДО / ПОСЛЕ ═══ */}
      <section id="path" className="relative py-20 sm:py-28 overflow-hidden">
        <div
          className="absolute inset-0"
          style={{
            background: `linear-gradient(180deg, ${C.bg} 0%, ${C.panel} 50%, ${C.bg} 100%)`,
          }}
        />

        <div className="relative z-10 max-w-5xl mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-2xl sm:text-3xl font-black mb-3">
              30 ДНЕЙ.{" "}
              <span style={{ color: C.acid }}>ДВА РАЗНЫХ ЧЕЛОВЕКА.</span>
            </h2>
            <p style={{ color: C.muted }} className="max-w-md mx-auto">
              Слева — тот, кем ты стал. Справа — тот, кем ты можешь быть через месяц.
              Не обещание. Разница.
            </p>
          </div>

          <div className="flex justify-center mb-10">
            <img
              src="https://wfkplqgufdaxnczvyhpn.supabase.co/storage/v1/object/public/assets/before-after.webp"
              alt="До и после"
              className="w-full max-w-[500px]"
              style={{
                border: `2px solid ${C.red}40`,
                boxShadow: `0 0 60px ${C.red}15, 0 0 60px ${C.acid}10`,
              }}
            />
          </div>

          {/* Path steps */}
          <div className="flex justify-center gap-6 sm:gap-10">
            <StepBadge num="1" label="сделай фото" color={C.cyan} />
            <div className="flex items-center" style={{ color: C.line }}>→</div>
            <StepBadge num="2" label="узнай правду" color={C.acid} />
            <div className="flex items-center" style={{ color: C.line }}>→</div>
            <StepBadge num="3" label="проживи 30 дней" color={C.red} />
          </div>
        </div>
      </section>

      {/* ═══ SECTION 5: ЦИФРЫ ═══ */}
      <section className="py-16 sm:py-20">
        <div className="max-w-4xl mx-auto px-4">
          <div className="grid grid-cols-3 gap-4 text-center">
            {[
              { n: 1247, label: "уже ждут запуска", color: C.acid },
              { n: 30, label: "дней на перемену", color: C.cyan },
              { n: 6, label: "слабостей под прицелом", color: C.red },
            ].map((stat) => (
              <PixelCard key={stat.label} className="p-4 sm:p-6">
                <div
                  className="text-2xl sm:text-3xl font-black mb-1"
                  style={{ color: stat.color, fontFamily: "'Press Start 2P', monospace", fontSize: "20px" }}
                >
                  <AnimatedNumber target={stat.n} />
                </div>
                <div className="text-xs" style={{ color: C.muted }}>
                  {stat.label}
                </div>
              </PixelCard>
            ))}
          </div>
        </div>
      </section>

      {/* ═══ SECTION 6: ЗАЯВКА ═══ */}
      <section id="join" className="relative py-20 sm:py-28 overflow-hidden">
        <div
          className="absolute inset-0"
          style={{
            background: `radial-gradient(ellipse 80% 60% at 50% 50%, ${C.acid}08, transparent)`,
          }}
        />

        <div className="relative z-10 max-w-lg mx-auto px-4">
          <div className="text-center mb-8">
            <h2 className="text-2xl sm:text-3xl font-black mb-3">
              ХВАТИТ <span style={{ color: C.red }}>ТЯНУТЬ</span>
            </h2>
            <p style={{ color: C.muted }}>
              Оставь заявку. Первая волна получит доступ бесплатно.
            </p>
          </div>

          {!submitted ? (
            <PixelCard borderColor={C.acid} className="p-6">
              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="block text-xs mb-1.5 font-semibold" style={{ color: C.muted }}>
                    ТЕЛЕГРАМ
                  </label>
                  <input
                    type="text"
                    placeholder="@username"
                    value={telegram}
                    onChange={(e) => setTelegram(e.target.value)}
                    className="w-full px-3 py-2.5 text-sm outline-none transition-colors"
                    style={{
                      background: C.bg,
                      border: `2px solid ${C.line}`,
                      color: C.ink,
                    }}
                    onFocus={(e) => (e.target.style.borderColor = C.acid)}
                    onBlur={(e) => (e.target.style.borderColor = C.line)}
                  />
                </div>

                <div>
                  <label className="block text-xs mb-1.5 font-semibold" style={{ color: C.muted }}>
                    ПОЧТА <span style={{ color: C.line }}>(по желанию)</span>
                  </label>
                  <input
                    type="email"
                    placeholder="mail@example.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full px-3 py-2.5 text-sm outline-none"
                    style={{
                      background: C.bg,
                      border: `2px solid ${C.line}`,
                      color: C.ink,
                    }}
                    onFocus={(e) => (e.target.style.borderColor = C.acid)}
                    onBlur={(e) => (e.target.style.borderColor = C.line)}
                  />
                </div>

                <button
                  type="submit"
                  className="w-full py-3 font-bold text-sm tracking-wider transition-all hover:brightness-110 active:scale-[0.98]"
                  style={{
                    background: C.acid,
                    color: C.bg,
                    boxShadow: `4px 4px 0px ${C.bg}, 0 0 30px ${C.acid}30`,
                  }}
                >
                  ЗАПИСАТЬСЯ
                </button>

                <p className="text-xs text-center" style={{ color: C.line }}>
                  Без рассылки. Одно сообщение — когда всё будет готово.
                </p>
              </form>
            </PixelCard>
          ) : (
            <PixelCard borderColor={C.acid} className="p-8 text-center">
              <div className="text-4xl mb-4">⚡</div>
              <h3
                className="text-lg font-black mb-2"
                style={{ color: C.acid }}
              >
                ПРИНЯТО
              </h3>
              <p style={{ color: C.muted }} className="text-sm">
                Ты в первой волне. Напишем, когда зеркало будет готово.
              </p>
            </PixelCard>
          )}
        </div>
      </section>

      {/* ═══ SECTION 7: ЧТО ДАЛЬШЕ ═══ */}
      <section className="py-16 sm:py-24">
        <div className="max-w-4xl mx-auto px-4 text-center">
          <div
            className="inline-block px-3 py-1 mb-6 text-xs"
            style={{
              color: C.muted,
              border: `1px solid ${C.line}`,
              fontFamily: "'Press Start 2P', monospace",
              fontSize: "7px",
            }}
          >
            СКОРО
          </div>
          <h2 className="text-xl sm:text-2xl font-black mb-6" style={{ color: C.muted }}>
            Прокачка. Бои. Таблица сильнейших.
          </h2>
          <p className="text-sm mb-8" style={{ color: C.line }}>
            Сначала — разберись с собой. Потом — докажи, что ты крепче остальных.
          </p>

          <div className="grid grid-cols-3 gap-3 max-w-md mx-auto">
            {[
              { icon: "⚔️", label: "поединки" },
              { icon: "📈", label: "рост двойника" },
              { icon: "🏆", label: "таблица сильнейших" },
            ].map((item) => (
              <div
                key={item.label}
                className="p-3 opacity-50"
                style={{ border: `1px solid ${C.line}30`, background: `${C.panel}80` }}
              >
                <div className="text-xl mb-1">{item.icon}</div>
                <div className="text-xs" style={{ color: C.line }}>
                  {item.label}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ═══ FOOTER ═══ */}
      <footer className="py-8 border-t" style={{ borderColor: `${C.line}30` }}>
        <div className="max-w-4xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div style={{ fontFamily: "'Press Start 2P', monospace", fontSize: "11px" }}>
            <span style={{ color: C.ink }}>NOTLOVE</span>
            <span style={{ color: C.acid }}>.</span>
            <span style={{ color: C.acid }}>ME</span>
          </div>
          <p className="text-xs" style={{ color: C.line }}>
            для тех, кто решил перестать быть тем, кем стал
          </p>
        </div>
      </footer>

      {/* ═══ CSS ANIMATIONS ═══ */}
      <style>{`
        @keyframes glitch-anim-1 {
          0%, 100% { clip-path: inset(0 0 0 0); transform: translate(0); }
          20% { clip-path: inset(20% 0 60% 0); transform: translate(-3px, 1px); }
          40% { clip-path: inset(60% 0 10% 0); transform: translate(3px, -1px); }
          60% { clip-path: inset(40% 0 30% 0); transform: translate(-2px, 0); }
        }
        @keyframes glitch-anim-2 {
          0%, 100% { clip-path: inset(0 0 0 0); transform: translate(0); }
          25% { clip-path: inset(30% 0 40% 0); transform: translate(2px, -1px); }
          50% { clip-path: inset(70% 0 5% 0); transform: translate(-3px, 1px); }
          75% { clip-path: inset(10% 0 70% 0); transform: translate(1px, 0); }
        }
        .glitch-layer {
          position: absolute;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
        }
        .glitch-r {
          color: ${C.red};
          animation: glitch-anim-1 3s infinite linear;
          opacity: 0.6;
        }
        .glitch-g {
          color: ${C.cyan};
          animation: glitch-anim-2 3s infinite linear;
          opacity: 0.4;
        }
        html {
          scroll-behavior: smooth;
        }
        @keyframes hero-pulse {
          0%, 100% { filter: brightness(1) saturate(1); }
          50% { filter: brightness(1.08) saturate(1.15); }
        }
        @keyframes hero-glow-pulse {
          0%, 100% { opacity: 0.6; }
          50% { opacity: 1; }
        }
        .hero-image-wrap img {
          animation: hero-pulse 4s ease-in-out infinite;
        }
        .hero-glow {
          animation: hero-glow-pulse 4s ease-in-out infinite;
        }
      `}</style>
    </div>
  );
}
