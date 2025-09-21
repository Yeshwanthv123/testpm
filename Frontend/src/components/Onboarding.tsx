import React, { useState } from 'react';
import { User, Briefcase, MapPin, ArrowRight, Star, TrendingUp, Users, Globe } from 'lucide-react';
import { User as UserType } from '../types';

interface OnboardingProps {
  user: UserType;
  onComplete: (userData: UserType) => void;
}

const Onboarding: React.FC<OnboardingProps> = ({ user, onComplete }) => {
  const [formData, setFormData] = useState({
    experience: user.experience || '',
    currentRole: user.currentRole || '',
    region: user.region || ''
  });

  const experienceLevels = [
    { 
      value: '0-2', 
      label: '0-2 years', 
      desc: 'Entry level, APM, or transitioning to PM',
      icon: '🌱',
      color: 'from-green-400 to-emerald-500'
    },
    { 
      value: '3-5', 
      label: '3-5 years', 
      desc: 'Mid-level PM with some experience',
      icon: '🚀',
      color: 'from-blue-400 to-cyan-500'
    },
    { 
      value: '6-10', 
      label: '6-10 years', 
      desc: 'Senior PM with proven track record',
      icon: '⭐',
      color: 'from-purple-400 to-pink-500'
    },
    { 
      value: '10+', 
      label: '10+ years', 
      desc: 'Principal/Director level experience',
      icon: '👑',
      color: 'from-yellow-400 to-orange-500'
    }
  ];

  const regions = [
    { name: 'North America', flag: '🇺🇸', desc: 'USA, Canada, Mexico' },
    { name: 'Europe', flag: '🇪🇺', desc: 'EU, UK, Switzerland, Norway' },
    { name: 'Asia Pacific', flag: '🌏', desc: 'India, China, Japan, Australia' },
    { name: 'South America', flag: '🇧🇷', desc: 'Brazil, Argentina, Chile' },
    { name: 'Africa', flag: '🌍', desc: 'South Africa, Nigeria, Kenya' },
    { name: 'Middle East', flag: '🇦🇪', desc: 'UAE, Saudi Arabia, Israel' }
  ];

  const handleSubmit = () => {
    if (!formData.experience || !formData.currentRole || !formData.region) {
      alert('Please fill in all fields');
      return;
    }

    const updatedUser: UserType = {
      ...user,
      experience: formData.experience,
      currentRole: formData.currentRole,
      region: formData.region
    };

    onComplete(updatedUser);
  };

  const canProceed = formData.experience && formData.currentRole && formData.region;

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 p-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8 md:mb-16">
          <div className="mb-6 flex justify-center">
            <div className="w-16 h-16 md:w-20 md:h-20 bg-gradient-to-br from-yellow-400 to-orange-500 rounded-full flex items-center justify-center shadow-2xl transform hover:scale-110 transition-all duration-300">
              <div className="text-3xl md:text-4xl">🧠</div>
            </div>
          </div>
          <h1 className="text-3xl md:text-4xl lg:text-5xl font-bold mb-4">
            <span className="bg-gradient-to-r from-yellow-600 to-orange-600 bg-clip-text text-transparent">
              Tell Us About Your Experience
            </span>
          </h1>
          <p className="text-lg md:text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed px-4">
            Help us personalize your interview experience by sharing your background. 
            We'll tailor questions to match your experience level and compare your performance with regional peers.
          </p>
        </div>

        <div className="bg-white rounded-3xl shadow-2xl p-6 md:p-8 border border-gray-100">
          {/* Experience Level Section */}
          <div className="mb-8 md:mb-12">
            <div className="flex flex-col md:flex-row md:items-center space-y-3 md:space-y-0 md:space-x-3 mb-6 md:mb-8">
              <div className="w-10 h-10 md:w-12 md:h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center flex-shrink-0">
                <Briefcase className="w-5 h-5 md:w-6 md:h-6 text-white" />
              </div>
              <div>
                <h2 className="text-xl md:text-2xl font-bold text-gray-900">Experience Level</h2>
                <p className="text-gray-600 text-sm md:text-base">This helps us adjust question difficulty and expectations</p>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 md:gap-4">
              {experienceLevels.map(level => (
                <button
                  key={level.value}
                  onClick={() => setFormData(prev => ({ ...prev, experience: level.value }))}
                  className={`p-4 md:p-6 text-left rounded-2xl border-2 transition-all transform hover:scale-105 ${
                    formData.experience === level.value
                      ? 'border-orange-500 bg-gradient-to-br from-orange-50 to-yellow-50 shadow-xl'
                      : 'border-gray-200 hover:border-gray-300 hover:shadow-lg bg-white'
                  }`}
                >
                  <div className="flex items-start space-x-3 md:space-x-4">
                    <div className={`w-10 h-10 md:w-12 md:h-12 bg-gradient-to-r ${level.color} rounded-xl flex items-center justify-center text-xl md:text-2xl shadow-lg flex-shrink-0`}>
                      {level.icon}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="font-bold text-base md:text-lg text-gray-900 mb-1">{level.label}</div>
                      <div className="text-sm text-gray-600">{level.desc}</div>
                    </div>
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* Current Role Section */}
          <div className="mb-8 md:mb-12">
            <div className="flex flex-col md:flex-row md:items-center space-y-3 md:space-y-0 md:space-x-3 mb-4 md:mb-6">
              <div className="w-10 h-10 md:w-12 md:h-12 bg-gradient-to-br from-green-500 to-teal-600 rounded-xl flex items-center justify-center flex-shrink-0">
                <User className="w-5 h-5 md:w-6 md:h-6 text-white" />
              </div>
              <div>
                <h2 className="text-xl md:text-2xl font-bold text-gray-900">Current Role</h2>
                <p className="text-gray-600 text-sm md:text-base">What's your current position or target role?</p>
              </div>
            </div>

            <input
              type="text"
              value={formData.currentRole}
              onChange={(e) => setFormData(prev => ({ ...prev, currentRole: e.target.value }))}
              className="w-full px-4 md:px-6 py-3 md:py-4 border-2 border-gray-300 rounded-2xl focus:ring-2 focus:ring-orange-500 focus:border-transparent transition-all text-base md:text-lg"
              placeholder="e.g., Senior Product Manager, APM, Software Engineer transitioning to PM"
            />
            
            <div className="mt-4 p-3 md:p-4 bg-blue-50 rounded-xl border border-blue-200">
              <h4 className="font-medium text-blue-900 mb-2 text-sm md:text-base">💡 Examples of roles:</h4>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-2 text-xs md:text-sm text-blue-800">
                <span>• Product Manager</span>
                <span>• Senior PM</span>
                <span>• Associate PM</span>
                <span>• Principal PM</span>
                <span>• Director of Product</span>
                <span>• VP of Product</span>
              </div>
            </div>
          </div>

          {/* Region Section */}
          <div className="mb-6 md:mb-8">
            <div className="flex flex-col md:flex-row md:items-center space-y-3 md:space-y-0 md:space-x-3 mb-6 md:mb-8">
              <div className="w-10 h-10 md:w-12 md:h-12 bg-gradient-to-br from-purple-500 to-pink-600 rounded-xl flex items-center justify-center flex-shrink-0">
                <MapPin className="w-5 h-5 md:w-6 md:h-6 text-white" />
              </div>
              <div>
                <h2 className="text-xl md:text-2xl font-bold text-gray-900">Your Region</h2>
                <p className="text-gray-600 text-sm md:text-base">We'll compare your performance with regional peers</p>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 md:gap-4 mb-4 md:mb-6">
              {regions.map(region => (
                <button
                  key={region.name}
                  onClick={() => setFormData(prev => ({ ...prev, region: region.name }))}
                  className={`p-3 md:p-4 text-center rounded-2xl border-2 transition-all transform hover:scale-105 ${
                    formData.region === region.name
                      ? 'border-orange-500 bg-gradient-to-br from-orange-50 to-yellow-50 shadow-xl'
                      : 'border-gray-200 hover:border-gray-300 hover:shadow-lg bg-white'
                  }`}
                >
                  <div className="text-2xl md:text-3xl mb-2">{region.flag}</div>
                  <div className="font-bold text-gray-900 mb-1 text-sm md:text-base">{region.name}</div>
                  <div className="text-xs text-gray-600">{region.desc}</div>
                </button>
              ))}
            </div>

            <div className="bg-gradient-to-r from-green-50 to-emerald-50 rounded-2xl p-4 md:p-6 border border-green-200">
              <div className="flex items-start space-x-3">
                <Globe className="w-5 h-5 md:w-6 md:h-6 text-green-600 mt-1 flex-shrink-0" />
                <div>
                  <h4 className="font-bold text-green-900 mb-2 text-sm md:text-base">🌍 Why we collect regional data:</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-2 md:gap-3 text-xs md:text-sm text-green-800">
                    <div className="flex items-center space-x-2">
                      <TrendingUp className="w-3 h-3 md:w-4 md:h-4 flex-shrink-0" />
                      <span>Compare with regional peers</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Users className="w-3 h-3 md:w-4 md:h-4 flex-shrink-0" />
                      <span>Understand local market standards</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Star className="w-3 h-3 md:w-4 md:h-4 flex-shrink-0" />
                      <span>Get region-specific insights</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Briefcase className="w-3 h-3 md:w-4 md:h-4 flex-shrink-0" />
                      <span>Receive targeted career advice</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Submit Button */}
          <div className="text-center">
            <button
              onClick={handleSubmit}
              disabled={!canProceed}
              className="inline-flex items-center space-x-3 px-8 md:px-12 py-3 md:py-4 bg-gradient-to-r from-yellow-500 to-orange-500 text-white rounded-2xl hover:from-yellow-600 hover:to-orange-600 transition-all transform hover:scale-105 font-bold text-base md:text-lg shadow-2xl disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none w-full sm:w-auto"
            >
              <span>Continue to Interview Setup</span>
              <ArrowRight className="w-5 h-5 md:w-6 md:h-6" />
            </button>
            {!canProceed && (
              <p className="text-red-600 text-sm mt-3">Please complete all sections to continue</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Onboarding;