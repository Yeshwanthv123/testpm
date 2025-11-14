"""
Ollama Wrapper — Flask service that calls Ollama and translates responses
for PM Bot's backend evaluation system.
"""
import os
import json
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
import time

app = Flask(__name__)
CORS(app)

# Ollama runs on localhost:11434 inside container
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
MODEL = os.environ.get("LLM_MODEL", "llama2")

def wait_for_ollama(max_wait=60):
    """Wait for Ollama to be ready."""
    start = time.time()
    while time.time() - start < max_wait:
        try:
            resp = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
            if resp.status_code == 200:
                print(f"[Ollama Wrapper] Ollama ready. Available models: {resp.json()}")
                return True
        except:
            pass
        print("[Ollama Wrapper] Waiting for Ollama...")
        time.sleep(3)
    print("[Ollama Wrapper] Ollama did not start in time")
    return False


def query_ollama(prompt: str, system_prompt: str = "", temperature: float = 0.7, model: str = None) -> str:
    """Query Ollama for text generation."""
    if not model:
        model = MODEL
    
    try:
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "temperature": temperature,
        }
        if system_prompt:
            payload["system"] = system_prompt
        
        print(f"[Ollama] Calling {model} with prompt ({len(prompt)} chars)...")
        resp = requests.post(f"{OLLAMA_URL}/api/generate", json=payload, timeout=180)
        
        if resp.status_code == 200:
            result = resp.json()
            text = result.get("response", "").strip()
            print(f"[Ollama] Got response ({len(text)} chars)")
            return text
        else:
            print(f"[Ollama] Error {resp.status_code}: {resp.text[:200]}")
            return ""
    except Exception as e:
        print(f"[Ollama] Exception: {e}")
        return ""


@app.route('/api/tags', methods=['GET'])
def tags():
    """Compatible with old interface — return available models."""
    return jsonify({"models": [{"name": MODEL}]})


@app.route('/api/generate', methods=['POST'])
def generate():
    """Main endpoint called by backend. Returns {response: "text"}."""
    try:
        data = request.json or {}
        prompt = data.get("prompt", "").strip()
        model = data.get("model", MODEL)
        
        if not prompt:
            return jsonify({"response": ""})
        
        # Call Ollama
        result = query_ollama(prompt, temperature=0.6, model=model)
        
        if not result:
            result = "I would approach this systematically by understanding the problem, analyzing the data, and implementing solutions based on metrics."
        
        return jsonify({"response": result})
    
    except Exception as e:
        print(f"[/api/generate] Error: {e}")
        return jsonify({"response": "", "error": str(e)}), 500


@app.route('/')
def index():
    return """
    <html>
        <head><title>PM Bot LLM Service (Ollama)</title></head>
        <body style="font-family: Arial; padding: 2rem;">
            <h1>PM Bot LLM Service</h1>
            <p>Running Ollama-based language models for PM interview evaluation.</p>
            <p>Model: %s</p>
        </body>
    </html>
    """ % MODEL


@app.route('/api/generate-answer', methods=['POST'])
def generate_answer():
    """Generate a model PM interview answer."""
    try:
        data = request.json or {}
        question = data.get("question", "").strip()
        skills = data.get("skills", [])
        model = data.get("model") or MODEL
        
        if not question:
            return jsonify({"error": "No question"}), 400
        
        skills_text = ", ".join(skills) if skills else "product thinking, execution, measurement"
        
        system = """You are an expert Product Manager. Generate a comprehensive, structured answer to this PM interview question.
Use clear frameworks, specific metrics, and business thinking. Be concise (150-200 words)."""
        
        prompt = f"PM Interview Question: {question}\n\nKey Skills: {skills_text}\n\nProvide a high-quality PM answer:"
        
        answer = query_ollama(prompt, system, temperature=0.6, model=model)
        
        if not answer:
            answer = "I would approach this systematically: 1) Understand the problem deeply, 2) Analyze the data and stakeholders, 3) Develop hypotheses, 4) Test and iterate. Key metrics would include user engagement, retention, and business impact."
        
        return jsonify({"answer": answer})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/evaluate-answer', methods=['POST'])
def evaluate_answer():
    """Evaluate user answer against model answer."""
    try:
        data = request.json or {}
        question = data.get("question", "").strip()
        user_answer = data.get("user_answer", "").strip()
        model_answer = data.get("model_answer", "").strip()
        skills = data.get("skills", [])
        model = data.get("model") or MODEL
        
        if not all([question, user_answer, model_answer]):
            return jsonify({"error": "Missing required fields"}), 400
        
        skills_text = ", ".join(skills) if skills else "product thinking"
        
        # Strong instructive system + example to increase chance of complete structured output
        system = (
            "You are an expert PM interview evaluator. Respond with a single valid JSON object only, no extra text."
            " The JSON must include the following keys: similarity_score (float 0.0-1.0), score (int 0-100), strengths (array of 2-4 short strings),"
            " improvements (array of 2-4 short strings), feedback (1-3 sentence human-readable summary), and ideal_answer (string)."
        )

        # Provide an explicit example of the expected JSON shape for the model to mimic.
        example = (
            '{"similarity_score":0.78,"score":78,"strengths":["Good structure","Used metrics"],'
            '"improvements":["Add concrete example","Quantify impact"],"feedback":"Good start; add an example and a metric.",'
            '"ideal_answer":"<ideal answer text>"}'
        )

        prompt = (
            f"Evaluate this PM answer.\n\nQUESTION: {question}\n\nIDEAL_ANSWER: {model_answer}\n\nUSER_ANSWER: {user_answer}\n\nSKILLS: {skills_text}\n\n"
            "Return ONLY a single JSON object exactly matching the keys in the example.\n"
            f"Example JSON: {example}\n\nJSON:"
        )

        response = query_ollama(prompt, system, temperature=0.3, model=model)
        
        # Parse JSON
        def try_parse(resp_text: str) -> dict | None:
            try:
                json_start = resp_text.find('{')
                json_end = resp_text.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    json_str = resp_text[json_start:json_end]
                    return json.loads(json_str)
                else:
                    return json.loads(resp_text)
            except Exception:
                return None

        eval_data = try_parse(response or "")
        # If model returned incomplete/missing fields, retry with an even stricter prompt
        def has_required_fields(d: dict) -> bool:
            if not isinstance(d, dict):
                return False
            keys = d.keys()
            return all(k in keys for k in ("similarity_score", "score", "strengths", "improvements", "feedback"))

        if not eval_data or not has_required_fields(eval_data):
            # Retry with a shorter, more directive prompt asking for keys only and short lists
            retry_prompt = (
                f"Return ONLY a JSON object with keys: similarity_score (0-1 float), score (0-100 int), strengths (array of 2-4 short strings),"
                f" improvements (array of 2-4 short strings), feedback (1-3 sentences), ideal_answer (string). No extra text.\n\nQuestion: {question}\n"
                f"IDEAL_ANSWER: {model_answer}\nUSER_ANSWER: {user_answer}\nJSON:"
            )
            print("[Ollama Wrapper] First eval parse incomplete, retrying with stricter prompt")
            response2 = query_ollama(retry_prompt, system, temperature=0.2, model=model)
            eval_data = try_parse(response2 or "")

        # If still incomplete, return an explicit minimal structured response so backend can present an actionable message
        if not eval_data or not has_required_fields(eval_data):
            print(f"[Ollama Wrapper] Evaluation still incomplete; returning minimal structured response. Resp1 len={len(response or '')} Resp2 len={len(response2 or '') if 'response2' in locals() else 0}")
            eval_data = {
                "similarity_score": 0.0,
                "score": 0,
                "strengths": [],
                "improvements": ["Evaluation unavailable: model did not return detailed items."],
                "feedback": "Evaluation unavailable: model did not return a full structured evaluation. Try pulling a model into Ollama.",
                "ideal_answer": model_answer,
            }
        
        # Normalize
        sim_score = float(eval_data.get("similarity_score", 0.5))
        score = int(eval_data.get("score", max(0, int(sim_score * 100))))
        
        if score >= 80:
            rating = "great"
        elif score >= 65:
            rating = "good"
        elif score >= 45:
            rating = "fair"
        else:
            rating = "needs_work"
        
        result = {
            "similarity_score": min(1.0, max(0.0, sim_score)),
            "score": min(100, max(0, score)),
            "ideal_answer": model_answer,
            "suggestions": {
                "rating": rating,
                "feedback": {
                    "comparison": eval_data.get("feedback", ""),
                    "strengths": eval_data.get("strengths", [])[:3],
                    "improvements": eval_data.get("improvements", [])[:3]
                }
            }
        }

        # Also return flattened top-level fields for convenience (backend expects these keys)
        try:
            fb = result.get("suggestions", {}).get("feedback", {})
            result["strengths"] = fb.get("strengths", [])
            result["improvements"] = fb.get("improvements", [])
            result["feedback"] = fb.get("comparison", "")
        except Exception:
            result["strengths"] = []
            result["improvements"] = []
            result["feedback"] = ""

        return jsonify(result)
    
    except Exception as e:
        print(f"[evaluate_answer] Error: {e}")
        return jsonify({"error": str(e)}), 500


@app.before_request
def startup():
    """Initialize on first request."""
    if not hasattr(app, 'ollama_ready'):
        app.ollama_ready = wait_for_ollama()


if __name__ == "__main__":
    print("[LLM Wrapper] Starting...")
    app.run(host="0.0.0.0", port=5000, debug=False)
