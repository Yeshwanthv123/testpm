from flask import Flask, request, jsonify
from flask_cors import CORS
import re
import json
import random

app = Flask(__name__)
CORS(app)

# Listen on port 11434 to match Ollama's default port
PORT = 11434

def generate_qwen_response(prompt):
    """
    Simulate Qwen model generating responses for our prompts.
    In a real implementation, this would make an API call to the actual model.
    """
    # For demonstration, we'll return structured responses that look like they came from an AI
    return {
        "choices": [{
            "text": prompt  # We'll handle the actual response generation in the calling function
        }]
    }

# Core functions for Qwen model simulation
def generate_model_answer(question, skills=None):
    """Generate an expert PM answer using Qwen-style prompting.
    Produces diverse, question-specific answers rather than generic templates."""
    skills_list = skills if skills else ["product thinking", "execution", "measurement", "leadership", "vision"]
    
    # Seed RNG based on question text for deterministic but diverse answers
    q_seed = sum(ord(c) for c in (question or "")) % 1000
    rng = random.Random(q_seed)

    q_lower = (question or "").lower()

    # Detect question type to produce contextual answers
    is_prioritization = any(w in q_lower for w in ["prioritize", "priority", "prioritization", "choose", "select features"])
    is_measurement = any(w in q_lower for w in ["measure", "success", "metric", "kpi", "track"])
    is_strategy = any(w in q_lower for w in ["strategy", "strategic", "approach", "how would", "how to"])
    is_problem = any(w in q_lower for w in ["problem", "issue", "challenge", "solve", "handle"])
    is_launch = any(w in q_lower for w in ["launch", "launch", "go-to-market", "gtm", "release"])

    # Generate context-specific metrics
    metric_vals = {
        "engagement": rng.randint(8, 35),
        "activation": rng.randint(5, 25),
        "retention": rng.randint(8, 30),
        "conversion": rng.randint(3, 15),
    }

    # Generate different answers based on question type
    if is_prioritization:
        answer = (
            f"I'd prioritize features using a 2x2 matrix: impact vs. effort.\n\n"
            f"1. Research: Interview {rng.randint(10, 30)} users to understand pain points and validate assumptions.\n"
            f"2. Scoring: Rate each feature on impact (business + user value) and effort (engineering complexity).\n"
            f"3. Prioritize: Focus on high-impact, low-effort features first to build momentum.\n"
            f"4. Track: Measure adoption (+{metric_vals['activation']}% target in 6 weeks) and retention weekly.\n\n"
            f"Example: When building our feature set, we prioritized onboarding improvements and saw +{metric_vals['activation']}% activation and {metric_vals['retention']}% month-over-month retention growth."
        )
    elif is_measurement:
        answer = (
            f"Success metrics depend on the product stage. For launches, I'd track:\n\n"
            f"1. Primary Metrics:\n"
            f"   - Activation: {metric_vals['activation']}%+ of new users completing onboarding.\n"
            f"   - Engagement: {rng.randint(30, 60)}%+ weekly active users returning (DAU/MAU).\n"
            f"   - Retention: {metric_vals['retention']}% of Day-1 users returning on Day-7.\n\n"
            f"2. Business Metrics:\n"
            f"   - Revenue impact or cost reduction aligned to OKRs.\n"
            f"   - Conversion rate lift: +{metric_vals['conversion']}%+ through the funnel.\n\n"
            f"3. Cadence: Measure daily for first 2 weeks, then weekly. Set guardrails (e.g., don't ship if activation drops below {metric_vals['activation']-5}%)."
        )
    elif is_launch:
        answer = (
            f"Go-to-market strategy: Internal → Beta → Public.\n\n"
            f"1. Internal (Week 1): Beta with {rng.randint(10, 50)} employees, gather feedback, iterate.\n"
            f"2. Beta (Week 2-3): Invite {rng.randint(100, 500)} power users, run surveys, measure engagement.\n"
            f"3. Public (Week 4+): Gradual rollout to all users; monitor for bugs, server load, user feedback.\n\n"
            f"Key metrics: Adoption to {metric_vals['activation']}% in 4 weeks, support ticket volume < 2% of user base, NPS > 40.\n\n"
            f"Example: Launched a new feature to 10% of users, achieved {metric_vals['engagement']}% DAU engagement in Week 1, then expanded to 100%."
        )
    elif is_problem or is_strategy:
        answer = (
            f"My approach:\n\n"
            f"1. Define the Problem: Understand user needs and business constraints. Set SMART goals.\n"
            f"2. Explore Solutions: Brainstorm {rng.randint(3, 8)} options; evaluate trade-offs (speed, cost, quality).\n"
            f"3. Validate: Run experiments with small user cohorts. Target conversion lift of +{metric_vals['conversion']}%.\n"
            f"4. Build & Ship: Create roadmap with weekly milestones. Launch to {rng.randint(10, 50)}% of users first.\n"
            f"5. Measure: Track success with engagement (+{metric_vals['engagement']}% DAU), retention, and NPS.\n\n"
            f"Trade-offs: Speed vs. quality. I'd prioritize speed for fast feedback loops, then iterate on quality."
        )
    else:
        # Default comprehensive answer
        answer = (
            f"Here's my structured approach:\n\n"
            f"1. Analyze: Understand the problem from user and business perspectives.\n"
            f"2. Ideate: Generate {rng.randint(3, 6)} potential solutions and evaluate impact vs. effort.\n"
            f"3. Plan: Create a detailed 8-12 week roadmap with weekly milestones and success criteria.\n"
            f"4. Execute: Work cross-functionally to build and deploy incrementally.\n"
            f"5. Learn: Measure key metrics (engagement {metric_vals['engagement']}%, retention {metric_vals['retention']}%) and iterate.\n\n"
            f"Success is defined by: adoption, user satisfaction (NPS), and business impact (revenue or cost savings)."
        )

    skills_text = ", ".join(skills_list) if skills_list else ""
    if skills_text:
        answer += f"\n\nSkills: {skills_text}"

    return answer

def evaluate_answer(question_text, model_answer, user_answer):
    """Generate structured evaluation with human-readable, context-aware feedback."""
    strengths = []
    weaknesses = []

    ua = (user_answer or "").lower()
    ma = (model_answer or "").lower()
    q = (question_text or "").lower()

    # Token sets excluding stopwords
    stopwords = set(["the", "a", "an", "and", "or", "to", "of", "in", "on", "for", "with", "is", "are", "that", "this", "be", "by", "at", "from", "i", "we"])
    ua_tokens = [t for t in re.findall(r"\w+", ua) if t not in stopwords]
    ma_tokens = [t for t in re.findall(r"\w+", ma) if t not in stopwords]

    overlap = len(set(ua_tokens) & set(ma_tokens))
    denom = max(1, min(len(set(ua_tokens)), len(set(ma_tokens))))
    concept_sim = overlap / denom if denom > 0 else 0.0

    # Detailed signal detection
    has_user_metrics = any(tok in ua for tok in ["%","percent","metric","kpi","increase","decrease","uplift","nps","activation","retention","conversion","dau","mau"])
    has_user_framework = any(tok in ua for tok in ["2x2","matrix","framework","step","approach","1)","2)","3)","4)","process","phase"])
    has_user_examples = any(tok in ua for tok in ["example","project","case","scenario","led","implemented","launched","we did","experienced"])
    has_user_outcomes = any(tok in ua for tok in ["result","impact","outcome","improve","improved","achieved","success","measure"])
    has_user_timeframe = any(tok in ua for tok in ["week","month","days","timeline","roadmap","sprint"])
    
    has_model_metrics = any(tok in ma for tok in ["%","percent","metric","kpi","nps","activation","retention","conversion","dau","mau"])
    has_model_framework = any(tok in ma for tok in ["2x2","matrix","framework","step","approach","1)","2)","3)","4)","process"])
    has_model_examples = any(tok in ma for tok in ["example","project","case"])

    # Length analysis
    ua_len = len(ua_tokens)
    ma_len = len(ma_tokens)
    length_score = max(0, min(1, (ua_len - 10) / 140))

    # Scoring formula
    score_float = (
        0.40 * concept_sim +
        0.25 * (1.0 if has_user_metrics else 0.0) +
        0.15 * (1.0 if has_user_framework else 0.0) +
        0.12 * (1.0 if has_user_examples else 0.0) +
        0.08 * length_score
    )

    # Deterministic jitter
    seed = sum(ord(c) for c in (q + ua)) % 100
    jitter = (seed % 5) - 2

    final_score = max(0, min(100, int(round(score_float * 100)) + jitter))

    # HUMAN-READABLE STRENGTHS (specific to what user DID well)
    if concept_sim > 0.6:
        strengths.append("You covered the main approach well—shows good PM thinking")
    if has_user_metrics and has_model_metrics:
        strengths.append("Great! You included specific metrics to track success")
    if has_user_framework and has_model_framework:
        strengths.append("Nice structure—you laid out a clear step-by-step plan")
    if has_user_examples and has_model_examples:
        strengths.append("Excellent! You backed up your answer with a real project example")
    if has_user_outcomes:
        strengths.append("Good focus on measuring impact and business outcomes")
    if has_user_timeframe:
        strengths.append("You thought about timing and realistic rollout phases")

    # QUESTION-TYPE SPECIFIC SIGNALS
    is_prioritization = any(w in q for w in ["prioritize", "priority", "prioritization", "choose", "select features", "rank", "order"])
    is_measurement = any(w in q for w in ["measure", "measurement", "success", "metric", "kpi", "track", "evaluate"])
    is_strategy = any(w in q for w in ["strategy", "strategic", "approach", "how would", "how to", "handle", "problem", "challenge"])

    # Add targeted strengths/weaknesses per question type to avoid generic repetition
    if is_prioritization:
        if has_user_framework:
            strengths.append("Good use of a prioritization framework; that helps make trade-offs explicit")
        else:
            weaknesses.append("Try using a framework (e.g., 2x2 impact vs. effort) to make prioritization defensible")
        if has_user_metrics:
            strengths.append("You tied prioritization to measurable impact")
        else:
            weaknesses.append("Quantify expected impact for prioritized items (e.g., activation %, revenue)")

    if is_measurement:
        if has_user_metrics:
            strengths.append("You named concrete metrics—good grounding for evaluation")
        else:
            weaknesses.append("Specify primary metrics (activation, retention, conversion) and their targets")
        # encourage cadence and guardrails
        if any(tok in ua for tok in ["daily","weekly","monthly","cadence"]):
            strengths.append("You described a measurement cadence")
        else:
            weaknesses.append("Add measurement cadence (e.g., daily for launch, weekly thereafter) and guardrails")

    if is_strategy:
        if has_user_outcomes:
            strengths.append("You focused on outcomes which is vital for strategic decisions")
        else:
            weaknesses.append("Tie your strategy to concrete business outcomes and success criteria")
        if has_user_framework:
            strengths.append("Good to see a phased approach or process in your strategy")
        else:
            weaknesses.append("Outline clear phases (e.g., discovery, validation, rollout) to structure the strategy")

    # HUMAN-READABLE WEAKNESSES (specific gaps)
    if concept_sim < 0.35:
        weaknesses.append("Your answer misses some key PM frameworks or structured thinking")
    if not has_user_metrics and has_model_metrics:
        weaknesses.append("Add specific metrics—e.g., activation %, retention, or revenue impact")
    if not has_user_framework and has_model_framework:
        weaknesses.append("Structure your answer more clearly—try: Problem → Solution → Measurement")
    if not has_user_examples and has_model_examples:
        weaknesses.append("Include a brief real-world example to back up your approach")
    if not has_user_timeframe and has_model_framework:
        weaknesses.append("Mention timeline or rollout phases—e.g., 'Week 1 for beta, Week 4 for full launch'")
    if ua_len < 25 and ma_len > 100:
        weaknesses.append("Your answer is too brief—expand with more reasoning and details")

    # Remove duplicates and limit
    strengths = list(dict.fromkeys(strengths))[:3]
    weaknesses = list(dict.fromkeys(weaknesses))[:3]

    if not strengths:
        strengths = ["You understood the question and gave a thoughtful response"]
    if not weaknesses:
        weaknesses = ["Consider adding more specific examples or metrics"]

    rating = "great" if final_score >= 80 else ("good" if final_score >= 65 else ("fair" if final_score >= 45 else "needs work"))
    
    # Detect question type for context-aware feedback
    q_lower = (question_text or "").lower()
    is_prioritization = any(w in q_lower for w in ["prioritize", "priority", "choose", "select features", "rank", "order"])
    is_measurement = any(w in q_lower for w in ["measure", "success", "metric", "kpi", "track", "evaluate"])
    is_strategy = any(w in q_lower for w in ["strategy", "strategic", "approach", "how would", "crisis", "challenge", "handle"])
    
    # HUMAN-READABLE COMPARISON MESSAGE - QUESTION-TYPE SPECIFIC
    if is_prioritization:
        if final_score >= 75:
            comparison = f"Strong prioritization thinking! You showed good judgment on impact vs. effort. Next time, explicitly use a 2x2 matrix framework and quantify expected metrics."
        elif final_score >= 55:
            comparison = f"Good start on prioritization. Your answer has solid ideas but needs more structure. Try a 2x2 matrix (impact vs. effort) and include expected business outcomes."
        else:
            comparison = f"Your prioritization approach needs more structure. Use a clear framework like 2x2 matrix, quantify impact, and explain trade-offs between options."
    elif is_measurement:
        if final_score >= 75:
            comparison = f"Excellent metrics thinking! You identified key success indicators and measurement cadence. Next time, add guardrails and failure modes to watch."
        elif final_score >= 55:
            comparison = f"Good effort on metrics. You covered some key areas but missed measurement cadence and guardrails. Add: When to measure, what signals matter most, and when to pivot."
        else:
            comparison = f"Your metrics answer needs more specificity. Add: Primary metrics (e.g., activation %), measurement frequency (daily/weekly), and decision guardrails."
    elif is_strategy:
        if final_score >= 75:
            comparison = f"Solid strategic thinking! You understood the challenge and outlined a clear approach. Next time, dive deeper into stakeholder considerations and trade-offs."
        elif final_score >= 55:
            comparison = f"Your strategy has promise but needs more depth. Add: Clear phases, stakeholder considerations, and how you'd handle trade-offs or pivots."
        else:
            comparison = f"Your strategy answer lacks clarity. Structure it: 1) Understand the problem, 2) Define success metrics, 3) Outline approach phases, 4) Handle risks/trade-offs."
    else:
        # Fallback for general questions
        if final_score >= 80:
            comparison = f"Excellent work! Your answer shows strong PM thinking with metrics and structure. Keep this level of detail."
        elif final_score >= 65:
            comparison = f"Good answer! You covered the main points. Add more metrics or a real example to strengthen it."
        elif final_score >= 45:
            comparison = f"Fair effort. Your answer has some good ideas but needs more structure, metrics, or details."
        else:
            comparison = f"You're on the right track but missing key elements. Review the model answer and add more specific details."

    suggestions = {
        "rating": rating,
        "feedback": {
            "comparison": comparison,
            "strengths": strengths,
            "improvements": weaknesses,
        }
    }

    evaluation = {
        "similarity_score": round(final_score / 100.0, 2),
        "score": final_score,
        "ideal_answer": model_answer,
        "suggestions": suggestions,
    }

    return evaluation
    

@app.route('/api/evaluate-answer', methods=['POST'])
def evaluate_answer_endpoint():
    """
    Evaluate a user's answer against a model/ideal answer.
    Expects: {question, user_answer, model_answer, skills}
    Returns: {score, similarity_score, strengths, improvements, feedback, ideal_answer, suggestions}
    """
    try:
        payload = request.get_json() or {}
        question = payload.get('question', '')
        user_answer = payload.get('user_answer', '')
        model_answer = payload.get('model_answer', '')
        
        # If no model answer provided, generate one
        if not model_answer:
            model_answer = generate_model_answer(question)
        
        # Use our evaluation function
        evaluation = evaluate_answer(question, model_answer, user_answer)
        
        return jsonify(evaluation), 200
    except Exception as e:
        print(f"[LLM Stub /api/evaluate-answer error] {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "score": 0,
            "similarity_score": 0.0,
            "strengths": [],
            "improvements": ["Evaluation service error"],
            "feedback": f"Error: {str(e)[:100]}",
            "ideal_answer": "",
            "suggestions": {}
        }), 500

@app.route('/api/tags', methods=['GET'])
def tags():
    # Only report Qwen model as available
    return jsonify({"models": [{"name": "qwen2:7b-instruct"}]})

@app.route('/')
def index():
    return """
    <html>
        <head><title>PM Bot LLM Service</title></head>
        <body style="font-family: Arial; padding: 2rem;">
            <h1>PM Bot LLM Service</h1>
            <p>Running Qwen model simulation for PM interview evaluation.</p>
        </body>
    </html>
    """


def qwen_generate_answer(question_text, skills=None):
    """Generate an expert PM answer for the given question using Qwen-style responses."""
    # Format skills list for response
    skills_text = ', '.join(skills) if skills else 'product thinking, execution, measurement, leadership, vision'
    
    # Clean and normalize question
    question_lower = question_text.lower().strip()
    
    # Generate structured approach for how-to questions
    if any(term in question_lower for term in ["how would you", "how to", "approach", "handle"]):
        return (
            f"Here's a structured approach to {question_text}\n\n"
            f"1. Initial Analysis\n"
            f"   - Conduct thorough market and user research\n"
            f"   - Gather data on current state and pain points\n"
            f"   - Identify key stakeholders and constraints\n\n"
            f"2. Strategy Development\n"
            f"   - Define clear success metrics and KPIs\n"
            f"   - Set SMART goals aligned with business objectives\n"
            f"   - Prioritize based on impact vs. effort analysis\n\n"
            f"3. Implementation Plan\n"
            f"   - Create detailed project timeline and milestones\n"
            f"   - Assemble cross-functional team and define roles\n"
            f"   - Establish communication and feedback channels\n\n"
            f"4. Risk Mitigation\n"
            f"   - Identify potential roadblocks and dependencies\n"
            f"   - Develop contingency plans and backup strategies\n"
            f"   - Set up monitoring and alert mechanisms\n\n"
            f"5. Success Measurement\n"
            f"   - Track key metrics: user engagement (+25%), retention (+15%)\n"
            f"   - Gather user feedback through multiple channels\n"
            f"   - Regular stakeholder updates and adjustments\n\n"
            f"Recent Example: Led a similar initiative that achieved 40% adoption within first month and 92% user satisfaction.\n\n"
            f"Key skills leveraged: {skills_text}"
        )
    elif any(term in question_lower for term in ["what is", "explain", "describe", "define"]):
        return (
            f"Let me explain {question_text}\n\n"
            f"Core Concept:\n"
            f"A fundamental aspect of product management that involves strategic thinking and execution excellence.\n\n"
            f"Key Components:\n"
            f"1. Strategic Vision\n"
            f"   - Long-term planning and goal setting\n"
            f"   - Market positioning and competitive analysis\n\n"
            f"2. Execution Framework\n"
            f"   - Systematic approach to implementation\n"
            f"   - Resource allocation and timeline management\n\n"
            f"3. Success Metrics\n"
            f"   - Quantitative KPIs (e.g., 30% increase in user engagement)\n"
            f"   - Qualitative feedback and user satisfaction\n\n"
            f"Practical Application:\n"
            f"Recently implemented this in a project that achieved:\n"
            f"- 25% improvement in team productivity\n"
            f"- 45% reduction in time-to-market\n"
            f"- 92% positive user feedback\n\n"
            f"Best Practices:\n"
            f"• Regular stakeholder communication\n"
            f"• Data-driven decision making\n"
            f"• Continuous iteration and improvement\n\n"
            f"Skills emphasized: {skills_text}"
        )
    else:
        # Default structured response for other question types
        return (
            f"Here's my comprehensive response to: {question_text}\n\n"
            f"Context & Background:\n"
            f"- Understanding the current landscape and challenges\n"
            f"- Identifying key opportunities and constraints\n"
            f"- Analyzing market trends and user needs\n\n"
            f"Strategic Approach:\n"
            f"1. Research & Analysis\n"
            f"   - Conduct user research and data analysis\n"
            f"   - Identify pain points and opportunities\n\n"
            f"2. Solution Design\n"
            f"   - Develop comprehensive strategy\n"
            f"   - Define success metrics and KPIs\n\n"
            f"3. Implementation\n"
            f"   - Create detailed execution plan\n"
            f"   - Set up monitoring and feedback loops\n\n"
            f"Results & Impact:\n"
            f"- Achieved 35% improvement in key metrics\n"
            f"- Reduced user friction by 40%\n"
            f"- Increased team efficiency by 25%\n\n"
            f"Key skills applied: {skills_text}"
        )


def ai_evaluate_answer(question, model_answer, user_answer):
    import random
    
    # Pre-defined evaluation patterns for different answer qualities
    EVALUATION_PATTERNS = [
        {
            "score_range": (85, 100),
            "strengths": [
                "Exceptional strategic thinking and problem-solving approach",
                "Comprehensive understanding of product management principles",
                "Strong data-driven decision making with concrete metrics",
                "Excellent stakeholder management perspective",
                "Clear articulation of implementation steps and success criteria"
            ],
            "weaknesses": [
                "Could add more industry-specific examples",
                "Consider including alternative approaches",
                "Might benefit from more specific timelines"
            ]
        },
        {
            "score_range": (70, 84),
            "strengths": [
                "Good grasp of core product management concepts",
                "Clear problem-solving methodology",
                "Effective consideration of user needs",
                "Strong focus on measurable outcomes",
                "Well-structured response with logical flow"
            ],
            "weaknesses": [
                "Could elaborate more on success metrics",
                "Consider deeper market analysis",
                "Add more specific examples from experience",
                "Expand on risk mitigation strategies"
            ]
        },
        {
            "score_range": (50, 69),
            "strengths": [
                "Basic understanding of product concepts",
                "Attempted structured approach",
                "Included some relevant examples",
                "Considered key stakeholders"
            ],
            "weaknesses": [
                "Need more specific success metrics",
                "Expand on implementation details",
                "Include more product management frameworks",
                "Consider cross-functional implications",
                "Add data-driven decision points"
            ]
        },
        {
            "score_range": (0, 49),
            "strengths": [
                "Shows potential for improvement",
                "Attempted to address the question",
                "Basic problem-solving approach"
            ],
            "weaknesses": [
                "Strengthen product management fundamentals",
                "Include specific metrics and KPIs",
                "Add structured approach to solution",
                "Consider user and business perspectives",
                "Provide concrete examples"
            ]
        }
    ]

    


@app.route('/api/generate', methods=['POST'])
def generate():
    payload = request.get_json() or {}
    prompt = (payload.get('prompt') or payload.get('input') or '')
    model = payload.get('model', 'llama3')

    # Detect batch model answer generation (exact match from backend's generate_answers_batch)
    if 'Output must be a single valid JSON array where each element is the model answer string' in prompt:
        try:
            # Parse questions (Q1: ... Q2: ... format)
            qs = re.findall(r"Q\d+:\s*(.*?)(?:\nQ\d+:|$)", prompt, flags=re.S)
            if qs:
                answers = []
                for q in qs:
                    question = q.strip()
                    # Extract any skills mentioned
                    skills_match = re.search(r"Skills:\s*(.*?)(?:\n|$)", question)
                    skills = skills_match.group(1).split(',') if skills_match else None
                    # Generate and add answer
                    model_answer = generate_model_answer(question, skills)
                    answers.append(model_answer)
                return jsonify({"response": json.dumps(answers)})
        except Exception as e:
            print(f"[LLM Stub] Batch answer generation error: {e}")
            return jsonify({"response": json.dumps([f"Error: {str(e)}"[:100]])})

    # Handle batch evaluation requests (robust detection for prompts asking for a single JSON array)
    if ("output must be a single valid json array" in prompt.lower()):
        try:
            print(f"[LLM Stub] Detected batch evaluation request")
            # Parse question blocks
            blocks = re.split(r"\nQ\d+:\s*", prompt)[1:]
            evaluations = []
            
            for blk in blocks:
                # Extract question and user answer
                qtext = blk.split('\n')[0].strip()
                ua_match = re.search(r"USER_ANSWER:\s*(.*)", blk, flags=re.S)
                user_answer = ua_match.group(1).strip() if ua_match else ""
                
                # Look for skills
                skills_match = re.search(r"Skills:\s*(.*?)(?:\n|$)", qtext)
                skills = skills_match.group(1).split(',') if skills_match else None
                
                # Generate model answer
                model_ans = generate_model_answer(qtext, skills)

                # Evaluate using our evaluator
                eval_obj = evaluate_answer(qtext, model_ans, user_answer)

                # Map eval_obj into the batch shape expected by the backend's evaluate_answers_batch
                # backend expects: model_answer, score, strengths, weaknesses, feedback
                suggestions = eval_obj.get("suggestions") or {}
                fb = suggestions.get("feedback") if isinstance(suggestions, dict) else None
                strengths = fb.get("strengths") if fb and isinstance(fb.get("strengths"), list) else []
                improvements = fb.get("improvements") if fb and isinstance(fb.get("improvements"), list) else []
                comparison = fb.get("comparison") if fb and isinstance(fb.get("comparison"), str) else ""

                evaluations.append({
                    "model_answer": model_ans,
                    "score": int(eval_obj.get("score") or 0),
                    "strengths": strengths,
                    "weaknesses": improvements,
                    "feedback": comparison or (eval_obj.get("feedback") or ""),
                })
            
            print(f"[LLM Stub] Returning {len(evaluations)} batch evaluations")
            # Return array of evaluations
            return jsonify({"response": json.dumps(evaluations)})
        except Exception as e:
            print(f"[LLM Stub] Batch evaluation error: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({"response": json.dumps([{
                "model_answer": "Error processing batch evaluation",
                "score": 0,
                "strengths": [],
                "weaknesses": ["Technical error in evaluation"],
                "feedback": "Failed to process evaluation"
            }])})

    # If prompt looks like a single-question evaluator (IDEAL_ANSWER + USER_ANSWER)
    if 'IDEAL_ANSWER' in prompt and 'USER_ANSWER' in prompt:
        # naive extraction and evaluation (robust try/except)
        try:
            ideal = prompt.split('IDEAL_ANSWER:')[1].split('USER_ANSWER:')[0].strip()
            user = prompt.split('USER_ANSWER:')[1].strip()
            question = prompt.split('IDEAL_ANSWER:')[0].strip()  # Try to extract the question part

            # Generate evaluation with our function
            evaluation = evaluate_answer(question, ideal, user)
        except Exception as e:
            print(f"Single evaluation extraction/eval error: {e}")
            # Build a conservative fallback that matches the expected structured shape
            evaluation = {
                "similarity_score": 0.0,
                "score": 50,
                "ideal_answer": ideal if 'ideal' in locals() else "",
                "suggestions": {
                    "rating": "needs_improvement",
                    "feedback": {
                        "comparison": "Could not generate full evaluation; please retry.",
                        "strengths": [],
                        "improvements": ["LLM evaluation failed; fallback used"]
                    }
                }
            }

        return jsonify({"response": json.dumps(evaluation)})

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
    # Use our expert PM answer generation
    ans = generate_model_answer(qtext)
    return jsonify({"response": ans})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=11434)
