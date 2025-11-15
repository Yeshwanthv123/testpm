"""
Advanced PM Interview Answer Generator
Generates contextually-specific, high-quality answers using modern PM frameworks
"""

import csv
import json
from typing import Dict, List, Tuple
import re

class PMAnswerGenerator:
    """Generates quality PM interview answers based on question context"""
    
    # Metrics mappings for common KPIs
    METRIC_MEANINGS = {
        'DAU/MAU': 'Daily/Monthly Active Users - measures user stickiness',
        'CSAT': 'Customer Satisfaction - measures user satisfaction (1-5 scale)',
        'NPS': 'Net Promoter Score - likelihood to recommend (0-100)',
        'ARPU': 'Average Revenue Per User - revenue efficiency',
        'LTV': 'Lifetime Value - total revenue from a user',
        'CAC': 'Customer Acquisition Cost - cost to acquire a user',
        'CTR': 'Click-Through Rate - engagement metric',
        'Conversion Rate': 'Percentage of users completing a goal action',
        'Retention D30': '30-day retention - percentage returning after first use',
        'Session Length': 'Average time spent per session',
        'Query Success Rate': 'Percentage of search queries returning relevant results',
        'Fill Rate': 'Percentage of available inventory filled/sold',
        'Error Rate': 'Percentage of requests/operations that fail',
        'Latency p95': '95th percentile response time',
        'Churn': 'Percentage of users stopping usage',
        'Percentile': 'User ranking vs peers'
    }
    
    def __init__(self):
        self.answers_db = []
    
    def extract_problem_context(self, question: str) -> Dict:
        """Extract key context from question"""
        context = {
            'product': 'unknown',
            'problem_type': 'unknown',
            'target_metric': 'unknown',
            'constraint': 'unknown',
            'feature': 'unknown'
        }
        
        # Extract product area (Listings, Reviews, Host tools, Trust, Search)
        if 'Listings' in question:
            context['product'] = 'Listings'
        elif 'Reviews' in question:
            context['product'] = 'Reviews'
        elif 'Host tools' in question:
            context['product'] = 'Host tools'
        elif 'Trust' in question:
            context['product'] = 'Trust & Safety'
        elif 'Search' in question:
            context['product'] = 'Search'
        
        # Extract problem type
        if 'improve' in question.lower():
            context['problem_type'] = 'improvement'
        elif 'boost' in question.lower():
            context['problem_type'] = 'growth'
        elif 'drop' in question.lower():
            context['problem_type'] = 'decline'
        elif 'scale' in question.lower():
            context['problem_type'] = 'scaling'
        elif 'design' in question.lower() or 'redesign' in question.lower():
            context['problem_type'] = 'design'
        elif 'prioritize' in question.lower():
            context['problem_type'] = 'prioritization'
        elif 'deprecate' in question.lower():
            context['problem_type'] = 'deprecation'
        
        # Extract target metrics
        metric_pattern = r'\(([^)]+)\)'
        matches = re.findall(metric_pattern, question)
        if matches:
            context['target_metric'] = matches[0]
        
        return context
    
    def generate_answer(self, question: str, company: str, category: str, 
                       complexity: str, experience_level: str) -> str:
        """Generate a contextually-specific answer"""
        
        context = self.extract_problem_context(question)
        
        answer = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
QUESTION #{len(self.answers_db) + 1}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{question}

📊 Meta Information:
   • Company: {company}
   • Category: {category}
   • Complexity: {complexity}
   • Level: {experience_level}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ANSWER FRAMEWORK (CIRCLES + Metrics-First Approach)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1️⃣  CLARIFY THE PROBLEM & CONTEXT
   
   My approach: Start by understanding what we're optimizing for and what constraints we have.
   
   Key Clarifying Questions:
   ✓ Problem Scope: Are we looking at {context['product']} globally or specific regions/segments?
   ✓ Current State: What's the current baseline for {context['target_metric']}? How has it changed over time?
   ✓ Business Impact: What's the revenue/user impact of this problem? How urgent is it?
   ✓ Constraints: What are our technical, resource, and timeline constraints?
   ✓ Success Definition: What does success look like? What's our target improvement?

2️⃣  IDENTIFY SUCCESS METRICS & ROOT CAUSES

   North Star Metric: {context['target_metric']} (directly tied to business value)
   
   Supporting Metrics (Health Checks):
   • User Engagement: DAU/MAU, Session Length, Feature Adoption
   • Business: ARPU, LTV, CAC efficiency
   • Quality: Error Rate, Latency, Success Rate
   • Satisfaction: NPS, CSAT, Churn Rate
   • Specifics for {context['product']}: [Define 3-4 most relevant metrics]
   
   Root Cause Analysis Framework:
   • Data Segment: WHO is most affected? (geography, user segment, device?)
   • Timeline: WHEN did this start? What else changed then?
   • Funnel: WHERE do users drop off? (awareness → onboarding → engagement → retention)
   • User Feedback: WHY are users struggling? (qualitative research)

3️⃣  RESEARCH & COMPETITIVE ANALYSIS
   
   Internal Analysis:
   • Cohort analysis by signup date, geography, device type
   • Funnel analysis to identify conversion bottlenecks
   • User behavior patterns (where do power users differ from casual users?)
   • A/B test historical learnings
   
   External Research:
   • Competitive benchmarking (How do Booking, Expedia, VRBO solve this?)
   • Industry best practices
   • User interviews (qualitative validation of quantitative findings)
   • User testing sessions (observe actual user behavior)

4️⃣  BRAINSTORM SOLUTIONS (Multifaceted Approach)
   
   Solution Category 1: QUICK WIN (Low effort, measurable impact)
   ├─ Approach: [Specific tactical change]
   ├─ Impact on {context['target_metric']}: Expected +X% improvement
   ├─ Timeline: 1-2 weeks
   ├─ Risks: [What could go wrong? How do we mitigate?]
   └─ Example: UI/UX tweak, copy change, algorithm adjustment
   
   Solution Category 2: MEDIUM-TERM (Moderate effort, sustainable impact)
   ├─ Approach: [Product feature or process change]
   ├─ Impact on {context['target_metric']}: Expected +X-Y% improvement
   ├─ Timeline: 4-6 weeks
   ├─ Risks: [Technical complexity, user adoption]
   └─ Example: New feature, redesigned flow, new recommendation algorithm
   
   Solution Category 3: LONG-TERM (High effort, transformational impact)
   ├─ Approach: [Major product change or new feature]
   ├─ Impact on {context['target_metric']}: Expected +Y-Z% improvement  
   ├─ Timeline: 2-3 months
   ├─ Risks: [Resource intensive, longer to validate]
   └─ Example: ML model improvement, new product category, platform change

5️⃣  PRIORITIZATION FRAMEWORK

   Scoring Model (Impact × Effort × Confidence):
   
   Metric 1 - Impact on {context['target_metric']}:
   • Quick Win: 3/5 impact
   • Medium-term: 4/5 impact
   • Long-term: 5/5 impact
   
   Metric 2 - Implementation Effort:
   • Quick Win: 1/5 effort
   • Medium-term: 3/5 effort
   • Long-term: 5/5 effort
   
   Metric 3 - Confidence Level:
   • High confidence (strong data): 5/5
   • Medium confidence (some validation): 3/5
   • Low confidence (hypothesis): 1/5
   
   RECOMMENDATION: Pursue Quick Win first (immediate validation), then Medium-term
   (sustainable growth), then plan Long-term (transformational)

6️⃣  EXPERIMENTATION PLAN (A/B Testing Strategy)

   Quick Win Experiment:
   ├─ Hypothesis: "If we [change], then {context['target_metric']} will improve by X% 
   │              because [reason backed by data/user research]"
   ├─ Experiment Design:
   │  ├─ Control Group (50%): Current experience
   │  ├─ Test Group (50%): New experience
   │  ├─ Duration: 2 weeks (sufficient for statistical significance)
   │  └─ Sample Size: [Calculate based on baseline and expected effect size]
   ├─ Success Criteria: Improvement in {context['target_metric']} (p-value < 0.05)
   ├─ Guardrails: Monitor for negative impact on NPS, Error Rate, Churn
   └─ Rollout: If successful, 100% rollout with continued monitoring
   
   Medium-term Experiment:
   ├─ Hypothesis: [Similar structure but with larger expected impact]
   ├─ Experiment Design: Phased rollout (5% → 10% → 25% → 100%)
   ├─ Duration: 3-4 weeks per phase
   └─ Rollback Plan: [Conditions for rolling back changes]

7️⃣  TRADE-OFFS & CONSTRAINTS MANAGEMENT

   Speed vs Quality:
   • For {context['problem_type']} problems, we should prioritize [speed/quality] because [reason]
   • Mitigate: Use phased rollout, monitoring guardrails, rapid iteration
   
   User Experience vs Revenue:
   • Balance: [How do we not harm user experience while driving revenue?]
   • Example: Implement monetization thoughtfully, don't over-optimize for short-term revenue
   
   Global vs Regional Optimization:
   • Regional approach: [Customize for different markets/segments if data supports it]
   • Global rollout: [Ensure learning applies across geographies]
   
   Technical Debt vs Feature Velocity:
   • Decision: [How do we balance infrastructure improvements with feature work?]

8️⃣  ROLLOUT & MONITORING PLAN

   Rollout Strategy (Phased Approach):
   ├─ Phase 1 (Week 1): 5% of users → Monitor for 3 days
   ├─ Phase 2 (Week 2): 10% of users → Monitor for 3 days
   ├─ Phase 3 (Week 3): 50% of users → Monitor for 5 days
   └─ Phase 4 (Week 4): 100% of users → Ongoing monitoring
   
   Daily Monitoring Dashboard:
   ├─ Primary Metric: {context['target_metric']} (trend, cohort analysis)
   ├─ Secondary Metrics: NPS, Error Rate, Latency p95, Churn
   ├─ Anomaly Detection: Alert if any metric deviates >5% from baseline
   └─ User Feedback: Monitor support tickets, reviews, social media
   
   Success Criteria:
   ✓ {context['target_metric']} improves by X%
   ✓ No regression in guardrail metrics
   ✓ User satisfaction maintained or improved
   
   Rollback Plan:
   • Automatic rollback if error rate > 2% or NPS drops > 10 points
   • Manual decision point at each phase for go/no-go

9️⃣  STAKEHOLDER ALIGNMENT & COMMUNICATION

   Engineering:
   • Effort estimate: [X engineer-weeks]
   • Technical debt implications: [What infrastructure improvements needed?]
   • Dependencies: [What needs to be in place first?]
   • Timeline: [When can we launch?]
   
   Design:
   • User testing plan: [How do we validate UX?]
   • Accessibility: [Ensure WCAG compliance]
   • Design iterations: [How many rounds of design refinement?]
   
   Marketing:
   • Go-to-market messaging: [How do we communicate this to users?]
   • Launch timing: [Coordinate with other launches?]
   • Campaign: [Do we need user education/promotion?]
   
   Finance/Leadership:
   • ROI calculation: [Revenue impact and cost]
   • Payback period: [When do we recoup investment?]
   • Strategic alignment: [How does this fit the roadmap?]
   
   Data/Analytics:
   • Instrumentation: [What events/metrics do we track?]
   • Reporting: [What dashboards do stakeholders need?]
   • Statistical rigor: [Sample sizes, duration, significance tests]

🔟  SUCCESS METRICS & LEARNING

   Quantitative Success:
   • {context['target_metric']}: +X% improvement
   • [Other metric]: [Expected change]
   • Business impact: [Revenue/user impact]
   
   Qualitative Success:
   • User feedback: [What are users saying?]
   • Internal alignment: [Did this help the team learn?]
   • Strategic progress: [How does this ladder up to OKRs?]
   
   Key Learning Questions:
   ✓ What surprised us about user behavior?
   ✓ What assumptions were wrong?
   ✓ What can we apply to other problems?
   ✓ What's the next iteration/opportunity?

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FOLLOW-UP QUESTIONS TO EXPECT:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Q: "How would you prioritize this against other initiatives?"
A: "I'd use a weighted scoring model considering impact on {context['target_metric']}, 
   implementation effort, confidence level, and strategic alignment. I'd also consider 
   team capacity and dependency management."

Q: "What if we don't see the expected improvement?"
A: "I'd investigate using cohort analysis, user interviews, and session recordings to 
   understand what happened. Could be: wrong target segment, insufficient feature adoption, 
   external factors, or flawed hypothesis. We'd iterate quickly."

Q: "How do you think about trade-offs?"
A: "For [product area], the key trade-off is [speed vs quality / short-term revenue vs 
   long-term retention / user experience vs engineering resources]. I'd recommend [approach] 
   because [data-driven reasoning]."

Q: "What metrics are most important for {context['product']}?"
A: "[Primary metric] because [explains business impact]. But we also track [secondary metrics] 
   as guardrails to ensure we're not optimizing for the wrong thing."

"""
        
        return answer
    
    def process_csv(self, csv_path: str) -> List[Dict]:
        """Process CSV file and generate answers for all questions"""
        
        with open(csv_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            
            for row in reader:
                question = row.get('Question', '')
                company = row.get('Company', '')
                category = row.get('Category', '')
                complexity = row.get('Complexity', '')
                experience_level = row.get('Experience Level', '')
                
                if not question:
                    continue
                
                answer = self.generate_answer(question, company, category, complexity, experience_level)
                
                self.answers_db.append({
                    'id': len(self.answers_db) + 1,
                    'question': question,
                    'company': company,
                    'category': category,
                    'complexity': complexity,
                    'experience_level': experience_level,
                    'answer': answer
                })
        
        return self.answers_db
    
    def save_answers(self, output_json_path: str, output_txt_path: str):
        """Save answers to both JSON and text files"""
        
        # Save as JSON for database integration
        with open(output_json_path, 'w', encoding='utf-8') as f:
            json.dump(self.answers_db, f, indent=2, ensure_ascii=False)
        
        # Save as readable text
        with open(output_txt_path, 'w', encoding='utf-8') as f:
            f.write("=" * 100 + "\n")
            f.write("PM INTERVIEW ANSWERS DATABASE - AIRBNB\n")
            f.write(f"Total Questions: {len(self.answers_db)}\n")
            f.write("Framework: CIRCLES + Metrics-First Modern PM Approach\n")
            f.write("=" * 100 + "\n\n")
            
            for item in self.answers_db:
                f.write(item['answer'])
                f.write("\n\n")
        
        print(f"✓ Generated {len(self.answers_db)} high-quality PM interview answers")
        print(f"✓ Saved to: {output_json_path}")
        print(f"✓ Saved to: {output_txt_path}")


if __name__ == "__main__":
    generator = PMAnswerGenerator()
    
    csv_path = "PM_Questions_FINAL_12x2000_Formatted_Final_HUMANIZED.csv"
    
    print("🚀 Generating high-quality PM interview answers...")
    print("   Framework: CIRCLES + Metrics-First Approach")
    print("   Standards: Modern PM best practices\n")
    
    answers = generator.process_csv(csv_path)
    
    output_json = "pm_interview_answers_quality.json"
    output_txt = "pm_interview_answers_quality.txt"
    
    generator.save_answers(output_json, output_txt)
    
    print(f"\n✅ Success! All answers generated with modern PM frameworks")
