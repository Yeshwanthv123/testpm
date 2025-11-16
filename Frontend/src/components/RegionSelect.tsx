import React, { useState } from 'react';
import { MapPin, ArrowRight } from 'lucide-react';
import { User as UserType } from '../types';

interface RegionSelectProps {
  user: UserType;
  onComplete: (userData: UserType) => void;
}

const RegionSelect: React.FC<RegionSelectProps> = ({ user, onComplete }) => {
  const [selectedRegion, setSelectedRegion] = useState<string>('');

  const regions = [
    { code: 'US', name: 'North America', flag: '🇺🇸', countries: 'USA, Canada, Mexico' },
    { code: 'EU', name: 'Europe', flag: '🇬🇧', countries: 'EU, UK, Switzerland, Norway' },
    { code: 'Asia Pacific', name: 'Asia Pacific', flag: '🇮🇳', countries: 'India, China, Japan, Australia' },
    { code: 'BR', name: 'South America', flag: '🇧🇷', countries: 'Brazil, Argentina, Chile' },
    { code: 'Africa', name: 'Africa', flag: '🇿🇦', countries: 'South Africa, Nigeria, Kenya' },
    { code: 'AE', name: 'Middle East', flag: '🇸🇦', countries: 'UAE, Saudi Arabia, Israel' }
  ];

  const handleRegionSelect = (regionCode: string) => {
    setSelectedRegion(regionCode);
  };

  const handleConfirm = () => {
    if (!selectedRegion) {
      alert('Please select a region');
      return;
    }

    const updatedUser: UserType = {
      ...user,
      region: selectedRegion
    };
    
    // Directly go to onboarding without confirmation dialog
    onComplete(updatedUser);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 flex items-center justify-center p-4">
      <div className="max-w-5xl w-full">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="mb-6 flex justify-center">
            <div className="w-20 h-20 bg-gradient-to-br from-yellow-400 to-orange-500 rounded-full flex items-center justify-center shadow-2xl transform hover:scale-110 transition-all duration-300">
              <div className="text-4xl">🧠</div>
            </div>
          </div>
          <h1 className="text-4xl md:text-5xl font-bold mb-4">
            <span className="bg-gradient-to-r from-purple-600 via-pink-600 to-orange-600 bg-clip-text text-transparent">
              Your Region
            </span>
          </h1>
          <p className="text-lg md:text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
            We'll compare your performance with regional peers
          </p>
        </div>

        {/* Region Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          {regions.map((region) => (
            <button
              key={region.code}
              onClick={() => handleRegionSelect(region.code)}
              className={`group relative p-6 rounded-2xl text-center transition-all duration-300 transform hover:scale-105 border-2 min-h-40 ${
                selectedRegion === region.code
                  ? 'border-orange-500 bg-gradient-to-br from-orange-50 to-yellow-50 shadow-xl'
                  : 'border-gray-200 bg-white hover:border-gray-300 hover:shadow-lg'
              }`}
            >
              <div className="relative z-10">
                <div className="text-7xl mb-4 drop-shadow-lg">{region.flag}</div>
                <h3 className="text-lg font-bold text-gray-900 mb-1">{region.name}</h3>
                <p className="text-xs text-gray-600">{region.countries}</p>
              </div>
            </button>
          ))}
        </div>

        {/* Info Box */}
        <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-2xl p-6 border border-blue-200 mb-8">
          <div className="flex items-start space-x-3">
            <MapPin className="w-6 h-6 text-blue-600 mt-1 flex-shrink-0" />
            <div className="text-left">
              <h4 className="font-bold text-blue-900 mb-2">🔒 Region Selection</h4>
              <p className="text-sm text-blue-800">
                Your selected region will be locked and used for peer comparison. You can still view all regional leaderboards, but your primary ranking will always be compared against your region.
              </p>
            </div>
          </div>
        </div>

        {/* Confirm Button */}
        <button
          onClick={handleConfirm}
          disabled={!selectedRegion}
          className="w-full flex items-center justify-center space-x-3 px-8 py-4 bg-gradient-to-r from-yellow-500 to-orange-500 text-white rounded-2xl hover:from-yellow-600 hover:to-orange-600 transition-all transform hover:scale-105 font-bold text-lg shadow-2xl disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
        >
          <span>Confirm Selection</span>
          <ArrowRight className="w-6 h-6" />
        </button>
      </div>
    </div>
  );
};

export default RegionSelect;
