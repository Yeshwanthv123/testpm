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
  const [sessionId, setSessionId] = useState<string | null>(null);
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
    // Ensure a persistent anonymous session id for unauthenticated users
    try {
      let sid = localStorage.getItem('pmbot_session_id');
      if (!sid) {
        // simple UUIDv4 generator
        sid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
          const r = (Math.random() * 16) | 0;
          const v = c === 'x' ? r : (r & 0x3) | 0x8;
          return v.toString(16);
        });
        localStorage.setItem('pmbot_session_id', sid);
      }
      setSessionId(sid);
    } catch (e) {
      /* ignore */
    }
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
      // Persist selected interview type so a "Retake" can restore the same config
      try { sessionStorage.setItem('pmbot_selected_type', JSON.stringify(interviewType)); } catch {}
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

    // Call backend evaluation endpoint to get AI-generated scores/feedback.
    (async () => {
      try {
        const token = localStorage.getItem('access_token');
        const evalResp = await fetch(`${API_BASE}/api/interview/evaluate-answers`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            ...(token ? { Authorization: `Bearer ${token}` } : {}),
            ...(sessionId ? { 'X-Session-Key': sessionId } : {}),
          },
          body: JSON.stringify({
            items: answers.map((a) => {
              const q = interviewQuestions.find((q) => String(q.id) === String(a.questionId));
              return { question: q || {}, user_answer: a.answer };
            }),
          }),
        });

        if (evalResp.ok) {
          const evalData = await evalResp.json();
          const perQuestion = evalData.per_question || [];
          const overallScore = evalData.overall_score || 0;

          // Transform per_question evaluations into skillScores for dashboard
          // Extract unique categories/skills from per_question items
          const categoryScores: { [key: string]: number[] } = {};
          const questionDetails: any[] = [];
          
          perQuestion.forEach((item: any) => {
            const qObj = item.question || {};
            const category = qObj.category || qObj.skills?.[0] || 'General';
            const score = item.score || 0;
            const feedback = item.feedback || '';
            const strengths = item.strengths || [];
            const weaknesses = item.weaknesses || [];
            const modelAnswer = item.model_answer || '';
            
            // Aggregate scores by category
            if (!categoryScores[category]) {
              categoryScores[category] = [];
            }
            categoryScores[category].push(score);
            
            // Store question details for perQuestionEvaluations
            questionDetails.push({
              question: qObj,
              model_answer: modelAnswer,
              score,
              strengths,
              weaknesses,
              feedback,
            });
          });

          // Create skillScores from aggregated category scores
          const skillScores: SkillScore[] = Object.entries(categoryScores).map(([skill, scores]) => {
            const avgScore = scores.reduce((a, b) => a + b, 0) / scores.length;
            return {
              skill,
              score: Math.round(avgScore),
              maxScore: 100,
              percentile: calculatePercentile(Math.round(avgScore), skill),
              feedback: `Scored ${Math.round(avgScore)}/100 on ${skill}`,
              trend: 'stable',
              industryAverage: Math.floor(Math.random() * 15) + 70,
            };
          });

          const result: InterviewResult = {
            sessionId: sessionId || new Date().toISOString(),
            overallScore: Math.round(overallScore),
            skillScores,
            strengths: skillScores.filter((s) => s.score > 85).map((s) => s.skill),
            improvements: skillScores.filter((s) => s.score < 75).map((s) => s.skill),
            peerComparison: mockPeerComparison,
            detailedFeedback: `Overall Performance: ${Math.round(overallScore)}/100. ${skillScores.map(s => `${s.skill}: ${s.score}/100`).join('. ')}`,
            perQuestionEvaluations: questionDetails,
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
    // Restore the last used questions and interview type (if available) so the user
    // retakes the exact same interview they just completed.
    try {
      const raw = sessionStorage.getItem('pmbot_questions');
      const rawType = sessionStorage.getItem('pmbot_selected_type');
      if (raw) {
        const qs = JSON.parse(raw) as Question[];
        setInterviewQuestions(qs);
      }
      if (rawType) {
        const itype = JSON.parse(rawType) as InterviewType;
        setSelectedInterviewType(itype);
      }
    } catch (e) {
      /* ignore */
    }
    setCurrentStep('interview');
  };

  // Show a past interview's results in the Dashboard by setting interviewResult
  const handleShowPastResult = (past: any) => {
    try {
      // past is expected to have: id, date, company, category, score, questions
      // questions is an array of: { id, question, category, skills, model_answer, score, strengths, weaknesses, feedback }
      const perQuestion = (past.questions || []).map((q: any) => ({
        question: {
          id: q.id || undefined,
          question: q.question || '',
          company: past.company || undefined,
          category: q.category || past.category || 'General',
          skills: q.skills || [],
        },
        model_answer: q.model_answer || '',
        score: q.score || 0,
        strengths: q.strengths || [],
        weaknesses: q.weaknesses || [],
        feedback: q.feedback || '',
      }));

      // Extract skill categories from questions and aggregate scores by skill
      // Each question contains a skills array that maps to its category
      const skillScores: { [key: string]: number[] } = {};
      
      perQuestion.forEach((pq: any) => {
        const score = pq.score || 0;
        const skills = (pq.question?.skills || []) as string[];
        const category = pq.question?.category || 'General';
        
        // If question has specific skills, use those; otherwise use category
        if (skills && skills.length > 0) {
          skills.forEach((skill: string) => {
            if (!skillScores[skill]) skillScores[skill] = [];
            skillScores[skill].push(score);
          });
        } else {
          if (!skillScores[category]) skillScores[category] = [];
          skillScores[category].push(score);
        }
      });

      // Create skillScores for each skill
      const skillResultScores: SkillScore[] = Object.entries(skillScores).map(([skill, scores]) => {
        const avgScore = scores.reduce((a, b) => a + b, 0) / scores.length;
        const roundedScore = Math.round(avgScore);
        return {
          skill,
          score: roundedScore,
          maxScore: 100,
          percentile: Math.min(Math.round((roundedScore / 100) * 100), 95),
          feedback: `Scored ${roundedScore}/100 on ${skill}`,
          trend: 'stable' as const,
          industryAverage: Math.floor(Math.random() * 15) + 70,
        };
      });

      const result: InterviewResult = {
        sessionId: past.id || String(Date.now()),
        overallScore: Math.round(past.score || 0),
        skillScores: skillResultScores.length > 0 ? skillResultScores : [{
          skill: 'Overall',
          score: Math.round(past.score || 0),
          maxScore: 100,
          percentile: Math.min(Math.round(((past.score || 0) / 100) * 100), 95),
          feedback: 'Overall interview performance',
          trend: 'stable' as const,
          industryAverage: 75,
        }],
        strengths: skillResultScores.filter((s) => s.score > 85).map((s) => s.skill),
        improvements: skillResultScores.filter((s) => s.score < 75).map((s) => s.skill),
        peerComparison: mockPeerComparison,
        detailedFeedback: `Past interview at ${past.company || 'Practice'} on ${past.date ? new Date(past.date).toLocaleDateString() : 'unknown date'}. Overall Performance: ${Math.round(past.score || 0)}/100.`,
        perQuestionEvaluations: perQuestion,
      };

      setInterviewResult(result);
      setCurrentStep('results');
    } catch (err) {
      console.error('Failed to show past result', err);
      alert('Failed to load past interview result');
    }
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
          onStartInterview={handleInterviewStart}
          onViewResult={handleShowPastResult}
        />
      )}
      {renderStep()}
    </div>
  );
}

export default App;
