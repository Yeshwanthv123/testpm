import React, { useState, useEffect } from 'react';
import { 
  User, Settings, Crown, Calendar, BarChart3, Trophy, 
  Clock, Target, Star, ChevronRight, Edit3, Lock, 
  CreditCard, Bell, Shield, Download, Share2, 
  Award, TrendingUp, Users, MapPin, Briefcase,
  Eye, EyeOff, Save, X, Check, LogOut
} from 'lucide-react';
import { fetchInterviewMetrics } from '../utils/api';

interface ProfileProps {
  onClose: () => void;
  user?: any;
  onUpdateUser?: (u: any) => void;
  onLogout?: () => void;
  onStartInterview?: (t: any, q: any[], jd?: string) => void;
  onViewResult?: (past: any) => void;
}

// Company logo URLs
const COMPANY_LOGOS: Record<string, string> = {
  'Google': 'https://www.google.com/favicon.ico',
  'Meta': 'https://www.facebook.com/favicon.ico',
  'Amazon': 'https://www.amazon.com/favicon.ico',
  'Apple': 'https://www.apple.com/favicon.ico',
  'Microsoft': 'https://www.microsoft.com/favicon.ico',
  'Netflix': 'https://www.netflix.com/favicon.ico',
  'Tesla': 'https://www.tesla.com/favicon.ico',
  'Twitter': 'https://www.twitter.com/favicon.ico',
  'LinkedIn': 'https://www.linkedin.com/favicon.ico',
  'Uber': 'https://www.uber.com/favicon.ico',
};

const getCompanyLogo = (company: string): string => {
  return COMPANY_LOGOS[company] || 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzIiIGhlaWdodD0iMzIiIHZpZXdCb3g9IjAgMCAzMiAzMiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMzIiIGhlaWdodD0iMzIiIHJ4PSI4IiBmaWxsPSIjNjU2NUY1Ii8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnRTaXplPSIxNiIgZm9udFdlaWdodD0iYm9sZCIgZmlsbD0id2hpdGUiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGR5PSIuM2VtIj5DPC90ZXh0Pjwvc3ZnPg==';
};

const Profile: React.FC<ProfileProps> = ({ onClose, onViewResult }) => {
  const [activeTab, setActiveTab] = useState<'overview' | 'settings' | 'billing' | 'history'>('overview');
  const [isEditingProfile, setIsEditingProfile] = useState(false);
  const [showPasswordChange, setShowPasswordChange] = useState(false);
  const [showCurrentPassword, setShowCurrentPassword] = useState(false);
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);

  // Filter state
  const [filters, setFilters] = useState({
    company: 'all',
    type: 'all',
    dateRange: 'all'
  });

  const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

  // Backend user data
  const [userProfile, setUserProfile] = useState({
    name: 'Loading...',
    email: '',
    currentRole: 'Product Manager',
    experience: '0-2',
    region: '',
    targetCompanies: [] as string[],
    joinDate: new Date().toISOString(),
    avatar: '👨‍💼'
  });

  // Backend metrics data
  const [metrics, setMetrics] = useState<any>(null);

  const displayImprovement = metrics?.improvementRate != null ? Math.round(Math.max(Math.min(metrics.improvementRate, 100), -100)) : 0;

  const [passwordData, setPasswordData] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  });

  const [notifications, setNotifications] = useState({
    emailUpdates: true,
    practiceReminders: true,
    performanceReports: false,
    newFeatures: true
  });

  // Backend interview history
  const [recentInterviews, setRecentInterviews] = useState<any[]>([
    {
      id: '1',
      company: 'Google',
      type: 'Product Strategy',
      date: '2024-01-20',
      score: 85,
      duration: 45,
      status: 'completed'
    },
    {
      id: '2',
      company: 'Meta',
      type: 'Behavioral',
      date: '2024-01-18',
      score: 78,
      duration: 40,
      status: 'completed'
    },
    {
      id: '3',
      company: 'Amazon',
      type: 'Leadership',
      date: '2024-01-15',
      score: 92,
      duration: 50,
      status: 'completed'
    }
  ]);

  // Dynamically calculate achievements based on metrics
  const achievements = [
    { 
      icon: '🏆', 
      title: 'Interview Master', 
      description: 'Completed 10+ interviews', 
      unlocked: (metrics?.completed || 0) >= 10 
    },
    { 
      icon: '⭐', 
      title: 'High Performer', 
      description: 'Scored 85+ average', 
      unlocked: (metrics?.avgScore || 0) >= 85 
    },
    { 
      icon: '🎯', 
      title: 'Consistent Practicer', 
      description: '7-day streak', 
      unlocked: (metrics?.achievements || []).some((a: any) => a.id === 'consistent_practicer') 
    },
    { 
      icon: '🚀', 
      title: 'Quick Learner', 
      description: 'Improved by 20+ points', 
      unlocked: (metrics?.improvementRate || 0) >= 20 
    },
    { 
      icon: '💎', 
      title: 'Premium Member', 
      description: 'Upgraded to Pro plan', 
      unlocked: (metrics?.achievements || []).some((a: any) => a.id === 'premium_member') 
    }
  ];

  // Load user data from backend on mount
  useEffect(() => {
    const loadUserData = async () => {
      const token = localStorage.getItem('access_token');
      if (!token) {
        setIsLoading(false);
        return;
      }

      try {
        // Fetch user profile
        const userResponse = await fetch(`${API_BASE}/auth/me`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        
        if (userResponse.ok) {
          const userData = await userResponse.json();
          setUserProfile({
            name: userData.full_name || 'User',
            email: userData.email || '',
            currentRole: userData.currentRole || 'Product Manager',
            experience: userData.experience || '0-2',
            region: userData.region || '',
            targetCompanies: userData.targetCompanies || [],
            joinDate: userData.joinDate || new Date().toISOString(),
            avatar: '👨‍💼'
          });
        }

        // Fetch metrics
        try {
          const metricsData = await fetchInterviewMetrics();
          setMetrics(metricsData);
          
          // Update recent interviews from metrics if available
          if (metricsData.recentInterviews && Array.isArray(metricsData.recentInterviews)) {
            setRecentInterviews(metricsData.recentInterviews.slice(0, 3));
          }
        } catch (err) {
          console.log('Metrics not available, using defaults');
        }
      } catch (err) {
        console.error('Failed to load user data:', err);
      } finally {
        setIsLoading(false);
      }
    };

    loadUserData();
  }, [API_BASE]);

  const handleProfileSave = async () => {
    const token = localStorage.getItem('access_token');
    if (!token) return;

    setIsSaving(true);
    try {
      const response = await fetch(`${API_BASE}/auth/me`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          full_name: userProfile.name,
          email: userProfile.email,
          currentRole: userProfile.currentRole,
          experience: userProfile.experience,
          region: userProfile.region,
          targetCompanies: userProfile.targetCompanies
        })
      });

      if (!response.ok) throw new Error('Failed to update profile');
      
      await response.json();
      setIsEditingProfile(false);
      alert('Profile updated successfully!');
    } catch (err) {
      console.error('Error saving profile:', err);
      alert('Failed to save profile');
    } finally {
      setIsSaving(false);
    }
  };

  const handlePasswordChange = async () => {
    if (passwordData.newPassword !== passwordData.confirmPassword) {
      alert('Passwords do not match');
      return;
    }

    const token = localStorage.getItem('access_token');
    if (!token) return;

    try {
      const response = await fetch(`${API_BASE}/auth/change-password`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          currentPassword: passwordData.currentPassword,
          newPassword: passwordData.newPassword
        })
      });

      if (!response.ok) throw new Error('Failed to change password');
      
      setShowPasswordChange(false);
      setPasswordData({ currentPassword: '', newPassword: '', confirmPassword: '' });
      alert('Password updated successfully!');
    } catch (err) {
      console.error('Error changing password:', err);
      alert('Failed to change password');
    }
  };

  const handleViewResult = (interviewId: string) => {
    try {
      const interview = recentInterviews.find((it) => String(it.id) === String(interviewId));
      if (!interview) {
        alert('Interview not found');
        return;
      }

      if (typeof onViewResult === 'function') {
        onViewResult(interview);
        onClose();
        return;
      }

      // Fallback: store the interview details in sessionStorage and navigate to results
      try {
        sessionStorage.setItem('pmbot_result', JSON.stringify(interview));
      } catch {}
      onClose();
      window.location.hash = '#results';
    } catch (err) {
      console.error('Error showing result:', err);
      alert('Failed to show interview result');
    }
  };

  const handleLogout = () => {
    try {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
    } catch {}
    onClose();
  };

  const getScoreColor = (score: number) => {
    if (score >= 85) return 'text-green-600 bg-green-100';
    if (score >= 70) return 'text-blue-600 bg-blue-100';
    if (score >= 60) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  // Filter interviews based on applied filters
  const getFilteredInterviews = () => {
    return recentInterviews.filter((interview) => {
      // Company filter
      if (filters.company !== 'all' && interview.company !== filters.company) {
        return false;
      }
      
      // Type filter
      if (filters.type !== 'all' && interview.type !== filters.type) {
        return false;
      }
      
      // Date range filter
      if (filters.dateRange !== 'all') {
        const interviewDate = new Date(interview.date);
        const now = new Date();
        const daysAgo = parseInt(filters.dateRange);
        const cutoffDate = new Date(now.getTime() - daysAgo * 24 * 60 * 60 * 1000);
        
        if (interviewDate < cutoffDate) {
          return false;
        }
      }
      
      return true;
    });
  };

  if (isLoading) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
        <div className="bg-white rounded-3xl shadow-2xl p-8 text-center">
          <div className="w-12 h-12 border-4 border-orange-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600">Loading profile...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-3xl shadow-2xl w-full max-w-6xl max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-yellow-500 to-orange-500 p-6 text-white">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="w-16 h-16 bg-white bg-opacity-20 rounded-full flex items-center justify-center text-2xl">
                {userProfile.avatar}
              </div>
              <div>
                <h1 className="text-2xl font-bold">{userProfile.name}</h1>
                <p className="text-yellow-100">{userProfile.currentRole}</p>
                <div className="flex items-center space-x-2 mt-1">
                  <Crown className="w-4 h-4" />
                  <span className="text-sm">Pro Member since {new Date(userProfile.joinDate).toLocaleDateString()}</span>
                </div>
              </div>
            </div>
            <button
              onClick={onClose}
              className="p-2 hover:bg-white hover:bg-opacity-20 rounded-lg transition-colors"
            >
              <X className="w-6 h-6" />
            </button>
          </div>
        </div>

        <div className="flex h-[calc(90vh-120px)]">
          {/* Sidebar */}
          <div className="w-64 bg-gray-50 border-r border-gray-200 p-6 flex flex-col justify-between">
            <nav className="space-y-2">
              {[
                { id: 'overview', label: 'Overview', icon: BarChart3 },
                { id: 'settings', label: 'Account Settings', icon: Settings },
                { id: 'billing', label: 'Billing & Plans', icon: CreditCard },
                { id: 'history', label: 'Interview History', icon: Clock }
              ].map((tab) => {
                const Icon = tab.icon;
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id as any)}
                    className={`w-full flex items-center space-x-3 px-4 py-3 rounded-xl transition-all ${
                      activeTab === tab.id
                        ? 'bg-orange-100 text-orange-700 font-medium'
                        : 'text-gray-600 hover:bg-gray-100'
                    }`}
                  >
                    <Icon className="w-5 h-5" />
                    <span>{tab.label}</span>
                  </button>
                );
              })}
            </nav>

            {/* Log Out button */}
            <div className="pt-4 border-t border-gray-200">
              <button
                onClick={handleLogout}
                className="flex items-center space-x-3 w-full px-4 py-3 text-red-600 hover:text-white
                           hover:bg-gradient-to-r hover:from-orange-500 hover:to-red-500 rounded-xl
                           font-semibold transition-all"
              >
                <LogOut className="w-5 h-5" />
                <span>Log Out</span>
              </button>
            </div>
          </div>

          {/* Main Content */}
          <div className="flex-1 overflow-y-auto">
            {/* Overview Tab */}
            {activeTab === 'overview' && (
              <div className="p-8">
                <h2 className="text-2xl font-bold text-gray-900 mb-8">Profile Overview</h2>
                
                {/* Stats Cards */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                  <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-2xl p-6 border border-blue-200">
                    <div className="flex items-center justify-between mb-4">
                      <Trophy className="w-8 h-8 text-blue-600" />
                      <span className="text-2xl font-bold text-blue-900">{metrics?.completed || 0}</span>
                    </div>
                    <div className="text-blue-800 font-medium">Interviews Completed</div>
                  </div>
                  
                  <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-2xl p-6 border border-green-200">
                    <div className="flex items-center justify-between mb-4">
                      <Star className="w-8 h-8 text-green-600" />
                      <span className="text-2xl font-bold text-green-900">{metrics?.avgScore ? Math.round(metrics.avgScore) : 0}</span>
                    </div>
                    <div className="text-green-800 font-medium">Average Score</div>
                  </div>
                  
                  <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-2xl p-6 border border-purple-200">
                    <div className="flex items-center justify-between mb-4">
                      <TrendingUp className="w-8 h-8 text-purple-600" />
                      <span className="text-2xl font-bold text-purple-900">{displayImprovement}%</span>
                    </div>
                    <div className="text-purple-800 font-medium">Improvement Rate</div>
                  </div>
                  
                  <div className="bg-gradient-to-br from-yellow-50 to-yellow-100 rounded-2xl p-6 border border-yellow-200">
                    <div className="flex items-center justify-between mb-4">
                      <Users className="w-8 h-8 text-yellow-600" />
                      <span className="text-2xl font-bold text-yellow-900">{metrics?.percentileRank || 0}%</span>
                    </div>
                    <div className="text-yellow-800 font-medium">Percentile Rank</div>
                  </div>
                </div>

                {/* Recent Activity */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                  <div className="bg-white rounded-2xl shadow-lg p-6 border border-gray-200">
                    <h3 className="text-xl font-bold text-gray-900 mb-6">Recent Interviews</h3>
                    <div className="space-y-4">
                      {recentInterviews.slice(0, 3).map((interview) => (
                        <div key={interview.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-xl">
                          <div>
                            <div className="font-medium text-gray-900">{interview.company}</div>
                            <div className="text-sm text-gray-600">{interview.type} • {interview.duration} min</div>
                            <div className="text-xs text-gray-500">{new Date(interview.date).toLocaleDateString()}</div>
                          </div>
                          <div className={`px-3 py-1 rounded-full text-sm font-medium ${getScoreColor(interview.score)}`}>
                            {interview.score}
                          </div>
                        </div>
                      ))}
                    </div>
                    <button className="w-full mt-4 text-orange-600 hover:text-orange-700 font-medium text-sm flex items-center justify-center space-x-1">
                      <span>View All Interviews</span>
                      <ChevronRight className="w-4 h-4" />
                    </button>
                  </div>

                  <div className="bg-white rounded-2xl shadow-lg p-6 border border-gray-200">
                    <h3 className="text-xl font-bold text-gray-900 mb-6">Achievements</h3>
                    <div className="space-y-3">
                      {achievements.map((achievement, index) => (
                        <div key={index} className={`flex items-center space-x-3 p-3 rounded-xl ${
                          achievement.unlocked ? 'bg-green-50 border border-green-200' : 'bg-gray-50 border border-gray-200'
                        }`}>
                          <div className="text-2xl">{achievement.icon}</div>
                          <div className="flex-1">
                            <div className={`font-medium ${achievement.unlocked ? 'text-green-900' : 'text-gray-500'}`}>
                              {achievement.title}
                            </div>
                            <div className={`text-sm ${achievement.unlocked ? 'text-green-700' : 'text-gray-400'}`}>
                              {achievement.description}
                            </div>
                          </div>
                          {achievement.unlocked && (
                            <Check className="w-5 h-5 text-green-600" />
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Settings Tab */}
            {activeTab === 'settings' && (
              <div className="p-8">
                <h2 className="text-2xl font-bold text-gray-900 mb-8">Account Settings</h2>
                
                {/* Profile Information */}
                <div className="bg-white rounded-2xl shadow-lg p-6 border border-gray-200 mb-8">
                  <div className="flex items-center justify-between mb-6">
                    <h3 className="text-xl font-bold text-gray-900">Profile Information</h3>
                    <button
                      onClick={() => setIsEditingProfile(!isEditingProfile)}
                      className="flex items-center space-x-2 px-4 py-2 text-orange-600 hover:bg-orange-50 rounded-lg transition-colors"
                    >
                      <Edit3 className="w-4 h-4" />
                      <span>{isEditingProfile ? 'Cancel' : 'Edit'}</span>
                    </button>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Full Name</label>
                      {isEditingProfile ? (
                        <input
                          type="text"
                          value={userProfile.name}
                          onChange={(e) => setUserProfile(prev => ({ ...prev, name: e.target.value }))}
                          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                        />
                      ) : (
                        <div className="px-4 py-3 bg-gray-50 rounded-lg text-gray-900">{userProfile.name}</div>
                      )}
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Email</label>
                      {isEditingProfile ? (
                        <input
                          type="email"
                          value={userProfile.email}
                          onChange={(e) => setUserProfile(prev => ({ ...prev, email: e.target.value }))}
                          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                        />
                      ) : (
                        <div className="px-4 py-3 bg-gray-50 rounded-lg text-gray-900">{userProfile.email}</div>
                      )}
                    </div>
                  </div>

                  {isEditingProfile && (
                    <div className="flex justify-end space-x-3 mt-6">
                      <button
                        onClick={() => setIsEditingProfile(false)}
                        className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                      >
                        Cancel
                      </button>
                      <button
                        onClick={handleProfileSave}
                        disabled={isSaving}
                        className="flex items-center space-x-2 px-6 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600 transition-colors disabled:opacity-50"
                      >
                        <Save className="w-4 h-4" />
                        <span>{isSaving ? 'Saving...' : 'Save Changes'}</span>
                      </button>
                    </div>
                  )}
                </div>

                {/* Password Change */}
                <div className="bg-white rounded-2xl shadow-lg p-6 border border-gray-200 mb-8">
                  <div className="flex items-center justify-between mb-6">
                    <h3 className="text-xl font-bold text-gray-900">Password & Security</h3>
                    <button
                      onClick={() => setShowPasswordChange(!showPasswordChange)}
                      className="flex items-center space-x-2 px-4 py-2 text-orange-600 hover:bg-orange-50 rounded-lg transition-colors"
                    >
                      <Lock className="w-4 h-4" />
                      <span>Change Password</span>
                    </button>
                  </div>

                  {showPasswordChange && (
                    <div className="space-y-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">Current Password</label>
                        <div className="relative">
                          <input
                            type={showCurrentPassword ? 'text' : 'password'}
                            value={passwordData.currentPassword}
                            onChange={(e) => setPasswordData(prev => ({ ...prev, currentPassword: e.target.value }))}
                            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent pr-12"
                          />
                          <button
                            type="button"
                            onClick={() => setShowCurrentPassword(!showCurrentPassword)}
                            className="absolute right-3 top-3 text-gray-400 hover:text-gray-600"
                          >
                            {showCurrentPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                          </button>
                        </div>
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">New Password</label>
                        <div className="relative">
                          <input
                            type={showNewPassword ? 'text' : 'password'}
                            value={passwordData.newPassword}
                            onChange={(e) => setPasswordData(prev => ({ ...prev, newPassword: e.target.value }))}
                            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent pr-12"
                          />
                          <button
                            type="button"
                            onClick={() => setShowNewPassword(!showNewPassword)}
                            className="absolute right-3 top-3 text-gray-400 hover:text-gray-600"
                          >
                            {showNewPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                          </button>
                        </div>
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">Confirm New Password</label>
                        <input
                          type="password"
                          value={passwordData.confirmPassword}
                          onChange={(e) => setPasswordData(prev => ({ ...prev, confirmPassword: e.target.value }))}
                          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                        />
                      </div>

                      <div className="flex justify-end space-x-3">
                        <button
                          onClick={() => setShowPasswordChange(false)}
                          className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                        >
                          Cancel
                        </button>
                        <button
                          onClick={handlePasswordChange}
                          className="px-6 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600 transition-colors"
                        >
                          Update Password
                        </button>
                      </div>
                    </div>
                  )}
                </div>

                {/* Notifications */}
                <div className="bg-white rounded-2xl shadow-lg p-6 border border-gray-200">
                  <h3 className="text-xl font-bold text-gray-900 mb-6">Notification Preferences</h3>
                  <div className="space-y-4">
                    {Object.entries(notifications).map(([key, value]) => (
                      <div key={key} className="flex items-center justify-between p-4 bg-gray-50 rounded-xl">
                        <div>
                          <div className="font-medium text-gray-900">
                            {key === 'emailUpdates' && 'Email Updates'}
                            {key === 'practiceReminders' && 'Practice Reminders'}
                            {key === 'performanceReports' && 'Performance Reports'}
                            {key === 'newFeatures' && 'New Features'}
                          </div>
                          <div className="text-sm text-gray-600">
                            {key === 'emailUpdates' && 'Receive updates about your account and interviews'}
                            {key === 'practiceReminders' && 'Get reminded to practice regularly'}
                            {key === 'performanceReports' && 'Weekly performance summaries'}
                            {key === 'newFeatures' && 'Be notified about new features and improvements'}
                          </div>
                        </div>
                        <label className="relative inline-flex items-center cursor-pointer">
                          <input
                            type="checkbox"
                            checked={value}
                            onChange={(e) => setNotifications(prev => ({ ...prev, [key]: e.target.checked }))}
                            className="sr-only peer"
                          />
                          <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-orange-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-orange-500"></div>
                        </label>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Billing Tab */}
            {activeTab === 'billing' && (
              <div className="p-8">
                <h2 className="text-2xl font-bold text-gray-900 mb-8">Billing & Plans</h2>
                
                {/* Current Plan */}
                <div className="bg-gradient-to-r from-orange-500 to-yellow-500 rounded-2xl p-8 text-white mb-8">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-2xl font-bold mb-2">Pro Plan</h3>
                      <p className="text-orange-100 mb-4">Unlimited interviews, detailed analytics, and priority support</p>
                      <div className="flex items-center space-x-4">
                        <span className="text-3xl font-bold">$29</span>
                        <span className="text-orange-100">/month</span>
                      </div>
                    </div>
                    <Crown className="w-16 h-16 text-yellow-200" />
                  </div>
                </div>

                {/* Plan Comparison */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                  <div className="bg-white rounded-2xl shadow-lg p-6 border border-gray-200">
                    <h4 className="text-lg font-bold text-gray-900 mb-4">Free Plan</h4>
                    <div className="text-3xl font-bold text-gray-900 mb-4">$0</div>
                    <ul className="space-y-2 text-sm text-gray-600 mb-6">
                      <li>• 3 interviews per month</li>
                      <li>• Basic feedback</li>
                      <li>• Limited analytics</li>
                      <li>• Community support</li>
                    </ul>
                    <button className="w-full py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors">
                      Current Plan
                    </button>
                  </div>

                  <div className="bg-white rounded-2xl shadow-lg p-6 border-2 border-orange-500 relative">
                    <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
                      <span className="bg-orange-500 text-white px-4 py-1 rounded-full text-sm font-medium">Current</span>
                    </div>
                    <h4 className="text-lg font-bold text-gray-900 mb-4">Pro Plan</h4>
                    <div className="text-3xl font-bold text-gray-900 mb-4">$29</div>
                    <ul className="space-y-2 text-sm text-gray-600 mb-6">
                      <li>• Unlimited interviews</li>
                      <li>• Detailed AI feedback</li>
                      <li>• Advanced analytics</li>
                      <li>• Priority support</li>
                      <li>• Custom JD questions</li>
                    </ul>
                    <button className="w-full py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600 transition-colors">
                      Manage Plan
                    </button>
                  </div>

                  <div className="bg-white rounded-2xl shadow-lg p-6 border border-gray-200">
                    <h4 className="text-lg font-bold text-gray-900 mb-4">Enterprise</h4>
                    <div className="text-3xl font-bold text-gray-900 mb-4">$99</div>
                    <ul className="space-y-2 text-sm text-gray-600 mb-6">
                      <li>• Everything in Pro</li>
                      <li>• Team management</li>
                      <li>• Custom branding</li>
                      <li>• Dedicated support</li>
                      <li>• API access</li>
                    </ul>
                    <button className="w-full py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors">
                      Upgrade
                    </button>
                  </div>
                </div>

                {/* Billing History */}
                <div className="bg-white rounded-2xl shadow-lg p-6 border border-gray-200">
                  <h3 className="text-xl font-bold text-gray-900 mb-6">Billing History</h3>
                  <div className="space-y-4">
                    {[
                      { date: '2024-01-01', amount: '$29.00', status: 'Paid', invoice: 'INV-001' },
                      { date: '2023-12-01', amount: '$29.00', status: 'Paid', invoice: 'INV-002' },
                      { date: '2023-11-01', amount: '$29.00', status: 'Paid', invoice: 'INV-003' }
                    ].map((bill, index) => (
                      <div key={index} className="flex items-center justify-between p-4 bg-gray-50 rounded-xl">
                        <div>
                          <div className="font-medium text-gray-900">{bill.invoice}</div>
                          <div className="text-sm text-gray-600">{new Date(bill.date).toLocaleDateString()}</div>
                        </div>
                        <div className="flex items-center space-x-4">
                          <span className="font-medium text-gray-900">{bill.amount}</span>
                          <span className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm font-medium">
                            {bill.status}
                          </span>
                          <button className="text-orange-600 hover:text-orange-700 text-sm font-medium">
                            Download
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* History Tab */}
            {activeTab === 'history' && (
              <div className="p-8">
                <h2 className="text-2xl font-bold text-gray-900 mb-8">Interview History</h2>
                
                {/* Filters */}
                <div className="bg-white rounded-2xl shadow-lg p-6 border border-gray-200 mb-8">
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <select 
                      value={filters.company}
                      onChange={(e) => setFilters({ ...filters, company: e.target.value })}
                      className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                    >
                      <option value="all">All Companies</option>
                      <option value="Google">Google</option>
                      <option value="Meta">Meta</option>
                      <option value="Amazon">Amazon</option>
                    </select>
                    <select 
                      value={filters.type}
                      onChange={(e) => setFilters({ ...filters, type: e.target.value })}
                      className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                    >
                      <option value="all">All Types</option>
                      <option value="Behavioral">Behavioral</option>
                      <option value="Product Strategy">Product Strategy</option>
                      <option value="Leadership">Leadership</option>
                    </select>
                    <select 
                      value={filters.dateRange}
                      onChange={(e) => setFilters({ ...filters, dateRange: e.target.value })}
                      className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                    >
                      <option value="all">All time</option>
                      <option value="30">Last 30 days</option>
                      <option value="90">Last 3 months</option>
                      <option value="180">Last 6 months</option>
                    </select>
                    <button 
                      onClick={() => {
                        // Filters are applied automatically below
                        console.log('Filters applied:', filters);
                      }}
                      className="px-4 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600 transition-colors font-medium"
                    >
                      Apply Filters
                    </button>
                  </div>
                </div>

                {/* Interview List */}
                <div className="bg-white rounded-2xl shadow-lg border border-gray-200">
                  <div className="p-6 border-b border-gray-200">
                    <h3 className="text-xl font-bold text-gray-900">All Interviews ({getFilteredInterviews().length})</h3>
                  </div>
                  <div className="divide-y divide-gray-200">
                    {getFilteredInterviews().length > 0 ? (
                      getFilteredInterviews().map((interview) => (
                      <div key={interview.id} className="p-6 hover:bg-gray-50 transition-colors">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-4">
                            <img 
                              src={getCompanyLogo(interview.company)} 
                              alt={interview.company}
                              className="w-12 h-12 rounded-xl object-cover bg-gray-100"
                              onError={(e) => {
                                (e.target as HTMLImageElement).src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzIiIGhlaWdodD0iMzIiIHZpZXdCb3g9IjAgMCAzMiAzMiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMzIiIGhlaWdodD0iMzIiIHJ4PSI4IiBmaWxsPSIjNjU2NUY1Ii8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnRTaXplPSIxNiIgZm9udFdlaWdodD0iYm9sZCIgZmlsbD0id2hpdGUiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGR5PSIuM2VtIj5DPC90ZXh0Pjwvc3ZnPg==';
                              }}
                            />
                            <div>
                              <div className="font-medium text-gray-900">{interview.company} Interview</div>
                              <div className="text-sm text-gray-600">{interview.type}</div>
                              <div className="text-xs text-gray-500">
                                {new Date(interview.date).toLocaleDateString()} • {interview.duration} minutes
                              </div>
                            </div>
                          </div>
                          <div className="flex items-center space-x-4">
                            <div className={`px-4 py-2 rounded-full text-sm font-medium ${getScoreColor(interview.score)}`}>
                              Score: {interview.score}
                            </div>
                            <button onClick={() => handleViewResult(interview.id)} className="flex items-center space-x-1 text-orange-600 hover:text-orange-700 font-medium">
                              <span>View Result</span>
                              <ChevronRight className="w-4 h-4" />
                            </button>
                          </div>
                        </div>
                      </div>
                      ))
                    ) : (
                      <div className="p-8 text-center text-gray-500">
                        <p className="text-lg">No interviews found matching the filters</p>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Profile;