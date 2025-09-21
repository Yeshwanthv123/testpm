import React, { useState } from 'react';
import { 
  User, Settings, Crown, Calendar, BarChart3, Trophy, 
  Clock, Target, Star, ChevronRight, Edit3, Lock, 
  CreditCard, Bell, Shield, Download, Share2, 
  Award, TrendingUp, Users, MapPin, Briefcase,
  Eye, EyeOff, Save, X, Check
} from 'lucide-react';

interface ProfileProps {
  onClose: () => void;
}

const Profile: React.FC<ProfileProps> = ({ onClose }) => {
  const [activeTab, setActiveTab] = useState<'overview' | 'settings' | 'billing' | 'history'>('overview');
  const [isEditingProfile, setIsEditingProfile] = useState(false);
  const [showPasswordChange, setShowPasswordChange] = useState(false);
  const [showCurrentPassword, setShowCurrentPassword] = useState(false);
  const [showNewPassword, setShowNewPassword] = useState(false);

  // Mock user data
  const [userProfile, setUserProfile] = useState({
    name: 'John Doe',
    email: 'john.doe@example.com',
    currentRole: 'Senior Product Manager',
    experience: '6-10',
    region: 'North America',
    targetCompanies: ['Google', 'Meta', 'Amazon'],
    joinDate: '2024-01-15',
    avatar: '👨‍💼'
  });

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

  // Mock interview history
  const recentInterviews = [
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
  ];

  const achievements = [
    { icon: '🏆', title: 'Interview Master', description: 'Completed 10+ interviews', unlocked: true },
    { icon: '⭐', title: 'High Performer', description: 'Scored 85+ average', unlocked: true },
    { icon: '🎯', title: 'Consistent Practicer', description: '7-day streak', unlocked: true },
    { icon: '🚀', title: 'Quick Learner', description: 'Improved by 20+ points', unlocked: false },
    { icon: '💎', title: 'Premium Member', description: 'Upgraded to Pro plan', unlocked: false }
  ];

  const handleProfileSave = () => {
    setIsEditingProfile(false);
    // In real app, would save to backend
  };

  const handlePasswordChange = () => {
    if (passwordData.newPassword !== passwordData.confirmPassword) {
      alert('Passwords do not match');
      return;
    }
    // In real app, would validate and update password
    setShowPasswordChange(false);
    setPasswordData({ currentPassword: '', newPassword: '', confirmPassword: '' });
    alert('Password updated successfully');
  };

  const getScoreColor = (score: number) => {
    if (score >= 85) return 'text-green-600 bg-green-100';
    if (score >= 70) return 'text-blue-600 bg-blue-100';
    if (score >= 60) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

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
          <div className="w-64 bg-gray-50 border-r border-gray-200 p-6">
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
                      <span className="text-2xl font-bold text-blue-900">15</span>
                    </div>
                    <div className="text-blue-800 font-medium">Interviews Completed</div>
                  </div>
                  
                  <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-2xl p-6 border border-green-200">
                    <div className="flex items-center justify-between mb-4">
                      <Star className="w-8 h-8 text-green-600" />
                      <span className="text-2xl font-bold text-green-900">85</span>
                    </div>
                    <div className="text-green-800 font-medium">Average Score</div>
                  </div>
                  
                  <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-2xl p-6 border border-purple-200">
                    <div className="flex items-center justify-between mb-4">
                      <TrendingUp className="w-8 h-8 text-purple-600" />
                      <span className="text-2xl font-bold text-purple-900">78%</span>
                    </div>
                    <div className="text-purple-800 font-medium">Improvement Rate</div>
                  </div>
                  
                  <div className="bg-gradient-to-br from-yellow-50 to-yellow-100 rounded-2xl p-6 border border-yellow-200">
                    <div className="flex items-center justify-between mb-4">
                      <Users className="w-8 h-8 text-yellow-600" />
                      <span className="text-2xl font-bold text-yellow-900">92nd</span>
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

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Current Role</label>
                      {isEditingProfile ? (
                        <input
                          type="text"
                          value={userProfile.currentRole}
                          onChange={(e) => setUserProfile(prev => ({ ...prev, currentRole: e.target.value }))}
                          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                        />
                      ) : (
                        <div className="px-4 py-3 bg-gray-50 rounded-lg text-gray-900">{userProfile.currentRole}</div>
                      )}
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Experience Level</label>
                      {isEditingProfile ? (
                        <select
                          value={userProfile.experience}
                          onChange={(e) => setUserProfile(prev => ({ ...prev, experience: e.target.value }))}
                          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                        >
                          <option value="0-2">0-2 years</option>
                          <option value="3-5">3-5 years</option>
                          <option value="6-10">6-10 years</option>
                          <option value="10+">10+ years</option>
                        </select>
                      ) : (
                        <div className="px-4 py-3 bg-gray-50 rounded-lg text-gray-900">{userProfile.experience} years</div>
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
                        className="flex items-center space-x-2 px-6 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600 transition-colors"
                      >
                        <Save className="w-4 h-4" />
                        <span>Save Changes</span>
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
                    <select className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent">
                      <option>All Companies</option>
                      <option>Google</option>
                      <option>Meta</option>
                      <option>Amazon</option>
                    </select>
                    <select className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent">
                      <option>All Types</option>
                      <option>Behavioral</option>
                      <option>Product Strategy</option>
                      <option>Technical</option>
                    </select>
                    <select className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent">
                      <option>Last 30 days</option>
                      <option>Last 3 months</option>
                      <option>Last 6 months</option>
                      <option>All time</option>
                    </select>
                    <button className="px-4 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600 transition-colors">
                      Apply Filters
                    </button>
                  </div>
                </div>

                {/* Interview List */}
                <div className="bg-white rounded-2xl shadow-lg border border-gray-200">
                  <div className="p-6 border-b border-gray-200">
                    <h3 className="text-xl font-bold text-gray-900">All Interviews</h3>
                  </div>
                  <div className="divide-y divide-gray-200">
                    {recentInterviews.map((interview) => (
                      <div key={interview.id} className="p-6 hover:bg-gray-50 transition-colors">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-4">
                            <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center text-white font-bold">
                              {interview.company.charAt(0)}
                            </div>
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
                            <button className="flex items-center space-x-1 text-orange-600 hover:text-orange-700 font-medium">
                              <span>View Details</span>
                              <ChevronRight className="w-4 h-4" />
                            </button>
                          </div>
                        </div>
                      </div>
                    ))}
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