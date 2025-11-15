import React, { useState, useEffect } from 'react';
import { Trophy, TrendingUp, MapPin, Users, ChevronLeft, ChevronRight, Search, Sparkles } from 'lucide-react';

interface LeaderboardEntry {
  rank: number;
  username: string;
  email: string;
  profile_picture?: string;
  region: string;
  avg_score: number;
  interview_count: number;
  percentile: number;
}

interface LeaderboardPageProps {
  onClose: () => void;
}

const REGION_CARDS = [
  { code: 'all', name: 'Global', icon: '🌍', countries: 'All Regions', color: 'from-blue-500 to-purple-500' },
  { code: 'US', name: 'North America', icon: '🇺🇸', countries: 'USA, Canada, Mexico', color: 'from-red-500 to-orange-500' },
  { code: 'EU', name: 'Europe', icon: '🇪🇺', countries: 'EU, UK, Switzerland, Norway', color: 'from-blue-500 to-cyan-500' },
  { code: 'Asia Pacific', name: 'Asia Pacific', icon: '🌏', countries: 'India, China, Japan, Australia', color: 'from-green-500 to-teal-500' },
  { code: 'BR', name: 'South America', icon: '🇧🇷', countries: 'Brazil, Argentina, Chile', color: 'from-yellow-500 to-green-500' },
  { code: 'Africa', name: 'Africa', icon: '🌍', countries: 'South Africa, Nigeria, Kenya', color: 'from-orange-500 to-red-500' },
  { code: 'AE', name: 'Middle East', icon: '🇦🇪', countries: 'UAE, Saudi Arabia, Israel', color: 'from-purple-500 to-pink-500' },
];

const LeaderboardPage: React.FC<LeaderboardPageProps> = ({ onClose }) => {
  const [leaderboardData, setLeaderboardData] = useState<LeaderboardEntry[]>([]);
  const [selectedRegion, setSelectedRegion] = useState<string>('');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalUsers, setTotalUsers] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [userRegion, setUserRegion] = useState<string | null>(null);
  const [showRegionSelector, setShowRegionSelector] = useState(true);
  
  const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';
  const pageSize = 20;

  // Fetch user's region on mount
  useEffect(() => {
    const fetchUserRegion = async () => {
      try {
        const token = localStorage.getItem('access_token');
        if (!token) return;
        
        const response = await fetch(`${API_BASE}/auth/me`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        
        if (response.ok) {
          const userData = await response.json();
          if (userData.region) {
            setUserRegion(userData.region);
          }
        }
      } catch (error) {
        console.error('Failed to fetch user region:', error);
      }
    };
    
    fetchUserRegion();
  }, []);

  useEffect(() => {
    fetchLeaderboard();
  }, [selectedRegion, currentPage]);

  const fetchLeaderboard = async () => {
    setIsLoading(true);
    try {
      const token = localStorage.getItem('access_token');
      const endpoint = selectedRegion === 'all' 
        ? `/leaderboard/global?page=${currentPage}&page_size=${pageSize}`
        : `/leaderboard/regional/${encodeURIComponent(selectedRegion)}?page=${currentPage}&page_size=${pageSize}`;
      
      const headers: Record<string, string> = {};
      if (token) headers['Authorization'] = `Bearer ${token}`;
      
      const response = await fetch(`${API_BASE}/api${endpoint}`, { headers });
      if (response.ok) {
        const data = await response.json();
        setLeaderboardData(data.leaderboard || []);
        setTotalUsers(data.total_users || 0);
      } else {
        console.warn(`Leaderboard API returned ${response.status}`);
        setLeaderboardData([]);
      }
    } catch (error) {
      console.error('Failed to fetch leaderboard:', error);
      setLeaderboardData([]);
    } finally {
      setIsLoading(false);
    }
  };

  const getRankMedal = (rank: number) => {
    if (rank === 1) return '🥇';
    if (rank === 2) return '🥈';
    if (rank === 3) return '🥉';
    return null;
  };

  const getInitials = (name: string) => {
    return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
  };

  const filteredData = leaderboardData.filter((entry: LeaderboardEntry) =>
    entry.username?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // Show region selector first
  if (showRegionSelector) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-orange-50">
        {/* Header Section */}
        <div className="bg-gradient-to-r from-blue-600 via-blue-500 to-orange-500 text-white py-12">
          <div className="max-w-7xl mx-auto px-6">
            <div className="flex items-center justify-between">
              <div>
                <div className="flex items-center space-x-3 mb-2">
                  <Trophy className="w-8 h-8" />
                  <h1 className="text-4xl font-bold">Leaderboards</h1>
                </div>
                <p className="text-blue-100">Select a region to view rankings</p>
                {userRegion && (
                  <p className="text-blue-100 text-sm mt-2">
                    🔒 Your locked region: <span className="font-bold">{userRegion}</span>
                  </p>
                )}
              </div>
              <button
                onClick={onClose}
                className="p-2 hover:bg-white/20 rounded-lg transition-colors"
              >
                <ChevronLeft className="w-6 h-6" />
              </button>
            </div>
          </div>
        </div>

        {/* Region Cards Grid */}
        <div className="max-w-7xl mx-auto px-6 py-12">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {REGION_CARDS.map((region) => (
              <button
                key={region.code}
                onClick={() => {
                  setSelectedRegion(region.code);
                  setCurrentPage(1);
                  setShowRegionSelector(false);
                }}
                className={`group relative p-8 rounded-2xl text-left text-white transition-all duration-300 transform hover:scale-105 hover:shadow-2xl bg-gradient-to-br ${region.color}`}
              >
                {/* Decorative background */}
                <div className="absolute top-0 right-0 opacity-10 text-6xl">{region.icon}</div>

                <div className="relative z-10">
                  <div className="text-5xl mb-4">{region.icon}</div>
                  <h3 className="text-2xl font-bold mb-2">{region.name}</h3>
                  <p className="text-white/90 mb-4">{region.countries}</p>
                  {userRegion === region.code && (
                    <div className="flex items-center space-x-2 text-yellow-300 font-bold mb-2">
                      <span>🔒 Your Region (Locked)</span>
                    </div>
                  )}
                  <div className="flex items-center space-x-2 text-white/80 group-hover:text-white transition-colors">
                    <MapPin className="w-4 h-4" />
                    <span className="text-sm font-medium">View Rankings</span>
                  </div>
                </div>
              </button>
            ))}
          </div>
        </div>
      </div>
    );
  }

  // Show leaderboard with region header
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-orange-50">
      {/* Header Section */}
      <div className="bg-gradient-to-r from-blue-600 via-blue-500 to-orange-500 text-white py-8 md:py-12">
        <div className="max-w-7xl mx-auto px-6">
          <div className="flex items-center justify-between mb-8">
            <div className="flex items-center space-x-4 flex-1">
              <button
                onClick={() => setShowRegionSelector(true)}
                className="p-2 hover:bg-white/20 rounded-lg transition-colors"
                title="Change region"
              >
                <ChevronLeft className="w-6 h-6" />
              </button>
              <div>
                <div className="flex items-center space-x-3 mb-2">
                  <Trophy className="w-8 h-8" />
                  <div>
                    <h1 className="text-3xl md:text-4xl font-bold">
                      {REGION_CARDS.find(r => r.code === selectedRegion)?.name || 'Leaderboard'}
                    </h1>
                    {userRegion && (
                      <p className="text-blue-100 text-sm md:text-base mt-1">
                        🔒 Your locked region: <span className="font-bold">{userRegion}</span>
                      </p>
                    )}
                  </div>
                </div>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <button
                onClick={onClose}
                className="p-2 hover:bg-white/20 rounded-lg transition-colors"
              >
                <ChevronLeft className="w-6 h-6" />
              </button>
            </div>
          </div>

          {/* Search Bar */}
          <div className="max-w-2xl">
            <div className="relative">
              <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search by name..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-12 pr-4 py-3 bg-white/95 backdrop-blur-sm text-gray-900 rounded-lg focus:outline-none focus:ring-2 focus:ring-yellow-300"
              />
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-12">
        {/* Top 3 Performers */}
        {filteredData.slice(0, 3).length > 0 && (
          <div className="mb-12">
            <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-2">
              <Sparkles className="w-6 h-6 text-yellow-500" />
              Top Performers
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {filteredData.slice(0, 3).map((entry, index) => {
                const medals = ['🥇', '🥈', '🥉'];
                return (
                  <div
                    key={entry.rank}
                    className={`relative rounded-2xl overflow-hidden transition-all duration-300 hover:shadow-2xl ${
                      index === 0
                        ? 'bg-gradient-to-br from-yellow-400 to-yellow-600 shadow-2xl transform scale-105'
                        : index === 1
                        ? 'bg-gradient-to-br from-gray-300 to-gray-500'
                        : 'bg-gradient-to-br from-orange-400 to-orange-600'
                    } text-white p-8`}
                  >
                    {/* Decorative background */}
                    <div className="absolute top-0 right-0 w-32 h-32 opacity-10">
                      <Trophy className="w-32 h-32" />
                    </div>

                    <div className="relative z-10">
                      <div className="text-6xl font-bold mb-4">{medals[index]}</div>
                      
                      {/* Avatar */}
                      <div className="w-20 h-20 rounded-full bg-white/20 border-4 border-white/40 flex items-center justify-center mb-4 mx-auto backdrop-blur-sm">
                        {entry.profile_picture && !entry.profile_picture.startsWith('data:image') ? (
                          <img src={entry.profile_picture} alt={entry.username} className="w-full h-full rounded-full object-cover" />
                        ) : (
                          <div className="w-full h-full rounded-full bg-gradient-to-br from-purple-400 to-blue-400 flex items-center justify-center font-bold">
                            {getInitials(entry.username)}
                          </div>
                        )}
                      </div>

                      <h3 className="text-xl font-bold text-center mb-1">{entry.username}</h3>
                      <p className="text-sm text-white/80 text-center mb-6">{entry.email}</p>

                      <div className="bg-white/20 backdrop-blur-md rounded-xl p-4 mb-4">
                        <div className="flex justify-between items-center mb-3">
                          <span className="text-sm font-semibold">Average Score</span>
                          <span className="text-2xl font-bold">{entry.avg_score}</span>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-sm">Interviews: {entry.interview_count}</span>
                          <span className="text-sm font-semibold">↑ {entry.percentile}%</span>
                        </div>
                      </div>

                      <div className="flex items-center justify-center space-x-2 text-sm">
                        <MapPin className="w-4 h-4" />
                        <span>{entry.region}</span>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Full Leaderboard Table */}
        <div className="bg-white rounded-3xl shadow-xl overflow-hidden border border-gray-100">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="bg-gradient-to-r from-blue-50 to-orange-50 border-b border-gray-200">
                  <th className="px-6 py-4 text-left text-sm font-bold text-gray-900">Rank</th>
                  <th className="px-6 py-4 text-left text-sm font-bold text-gray-900">User</th>
                  <th className="px-6 py-4 text-left text-sm font-bold text-gray-900">Region</th>
                  <th className="px-6 py-4 text-right text-sm font-bold text-gray-900">Avg Score</th>
                  <th className="px-6 py-4 text-right text-sm font-bold text-gray-900">Interviews</th>
                  <th className="px-6 py-4 text-right text-sm font-bold text-gray-900">Percentile</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {isLoading ? (
                  <tr>
                    <td colSpan={6} className="px-6 py-12 text-center">
                      <div className="inline-block">
                        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-500"></div>
                      </div>
                    </td>
                  </tr>
                ) : filteredData.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="px-6 py-12 text-center text-gray-500">
                      No users found
                    </td>
                  </tr>
                ) : (
                  filteredData.map((entry) => (
                    <tr
                      key={entry.rank}
                      className="hover:bg-gradient-to-r hover:from-blue-50 hover:to-orange-50 transition-colors duration-200"
                    >
                      <td className="px-6 py-4">
                        <div className="flex items-center space-x-2">
                          {getRankMedal(entry.rank) && (
                            <span className="text-2xl">{getRankMedal(entry.rank)}</span>
                          )}
                          <span className="font-bold text-gray-900 text-lg">#{entry.rank}</span>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center space-x-3">
                          <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center text-white font-bold flex-shrink-0 border-2 border-gray-200">
                            {entry.profile_picture && !entry.profile_picture.startsWith('data:image') ? (
                              <img src={entry.profile_picture} alt={entry.username} className="w-full h-full rounded-full object-cover" />
                            ) : (
                              getInitials(entry.username)
                            )}
                          </div>
                          <div className="flex-1">
                            <p className="font-semibold text-gray-900">{entry.username}</p>
                            <p className="text-sm text-gray-500">{entry.email}</p>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center space-x-2 text-gray-700">
                          <MapPin className="w-4 h-4 text-orange-500" />
                          <span>{entry.region}</span>
                        </div>
                      </td>
                      <td className="px-6 py-4 text-right">
                        <div className="inline-block px-4 py-2 rounded-lg bg-blue-100 text-blue-900 font-bold">
                          {entry.avg_score}
                        </div>
                      </td>
                      <td className="px-6 py-4 text-right">
                        <div className="flex items-center justify-end space-x-1 text-gray-700">
                          <Users className="w-4 h-4" />
                          <span className="font-semibold">{entry.interview_count}</span>
                        </div>
                      </td>
                      <td className="px-6 py-4 text-right">
                        <div className="inline-flex items-center space-x-1 px-3 py-1 rounded-full bg-green-100">
                          <TrendingUp className="w-4 h-4 text-green-600" />
                          <span className="font-bold text-green-700">{entry.percentile}%</span>
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          {!isLoading && filteredData.length > 0 && (
            <div className="flex items-center justify-between px-6 py-6 border-t border-gray-100 bg-gray-50">
              <div className="text-sm text-gray-600">
                Page <span className="font-bold">{currentPage}</span> of <span className="font-bold">{Math.ceil(totalUsers / pageSize)}</span>
              </div>
              <div className="flex space-x-3">
                <button
                  onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                  disabled={currentPage === 1}
                  className="p-2 rounded-lg border border-gray-300 text-gray-700 hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  <ChevronLeft className="w-5 h-5" />
                </button>
                <button
                  onClick={() => setCurrentPage(currentPage + 1)}
                  disabled={currentPage >= Math.ceil(totalUsers / pageSize)}
                  className="p-2 rounded-lg border border-gray-300 text-gray-700 hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  <ChevronRight className="w-5 h-5" />
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default LeaderboardPage;
