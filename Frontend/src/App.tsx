import React, { useState, useEffect } from 'react';
import Navigation from './components/Navigation';
import LoginSignup from './components/LoginSignup';
import RegionSelect from './components/RegionSelect';
import Onboarding from './components/Onboarding';
import InterviewSetup from './components/InterviewSetup';
import InterviewFlow from './components/InterviewFlow';
import Dashboard from './components/Dashboard';
import LeaderboardPage from './components/LeaderboardPage';
import { User, InterviewType, Answer, InterviewResult, SkillScore, Question } from './types';
import { mockSkillScores, mockPeerComparison } from './data/mockData';
import { calculateSkillScore, generateFeedback, calculatePercentile } from './utils/scoring';

type AppStep = 'login' | 'region-select' | 'onboarding' | 'setup' | 'interview' | 'results' | 'leaderboard';

const API_BASE = (import.meta as any).env.VITE_API_BASE || 'http://localhost:8000';

function App() {
  const [currentStep, setCurrentStep] = useState<AppStep>('login');
  const [user, setUser] = useState<User | null>(null);
  const [selectedInterviewType, setSelectedInterviewType] = useState<InterviewType | null>(null);
  const [interviewResult, setInterviewResult] = useState<InterviewResult | null>(null);
  const [jobDescription, setJobDescription] = useState<string | undefined>(undefined);
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [interviewQuestions, setInterviewQuestions] = useState<Question[]>([]);

  useEffect(() => {
    const checkAuthStatus = async () => {
      // First, check if we're coming back from OAuth callback
      const hash = window.location.hash;
      if (hash.startsWith('#auth=')) {
        try {
          const encodedAuth = hash.substring(6); // Remove '#auth='
          const authData = JSON.parse(decodeURIComponent(encodedAuth));
          if (authData.access_token && authData.refresh_token) {
            localStorage.setItem('access_token', authData.access_token);
            localStorage.setItem('refresh_token', authData.refresh_token);
            // Clean up URL
            window.history.replaceState({}, document.title, window.location.pathname);
          }
        } catch (e) {
          console.error('Failed to parse OAuth callback', e);
        }
      }

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

  // ✅ After login, check if user has region set
  const handleLoginSuccess = (userData: User) => {
    setUser(userData);
    // If user already has a region, skip to onboarding
    if (userData.region) {
      setCurrentStep('onboarding');
    } else {
      setCurrentStep('region-select');
    }
  };

  const handleRegionSelect = async (updatedUserData: User) => {
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
        body: JSON.stringify({
          region: updatedUserData.region,
        }),
      });
      if (!response.ok) throw new Error('Failed to update region.');

      const updatedUser = await response.json();
      setUser(updatedUser);
      setCurrentStep('onboarding');
    } catch (error) {
      console.error('Region selection failed:', error);
    }
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
      // Store interview metadata (company, years, level) from first question if available
      try {
        const firstQuestion = questions[0] as any;
        if (firstQuestion && firstQuestion._interview_metadata) {
          sessionStorage.setItem('pmbot_interview_metadata', JSON.stringify(firstQuestion._interview_metadata));
          console.log('[handleInterviewStart] Stored interview metadata:', firstQuestion._interview_metadata);
        } else {
          console.log('[handleInterviewStart] First question has no _interview_metadata');
        }
      } catch (e) {
        console.error('[handleInterviewStart] Failed to store metadata:', e);
      }
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
      setIsSubmitting(true);
      try {
        const token = localStorage.getItem('access_token');
        const payloadItems = answers.map((a) => {
          // Robust question lookup: try current state, then sessionStorage, then global var
          let q = interviewQuestions.find((q) => String(q.id) === String(a.questionId));
          if (!q) {
            try {
              const cached = sessionStorage.getItem('pmbot_questions');
              if (cached) {
                const parsed = JSON.parse(cached) as any[];
                q = parsed.find((pq) => String(pq.id) === String(a.questionId));
              }
            } catch (e) {
              // ignore
            }
          }
          if (!q && (window as any).__PMBOT_QUESTIONS) {
            q = (window as any).__PMBOT_QUESTIONS.find((pq: any) => String(pq.id) === String(a.questionId));
          }
          return { question: q || {}, user_answer: a.answer };
        });

        // Extract interview metadata from sessionStorage or first question
        let interviewMetadata = null;
        try {
          const stored = sessionStorage.getItem('pmbot_interview_metadata');
          if (stored) {
            interviewMetadata = JSON.parse(stored);
            console.log('[handleInterviewComplete] Retrieved interview metadata from storage:', interviewMetadata);
          } else {
            console.log('[handleInterviewComplete] No interview metadata in sessionStorage');
          }
        } catch (e) {
          console.error('[handleInterviewComplete] Failed to retrieve metadata from storage:', e);
        }
        
        // Fallback: try to get from first question
        if (!interviewMetadata && interviewQuestions.length > 0) {
          const firstQuestion = interviewQuestions[0] as any;
          if (firstQuestion._interview_metadata) {
            interviewMetadata = firstQuestion._interview_metadata;
            console.log('[handleInterviewComplete] Retrieved interview metadata from first question:', interviewMetadata);
          }
        }

        const evalResp = await fetch(`${API_BASE}/api/interview/evaluate-answers`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            ...(token ? { Authorization: `Bearer ${token}` } : {}),
            ...(sessionId ? { 'X-Session-Key': sessionId } : {}),
          },
          body: JSON.stringify({ items: payloadItems, interview_metadata: interviewMetadata }),
        });

        if (evalResp.ok) {
          const evalData = await evalResp.json();
          const perQuestion = evalData.per_question || [];
          const overallScore = evalData.overall_score || 0;

          // Transform per_question evaluations into skillScores for dashboard
          const categoryScores: { [key: string]: number[] } = {};
          const questionDetails: any[] = [];

          perQuestion.forEach((item: any) => {
            const qObj = item.question || {};
            const category = qObj.category || qObj.skills?.[0] || 'General';
            const score = item.score || 0;
            const feedback = item.feedback || '';
            const strengths = item.strengths || item.suggestions?.feedback?.strengths || [];
            const weaknesses = item.weaknesses || item.suggestions?.feedback?.improvements || item.improvements || [];
            const modelAnswer = item.model_answer || item.ideal_answer || '';

            if (!categoryScores[category]) categoryScores[category] = [];
            categoryScores[category].push(score);

            questionDetails.push({
              question: qObj,
              model_answer: modelAnswer,
              score,
              strengths,
              weaknesses,
              feedback,
            });
          });

          const skillScores: SkillScore[] = Object.entries(categoryScores).map(([skill, scores]) => {
            const avgScore = scores.reduce((a, b) => a + b, 0) / scores.length;
            return {
              skill,
              score: Math.round(avgScore),
              maxScore: 100,
              percentile: calculatePercentile(Math.round(avgScore), skill),
              feedback: `Scored ${Math.round(avgScore)}/100 on ${skill}`,
              trend: 'stable',
              industryAverage: 75, // Use consistent industry average for graph consistency
            };
          });

          // Fetch peer comparison data from backend
          let peerComparison = mockPeerComparison;
          let improvementRate = 0;
          try {
            const rankingResp = await fetch(`${API_BASE}/api/interview/my-ranking`, {
              headers: token ? { 'Authorization': `Bearer ${token}` } : {},
            });
            if (rankingResp.ok) {
              const rankingData = await rankingResp.json();
              // Map backend response to peerComparison structure with separate percentiles
              peerComparison = {
                region: {
                  average: rankingData.avgScore || 0,
                  percentile: rankingData.regionalPercentile || 0,
                },
                experience: {
                  average: rankingData.avgScore || 0,
                  percentile: rankingData.experiencePercentile || 0,
                },
                overall: {
                  average: rankingData.avgScore || 0,
                  percentile: rankingData.percentileRank || 0,
                  totalCandidates: rankingData.totalCandidates || 0,
                },
              };
            }
            
            // Fetch metrics to get improvement rate
            const metricsResp = await fetch(`${API_BASE}/api/interview/metrics`, {
              headers: token ? { 'Authorization': `Bearer ${token}` } : {},
            });
            if (metricsResp.ok) {
              const metricsData = await metricsResp.json();
              improvementRate = metricsData.improvementRate || 0;
            }
          } catch (err) {
            console.error('Failed to fetch peer comparison or metrics:', err);
          }

          const result: InterviewResult = {
            sessionId: sessionId || new Date().toISOString(),
            overallScore: Math.round(overallScore),
            skillScores,
            strengths: skillScores.filter((s) => s.score > 85).map((s) => s.skill),
            improvements: skillScores.filter((s) => s.score < 75).map((s) => s.skill),
            peerComparison,
            improvementRate,
            detailedFeedback: `Overall Performance: ${Math.round(overallScore)}/100. ${skillScores.map(s => `${s.skill}: ${s.score}/100`).join('. ')}`,
            perQuestionEvaluations: questionDetails,
            // User metadata for download reports
            username: user?.email?.split('@')[0] || 'User',
            region: user?.region || 'Not specified',
            experience: user?.experience || 'Not specified',
            user: {
              full_name: user?.email?.split('@')[0],
              email: user?.email,
              region: user?.region,
              experience: user?.experience,
            },
          };

          setInterviewResult(result);
          setIsSubmitting(false);
          setCurrentStep('results');
          return;
        }
      } catch (err) {
        console.error('AI evaluation request failed:', err);
        // eslint-disable-next-line no-console
        console.warn('AI evaluation failed, falling back to local scoring', err);
      } finally {
        setIsSubmitting(false);
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
          industryAverage: 75, // Use consistent industry average for graph consistency
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
        improvementRate: 0,
        detailedFeedback: 'Detailed feedback would be generated by an AI model here.',
        // User metadata for download reports
        username: user?.email?.split('@')[0] || 'User',
        region: user?.region || 'Not specified',
        experience: user?.experience || 'Not specified',
        user: {
          full_name: user?.email?.split('@')[0],
          email: user?.email,
          region: user?.region,
          experience: user?.experience,
        },
      };
      setInterviewResult(result);
      setCurrentStep('results');
    })();
  };

  const handleRetakeInterview = () => {
    // If we have a past interview result (from Profile -> View Result), try to
    // request the original questions from the backend so the user retakes the
    // exact same interview. Fall back to sessionStorage behavior if unauthenticated
    // or the API call fails.
    (async () => {
      try {
        // Prefer server-side retake when possible
        const token = localStorage.getItem('access_token');
        if (token && interviewResult && interviewResult.sessionId) {
          try {
            const res = await fetch(`${API_BASE}/api/interview/retake`, {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
                Authorization: `Bearer ${token}`,
              },
              body: JSON.stringify({ interview_id: interviewResult.sessionId }),
            });

            if (res.ok) {
              const payload = await res.json();
              const qs = (payload?.questions || []).map((q: any, idx: number) => ({
                id: q?.id != null ? String(q.id) : `restored_${idx}`,
                question: q?.question || q?.text || '',
                category: q?.category || 'General',
                timeLimit: typeof q?.timeLimit === 'number' ? q.timeLimit : undefined,
                difficulty: (q?.complexity as any) || 'medium',
                skills: q?.skills || [],
                company: q?.company || undefined,
              }));

              if (qs.length) {
                try { sessionStorage.setItem('pmbot_questions', JSON.stringify(qs)); } catch {}
                setInterviewQuestions(qs as any);
                
                // Calculate duration: use original interview duration if available
                // Otherwise, preserve 3 minutes (180 seconds) per question as default
                let retakeDuration = 30; // default 30 minutes
                if (selectedInterviewType?.duration) {
                  retakeDuration = selectedInterviewType.duration;
                } else {
                  // Fallback: 3 minutes per question (180 seconds per question)
                  retakeDuration = Math.max(10, Math.ceil((qs.length * 180) / 60));
                }
                
                setSelectedInterviewType({
                  id: 'retake',
                  name: 'Retake Interview',
                  description: 'Retake the selected past interview',
                  duration: retakeDuration,
                  questionCount: qs.length,
                  skills: qs.flatMap((x:any) => x.skills || []),
                  icon: 'refresh',
                  color: '#f59e0b',
                } as InterviewType);
                setCurrentStep('interview');
                return;
              }
            }
          } catch (err) {
            console.warn('Retake API failed, falling back to session restore', err);
          }
        }

        // Fallback: restore last used questions from sessionStorage (existing behavior)
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
      } catch (err) {
        console.error('Retake flow failed', err);
        // Ensure we still attempt the fallback path
        try {
          const raw = sessionStorage.getItem('pmbot_questions');
          if (raw) setInterviewQuestions(JSON.parse(raw) as Question[]);
        } catch {}
        setCurrentStep('interview');
      }
    })();
  };

  // Show a past interview's results in the Dashboard by setting interviewResult
  const handleShowPastResult = async (past: any) => {
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
          industryAverage: 75, // Use consistent industry average for graph consistency
        };
      });

      // Fetch real peer comparison and improvement rate data from backend
      let peerComparison = mockPeerComparison;
      let improvementRate = 0;
      try {
        const token = localStorage.getItem('access_token');
        if (token) {
          const rankingResp = await fetch(`${API_BASE}/api/interview/my-ranking`, {
            headers: { 'Authorization': `Bearer ${token}` },
          });
          if (rankingResp.ok) {
            const rankingData = await rankingResp.json();
            peerComparison = {
              region: {
                average: rankingData.avgScore || 0,
                percentile: rankingData.regionalPercentile || 0,
              },
              experience: {
                average: rankingData.avgScore || 0,
                percentile: rankingData.experiencePercentile || 0,
              },
              overall: {
                average: rankingData.avgScore || 0,
                percentile: rankingData.percentileRank || 0,
                totalCandidates: rankingData.totalCandidates || 0,
              },
            };
          }
          
          const metricsResp = await fetch(`${API_BASE}/api/interview/metrics`, {
            headers: { 'Authorization': `Bearer ${token}` },
          });
          if (metricsResp.ok) {
            const metricsData = await metricsResp.json();
            improvementRate = metricsData.improvementRate || 0;
          }
        }
      } catch (err) {
        console.error('Failed to fetch peer comparison for past result:', err);
      }

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
        peerComparison,
        improvementRate,
        detailedFeedback: `Past interview at ${past.company || 'Practice'} on ${past.date ? new Date(past.date).toLocaleDateString() : 'unknown date'}. Overall Performance: ${Math.round(past.score || 0)}/100.`,
        perQuestionEvaluations: perQuestion,
        // User metadata for download reports
        username: user?.email?.split('@')[0] || 'User',
        region: user?.region || 'Not specified',
        experience: user?.experience || 'Not specified',
        user: {
          full_name: user?.email?.split('@')[0],
          email: user?.email,
          region: user?.region,
          experience: user?.experience,
        },
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
    try {
      // Clear all auth tokens
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user_id');
      localStorage.removeItem('session_id');
    } catch (e) {
      console.error('Error clearing localStorage:', e);
    }
    
    // Reset all state
    setUser(null);
    setInterviewResult(null);
    setSelectedInterviewType(null);
    setInterviewQuestions([]);
    setCurrentStep('login');
    
    // Force a page reload to clear all session data
    setTimeout(() => {
      window.location.href = '/';
    }, 50);
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
      case 'region-select':
        return user ? (
          <RegionSelect user={user} onComplete={handleRegionSelect} />
        ) : (
          <LoginSignup onComplete={handleLoginSuccess} />
        );
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
      case 'leaderboard':
        return user ? (
          <LeaderboardPage onClose={() => setCurrentStep('setup')} />
        ) : (
          <LoginSignup onComplete={handleLoginSuccess} />
        );
      default:
        return <LoginSignup onComplete={handleLoginSuccess} />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {isSubmitting && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-40">
          <div className="bg-white p-6 rounded-lg shadow-lg text-center">
            <div className="w-12 h-12 border-4 border-orange-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
            <div className="font-semibold">Submitting answers — generating AI feedback...</div>
            <div className="text-sm text-gray-600 mt-2">This can take up to a minute depending on model latency.</div>
          </div>
        </div>
      )}
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
