import React, { useState } from 'react';
import { Users, Target, Zap } from 'lucide-react';
import { RadarChart, PolarGrid, PolarAngleAxis, Radar, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, PieChart, Pie, Cell } from 'recharts';
import { InterviewResult } from '../types';
import { detailedInsights } from '../data/mockData';

interface DashboardProps {
  result: InterviewResult;
  onRetakeInterview: () => void;
}

const Dashboard: React.FC<DashboardProps> = ({ result, onRetakeInterview }) => {
  const [activeTab, setActiveTab] = useState<'overview' | 'skills' | 'insights' | 'comparison'>('overview');

  const overallScore = Math.round(result.skillScores.reduce((s, k) => s + k.score, 0) / Math.max(1, result.skillScores.length));

  const radarData = result.skillScores.map(s => ({ skill: s.skill, score: s.score, industry: s.industryAverage || 75 }));
  const barData = result.skillScores.map(s => ({ name: s.skill, score: s.score, industry: s.industryAverage || 75 }));
  const pieData = [
    { name: 'Excellent (85+)', value: result.skillScores.filter(s => s.score >= 85).length, color: '#10B981' },
    { name: 'Good (70-84)', value: result.skillScores.filter(s => s.score >= 70 && s.score < 85).length, color: '#3B82F6' },
    { name: 'Fair (60-69)', value: result.skillScores.filter(s => s.score >= 60 && s.score < 70).length, color: '#F59E0B' },
    { name: 'Needs Work (<60)', value: result.skillScores.filter(s => s.score < 60).length, color: '#EF4444' }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 p-4">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">Interview Performance Analysis</h1>
          <p className="text-xl text-gray-600">Comprehensive AI-powered evaluation of your PM interview</p>
        </div>

        <div className="bg-white rounded-3xl shadow-2xl p-8 mb-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-center">
            <div>
              <div className="text-6xl font-bold text-gray-900">{overallScore}</div>
              <div className="mt-2 text-gray-600">Overall Performance</div>
              <div className="mt-4 grid grid-cols-3 gap-4">
                <div className="text-center p-4 bg-green-50 rounded-xl">
                  <Zap className="mx-auto mb-2" />
                  <div className="font-bold">{result.skillScores.filter(s => s.score >= 85).length}</div>
                  <div className="text-sm text-green-700">Skills Mastered</div>
                </div>
                <div className="text-center p-4 bg-blue-50 rounded-xl">
                  <Users className="mx-auto mb-2" />
                  <div className="font-bold">{result.peerComparison.overall.percentile}%</div>
                  <div className="text-sm text-blue-700">Better than peers</div>
                </div>
                <div className="text-center p-4 bg-purple-50 rounded-xl">
                  <Target className="mx-auto mb-2" />
                  <div className="font-bold">{Math.round((result.skillScores.reduce((sum, s) => sum + (s.percentile||0), 0) / Math.max(1, result.skillScores.length)))}</div>
                  <div className="text-sm text-purple-700">Avg Percentile</div>
                </div>
              </div>
            </div>
            <div className="h-72">
              <ResponsiveContainer width="100%" height="100%">
                <RadarChart data={radarData}>
                  <PolarGrid />
                  <PolarAngleAxis dataKey="skill" />
                  <Radar name="You" dataKey="score" stroke="#3B82F6" fill="#3B82F6" fillOpacity={0.25} />
                </RadarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-2xl shadow-lg p-2 mb-8">
          <div className="flex space-x-1">
            {[{ id: 'overview', label: 'Overview' },{ id: 'skills', label: 'Skills Analysis' },{ id: 'insights', label: 'Detailed Insights' },{ id: 'comparison', label: 'Peer Comparison' }].map(t => (
              <button key={t.id} onClick={() => setActiveTab(t.id as any)} className={`px-6 py-3 rounded-xl ${activeTab===t.id? 'bg-gradient-to-r from-blue-500 to-purple-500 text-white':'text-gray-600'}`}>
                {t.label}
              </button>
            ))}
          </div>
        </div>

        {activeTab==='overview' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <div className="bg-white rounded-2xl shadow-lg p-6">
              <h3 className="text-xl font-bold mb-4">Skills Performance vs Industry</h3>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={barData}><CartesianGrid strokeDasharray="3 3" /><XAxis dataKey="name" /><YAxis /><Tooltip /><Bar dataKey="score" fill="#3B82F6" /><Bar dataKey="industry" fill="#94A3B8" /></BarChart>
                </ResponsiveContainer>
              </div>
            </div>
            <div className="bg-white rounded-2xl shadow-lg p-6">
              <h3 className="text-xl font-bold mb-4">Performance Distribution</h3>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart><Pie data={pieData} dataKey="value" cx="50%" cy="50%" outerRadius={80}>{pieData.map((p,i)=>(<Cell key={i} fill={p.color}/>))}</Pie><Tooltip/></PieChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        )}

        {activeTab==='skills' && (
          <div className="bg-white rounded-2xl shadow-lg p-6">
            <h3 className="text-xl font-bold mb-6">Detailed Skills Analysis</h3>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {result.skillScores.map((skill) => (
                <div key={skill.skill} className="p-6 border rounded-xl">
                  <div className="flex justify-between items-center mb-3">
                    <div className="font-semibold">{skill.skill}</div>
                    <div className="font-bold">{skill.score}</div>
                  </div>
                  <div className="text-sm text-gray-600 mb-2">Industry Avg: {skill.industryAverage}</div>
                  <div className="w-full bg-gray-200 rounded-full h-3"><div className="h-3 rounded-full bg-blue-500" style={{width:`${skill.score}%`}}/></div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab==='insights' && (
          <div className="space-y-6">
            <div className="bg-white rounded-2xl shadow-lg p-8">
              <h3 className="text-2xl font-bold mb-4">Key Strengths</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">{detailedInsights.strengths.map((s,i)=>(<div key={i} className="p-6 bg-green-50 rounded-xl"><h4 className="font-semibold">{s.title}</h4><p className="text-sm mt-2">{s.description}</p></div>))}</div>
            </div>
            {/* Per-question AI evaluations (if available) */}
            {result.perQuestionEvaluations && result.perQuestionEvaluations.length > 0 && (
              <div className="bg-white rounded-2xl shadow-lg p-8">
                <h3 className="text-2xl font-bold mb-4">Per-question AI Feedback</h3>
                <div className="space-y-6">
                  {result.perQuestionEvaluations.map((pq, idx) => (
                    <div key={idx} className="p-4 border rounded-lg">
                      <div className="font-semibold mb-2">Q: {((pq.question || {}) as any).question || ((pq.question || {}) as any).text || 'Question text not available'}</div>
                      <div className="text-sm text-gray-700 mb-2"><strong>Score:</strong> {pq.score ?? 'N/A'}</div>
                      {pq.model_answer && (
                        <div className="mb-2"><strong>Model answer:</strong>
                          <div className="mt-1 text-sm text-gray-600 whitespace-pre-line">{pq.model_answer}</div>
                        </div>
                      )}
                      {pq.strengths && pq.strengths.length > 0 && (
                        <div className="mb-2"><strong>Strengths:</strong>
                          <ul className="list-disc ml-6 text-sm text-gray-700">{pq.strengths.map((s:any,i:any)=>(<li key={i}>{s}</li>))}</ul>
                        </div>
                      )}
                      {pq.weaknesses && pq.weaknesses.length > 0 && (
                        <div className="mb-2"><strong>Weaknesses:</strong>
                          <ul className="list-disc ml-6 text-sm text-gray-700">{pq.weaknesses.map((w:any,i:any)=>(<li key={i}>{w}</li>))}</ul>
                        </div>
                      )}
                      {pq.feedback && (
                        <div className="mt-2 text-sm text-gray-800"><strong>Feedback:</strong>
                          <div className="mt-1 whitespace-pre-line">{pq.feedback}</div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab==='comparison' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <div className="bg-white rounded-2xl shadow-lg p-6">
              <h3 className="text-xl font-bold mb-4">Peer Comparison</h3>
              <div className="space-y-4">
                <div className="p-4 bg-gray-50 rounded-lg flex justify-between"><div>Regional</div><div>{result.peerComparison.region.percentile}%</div></div>
                <div className="p-4 bg-gray-50 rounded-lg flex justify-between"><div>Experience</div><div>{result.peerComparison.experience.percentile}%</div></div>
                <div className="p-4 bg-blue-50 rounded-lg flex justify-between"><div>Overall</div><div>{result.peerComparison.overall.percentile}%</div></div>
              </div>
            </div>
            <div className="bg-white rounded-2xl shadow-lg p-6">
              <h3 className="text-xl font-bold mb-4">Next Steps</h3>
              <div className="space-y-4">
                <button onClick={onRetakeInterview} className="w-full px-6 py-3 bg-gradient-to-r from-blue-500 to-purple-500 text-white rounded-xl">Retake Interview</button>
                <button className="w-full px-6 py-3 border rounded-xl">Download Detailed Report</button>
                <button className="w-full px-6 py-3 border rounded-xl">Share Results</button>
              </div>
            </div>
          </div>
        )}

      </div>
    </div>
  );
};

export default Dashboard;