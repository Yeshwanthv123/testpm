import { Question } from '../types';

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

// Fetches and transforms questions from the backend
export const fetchInterviewQuestions = async (company: string, role: string): Promise<Question[]> => {
  try {
    const path = `/api/interview/questions?company=${encodeURIComponent(company)}&role=${encodeURIComponent(role)}`;
    const backendQuestions = await api<any[]>(path, 'GET');

    // Transform backend data to match the frontend's Question type
    return backendQuestions.map(q => ({
        id: String(q.id),
        question: q.text,
        category: q.category || 'General',
        difficulty: (q.complexity?.toLowerCase() as 'easy' | 'medium' | 'hard') || 'medium',
        type: 'behavioral', // Defaulting type as it's not in the backend model
        timeLimit: 240, // Defaulting time limit
        skills: ['Problem Solving', 'Communication'], // Defaulting skills
    }));
  } catch (error) {
    console.error('Failed to fetch interview questions:', error);
    return []; // Return empty array on failure
  }
};