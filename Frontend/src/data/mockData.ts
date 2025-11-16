import { Question, InterviewType, SkillScore, PeerComparison } from '../types';

export const interviewTypes: InterviewType[] = [
  {
    id: 'general-pm',
    name: 'General Product Management',
    description: 'Comprehensive PM interview covering all core competencies across industries',
    duration: 40,
    questionCount: 8,
    skills: ['Product Strategy', 'Execution', 'Leadership', 'Analytics', 'Communication', 'Vision'],
    icon: 'Target',
    color: 'from-blue-500 to-cyan-500',
    isGeneral: true
  },
  {
    id: 'google-pm',
    name: 'Google PM',
    company: 'Google',
    description: 'Google-style product management interview with emphasis on scale and innovation',
    duration: 40,
    questionCount: 8,
    skills: ['Product Strategy', 'Technical Depth', 'Leadership', 'Data Analysis', 'Innovation'],
    icon: 'Chrome',
    color: 'from-red-500 to-yellow-500',
    companyLogo: '🔍',
    companyColor: 'bg-red-50 border-red-200'
  },
  {
    id: 'meta-pm',
    name: 'Meta PM',
    company: 'Meta',
    description: 'Meta-focused interview emphasizing user engagement and growth',
    duration: 40,
    questionCount: 8,
    skills: ['Growth', 'User Experience', 'Analytics', 'Vision', 'Social Impact'],
    icon: 'Users',
    color: 'from-blue-600 to-purple-600',
    companyLogo: '👥',
    companyColor: 'bg-blue-50 border-blue-200'
  },
  {
    id: 'amazon-pm',
    name: 'Amazon PM',
    company: 'Amazon',
    description: 'Amazon leadership principles and customer obsession focused interview',
    duration: 40,
    questionCount: 8,
    skills: ['Customer Focus', 'Leadership', 'Operations', 'Innovation', 'Ownership'],
    icon: 'Package',
    color: 'from-orange-500 to-yellow-500',
    companyLogo: '📦',
    companyColor: 'bg-orange-50 border-orange-200'
  },
  {
    id: 'microsoft-pm',
    name: 'Microsoft PM',
    company: 'Microsoft',
    description: 'Microsoft-style interview focusing on enterprise solutions and partnerships',
    duration: 40,
    questionCount: 8,
    skills: ['Enterprise Strategy', 'Partnerships', 'Technical Vision', 'Execution', 'Collaboration'],
    icon: 'Building2',
    color: 'from-blue-500 to-teal-500',
    companyLogo: '🪟',
    companyColor: 'bg-blue-50 border-blue-200'
  },
  {
    id: 'apple-pm',
    name: 'Apple PM',
    company: 'Apple',
    description: 'Apple-focused interview emphasizing design thinking and user experience',
    duration: 40,
    questionCount: 8,
    skills: ['Design Thinking', 'User Experience', 'Innovation', 'Quality', 'Simplicity'],
    icon: 'Smartphone',
    color: 'from-gray-600 to-gray-800',
    companyLogo: '🍎',
    companyColor: 'bg-gray-50 border-gray-200'
  },
  {
    id: 'netflix-pm',
    name: 'Netflix PM',
    company: 'Netflix',
    description: 'Netflix-style interview focusing on content strategy and personalization',
    duration: 40,
    questionCount: 8,
    skills: ['Content Strategy', 'Personalization', 'Analytics', 'Global Thinking', 'Innovation'],
    icon: 'Play',
    color: 'from-red-600 to-red-800',
    companyLogo: '🎬',
    companyColor: 'bg-red-50 border-red-200'
  },
  {
    id: 'uber-pm',
    name: 'Uber PM',
    company: 'Uber',
    description: 'Uber-focused interview emphasizing marketplace dynamics and operations',
    duration: 40,
    questionCount: 8,
    skills: ['Marketplace Strategy', 'Operations', 'Growth', 'Analytics', 'Global Expansion'],
    icon: 'Car',
    color: 'from-black to-gray-700',
    companyLogo: '🚗',
    companyColor: 'bg-gray-50 border-gray-200'
  }
];

export const sampleQuestions: Question[] = [
  {
    id: 'q1',
    type: 'product_design',
    category: 'Product Strategy',
    question: 'Design a product for people who are new to a city. Walk me through your approach.',
    timeLimit: 300,
    difficulty: 'medium',
    skills: ['Product Strategy', 'User Research', 'Design Thinking']
  },
  {
    id: 'q2',
    type: 'analytical',
    category: 'Data Analysis',
    question: 'Instagram Stories engagement has dropped 15% over the last month. How would you investigate and address this?',
    timeLimit: 240,
    difficulty: 'hard',
    skills: ['Analytics', 'Problem Solving', 'Hypothesis Testing']
  },
  {
    id: 'q3',
    type: 'behavioral',
    category: 'Leadership',
    question: 'Tell me about a time when you had to influence a team without having direct authority over them.',
    timeLimit: 180,
    difficulty: 'medium',
    skills: ['Leadership', 'Communication', 'Influence']
  },
  {
    id: 'q4',
    type: 'strategic',
    category: 'Vision',
    question: 'How would you prioritize features for a new fintech app targeting Gen Z users?',
    timeLimit: 270,
    difficulty: 'medium',
    skills: ['Prioritization', 'User Understanding', 'Strategy']
  },
  {
    id: 'q5',
    type: 'technical',
    category: 'Technical Depth',
    question: 'Explain to me how you would scale a messaging platform to support 1 billion users.',
    timeLimit: 300,
    difficulty: 'hard',
    skills: ['Technical Knowledge', 'Systems Thinking', 'Scalability']
  }
];

export const mockSkillScores: SkillScore[] = [
  {
    skill: 'Product Strategy',
    score: 85,
    maxScore: 100,
    percentile: 78,
    feedback: 'Strong strategic thinking with clear framework application. Consider diving deeper into competitive analysis.',
    trend: 'up',
    industryAverage: 72
  },
  {
    skill: 'Execution',
    score: 92,
    maxScore: 100,
    percentile: 89,
    feedback: 'Excellent execution mindset with practical solutions. Great attention to implementation details.',
    trend: 'up',
    industryAverage: 75
  },
  {
    skill: 'Communication',
    score: 78,
    maxScore: 100,
    percentile: 65,
    feedback: 'Clear communication overall. Work on structuring complex responses and improving storytelling.',
    trend: 'stable',
    industryAverage: 80
  },
  {
    skill: 'Analytics',
    score: 88,
    maxScore: 100,
    percentile: 82,
    feedback: 'Strong analytical approach with good metric selection. Consider exploring more advanced statistical concepts.',
    trend: 'up',
    industryAverage: 73
  },
  {
    skill: 'Leadership',
    score: 81,
    maxScore: 100,
    percentile: 71,
    feedback: 'Good leadership examples with clear impact. Expand on team motivation and conflict resolution strategies.',
    trend: 'stable',
    industryAverage: 77
  },
  {
    skill: 'Vision',
    score: 89,
    maxScore: 100,
    percentile: 85,
    feedback: 'Impressive long-term thinking and market understanding. Continue developing ecosystem perspective.',
    trend: 'up',
    industryAverage: 71
  }
];

export const mockPeerComparison: PeerComparison = {
  region: {
    average: 76,
    percentile: 73
  },
  experience: {
    average: 82,
    percentile: 68
  },
  overall: {
    average: 79,
    percentile: 75,
    totalCandidates: 2847
  }
};

export const detailedInsights = {
  strengths: [
    {
      title: 'Strategic Framework Application',
      description: 'Consistently applied structured frameworks like RICE, Jobs-to-be-Done, and competitive analysis across multiple questions.',
      impact: 'This systematic approach demonstrates senior-level thinking and would translate well to real PM responsibilities.',
      examples: ['Used RICE prioritization for feature ranking', 'Applied competitive moats analysis', 'Structured market sizing with TAM/SAM/SOM']
    },
    {
      title: 'Execution Excellence',
      description: 'Showed strong ability to break down complex problems into actionable steps with clear timelines and success metrics.',
      impact: 'This execution mindset is crucial for driving products from concept to launch successfully.',
      examples: ['Defined clear success metrics for each initiative', 'Created realistic project timelines', 'Identified potential blockers proactively']
    },
    {
      title: 'Data-Driven Decision Making',
      description: 'Consistently referenced metrics, A/B testing, and quantitative analysis to support recommendations.',
      impact: 'This analytical rigor helps build credibility with engineering teams and executives.',
      examples: ['Proposed specific A/B test designs', 'Referenced industry benchmarks', 'Suggested cohort analysis approaches']
    }
  ],
  improvements: [
    {
      title: 'Stakeholder Management Depth',
      description: 'While you mentioned stakeholders, responses could benefit from more detailed strategies for managing different stakeholder types.',
      actionItems: [
        'Practice RACI matrix creation for complex projects',
        'Develop templates for stakeholder communication plans',
        'Study conflict resolution techniques for cross-functional teams'
      ],
      resources: ['Read "Crucial Conversations" by Kerry Patterson', 'Take a negotiation course', 'Practice stakeholder mapping exercises']
    },
    {
      title: 'Technical Architecture Understanding',
      description: 'Some responses showed gaps in understanding technical trade-offs and system design implications.',
      actionItems: [
        'Learn basic system design principles',
        'Understand API design and database concepts',
        'Study scalability patterns and their business implications'
      ],
      resources: ['Complete "System Design Interview" course', 'Partner with engineers on technical deep-dives', 'Read "Designing Data-Intensive Applications"']
    },
    {
      title: 'Quantitative Analysis Sophistication',
      description: 'While you used metrics well, consider incorporating more advanced statistical concepts and modeling.',
      actionItems: [
        'Learn statistical significance testing',
        'Practice cohort analysis and retention modeling',
        'Understand causal inference basics'
      ],
      resources: ['Take a statistics refresher course', 'Use tools like Amplitude or Mixpanel', 'Read "Trustworthy Online Controlled Experiments"']
    }
  ],
  careerGuidance: {
    currentLevel: 'Senior PM Ready',
    nextLevel: 'Principal PM',
    timeToNextLevel: '12-18 months',
    keyFocusAreas: [
      'Develop deeper technical architecture knowledge',
      'Build stronger stakeholder influence skills',
      'Gain experience with larger, more complex initiatives'
    ],
    recommendedRoles: [
      'Senior Product Manager at growth-stage startups',
      'Product Manager II at FAANG companies',
      'Lead Product Manager at established tech companies'
    ]
  }
};