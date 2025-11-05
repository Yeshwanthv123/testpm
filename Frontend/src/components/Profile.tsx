import React, { useState, useEffect } from 'react';
import {
  User, Settings, Crown, Clock, Edit3, CreditCard, LogOut, Save, X
} from 'lucide-react';
import { User as UserType } from '../types';

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

interface ProfileProps {
  user: UserType;
  onUpdateUser: (user: UserType) => void;
  onClose: () => void;
  onLogout: () => void; // ✅ Added this line
}

const Profile: React.FC<ProfileProps> = ({ user, onUpdateUser, onClose, onLogout }) => {
  const [activeTab, setActiveTab] =
    useState<'overview' | 'settings' | 'billing' | 'history'>('overview');
  const [isEditingProfile, setIsEditingProfile] = useState(false);

  const [userProfile, setUserProfile] = useState({
    full_name: user.full_name || '',
    email: user.email || '',
    currentRole: user.currentRole || 'Not Set',
    experience: user.experience || '0-2',
    region: user.region || 'Not Set',
    avatar: '👨‍💼',
    joinDate: '2024-01-15'
  });

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

  const handleProfileSave = async () => {
    const token = localStorage.getItem('access_token');
    if (!token) return;

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

      if (!response.ok) throw new Error('Failed to update profile');

      const updatedUser = await response.json();
      onUpdateUser(updatedUser);
      setIsEditingProfile(false);
    } catch (err) {
      console.error(err);
    }
  };

  // ✅ Correct instant logout
  const handleLogout = () => {
    try {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
    } catch {}
    onClose();    // close the modal
    onLogout();   // tells App.tsx to set currentStep = 'login' immediately
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
                  <span className="text-sm">
                    Pro Member since {new Date(userProfile.joinDate).toLocaleDateString()}
                  </span>
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
            <div>
              <nav className="space-y-2">
                {[
                  { id: 'overview', label: 'Overview', icon: User },
                  { id: 'settings', label: 'Account Settings', icon: Settings },
                  { id: 'billing', label: 'Billing & Plans', icon: CreditCard },
                  { id: 'history', label: 'Interview History', icon: Clock },
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

            {/* ✅ Persistent Log Out button */}
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
          <div className="flex-1 overflow-y-auto p-8">
            {activeTab === 'settings' && (
              <>
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
                          onChange={(e) =>
                            setUserProfile((prev) => ({ ...prev, full_name: e.target.value }))
                          }
                          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                        />
                      ) : (
                        <div className="px-4 py-3 bg-gray-50 rounded-lg text-gray-900">
                          {userProfile.full_name}
                        </div>
                      )}
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Email</label>
                      {isEditingProfile ? (
                        <input
                          type="email"
                          value={userProfile.email}
                          onChange={(e) =>
                            setUserProfile((prev) => ({ ...prev, email: e.target.value }))
                          }
                          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                        />
                      ) : (
                        <div className="px-4 py-3 bg-gray-50 rounded-lg text-gray-900">
                          {userProfile.email}
                        </div>
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
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Profile;
