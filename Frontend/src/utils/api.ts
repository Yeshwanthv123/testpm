// ---- Types ---------------------------------------------------------------

export type QuestionDTO = {
  id: string | number | null;
  question: string | null;
  company?: string | null;
  category?: string | null;
  complexity?: string | null;
  experience_level?: string | null;
  years_of_experience?: string | null;
  // ADDED: skills to match backend output from _serialize_question
  skills?: string[] | null;
};

export type FetchQuestionsParams = {
  company?: string | null;
  role?: string | null; // APM | PM | Senior PM | Group PM | Principal PM | Director
  experience?: string | null; // "0-2" | "2-4" | "5-8" | "8+"
  signal?: AbortSignal;
};

// ---- Config --------------------------------------------------------------

/**
 * Resolve API base URL without changing other files.
 * Priority:
 * 1) Vite env: import.meta.env.VITE_API_BASE
 * 2) Global injected var: (window as any).__API_BASE__
 * 3) Fallback: http://localhost:8000
 */
function getApiBase(): string {
  const viteEnv = (import.meta as any)?.env?.VITE_API_BASE;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const injected = (window as any)?.__API_BASE__;
  return (viteEnv || injected || "http://localhost:8000").replace(/\/+$/, "");
}

const API_BASE = getApiBase();
const INTERVIEW_PATH = "/api/interview/questions";
// --- ADDED THIS LINE ---
const INTERVIEW_JD_PATH = "/api/interview/start-with-jd";

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
        skills: item?.skills ?? null, // Added skills
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

//
// --- START OF NEW FUNCTION ---
//

/**
 * Fetch a single interview question based on a Job Description (JD).
 * Returns an array containing a single QuestionDTO.
 */
export async function startInterviewWithJD(
  jdText: string,
  params: { signal?: AbortSignal }
): Promise<QuestionDTO[]> {
  const url = API_BASE + INTERVIEW_JD_PATH;

  let res: Response;
  try {
    res = await fetch(url, {
      method: "POST",
      headers: {
        "Accept": "application/json",
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ jd_text: jdText }),
      signal: params.signal,
    });
  } catch (networkErr) {
    return [
      {
        id: null,
        question:
          "We couldn’t reach the interview service to analyze the JD. Please ensure the backend is running and CORS allows this origin.",
        company: "From JD",
        category: null,
        complexity: null,
        experience_level: null,
        years_of_experience: null,
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
          `AI service returned ${res.status}. Make sure the '/api/interview/start-with-jd' endpoint is working.`,
        company: "From JD",
        category: null,
        complexity: null,
        experience_level: null,
        years_of_experience: null,
      },
    ];
  }

  try {
    // The backend returns a SINGLE question object (or sometimes a wrapper like { data: { ... } }).
    const item = (await res.json()) as unknown;

    if (typeof item !== "object" || item === null || Array.isArray(item)) {
      throw new Error("Unexpected response shape: expected a single object");
    }

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const anyItem = item as any;
    // Support both direct object and wrapped responses { data: { ... } }
    const payload = anyItem?.data ?? anyItem;

    // The question text may exist as 'question' or 'text', and in some shapes
    // it could be nested; be permissive.
    const qText =
      payload?.question ??
      payload?.text ??
      (typeof payload?.question === 'object' ? payload?.question?.text : null) ??
      null;

    // If the AI returns metadata under `ai_extracted`, prefer those fields
    const aiMeta = payload?.ai_extracted ?? null;

    const mapped: QuestionDTO = {
      id: payload?.id ?? null,
      question: typeof qText === "string" ? qText : qText == null ? null : String(qText),
      company: payload?.company ?? aiMeta?.company_name ?? null,
      category: payload?.category ?? null,
      complexity: payload?.complexity ?? null,
      // Preference: explicit experience_level, otherwise fall back to ai_extracted.role
      experience_level: payload?.experience_level ?? aiMeta?.role ?? null,
      years_of_experience: payload?.years_of_experience ?? null,
      skills: payload?.skills ?? null,
    };

    // Return it as an array with one item, so InterviewSetup.tsx can treat it
    // the same as fetchInterviewQuestions
    return [mapped];

  } catch (err) {
    return [
      {
        id: null,
        question:
          "Failed to parse the question from the AI service. Check that the backend returns JSON and matches the expected shape.",
        company: "From JD",
        category: null,
        complexity: null,
        experience_level: null,
        years_of_experience: null,
      },
    ];
  }
}

// --- END OF NEW FUNCTION ---

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