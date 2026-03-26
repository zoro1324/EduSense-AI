import React from 'react';
import { MainLayout } from '../components/layout/MainLayout';
import { ChartCard } from '../components/common/Card';
import { mockParticipationData } from '../data/mockData';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

export const ParticipationPage = () => {
  const { participationList, leaderboard, participationTrend } = mockParticipationData;

  return (
    <MainLayout>
      <div className="max-w-7xl mx-auto">
        {/* Page Header */}
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-gray-900">Participation Insights</h2>
          <p className="text-gray-600 mt-1">Student participation behavior and leaderboard</p>
        </div>

        {/* Participation Trend */}
        <ChartCard title="Participation Trend" className="mb-8">
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={participationTrend}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis dataKey="time" />
              <YAxis />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#fff',
                  border: '1px solid #e5e7eb',
                  borderRadius: '8px',
                }}
              />
              <Legend />
              <Line
                type="monotone"
                dataKey="count"
                stroke="#8b5cf6"
                strokeWidth={2}
                dot={{ fill: '#8b5cf6', r: 4 }}
                activeDot={{ r: 6 }}
                name="Active Participants"
              />
            </LineChart>
          </ResponsiveContainer>
        </ChartCard>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8">
          {/* Leaderboard */}
          <ChartCard title="Participation Leaderboard" className="lg:col-span-1">
            <div className="space-y-3">
              {leaderboard.map((entry) => (
                <div
                  key={entry.rank}
                  className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <div
                      className={`w-10 h-10 rounded-full flex items-center justify-center text-white font-bold text-sm ${
                        entry.rank === 1
                          ? 'bg-yellow-500'
                          : entry.rank === 2
                          ? 'bg-gray-400'
                          : entry.rank === 3
                          ? 'bg-orange-500'
                          : 'bg-blue-500'
                      }`}
                    >
                      {entry.rank}
                    </div>
                    <div>
                      <p className="font-medium text-gray-900 text-sm">{entry.name}</p>
                      <p className="text-xs text-gray-500">{entry.points} points</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="font-bold text-gray-900 text-lg">{entry.points}</p>
                  </div>
                </div>
              ))}
            </div>
          </ChartCard>

          {/* Recent Participation */}
          <ChartCard title="Recent Participation Activity" className="lg:col-span-2">
            <div className="space-y-3">
              {participationList.map((entry) => (
                <div
                  key={entry.id}
                  className="flex items-start gap-4 p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                >
                  <div className="w-10 h-10 bg-blue-600 text-white rounded-full flex items-center justify-center font-semibold text-sm flex-shrink-0 mt-1">
                    {entry.studentName.charAt(0)}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center justify-between">
                      <p className="font-medium text-gray-900">{entry.studentName}</p>
                      <span className="text-xs text-gray-500">{entry.timestamp}</span>
                    </div>
                    <div className="flex items-center gap-2 mt-2">
                      <span
                        className={`inline-flex items-center px-2 py-1 rounded text-xs font-medium ${
                          entry.participationType === 'Hand Raise'
                            ? 'bg-blue-100 text-blue-800'
                            : entry.participationType === 'Verbal Response'
                            ? 'bg-green-100 text-green-800'
                            : entry.participationType === 'Question Asked'
                            ? 'bg-purple-100 text-purple-800'
                            : 'bg-gray-100 text-gray-800'
                        }`}
                      >
                        {entry.participationType}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </ChartCard>
        </div>

        {/* Participation Summary */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <ChartCard title="Participation Summary">
            <div className="space-y-4">
              <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
                <p className="text-sm text-gray-600">Total Participation Events</p>
                <p className="text-3xl font-bold text-blue-600 mt-2">{participationList.length}</p>
              </div>
              <div className="p-4 bg-green-50 rounded-lg border border-green-200">
                <p className="text-sm text-gray-600">Active Participants</p>
                <p className="text-3xl font-bold text-green-600 mt-2">{leaderboard.length}</p>
              </div>
              <div className="p-4 bg-purple-50 rounded-lg border border-purple-200">
                <p className="text-sm text-gray-600">Response Rate</p>
                <p className="text-3xl font-bold text-purple-600 mt-2">65%</p>
              </div>
            </div>
          </ChartCard>

          {/* Participation Types */}
          <ChartCard title="Participation Types">
            <div className="space-y-4">
              <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <span className="text-sm text-gray-700">Hand Raises</span>
                <span className="font-bold text-gray-900">8</span>
              </div>
              <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <span className="text-sm text-gray-700">Verbal Responses</span>
                <span className="font-bold text-gray-900">6</span>
              </div>
              <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <span className="text-sm text-gray-700">Questions Asked</span>
                <span className="font-bold text-gray-900">4</span>
              </div>
              <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <span className="text-sm text-gray-700">Comments</span>
                <span className="font-bold text-gray-900">3</span>
              </div>
            </div>
          </ChartCard>

          {/* Participation Quality */}
          <ChartCard title="Top Participants">
            <div className="space-y-3">
              {leaderboard.slice(0, 3).map((student) => (
                <div key={student.rank} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center gap-2">
                    <div className={`w-6 h-6 rounded-full flex items-center justify-center text-white font-bold text-xs ${
                      student.rank === 1
                        ? 'bg-yellow-500'
                        : student.rank === 2
                        ? 'bg-gray-400'
                        : 'bg-orange-500'
                    }`}>
                      {student.rank}
                    </div>
                    <span className="font-medium text-gray-900 text-sm">{student.name.split(' ')[0]}</span>
                  </div>
                  <span className="font-bold text-gray-900">{student.points}</span>
                </div>
              ))}
            </div>
          </ChartCard>
        </div>
      </div>
    </MainLayout>
  );
};
