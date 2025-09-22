import React, { useState, useEffect } from 'react';
import {
  User, Settings, Crown, Calendar, BarChart3, Trophy,
  Clock, Target, Star, ChevronRight, Edit3, Lock,
  CreditCard, Bell, Shield, Download, Share2,
  Award, TrendingUp, Users, MapPin, Briefcase,
  Eye, EyeOff, Save, X, Check
} from 'lucide-react';
import { User as UserType } from '../types';

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

interface ProfileProps {
  user: UserType;
  onUpdateUser: (user: UserType) => void;
  onClose: () => void;
}

const Profile: React.FC<ProfileProps> = ({ user, onUpdateUser, onClose }) => {
  const [activeTab, setActiveTab] = useState<'overview' | 'settings' | 'billing' | 'history'>('overview');
  const [isEditingProfile, setIsEditingProfile] = useState(false);
  const [showPasswordChange, setShowPasswordChange] = useState(false);
  const [showCurrentPassword, setShowCurrentPassword] = useState(false);
  const [showNewPassword, setShowNewPassword] = useState(false);

  // Use state derived from props for the form
  const [userProfile, setUserProfile] = useState({
    full_name: user.full_name || '',
    email: user.email || '',
    currentRole: user.currentRole || 'Not Set',
    experience: user.experience || '0-2',
    region: user.region || 'Not Set',
    avatar: '👨‍💼', // This can remain a frontend-only mock for now
    joinDate: '2024-01-15' // This can be replaced with real data if available
  });

  // Update state if the user prop changes
  useEffect(() => {
    setUserProfile({
        full_name: user.full_name || '',
        email: user.email || '',
        currentRole: user.currentRole || 'Not Set',
        experience: user.experience || '0-2',
        region: user.region || 'Not Set',
        avatar: '👨‍💼',
        joinDate: '2024-01-15'
    });
  }, [user]);


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
  
  const handleProfileSave = async () => {
    const token = localStorage.getItem('accessToken');
    if (!token) {
        alert("You are not logged in.");
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/auth/me`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                full_name: userProfile.full_name,
                email: userProfile.email,
                currentRole: userProfile.currentRole,
                experience: userProfile.experience,
                region: userProfile.region,
            }),
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || "Failed to update profile");
        }

        const updatedUserData = await response.json();
        onUpdateUser(updatedUserData); // Update the state in App.tsx
        setIsEditingProfile(false);
        alert('Profile updated successfully!');

    } catch (error: any) {
        alert(`Error: ${error.message}`);
    }
  };


  const handlePasswordChange = () => {
    if (passwordData.newPassword !== passwordData.confirmPassword) {
      alert('Passwords do not match');
      return;
    }
    // In a real app, you would have an endpoint to change the password
    console.log("Password change requested", passwordData);
    setShowPasswordChange(false);
    setPasswordData({ currentPassword: '', newPassword: '', confirmPassword: '' });
    alert('Password updated successfully (mocked)');
  };


  // Mock interview history
  const recentInterviews = [
    { id: '1', company: 'Google', type: 'Product Strategy', date: '2024-01-20', score: 85, duration: 45, status: 'completed' },
    { id: '2', company: 'Meta', type: 'Behavioral', date: '2024-01-18', score: 78, duration: 40, status: 'completed' },
    { id: '3', company: 'Amazon', type: 'Leadership', date: '2024-01-15', score: 92, duration: 50, status: 'completed' }
  ];

  const achievements = [
    { icon: '🏆', title: 'Interview Master', description: 'Completed 10+ interviews', unlocked: true },
    { icon: '⭐', title: 'High Performer', description: 'Scored 85+ average', unlocked: true },
    { icon: '🎯', title: 'Consistent Practicer', description: '7-day streak', unlocked: true },
    { icon: '🚀', title: 'Quick Learner', description: 'Improved by 20+ points', unlocked: false },
    { icon: '💎', title: 'Premium Member', description: 'Upgraded to Pro plan', unlocked: false }
  ];

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
                <h1 className="text-2xl font-bold">{userProfile.full_name}</h1>
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
             {activeTab === 'settings' && (
              <div className="p-8">
                <h2 className="text-2xl font-bold text-gray-900 mb-8">Account Settings</h2>
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
                          value={userProfile.full_name}
                          onChange={(e) => setUserProfile(prev => ({ ...prev, full_name: e.target.value }))}
                          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                        />
                      ) : (
                        <div className="px-4 py-3 bg-gray-50 rounded-lg text-gray-900">{userProfile.full_name}</div>
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
                        className="flex items-center space-x-2 px-6 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600 transition-colors"
                      >
                        <Save className="w-4 h-4" />
                        <span>Save Changes</span>
                      </button>
                    </div>
                  )}
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