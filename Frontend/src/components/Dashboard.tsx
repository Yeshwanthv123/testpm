import React, { useState } from 'react';
import { 
  TrendingUp, Award, Users, MapPin, Star, ChevronRight, 
  BarChart3, Target, Brain, MessageSquare, Lightbulb, 
  Download, Share2, RotateCcw, ArrowUp, ArrowDown, 
  Minus, Trophy, Zap, BookOpen, AlertTriangle
} from 'lucide-react';
import { 
  RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, 
  ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, 
  Tooltip, LineChart, Line, PieChart, Pie, Cell
} from 'recharts';
import { InterviewResult, SkillScore } from '../types';
import { mockSkillScores, mockPeerComparison, detailedInsights } from '../data/mockData';

interface DashboardProps {
  result: InterviewResult;
  onRetakeInterview: () => void;
}

const Dashboard: React.FC<DashboardProps> = ({ result, onRetakeInterview }) => {
  const [selectedSkill, setSelectedSkill] = useState<SkillScore | null>(null);
  const [activeTab, setActiveTab] = useState<'overview' | 'skills' | 'insights' | 'comparison'>('overview');

  const overallScore = Math.round(result.skillScores.reduce((sum, skill) => sum + skill.score, 0) / result.skillScores.length);
  
  const getScoreColor = (score: number) => {
    if (score >= 85) return 'text-green-600';
    if (score >= 70) return 'text-blue-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreBgColor = (score: number) => {
    if (score >= 85) return 'bg-green-100';
    if (score >= 70) return 'bg-blue-100';
    if (score >= 60) return 'bg-yellow-100';
    return 'bg-red-100';
  };

  const getPerformanceLevel = (score: number) => {
    if (score >= 85) return 'Excellent';
    if (score >= 70) return 'Good';
    if (score >= 60) return 'Fair';
    return 'Needs Improvement';
  };

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'up': return <ArrowUp className="w-4 h-4 text-green-500" />;
      case 'down': return <ArrowDown className="w-4 h-4 text-red-500" />;
      default: return <Minus className="w-4 h-4 text-gray-500" />;
    }
  };

  // Prepare data for charts
  const radarData = result.skillScores.map(skill => ({
    skill: skill.skill.replace(' ', '\n'),
    score: skill.score,
    industry: skill.industryAverage || 75
  }));

  const barData = result.skillScores.map(skill => ({
    name: skill.skill,
    score: skill.score,
    industry: skill.industryAverage || 75,
    percentile: skill.percentile
  }));

  const pieData = [
    { name: 'Excellent (85+)', value: result.skillScores.filter(s => s.score >= 85).length, color: '#10B981' },
    { name: 'Good (70-84)', value: result.skillScores.filter(s => s.score >= 70 && s.score < 85).length, color: '#3B82F6' },
    { name: 'Fair (60-69)', value: result.skillScores.filter(s => s.score >= 60 && s.score < 70).length, color: '#F59E0B' },
    { name: 'Needs Work (<60)', value: result.skillScores.filter(s => s.score < 60).length, color: '#EF4444' }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 p-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">Interview Performance Analysis</h1>
          <p className="text-xl text-gray-600">Comprehensive AI-powered evaluation of your PM interview</p>
        </div>

        {/* Overall Score Hero Section */}
        <div className="bg-white rounded-3xl shadow-2xl p-8 mb-8 relative overflow-hidden">
          <div className="absolute top-0 right-0 w-64 h-64 bg-gradient-to-br from-blue-500 to-purple-500 opacity-5 rounded-full transform translate-x-32 -translate-y-32" />
          
          <div className="relative">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-center">
              <div>
                <div className="flex items-center space-x-4 mb-6">
                  <div className={`text-6xl font-bold ${getScoreColor(overallScore)}`}>
                    {overallScore}
                  </div>
                  <div>
                    <div className="text-2xl font-bold text-gray-900">{getPerformanceLevel(overallScore)}</div>
                    <div className="text-gray-600">Overall Performance</div>
                    <div className="flex items-center space-x-2 mt-1">
                      <Trophy className="w-4 h-4 text-yellow-500" />
                      <span className="text-sm text-gray-600">{result.peerComparison.overall.percentile}th percentile</span>
                    </div>
                  </div>
                </div>
                
                <div className="grid grid-cols-3 gap-4">
                  <div className="text-center p-4 bg-gradient-to-br from-green-50 to-green-100 rounded-xl">
                    <Zap className="w-6 h-6 text-green-600 mx-auto mb-2" />
                    <div className="font-bold text-xl text-green-900">
                      {result.skillScores.filter(s => s.score >= 85).length}
                    </div>
                    <div className="text-sm text-green-700">Skills Mastered</div>
                  </div>
                  <div className="text-center p-4 bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl">
                    <Users className="w-6 h-6 text-blue-600 mx-auto mb-2" />
                    <div className="font-bold text-xl text-blue-900">{result.peerComparison.overall.percentile}%</div>
                    <div className="text-sm text-blue-700">Better than peers</div>
                  </div>
                  <div className="text-center p-4 bg-gradient-to-br from-purple-50 to-purple-100 rounded-xl">
                    <Target className="w-6 h-6 text-purple-600 mx-auto mb-2" />
                    <div className="font-bold text-xl text-purple-900">
                      {Math.round((result.skillScores.reduce((sum, s) => sum + s.percentile, 0) / result.skillScores.length))}
                    </div>
                    <div className="text-sm text-purple-700">Avg Percentile</div>
                  </div>
                </div>
              </div>
              
              <div className="h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <RadarChart data={radarData}>
                    <PolarGrid />
                    <PolarAngleAxis dataKey="skill" tick={{ fontSize: 12 }} />
                    <PolarRadiusAxis angle={90} domain={[0, 100]} tick={false} />
                    <Radar name="Your Score" dataKey="score" stroke="#3B82F6" fill="#3B82F6" fillOpacity={0.3} strokeWidth={2} />
                    <Radar name="Industry Avg" dataKey="industry" stroke="#94A3B8" fill="transparent" strokeWidth={1} strokeDasharray="5 5" />
                  </RadarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        </div>

        {/* Navigation Tabs */}
        <div className="bg-white rounded-2xl shadow-lg p-2 mb-8">
          <div className="flex space-x-1">
            {[
              { id: 'overview', label: 'Overview', icon: BarChart3 },
              { id: 'skills', label: 'Skills Analysis', icon: Target },
              { id: 'insights', label: 'Detailed Insights', icon: Brain },
              { id: 'comparison', label: 'Peer Comparison', icon: Users }
            ].map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as any)}
                  className={`flex items-center space-x-2 px-6 py-3 rounded-xl font-medium transition-all ${
                    activeTab === tab.id
                      ? 'bg-gradient-to-r from-blue-500 to-purple-500 text-white shadow-lg'
                      : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span>{tab.label}</span>
                </button>
              );
            })}
          </div>
        </div>

        {/* Tab Content */}
        {activeTab === 'overview' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Skills Performance Chart */}
            <div className="bg-white rounded-2xl shadow-lg p-6">
              <h3 className="text-xl font-bold text-gray-900 mb-6">Skills Performance vs Industry</h3>
              <div className="h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={barData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" angle={-45} textAnchor="end" height={80} fontSize={12} />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="score" fill="#3B82F6" name="Your Score" radius={[4, 4, 0, 0]} />
                    <Bar dataKey="industry" fill="#94A3B8" name="Industry Average" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Performance Distribution */}
            <div className="bg-white rounded-2xl shadow-lg p-6">
              <h3 className="text-xl font-bold text-gray-900 mb-6">Performance Distribution</h3>
              <div className="h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={pieData}
                      cx="50%"
                      cy="50%"
                      outerRadius={100}
                      fill="#8884d8"
                      dataKey="value"
                      label={({ name, value }) => value > 0 ? `${name}: ${value}` : ''}
                    >
                      {pieData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'skills' && (
          <div className="bg-white rounded-2xl shadow-lg p-6">
            <h3 className="text-xl font-bold text-gray-900 mb-6">Detailed Skills Analysis</h3>
            
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {result.skillScores.map((skill, index) => (
                <div 
                  key={skill.skill}
                  onClick={() => setSelectedSkill(selectedSkill?.skill === skill.skill ? null : skill)}
                  className="cursor-pointer hover:bg-gray-50 p-6 rounded-xl border border-gray-200 transition-all"
                >
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center space-x-3">
                      <div className={`w-4 h-4 rounded-full ${
                        skill.score >= 85 ? 'bg-green-500' :
                        skill.score >= 70 ? 'bg-blue-500' :
                        skill.score >= 60 ? 'bg-yellow-500' : 'bg-red-500'
                      }`} />
                      <span className="font-semibold text-gray-900">{skill.skill}</span>
                      {getTrendIcon(skill.trend || 'stable')}
                    </div>
                    <div className="text-right">
                      <div className={`text-2xl font-bold ${getScoreColor(skill.score)}`}>
                        {skill.score}
                      </div>
                      <div className="text-xs text-gray-500">{skill.percentile}th percentile</div>
                    </div>
                  </div>
                  
                  <div className="mb-3">
                    <div className="flex justify-between text-sm text-gray-600 mb-1">
                      <span>Your Score</span>
                      <span>Industry Avg: {skill.industryAverage}</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-3">
                      <div 
                        className={`h-3 rounded-full transition-all duration-500 ${
                          skill.score >= 85 ? 'bg-green-500' :
                          skill.score >= 70 ? 'bg-blue-500' :
                          skill.score >= 60 ? 'bg-yellow-500' : 'bg-red-500'
                        }`}
                        style={{ width: `${skill.score}%` }}
                      />
                    </div>
                  </div>
                  
                  {selectedSkill?.skill === skill.skill && (
                    <div className="mt-4 p-4 bg-gray-50 rounded-lg">
                      <p className="text-sm text-gray-700">{skill.feedback}</p>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'insights' && (
          <div className="space-y-8">
            {/* Strengths */}
            <div className="bg-white rounded-2xl shadow-lg p-8">
              <div className="flex items-center space-x-3 mb-6">
                <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
                  <Trophy className="w-5 h-5 text-green-600" />
                </div>
                <h3 className="text-2xl font-bold text-gray-900">Key Strengths</h3>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {detailedInsights.strengths.map((strength, index) => (
                  <div key={index} className="bg-green-50 rounded-xl p-6 border border-green-200">
                    <h4 className="font-bold text-green-900 mb-3">{strength.title}</h4>
                    <p className="text-green-800 text-sm mb-4">{strength.description}</p>
                    <div className="mb-4">
                      <div className="font-medium text-green-900 text-sm mb-2">Impact:</div>
                      <p className="text-green-700 text-xs">{strength.impact}</p>
                    </div>
                    <div>
                      <div className="font-medium text-green-900 text-sm mb-2">Examples:</div>
                      <ul className="text-green-700 text-xs space-y-1">
                        {strength.examples.map((example, i) => (
                          <li key={i}>• {example}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Areas for Improvement */}
            <div className="bg-white rounded-2xl shadow-lg p-8">
              <div className="flex items-center space-x-3 mb-6">
                <div className="w-10 h-10 bg-yellow-100 rounded-full flex items-center justify-center">
                  <AlertTriangle className="w-5 h-5 text-yellow-600" />
                </div>
                <h3 className="text-2xl font-bold text-gray-900">Growth Opportunities</h3>
              </div>
              
              <div className="space-y-6">
                {detailedInsights.improvements.map((improvement, index) => (
                  <div key={index} className="bg-yellow-50 rounded-xl p-6 border border-yellow-200">
                    <h4 className="font-bold text-yellow-900 mb-3">{improvement.title}</h4>
                    <p className="text-yellow-800 text-sm mb-4">{improvement.description}</p>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <div className="font-medium text-yellow-900 text-sm mb-2">Action Items:</div>
                        <ul className="text-yellow-700 text-xs space-y-1">
                          {improvement.actionItems.map((item, i) => (
                            <li key={i}>• {item}</li>
                          ))}
                        </ul>
                      </div>
                      <div>
                        <div className="font-medium text-yellow-900 text-sm mb-2">Resources:</div>
                        <ul className="text-yellow-700 text-xs space-y-1">
                          {improvement.resources.map((resource, i) => (
                            <li key={i}>• {resource}</li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Career Guidance */}
            <div className="bg-white rounded-2xl shadow-lg p-8">
              <div className="flex items-center space-x-3 mb-6">
                <div className="w-10 h-10 bg-purple-100 rounded-full flex items-center justify-center">
                  <BookOpen className="w-5 h-5 text-purple-600" />
                </div>
                <h3 className="text-2xl font-bold text-gray-900">Career Guidance</h3>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div className="space-y-4">
                  <div className="bg-purple-50 rounded-lg p-4">
                    <div className="font-semibold text-purple-900 mb-2">Current Assessment</div>
                    <div className="text-purple-800">{detailedInsights.careerGuidance.currentLevel}</div>
                  </div>
                  
                  <div className="bg-blue-50 rounded-lg p-4">
                    <div className="font-semibold text-blue-900 mb-2">Next Level Target</div>
                    <div className="text-blue-800">{detailedInsights.careerGuidance.nextLevel}</div>
                    <div className="text-blue-600 text-sm mt-1">
                      Estimated timeline: {detailedInsights.careerGuidance.timeToNextLevel}
                    </div>
                  </div>
                </div>
                
                <div className="space-y-4">
                  <div>
                    <div className="font-semibold text-gray-900 mb-2">Key Focus Areas</div>
                    <ul className="text-gray-700 text-sm space-y-1">
                      {detailedInsights.careerGuidance.keyFocusAreas.map((area, i) => (
                        <li key={i}>• {area}</li>
                      ))}
                    </ul>
                  </div>
                  
                  <div>
                    <div className="font-semibold text-gray-900 mb-2">Recommended Roles</div>
                    <ul className="text-gray-700 text-sm space-y-1">
                      {detailedInsights.careerGuidance.recommendedRoles.map((role, i) => (
                        <li key={i}>• {role}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'comparison' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Peer Comparison */}
            <div className="bg-white rounded-2xl shadow-lg p-6">
              <h3 className="text-xl font-bold text-gray-900 mb-6 flex items-center">
                <Users className="w-6 h-6 mr-2 text-green-500" />
                Peer Comparison
              </h3>
              
              <div className="space-y-4">
                <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                  <div className="flex items-center space-x-2">
                    <MapPin className="w-4 h-4 text-blue-500" />
                    <span className="text-sm font-medium text-gray-700">Regional</span>
                  </div>
                  <div className="text-right">
                    <div className="font-bold text-gray-900">{result.peerComparison.region.percentile}%</div>
                    <div className="text-xs text-gray-500">vs {result.peerComparison.region.average} avg</div>
                  </div>
                </div>
                
                <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                  <div className="flex items-center space-x-2">
                    <Lightbulb className="w-4 h-4 text-yellow-500" />
                    <span className="text-sm font-medium text-gray-700">Experience</span>
                  </div>
                  <div className="text-right">
                    <div className="font-bold text-gray-900">{result.peerComparison.experience.percentile}%</div>
                    <div className="text-xs text-gray-500">vs {result.peerComparison.experience.average} avg</div>
                  </div>
                </div>
                
                <div className="flex items-center justify-between p-4 bg-blue-50 rounded-lg border-2 border-blue-200">
                  <div className="flex items-center space-x-2">
                    <Target className="w-4 h-4 text-blue-500" />
                    <span className="text-sm font-medium text-blue-700">Overall</span>
                  </div>
                  <div className="text-right">
                    <div className="font-bold text-blue-900">{result.peerComparison.overall.percentile}%</div>
                    <div className="text-xs text-blue-600">vs {result.peerComparison.overall.average} avg</div>
                  </div>
                </div>
              </div>
              
              <div className="mt-4 p-3 bg-green-50 rounded-lg">
                <p className="text-xs text-green-700">
                  Compared against {result.peerComparison.overall.totalCandidates.toLocaleString()} candidates
                </p>
              </div>
            </div>

            {/* Actions */}
            <div className="bg-white rounded-2xl shadow-lg p-6">
              <h3 className="text-xl font-bold text-gray-900 mb-6">Next Steps</h3>
              
              <div className="space-y-4">
                <button 
                  onClick={onRetakeInterview}
                  className="w-full flex items-center justify-center space-x-2 px-6 py-4 bg-gradient-to-r from-blue-500 to-purple-500 text-white rounded-xl hover:from-blue-600 hover:to-purple-600 transition-all transform hover:scale-105 font-medium"
                >
                  <RotateCcw className="w-5 h-5" />
                  <span>Retake Interview</span>
                </button>
                
                <button className="w-full flex items-center justify-center space-x-2 px-6 py-4 border-2 border-gray-300 text-gray-700 rounded-xl hover:bg-gray-50 transition-all font-medium">
                  <Download className="w-5 h-5" />
                  <span>Download Detailed Report</span>
                </button>
                
                <button className="w-full flex items-center justify-center space-x-2 px-6 py-4 border-2 border-gray-300 text-gray-700 rounded-xl hover:bg-gray-50 transition-all font-medium">
                  <Share2 className="w-5 h-5" />
                  <span>Share Results</span>
                </button>
              </div>
              
              <div className="mt-6 p-4 bg-blue-50 rounded-lg">
                <h4 className="font-medium text-blue-900 mb-2">💡 Pro Tips</h4>
                <ul className="text-sm text-blue-800 space-y-1">
                  <li>• Practice with different company types</li>
                  <li>• Focus on your lowest-scoring skills</li>
                  <li>• Use voice input for more natural responses</li>
                  <li>• Review detailed feedback for each skill</li>
                </ul>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;