const API_BASE =
  (import.meta.env.VITE_API_BASE as string) ||
  (window as any).REACT_APP_API_BASE ||
  "http://localhost:8000";

export type HttpMethod = "GET" | "POST" | "PUT" | "DELETE";

export function getApiBase() {
  return API_BASE;
}

export async function api<T>(
  path: string,
  method: HttpMethod = "GET",
  body?: unknown,
  token?: string
): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    method,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: body ? JSON.stringify(body) : undefined,
  });

  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(text || `${res.status} ${res.statusText}`);
  }
  return (await res.json()) as T;
}
