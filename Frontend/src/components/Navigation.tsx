import React, { useState } from "react";
import { ArrowLeft, Home, BarChart3, Briefcase, ChevronRight } from "lucide-react";
import Profile from "./Profile";
import { User as UserType } from "../types";

interface NavigationProps {
  currentStep: string;
  onNavigate: (step: string) => void;
  canGoBack?: boolean;
  user: UserType | null;
  onUpdateUser: (user: UserType) => void;
  onLogout: () => void;
  onStartInterview?: (interviewType: any, questions: any[], jd?: string) => void;
  onViewResult?: (past: any) => void;
}

class ProfileErrorBoundary extends React.Component<{children?: React.ReactNode}, {hasError: boolean, error?: any}> {
  constructor(props: any) {
    super(props);
    this.state = { hasError: false };
  }
  static getDerivedStateFromError() {
    return { hasError: true };
  }
  componentDidCatch(error: any) {
    console.error('Error rendering profile modal', error);
  }
  render() {
    if (this.state.hasError) {
      return (
        <div className="fixed inset-0 bg-white flex items-center justify-center z-50">
          <div className="text-center">
            <h3 className="text-xl font-bold">Something went wrong</h3>
            <p className="text-sm text-gray-600 mt-2">Failed to open profile. Please refresh the page.</p>
          </div>
        </div>
      );
    }
    return this.props.children as any;
  }
}

const Navigation: React.FC<NavigationProps> = ({
  currentStep,
  onNavigate,
  canGoBack = true,
  user,
  onUpdateUser,
  onLogout,
  onStartInterview,
  onViewResult,
}) => {
  const [showProfile, setShowProfile] = useState(false);

  const steps = [
    { id: "onboarding", label: "Onboarding", icon: Briefcase, description: "Set up your profile" },
    { id: "setup", label: "Interview Setup", icon: Home, description: "Choose company & type" },
    { id: "interview", label: "Interview", icon: BarChart3, description: "Take the interview" },
    { id: "results", label: "Results", icon: BarChart3, description: "View your performance" },
  ] as const;

  const currentStepIndex = steps.findIndex((s) => s.id === currentStep);

  const handleStepNavigation = (stepId: string) => {
    const targetIndex = steps.findIndex((s) => s.id === stepId);
    if (targetIndex <= currentStepIndex) onNavigate(stepId);
  };

  const handleBackNavigation = () => {
    if (currentStepIndex > 0) onNavigate(steps[currentStepIndex - 1].id);
  };

  const handleHomeNavigation = () => onNavigate("onboarding");

  const getInitials = (name?: string) => {
    if (!name) return "U";
    const parts = name.trim().split(/\s+/);
    if (parts.length > 1) return `${parts[0][0]}${parts[parts.length - 1][0]}`.toUpperCase();
    return parts[0][0].toUpperCase();
  };

  // ✅ During interview: disable navigation buttons (except Profile)
  const isLocked = currentStep === "interview";

  return (
    <>
      <nav className="bg-white shadow-sm border-b sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Left Section */}
            <div className="flex items-center space-x-4">
              {canGoBack && currentStepIndex > 0 && (
                <button
                  onClick={!isLocked ? handleBackNavigation : undefined}
                  disabled={isLocked}
                  className={`p-2 text-gray-600 rounded-lg transition-colors group ${
                    isLocked
                      ? "opacity-50 cursor-not-allowed"
                      : "hover:text-gray-900 hover:bg-gray-100"
                  }`}
                  title={isLocked ? "Navigation disabled during interview" : "Go back"}
                >
                  <ArrowLeft className="w-5 h-5 group-hover:-translate-x-1 transition-transform" />
                </button>
              )}

              <button
                onClick={!isLocked ? handleHomeNavigation : undefined}
                disabled={isLocked}
                className={`p-2 text-gray-600 rounded-lg transition-colors group ${
                  isLocked
                    ? "opacity-50 cursor-not-allowed"
                    : "hover:text-gray-900 hover:bg-gray-100"
                }`}
                title={isLocked ? "Navigation disabled during interview" : "Go to Interview Setup"}
              >
                <Home className="w-5 h-5 group-hover:scale-110 transition-transform" />
              </button>

              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 bg-gradient-to-br from-yellow-400 to-orange-500 rounded-full flex items-center justify-center">
                  <div className="text-sm">🧠</div>
                </div>
                <h1 className="text-xl font-bold bg-gradient-to-r from-yellow-600 to-orange-600 bg-clip-text text-transparent">
                  Abhyas
                </h1>
              </div>
            </div>

            {/* Center Section — Breadcrumbs */}
            <div className="hidden lg:flex items-center space-x-2">
              {steps.map((step, index) => {
                const Icon = step.icon;
                const isActive = index === currentStepIndex;
                const isEnabled = index <= currentStepIndex && !isLocked; // ✅ disabled during interview

                return (
                  <React.Fragment key={step.id}>
                    <button
                      type="button"
                      onClick={() => isEnabled && handleStepNavigation(step.id)}
                      disabled={!isEnabled}
                      className={[
                        "flex items-center gap-2 px-3 py-2 rounded-lg transition-colors",
                        isActive
                          ? "bg-indigo-50 text-indigo-700"
                          : isEnabled
                          ? "text-gray-700 hover:bg-gray-100"
                          : "text-gray-400 cursor-not-allowed opacity-50",
                      ].join(" ")}
                      title={
                        isLocked
                          ? "Navigation disabled during interview"
                          : step.description
                      }
                    >
                      <Icon className="w-4 h-4" />
                      <span className="text-sm font-medium">{step.label}</span>
                    </button>

                    {index < steps.length - 1 && (
                      <ChevronRight key={`${step.id}-sep`} className="w-4 h-4 text-gray-300" />
                    )}
                  </React.Fragment>
                );
              })}
            </div>

            {/* Right Section */}
            <div className="flex items-center space-x-2 md:space-x-4">
              <button
                onClick={() => setShowProfile(true)}
                className="flex items-center space-x-2 px-3 md:px-4 py-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors group"
                title="View Profile"
              >
                <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white text-sm font-medium group-hover:scale-110 transition-transform">
                  {getInitials(user?.full_name)}
                </div>
                <span className="text-sm font-medium hidden sm:block">Profile</span>
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* ✅ Profile Modal */}
      {showProfile && user && (
        <ProfileErrorBoundary>
          <Profile
            user={user}
            onUpdateUser={onUpdateUser}
            onClose={() => setShowProfile(false)}
            onLogout={onLogout}
            onStartInterview={onStartInterview}
            onViewResult={onViewResult}
            onNavigate={(step) => {
              setShowProfile(false);
              onNavigate(step);
            }}
          />
        </ProfileErrorBoundary>
      )}
    </>
  );
};

export default Navigation;
