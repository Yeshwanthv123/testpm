import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { InterviewType, Question, Answer } from '../types';
import { useVoice } from '../hooks/useVoice';
// Import icons as needed...
import { Clock, MessageSquare, ArrowRight, ArrowLeft } from 'lucide-react';

const InterviewFlow: React.FC = () => {
    const location = useLocation();
    const navigate = useNavigate();

    const [questions, setQuestions] = useState<Question[]>([]);
    const [interviewType, setInterviewType] = useState<InterviewType | null>(null);
    const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
    const [currentAnswer, setCurrentAnswer] = useState('');
    const [answers, setAnswers] = useState<Answer[]>([]);
    const [timeRemaining, setTimeRemaining] = useState(0);
    
    // ... other states like isTransitioning, showExitConfirm etc.

    const { voiceState, startRecording, stopRecording, speakText, clearTranscript } = useVoice();

    useEffect(() => {
        // This is the key change: getting real data from the navigation state
        if (!location.state?.questions || location.state.questions.length === 0) {
            console.error("No questions found, redirecting to setup.");
            navigate('/');
            return;
        }
        setQuestions(location.state.questions);
        setInterviewType(location.state.settings.interviewType);
    }, [location, navigate]);

    const currentQuestion = questions[currentQuestionIndex];

    useEffect(() => {
        if (currentQuestion) {
            setTimeRemaining(currentQuestion.timeLimit);
        }
    }, [currentQuestion]);

    // ... All your other functions (handleNextQuestion, formatTime, timers, etc.) remain the same
    
    const handleNextQuestion = () => {
        if (!currentAnswer.trim() || !currentQuestion) return;

        const answer: Answer = {
            questionId: currentQuestion.id,
            answer: currentAnswer,
            timeSpent: currentQuestion.timeLimit - timeRemaining,
            timestamp: new Date(),
        };

        const newAnswers = [...answers, answer];
        setAnswers(newAnswers);

        if (currentQuestionIndex < questions.length - 1) {
            setCurrentQuestionIndex(prev => prev + 1);
            setCurrentAnswer('');
            clearTranscript();
        } else {
            // On completion, navigate to a dashboard or results page
            navigate('/dashboard', { state: { results: newAnswers } });
        }
    };

    if (!currentQuestion || !interviewType) {
        return (
            <div className="flex items-center justify-center h-screen">
                <p>Loading Interview...</p>
            </div>
        );
    }
    
    // Your full JSX for the interview flow remains here. It will now use `currentQuestion`
    // which contains the real data from your backend.
    return (
        <div className="min-h-screen ...">
           {/* ... Your full interview UI ... */}
           <h2>Question {currentQuestionIndex + 1}: {currentQuestion.question}</h2>
           <textarea value={currentAnswer} onChange={(e) => setCurrentAnswer(e.target.value)} />
           <button onClick={handleNextQuestion}>Next Question</button>
           {/* ... etc. ... */}
        </div>
    );
};

export default InterviewFlow;