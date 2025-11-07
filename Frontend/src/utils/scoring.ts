import { Answer, Question, SkillScore } from '../types';

export const calculateSkillScore = (
  answers: Answer[],
  questions: Question[],
  skill: string
): number => {
  // Match skills case-insensitively and allow partial matches so that
  // backend-derived skills (e.g. "Strategy") map to frontend skill names
  // (e.g. "Product Strategy"). This makes scoring robust across sources.
  const relevantQuestions = questions.filter((q) => {
    if (!Array.isArray(q.skills) || !q.skills.length) return false;
    const target = (skill || '').toLowerCase();
    return q.skills.some((s) => {
      const ss = String(s || '').toLowerCase();
      return ss === target || ss.includes(target) || target.includes(ss);
    });
  });
  if (relevantQuestions.length === 0) return 0;

  let totalScore = 0;
  let maxPossibleScore = 0;

  relevantQuestions.forEach(question => {
    const answer = answers.find(a => a.questionId === question.id);
    if (answer) {
      // Mock scoring algorithm - in real app, this would use AI
      const wordCount = String(answer.answer || '').split(/\s+/).filter(Boolean).length;
      const timeLimit = question.timeLimit && question.timeLimit > 0 ? question.timeLimit : 180;
      const timeEfficiency = Math.min((answer.timeSpent || 0) / timeLimit, 1);
      const contentScore = Math.min(wordCount / 50, 1) * 70; // Up to 70 points for content
      const efficiencyScore = (1 - timeEfficiency) * 30; // Up to 30 points for efficiency
      
      totalScore += contentScore + efficiencyScore;
    }
    maxPossibleScore += 100;
  });

  return maxPossibleScore > 0 ? Math.round((totalScore / maxPossibleScore) * 100) : 0;
};

export const generateFeedback = (score: number, skill: string): string => {
  const feedbackTemplates = {
    'Product Strategy': {
      excellent: 'Exceptional strategic thinking with comprehensive market analysis and clear value propositions.',
      good: 'Strong strategic foundation with room for deeper competitive analysis and market positioning.',
      needs_improvement: 'Focus on developing structured frameworks for strategy development and market assessment.'
    },
    'Execution': {
      excellent: 'Outstanding execution mindset with detailed implementation plans and risk mitigation strategies.',
      good: 'Solid execution approach with practical solutions and clear prioritization.',
      needs_improvement: 'Work on breaking down complex projects and developing detailed execution roadmaps.'
    },
    'Communication': {
      excellent: 'Exceptional communication skills with clear structure, compelling storytelling, and audience awareness.',
      good: 'Good communication with clear explanations and logical flow.',
      needs_improvement: 'Focus on structuring responses better and improving clarity in complex explanations.'
    }
  };

  const skillFeedback = feedbackTemplates[skill as keyof typeof feedbackTemplates] || {
    excellent: 'Excellent performance in this area.',
    good: 'Good performance with room for improvement.',
    needs_improvement: 'This area needs focused development.'
  };

  if (score >= 85) return skillFeedback.excellent;
  if (score >= 70) return skillFeedback.good;
  return skillFeedback.needs_improvement;
};

export const calculatePercentile = (score: number, skill: string): number => {
  // Mock percentile calculation - in real app, this would query actual data
  const basePercentile = (score / 100) * 80; // Base percentile
  const randomVariation = Math.random() * 20 - 10; // Add some variation
  return Math.max(5, Math.min(95, Math.round(basePercentile + randomVariation)));
};