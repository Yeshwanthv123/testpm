import sys
import json
from pathlib import Path

# Ensure backend package is importable
ROOT = Path(__file__).resolve().parent.parent
BACKEND = ROOT / 'backend'
sys.path.insert(0, str(BACKEND))

from app.ai_services import AIService

def main():
    # Replace these with the question and user answer you want to test
    question = "What is the role of a Product Manager?"
    user_answer = "To define product strategy and ensure the team builds what customers need."

    svc = AIService()
    print(f"Using LLM endpoint: {svc.llm_api_url} (model: {svc.model})")

    print("Generating model answer (may call your LLM endpoint)...")
    model_answer = svc.generate_answer(question, skills=None)
    print('\n--- MODEL ANSWER ---\n')
    print(model_answer)

    print('\nEvaluating user answer...')
    result = svc.evaluate_answer(question, user_answer, model_answer)

    print('\n--- EVALUATION RESULT ---\n')
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
