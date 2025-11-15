import React, { useState, useEffect } from 'react';
import { Trophy, Medal, TrendingUp, MapPin, Users, ChevronRight } from 'lucide-react';

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

interface LeaderboardProps {
  onClose?: () => void;
  userId?: number;
}

const Leaderboard: React.FC<LeaderboardProps> = ({ onClose, userId }) => {
  const [leaderboardData, setLeaderboardData] = useState<LeaderboardEntry[]>([]);
  const [regions, setRegions] = useState<string[]>([]);
  const [selectedRegion, setSelectedRegion] = useState<string>('all');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalUsers, setTotalUsers] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [userRanking, setUserRanking] = useState<any>(null);

  const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';
  const pageSize = 20;

  useEffect(() => {
    fetchLeaderboard();
    fetchRegions();
    if (userId) {
      fetchUserRanking();
    }
  }, [selectedRegion, currentPage, userId]);

  const fetchLeaderboard = async () => {
    setIsLoading(true);
    try {
      const token = localStorage.getItem('access_token');
      const endpoint = selectedRegion === 'all' 
        ? `/leaderboard/global?page=${currentPage}&page_size=${pageSize}`
        : `/leaderboard/regional/${selectedRegion}?page=${currentPage}&page_size=${pageSize}`;
      
      const headers: Record<string, string> = {};
      if (token) headers['Authorization'] = `Bearer ${token}`;
      
      const response = await fetch(`${API_BASE}/api${endpoint}`, { headers });
      if (response.ok) {
        const data = await response.json();
        setLeaderboardData(data.leaderboard || []);
        setTotalUsers(data.total_users || 0);
      }
    } catch (error) {
      console.error('Failed to fetch leaderboard:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const fetchRegions = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/leaderboard/regions`);
      if (response.ok) {
        const data = await response.json();
        setRegions(data.regions || []);
      }
    } catch (error) {
      console.error('Failed to fetch regions:', error);
    }
  };

  const fetchUserRanking = async () => {
    try {
      const token = localStorage.getItem('access_token');
      if (!token || !userId) return;
      
      const headers: Record<string, string> = { Authorization: `Bearer ${token}` };
      const response = await fetch(`${API_BASE}/api/leaderboard/user/${userId}`, { headers });
      if (response.ok) {
        const data = await response.json();
        setUserRanking(data);
      }
    } catch (error) {
      console.error('Failed to fetch user ranking:', error);
    }
  };

  const getAvatarColor = (index: number) => {
    const colors = ['bg-yellow-500', 'bg-gray-400', 'bg-orange-600'];
    return colors[index] || 'bg-blue-500';
  };

  const getRankMedal = (rank: number) => {
    if (rank === 1) return '🥇';
    if (rank === 2) return '🥈';
    if (rank === 3) return '🥉';
    return null;
  };

  const getTotalPages = () => Math.ceil(totalUsers / pageSize);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      <div className="max-w-6xl mx-auto p-4">
        {/* Header */}
        <div className="text-center mb-8">
          <Trophy className="w-12 h-12 mx-auto mb-4 text-yellow-500" />
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Global Leaderboard</h1>
          <p className="text-xl text-gray-600">Compete with PMs worldwide</p>
        </div>

        {/* User's Ranking Card (if user logged in) */}
        {userRanking && (
          <div className="bg-gradient-to-r from-blue-500 to-purple-600 rounded-2xl shadow-lg p-6 mb-8 text-white">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div>
                <div className="text-sm opacity-90">Your Global Percentile</div>
                <div className="text-4xl font-bold">{userRanking.global_percentile}%</div>
              </div>
              <div>
                <div className="text-sm opacity-90">Regional Percentile</div>
                <div className="text-4xl font-bold">{userRanking.regional_percentile}%</div>
              </div>
              <div>
                <div className="text-sm opacity-90">Average Score</div>
                <div className="text-4xl font-bold">{userRanking.avg_score}</div>
              </div>
              <div>
                <div className="text-sm opacity-90">Interviews Completed</div>
                <div className="text-4xl font-bold">{userRanking.interview_count}</div>
              </div>
            </div>
          </div>
        )}

        {/* Filters */}
        <div className="bg-white rounded-2xl shadow-lg p-6 mb-8">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">Filter by Region</label>
              <select
                value={selectedRegion}
                onChange={(e) => {
                  setSelectedRegion(e.target.value);
                  setCurrentPage(1);
                }}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="all">🌍 Global</option>
                {regions.map(region => (
                  <option key={region} value={region}>{region}</option>
                ))}
              </select>
            </div>
            <div className="flex items-end">
              <div className="w-full text-center p-3 bg-blue-50 rounded-lg">
                <div className="text-sm text-gray-600">Total Users</div>
                <div className="text-2xl font-bold text-blue-600">{totalUsers}</div>
              </div>
            </div>
          </div>
        </div>

        {/* Leaderboard Table */}
        <div className="bg-white rounded-2xl shadow-lg overflow-hidden">
          {isLoading ? (
            <div className="p-8 text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
              <p className="text-gray-600 mt-4">Loading leaderboard...</p>
            </div>
          ) : leaderboardData.length === 0 ? (
            <div className="p-8 text-center">
              <Users className="w-12 h-12 mx-auto text-gray-300 mb-4" />
              <p className="text-gray-600">No users in this leaderboard yet</p>
            </div>
          ) : (
            <>
              {/* Top 3 Highlighted */}
              {leaderboardData.slice(0, 3).length > 0 && (
                <div className="p-6 border-b-2 border-gray-100">
                  <h3 className="text-lg font-bold text-gray-900 mb-4">🌟 Top Performers</h3>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {leaderboardData.slice(0, 3).map((entry, idx) => (
                      <div
                        key={`${entry.rank}-${entry.email}`}
                        className={`rounded-xl p-4 border-2 ${
                          idx === 0
                            ? 'bg-yellow-50 border-yellow-300'
                            : idx === 1
                            ? 'bg-gray-50 border-gray-300'
                            : 'bg-orange-50 border-orange-300'
                        }`}
                      >
                        <div className="text-4xl mb-2">{getRankMedal(entry.rank)}</div>
                        <div className="flex items-center gap-3 mb-2">
                          {entry.profile_picture ? (
                            <img
                              src={entry.profile_picture}
                              alt={entry.username}
                              className="w-10 h-10 rounded-full object-cover"
                            />
                          ) : (
                            <div className={`w-10 h-10 rounded-full ${getAvatarColor(idx)} flex items-center justify-center text-white font-bold text-sm`}>
                              {entry.username.charAt(0).toUpperCase()}
                            </div>
                          )}
                          <div>
                            <div className="font-bold text-gray-900 truncate">{entry.username}</div>
                            <div className="text-xs text-gray-600 flex items-center gap-1">
                              <MapPin className="w-3 h-3" /> {entry.region}
                            </div>
                          </div>
                        </div>
                        <div className="grid grid-cols-2 gap-2 text-sm">
                          <div>
                            <div className="text-gray-600">Score</div>
                            <div className="font-bold text-lg text-blue-600">{entry.avg_score}</div>
                          </div>
                          <div>
                            <div className="text-gray-600">Interviews</div>
                            <div className="font-bold text-lg">{entry.interview_count}</div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Full Leaderboard Table */}
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50 border-b">
                    <tr>
                      <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Rank</th>
                      <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">User</th>
                      <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Region</th>
                      <th className="px-6 py-3 text-center text-sm font-semibold text-gray-900">Avg Score</th>
                      <th className="px-6 py-3 text-center text-sm font-semibold text-gray-900">Interviews</th>
                      <th className="px-6 py-3 text-center text-sm font-semibold text-gray-900">Percentile</th>
                    </tr>
                  </thead>
                  <tbody>
                    {leaderboardData.map((entry, idx) => (
                      <tr
                        key={`${entry.rank}-${entry.email}`}
                        className={`border-b hover:bg-gray-50 transition ${
                          idx < 3 ? 'bg-yellow-50 bg-opacity-30' : ''
                        }`}
                      >
                        <td className="px-6 py-4">
                          <div className="flex items-center gap-2">
                            <span className="text-xl">{getRankMedal(entry.rank) || `#${entry.rank}`}</span>
                            <span className="text-sm font-bold text-gray-700">{entry.rank}</span>
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          <div className="flex items-center gap-3">
                            {entry.profile_picture ? (
                              <img
                                src={entry.profile_picture}
                                alt={entry.username}
                                className="w-8 h-8 rounded-full object-cover"
                              />
                            ) : (
                              <div className="w-8 h-8 rounded-full bg-blue-500 flex items-center justify-center text-white font-bold text-sm">
                                {entry.username.charAt(0).toUpperCase()}
                              </div>
                            )}
                            <div>
                              <div className="font-semibold text-gray-900">{entry.username}</div>
                              <div className="text-xs text-gray-500">{entry.email}</div>
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          <div className="flex items-center gap-1 text-sm text-gray-600">
                            <MapPin className="w-4 h-4" />
                            {entry.region}
                          </div>
                        </td>
                        <td className="px-6 py-4 text-center">
                          <span className="font-bold text-blue-600 text-lg">{entry.avg_score}</span>
                        </td>
                        <td className="px-6 py-4 text-center">
                          <span className="font-semibold text-gray-900">{entry.interview_count}</span>
                        </td>
                        <td className="px-6 py-4 text-center">
                          <div className="flex items-center justify-center gap-1">
                            <TrendingUp className="w-4 h-4 text-green-600" />
                            <span className="font-semibold text-green-600">{entry.percentile}%</span>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Pagination */}
              {getTotalPages() > 1 && (
                <div className="flex items-center justify-between px-6 py-4 border-t bg-gray-50">
                  <button
                    onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                    disabled={currentPage === 1}
                    className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition"
                  >
                    ← Previous
                  </button>
                  <span className="text-sm text-gray-600 font-semibold">
                    Page {currentPage} of {getTotalPages()}
                  </span>
                  <button
                    onClick={() => setCurrentPage(Math.min(getTotalPages(), currentPage + 1))}
                    disabled={currentPage === getTotalPages()}
                    className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition"
                  >
                    Next →
                  </button>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default Leaderboard;
