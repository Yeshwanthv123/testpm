import React, { useState, useEffect } from 'react';
import Navigation from './components/Navigation';
import LoginSignup from './components/LoginSignup';
import Onboarding from './components/Onboarding';
import InterviewSetup from './components/InterviewSetup';
import InterviewFlow from './components/InterviewFlow';
import Dashboard from './components/Dashboard';
import { User, InterviewType, Answer, InterviewResult, SkillScore } from './types';
import { mockSkillScores, mockPeerComparison } from './data/mockData';
import { calculateSkillScore, generateFeedback, calculatePercentile } from './utils/scoring';

type AppStep = 'login' | 'onboarding' | 'setup' | 'interview' | 'results';

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

function App() {
  const [currentStep, setCurrentStep] = useState<AppStep>('login');
  const [user, setUser] = useState<User | null>(null);
  const [selectedInterviewType, setSelectedInterviewType] = useState<InterviewType | null>(null);
  const [interviewResult, setInterviewResult] = useState<InterviewResult | null>(null);
  const [jobDescription, setJobDescription] = useState<string | undefined>(undefined);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const checkAuthStatus = async () => {
      const token = localStorage.getItem('accessToken');
      if (token) {
        try {
          const response = await fetch(`${API_BASE}/auth/me`, {
            headers: { 'Authorization': `Bearer ${token}` }
          });
          if (response.ok) {
            const userData = await response.json();
            handleLoginComplete(userData);
          } else {
            localStorage.removeItem('accessToken');
            localStorage.removeItem('refreshToken');
          }
        } catch (error) {
          console.error("Failed to verify auth status", error);
        }
      }
      setIsLoading(false);
    };
    checkAuthStatus();
  }, []);

  const handleLoginComplete = (userData: User) => {
    setUser(userData);
    if (!userData.experience || !userData.currentRole || !userData.region) {
      setCurrentStep('onboarding');
    } else {
      setCurrentStep('setup');
    }
  };
  
  const handleUpdateUser = (updatedUser: User) => {
    setUser(updatedUser);
  };

  const handleOnboardingComplete = (userData: User) => {
    setUser(userData);
    setCurrentStep('setup');
  };

  const handleInterviewStart = (interviewType: InterviewType, jd?: string) => {
    setSelectedInterviewType(interviewType);
    setJobDescription(jd);
    setCurrentStep('interview');
  };

  const handleInterviewComplete = (answers: Answer[]) => {
    if (!selectedInterviewType) return;
    const skillScores: SkillScore[] = mockSkillScores.map(mockScore => ({
      ...mockScore,
      feedback: generateFeedback(mockScore.score, mockScore.skill),
      percentile: calculatePercentile(mockScore.score, mockScore.skill)
    }));
    const result: InterviewResult = {
      sessionId: Date.now().toString(),
      overallScore: Math.round(skillScores.reduce((sum, skill) => sum + skill.score, 0) / skillScores.length),
      skillScores,
      strengths: ['Strength 1', 'Strength 2'],
      improvements: ['Improvement 1', 'Improvement 2'],
      peerComparison: mockPeerComparison,
      detailedFeedback: 'Good job!'
    };
    setInterviewResult(result);
    setCurrentStep('results');
  };

  const handleRetakeInterview = () => {
    setCurrentStep('setup');
    setInterviewResult(null);
    setSelectedInterviewType(null);
    setJobDescription(undefined);
  };

  const handleNavigate = (step: string) => {
    setCurrentStep(step as AppStep);
  };

  if (isLoading) {
    return (
        <div className="min-h-screen bg-gray-50 flex items-center justify-center">
            <div className="w-16 h-16 border-4 border-orange-500 border-t-transparent rounded-full animate-spin"></div>
        </div>
    );
  }

  if (!user) {
    return <LoginSignup onComplete={handleLoginComplete} />;
  }

  if (currentStep === 'onboarding') {
    return <Onboarding user={user} onComplete={handleOnboardingComplete} />;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navigation
        currentStep={currentStep}
        onNavigate={handleNavigate}
        canGoBack={currentStep !== 'interview'}
        user={user}
        onUpdateUser={handleUpdateUser}
      />
      
      {currentStep === 'setup' && (
        <InterviewSetup onStartInterview={handleInterviewStart} />
      )}
      
      {currentStep === 'interview' && selectedInterviewType && (
        <InterviewFlow
          interviewType={selectedInterviewType}
          onComplete={handleInterviewComplete}
          jobDescription={jobDescription}
        />
      )}
      
      {currentStep === 'results' && interviewResult && (
        <Dashboard
          result={interviewResult}
          onRetakeInterview={handleRetakeInterview}
        />
      )}
    </div>
  );
}

export default App;