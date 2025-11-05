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

function deriveSkills(category?: string, difficulty?: string): string[] {
  const cat = (category || '').toLowerCase();
  const map: Record<string, string[]> = {
    strategic: ['Strategy', 'Prioritization', 'Business Acumen'],
    strategy: ['Strategy', 'Prioritization', 'Business Acumen'],
    leadership: ['Leadership', 'Stakeholder Mgmt', 'Communication'],
    metrics: ['Metrics', 'Analysis', 'Decision-making'],
    'product health': ['Metrics', 'Product Health', 'Diagnostics'],
    growth: ['Growth', 'Experimentation', 'Retention'],
    'a/b testing': ['Experimentation', 'Hypothesis Design', 'Analysis'],
    'customer obsession': ['Customer Empathy', 'Voice of Customer', 'Execution'],
    foundation: ['Execution', 'Ownership', 'Collaboration'],
    behavioral: ['Communication', 'Leadership', 'Stakeholder Mgmt'],
    technical: ['Technical Depth', 'System Design', 'Trade-offs'],
    'system design': ['System Design', 'Scalability', 'Trade-offs'],
    'product sense': ['Product Sense', 'User Empathy', 'Prioritization'],
    execution: ['Execution', 'Project Mgmt', 'Cross-functional'],
    launch: ['Go-to-Market', 'Execution', 'Stakeholder Mgmt'],
    'go-to-market': ['Go-to-Market', 'Positioning', 'Execution'],
    pricing: ['Pricing', 'Market Analysis', 'Trade-offs'],
    'success criteria': ['Metrics', 'Success Criteria', 'Decision-making'],
    prioritization: ['Prioritization', 'Trade-offs', 'Decision-making'],
  };

  let picked: string[] | undefined;
  for (const key of Object.keys(map)) {
    if (cat.includes(key)) {
      picked = map[key];
      break;
    }
  }
  if (!picked) picked = ['Product Sense', 'Execution'];

  const diff = (difficulty || '').toLowerCase();
  if (diff === 'easy') return picked.slice(0, 2);
  if (diff === 'hard') return Array.from(new Set([...picked, 'Depth', 'Edge Cases']));
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

  const generateJobDescriptionQuestions = (jd: string, count: number): Question[] => {
    const sec = perQuestionSeconds();
    const mockJDQuestions: Question[] = [
      {
        id: 'jd1',
        type: 'strategic',
        category: 'Role-Specific',
        question: `Based on the job requirements, how would you approach the key responsibilities mentioned in this role during your first 90 days?`,
        timeLimit: sec,
        difficulty: 'medium',
        skills: ['Strategy', 'Planning', 'Execution'],
      },
      {
        id: 'jd2',
        type: 'behavioral',
        category: 'Experience Match',
        question: `Tell me about a time when you handled a situation similar to the challenges described in this job posting.`,
        timeLimit: sec,
        difficulty: 'medium',
        skills: ['Experience', 'Problem Solving', 'Leadership'],
      },
    ];
    return mockJDQuestions.slice(0, count);
  };

  const questions: Question[] = useMemo(() => {
    const fromBackend = getInjectedQuestions();

    if (fromBackend && fromBackend.length) {
      if (jobDescription) {
        const firstHalf = Math.floor(interviewType.questionCount / 2);
        const secondHalf = Math.max(0, interviewType.questionCount - firstHalf);
        const jdQs = generateJobDescriptionQuestions(jobDescription, secondHalf);
        const base = fromBackend.slice(0, firstHalf);
        return [...base, ...jdQs];
      }
      return fromBackend.slice(0, interviewType.questionCount);
    }

    if (jobDescription) {
      return [
        ...sampleQuestions.slice(0, Math.floor(interviewType.questionCount / 2)),
        ...generateJobDescriptionQuestions(jobDescription, Math.ceil(interviewType.questionCount / 2)),
      ];
    }
    return sampleQuestions.slice(0, interviewType.questionCount);
  }, [interviewType, jobDescription]);

  const currentQuestion = questions[currentQuestionIndex];

  useEffect(() => {
    if (currentQuestion) setTimeRemaining(currentQuestion.timeLimit);
  }, [currentQuestion]);

  useEffect(() => {
    if (timeRemaining > 0) {
      const timer = setTimeout(() => setTimeRemaining((t) => t - 1), 1000);
      return () => clearTimeout(timer);
    }
  }, [timeRemaining]);

  useEffect(() => {
    if (voiceState.transcript) setCurrentAnswer(voiceState.transcript);
  }, [voiceState.transcript]);

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
              <div>
                <h1 className="text-2xl font-bold text-gray-900">{interviewType.name}</h1>
                <p className="text-gray-600 text-sm">
                  Question {currentQuestionIndex + 1} of {questions.length}
                </p>
              </div>
            </div>
            <div className="text-right">
              <div className={`text-2xl font-bold ${getTimeColor()}`}>{formatTime(timeRemaining)}</div>
              <div className="text-sm text-gray-500">Time remaining</div>
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
          <div className="bg-orange-50 rounded-lg p-4 border border-orange-200 mb-4">
            <div className="flex space-x-2">
              <Lightbulb className="w-5 h-5 text-orange-600" />
              <p className="text-sm text-orange-800">
                💡 Tip: {getTipForQuestionType(currentQuestion.type)}
              </p>
            </div>
          </div>
          <div className="flex flex-wrap gap-2">
            {currentQuestion.skills.map((s, i) => (
              <span
                key={i}
                className="bg-orange-50 text-orange-700 text-sm px-3 py-1 rounded-full font-medium"
              >
                {s}
              </span>
            ))}
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
            onChange={(e) => setCurrentAnswer(e.target.value)}
            placeholder="Start typing your answer..."
            className="w-full h-64 p-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500"
          />

          <div className="flex justify-between items-center mt-4">
            <span className="text-sm text-gray-500">
              {currentAnswer.length} chars •{' '}
              {currentAnswer.split(' ').filter((w) => w).length} words
            </span>
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
