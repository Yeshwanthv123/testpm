import React, { useState, useEffect } from 'react';
import { Clock, MessageSquare, ArrowRight, CheckCircle, AlertCircle, Mic, MicOff, Volume2, VolumeX, Sparkles, Lightbulb, Home, ArrowLeft } from 'lucide-react';
import { InterviewType, Question, Answer } from '../types';
import { sampleQuestions } from '../data/mockData';
import { useVoice } from '../hooks/useVoice';

interface InterviewFlowProps {
  interviewType: InterviewType;
  onComplete: (answers: Answer[]) => void;
  jobDescription?: string;
}

const InterviewFlow: React.FC<InterviewFlowProps> = ({ interviewType, onComplete, jobDescription }) => {
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [answers, setAnswers] = useState<Answer[]>([]);
  const [currentAnswer, setCurrentAnswer] = useState('');
  const [timeRemaining, setTimeRemaining] = useState(0);
  const [questionStartTime, setQuestionStartTime] = useState(Date.now());
  const [isTransitioning, setIsTransitioning] = useState(false);
  const [isQuestionPlaying, setIsQuestionPlaying] = useState(false);
  const [showExitConfirm, setShowExitConfirm] = useState(false);

  const { voiceState, startRecording, stopRecording, speakText, clearTranscript, isSupported } = useVoice();

  // Mock questions for the interview type - in real app, would generate from JD if provided
  const questions = jobDescription 
    ? [...sampleQuestions.slice(0, Math.floor(interviewType.questionCount / 2)), 
       ...generateJobDescriptionQuestions(jobDescription, Math.ceil(interviewType.questionCount / 2))]
    : sampleQuestions.slice(0, interviewType.questionCount);
  
  const currentQuestion = questions[currentQuestionIndex];

  // Mock function to generate questions from job description
  function generateJobDescriptionQuestions(jd: string, count: number): Question[] {
    // In real app, this would use AI to analyze JD and generate relevant questions
    const mockJDQuestions: Question[] = [
      {
        id: 'jd1',
        type: 'strategic',
        category: 'Role-Specific',
        question: `Based on the job requirements, how would you approach the key responsibilities mentioned in this role during your first 90 days?`,
        timeLimit: 300,
        difficulty: 'medium',
        skills: ['Strategy', 'Planning', 'Execution']
      },
      {
        id: 'jd2',
        type: 'behavioral',
        category: 'Experience Match',
        question: `Tell me about a time when you handled a situation similar to the challenges described in this job posting.`,
        timeLimit: 240,
        difficulty: 'medium',
        skills: ['Experience', 'Problem Solving', 'Leadership']
      }
    ];
    return mockJDQuestions.slice(0, count);
  }

  useEffect(() => {
    if (currentQuestion) {
      setTimeRemaining(currentQuestion.timeLimit);
      setQuestionStartTime(Date.now());
    }
  }, [currentQuestion]);

  useEffect(() => {
    if (timeRemaining > 0) {
      const timer = setTimeout(() => {
        setTimeRemaining(timeRemaining - 1);
      }, 1000);
      return () => clearTimeout(timer);
    }
  }, [timeRemaining]);

  // Update current answer with voice transcript
  useEffect(() => {
    if (voiceState.transcript) {
      setCurrentAnswer(voiceState.transcript);
    }
  }, [voiceState.transcript]);

  const handlePlayQuestion = () => {
    if (isQuestionPlaying) {
      speechSynthesis.cancel();
      setIsQuestionPlaying(false);
    } else {
      setIsQuestionPlaying(true);
      speakText(currentQuestion.question);
      
      // Listen for speech end
      const utterance = new SpeechSynthesisUtterance(currentQuestion.question);
      utterance.onend = () => setIsQuestionPlaying(false);
      utterance.onerror = () => setIsQuestionPlaying(false);
    }
  };

  const handleVoiceToggle = () => {
    if (voiceState.isRecording) {
      stopRecording();
    } else {
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
      isVoiceAnswer: voiceState.transcript.length > 0
    };

    const newAnswers = [...answers, answer];
    setAnswers(newAnswers);

    if (currentQuestionIndex < questions.length - 1) {
      setIsTransitioning(true);
      setTimeout(() => {
        setCurrentQuestionIndex(currentQuestionIndex + 1);
        setCurrentAnswer('');
        clearTranscript();
        setIsTransitioning(false);
      }, 500);
    } else {
      onComplete(newAnswers);
    }
  };

  const handleExitInterview = () => {
    setShowExitConfirm(true);
  };

  const confirmExit = () => {
    // Navigate back to setup - this would be handled by parent component
    window.history.back();
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const getTimeColor = () => {
    const percentage = timeRemaining / currentQuestion.timeLimit;
    if (percentage > 0.5) return 'text-green-600';
    if (percentage > 0.25) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getTipForQuestionType = (type: string) => {
    const tips = {
      behavioral: 'Use the STAR method: Situation, Task, Action, Result',
      product_design: 'Walk through your design process step by step',
      analytical: 'Show your analytical framework and reasoning',
      technical: 'Explain technical concepts clearly and consider trade-offs',
      strategic: 'Think about long-term implications and stakeholder impact'
    };
    return tips[type as keyof typeof tips] || 'Structure your response clearly and provide specific examples';
  };

  const progress = ((currentQuestionIndex + 1) / questions.length) * 100;

  if (isTransitioning) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-orange-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-lg text-gray-600">Loading next question...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 p-4">
      <div className="max-w-4xl mx-auto">
        {/* Header with Exit Option */}
        <div className="bg-white rounded-2xl shadow-lg p-6 mb-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-4">
              <button
                onClick={handleExitInterview}
                className="p-2 text-gray-600 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors group"
                title="Exit Interview"
              >
                <ArrowLeft className="w-5 h-5 group-hover:transform group-hover:-translate-x-1 transition-transform" />
              </button>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">{interviewType.name}</h1>
                <div className="flex items-center space-x-2">
                  <p className="text-gray-600">Question {currentQuestionIndex + 1} of {questions.length}</p>
                  {jobDescription && (
                    <div className="flex items-center space-x-1 bg-purple-100 text-purple-700 px-2 py-1 rounded-full text-xs">
                      <Sparkles className="w-3 h-3" />
                      <span>JD Enhanced</span>
                    </div>
                  )}
                </div>
              </div>
            </div>
            <div className="text-right">
              <div className={`text-2xl font-bold ${getTimeColor()}`}>
                {formatTime(timeRemaining)}
              </div>
              <div className="text-sm text-gray-500">Time remaining</div>
            </div>
          </div>

          {/* Progress Bar */}
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className="bg-gradient-to-r from-yellow-500 to-orange-500 h-2 rounded-full transition-all duration-500"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>

        {/* Question Card */}
        <div className="bg-white rounded-2xl shadow-lg p-8 mb-6">
          <div className="flex items-start space-x-4 mb-6">
            <div className={`flex-shrink-0 w-12 h-12 rounded-full flex items-center justify-center ${
              currentQuestion.difficulty === 'easy' ? 'bg-green-100' :
              currentQuestion.difficulty === 'medium' ? 'bg-yellow-100' : 'bg-red-100'
            }`}>
              {currentQuestion.difficulty === 'easy' ? (
                <CheckCircle className="w-6 h-6 text-green-600" />
              ) : currentQuestion.difficulty === 'medium' ? (
                <AlertCircle className="w-6 h-6 text-yellow-600" />
              ) : (
                <AlertCircle className="w-6 h-6 text-red-600" />
              )}
            </div>
            <div className="flex-1">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center space-x-2">
                  <span className={`text-xs px-2 py-1 rounded-full font-medium ${
                    currentQuestion.type === 'behavioral' ? 'bg-blue-100 text-blue-700' :
                    currentQuestion.type === 'product_design' ? 'bg-purple-100 text-purple-700' :
                    currentQuestion.type === 'analytical' ? 'bg-green-100 text-green-700' :
                    currentQuestion.type === 'technical' ? 'bg-orange-100 text-orange-700' :
                    'bg-gray-100 text-gray-700'
                  }`}>
                    {currentQuestion.type.replace('_', ' ').toUpperCase()}
                  </span>
                  <span className={`text-xs px-2 py-1 rounded-full font-medium ${
                    currentQuestion.difficulty === 'easy' ? 'bg-green-100 text-green-700' :
                    currentQuestion.difficulty === 'medium' ? 'bg-yellow-100 text-yellow-700' :
                    'bg-red-100 text-red-700'
                  }`}>
                    {currentQuestion.difficulty.toUpperCase()}
                  </span>
                  {currentQuestion.id.startsWith('jd') && (
                    <span className="text-xs px-2 py-1 rounded-full font-medium bg-purple-100 text-purple-700">
                      JD BASED
                    </span>
                  )}
                </div>
                <button
                  onClick={handlePlayQuestion}
                  className="flex items-center space-x-1 px-3 py-1 bg-orange-100 text-orange-700 rounded-full hover:bg-orange-200 transition-colors"
                >
                  {isQuestionPlaying ? (
                    <VolumeX className="w-4 h-4" />
                  ) : (
                    <Volume2 className="w-4 h-4" />
                  )}
                  <span className="text-xs font-medium">
                    {isQuestionPlaying ? 'Stop' : 'Play'}
                  </span>
                </button>
              </div>
              <h2 className="text-xl font-semibold text-gray-900 leading-relaxed mb-4">
                {currentQuestion.question}
              </h2>

              {/* Tip moved inside question card */}
              <div className="bg-orange-50 rounded-lg p-4 mb-4 border border-orange-200">
                <div className="flex items-start space-x-2">
                  <Lightbulb className="w-5 h-5 text-orange-600 mt-0.5 flex-shrink-0" />
                  <div>
                    <h4 className="font-medium text-orange-900 mb-1">💡 Tip for this question:</h4>
                    <p className="text-sm text-orange-800">
                      {getTipForQuestionType(currentQuestion.type)}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Skills Tags */}
          <div className="mb-6">
            <div className="text-sm font-medium text-gray-700 mb-2">Skills being evaluated:</div>
            <div className="flex flex-wrap gap-2">
              {currentQuestion.skills.map((skill, index) => (
                <span
                  key={index}
                  className="bg-orange-50 text-orange-700 text-sm px-3 py-1 rounded-full font-medium"
                >
                  {skill}
                </span>
              ))}
            </div>
          </div>
        </div>

        {/* Answer Input */}
        <div className="bg-white rounded-2xl shadow-lg p-8">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-2">
              <MessageSquare className="w-5 h-5 text-orange-500" />
              <h3 className="text-lg font-semibold text-gray-900">Your Answer</h3>
            </div>
            
            {isSupported && (
              <div className="flex items-center space-x-2">
                <button
                  onClick={handleVoiceToggle}
                  className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-all ${
                    voiceState.isRecording
                      ? 'bg-red-100 text-red-700 hover:bg-red-200'
                      : 'bg-orange-100 text-orange-700 hover:bg-orange-200'
                  }`}
                >
                  {voiceState.isRecording ? (
                    <MicOff className="w-4 h-4" />
                  ) : (
                    <Mic className="w-4 h-4" />
                  )}
                  <span className="text-sm font-medium">
                    {voiceState.isRecording ? 'Stop Recording' : 'Voice Input'}
                  </span>
                </button>
                
                {voiceState.isRecording && (
                  <div className="flex items-center space-x-2 text-sm text-red-600">
                    <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
                    <span>Recording...</span>
                  </div>
                )}
              </div>
            )}
          </div>
          
          <textarea
            value={currentAnswer}
            onChange={(e) => setCurrentAnswer(e.target.value)}
            placeholder="Start typing your answer here... Or use voice input to speak your response naturally."
            className="w-full h-64 p-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent resize-none text-gray-900 placeholder-gray-500"
          />
          
          <div className="flex items-center justify-between mt-4">
            <div className="flex items-center space-x-4 text-sm text-gray-500">
              <span>{currentAnswer.length} characters • {currentAnswer.split(' ').filter(w => w.length > 0).length} words</span>
              {voiceState.confidence > 0 && (
                <span className="text-orange-600">
                  Voice confidence: {Math.round(voiceState.confidence * 100)}%
                </span>
              )}
            </div>
            
            <button
              onClick={handleNextQuestion}
              disabled={!currentAnswer.trim()}
              className="flex items-center space-x-2 px-6 py-3 bg-gradient-to-r from-yellow-500 to-orange-500 text-white rounded-lg hover:from-yellow-600 hover:to-orange-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all font-medium"
            >
              <span>
                {currentQuestionIndex < questions.length - 1 ? 'Next Question' : 'Complete Interview'}
              </span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Exit Confirmation Modal */}
      {showExitConfirm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-2xl shadow-2xl p-8 max-w-md w-full">
            <div className="text-center">
              <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <AlertCircle className="w-8 h-8 text-red-600" />
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-2">Exit Interview?</h3>
              <p className="text-gray-600 mb-6">
                Are you sure you want to exit? Your progress will be lost and you'll need to start over.
              </p>
              <div className="flex space-x-3">
                <button
                  onClick={() => setShowExitConfirm(false)}
                  className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  Continue Interview
                </button>
                <button
                  onClick={confirmExit}
                  className="flex-1 px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors"
                >
                  Exit Interview
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default InterviewFlow;