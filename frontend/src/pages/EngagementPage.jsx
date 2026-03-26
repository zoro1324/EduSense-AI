import React from 'react';
import { MainLayout } from '../components/layout/MainLayout';
import { ChartCard } from '../components/common/Card';
import { StatusBadge } from '../components/common/Badge';
import { mockEngagementData } from '../data/mockData';

export const EngagementPage = () => {
  const { heatmapData, studentEngagementScores, attentionPercentage } = mockEngagementData;

  const isLowEngagement = attentionPercentage < 50;

  return (
    <MainLayout>
      <div className="max-w-7xl mx-auto">
        {/* Page Header */}
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-gray-900">Engagement Analytics</h2>
          <p className="text-gray-600 mt-1">Student engagement visualization and metrics</p>
        </div>

        {/* Alert Banner */}
        {isLowEngagement && (
          <div className="mb-8 bg-red-50 border border-red-200 rounded-lg p-4 flex items-start gap-3">
            <div className="text-red-600 mt-0.5">
              <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
            </div>
            <div>
              <h3 className="font-semibold text-red-900">Low Engagement Alert</h3>
              <p className="text-red-700 text-sm mt-1">Classroom engagement has fallen below 50%. Consider interactive activities or break time.</p>
            </div>
          </div>
        )}

        {/* Attention Overview */}
        <ChartCard title="Classroom Attention Overview" className="mb-8">
          <div className="flex items-center gap-8">
            <div className="flex-1">
              <div className="relative w-48 h-48 mx-auto">
                <svg className="w-full h-full transform -rotate-90" viewBox="0 0 200 200">
                  {/* Background circle */}
                  <circle
                    cx="100"
                    cy="100"
                    r="90"
                    fill="none"
                    stroke="#e5e7eb"
                    strokeWidth="20"
                  />
                  {/* Progress circle */}
                  <circle
                    cx="100"
                    cy="100"
                    r="90"
                    fill="none"
                    stroke="#3b82f6"
                    strokeWidth="20"
                    strokeDasharray={`${(attentionPercentage / 100) * (2 * Math.PI * 90)} ${2 * Math.PI * 90}`}
                    strokeLinecap="round"
                  />
                </svg>
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="text-center">
                    <p className="text-4xl font-bold text-blue-600">{attentionPercentage}%</p>
                    <p className="text-gray-600 text-sm">Attention Rate</p>
                  </div>
                </div>
              </div>
            </div>

            <div className="flex-1">
              <div className="space-y-4">
                <div>
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-gray-700 font-medium">Very High Focus</span>
                    <span className="text-sm text-gray-600">35%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div className="bg-green-500 h-2 rounded-full" style={{ width: '35%' }}></div>
                  </div>
                </div>

                <div>
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-gray-700 font-medium">Focus</span>
                    <span className="text-sm text-gray-600">38%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div className="bg-blue-500 h-2 rounded-full" style={{ width: '38%' }}></div>
                  </div>
                </div>

                <div>
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-gray-700 font-medium">Distracted</span>
                    <span className="text-sm text-gray-600">27%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div className="bg-yellow-500 h-2 rounded-full" style={{ width: '27%' }}></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </ChartCard>

        {/* Classroom Heatmap */}
        <ChartCard title="Classroom Engagement Heatmap" className="mb-8">
          <div className="space-y-4">
            {heatmapData.map((row, rowIdx) => (
              <div key={rowIdx}>
                <div className="flex items-center gap-4">
                  <span className="font-semibold text-gray-700 w-12">{row.row}</span>
                  <div className="flex gap-2 flex-1">
                    {[row.col1, row.col2, row.col3, row.col4, row.col5].map((value, colIdx) => {
                      let color = 'bg-red-100';
                      if (value >= 80) color = 'bg-green-100 border-green-300';
                      else if (value >= 60) color = 'bg-yellow-100 border-yellow-300';
                      else if (value >= 40) color = 'bg-orange-100 border-orange-300';

                      return (
                        <div
                          key={colIdx}
                          className={`flex-1 p-4 rounded-lg border text-center ${color} transition-all hover:shadow-md cursor-pointer`}
                        >
                          <p className="font-bold text-gray-900">{value}%</p>
                          <p className="text-xs text-gray-600">Seat {colIdx + 1}</p>
                        </div>
                      );
                    })}
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Legend */}
          <div className="mt-6 flex flex-wrap gap-4 justify-center text-sm">
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 bg-green-100 border border-green-300 rounded"></div>
              <span>High Engagement (80-100%)</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 bg-yellow-100 border border-yellow-300 rounded"></div>
              <span>Medium (60-79%)</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 bg-orange-100 border border-orange-300 rounded"></div>
              <span>Low (40-59%)</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 bg-red-100 border border-red-300 rounded"></div>
              <span>Very Low (&lt;40%)</span>
            </div>
          </div>
        </ChartCard>

        {/* Student Engagement Scores */}
        <ChartCard title="Individual Student Engagement Scores">
          <div className="space-y-4">
            {studentEngagementScores.map((student, idx) => (
              <div key={idx} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                <div className="flex-1">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-blue-600 text-white rounded-full flex items-center justify-center font-semibold text-sm">
                      {student.name.charAt(0)}
                    </div>
                    <div>
                      <p className="font-medium text-gray-900">{student.name}</p>
                      <p className="text-xs text-gray-500">ID: STU{String(idx + 1).padStart(3, '0')}</p>
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-4">
                  <div className="text-right">
                    <div className="w-32 bg-gray-200 rounded-full h-2">
                      <div
                        className={`h-2 rounded-full transition-all ${
                          student.score >= 80
                            ? 'bg-green-500'
                            : student.score >= 60
                            ? 'bg-yellow-500'
                            : 'bg-red-500'
                        }`}
                        style={{ width: `${student.score}%` }}
                      ></div>
                    </div>
                    <p className="text-sm font-bold text-gray-900 mt-1">{student.score}%</p>
                  </div>
                  <StatusBadge status={student.status} />
                </div>
              </div>
            ))}
          </div>
        </ChartCard>
      </div>
    </MainLayout>
  );
};
