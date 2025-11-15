import React, { useState } from 'react';
import { MapPin, ArrowRight } from 'lucide-react';
import { User as UserType } from '../types';

interface RegionSelectProps {
  user: UserType;
  onComplete: (userData: UserType) => void;
}

const RegionSelect: React.FC<RegionSelectProps> = ({ user, onComplete }) => {
  const [selectedRegion, setSelectedRegion] = useState<string>('');
  const [showBg, setShowBg] = useState(true);
  const [showConfirmation, setShowConfirmation] = useState(false);

  const regions = [
    { code: 'US', name: 'North America', flag: '🇺🇸', countries: 'USA, Canada, Mexico' },
    { code: 'EU', name: 'Europe', flag: '🇪🇺', countries: 'EU, UK, Switzerland, Norway' },
    { code: 'Asia Pacific', name: 'Asia Pacific', flag: '🌏', countries: 'India, China, Japan, Australia' },
    { code: 'BR', name: 'South America', flag: '🇧🇷', countries: 'Brazil, Argentina, Chile' },
    { code: 'Africa', name: 'Africa', flag: '🌍', countries: 'South Africa, Nigeria, Kenya' },
    { code: 'AE', name: 'Middle East', flag: '🇦🇪', countries: 'UAE, Saudi Arabia, Israel' }
  ];

  const handleRegionSelect = (regionCode: string) => {
    setSelectedRegion(regionCode);
    setShowConfirmation(true);
  };

  const handleConfirmRegion = () => {
    setShowBg(false);
  };

  const handleGoBack = () => {
    setSelectedRegion('');
    setShowConfirmation(false);
  };

  const handleContinue = () => {
    if (!selectedRegion) {
      alert('Please select a region');
      return;
    }

    const updatedUser: UserType = {
      ...user,
      region: selectedRegion
    };

    onComplete(updatedUser);
  };

  if (selectedRegion && showConfirmation && !showBg) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center p-4">
        <div className="max-w-4xl w-full">
          {/* Region Confirmation Card */}
          <div className="text-center mb-12">
            <div className="mb-6 flex justify-center">
              <div className="w-20 h-20 bg-gradient-to-br from-yellow-400 to-orange-500 rounded-full flex items-center justify-center shadow-2xl">
                <div className="text-4xl">🧠</div>
              </div>
            </div>
            <h1 className="text-4xl font-bold mb-4">
              <span className="bg-gradient-to-r from-yellow-600 to-orange-600 bg-clip-text text-transparent">
                Region Selected
              </span>
            </h1>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto leading-relaxed">
              Your region has been set to <span className="font-bold text-orange-600">{regions.find(r => r.code === selectedRegion)?.name}</span>
            </p>
          </div>

          {/* Selected Region Card */}
          <div className="bg-gradient-to-br from-orange-50 to-yellow-50 rounded-2xl p-8 border-2 border-orange-500 mb-8 text-center">
            <div className="text-5xl mb-4">{regions.find(r => r.code === selectedRegion)?.flag}</div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              {regions.find(r => r.code === selectedRegion)?.name}
            </h2>
            <p className="text-gray-600">
              {regions.find(r => r.code === selectedRegion)?.countries}
            </p>
            <div className="flex items-center justify-center space-x-2 text-orange-600 font-bold mt-4">
              <span>🔒 Locked</span>
            </div>
          </div>

          {/* Info Box */}
          <div className="bg-blue-50 rounded-2xl p-6 border border-blue-200 mb-8">
            <div className="flex items-start space-x-3">
              <MapPin className="w-6 h-6 text-blue-600 mt-1 flex-shrink-0" />
              <div className="text-left">
                <h4 className="font-bold text-blue-900 mb-2">Region Lock</h4>
                <p className="text-sm text-blue-800">
                  Your region is now locked and will be used to compare your performance with regional peers. You'll still be able to view all regional leaderboards.
                </p>
              </div>
            </div>
          </div>

          {/* Continue Button */}
          <button
            onClick={handleContinue}
            className="w-full flex items-center justify-center space-x-3 px-8 py-4 bg-gradient-to-r from-yellow-500 to-orange-500 text-white rounded-2xl hover:from-yellow-600 hover:to-orange-600 transition-all transform hover:scale-105 font-bold text-lg shadow-2xl"
          >
            <span>Continue to Setup</span>
            <ArrowRight className="w-6 h-6" />
          </button>
        </div>
      </div>
    );
  }

  // Confirmation Dialog
  if (selectedRegion && showConfirmation && showBg) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 flex items-center justify-center p-4">
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-2xl shadow-2xl p-8 max-w-md w-full">
            <div className="text-center mb-6">
              <div className="text-5xl mb-4">{regions.find(r => r.code === selectedRegion)?.flag}</div>
              <h2 className="text-2xl font-bold text-gray-900 mb-2">
                {regions.find(r => r.code === selectedRegion)?.name}
              </h2>
              <p className="text-sm text-gray-600 mb-4">
                {regions.find(r => r.code === selectedRegion)?.countries}
              </p>
            </div>

            <div className="bg-blue-50 rounded-lg p-4 mb-8 border border-blue-200">
              <p className="text-sm text-gray-700">
                <span className="font-bold">Are you sure</span> you want to choose this region? Once confirmed, it will be <span className="font-bold">locked</span> and cannot be changed.
              </p>
            </div>

            {/* Buttons */}
            <div className="flex gap-3">
              <button
                onClick={handleGoBack}
                className="flex-1 px-4 py-3 border-2 border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors font-semibold"
              >
                No, Choose Again
              </button>
              <button
                onClick={handleConfirmRegion}
                className="flex-1 px-4 py-3 bg-gradient-to-r from-yellow-500 to-orange-500 text-white rounded-lg hover:from-yellow-600 hover:to-orange-600 transition-all font-semibold"
              >
                Yes, Confirm
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (selectedRegion && !showBg) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center p-4">
        <div className="max-w-4xl w-full">
          {/* Region Confirmation Card */}
          <div className="text-center mb-12">
            <div className="mb-6 flex justify-center">
              <div className="w-20 h-20 bg-gradient-to-br from-yellow-400 to-orange-500 rounded-full flex items-center justify-center shadow-2xl">
                <div className="text-4xl">🧠</div>
              </div>
            </div>
            <h1 className="text-4xl font-bold mb-4">
              <span className="bg-gradient-to-r from-yellow-600 to-orange-600 bg-clip-text text-transparent">
                Region Selected
              </span>
            </h1>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto leading-relaxed">
              Your region has been set to <span className="font-bold text-orange-600">{regions.find(r => r.code === selectedRegion)?.name}</span>
            </p>
          </div>

          {/* Selected Region Card */}
          <div className="bg-gradient-to-br from-orange-50 to-yellow-50 rounded-2xl p-8 border-2 border-orange-500 mb-8 text-center">
            <div className="text-5xl mb-4">{regions.find(r => r.code === selectedRegion)?.flag}</div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              {regions.find(r => r.code === selectedRegion)?.name}
            </h2>
            <p className="text-gray-600">
              {regions.find(r => r.code === selectedRegion)?.countries}
            </p>
            <div className="flex items-center justify-center space-x-2 text-orange-600 font-bold mt-4">
              <span>🔒 Locked</span>
            </div>
          </div>

          {/* Info Box */}
          <div className="bg-blue-50 rounded-2xl p-6 border border-blue-200 mb-8">
            <div className="flex items-start space-x-3">
              <MapPin className="w-6 h-6 text-blue-600 mt-1 flex-shrink-0" />
              <div className="text-left">
                <h4 className="font-bold text-blue-900 mb-2">Region Lock</h4>
                <p className="text-sm text-blue-800">
                  Your region is now locked and will be used to compare your performance with regional peers. You'll still be able to view all regional leaderboards.
                </p>
              </div>
            </div>
          </div>

          {/* Continue Button */}
          <button
            onClick={handleContinue}
            className="w-full flex items-center justify-center space-x-3 px-8 py-4 bg-gradient-to-r from-yellow-500 to-orange-500 text-white rounded-2xl hover:from-yellow-600 hover:to-orange-600 transition-all transform hover:scale-105 font-bold text-lg shadow-2xl"
          >
            <span>Continue to Setup</span>
            <ArrowRight className="w-6 h-6" />
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className={`min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 flex items-center justify-center p-4 ${showBg ? 'opacity-100' : 'opacity-0 pointer-events-none'} transition-opacity duration-500`}>
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
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          {regions.map((region) => (
            <button
              key={region.code}
              onClick={() => handleRegionSelect(region.code)}
              className={`group relative p-6 rounded-2xl text-center transition-all duration-300 transform hover:scale-105 border-2 ${
                selectedRegion === region.code
                  ? 'border-orange-500 bg-gradient-to-br from-orange-50 to-yellow-50 shadow-xl'
                  : 'border-gray-200 bg-white hover:border-gray-300 hover:shadow-lg'
              }`}
            >
              <div className="relative z-10">
                <div className="text-5xl mb-4">{region.flag}</div>
                <h3 className="text-xl font-bold text-gray-900 mb-1">{region.name}</h3>
                <p className="text-sm text-gray-600 mb-2">{region.code}</p>
                <p className="text-xs text-gray-500">{region.countries}</p>
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

        {/* Continue Button */}
        <button
          onClick={() => {
            if (!selectedRegion) {
              alert('Please select a region');
              return;
            }
            handleRegionSelect(selectedRegion);
          }}
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
