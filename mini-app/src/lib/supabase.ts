import { createClient } from "@supabase/supabase-js";

const SUPABASE_URL = "https://wfkplqgufdaxnczvyhpn.supabase.co";
const SUPABASE_ANON_KEY = import.meta.env.VITE_SUPABASE_ANON_KEY || "";

export const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

export interface User {
  id: string;
  tg_id: number;
  username: string;
  first_name: string;
  state: string;
  archetype: string | null;
  avatar_url: string | null;
  photo_url: string | null;
  created_at: string;
}

export interface Challenge {
  id: string;
  tg_id: number;
  started_at: string;
  ends_at: string;
  day: number;
  streak: number;
  total_checkins: number;
  total_fails: number;
  active: boolean;
}

export interface Checkin {
  id: string;
  tg_id: number;
  challenge_id: string;
  day: number;
  passed: boolean;
  weaknesses_held: string[];
  note: string;
  checked_at: string;
}

export async function getUser(tgId: number): Promise<User | null> {
  const { data } = await supabase
    .from("users")
    .select("*")
    .eq("tg_id", tgId)
    .maybeSingle();
  return data;
}

export async function getActiveChallenge(
  tgId: number,
): Promise<Challenge | null> {
  const { data } = await supabase
    .from("challenges")
    .select("*")
    .eq("tg_id", tgId)
    .eq("active", true)
    .order("started_at", { ascending: false })
    .limit(1)
    .maybeSingle();
  return data;
}

export async function getCheckins(challengeId: string): Promise<Checkin[]> {
  const { data } = await supabase
    .from("checkins")
    .select("*")
    .eq("challenge_id", challengeId)
    .order("day");
  return data ?? [];
}

export async function getUserWeaknesses(tgId: number): Promise<string[]> {
  const { data } = await supabase
    .from("user_weaknesses")
    .select("weakness_id")
    .eq("tg_id", tgId);
  return data?.map((r) => r.weakness_id) ?? [];
}
