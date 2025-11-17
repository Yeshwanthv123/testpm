import React, { useState, useEffect, useMemo } from 'react';
import {
  Clock,
  MessageSquare,
  ArrowRight,
  CheckCircle,
  AlertCircle,
  Mic,
  MicOff,
  Volume2,
  VolumeX,
  Sparkles,
  Lightbulb,
  ArrowLeft,
} from 'lucide-react';
import { InterviewType, Question, Answer } from '../types';
import { sampleQuestions } from '../data/mockData';
import { useVoice } from '../hooks/useVoice';

interface InterviewFlowProps {
  interviewType: InterviewType;
  onComplete: (answers: Answer[]) => void;
  jobDescription?: string;
  onExitInterview: () => void; // ✅ Added to handle exit
}

const DEFAULT_PER_QUESTION_SECONDS = 180;

// Company logo URLs - Using multiple sources with fallbacks
const COMPANY_LOGOS: Record<string, string> = {
  'Google': 'https://www.google.com/favicon.ico',
  'Meta': 'https://www.meta.com/favicon.ico',
  'Amazon': 'https://www.amazon.com/favicon.ico',
  'Apple': 'https://www.apple.com/favicon.ico',
  'Microsoft': 'https://www.microsoft.com/favicon.ico',
  'Netflix': 'https://www.netflix.com/favicon.ico',
  'Uber': 'https://www.uber.com/favicon.ico',
  'Airbnb': 'https://www.airbnb.com/favicon.ico',
  'Stripe': 'https://www.stripe.com/favicon.ico',
  'Salesforce': 'https://www.salesforce.com/favicon.ico',
  'Freshworks': 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzIiIGhlaWdodD0iMzIiIHZpZXdCb3g9IjAgMCAzMiAzMiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMzIiIGhlaWdodD0iMzIiIHJ4PSI4IiBmaWxsPSIjMDAxQzMwIi8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnRTaXplPSIxNCIgZm9udFdlaWdodD0iYm9sZCIgZmlsbD0id2hpdGUiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGR5PSIuM2VtIj5GVzwvdGV4dD48L3N2Zz4=',
  'Zoho': 'https://www.zoho.com/favicon.ico',
  'Random Interview': 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzIiIGhlaWdodD0iMzIiIHZpZXdCb3g9IjAgMCAzMiAzMiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMzIiIGhlaWdodD0iMzIiIHJ4PSI4IiBmaWxsPSIjNjM2MyYiIi8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnRTaXplPSIyNCIgZm9udFdlaWdodD0iYm9sZCIgZmlsbD0id2hpdGUiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGR5PSIuM2VtIj8+P+KCojwvdGV4dD48L3N2Zz4=',
};

const getCompanyLogo = (company: string): string => {
  // First, try to get favicon from COMPANY_LOGOS
  const logo = COMPANY_LOGOS[company];
  if (logo) return logo;
  
  // For Generic or Unknown companies, return a generic company placeholder SVG
  const companyInitial = (company?.charAt(0) || 'C').toUpperCase();
  // Use a colorful SVG placeholder that always works (no external dependency)
  const colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8', '#6C5CE7'];
  const colorIndex = (company?.charCodeAt(0) || 0) % colors.length;
  const bgColor = colors[colorIndex];
  
  const svg = `<svg width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg"><rect width="32" height="32" rx="8" fill="${bgColor}"/><text x="50%" y="50%" fontSize="16" fontWeight="bold" fill="white" textAnchor="middle" dy=".3em">${companyInitial}</text></svg>`;
  return `data:image/svg+xml;base64,${btoa(svg)}`;
};

function deriveSkills(category?: string, difficulty?: string): string[] {
  const cat = (category || '').toLowerCase();
  const map: Record<string, string[]> = {
    strategic: ['Product Strategy', 'Product Execution', 'Analytical Thinking'],
    strategy: ['Product Strategy', 'Product Execution', 'Analytical Thinking'],
    leadership: ['Leadership & Ownership', 'Communication', 'Analytical Thinking'],
    metrics: ['Analytical Thinking', 'Leadership & Ownership', 'Communication'],
    'product health': ['Analytical Thinking', 'Product Execution', 'Leadership & Ownership'],
    growth: ['Product Strategy', 'Product Execution', 'Analytical Thinking'],
    'a/b testing': ['Analytical Thinking', 'Product Execution', 'Leadership & Ownership'],
    'customer obsession': ['Product Execution', 'Communication', 'Leadership & Ownership'],
    foundation: ['Product Execution', 'Leadership & Ownership', 'Communication'],
    behavioral: ['Communication', 'Leadership & Ownership', 'Product Strategy'],
    technical: ['Analytical Thinking', 'Product Execution', 'Product Strategy'],
    'system design': ['Product Execution', 'Analytical Thinking', 'Product Strategy'],
    'product sense': ['Product Strategy', 'Communication', 'Product Execution'],
    execution: ['Product Execution', 'Product Strategy', 'Leadership & Ownership'],
    launch: ['Product Execution', 'Leadership & Ownership', 'Communication'],
    'go-to-market': ['Product Strategy', 'Communication', 'Product Execution'],
    pricing: ['Analytical Thinking', 'Product Strategy', 'Product Execution'],
    'success criteria': ['Analytical Thinking', 'Product Execution', 'Leadership & Ownership'],
    prioritization: ['Product Strategy', 'Analytical Thinking', 'Leadership & Ownership'],
  };

  let picked: string[] | undefined;
  for (const key of Object.keys(map)) {
    if (cat.includes(key)) {
      picked = map[key];
      break;
    }
  }
  if (!picked) picked = ['Product Strategy', 'Product Execution', 'Analytical Thinking'];

  const diff = (difficulty || '').toLowerCase();
  if (diff === 'easy') return picked.slice(0, 2);
  if (diff === 'hard') return Array.from(new Set([...picked, 'Communication', 'Leadership & Ownership']));
  return picked;
}

const InterviewFlow: React.FC<InterviewFlowProps> = ({
  interviewType,
  onComplete,
  jobDescription,
  onExitInterview,
}) => {
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [answers, setAnswers] = useState<Answer[]>([]);
  const [currentAnswer, setCurrentAnswer] = useState('');
  const [timeRemaining, setTimeRemaining] = useState(0);
  const [isTransitioning, setIsTransitioning] = useState(false);
  const [isQuestionPlaying, setIsQuestionPlaying] = useState(false);
  const [showExitConfirm, setShowExitConfirm] = useState(false);
  const [stopTimer, setStopTimer] = useState(false);

  const { voiceState, startRecording, stopRecording, speakText, clearTranscript, isSupported } =
    useVoice();

  const perQuestionSeconds = () => {
    const total = Math.max(1, interviewType?.questionCount ?? 10);
    const fromType = Math.floor(((interviewType?.duration ?? 30) * 60) / total);
    return fromType > 0 ? fromType : DEFAULT_PER_QUESTION_SECONDS;
  };

  function toQuestionArray(raw: unknown): Question[] {
    const sec = perQuestionSeconds();
    if (!Array.isArray(raw)) return [];

    return raw
      .map((item: any, idx: number): Question | null => {
        const qText =
          typeof item?.question === 'string'
            ? item.question
            : typeof item?.text === 'string'
            ? item.text
            : null;
        if (!qText || !qText.trim()) return null;

        const id = item?.id != null ? String(item.id) : `q_${idx}`;
        const q: Question = {
          id,
          question: qText.trim(),
          type: (item?.type as Question['type']) || 'behavioral',
          category: (item?.category as string) || 'General',
          company: (item?.company as string) || undefined,
          timeLimit:
            typeof item?.timeLimit === 'number' && item.timeLimit > 0
              ? item.timeLimit
              : sec,
          difficulty:
            (item?.difficulty as Question['difficulty']) ||
            (item?.complexity as any) ||
            'medium',
          skills:
            Array.isArray(item?.skills) && item.skills.length
              ? item.skills
              : deriveSkills(item?.category, item?.difficulty || item?.complexity),
        };
        return q;
      })
      .filter((q): q is Question => q !== null);
  }

  function getInjectedQuestions(): Question[] | null {
    try {
      const cached = sessionStorage.getItem('pmbot_questions');
      if (cached) {
        const parsed = JSON.parse(cached);
        const arr = toQuestionArray(parsed);
        if (arr.length) return arr.slice(0, Math.max(1, interviewType.questionCount));
      }
    } catch {}
    return null;
  }

  const questions: Question[] = useMemo(() => {
    const fromBackend = getInjectedQuestions();

    // ONLY use questions from backend (loaded from CSV database)
    // Do NOT mix in mock/template questions
    if (fromBackend && fromBackend.length) {
      return fromBackend.slice(0, interviewType.questionCount);
    }

    // If no backend questions available, return empty (don't fall back to mock data)
    return [];
  }, [interviewType, jobDescription]);

  const currentQuestion = questions[currentQuestionIndex];

  useEffect(() => {
    if (currentQuestion) setTimeRemaining(currentQuestion.timeLimit);
  }, [currentQuestion]);

  useEffect(() => {
    if (stopTimer) return;
    if (timeRemaining > 0) {
      const timer = setTimeout(() => setTimeRemaining((t) => t - 1), 1000);
      return () => clearTimeout(timer);
    }
  }, [timeRemaining, stopTimer]);

  useEffect(() => {
    // Sync voice transcript to answer field whenever recording is active
    if (voiceState.isRecording) {
      setCurrentAnswer(voiceState.transcript);
    }
  }, [voiceState.transcript, voiceState.isRecording]);

  // Auto-advance when timer reaches 0
  useEffect(() => {
    if (timeRemaining === 0 && !stopTimer && currentQuestion && currentQuestionIndex < questions.length) {
      const autoAdvanceTimer = setTimeout(() => {
        const answer: Answer = {
          questionId: currentQuestion.id,
          answer: currentAnswer || '(No answer - Time expired)',
          timeSpent: currentQuestion.timeLimit,
          timestamp: new Date(),
          isVoiceAnswer: voiceState.transcript.length > 0,
        };

        const newAnswers = [...answers, answer];
        setAnswers(newAnswers);

        if (currentQuestionIndex < questions.length - 1) {
          // Move to next question sequentially (not skipping)
          setIsTransitioning(true);
          setTimeout(() => {
            setCurrentQuestionIndex(currentQuestionIndex + 1);
            setCurrentAnswer('');
            clearTranscript();
            setIsTransitioning(false);
            setStopTimer(false); // Reset timer for next question
          }, 500);
        } else {
          // Last question timed out - show results
          setStopTimer(true);
          onComplete(newAnswers);
        }
      }, 100);
      
      return () => clearTimeout(autoAdvanceTimer);
    }
  }, [timeRemaining, stopTimer, currentQuestion, currentQuestionIndex, questions.length, answers, voiceState.transcript, onComplete, clearTranscript, currentAnswer]);

  const handlePlayQuestion = () => {
    if (!currentQuestion) return;
    if (isQuestionPlaying) {
      speechSynthesis.cancel();
      setIsQuestionPlaying(false);
    } else {
      setIsQuestionPlaying(true);
      const utterance = new SpeechSynthesisUtterance(currentQuestion.question);
      utterance.onend = () => setIsQuestionPlaying(false);
      utterance.onerror = () => setIsQuestionPlaying(false);
      speechSynthesis.speak(utterance);
    }
  };

  const handleVoiceToggle = () => {
    if (voiceState.isRecording) stopRecording();
    else {
      clearTranscript();
      startRecording();
    }
  };

  const handleNextQuestion = () => {
    if (!currentAnswer.trim()) return;

    const answer: Answer = {
      questionId: currentQuestion.id,
      answer: currentAnswer,
      timeSpent: currentQuestion.timeLimit - timeRemaining,
      timestamp: new Date(),
      isVoiceAnswer: voiceState.transcript.length > 0,
    };

    const newAnswers = [...answers, answer];
    setAnswers(newAnswers);

    if (currentQuestionIndex < questions.length - 1) {
      setIsTransitioning(true);
      setTimeout(() => {
        setCurrentQuestionIndex((i) => i + 1);
        setCurrentAnswer('');
        clearTranscript();
        setIsTransitioning(false);
      }, 500);
    } else {
      // Stop the timer before submitting so the countdown doesn't continue
      setStopTimer(true);
      setTimeRemaining(0);
      onComplete(newAnswers);
    }
  };

  const handleExitInterview = () => setShowExitConfirm(true);

  const confirmExit = () => {
    setShowExitConfirm(false);
    onExitInterview(); // ✅ Go back to setup cleanly
  };

  const formatTime = (s: number) => `${Math.floor(s / 60)}:${(s % 60).toString().padStart(2, '0')}`;

  const getTimeColor = () => {
    if (!currentQuestion) return 'text-gray-600';
    const pct = timeRemaining / currentQuestion.timeLimit;
    if (pct > 0.5) return 'text-green-600';
    if (pct > 0.25) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getTipForQuestionType = (type: string) => {
    const tips: Record<string, string> = {
      behavioral: 'Use the STAR method: Situation, Task, Action, Result',
      product_design: 'Walk through your design process step by step',
      analytical: 'Show your analytical framework and reasoning',
      technical: 'Explain technical concepts clearly and consider trade-offs',
      strategic: 'Think about long-term implications and stakeholder impact',
    };
    return tips[type] || 'Structure your response clearly and provide specific examples';
  };

  const progress = ((currentQuestionIndex + 1) / Math.max(1, questions.length)) * 100;

  if (isTransitioning)
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-white">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-orange-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-lg text-gray-600">Loading next question...</p>
        </div>
      </div>
    );

  if (!currentQuestion)
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-white">
        <div className="bg-white rounded-2xl shadow-lg p-8 text-center">
          <h2 className="text-xl font-semibold mb-2">No questions available</h2>
          <p className="text-gray-600">Please go back and try again.</p>
          <button
            onClick={onExitInterview}
            className="mt-4 px-6 py-3 bg-gradient-to-r from-yellow-500 to-orange-500 text-white rounded-lg hover:from-yellow-600 hover:to-orange-600 transition-all font-medium"
          >
            Go Back
          </button>
        </div>
      </div>
    );

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 p-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="bg-white rounded-2xl shadow-lg p-6 mb-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <button
                onClick={handleExitInterview}
                className="p-2 text-gray-600 hover:text-red-600 hover:bg-red-50 rounded-lg transition"
                title="Exit Interview"
              >
                <ArrowLeft className="w-5 h-5" />
              </button>
              <img 
                src={getCompanyLogo(currentQuestion?.company || interviewType.company || interviewType.name)} 
                alt={currentQuestion?.company || interviewType.company || interviewType.name}
                className="w-12 h-12 rounded-lg object-cover bg-white border border-gray-200"
                onError={(e) => {
                  e.currentTarget.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzIiIGhlaWdodD0iMzIiIHZpZXdCb3g9IjAgMCAzMiAzMiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMzIiIGhlaWdodD0iMzIiIHJ4PSI4IiBmaWxsPSIjNjU2NUY1Ii8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnRTaXplPSIxNiIgZm9udFdlaWdodD0iYm9sZCIgZmlsbD0id2hpdGUiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGR5PSIuM2VtIj5DPC90ZXh0Pjwvc3ZnPg==';
                }}
              />
              <div>
                <h1 className="text-2xl font-bold text-gray-900">{currentQuestion?.company || interviewType.company || interviewType.name}</h1>
                <p className="text-gray-600 text-sm">
                  {jobDescription ? 'Interview' : `Question ${currentQuestionIndex + 1} of ${questions.length}`}
                </p>
              </div>
            </div>
            <div className="text-right flex flex-col items-center space-y-1">
              <div className={`text-3xl font-bold ${getTimeColor()}`}>{formatTime(timeRemaining)}</div>
              <div className="text-xs text-gray-500 font-medium">Time Remaining</div>
            </div>
          </div>
          <div className="w-full bg-gray-200 h-2 rounded-full mt-4">
            <div
              className="bg-gradient-to-r from-yellow-500 to-orange-500 h-2 rounded-full transition-all"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>

        {/* Question */}
        <div className="bg-white rounded-2xl shadow-lg p-8 mb-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">{currentQuestion.question}</h2>
          <div className="flex flex-wrap gap-2">
            {currentQuestion.skills && currentQuestion.skills.length > 0 ? (
              currentQuestion.skills.map((s, i) => (
                <span
                  key={i}
                  className="bg-orange-50 text-orange-700 text-sm px-3 py-1 rounded-full font-medium"
                >
                  {s}
                </span>
              ))
            ) : (
              <>
                {currentQuestion.category && (
                  <span className="bg-blue-50 text-blue-700 text-sm px-3 py-1 rounded-full font-medium">
                    {currentQuestion.category}
                  </span>
                )}
                {currentQuestion.difficulty && (
                  <span className="bg-purple-50 text-purple-700 text-sm px-3 py-1 rounded-full font-medium">
                    {currentQuestion.difficulty}
                  </span>
                )}
              </>
            )}
          </div>
        </div>

        {/* Answer */}
        <div className="bg-white rounded-2xl shadow-lg p-8">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-2">
              <MessageSquare className="w-5 h-5 text-orange-500" />
              <h3 className="text-lg font-semibold text-gray-900">Your Answer</h3>
            </div>
            {isSupported && (
              <button
                onClick={handleVoiceToggle}
                className={`flex items-center px-4 py-2 rounded-lg transition ${
                  voiceState.isRecording
                    ? 'bg-red-100 text-red-700 hover:bg-red-200'
                    : 'bg-orange-100 text-orange-700 hover:bg-orange-200'
                }`}
              >
                {voiceState.isRecording ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
                <span className="ml-2 text-sm font-medium">
                  {voiceState.isRecording ? 'Stop' : 'Voice Input'}
                </span>
              </button>
            )}
          </div>

          <textarea
            value={currentAnswer}
            onChange={(e) => {
              // Calculate tokens after trimming whitespace
              const trimmedText = e.target.value.trim();
              const tokens = Math.ceil(trimmedText.length / 4);
              
              // Only allow up to 300 tokens
              if (tokens <= 300) {
                setCurrentAnswer(e.target.value);
              }
            }}
            placeholder="Start typing your answer..."
            className="w-full h-64 p-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 font-mono text-sm"
          />

          <div className="flex justify-between items-center mt-4">
            <div className="flex gap-4 text-sm text-gray-500">
              <span>{currentAnswer.length} chars</span>
              <span>•</span>
              <span>{currentAnswer.split(' ').filter((w) => w).length} words</span>
              <span>•</span>
              <span className={Math.ceil(currentAnswer.trim().length / 4) >= 300 ? 'text-red-600 font-bold' : ''}>
                {Math.ceil(currentAnswer.trim().length / 4)} / 300 tokens
              </span>
            </div>
            <button
              onClick={handleNextQuestion}
              disabled={!currentAnswer.trim()}
              className="px-6 py-3 bg-gradient-to-r from-yellow-500 to-orange-500 text-white rounded-lg hover:from-yellow-600 hover:to-orange-600 disabled:opacity-50 font-medium"
            >
              {currentQuestionIndex < questions.length - 1
                ? 'Next Question →'
                : 'Complete Interview'}
            </button>
          </div>
        </div>
      </div>

      {/* Exit Modal */}
      {showExitConfirm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl shadow-2xl p-8 max-w-md w-full text-center">
            <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <AlertCircle className="w-8 h-8 text-red-600" />
            </div>
            <h3 className="text-xl font-bold text-gray-900 mb-2">Exit Interview?</h3>
            <p className="text-gray-600 mb-6">
              Are you sure you want to exit? Your progress will be lost and you'll need to start
              over.
            </p>
            <div className="flex space-x-3">
              <button
                onClick={() => setShowExitConfirm(false)}
                className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
              >
                Continue Interview
              </button>
               <button
                onClick={confirmExit}
                className="flex-1 px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600"
              >
                Exit Interview
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default InterviewFlow;
