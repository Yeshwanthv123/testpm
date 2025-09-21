import React, { useState } from 'react';
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

function App() {
  const [currentStep, setCurrentStep] = useState<AppStep>('login');
  const [user, setUser] = useState<User | null>(null);
  const [selectedInterviewType, setSelectedInterviewType] = useState<InterviewType | null>(null);
  const [interviewResult, setInterviewResult] = useState<InterviewResult | null>(null);
  const [jobDescription, setJobDescription] = useState<string | undefined>(undefined);

  const handleLoginComplete = (userData: User) => {
    setUser(userData);
    // ALWAYS go to onboarding after login, regardless of login method
    setCurrentStep('onboarding');
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

    // Mock skill evaluation - in real app, this would use AI
    const skillScores: SkillScore[] = mockSkillScores.map(mockScore => ({
      ...mockScore,
      feedback: generateFeedback(mockScore.score, mockScore.skill),
      percentile: calculatePercentile(mockScore.score, mockScore.skill)
    }));

    const result: InterviewResult = {
      sessionId: Date.now().toString(),
      overallScore: Math.round(skillScores.reduce((sum, skill) => sum + skill.score, 0) / skillScores.length),
      skillScores,
      strengths: [
        'Excellent strategic thinking and framework application',
        'Strong execution mindset with practical solutions',
        'Clear communication and structured responses'
      ],
      improvements: [
        'Expand on stakeholder management strategies',
        'Include more quantitative analysis in responses',
        'Develop deeper technical architecture understanding'
      ],
      peerComparison: mockPeerComparison,
      detailedFeedback: 'Overall strong performance with clear product thinking and good communication skills.'
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
    // Validate navigation - users can only go back to previous steps or current step
    const stepOrder: AppStep[] = ['login', 'onboarding', 'setup', 'interview', 'results'];
    const currentIndex = stepOrder.indexOf(currentStep);
    const targetIndex = stepOrder.indexOf(step as AppStep);
    
    // Allow navigation to previous steps, current step, or next step if conditions are met
    if (targetIndex <= currentIndex || (targetIndex === currentIndex + 1 && canProceedToStep(step as AppStep))) {
      setCurrentStep(step as AppStep);
    }
  };

  const canProceedToStep = (step: AppStep): boolean => {
    switch (step) {
      case 'login':
        return true;
      case 'onboarding':
        return !!user;
      case 'setup':
        return !!user && !!user.experience && !!user.currentRole && !!user.region;
      case 'interview':
        return !!selectedInterviewType;
      case 'results':
        return !!interviewResult;
      default:
        return false;
    }
  };

  if (currentStep === 'login') {
    return <LoginSignup onComplete={handleLoginComplete} />;
  }

  if (currentStep === 'onboarding') {
    return <Onboarding user={user!} onComplete={handleOnboardingComplete} />;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navigation 
        currentStep={currentStep} 
        onNavigate={handleNavigate}
        canGoBack={currentStep !== 'interview'}
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