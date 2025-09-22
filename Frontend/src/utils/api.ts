import { Question } from '../types'; // Import the Question type

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

// +++ Add the following new function +++
export const fetchInterviewQuestions = async (company: string, role: string): Promise<Question[]> => {
  try {
    // Construct the path with URL query parameters
    const path = `/api/interview/questions?company=${encodeURIComponent(company)}&role=${encodeURIComponent(role)}`;
    // Use the existing generic 'api' function to make the request
    const questions = await api<Question[]>(path, 'GET');
    return questions;
  } catch (error) {
    console.error('Failed to fetch interview questions:', error);
    // On failure, return an empty array to prevent the app from crashing
    return [];
  }
};
// +++ End of new code +++