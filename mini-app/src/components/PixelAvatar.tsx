import { useEffect, useRef } from "react";

interface PixelAvatarProps {
  avatarUrl?: string | null;
  archetype?: string;
  streak?: number;
  size?: number;
}

/**
 * Пиксельный аватар с idle-анимацией.
 *
 * Если есть avatarUrl — показываем сгенерированный аватар.
 * Если нет — рисуем процедурного персонажа на canvas.
 */
export function PixelAvatar({
  avatarUrl,
  archetype = "slug",
  streak = 0,
  size = 256,
}: PixelAvatarProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const frameRef = useRef(0);

  // Цвета по архетипу
  const colors: Record<string, { body: string; accent: string }> = {
    slug: { body: "#4a5a4a", accent: "#8b978f" },
    gladiator: { body: "#6a4a3a", accent: "#e8a72f" },
    boss: { body: "#5a4a5a", accent: "#e64036" },
    demon: { body: "#2a2a4a", accent: "#41d1da" },
    empty: { body: "#5a5a3a", accent: "#b9f22a" },
  };

  useEffect(() => {
    if (avatarUrl) return; // Не рисуем, если есть картинка

    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    // Работаем в низком разрешении для пиксельного эффекта
    const pixelSize = 4;
    const w = size / pixelSize;
    const h = size / pixelSize;
    canvas.width = w;
    canvas.height = h;

    const c = colors[archetype] || colors.slug;

    let animFrame: number;

    function draw() {
      if (!ctx) return;
      frameRef.current++;
      const frame = frameRef.current;

      // Фон
      ctx.fillStyle = "#050608";
      ctx.fillRect(0, 0, w, h);

      // Простой пиксельный персонаж
      const cx = Math.floor(w / 2);
      const cy = Math.floor(h * 0.6);

      // Idle-дыхание
      const breathe = Math.sin(frame * 0.05) * 0.5;

      // Тело
      ctx.fillStyle = c.body;

      // Голова (8x8 пикселей)
      const headY = cy - 14 + Math.round(breathe);
      ctx.fillRect(cx - 4, headY, 8, 8);

      // Глаза
      ctx.fillStyle = streak > 0 ? c.accent : "#e64036";
      ctx.fillRect(cx - 2, headY + 3, 2, 2);
      ctx.fillRect(cx + 1, headY + 3, 2, 2);

      // Тело
      ctx.fillStyle = c.body;
      const bodyY = headY + 8;
      ctx.fillRect(cx - 5, bodyY, 10, 10);

      // Руки
      const armSwing = Math.sin(frame * 0.08) * 1;
      ctx.fillRect(cx - 7, bodyY + 1 + Math.round(armSwing), 2, 6);
      ctx.fillRect(cx + 5, bodyY + 1 - Math.round(armSwing), 2, 6);

      // Ноги
      ctx.fillRect(cx - 4, bodyY + 10, 3, 5);
      ctx.fillRect(cx + 1, bodyY + 10, 3, 5);

      // Эволюция: если стрик > 7, добавляем "броню"
      if (streak >= 7) {
        ctx.fillStyle = c.accent;
        // Наплечники
        ctx.fillRect(cx - 7, bodyY - 1, 3, 3);
        ctx.fillRect(cx + 4, bodyY - 1, 3, 3);
      }

      // Стрик >= 14: аура
      if (streak >= 14) {
        ctx.fillStyle = c.accent + "40";
        ctx.fillRect(cx - 8, headY - 3, 16, 28);
      }

      // Стрик >= 21: корона
      if (streak >= 21) {
        ctx.fillStyle = "#e8a72f";
        ctx.fillRect(cx - 3, headY - 3, 6, 2);
        ctx.fillRect(cx - 3, headY - 4, 2, 1);
        ctx.fillRect(cx - 1, headY - 5, 2, 1);
        ctx.fillRect(cx + 1, headY - 4, 2, 1);
      }

      animFrame = requestAnimationFrame(draw);
    }

    draw();
    return () => cancelAnimationFrame(animFrame);
  }, [avatarUrl, archetype, streak, size]);

  if (avatarUrl) {
    return (
      <div
        className="relative mx-auto"
        style={{ width: size, height: size }}
      >
        <img
          src={avatarUrl}
          alt="Твой двойник"
          className="w-full h-full object-cover"
          style={{ imageRendering: "pixelated" }}
        />
        {/* CRT overlay */}
        <div
          className="absolute inset-0 pointer-events-none"
          style={{
            background:
              "repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(0,0,0,0.1) 2px, rgba(0,0,0,0.1) 4px)",
          }}
        />
      </div>
    );
  }

  return (
    <canvas
      ref={canvasRef}
      className="mx-auto"
      style={{
        width: size,
        height: size,
        imageRendering: "pixelated",
      }}
    />
  );
}
