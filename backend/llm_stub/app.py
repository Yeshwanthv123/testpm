from flask import Flask, request, jsonify
from flask_cors import CORS
import re
import json

# Optional embeddings (sentence-transformers) to compute semantic similarity.
EMBEDDING_AVAILABLE = False
_embed_model = None
try:
    from sentence_transformers import SentenceTransformer
    _embed_model = SentenceTransformer('all-MiniLM-L6-v2')
    EMBEDDING_AVAILABLE = True
    print('[llm_stub] sentence-transformers loaded')
except Exception:
    EMBEDDING_AVAILABLE = False
    _embed_model = None

app = Flask(__name__)
CORS(app)

# Listen on port 11434 to match Ollama's default port
PORT = 11434

# Simple lightweight Ollama-like stub that returns deterministic, structured
# responses based on heuristic parsing of the incoming prompt. This is intended
# only for offline/demo use where a real LLM is not available.


@app.route('/api/tags', methods=['GET'])
def tags():
    # report available "models" so AIService._get_available_model can pick one
    return jsonify({"models": [{"name": "llama3"}]})


@app.route('/api/version', methods=['GET'])
def version():
    # Simple health/version endpoint to emulate an LLM service
    try:
        return jsonify({"ok": True, "service": "llm_stub", "version": "1.0.0", "models": ["llama3"]})
    except Exception:
        return jsonify({"ok": False}), 500


def fallback_model_answer(question_text, skills=None):
    skills_text = ", ".join(skills) if skills else "product thinking, execution, and measurement"
    return (
        f"Summary:\nProvide a concise recommendation and primary outcome.\n\n"
        f"Approach:\n1) Clarify goals and target users. 2) Break problem into key pillars (user research, MVP, metrics).\n"
        f"3) Design experiments and success criteria. 4) Iterate with cross-functional partners.\n\n"
        f"Example:\nDescribe a specific project example: timeline, decisions made, trade-offs, stakeholders involved, and measurable outcomes.\n\n"
        f"Metrics & Impact:\nList the metrics you would track (e.g., activation, retention, NPS) and target improvements.\n\n"
        f"Skills emphasized: {skills_text}.\n"
    )


def heuristic_eval(model_answer, user_answer):
    """
    Improved heuristic evaluator.

    Features:
    - token overlap and difflib ratio for semantic similarity
    - length-based contribution
    - deterministic small variation per question (seeded by model_answer+user_answer)
    - per-skill breakdown using simple keyword maps
    Returns a dict with overall score, per-skill scores, strengths, weaknesses and feedback.
    """
    ua = (user_answer or "").lower()
    ma = (model_answer or "").lower()

    # token sets
    ua_tokens = [t for t in re.split(r"\W+", ua) if t]
    ma_tokens = [t for t in re.split(r"\W+", ma) if t]
    ua_set = set(ua_tokens)
    ma_set = set(ma_tokens)

    # overlap ratio (0..1)
    overlap = len(ua_set & ma_set) / max(1, len(ma_set))

    # difflib sequence similarity for fuzzy matching
    seq_ratio = 0.0
    try:
        seq_ratio = __import__('difflib').SequenceMatcher(None, ua, ma).ratio()
    except Exception:
        seq_ratio = 0.0

    # semantic similarity via embeddings when available
    semantic_similarity = None
    if EMBEDDING_AVAILABLE and _embed_model is not None:
        try:
            import numpy as _np
            ua_vec = _embed_model.encode([ua], convert_to_numpy=True)[0]
            ma_vec = _embed_model.encode([ma], convert_to_numpy=True)[0]
            dot = float(_np.dot(ua_vec, ma_vec))
            norm = float(_np.linalg.norm(ua_vec) * _np.linalg.norm(ma_vec))
            semantic_similarity = dot / norm if norm > 0 else 0.0
        except Exception:
            semantic_similarity = None

    # length score (caps at 1.0 equivalent to full contribution)
    ua_len = max(0, len(ua_tokens))
    length_ratio = min(1.0, ua_len / 50.0)

    # skill keyword map / descriptions - used for fallback if embeddings unavailable
    skill_keywords = {
        "Product Strategy": ["strategy", "roadmap", "positioning", "segment", "vision"],
        "Execution": ["launch", "release", "iterat", "build", "deliver", "execute"],
        "Leadership": ["stakeholder", "align", "lead", "owner", "collaborat"],
        "Analytics": ["metric", "kpi", "nps", "cohort", "retention", "activation"],
        "Communication": ["message", "announce", "share", "update", "presentation"],
        "Vision": ["north star", "vision", "long term", "goal", "objective"],
    }

    skill_scores = {}
    # If embeddings are available, compute semantic similarity between user answer
    # and each skill description for more robust per-skill scoring.
    if EMBEDDING_AVAILABLE and _embed_model is not None:
        try:
            ua_vec = _embed_model.encode([ua], convert_to_numpy=True)[0]
            ma_vec = _embed_model.encode([ma], convert_to_numpy=True)[0]
            # precompute skill vectors
            skill_vecs = {}
            skill_texts = {s: " ".join(kws) for s, kws in skill_keywords.items()}
            texts = [skill_texts[s] for s in skill_texts.keys()]
            vecs = _embed_model.encode(texts, convert_to_numpy=True)
            for i, s in enumerate(skill_texts.keys()):
                skill_vecs[s] = vecs[i]

            # compute cosine similarities
            import numpy as _np
            # small deterministic RNG for per-skill noise
            seed_key_local = (ma + "|" + ua)
            rng_local = __import__('random').Random()
            rng_local.seed(seed_key_local + "|skill")
            for s, vec in skill_vecs.items():
                dot = float(_np.dot(ua_vec, vec))
                norm = float(_np.linalg.norm(ua_vec) * _np.linalg.norm(vec))
                sim = dot / norm if norm > 0 else 0.0
                # map similarity (0..1) to 0..100 scale and add small deterministic noise
                noisy = sim * 100 + rng_local.uniform(-2.0, 2.0)
                skill_scores[s] = int(min(100, max(0, noisy)))
        except Exception:
            # fallback to keyword coverage below
            skill_scores = {}

    if not skill_scores:
        for skill, keywords in skill_keywords.items():
            kw_set = set(keywords)
            # how much of model_answer relates to this skill
            ma_kw_hits = len([t for t in ma_tokens if any(k in t for k in keywords)])
            ua_kw_hits = len([t for t in ua_tokens if any(k in t for k in keywords)])
            # coverage ratio relative to model keywords (0..1)
            coverage = min(1.0, ua_kw_hits / max(1, ma_kw_hits)) if ma_kw_hits > 0 else (0.5 if ua_kw_hits > 0 else 0.0)
            skill_scores[skill] = int(coverage * 100)

    # combine signals with weights and widen semantic contribution for variability
    if semantic_similarity is not None:
        raw_score = overlap * 25.0 + semantic_similarity * 60.0 + length_ratio * 15.0
    else:
        raw_score = overlap * 50.0 + seq_ratio * 25.0 + length_ratio * 25.0

    # deterministic variation per question (broader range than before)
    seed_key = (ma + "|" + ua)
    rng = __import__('random').Random()
    rng.seed(seed_key)
    noise = rng.uniform(-5.0, 5.0)

    score = max(0.0, min(100.0, raw_score + noise))

    strengths = []
    weaknesses = []
    next_steps = []

    if overlap >= 0.4 or seq_ratio >= 0.45:
        strengths.append("Good topical alignment with the ideal answer; covered major points.")
    elif overlap >= 0.2 or seq_ratio >= 0.3:
        strengths.append("Touched on relevant topics from the ideal answer; decent coverage.")
    else:
        if ua_len > 10:
            strengths.append("Provided a clear approach or structure.")

    has_metric = any(tok in ua for tok in ["%", "percent", "nps", "metric", "kpi", "rate", "users", "increase", "decrease", "conversion"]) 
    has_example = any(tok in ua for tok in ["example", "for instance", "we did", "we increased", "in one project", "such as"]) 
    if not has_metric:
        weaknesses.append("Lacks concrete metrics — add measurable outcomes (e.g., % increase, NPS).")
        next_steps.append("Add a baseline and a target for one key metric.")
    if not has_example:
        weaknesses.append("Few concrete examples — include a brief STAR example.")
        next_steps.append("Give a 1–2 sentence example showing Situation, Action, Result.")

    # Build a more readable feedback blob
    feedback_parts = []
    feedback_parts.append(f"Overall heuristics: topical coverage {int(overlap*100)}/100, fuzzy match {int(seq_ratio*100)}/100, thoroughness {int(length_ratio*100)}/100.")
    if strengths:
        feedback_parts.append("What went well: " + "; ".join(strengths))
    if weaknesses:
        feedback_parts.append("Opportunities: " + "; ".join(weaknesses))
    if next_steps:
        feedback_parts.append("Concrete next steps: " + "; ".join(next_steps))
    feedback_parts.append("Tip: Start with a 1-line summary → approach (2–4 steps) → example → metrics. Mention how you'd measure success.")
    feedback = "\n".join(feedback_parts)

    # Add a compact comparison section: overlapping words and sentence matches
    try:
        import difflib
        ua_words = [w for w in ua.lower().split() if w]
        ma_words = [w for w in ma.lower().split() if w]
        overlap_words = sorted(list(set(ua_words) & set(ma_words)))[:50]

        ma_sents = [s.strip() for s in __import__('re').split(r"(?<=[.?!])\s+", ma) if s.strip()]
        ua_sents = [s.strip() for s in __import__('re').split(r"(?<=[.?!])\s+", ua) if s.strip()]
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
    except Exception:
        overlap_words = []
        sent_matches = []

    return {
        "score": int(round(score)),
        "skill_scores": skill_scores,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "feedback": feedback,
        "comparison": {"overlap_words": overlap_words, "sentence_matches": sent_matches},
    }


@app.route('/api/generate', methods=['POST'])
def generate():
    payload = request.get_json() or {}
    prompt = (payload.get('prompt') or payload.get('input') or '')
    model = payload.get('model', 'llama3')

    # If the prompt asks to return a JSON array of strings for questions
    if 'Return a valid JSON array of strings' in prompt or 'Return a valid JSON array' in prompt and 'model answer' in prompt.lower():
        # parse questions lines like Q1: text
        qs = re.findall(r"Q\d+:\s*(.*?)(?:\nQ\d+:|$)", prompt, flags=re.S)
        answers = []
        for q in qs:
            answers.append(fallback_model_answer(q.strip()))
        return jsonify({"response": json.dumps(answers)})

    # If batch evaluator requested JSON array of objects
    if 'Return a single valid JSON array of objects' in prompt or 'Return a single valid JSON array of objects where' in prompt:
        # attempt to find Q blocks
        blocks = re.split(r"\nQ\d+:\s*", prompt)[1:]
        out = []
        for blk in blocks:
            # blk contains the question and maybe USER_ANSWER
            qtext = blk.split('\n')[0].strip()
            # attempt to find USER_ANSWER: ... on same block
            ua_match = re.search(r"USER_ANSWER:\s*(.*)", blk, flags=re.S)
            ua = ua_match.group(1).strip() if ua_match else ""
            model_ans = fallback_model_answer(qtext)
            evaln = heuristic_eval(model_ans, ua)
            out.append({
                "model_answer": model_ans,
                "score": evaln["score"],
                "strengths": evaln["strengths"],
                "weaknesses": evaln["weaknesses"],
                "feedback": evaln["feedback"],
            })
        return jsonify({"response": json.dumps(out)})

    # If prompt looks like a single-question evaluator (IDEAL_ANSWER + USER_ANSWER)
    if 'IDEAL_ANSWER' in prompt and 'USER_ANSWER' in prompt:
        # naive extraction
        try:
            ideal = prompt.split('IDEAL_ANSWER:')[1].split('USER_ANSWER:')[0].strip()
            user = prompt.split('USER_ANSWER:')[1].strip()
        except Exception:
            ideal = ''
            user = ''
        evaln = heuristic_eval(ideal, user)
        # Return only JSON object string (no extra text)
        return jsonify({"response": json.dumps(evaln)})

    # If prompt asks to extract details from a JD, respond with simple best-effort JSON
    if 'extract these three things' in prompt.lower() or 'extract' in prompt.lower() and 'company' in prompt.lower():
        # very small heuristic: look for Company: and Role: lines
        company = "Unknown Company"
        role = "PM"
        level = "Strategic"
        m = re.search(r"Company[:\-]\s*(.*)", prompt)
        if m:
            company = m.group(1).strip()
        m2 = re.search(r"Role[:\-]\s*(.*)", prompt)
        if m2:
            role = m2.group(1).strip()
        return jsonify({"response": json.dumps({"company_name": company, "role": role, "level": level})})

    # Default: return a plausible single model answer string
    # Try to extract a question line
    q_match = re.search(r"Question:\s*(.*)", prompt, flags=re.S)
    qtext = q_match.group(1).strip() if q_match else ""
    ans = fallback_model_answer(qtext)
    return jsonify({"response": ans})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=11434)
