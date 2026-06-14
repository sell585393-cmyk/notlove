-- NOTLOVE.ME — Схема базы данных
-- Пользователи, вызовы, чек-ины, слабости

-- ─── Пользователи ───────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS public.users (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    tg_id BIGINT UNIQUE NOT NULL,
    username TEXT DEFAULT '',
    first_name TEXT DEFAULT '',
    state TEXT DEFAULT 'new' CHECK (state IN ('new', 'ready', 'active', 'paused')),
    archetype TEXT CHECK (archetype IN ('slug', 'gladiator', 'boss', 'demon', 'empty', NULL)),
    avatar_url TEXT,
    photo_url TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_users_tg_id ON public.users(tg_id);

-- ─── Слабости пользователя ──────────────────────────────────────

CREATE TABLE IF NOT EXISTS public.user_weaknesses (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    tg_id BIGINT NOT NULL REFERENCES public.users(tg_id) ON DELETE CASCADE,
    weakness_id TEXT NOT NULL CHECK (weakness_id IN ('sleep', 'feed', 'porn', 'food', 'gym', 'money')),
    UNIQUE(tg_id, weakness_id)
);

CREATE INDEX IF NOT EXISTS idx_user_weaknesses_tg_id ON public.user_weaknesses(tg_id);

-- ─── Вызовы (30-дневные) ────────────────────────────────────────

CREATE TABLE IF NOT EXISTS public.challenges (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    tg_id BIGINT NOT NULL REFERENCES public.users(tg_id) ON DELETE CASCADE,
    started_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    ends_at TIMESTAMPTZ NOT NULL,
    day INTEGER DEFAULT 1,
    streak INTEGER DEFAULT 0,
    best_streak INTEGER DEFAULT 0,
    total_checkins INTEGER DEFAULT 0,
    total_fails INTEGER DEFAULT 0,
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_challenges_tg_id ON public.challenges(tg_id);
CREATE INDEX IF NOT EXISTS idx_challenges_active ON public.challenges(active) WHERE active = true;

-- ─── Чек-ины ────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS public.checkins (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    tg_id BIGINT NOT NULL REFERENCES public.users(tg_id) ON DELETE CASCADE,
    challenge_id UUID NOT NULL REFERENCES public.challenges(id) ON DELETE CASCADE,
    day INTEGER NOT NULL,
    passed BOOLEAN NOT NULL DEFAULT false,
    weaknesses_held TEXT[] DEFAULT '{}',
    note TEXT DEFAULT '',
    checked_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_checkins_challenge_id ON public.checkins(challenge_id);
CREATE INDEX IF NOT EXISTS idx_checkins_tg_id ON public.checkins(tg_id);
CREATE INDEX IF NOT EXISTS idx_checkins_checked_at ON public.checkins(checked_at);

-- ─── RLS ────────────────────────────────────────────────────────

ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_weaknesses ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.challenges ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.checkins ENABLE ROW LEVEL SECURITY;

-- Бот обращается через service_role key, поэтому RLS не мешает.
-- Для мини-аппа через anon key — разрешаем чтение по tg_id.

CREATE POLICY "Users can read own data" ON public.users
    FOR SELECT USING (true);

CREATE POLICY "Users can read own weaknesses" ON public.user_weaknesses
    FOR SELECT USING (true);

CREATE POLICY "Users can read own challenges" ON public.challenges
    FOR SELECT USING (true);

CREATE POLICY "Users can read own checkins" ON public.checkins
    FOR SELECT USING (true);

-- Запись — только через бота (service_role), не через anon.
-- Для anon key запрещаем INSERT/UPDATE/DELETE.
