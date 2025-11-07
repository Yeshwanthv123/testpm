import React, { useState, useEffect } from 'react';
import Navigation from './components/Navigation';
import LoginSignup from './components/LoginSignup';
import Onboarding from './components/Onboarding';
import InterviewSetup from './components/InterviewSetup';
import InterviewFlow from './components/InterviewFlow';
import Dashboard from './components/Dashboard';
import { User, InterviewType, Answer, InterviewResult, SkillScore, Question } from './types';
import { mockSkillScores, mockPeerComparison } from './data/mockData';
import { calculateSkillScore, generateFeedback, calculatePercentile } from './utils/scoring';

type AppStep = 'login' | 'onboarding' | 'setup' | 'interview' | 'results';

const API_BASE = (import.meta as any).env.VITE_API_BASE || 'http://localhost:8000';

function App() {
  const [currentStep, setCurrentStep] = useState<AppStep>('login');
  const [user, setUser] = useState<User | null>(null);
  const [selectedInterviewType, setSelectedInterviewType] = useState<InterviewType | null>(null);
  const [interviewResult, setInterviewResult] = useState<InterviewResult | null>(null);
  const [jobDescription, setJobDescription] = useState<string | undefined>(undefined);
  const [isLoading, setIsLoading] = useState(true);
  const [interviewQuestions, setInterviewQuestions] = useState<Question[]>([]);

  useEffect(() => {
    const checkAuthStatus = async () => {
      const token = localStorage.getItem('access_token');
      if (token) {
        try {
          const response = await fetch(`${API_BASE}/auth/me`, {
            headers: { Authorization: `Bearer ${token}` },
          });
          if (response.ok) {
            const userData = await response.json();
            handleLoginSuccess(userData);
          } else {
            handleLogout();
          }
        } catch (error) {
          console.error('Failed to verify auth status', error);
          handleLogout();
        }
      }
      setIsLoading(false);
    };
    checkAuthStatus();
  }, []);

  // ✅ Always go to onboarding after login
  const handleLoginSuccess = (userData: User) => {
    setUser(userData);
    setCurrentStep('onboarding');
  };

  const handleOnboardingComplete = async (updatedUserData: User) => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      setCurrentStep('login');
      return;
    }
    try {
      const response = await fetch(`${API_BASE}/auth/me`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(updatedUserData),
      });
      if (!response.ok) throw new Error('Failed to update user profile.');

      const updatedUser = await response.json();
      setUser(updatedUser);
      setCurrentStep('setup');
    } catch (error) {
      console.error('Onboarding completion failed:', error);
    }
  };

  const handleUpdateUser = (updatedUser: User) => {
    setUser(updatedUser);
  };

  const handleInterviewStart = (
    interviewType: InterviewType,
    questions: Question[],
    jd?: string
  ) => {
    try {
      sessionStorage.setItem('pmbot_questions', JSON.stringify(questions));
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      (window as any).__PMBOT_QUESTIONS = questions;
    } catch {
      /* ignore */
    }

    setSelectedInterviewType(interviewType);
    setInterviewQuestions(questions);
    setJobDescription(jd);
    setCurrentStep('interview');
  };

  const handleInterviewComplete = (answers: Answer[]) => {
    if (!selectedInterviewType) return;

    // Try to call backend evaluation endpoint to get AI-generated scores/feedback.
    (async () => {
      try {
        const token = localStorage.getItem('access_token');
  const resp = await fetch(`${API_BASE}/api/interview/evaluate-answers`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            ...(token ? { Authorization: `Bearer ${token}` } : {}),
          },
          body: JSON.stringify({
            items: answers.map((a) => {
              const q = interviewQuestions.find((q) => String(q.id) === String(a.questionId));
              return { question: q || {}, user_answer: a.answer };
            }),
          }),
        });

        if (resp.ok) {
          const data = await resp.json();
          // If the backend returned per-question AI evaluations, derive skill-level
          // scores from those evaluations (preferred). Otherwise fall back to the
          // local heuristic scoring.
          let skillScores: SkillScore[] = [];
          if (Array.isArray(data.per_question) && data.per_question.length > 0) {
            // Build mapping from skill -> collected evaluations (scores, strengths, weaknesses, feedback)
            const skillBuckets: Record<string, { scores: number[]; strengths: string[]; weaknesses: string[]; feedbacks: string[]; examples: string[] }> = {};

            const tokenize = (s?: string) =>
              (s || '')
                .toLowerCase()
                .replace(/[^a-z0-9]+/g, ' ')
                .split(/\s+/)
                .filter(Boolean);

            // helper to compute token overlap ratio between two token sets
            const overlapRatio = (aTokens: string[], bTokens: string[]) => {
              if (!aTokens.length || !bTokens.length) return 0;
              const aset = new Set(aTokens);
              const common = bTokens.filter((t) => aset.has(t)).length;
              return common / Math.max(1, bTokens.length);
            };

            data.per_question.forEach((pq: any) => {
              const q = pq.question || {};
              // If the backend returned a per-skill breakdown, use that directly
                if (pq.skill_breakdown && typeof pq.skill_breakdown === 'object') {
                  Object.entries(pq.skill_breakdown).forEach(([sk, evalObj]) => {
                    const key = String(sk || '').trim();
                    const ev = evalObj as any;
                    const score = typeof ev.score === 'number' ? ev.score : parseInt(ev.score) || 0;
                    const strengths = Array.isArray(ev.strengths) ? ev.strengths.map(String) : [];
                    const weaknesses = Array.isArray(ev.weaknesses) ? ev.weaknesses.map(String) : [];
                    const feedback = ev.feedback ? String(ev.feedback) : '';
                    const example = ev.example_snippet ? String(ev.example_snippet) : '';
                    if (!key) return;
                    if (!skillBuckets[key]) skillBuckets[key] = { scores: [], strengths: [], weaknesses: [], feedbacks: [], examples: [] };
                    skillBuckets[key].scores.push(score);
                    skillBuckets[key].strengths.push(...strengths);
                    skillBuckets[key].weaknesses.push(...weaknesses);
                    if (feedback) skillBuckets[key].feedbacks.push(feedback);
                    if (example) skillBuckets[key].examples.push(example);
                  });
                  return;
                }

              const score = typeof pq.score === 'number' ? pq.score : parseInt(pq.score) || 0;
              let qskills: string[] = [];
              if (Array.isArray(q.skills) && q.skills.length) qskills = q.skills.map((x: any) => String(x || ''));
              if (qskills.length === 0 && typeof q.category === 'string') qskills = [q.category as string];
              if (qskills.length === 0 && typeof q.question === 'string') qskills = [q.question.slice(0, 40)];

              // Normalize keys and push
              qskills.forEach((s) => {
                const key = String(s || '').trim();
                if (!key) return;
                if (!skillBuckets[key]) skillBuckets[key] = { scores: [], strengths: [], weaknesses: [], feedbacks: [], examples: [] };
                skillBuckets[key].scores.push(score);
              });
            });

            // For each desired skill on the interview type, compute an averaged score
            skillScores = selectedInterviewType.skills.map((skill) => {
              const skTokens = tokenize(skill);
              // find bucket keys with good token overlap
              const matches = Object.keys(skillBuckets).filter((k) => {
                const kt = tokenize(k);
                const r1 = overlapRatio(kt, skTokens);
                const r2 = overlapRatio(skTokens, kt);
                return Math.max(r1, r2) >= 0.25 || k.toLowerCase().includes(skill.toLowerCase()) || skill.toLowerCase().includes(k.toLowerCase());
              });

              // If no good matches found, attempt fuzzy match against question text
              let allScores: number[] = [];
              if (matches.length === 0) {
                // try to find any bucket where question text contains a skill token
                const fallbackMatches = Object.keys(skillBuckets).filter((k) => {
                  const kt = tokenize(k);
                  return kt.some((t) => skTokens.includes(t));
                });
                allScores = fallbackMatches.reduce<number[]>((acc, k) => acc.concat(skillBuckets[k]?.scores || []), []);
              } else {
                allScores = matches.reduce<number[]>((acc, k) => acc.concat(skillBuckets[k]?.scores || []), []);
              }

              // If still empty, as a last resort, take a small contribution from any question scores
              if (allScores.length === 0) {
                const anyScores = Object.values(skillBuckets).flatMap((v) => v.scores || []);
                allScores = anyScores.length ? [Math.round(anyScores.reduce((a, b) => a + b, 0) / anyScores.length)] : [];
              }

              const avg = allScores.length ? Math.round(allScores.reduce((a, b) => a + b, 0) / allScores.length) : 0;
              // If we have collected richer metadata for this skill, aggregate it to produce detailed feedback
              const bucketKey = Object.keys(skillBuckets).find((k) => {
                const kt = tokenize(k);
                const skt = tokenize(skill);
                const common = kt.filter((t) => skt.includes(t)).length;
                return common > 0 || k.toLowerCase().includes(skill.toLowerCase()) || skill.toLowerCase().includes(k.toLowerCase());
              });
              let detailedFeedback = generateFeedback(avg, skill);
              if (bucketKey && skillBuckets[bucketKey]) {
                const b = skillBuckets[bucketKey];
                const uniqStrengths = Array.from(new Set(b.strengths)).slice(0, 5);
                const uniqWeaknesses = Array.from(new Set(b.weaknesses)).slice(0, 5);
                const combinedExamples = Array.from(new Set(b.examples)).slice(0, 2);
                const combinedFeedback = b.feedbacks.join('\n\n');
                detailedFeedback = [
                  `Score breakdown: ${avg}/100.`,
                  uniqStrengths.length ? `Strengths: ${uniqStrengths.join('; ')}` : null,
                  uniqWeaknesses.length ? `Opportunities: ${uniqWeaknesses.join('; ')}` : null,
                  combinedFeedback ? `Feedback: ${combinedFeedback}` : null,
                  combinedExamples.length ? `Suggested phrasing/example: ${combinedExamples.join(' \n')}` : null,
                ]
                  .filter(Boolean)
                  .join('\n\n');
              }

              return {
                skill,
                score: avg,
                maxScore: 100,
                percentile: calculatePercentile(avg, skill),
                feedback: detailedFeedback,
                trend: 'stable',
                industryAverage: Math.floor(Math.random() * 15) + 70,
              } as SkillScore;
            });
          } else {
            skillScores = selectedInterviewType.skills.map((skill) => {
              const score = calculateSkillScore(answers, interviewQuestions, skill);
              return {
                skill,
                score,
                maxScore: 100,
                percentile: calculatePercentile(score, skill),
                feedback: generateFeedback(score, skill),
                trend: 'stable',
                industryAverage: Math.floor(Math.random() * 15) + 70,
              };
            });
          }

          const overallScore = data.overall_score ?? Math.round(skillScores.reduce((acc, s) => acc + s.score, 0) / Math.max(1, skillScores.length));
          const detailedFeedback = Array.isArray(data.per_question)
            ? data.per_question.map((p: any) => p.feedback || '').filter(Boolean).join('\n\n')
            : 'Detailed feedback will appear here.';

          const result: InterviewResult = {
            sessionId: new Date().toISOString(),
            overallScore: Math.round(overallScore),
            skillScores,
            strengths: skillScores.filter((s) => s.score > 85).map((s) => s.skill),
            improvements: skillScores.filter((s) => s.score < 75).map((s) => s.skill),
            peerComparison: mockPeerComparison,
            detailedFeedback,
            perQuestionEvaluations: Array.isArray(data.per_question) ? data.per_question : [],
          };
          setInterviewResult(result);
          setCurrentStep('results');
          return;
        }
      } catch (err) {
        console.warn('AI evaluation failed, falling back to local scoring', err);
      }

      // Fallback: original heuristic scoring
      const skillScores: SkillScore[] = selectedInterviewType.skills.map((skill) => {
        const score = calculateSkillScore(answers, interviewQuestions, skill);
        return {
          skill,
          score,
          maxScore: 100,
          percentile: calculatePercentile(score, skill),
          feedback: generateFeedback(score, skill),
          trend: 'stable',
          industryAverage: Math.floor(Math.random() * 15) + 70,
        };
      });
      const overallScore =
        skillScores.reduce((acc, s) => acc + s.score, 0) / skillScores.length;
      const result: InterviewResult = {
        sessionId: new Date().toISOString(),
        overallScore: Math.round(overallScore),
        skillScores,
        strengths: mockSkillScores.filter((s) => s.score > 85).map((s) => s.skill),
        improvements: mockSkillScores.filter((s) => s.score < 75).map((s) => s.skill),
        peerComparison: mockPeerComparison,
        detailedFeedback: 'Detailed feedback would be generated by an AI model here.',
      };
      setInterviewResult(result);
      setCurrentStep('results');
    })();
  };

  const handleRetakeInterview = () => {
    setCurrentStep('setup');
  };

  const handleNavigate = (step: string) => {
    setCurrentStep(step as AppStep);
  };

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setUser(null);
    setCurrentStep('login');
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-orange-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-lg text-gray-600">Loading your session...</p>
        </div>
      </div>
    );
  }

  const renderStep = () => {
    switch (currentStep) {
      case 'login':
        return <LoginSignup onComplete={handleLoginSuccess} />;
      case 'onboarding':
        return user ? (
          <Onboarding user={user} onComplete={handleOnboardingComplete} />
        ) : (
          <LoginSignup onComplete={handleLoginSuccess} />
        );
      case 'setup':
        return user ? (
          <InterviewSetup user={user} onStartInterview={handleInterviewStart} />
        ) : (
          <LoginSignup onComplete={handleLoginSuccess} />
        );
      case 'interview':
        return selectedInterviewType && user ? (
          <InterviewFlow
            interviewType={selectedInterviewType}
            onComplete={handleInterviewComplete}
            jobDescription={jobDescription}
            onExitInterview={() => setCurrentStep('setup')} // ✅ enables Exit Interview button
          />
        ) : (
          <InterviewSetup user={user!} onStartInterview={handleInterviewStart} />
        );
      case 'results':
        return interviewResult && user ? (
          <Dashboard
            result={interviewResult}
            onRetakeInterview={handleRetakeInterview}
          />
        ) : (
          <InterviewSetup user={user!} onStartInterview={handleInterviewStart} />
        );
      default:
        return <LoginSignup onComplete={handleLoginSuccess} />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {currentStep !== 'login' && user && (
        <Navigation
          currentStep={currentStep}
          onNavigate={handleNavigate}
          user={user}
          onUpdateUser={handleUpdateUser}
          onLogout={handleLogout}
        />
      )}
      {renderStep()}
    </div>
  );
}

export default App;
