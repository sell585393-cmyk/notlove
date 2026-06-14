/**
 * Слабости и архетипы — зеркало конфига бота
 */

export const WEAKNESSES: Record<
  string,
  { label: string; emoji: string; desc: string; color: string }
> = {
  sleep: {
    label: "Сон",
    emoji: "🌙",
    desc: "Ложишься когда придётся, встаёшь никакой",
    color: "#41d1da",
  },
  feed: {
    label: "Лента",
    emoji: "📱",
    desc: "Часы уходят в чужие жизни",
    color: "#b9f22a",
  },
  porn: {
    label: "18+",
    emoji: "🔞",
    desc: "Каждый вечер одно и то же",
    color: "#e64036",
  },
  food: {
    label: "Еда",
    emoji: "🍔",
    desc: "Топливо из помойки",
    color: "#e8a72f",
  },
  gym: {
    label: "Тело",
    emoji: "🏋️",
    desc: "Ни разу не встал ради себя",
    color: "#e64036",
  },
  money: {
    label: "Деньги",
    emoji: "💸",
    desc: "Тратишь на мусор, копишь на ничего",
    color: "#e8a72f",
  },
};

export const ARCHETYPES: Record<
  string,
  { label: string; desc: string }
> = {
  slug: { label: "Сутулый Слизень", desc: "Сидячий, телефон, ноль режима" },
  gladiator: {
    label: "Сырой Гладиатор",
    desc: "Потенциал есть, дисциплины нет",
  },
  boss: {
    label: "Жирный Босс",
    desc: "Деньги/еда/стресс, надо резать лишнее",
  },
  demon: { label: "Ночной Демон", desc: "Сон убит, думскролл, хаос" },
  empty: {
    label: "Пустой Качок",
    desc: "Форма есть, но режим ломает прогресс",
  },
};
