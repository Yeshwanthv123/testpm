// Frontend/src/utils/api.ts

// ---- Types ---------------------------------------------------------------

export type QuestionDTO = {
  id: string | number | null;
  question: string | null;
  company?: string | null;
  category?: string | null;
  complexity?: string | null;
  experience_level?: string | null;
  years_of_experience?: string | null;
};

export type FetchQuestionsParams = {
  company?: string | null;
  role?: string | null;        // APM | PM | Senior PM | Group PM | Principal PM | Director
  experience?: string | null;  // "0-2" | "2-4" | "5-8" | "8+"
  signal?: AbortSignal;
};

// ---- Config --------------------------------------------------------------

/**
 * Resolve API base URL without changing other files.
 * Priority:
 *   1) Vite env: import.meta.env.VITE_API_BASE
 *   2) Global injected var: (window as any).__API_BASE__
 *   3) Fallback: http://localhost:8000
 */
function getApiBase(): string {
  const viteEnv = (import.meta as any)?.env?.VITE_API_BASE;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const injected = (window as any)?.__API_BASE__;
  return (viteEnv || injected || "http://localhost:8000").replace(/\/+$/, "");
}

const API_BASE = getApiBase();
const INTERVIEW_PATH = "/api/interview/questions";

// ---- Helpers -------------------------------------------------------------

function qs(obj: Record<string, string | undefined>): string {
  const parts: string[] = [];
  for (const [k, v] of Object.entries(obj)) {
    if (v === undefined) continue;
    parts.push(`${encodeURIComponent(k)}=${encodeURIComponent(v)}`);
  }
  return parts.length ? `?${parts.join("&")}` : "";
}

function normalizeStr(v?: string | null): string | undefined {
  if (v == null) return undefined;
  const s = String(v).trim();
  return s.length ? s : undefined;
}

// NEW: stable anonymous session key for no-repeat sampling
function getSessionKey(): string {
  const KEY = "pmbot_session_id";
  let id = localStorage.getItem(KEY);
  if (!id) {
    // Prefer crypto.randomUUID if available; otherwise fallback
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const anyCrypto: any = (typeof crypto !== "undefined" ? crypto : null);
    if (anyCrypto?.randomUUID) {
      id = anyCrypto.randomUUID();
    } else {
      // Simple fallback UUID-ish
      id = "xxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, (c) => {
        const r = (Math.random() * 16) | 0;
        const v = c === "x" ? r : (r & 0x3) | 0x8;
        return v.toString(16);
      });
    }
    localStorage.setItem(KEY, id);
  }
  return id;
}

// ---- Public API ----------------------------------------------------------

/**
 * Fetch interview questions from backend with safe defaults.
 * Returns an array (up to 10) of QuestionDTO.
 */
export async function fetchInterviewQuestions(params: FetchQuestionsParams): Promise<QuestionDTO[]> {
  const company = normalizeStr(params.company);
  const role = normalizeStr(params.role);
  const experience = normalizeStr(params.experience);

  // NEW: include session so server can avoid repeating questions across runs
  const session = getSessionKey();

  const url =
    API_BASE +
    INTERVIEW_PATH +
    qs({
      company,
      role,
      experience,
      session, // <— NEW
    });

  let res: Response;
  try {
    res = await fetch(url, {
      method: "GET",
      headers: {
        "Accept": "application/json",
      },
      signal: params.signal,
    });
  } catch (networkErr) {
    return [
      {
        id: null,
        question:
          "We couldn’t reach the interview service. Please ensure the backend is running and CORS allows this origin.",
        company: company ?? null,
        category: null,
        complexity: null,
        experience_level: role ?? null,
        years_of_experience: experience ?? null,
      },
    ];
  }

  if (!res.ok) {
    const detail = (() => {
      try {
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        const j = (res as any)._jsonParsed ?? null;
        return j?.detail ?? null;
      } catch {
        return null;
      }
    })();

    return [
      {
        id: null,
        question:
          detail ||
          `Interview service returned ${res.status}. Make sure questions are loaded from CSV and the API is reachable.`,
        company: company ?? null,
        category: null,
        complexity: null,
        experience_level: role ?? null,
        years_of_experience: experience ?? null,
      },
    ];
  }

  try {
    const data = (await res.json()) as unknown;

    if (!Array.isArray(data)) {
      throw new Error("Unexpected response shape");
    }

    const mapped: QuestionDTO[] = data.map((item: any) => {
      const qText = item?.question ?? item?.text ?? null;
      return {
        id: item?.id ?? null,
        question: typeof qText === "string" ? qText : qText == null ? null : String(qText),
        company: item?.company ?? null,
        category: item?.category ?? null,
        complexity: item?.complexity ?? null,
        experience_level: item?.experience_level ?? null,
        years_of_experience: item?.years_of_experience ?? null,
      };
    });

    if (!mapped.length) {
      return [
        {
          id: null,
          question:
            "No questions were returned. If you just set up, load the CSV into the database and try again.",
          company: company ?? null,
          category: null,
          complexity: null,
          experience_level: role ?? null,
          years_of_experience: experience ?? null,
        },
      ];
    }

    return mapped;
  } catch {
    return [
      {
        id: null,
        question:
          "Failed to parse questions from the server. Check that the backend returns JSON and matches the expected shape.",
        company: company ?? null,
        category: null,
        complexity: null,
        experience_level: role ?? null,
        years_of_experience: experience ?? null,
      },
    ];
  }
}

/**
 * Optional: small health check you can call from your app if needed.
 * (Safe to ignore if unused; doesn't change any existing code.)
 */
export async function pingApi(): Promise<boolean> {
  try {
    const res = await fetch(API_BASE + "/openapi.json", { method: "GET" });
    return res.ok;
  } catch {
    return false;
  }
}
