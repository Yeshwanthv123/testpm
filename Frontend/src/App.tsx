import React, { useState, useEffect } from 'react';
import Navigation from './components/Navigation';
import LoginSignup from './components/LoginSignup';
import Onboarding from './components/Onboarding';
import InterviewSetup from './components/InterviewSetup';
import InterviewFlow from './components/InterviewFlow';
import Dashboard from './components/Dashboard';
import { User, InterviewType, Answer, InterviewResult, SkillScore, Question } from './types'; // Import Question
import { mockSkillScores, mockPeerComparison, detailedInsights } from './data/mockData';
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
  const [interviewQuestions, setInterviewQuestions] = useState<Question[]>([]); // <-- ADD THIS STATE

  // Check for an existing token on initial load
  useEffect(() => {
    const checkAuthStatus = async () => {
      const token = localStorage.getItem('access_token');
      if (token) {
        try {
          const response = await fetch(`${API_BASE}/auth/me`, {
            headers: { 'Authorization': `Bearer ${token}` }
          });
          if (response.ok) {
            const userData = await response.json();
            handleLoginSuccess(userData);
          } else {
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
          }
        } catch (error) {
          console.error("Failed to verify auth status", error);
        }
      }
      setIsLoading(false);
    };
    checkAuthStatus();
  }, []);

  const handleLoginSuccess = (userData: User) => {
    setUser(userData);
    if (!userData.experience || !userData.currentRole || !userData.region) {
      setCurrentStep('onboarding');
    } else {
      setCurrentStep('setup');
    }
  };
  
  const handleOnboardingComplete = async (updatedUserData: User) => {
    // ... (This function remains the same as before)
  };
  
  const handleUpdateUser = (updatedUser: User) => {
    setUser(updatedUser);
  };

  // v-- THIS FUNCTION IS UPDATED
  const handleInterviewStart = (interviewType: InterviewType, questions: Question[], jd?: string) => {
    setSelectedInterviewType(interviewType);
    setInterviewQuestions(questions); // <-- SET THE QUESTIONS
    setJobDescription(jd);
    setCurrentStep('interview');
  };

  const handleInterviewComplete = (answers: Answer[]) => {
    // ... (This function remains the same as before)
  };

  const handleRetakeInterview = () => {
    // ... (This function remains the same as before)
  };

  const handleNavigate = (step: string) => {
    setCurrentStep(step as AppStep);
  };
  
  const handleLogout = () => {
    // ... (This function remains the same as before)
  };

  if (isLoading) {
    // ... (remains the same)
  }
  
  const renderStep = () => {
    switch(currentStep) {
      case 'login':
        return <LoginSignup onComplete={handleLoginSuccess} />;
      case 'onboarding':
        return user ? <Onboarding user={user} onComplete={handleOnboardingComplete} /> : <LoginSignup onComplete={handleLoginSuccess} />;
      case 'setup':
        return <InterviewSetup onStartInterview={handleInterviewStart} />;
      case 'interview':
        // v-- THIS PART IS UPDATED
        return selectedInterviewType ? (
          <InterviewFlow 
            interviewType={selectedInterviewType}
            questions={interviewQuestions} // <-- PASS THE QUESTIONS
            onComplete={handleInterviewComplete}
            jobDescription={jobDescription} 
          />
        ) : <InterviewSetup onStartInterview={handleInterviewStart} />;
      case 'results':
        return interviewResult ? <Dashboard result={interviewResult} onRetakeInterview={handleRetakeInterview} /> : <InterviewSetup onStartInterview={handleInterviewStart} />;
      default:
        return <LoginSignup onComplete={handleLoginSuccess} />;
    }
  }

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