import React, { useState } from 'react';
import { ArrowLeft, Home, User, BarChart3, Settings, Briefcase, ChevronRight } from 'lucide-react';
import Profile from './Profile';

interface NavigationProps {
  currentStep: string;
  onNavigate: (step: string) => void;
  canGoBack?: boolean;
}

const Navigation: React.FC<NavigationProps> = ({ currentStep, onNavigate, canGoBack = true }) => {
  const [showProfile, setShowProfile] = useState(false);

  const steps = [
    { id: 'onboarding', label: 'Onboarding', icon: Briefcase, description: 'Set up your profile' },
    { id: 'setup', label: 'Interview Setup', icon: Home, description: 'Choose company & type' },
    { id: 'interview', label: 'Interview', icon: BarChart3, description: 'Take the interview' },
    { id: 'results', label: 'Results', icon: BarChart3, description: 'View your performance' }
  ];

  const getCurrentStepIndex = () => steps.findIndex(s => s.id === currentStep);
  const currentStepIndex = getCurrentStepIndex();

  const handleStepNavigation = (stepId: string) => {
    const targetIndex = steps.findIndex(s => s.id === stepId);
    const currentIndex = getCurrentStepIndex();
    
    // Only allow navigation to previous steps or current step
    if (targetIndex <= currentIndex) {
      onNavigate(stepId);
    }
  };

  const handleBackNavigation = () => {
    if (currentStepIndex > 0) {
      onNavigate(steps[currentStepIndex - 1].id);
    }
  };

  const handleHomeNavigation = () => {
    // Go to the first available step (onboarding or setup)
    onNavigate('setup');
  };

  return (
    <>
      <nav className="bg-white shadow-sm border-b sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Left Section - Logo and Navigation Controls */}
            <div className="flex items-center space-x-4">
              {/* Back Button */}
              {canGoBack && currentStepIndex > 0 && (
                <button
                  onClick={handleBackNavigation}
                  className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors group"
                  title="Go back to previous step"
                >
                  <ArrowLeft className="w-5 h-5 group-hover:transform group-hover:-translate-x-1 transition-transform" />
                </button>
              )}

              {/* Home Button */}
              <button
                onClick={handleHomeNavigation}
                className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors group"
                title="Go to Interview Setup"
              >
                <Home className="w-5 h-5 group-hover:scale-110 transition-transform" />
              </button>

              {/* Logo */}
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 bg-gradient-to-br from-yellow-400 to-orange-500 rounded-full flex items-center justify-center">
                  <div className="text-sm">🧠</div>
                </div>
                <h1 className="text-xl font-bold bg-gradient-to-r from-yellow-600 to-orange-600 bg-clip-text text-transparent">
                  Abhyas
                </h1>
              </div>
            </div>
            
            {/* Center Section - Breadcrumbs (Hidden on mobile) */}
            <div className="hidden lg:flex items-center space-x-2">
              {steps.map((step, index) => {
                const Icon = step.icon;
                const isActive = step.id === currentStep;
                const isCompleted = currentStepIndex > index;
                const isAccessible = index <= currentStepIndex;
                
                return (
                  <div key={step.id} className="flex items-center">
                    <button
                      onClick={() => handleStepNavigation(step.id)}
                      disabled={!isAccessible}
                      className={`flex items-center space-x-2 px-3 py-2 rounded-lg transition-all group ${
                        isActive
                          ? 'bg-orange-100 text-orange-700 shadow-sm'
                          : isCompleted
                          ? 'text-green-600 hover:bg-green-50 cursor-pointer'
                          : isAccessible
                          ? 'text-gray-600 hover:bg-gray-50 cursor-pointer'
                          : 'text-gray-300 cursor-not-allowed'
                      }`}
                      title={isAccessible ? `Go to ${step.label}` : step.description}
                    >
                      <Icon className={`w-4 h-4 ${isAccessible ? 'group-hover:scale-110' : ''} transition-transform`} />
                      <span className="text-sm font-medium">{step.label}</span>
                      {isCompleted && (
                        <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                      )}
                    </button>
                    {index < steps.length - 1 && (
                      <ChevronRight className="w-4 h-4 text-gray-300 mx-1" />
                    )}
                  </div>
                );
              })}
            </div>

            {/* Right Section - Progress and Profile */}
            <div className="flex items-center space-x-2 md:space-x-4">
              {/* Mobile Progress Indicator */}
              <div className="lg:hidden flex items-center space-x-2">
                <div className="text-sm font-medium text-gray-600">
                  Step {currentStepIndex + 1} of {steps.length}
                </div>
                <div className="w-16 bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-gradient-to-r from-orange-400 to-yellow-500 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${((currentStepIndex + 1) / steps.length) * 100}%` }}
                  />
                </div>
              </div>

              {/* Profile Button */}
              <button
                onClick={() => setShowProfile(true)}
                className="flex items-center space-x-2 px-3 md:px-4 py-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors group"
                title="View Profile"
              >
                <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white text-sm font-medium group-hover:scale-110 transition-transform">
                  U
                </div>
                <span className="text-sm font-medium hidden sm:block">Profile</span>
              </button>
            </div>
          </div>

          {/* Mobile Breadcrumbs - Below main nav on small screens */}
          <div className="lg:hidden pb-4 border-t border-gray-100 mt-4">
            <div className="flex items-center space-x-1 overflow-x-auto py-2">
              {steps.map((step, index) => {
                const Icon = step.icon;
                const isActive = step.id === currentStep;
                const isCompleted = currentStepIndex > index;
                const isAccessible = index <= currentStepIndex;
                
                return (
                  <div key={step.id} className="flex items-center flex-shrink-0">
                    <button
                      onClick={() => handleStepNavigation(step.id)}
                      disabled={!isAccessible}
                      className={`flex items-center space-x-2 px-3 py-2 rounded-lg transition-all whitespace-nowrap ${
                        isActive
                          ? 'bg-orange-100 text-orange-700 shadow-sm'
                          : isCompleted
                          ? 'text-green-600 hover:bg-green-50'
                          : isAccessible
                          ? 'text-gray-600 hover:bg-gray-50'
                          : 'text-gray-300 cursor-not-allowed'
                      }`}
                    >
                      <Icon className="w-4 h-4" />
                      <span className="text-xs font-medium">{step.label}</span>
                      {isCompleted && (
                        <div className="w-1.5 h-1.5 bg-green-500 rounded-full"></div>
                      )}
                    </button>
                    {index < steps.length - 1 && (
                      <ChevronRight className="w-3 h-3 text-gray-300 mx-1" />
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </nav>

      {/* Profile Modal */}
      {showProfile && (
        <Profile onClose={() => setShowProfile(false)} />
      )}
    </>
  );
};

export default Navigation;