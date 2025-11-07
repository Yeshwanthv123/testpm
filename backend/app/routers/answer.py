import json
from fastapi import FastAPI, APIRouter, Request, HTTPException
from sentence_transformers import SentenceTransformer, util
import torch
import os
import uvicorn
from app.llm_client import OllamaClient

# Create FastAPI app
app = FastAPI(title="Answer Evaluation API")

# Create router
router = APIRouter(prefix="/answer", tags=["answer"])


@app.on_event("startup")
async def startup_event():
    """Initialize embedding model and Ollama client on startup"""
    embed_model = os.getenv("EMBED_MODEL", "all-MiniLM-L6-v2")
    app.state.embedder = SentenceTransformer(embed_model)

    ollama_model = "qwen2:7b-instruct"
    ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    app.state.ollama = OllamaClient(base_url=ollama_host, model=ollama_model)


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up Ollama client on shutdown"""
    await app.state.ollama.aclose()


@router.post("/evaluate/")
async def evaluate_answer(request: Request):
    """Evaluate user's answer vs. LLM ideal answer"""
    data = await request.json()
    question = data.get("question")
    user_answer = data.get("user_answer")

    if not question or not user_answer:
        raise HTTPException(status_code=400, detail="Both 'question' and 'user_answer' are required")

    # 1️⃣ Generate ideal answer from Ollama
    prompt = (
        f"You are an expert Product Manager. Provide a concise, expert-level answer "
        f"for the following question:\n\n{question}\n\n"
        "Answer clearly without restating the question or including unnecessary symbols."
    )

    response_data = await app.state.ollama.generate(prompt, max_tokens=256)

    # Normalize LLM output
    if isinstance(response_data, dict):
        llm_answer = response_data.get("response", json.dumps(response_data))
    else:
        # Some Ollama responses include JSON per line; extract only text fields
        try:
            lines = [json.loads(l) for l in response_data.split("\n") if l.strip().startswith("{")]
            llm_answer = " ".join([l.get("response", "") for l in lines if "response" in l]).strip() or response_data
        except Exception:
            llm_answer = str(response_data)

    # 2️⃣ Compute semantic similarity
    emb_user = app.state.embedder.encode(user_answer, convert_to_tensor=True)
    emb_llm = app.state.embedder.encode(llm_answer, convert_to_tensor=True)
    similarity = util.cos_sim(emb_user, emb_llm).item()

    # 3️⃣ Generate improvement suggestions
    improvement_prompt = f"""
You are an interviewer evaluating a candidate's answer.

Candidate's Answer: "{user_answer}"
Reference Answer: "{llm_answer}"

Task:
- Compare both answers.
- Provide constructive feedback.
- Rate it as "good", "average", or "bad" (not a numeric score).
- Highlight strengths and suggest improvements.
- Respond ONLY in JSON format with keys: "rating", "feedback".
"""



    import json

    improvement_data = await app.state.ollama.generate(improvement_prompt, max_tokens=300)

# Try to decode JSON-like responses cleanly
    try:
    # Step 1: Handle if model output is a JSON string
         if isinstance(improvement_data, str):
            cleaned_text = improvement_data.strip().replace("\\n", "").replace("\\", "")
            improvement = json.loads(cleaned_text)
    # Step 2: Handle if model already returned dict
         elif isinstance(improvement_data, dict):
            improvement = improvement_data
         else:
            improvement = {"raw_text": str(improvement_data)}
    except json.JSONDecodeError:
    # Fallback: if still not valid JSON
        improvement = {"feedback": improvement_data.strip().replace("\\n", " ").replace("\\", "")}





    # 4️⃣ Return final results
    return {
        "similarity_score": similarity,
        "ideal_answer": llm_answer,
        "suggestions": improvement,
    }


# Register router
#app.include_router(router)

#if __name__ == "__main__":
 #   uvicorn.run("app.routers.answer:app", host="127.0.0.1", port=8000, reload=True)
#