export interface User {
  id: string;
  full_name: string; // Changed from 'name' to 'full_name'
  email: string;
  experience: string;
  targetCompanies: string[];
  region: string;
  currentRole: string;
}

export interface Question {
  id: string;
  type: 'behavioral' | 'product_design' | 'analytical' | 'technical' | 'strategic';
  category: string;
  question: string;
  followUpQuestions?: string[];
  timeLimit: number;
  difficulty: 'easy' | 'medium' | 'hard';
  skills: string[];
}

// ... (rest of the file is unchanged)
export interface InterviewSession {
  id: string;
  userId: string;
  interviewType: string;
  questions: Question[];
  answers: Answer[];
  startTime: Date;
  endTime?: Date;
  status: 'in_progress' | 'completed' | 'abandoned';
}

export interface Answer {
  questionId: string;
  answer: string;
  timeSpent: number;
  timestamp: Date;
  isVoiceAnswer?: boolean;
}

export interface SkillScore {
  skill: string;
  score: number;
  maxScore: number;
  percentile: number;
  feedback: string;
  trend?: 'up' | 'down' | 'stable';
  industryAverage?: number;
}

export interface InterviewResult {
  sessionId: string;
  overallScore: number;
  skillScores: SkillScore[];
  strengths: string[];
  improvements: string[];
  peerComparison: PeerComparison;
  detailedFeedback: string;
}

export interface PeerComparison {
  region: {
    average: number;
    percentile: number;
  };
  experience: {
    average: number;
    percentile: number;
  };
  overall: {
    average: number;
    percentile: number;
    totalCandidates: number;
  };
}

export interface InterviewType {
  id: string;
  name: string;
  company?: string;
  description: string;
  duration: number;
  questionCount: number;
  skills: string[];
  icon: string;
  color: string;
  isGeneral?: boolean;
  companyLogo?: string;
  companyColor?: string;
}

export interface VoiceRecording {
  isRecording: boolean;
  transcript: string;
  confidence: number;
}