import { api } from "./api";

const ACCESS_KEY = "access_token";
const REFRESH_KEY = "refresh_token";

type TokenPair = { access_token: string; refresh_token: string; token_type: "bearer" };
export type User = { id: number; email: string; full_name?: string | null };

export async function register(email: string, password: string, fullName?: string) {
  return api<User>("/auth/register", "POST", { email, password, full_name: fullName ?? "" });
}

export async function login(email: string, password: string) {
  const tokens = await api<TokenPair>("/auth/login", "POST", { email, password });
  localStorage.setItem(ACCESS_KEY, tokens.access_token);
  localStorage.setItem(REFRESH_KEY, tokens.refresh_token);
  return tokens;
}

export function getAccessToken() {
  return localStorage.getItem(ACCESS_KEY) || "";
}

export function getRefreshToken() {
  return localStorage.getItem(REFRESH_KEY) || "";
}

export async function me() {
  const token = getAccessToken();
  if (!token) throw new Error("Not authenticated");
  return api<User>("/auth/me", "GET", undefined, token);
}

export function logout() {
  localStorage.removeItem(ACCESS_KEY);
  localStorage.removeItem(REFRESH_KEY);
}

export async function refresh() {
  const rt = getRefreshToken();
  if (!rt) throw new Error("Missing refresh token");
  const tokens = await api<TokenPair>("/auth/refresh", "POST", { refresh_token: rt });
  localStorage.setItem(ACCESS_KEY, tokens.access_token);
  localStorage.setItem(REFRESH_KEY, tokens.refresh_token);
  return tokens;
}
