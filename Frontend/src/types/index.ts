export interface User {
  id: number; // backend uses number IDs
  full_name: string;
  email: string;
  experience: string;
  targetCompanies: string[];
  region: string;
  currentRole: string;
}

export interface Question {
  id: string;
  type: 'behavioral' | 'product_design' | 'analytical' | 'technical' | 'strategic' | string;
  category: string;
  question: string;
  followUpQuestions?: string[];
  timeLimit: number; // in seconds
  difficulty: 'easy' | 'medium' | 'hard' | string;
  skills: string[];

  // --- optional backend fields (do not break existing logic) ---
  text?: string | null;
  company?: string | null;
  complexity?: string | null;
  experience_level?: string | null;
  years_of_experience?: string | null;
  created_at?: string | null | Date;
  [key: string]: any;
}

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
  answer: string; // Can be text or a URL to a voice file
  timeSpent: number; // in seconds
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
  duration: number; // in minutes
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
