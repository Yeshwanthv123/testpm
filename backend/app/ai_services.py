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

2️⃣ role — must be one of these:
{VALID_ROLES}

3️⃣ level — must be one of these:
{VALID_LEVELS}

Respond ONLY in valid JSON:
{{"company_name": "...", "role": "...", "level": "..."}}.
"""

class AIService:
    def __init__(self):
        # Allow configuring the LLM HTTP base URL via env var so the service
        # can point to an external Ollama-like endpoint or an in-repo stub.
        self.llm_api_url = os.environ.get("LLM_API_URL", "http://localhost:11434").rstrip("/")
        self.model = self._get_available_model()
        # simple in-memory cache for generated model answers keyed by question text
        self._answer_cache: dict = {}
        print(f"[AIService] Using LLM endpoint: {self.llm_api_url}, model: {self.model}")

    def _get_available_model(self):
        try:
            r = requests.get(f"{self.llm_api_url}/api/tags", timeout=5)
            models = r.json().get("models", [])
            if models:
                for m in models:
                    if "llama3" in m["name"]:
                        return m["name"]
                return models[0]["name"]
        except Exception:
            pass
        return "llama3"

    def _query_ollama(self, prompt: str) -> str:
        try:
            response = requests.post(
                f"{self.llm_api_url}/api/generate",
                json={"model": self.model, "prompt": prompt, "stream": False},
                timeout=120,
            )
            return response.json().get("response", "").strip()
        except Exception as e:
            print(f"[Ollama error] {e}")
            return ""

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

        # add a little deterministic variation to increase score diversity
        noise = rnd.uniform(-6.0, 6.0)
        score = int(max(0, min(100, raw + noise)))

        # build readable strengths/weaknesses and actionable next steps
        strengths = []
        weaknesses = []
        next_steps = []
        if has_example:
            strengths.append("You included a concrete example which helps demonstrate your experience.")
        if has_metrics:
            strengths.append("You referenced measurable outcomes which helps validate impact.")
        if has_summary:
            strengths.append("Your answer had a clear structure or roadmap.")

        if not has_example:
            weaknesses.append("No concise example — add a 1–2 sentence STAR example to show execution.")
            next_steps.append("Pick one relevant project and summarize Situation, Action, and Result with a number.")
        if not has_metrics:
            weaknesses.append("Missing concrete metrics — add baselines and targets to make impact tangible.")
            next_steps.append("State the metric you'll track and the target change (e.g., +8% activation).")
        if not has_summary:
            weaknesses.append("Answer lacked a short opening summary — start with a single-sentence recommendation.")
            next_steps.append("Open with one sentence that clearly states your recommendation and main trade-off.")

        # Comparison hints: missing model points
        missing_points = []
        try:
            ma_sentences = [s.strip() for s in __import__('re').split(r"(?<=[.?!])\s+", ma) if s.strip()]
            for s in ma_sentences[:5]:
                # if few words from model sentence appear in UA, mark as missing
                words = set([w for w in s.lower().split() if w])
                if len(words & tokens_ua) / max(1, len(words)) < 0.2:
                    missing_points.append(s)
        except Exception:
            missing_points = []

        # Compose human-friendly feedback
        feedback_lines = []
        feedback_lines.append(f"Score: {score}/100 — {('Strong' if score>=75 else 'Satisfactory' if score>=45 else 'Needs work')}")
        if strengths:
            feedback_lines.append("What you did well:")
            for s in strengths:
                feedback_lines.append(f"- {s}")
        if weaknesses:
            feedback_lines.append("What to improve:")
            for w in weaknesses:
                feedback_lines.append(f"- {w}")
        if next_steps:
            feedback_lines.append("Concrete next steps:")
            for n in next_steps:
                feedback_lines.append(f"- {n}")
        if missing_points:
            feedback_lines.append("Points from the ideal answer you may have missed:")
            for p in missing_points[:3]:
                feedback_lines.append(f"- {p}")
        feedback_lines.append("Tip: " + tip)

        return {
            "score": int(score),
            "strengths": strengths,
            "weaknesses": weaknesses,
            "feedback": "\n".join(feedback_lines),
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

    def generate_answer(self, question_text: str, skills: list | None = None) -> str:
        """
        Generate a model answer for a given interview question. Prefer concise, modern
        high-quality interview answers that demonstrate frameworks, structure, and examples.
        """
        try:
            skills_text = "\nSkills to emphasize: " + ", ".join(skills) if skills else ""
            key = (question_text or "").strip()
            if key in self._answer_cache:
                return self._answer_cache[key]
            prompt = (
                "You are an expert interview coach and candidate.\n"
                "Given the question below, produce a high-quality sample answer suitable for a mid-to-senior product manager. Use a clear structure (summary, approach, examples, metrics).\n\n"
                "Question:\n" + question_text + "\n\n" + skills_text + "\n\nAnswer:\n"
            )
            ans = self._query_ollama(prompt)
            # If LLM is unavailable or returned an empty response, provide a simple
            # deterministic fallback answer so the system can still evaluate and
            # provide feedback even offline.
            if not ans or len(ans.strip()) == 0:
                skills_text = ", ".join(skills) if skills else ""
                ans = (
                    f"Structured answer: Summary -> Approach -> Example -> Metrics.\n"
                    f"Question: {question_text}\n"
                    f"Skills to emphasize: {skills_text}\n\n"
                    "Example: I would start by clarifying goals, define metrics, run a small-scale experiment, "
                    "iterate based on results, and measure impact using retention and NPS."
                )
            try:
                # cache short non-empty answers
                if ans and len(ans) > 10:
                    self._answer_cache[key] = ans
            except Exception:
                pass
            return ans
        except Exception as e:
            print(f"[AIService generate_answer error] {e}")
            return ""

    def generate_answers_batch(self, questions: list[dict]) -> list[str]:
        """
        Attempt to generate model answers for a list of question dicts in a single batch
        call. The `questions` list should contain dicts with keys 'question' and
        optionally 'skills' (list). Returns a list of answer strings in same order.
        Falls back to individual generation on failure.
        """
        try:
            # Build a prompt asking for JSON list of answers
            parts = []
            for i, q in enumerate(questions):
                qtext = q.get("question") or q.get("text") or ""
                skills = q.get("skills")
                sk_text = f"\nSkills: {', '.join(skills)}" if skills else ""
                parts.append(f"Q{i+1}: {qtext}{sk_text}")

            prompt = (
                "You are an expert interview coach. For each numbered question below, produce a concise, high-quality model answer.\n"
                "IMPORTANT: OUTPUT MUST BE a valid JSON array of strings ONLY. Do NOT include any extra commentary or surrounding text. The nth element must be the model answer for question n.\n\n"
                "Questions:\n" + "\n".join(parts) + "\n\nJSON:\n"
            )

            raw = self._query_ollama(prompt)
            try:
                data = json.loads(raw)
                if isinstance(data, list):
                    return [str(x) for x in data]
            except Exception:
                pass

            # fallback: generate individually (ensure non-empty answers)
            answers = []
            for q in questions:
                qa = q.get("question") or q.get("text") or ""
                sk = q.get("skills") or []
                ans = self.generate_answer(qa, sk)
                if not ans or not ans.strip():
                    # deterministic fallback if model unavailable
                    skills_text = ", ".join(sk) if sk else ""
                    ans = (
                        f"Structured answer: Summary -> Approach -> Example -> Metrics.\n"
                        f"Question: {qa}\n"
                        f"Skills to emphasize: {skills_text}\n\n"
                        "Example: I would start by clarifying goals, define metrics, run a small experiment, iterate based on results, and measure impact using retention and NPS."
                    )
                answers.append(ans)
            return answers
        except Exception as e:
            print(f"[AIService generate_answers_batch error] {e}")
            # fallback individually
            return [self.generate_answer(q.get("question") or q.get("text") or "", q.get("skills")) for q in questions]

    def evaluate_answer(self, question_text: str, user_answer: str, model_answer: str) -> dict:
        """
        Ask the model to compare the user's answer to the model answer and return a JSON
        summary with a numeric score (0-100), strengths, weaknesses and suggested improvements.
        """
        try:
            prompt = (
                "You are an expert interview evaluator. Compare the USER_ANSWER to the IDEAL_ANSWER for the question below.\n"
                "Score the USER_ANSWER from 0-100 based on completeness, structure, relevance to the question, use of metrics/examples, and alignment with modern interview best practices.\n"
                "IMPORTANT: OUTPUT MUST BE valid JSON ONLY. Do NOT include any extra commentary or surrounding text. The JSON must contain these keys exactly: score (integer 0-100), strengths (array of strings), weaknesses (array of strings), feedback (string).\n\n"
                "Question:\n" + question_text + "\n\n"
                "IDEAL_ANSWER:\n" + model_answer + "\n\n"
                "USER_ANSWER:\n" + user_answer + "\n\n"
                "JSON:\n"
            )
            raw = self._query_ollama(prompt)
            data = {}
            try:
                if raw and raw.strip():
                    try:
                        data = json.loads(raw)
                    except Exception:
                        start, end = raw.find("{"), raw.rfind("}") + 1
                        if start != -1 and end != -1:
                            data = json.loads(raw[start:end])
                else:
                    data = {}
            except Exception:
                data = {}

            # If the LLM didn't return a structured evaluation, fall back to a
            # simple heuristic: score by overlap and length.
            try:
                score = int(data.get("score") or 0)
            except Exception:
                score = 0

            strengths = data.get("strengths") or []
            weaknesses = data.get("weaknesses") or []
            feedback = data.get("feedback") or ""

            if score == 0 and (not strengths and not weaknesses and not feedback):
                # Heuristic scoring: combine content length and word overlap with model answer
                ua_words = set((user_answer or "").lower().split())
                ma_words = set((model_answer or "").lower().split())
                overlap = len([w for w in ua_words if w and w in ma_words])
                ua_len = max(1, len((user_answer or "").split()))
                # overlap ratio scaled to 60 points, length gives up to 40 points
                overlap_score = 0
                if ma_words:
                    overlap_score = min(60, int((overlap / max(1, len(ma_words))) * 60))
                length_score = min(40, int((ua_len / 50) * 40)) if ua_len else 0
                heur_score = max(0, min(100, overlap_score + length_score))
                score = heur_score

                # More descriptive strengths/weaknesses based on heuristics
                strengths = []
                weaknesses = []
                if overlap_score >= 40:
                    strengths.append("High topical alignment with the ideal answer; covered major points.")
                elif overlap_score >= 20:
                    strengths.append("Touched on relevant topics from the ideal answer; good breadth.")
                else:
                    if ua_len > 10:
                        strengths.append("Clear approach or structure present in the response.")

                # Detect presence of concrete metrics/examples
                ua_lower = (user_answer or "").lower()
                has_metric = any(tok in ua_lower for tok in ["%","percent","nps","metric","kpi","rate","users","increase","decrease","conversion"]) 
                has_example = any(tok in ua_lower for tok in ["example","for instance","we did","we increased","in one project","such as"]) 
                if not has_metric:
                    weaknesses.append("Lacks concrete metrics — add measurable outcomes (e.g., % increase, NPS, retention).")
                if not has_example:
                    weaknesses.append("Few concrete examples — include a specific project/example to illustrate impact.")

                # Compose feedback blending heuristics
                feedback_parts = []
                feedback_parts.append(f"Heuristic evaluation: topical coverage {overlap_score}/60, thoroughness {length_score}/40.")
                if strengths:
                    feedback_parts.append("Strengths: " + "; ".join(strengths))
                if weaknesses:
                    feedback_parts.append("Opportunities: " + "; ".join(weaknesses))
                feedback_parts.append("Tip: Structure answers with Summary → Approach → Example → Metrics.")
                feedback = "\n".join(feedback_parts)

            # Build a compact comparison summary to help the user see what was
            # present vs missing relative to the ideal answer.
            try:
                import difflib
                ua_words = [w for w in (user_answer or "").lower().split() if w]
                ma_words = [w for w in (model_answer or "").lower().split() if w]
                overlap_words = sorted(list(set(ua_words) & set(ma_words)))[:50]

                # sentence-level similarity: for each model sentence, find best match in user sentences
                ma_sents = [s.strip() for s in __import__('re').split(r"(?<=[.?!])\s+", model_answer or "") if s.strip()]
                ua_sents = [s.strip() for s in __import__('re').split(r"(?<=[.?!])\s+", user_answer or "") if s.strip()]
                sent_matches = []
                for ms in ma_sents[:6]:
                    best = 0.0
                    best_text = ""
                    for us in ua_sents:
                        try:
                            r = difflib.SequenceMatcher(None, ms.lower(), us.lower()).ratio()
                            if r > best:
                                best = r
                                best_text = us
                        except Exception:
                            continue
                    sent_matches.append({"model_sentence": ms, "best_user_sentence": best_text, "similarity": round(best, 3)})

                # missing model phrases (short list)
                missing = []
                for ms in ma_sents[:6]:
                    words = set([w for w in ms.lower().split() if w])
                    if len(words & set(ua_words)) / max(1, len(words)) < 0.2:
                        missing.append(ms)
                comparison = {
                    "overlap_words": overlap_words,
                    "sentence_matches": sent_matches,
                    "missing_model_points": missing[:6],
                }
            except Exception:
                comparison = {"overlap_words": [], "sentence_matches": [], "missing_model_points": []}

            raw = {
                "score": max(0, min(100, int(score))),
                "strengths": strengths,
                "weaknesses": weaknesses,
                "feedback": feedback,
                # include a per-skill heuristic breakdown for richer UI
                "skill_breakdown": self._skill_heuristic_eval(question_text, user_answer, model_answer, skills=None),
                "comparison": comparison,
            }

            # Build a structured, user-friendly feedback envelope while preserving
            # existing keys so the frontend is unaffected. This adds: label,
            # recommended_snippet, and priority_actions.
            try:
                structured = self._build_structured_feedback(question_text, user_answer, model_answer, raw)
                # merge structured fields into raw (do not overwrite core keys)
                raw.update({k: v for k, v in structured.items() if k not in raw})
            except Exception:
                # if building structured feedback fails, return raw result
                pass

            return raw
        except Exception as e:
            print(f"[AIService evaluate_answer error] {e}")
            return {"score": 0, "strengths": [], "weaknesses": [], "feedback": "Evaluation failed."}

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
            try:
                data = json.loads(raw) if raw and raw.strip() else None
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
            role = self._find_best_match(data.get("role", ""), VALID_ROLES)
            level = self._find_best_match(data.get("level", ""), VALID_LEVELS)

            return {"company_name": company, "role": role, "level": level}
        except Exception as e:
            print(f"[AIService Error] {e}")
            return {"company_name": "Unknown Company", "role": "PM", "level": "Strategic"}

ai_service = AIService()

