import os
import json
import pandas as pd
import requests

# Optional sentence embedding support — try to load sentence-transformers if available.
EMBEDDING_AVAILABLE = False
_embed_model = None
try:
    from sentence_transformers import SentenceTransformer
    _embed_model = SentenceTransformer('all-MiniLM-L6-v2')
    EMBEDDING_AVAILABLE = True
    print('[AIService] sentence-transformers available — using semantic similarity')
except Exception:
    EMBEDDING_AVAILABLE = False
    _embed_model = None

CSV_PATH = os.path.join(os.path.dirname(__file__), "../PM_Questions_8000_expanded_clean_final5.csv")

try:
    df = pd.read_csv(CSV_PATH)
    VALID_COMPANIES = sorted(df["Company"].dropna().unique().tolist())
    VALID_ROLES = sorted(df["Experience Level"].dropna().unique().tolist())
    VALID_LEVELS = sorted(df["Category"].dropna().unique().tolist())
except Exception as e:
    print(f"[AIService] CSV load failed: {e}")
    VALID_COMPANIES = ["Unknown Company"]
    VALID_ROLES = ["PM", "Senior PM", "APM", "Group PM", "Principal PM", "Director"]
    VALID_LEVELS = ["Strategic"]

SYSTEM_PROMPT = f"""
You are an expert HR assistant. Read the following job description (JD)
and extract these three things:

1️⃣ company_name — must be one of these or closest match:
{VALID_COMPANIES[:80]}

2️⃣ years_of_experience — infer from JD and return one of:
   "0-2", "3-5", "6-10", "10+"

3️⃣ level — must be one of these (job category/topic):
{VALID_LEVELS}

Respond ONLY in valid JSON:
{{"company_name": "...", "years_of_experience": "...", "level": "..."}}.
"""

class AIService:
    def __init__(self):
        # Allow configuring the LLM HTTP base URL via env var so the service
        # can point to an external Ollama-like endpoint or an in-repo stub.
        self.llm_api_url = os.environ.get("LLM_API_URL", "http://localhost:11434").rstrip("/")
        # Allow forcing a model via env var (e.g., qwen2:7b-instruct). If provided,
        # try to use it when available; otherwise fallback to any available model.
        # Default to qwen2:7b-instruct for environments where no variable is set.
        self.desired_model = os.environ.get("LLM_MODEL", "qwen2:7b-instruct")
        # If set, enforce using the LLM and do NOT fall back to the heuristic evaluator.
        self.force_llm = str(os.environ.get("LLM_FORCE", "0")).lower() in ("1", "true", "yes")
        self._answer_cache = {}

        if self.desired_model:
            # Prefer the explicitly configured desired model. Set it as the model
            # to use and attempt to verify availability; if verification fails,
            # we still keep the desired_model so the runtime will attempt to use it.
            self.model = self.desired_model
            try:
                r = requests.get(f"{self.llm_api_url}/api/tags", timeout=5)
                models = r.json().get("models", [])
                listed = [m.get("name", "") for m in models]
                if not any(self.desired_model == n or self.desired_model in n for n in listed):
                    print(f"[AIService] Desired model '{self.desired_model}' not listed by LLM endpoint; will still attempt to use it and fallback on failure.")
            except Exception as e:
                print(f"[AIService] Could not contact LLM tags endpoint to verify desired model: {e}; will attempt to use desired model and fallback on errors.")
        else:
            self.model = self._get_available_model()

        print(f"[AIService] Using LLM endpoint: {self.llm_api_url}, model: {self.model}")

    def _get_available_model(self):
        # Try to query the tags endpoint a few times in case the LLM service
        # is still starting. This reduces race conditions where backend starts
        # before the LLM stub and immediately falls back to the default model.
        tries = 6
        delay = 2
        for attempt in range(tries):
            try:
                r = requests.get(f"{self.llm_api_url}/api/tags", timeout=5)
                models = r.json().get("models", [])
                if models:
                    # If a desired model was configured, prefer it when returned by the endpoint
                    if self.desired_model:
                        for m in models:
                            name = m.get("name", "")
                            if name == self.desired_model or (self.desired_model in name):
                                return name
                    # Otherwise prefer llama3 if available for backwards-compatibility
                    for m in models:
                        name = m.get("name", "")
                        if "llama3" in name:
                            return name
                    # Fallback: return the first available model name
                    return models[0]["name"]
            except Exception:
                # Sleep briefly and retry
                try:
                    import time
                    time.sleep(delay)
                except Exception:
                    pass
        # If we could not contact tags or no models found, prefer the desired_model
        # if it was set (we'll still attempt to use it); otherwise fall back to llama3.
        if self.desired_model:
            return self.desired_model
        return "llama3"

    def _query_ollama(self, prompt: str) -> str:
        """
        Send prompt to the configured LLM endpoint and return the model's text output.
        Adds flexible parsing for different JSON response formats and detailed error logs.
        """
        tries = 3
        delay = 1
        last_exc = None

        for attempt in range(tries):
            try:
                response = requests.post(
                    f"{self.llm_api_url}/api/generate",
                    json={"model": self.model, "prompt": prompt, "stream": False},
                    timeout=600,
                )

                # Try multiple possible response structures
                resp_json = response.json()
                raw_text = (
                    resp_json.get("response")
                    or resp_json.get("data", {}).get("output_text")
                    or resp_json.get("message")
                    or resp_json.get("text")
                    or ""
                )

                raw_text = (raw_text or "").strip()

                # Optional: small debug log for troubleshooting
                if not raw_text:
                    print(f"[AIService] Empty response on attempt {attempt+1} from {self.llm_api_url}, model={self.model}")
                else:
                    return raw_text

            except Exception as e:
                last_exc = e
                print(f"[AIService] LLM query error on attempt {attempt+1}: {e}")
                try:
                    import time
                    time.sleep(delay)
                    delay *= 2
                except Exception:
                    pass

        print(f"[Ollama error] Failed after {tries} attempts: {last_exc}")
        return ""

    def _wrapper_generate_answer(self, question_text: str, skills: list | None = None, model: str | None = None) -> str:
        """Call the LLM wrapper `/api/generate-answer` to get a single structured model answer."""
        try:
            url = f"{self.llm_api_url.rstrip('/')}/api/generate-answer"
            payload = {"question": question_text, "skills": skills or []}
            if model:
                payload["model"] = model
            resp = requests.post(url, json=payload, timeout=600)
            if resp.status_code == 200:
                data = resp.json()
                # wrapper returns {'answer': '...'}
                ans = data.get('answer') or data.get('response') or ''
                return (ans or '').strip()
        except Exception as e:
            print(f"[AIService _wrapper_generate_answer error] {e}")
        return ""

    def _wrapper_evaluate_answer(self, question_text: str, user_answer: str, model_answer: str, skills: list | None = None, model: str | None = None) -> dict:
        """Call the LLM wrapper `/api/evaluate-answer` which returns structured JSON evaluation."""
        try:
            url = f"{self.llm_api_url.rstrip('/')}/api/evaluate-answer"
            payload = {"question": question_text, "user_answer": user_answer, "model_answer": model_answer, "skills": skills or []}
            if model_answer is None:
                payload.pop('model_answer', None)
            # If caller specified model param, use it; else allow an eval_model_override attribute
            if model:
                payload['model'] = model
            elif getattr(self, 'eval_model_override', None):
                payload['model'] = getattr(self, 'eval_model_override')
            resp = requests.post(url, json=payload, timeout=600)
            if resp.status_code == 200:
                data = resp.json()
                # Normalize possible wrapper structures: accept nested suggestions.feedback or top-level keys
                out = {}
                out['similarity_score'] = float(data.get('similarity_score') or 0.0)
                out['score'] = int(data.get('score') or 0)
                out['ideal_answer'] = data.get('ideal_answer') or model_answer
                # strengths/improvements may be top-level or under suggestions.feedback
                strengths = data.get('strengths')
                improvements = data.get('improvements')
                feedback_text = data.get('feedback')
                if (not strengths or not improvements) and isinstance(data.get('suggestions'), dict):
                    fb = data.get('suggestions', {}).get('feedback', {})
                    if isinstance(fb, dict):
                        strengths = strengths or fb.get('strengths') or []
                        improvements = improvements or fb.get('improvements') or []
                        feedback_text = feedback_text or fb.get('comparison') or fb.get('feedback')
                out['strengths'] = strengths or []
                out['improvements'] = improvements or []
                out['feedback'] = feedback_text or ''
                out['suggestions'] = data.get('suggestions') or {}
                return out
            else:
                print(f"[AIService _wrapper_evaluate_answer] HTTP {resp.status_code}: {resp.text[:200]}")
        except Exception as e:
            print(f"[AIService _wrapper_evaluate_answer error] {e}")
        return {}

    def _find_best_match(self, text: str, valid_list: list) -> str:
        if not text or not valid_list:
            return valid_list[0]
        lower = text.lower().strip()
        for v in valid_list:
            if v.lower() == lower:
                return v
        for v in valid_list:
            if lower in v.lower() or v.lower() in lower:
                return v
        return valid_list[0]

    def _fallback_model_answer(self, question_text: str, skills: list | None = None) -> str:
        """Deterministic high-quality scaffolded model answer used when the LLM
        is unavailable. This produces a detailed, multi-paragraph answer that
        the evaluator can compare against the user's answer.
        """
        skills_text = ", ".join(skills) if skills else "product thinking, execution, and measurement"
        return (
            f"Summary:\nProvide a concise recommendation and primary outcome.\n\n"
            f"Approach:\n1) Clarify goals and target users. 2) Break problem into key pillars (user research, MVP, metrics).\n"
            f"3) Design experiments and success criteria. 4) Iterate with cross-functional partners.\n\n"
            f"Example:\nDescribe a specific project example: timeline, decisions made, trade-offs, stakeholders involved, and measurable outcomes.\n\n"
            f"Metrics & Impact:\nList the metrics you would track (e.g., activation, retention, NPS) and target improvements.\n\n"
            f"Skills emphasized: {skills_text}.\n"
        )

    def _heuristic_evaluate(self, question_text: str, user_answer: str, model_answer: str) -> dict:
        """Produce a varied evaluation based on simple linguistic heuristics.
        This is a best-effort evaluator used when the LLM cannot produce a
        structured JSON response. It inspects the user's answer for:
          - presence of a clear summary / structure (look for 'I would', 'Approach', 'Steps')
          - concrete examples (words like 'example', 'project', 'launched')
          - metrics (numbers, % or terms like 'NPS', 'retention')
        The function returns score (0-100), strengths, weaknesses, and feedback.
        """
        ua = (user_answer or "").strip()
        ma = (model_answer or "").strip()

        # token-level signals
        ua_lower = ua.lower()
        ma_lower = ma.lower()
        tokens_ua = set([t for t in ua_lower.split() if t])
        tokens_ma = set([t for t in ma_lower.split() if t])
        overlap = len(tokens_ua & tokens_ma)

        # structural and content signals
        has_summary = any(kw in ua_lower for kw in ["i would","my approach","summary","approach","steps","first"]) or len(ua.split()) > 40
        has_example = any(kw in ua_lower for kw in ["example","project","launched","led","implemented","we did","for example"]) or any(ch.isdigit() for ch in ua)
        has_metrics = any(kw in ua_lower for kw in ["nps","%","percent","retention","growth","metric","kpi","users"]) or any(token.isdigit() for token in ua_lower.split())

        # base signals -> flexible weighted composition to increase spread
        # overlap contributes strongly when present; length contributes modestly
        overlap_score = min(70, int((overlap / max(1, len(tokens_ma))) * 70)) if tokens_ma else 0
        length_score = min(20, int((len(ua.split()) / 50) * 20))
        bonus = 0
        if has_summary: bonus += 6
        if has_example: bonus += 10
        if has_metrics: bonus += 8

        raw = overlap_score + length_score + bonus

        # deterministic tip/template selection for varied, sensible feedback
        rnd = __import__('random').Random()
        rnd.seed((question_text or '') + '|' + (ua or ''))
        tip_templates = [
            "Start with a one-sentence summary, then outline 2–4 steps, and finish with expected impact.",
            "Use the STAR format: Situation → Task → Action → Result. Be concise and include metrics.",
            "Quantify impact where possible (e.g., % lift, absolute users). Mention how you'd measure success.",
            "Lead with the decision, then explain trade-offs and measurable outcomes. This helps interviewers follow your thinking.",
        ]
        tip = rnd.choice(tip_templates)

        # build score with topical relevance and length signals, plus small deterministic jitter
        topical = int(min(70, (overlap / max(1, len(tokens_ma))) * 70)) if tokens_ma else 0
        length_sig = min(30, int((len(ua.split()) / 60) * 30))
        base = topical + length_sig
        jitter = rnd.randint(-6, 6)
        score = int(max(0, min(100, base + jitter)))

        # build readable strengths/weaknesses and short actionable tips
        strengths = []
        weaknesses = []
        tips = []
        if overlap > 0:
            strengths.append('You covered some of the key points from the ideal answer.')
        if has_example:
            strengths.append('Good — you used a short example to illustrate your point.')
        if has_metrics:
            strengths.append('Nice use of metrics to quantify impact.')

        if not has_example:
            weaknesses.append('Missing a concise example — add a 1–2 sentence STAR example (Situation, Action, Result).')
            tips.append('Pick one relevant project and state what you changed and the measurable outcome.')
        if not has_metrics:
            weaknesses.append('No concrete metrics — include an outcome (e.g., % increase, absolute numbers).')
            tips.append('State the metric you would track and the expected lift (e.g., +8% conversion).')
        if not any(k in ua_lower for k in ['summary','i would','in short','approach','steps']):
            weaknesses.append('Starts without a one-line summary — lead with your recommendation.')
            tips.append("Open with a 1-line recommendation, then list 2–3 steps and finish with impact.")

        # Missing model points (short list) — give a few example sentences the user missed
        missing_points = []
        try:
            ma_sents = [s.strip() for s in __import__('re').split(r"(?<=[.?!])\s+", ma) if s.strip()]
            for s in ma_sents[:4]:
                words = set([w for w in s.lower().split() if w])
                if len(words & tokens_ua) / max(1, len(words)) < 0.25:
                    missing_points.append(s)
        except Exception:
            missing_points = []

        # Compose short, user-friendly feedback
        feedback_lines = [f"Score: {score}/100."]
        if strengths:
            feedback_lines.append('What went well:')
            for s in strengths:
                feedback_lines.append(f"- {s}")
        if weaknesses:
            feedback_lines.append('What to improve:')
            for w in weaknesses:
                feedback_lines.append(f"- {w}")
        if tips:
            feedback_lines.append('Quick tips:')
            for t in tips[:2]:
                feedback_lines.append(f"- {t}")
        if missing_points:
            feedback_lines.append('Example points you could add:')
            for p in missing_points[:3]:
                feedback_lines.append(f"- {p}")
        feedback_lines.append('Try: Summary → Approach → Example → Metric.')

        return {
            'score': int(score),
            'strengths': strengths,
            'weaknesses': weaknesses,
            'feedback': '\n'.join(feedback_lines),
        }

    def _label_for_score(self, score: int) -> str:
        if score >= 85:
            return "Excellent"
        if score >= 70:
            return "Strong"
        if score >= 50:
            return "Average"
        if score >= 30:
            return "Needs work"
        return "Poor"

    def _deterministic_rng(self, *parts: str):
        s = "||".join([p or "" for p in parts])
        import hashlib, random
        h = hashlib.sha256(s.encode()).hexdigest()
        return random.Random(int(h[:16], 16))

    def _build_structured_feedback(self, question_text: str, user_answer: str, model_answer: str, raw_eval: dict) -> dict:
        """Produce a readable, actionable feedback envelope without changing
        the existing core keys. Returns extra fields to merge into the response.
        """
        score = int(raw_eval.get("score", 0))
        strengths = raw_eval.get("strengths") or []
        weaknesses = raw_eval.get("weaknesses") or []
        comparison = raw_eval.get("comparison") or {}
        skill_breakdown = raw_eval.get("skill_breakdown") or {}

        rng = self._deterministic_rng(question_text, user_answer, str(score))

        # priority actions derived from weaknesses
        action_map = {
            "metrics": "Add baseline + explicit target (e.g., +6% MAU in 8 weeks) and state how you'll measure it.",
            "segment": "Pick 1 prioritized customer segment and state why packaging helps them.",
            "experiment": "Define control vs variant, primary metric, MDE, sample size and timeline (e.g., 8 weeks).",
            "tradeoff": "State trade-offs (revenue vs MAU, support cost) and guardrails to monitor.",
            "example": "Include a 1–2 sentence STAR example with numbers (impact + metric).",
            "default": "Pick one testable hypothesis, one metric, one timeline, and one owner."
        }

        priority_actions = []
        for w in weaknesses[:4]:
            lw = w.lower()
            if "metric" in lw or "target" in lw or "baseline" in lw:
                priority_actions.append(action_map["metrics"])
            elif "segment" in lw or "customer" in lw:
                priority_actions.append(action_map["segment"])
            elif "experiment" in lw or "a/b" in lw or "experiment" in lw:
                priority_actions.append(action_map["experiment"])
            elif "trade-off" in lw or "tradeoffs" in lw or "trade off" in lw:
                priority_actions.append(action_map["tradeoff"])
            elif "example" in lw or "project" in lw:
                priority_actions.append(action_map["example"])
            else:
                priority_actions.append(action_map["default"])

        # de-duplicate while preserving order
        seen = set()
        pruned = []
        for a in priority_actions:
            if a not in seen:
                pruned.append(a)
                seen.add(a)

        # recommended_snippet: concise actionable answer derived from model_answer,
        # fall back to a simple template if model_answer is empty.
        rec = ""
        try:
            if model_answer and len(model_answer.strip()) > 40:
                # take the first 3 lines / sentences of the model answer as a short snippet
                import re
                sents = [s.strip() for s in re.split(r'(?<=[.?!])\s+', model_answer) if s.strip()]
                rec = " ".join(sents[:4])
                if len(rec) > 600:
                    rec = rec[:600].rsplit(' ', 1)[0] + '...'
            else:
                rec = "Start with a one-line recommendation, then 2–3 steps (approach), one concise example, and 1 metric target."
        except Exception:
            rec = "Start with a one-line recommendation, then 2–3 actionable steps and a measurable target."

        label = self._label_for_score(score)

        # Build a short comparison summary: top 3 missing model points (if present)
        missing = []
        try:
            missing = raw_eval.get("comparison", {}).get("missing_model_points", [])[:3]
        except Exception:
            missing = []

        extra = {
            "label": label,
            "recommended_snippet": rec,
            "priority_actions": pruned,
            "missing_model_points": missing,
        }
        return extra

    # Simple skill -> keywords map used when the model is not available to
    # produce differentiated feedback per skill (growth, UX, analytics, etc.).
    SKILL_KEYWORDS = {
        "growth": ["growth","activation","retention","acquisition","funnel","experiment","a/b","ab test","conversion","kpi","metric"],
        "user experience": ["ux","user research","usability","persona","wireframe","prototype","usability test","user interview","journey"],
        "analytics": ["sql","analytics","data","cohort","segmentation","dashboard","metric","kpi","funnel","measurement"],
        "vision": ["vision","roadmap","strategy","long-term","north star","product vision","mission"],
        "social impact": ["impact","sustainability","social","community","ethics","accessibility"],
        "product strategy": ["strategy","market","positioning","value proposition","differentiation","segmentation"],
        "execution": ["execution","launch","timeline","milestone","stakeholder","resourcing","delivery","implementation"]
    }

    def _skill_heuristic_eval(self, question_text: str, user_answer: str, model_answer: str, skills: list[str] | None = None) -> dict:
        """Produce a per-skill breakdown (score, strengths, weaknesses, feedback).

        Improvements vs earlier heuristic:
        - larger, deterministic per-skill variation to avoid uniform scores
        - clearer, templated feedback sections: "What went well", "Opportunities", "Next steps"
        - when embeddings are available use them with a stronger weight
        - produce a short example snippet tailored to the missing signals
        """
        ua = (user_answer or "").strip()
        ma = (model_answer or "").strip()
        ua_lower = ua.lower()
        ma_lower = ma.lower()
        ua_tokens = set([t for t in ua_lower.split() if t])
        ma_tokens = set([t for t in ma_lower.split() if t])

        skill_breakdown = {}
        candidates = skills if skills and len(skills) else list(self.SKILL_KEYWORDS.keys())

        # deterministic RNG seeded by question+user_answer to introduce reproducible variation
        seed_key = (question_text or "") + "|" + (ua or "")
        rnd = __import__('random').Random()
        rnd.seed(seed_key)

        # Prepare skill descriptions for embedding if available
        skill_texts = {sk: " ".join(self.SKILL_KEYWORDS.get(sk, [])) for sk in candidates}

        ua_vec = None
        model_vec = None
        skill_vecs = {}
        if EMBEDDING_AVAILABLE and _embed_model is not None:
            try:
                ua_vec = _embed_model.encode([ua], convert_to_numpy=True)[0]
                model_vec = _embed_model.encode([ma], convert_to_numpy=True)[0]
                texts = [skill_texts[sk] for sk in candidates]
                vecs = _embed_model.encode(texts, convert_to_numpy=True)
                for i, sk in enumerate(candidates):
                    skill_vecs[sk] = vecs[i]
            except Exception:
                ua_vec = None
                model_vec = None
                skill_vecs = {}

        # tip template bank to vary tips deterministically
        tip_bank = [
            "Open with a short recommendation, then 2–3 steps and a metric.",
            "Add a STAR example (Situation, Task, Action, Result) with a number.",
            "Mention how you'd measure success (dashboard, cohorts, A/B test).",
            "Call out one trade-off and the decision you made; interviewers like trade-off thinking.",
        ]

        for sk in candidates:
            key = sk
            keywords = self.SKILL_KEYWORDS.get(key.lower(), []) if isinstance(self.SKILL_KEYWORDS, dict) else self.SKILL_KEYWORDS.get(key, [])

            # semantic similarity signals (stronger weight when available)
            semantic_skill_sim = None
            if ua_vec is not None and sk in skill_vecs:
                try:
                    import numpy as _np
                    sdot = float(_np.dot(ua_vec, skill_vecs[sk]))
                    snorm = float(_np.linalg.norm(ua_vec) * _np.linalg.norm(skill_vecs[sk]))
                    semantic_skill_sim = sdot / snorm if snorm > 0 else 0.0
                except Exception:
                    semantic_skill_sim = None

            semantic_similarity = None
            if ua_vec is not None and model_vec is not None:
                try:
                    import numpy as _np
                    dot = float(_np.dot(ua_vec, model_vec))
                    norm = float(_np.linalg.norm(ua_vec) * _np.linalg.norm(model_vec))
                    semantic_similarity = dot / norm if norm > 0 else 0.0
                except Exception:
                    semantic_similarity = None

            # keyword coverage and overlap
            kw_present = sum(1 for kw in keywords if kw in ua_lower)
            kw_ratio = kw_present / max(1, len(keywords)) if keywords else 0.0
            overlap = len([w for w in ua_tokens if w in ma_tokens])
            overlap_ratio = overlap / max(1, len(ma_tokens)) if ma_tokens else 0.0

            # signals
            has_example = any(tok in ua_lower for tok in ["example", "project", "launched", "led", "for instance"]) or any(ch.isdigit() for ch in ua)
            has_metric = any(tok in ua_lower for tok in ["%", "percent", "nps", "kpi", "metric", "users", "retention", "growth"]) or any(ch.isdigit() for ch in ua)
            has_structure = any(kw in ua_lower for kw in ["i would", "approach", "steps", "first", "second", "then", "finally", "summary"]) or len(ua.split()) > 40

            # Compose a richer score: prefer embeddings when available and scale to produce wider spread
            if semantic_skill_sim is not None:
                semantic_component = min(80, int(semantic_skill_sim * 80))
            elif semantic_similarity is not None:
                semantic_component = min(60, int(semantic_similarity * 60))
            else:
                # fallback: use overlap_ratio as a proxy
                semantic_component = min(40, int(overlap_ratio * 40))

            kw_score = min(15, int(kw_ratio * 15))
            overlap_score = min(10, int(overlap_ratio * 10))
            example_score = 20 if has_example else 0
            metric_score = 10 if has_metric else 0
            structure_score = 5 if has_structure else 0

            base_score = semantic_component + kw_score + overlap_score + example_score + metric_score + structure_score

            # deterministic noise broader range to increase cross-skill diversity
            noise = rnd.uniform(-6.0, 6.0)
            score = int(max(0, min(100, base_score + noise)))

            # strengths, weaknesses, tips
            strengths = []
            weaknesses = []
            tips = []
            if kw_present > 0:
                strengths.append(f"Mentioned {kw_present} {('term' if kw_present==1 else 'terms')} related to {sk}.")
            if overlap_ratio > 0.2:
                strengths.append("Good topical alignment with the ideal answer.")
            if has_example:
                strengths.append("Used an example to illustrate your approach.")
            if has_metric:
                strengths.append("Included measurable outcomes or targets.")
            if has_structure:
                strengths.append("Clear structure or roadmap present.")

            if kw_present == 0:
                weaknesses.append(f"Could explicitly name 1–2 {sk} techniques or concepts.")
                tips.append(f"Try adding: {', '.join(keywords[:3])} and briefly say how you'd apply them.")
            if not has_example:
                weaknesses.append("No concise project/example — include a short STAR example.")
                tips.append("Write a 1–2 sentence example describing context, action, and result.")
            if not has_metric:
                weaknesses.append("No metrics — add a baseline and target to show impact.")
                tips.append("State what you'd measure (e.g., activation) and a target (e.g., +5–10%).")
            if not has_structure:
                weaknesses.append("Consider opening with a one-line summary before diving into steps.")
                tips.append("Start with: 'In short, I would ...' then list steps and finish with impact.")

            # choose a deterministic tip from bank for diversity
            chosen_tip = tip_bank[rnd.randint(0, len(tip_bank)-1)]

            # example snippet tailored to missing pieces
            example_snippet = ""
            if not has_example or not has_metric:
                example_snippet = (
                    f"Example: 'On project X, I led a 6-week experiment that improved activation by 8% (from 12% → 20%) by changing onboarding flows; tracked via funnel cohorts.'"
                )

            feedback_lines = [f"Skill: {sk} — {score}/100"]
            if strengths:
                feedback_lines.append("What went well:")
                for s in strengths:
                    feedback_lines.append(f"- {s}")
            if weaknesses:
                feedback_lines.append("Opportunities:")
                for w in weaknesses:
                    feedback_lines.append(f"- {w}")
            if tips:
                feedback_lines.append("Quick tips:")
                for t in tips[:2]:
                    feedback_lines.append(f"- {t}")
            feedback_lines.append(f"Try this: {chosen_tip}")

            skill_breakdown[sk] = {
                "score": int(score),
                "strengths": strengths,
                "weaknesses": weaknesses,
                "feedback": "\n".join(feedback_lines) + ("\n\n" + example_snippet if example_snippet else ""),
                "example_snippet": example_snippet,
            }

        return skill_breakdown

    def generate_answers_batch(self, questions: list[dict]) -> list:
        """
        Generate model answers for a batch of question dicts. Each question dict should
        include at least the 'question' key and optionally 'skills'. Returns a list of
        model answer strings matching the input order. Falls back to per-question
        generation when the LLM endpoint cannot provide a structured array.
        """
        try:
            parts = []
            for i, q in enumerate(questions):
                qq = q.get('question') or q.get('text') or ''
                sks = q.get('skills') or []
                sk = f"\nSkills: {', '.join(sks)}" if sks else ''
                parts.append(f"Q{i+1}: {qq}{sk}")

            prompt = (
                "You are an expert interview coach. For each numbered question below, produce a high-quality model answer.\n"
                "Output must be a single valid JSON array where each element is the model answer string for the corresponding question.\n\n"
                "Questions:\n" + "\n".join(parts) + "\n\nJSON:\n"
            )
            raw = self._query_ollama(prompt)
            if raw and raw.strip():
                try:
                    data = json.loads(raw)
                    if isinstance(data, list) and len(data) == len(questions):
                        return [str(x) for x in data]
                except Exception:
                    # try to extract JSON array substring
                    start = raw.find('[')
                    end = raw.rfind(']')
                    if start != -1 and end != -1 and end > start:
                        try:
                            data = json.loads(raw[start:end+1])
                            if isinstance(data, list) and len(data) == len(questions):
                                return [str(x) for x in data]
                        except Exception:
                            pass

            # If LLM didn't return structured output, respect force_llm
            if getattr(self, 'force_llm', False):
                raise Exception('LLM did not return structured batch answers and LLM_FORCE is enabled')

        except Exception as e:
            print(f"[AIService generate_answers_batch error] {e}")

        # Fallback: call generate_answer per question
        out = []
        # Try wrapper per-question generation first (structured single-answer endpoint)
        try:
            for q in questions:
                qa = q.get('question') or q.get('text') or ''
                sk = q.get('skills') or []
                a = self._wrapper_generate_answer(qa, sk, model='llama3')
                if not a:
                    # fallback to existing generate_answer which may call LLM directly
                    a = self.generate_answer(qa, sk)
                out.append(a or self._fallback_model_answer(qa, sk))
            return out
        except Exception as e:
            print(f"[AIService generate_answers_batch wrapper fallback error] {e}")

        # Final fallback: per-question generate_answer
        out = []
        for q in questions:
            qa = q.get('question') or q.get('text') or ''
            sk = q.get('skills') or []
            try:
                a = self.generate_answer(qa, sk)
            except Exception:
                a = self._fallback_model_answer(qa, sk)
            out.append(a)
        return out

    def generate_answer(self, question_text: str, skills: list | None = None) -> str:
        """
        Generate a model answer for a given interview question. Prefer concise, structured
        high-quality answers. This tries the LLM and falls back to a deterministic template
        when the LLM is unavailable (unless force_llm is enabled, in which case an
        exception is raised).
        """
        key = (question_text or "").strip()
        try:
            if key in self._answer_cache:
                return self._answer_cache[key]

            skills_text = "\nSkills to emphasize: " + ", ".join(skills) if skills else ""
            prompt = (
                "You are an expert interview coach and candidate.\n"
                "Given the question below, produce a high-quality sample answer suitable for a mid-to-senior product manager. Use a clear structure (summary, approach, example, metrics).\n\n"
                "Question:\n" + question_text + "\n\n" + skills_text + "\n\nAnswer:\n"
            )

            # Prefer using the wrapper's generate endpoint with local llama3 model if available
            try:
                ans = self._wrapper_generate_answer(question_text, skills, model='llama3')
            except Exception:
                ans = ""
            if not ans:
                ans = self._query_ollama(prompt)
            if not ans or not ans.strip():
                if getattr(self, 'force_llm', False):
                    raise Exception("LLM returned empty response and LLM_FORCE is enabled")
                skills_text = ", ".join(skills) if skills else ""
                ans = (
                    f"Summary:\nProvide a concise recommendation and primary outcome.\n\n"
                    f"Approach:\n1) Clarify goals and target users. 2) Break problem into key pillars (user research, MVP, metrics).\n"
                    f"Example:\nDescribe a specific project example: timeline, decisions made, trade-offs, stakeholders involved, and measurable outcomes.\n\n"
                    f"Metrics & Impact:\nList the metrics you would track (e.g., activation, retention, NPS) and target improvements.\n\n"
                    f"Skills emphasized: {skills_text}."
                )

            # Cache non-trivial answers
            try:
                if ans and len(ans) > 20:
                    self._answer_cache[key] = ans
            except Exception:
                pass

            return ans
        except Exception as e:
            print(f"[AIService generate_answer error] {e}")
            # final fallback deterministic answer
            return self._fallback_model_answer(question_text, skills)

    def evaluate_answer(self, question_text: str, user_answer: str, model_answer: str) -> dict:
        """
        Ask the model to compare the user's answer to the model answer and return a JSON
        summary with a numeric score (0-100), strengths, weaknesses and suggested improvements.
        """
        # Prefer using the LLM to produce a structured, rich JSON evaluation.
        # We'll try up to two LLM calls before falling back to the heuristic evaluator.
        try:
            if not model_answer or not model_answer.strip():
                model_answer = self.generate_answer(question_text)

            eval_prompt = (
                "You are an expert interview evaluator. Compare the USER_ANSWER to the IDEAL_ANSWER for the question below.\n"
                "Produce ONLY a single valid JSON object (no extra text) with the following structure:\n"
                "{\n"
                "  \"similarity_score\": <float 0.0-1.0>,\n"
                "  \"score\": <int 0-100>,\n"
                "  \"ideal_answer\": \"<string>\",\n"
                "  \"suggestions\": {\n"
                "    \"rating\": \"good|satisfactory|needs_improvement\",\n"
                "    \"feedback\": {\n"
                "      \"comparison\": \"short human-readable comparison sentence\",\n"
                "      \"strengths\": [\"...\"],\n"
                "      \"improvements\": [\"...\"]\n"
                "    }\n"
                "  }\n"
                "}\n\n"
                "Guidance: keep feedback short and actionable (1-3 bullets per section). Similarity_score should be a decimal between 0 and 1. Score should be integer 0-100 roughly similarity_score*100 with professional judgment. Do NOT include internal notes or technical terms like 'fuzzy' or 'heuristic'.\n\n"
                "Question:\n" + question_text + "\n\n"
                "IDEAL_ANSWER:\n" + (model_answer or "") + "\n\n"
                "USER_ANSWER:\n" + (user_answer or "") + "\n\n"
                "JSON:\n"
            )

            raw = self._query_ollama(eval_prompt)
            data = {}
            if raw and raw.strip():
                try:
                    data = json.loads(raw)
                except Exception:
                    # try to extract the first JSON object substring
                    start = raw.find('{')
                    end = raw.rfind('}')
                    if start != -1 and end != -1 and end > start:
                        try:
                            data = json.loads(raw[start:end+1])
                        except Exception:
                            data = {}

            # If we didn't get a structured response, retry once with a simpler prompt
            if not data:
                retry_prompt = (
                    "Provide ONLY a JSON object with keys: similarity_score (0-1 float), score (0-100 int), ideal_answer (string), suggestions (object with rating and feedback).\n"
                    "Question:\n" + question_text + "\nIDEAL_ANSWER:\n" + (model_answer or "") + "\nUSER_ANSWER:\n" + (user_answer or "") + "\nJSON:\n"
                )
                raw2 = self._query_ollama(retry_prompt)
                if raw2 and raw2.strip():
                    try:
                        data = json.loads(raw2)
                    except Exception:
                        start = raw2.find('{')
                        end = raw2.rfind('}')
                        if start != -1 and end != -1 and end > start:
                            try:
                                data = json.loads(raw2[start:end+1])
                            except Exception:
                                data = {}

            # If we have structured data, normalize it to the expected shape
            if data and isinstance(data, dict):
                similarity = float(data.get('similarity_score') or 0.0)
                score = int(data.get('score') or round(similarity * 100))
                ideal = data.get('ideal_answer') or model_answer
                suggestions = data.get('suggestions') or {}
                feedback_obj = suggestions.get('feedback') if isinstance(suggestions, dict) else None
                strengths = feedback_obj.get('strengths') if feedback_obj and isinstance(feedback_obj.get('strengths'), list) else []
                improvements = feedback_obj.get('improvements') if feedback_obj and isinstance(feedback_obj.get('improvements'), list) else []
                comparison = feedback_obj.get('comparison') if feedback_obj and isinstance(feedback_obj.get('comparison'), str) else (suggestions.get('feedback') if isinstance(suggestions.get('feedback'), str) else '')
                feedback_text = comparison

                return {
                    'score': max(0, min(100, int(score))),
                    'strengths': strengths,
                    'weaknesses': improvements,
                    'feedback': feedback_text,
                    'similarity_score': similarity,
                    'ideal_answer': ideal,
                    'suggestions': suggestions,
                }
            # If the LLM could not produce structured output, respect force_llm setting.
            if getattr(self, 'force_llm', False):
                raise Exception("LLM did not return structured evaluation and LLM_FORCE is enabled")
        except Exception as e:
            print(f"[AIService evaluate_answer LLM error] {e}")
        # If structured LLM output was not produced, try the wrapper's evaluate endpoint
        try:
            # Use qwen2:7b-instruct for evaluation (preferred for scoring/feedback)
            wrapper_resp = self._wrapper_evaluate_answer(question_text, user_answer, model_answer, model='qwen2:7b-instruct')
            # wrapper returns a dict with similarity_score, score, strengths, improvements, feedback
            if wrapper_resp and isinstance(wrapper_resp, dict):
                sim = float(wrapper_resp.get('similarity_score') or wrapper_resp.get('score', 0) / 100.0 or 0.0)
                score = int(wrapper_resp.get('score') or round(sim * 100))
                strengths = wrapper_resp.get('strengths') or wrapper_resp.get('strengths', [])
                improvements = wrapper_resp.get('improvements') or wrapper_resp.get('weaknesses') or []
                feedback_text = wrapper_resp.get('feedback') or wrapper_resp.get('comparison') or ''
                return {
                    'score': max(0, min(100, int(score))),
                    'strengths': strengths,
                    'weaknesses': improvements,
                    'feedback': feedback_text,
                    'similarity_score': float(sim),
                    'ideal_answer': wrapper_resp.get('ideal_answer') or model_answer,
                    'suggestions': wrapper_resp.get('suggestions') or {},
                }
        except Exception as e:
            print(f"[AIService evaluate_answer wrapper fallback error] {e}")

        # Heuristic fallback only if explicitly allowed via env var
        try:
            import os
            allow_heur = os.environ.get('ALLOW_HEURISTIC', '1') == '1'
            if allow_heur:
                return self._heuristic_evaluate(question_text, user_answer, model_answer)
            else:
                # If heuristics are disabled, return a conservative structured response
                # indicating the evaluation could not be completed by the LLM.
                return {
                    'score': 0,
                    'strengths': [],
                    'weaknesses': ['Evaluation unavailable - model did not return structured output.'],
                    'feedback': 'Evaluation unavailable: LLM did not provide structured output. Try pulling a local model or enable ALLOW_HEURISTIC=1 for fallback.',
                    'similarity_score': 0.0,
                    'ideal_answer': model_answer,
                    'suggestions': {},
                }
        except Exception as e:
            print(f"[AIService evaluate_answer final fallback error] {e}")
            return {'score': 0, 'strengths': [], 'weaknesses': [], 'feedback': 'Evaluation failed.'}

    def evaluate_answers_batch(self, items: list[dict]) -> list[dict]:
        """
        Attempt to evaluate multiple user answers in one shot. Expects items to be a list
        of dicts with keys: 'question' (text), 'user_answer' (text), optionally 'skills'.
        Returns a list of dicts with keys: model_answer, score, strengths, weaknesses, feedback.
        If the batch attempt fails, returns an empty list to signal fallback.
        """
        try:
            parts = []
            for i, it in enumerate(items):
                q = it.get("question") or ""
                ua = it.get("user_answer") or ""
                skills = it.get("skills") or []
                sk = f"\nSkills: {', '.join(skills)}" if skills else ""
                parts.append(f"Q{i+1}: {q}{sk}\nUSER_ANSWER: {ua}")

            prompt = (
                "You are an expert interview evaluator. For each numbered question below, you will be given the QUESTION and the USER_ANSWER.\n"
                "For each item, produce two things: (1) a concise IDEAL model answer, and (2) a short JSON evaluation object with keys: score (0-100), strengths (array of strings), weaknesses (array of strings), feedback (string).\n"
                "IMPORTANT: OUTPUT MUST BE a single valid JSON array ONLY. Do NOT include any extra commentary or surrounding text. Each array element must be an object with keys exactly: model_answer, score, strengths, weaknesses, feedback.\n\n"
                "Items:\n" + "\n".join(parts) + "\n\nJSON:\n"
            )

            raw = self._query_ollama(prompt)
            print(f"[AIService evaluate_answers_batch] Raw response (first 200 chars): {raw[:200] if raw else 'EMPTY'}")
            print(f"[AIService evaluate_answers_batch] Items count: {len(items)}")
            try:
                data = json.loads(raw) if raw and raw.strip() else None
                print(f"[AIService evaluate_answers_batch] Parsed data type: {type(data)}, length: {len(data) if isinstance(data, list) else 'N/A'}")
                if isinstance(data, list) and len(data) == len(items):
                    out = []
                    for obj in data:
                        out.append({
                            "model_answer": obj.get("model_answer") or obj.get("ideal_answer") or "",
                            "score": int(obj.get("score") or 0) if obj.get("score") is not None else 0,
                            "strengths": obj.get("strengths") or [],
                            "weaknesses": obj.get("weaknesses") or [],
                            "feedback": obj.get("feedback") or "",
                        })
                    return out
            except Exception:
                # ignore and fall back below
                pass

            # If batch attempt failed or returned nothing, return an empty list so
            # the router will fall back to per-question generation + evaluation
            return []
        except Exception as e:
            print(f"[AIService evaluate_answers_batch error] {e}")
            return []

    async def extract_details_from_jd(self, jd_text: str) -> dict:
        try:
            full_prompt = SYSTEM_PROMPT + "\n\n" + jd_text
            raw = self._query_ollama(full_prompt)
            try:
                data = json.loads(raw)
            except Exception:
                start, end = raw.find("{"), raw.rfind("}") + 1
                data = json.loads(raw[start:end]) if start != -1 else {}

            company = self._find_best_match(data.get("company_name", ""), VALID_COMPANIES)
            years_of_experience = data.get("years_of_experience", "6-10")
            # Normalize years_of_experience to standard buckets
            if years_of_experience not in ("0-2", "3-5", "6-10", "10+"):
                years_of_experience = "6-10"  # Default
            level = self._find_best_match(data.get("level", ""), VALID_LEVELS)

            return {"company_name": company, "years_of_experience": years_of_experience, "level": level}
        except Exception as e:
            print(f"[AIService Error] {e}")
            return {"company_name": "Unknown Company", "years_of_experience": "6-10", "level": "Strategic"}

ai_service = AIService()

