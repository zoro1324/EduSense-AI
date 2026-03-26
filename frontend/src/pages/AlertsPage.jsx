import React, { useState } from 'react';
import { MainLayout } from '../components/layout/MainLayout';
import { ChartCard } from '../components/common/Card';
import { AlertBadge } from '../components/common/Badge';
import { mockAlerts } from '../data/mockData';

export const AlertsPage = () => {
  const [alerts, setAlerts] = useState(mockAlerts);
  const [filter, setFilter] = useState('all');

  const filteredAlerts = filter === 'all' ? alerts : alerts.filter((a) => a.type === filter);

  const alertCounts = {
    all: alerts.length,
    danger: alerts.filter((a) => a.type === 'danger').length,
    warning: alerts.filter((a) => a.type === 'warning').length,
    success: alerts.filter((a) => a.type === 'success').length,
    info: alerts.filter((a) => a.type === 'info').length,
  };

  const dismissAlert = (id) => {
    setAlerts(alerts.filter((a) => a.id !== id));
  };

  return (
    <MainLayout>
      <div className="max-w-4xl mx-auto">
        {/* Page Header */}
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-gray-900">Alerts & Notifications</h2>
          <p className="text-gray-600 mt-1">Real-time classroom alerts and notifications</p>
        </div>

        {/* Alert Summary */}
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-8">
          <button
            onClick={() => setFilter('all')}
            className={`p-4 rounded-lg border-2 transition-all ${
              filter === 'all'
                ? 'bg-blue-50 border-blue-300 text-blue-900'
                : 'bg-white border-gray-200 text-gray-700 hover:border-gray-300'
            }`}
          >
            <p className="text-2xl font-bold">{alertCounts.all}</p>
            <p className="text-xs mt-1">All Alerts</p>
          </button>

          <button
            onClick={() => setFilter('danger')}
            className={`p-4 rounded-lg border-2 transition-all ${
              filter === 'danger'
                ? 'bg-red-50 border-red-300 text-red-900'
                : 'bg-white border-gray-200 text-gray-700 hover:border-gray-300'
            }`}
          >
            <p className="text-2xl font-bold">{alertCounts.danger}</p>
            <p className="text-xs mt-1">Critical</p>
          </button>

          <button
            onClick={() => setFilter('warning')}
            className={`p-4 rounded-lg border-2 transition-all ${
              filter === 'warning'
                ? 'bg-yellow-50 border-yellow-300 text-yellow-900'
                : 'bg-white border-gray-200 text-gray-700 hover:border-gray-300'
            }`}
          >
            <p className="text-2xl font-bold">{alertCounts.warning}</p>
            <p className="text-xs mt-1">Warning</p>
          </button>

          <button
            onClick={() => setFilter('success')}
            className={`p-4 rounded-lg border-2 transition-all ${
              filter === 'success'
                ? 'bg-green-50 border-green-300 text-green-900'
                : 'bg-white border-gray-200 text-gray-700 hover:border-gray-300'
            }`}
          >
            <p className="text-2xl font-bold">{alertCounts.success}</p>
            <p className="text-xs mt-1">Success</p>
          </button>

          <button
            onClick={() => setFilter('info')}
            className={`p-4 rounded-lg border-2 transition-all ${
              filter === 'info'
                ? 'bg-blue-50 border-blue-300 text-blue-900'
                : 'bg-white border-gray-200 text-gray-700 hover:border-gray-300'
            }`}
          >
            <p className="text-2xl font-bold">{alertCounts.info}</p>
            <p className="text-xs mt-1">Info</p>
          </button>
        </div>

        {/* Alerts List */}
        <ChartCard title="Alert Feed">
          {filteredAlerts.length === 0 ? (
            <div className="text-center py-12">
              <div className="mb-4">
                <svg
                  className="w-16 h-16 mx-auto text-gray-400"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
              </div>
              <p className="text-gray-600 font-medium">No alerts to display</p>
              <p className="text-gray-500 text-sm mt-1">Great job! No issues detected.</p>
            </div>
          ) : (
            <div className="space-y-4">
              {filteredAlerts.map((alert) => {
                const getIconColor = (type) => {
                  switch (type.toLowerCase()) {
                    case 'danger':
                      return 'text-red-600';
                    case 'warning':
                      return 'text-yellow-600';
                    case 'success':
                      return 'text-green-600';
                    case 'info':
                      return 'text-blue-600';
                    default:
                      return 'text-gray-600';
                  }
                };

                const getBgColor = (type) => {
                  switch (type.toLowerCase()) {
                    case 'danger':
                      return 'bg-red-50 border-red-200';
                    case 'warning':
                      return 'bg-yellow-50 border-yellow-200';
                    case 'success':
                      return 'bg-green-50 border-green-200';
                    case 'info':
                      return 'bg-blue-50 border-blue-200';
                    default:
                      return 'bg-gray-50 border-gray-200';
                  }
                };

                const getIcon = (type) => {
                  switch (type.toLowerCase()) {
                    case 'danger':
                      return (
                        <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                        </svg>
                      );
                    case 'warning':
                      return (
                        <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                        </svg>
                      );
                    case 'success':
                      return (
                        <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                      );
                    default:
                      return (
                        <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M18 5v8a2 2 0 01-2 2h-5l-5 4v-4H4a2 2 0 01-2-2V5a2 2 0 012-2h12a2 2 0 012 2zm-11-1a1 1 0 11-2 0 1 1 0 012 0zm6 0a1 1 0 11-2 0 1 1 0 012 0z" clipRule="evenodd" />
                        </svg>
                      );
                  }
                };

                return (
                  <div
                    key={alert.id}
                    className={`flex items-start gap-4 p-4 rounded-lg border ${getBgColor(alert.type)} hover:shadow-md transition-all`}
                  >
                    <div className={`flex-shrink-0 ${getIconColor(alert.type)} mt-0.5`}>
                      {getIcon(alert.type)}
                    </div>

                    <div className="flex-1">
                      <div className="flex items-start justify-between">
                        <div>
                          <h3 className="font-semibold text-gray-900">{alert.title}</h3>
                          <p className="text-gray-600 text-sm mt-1">{alert.message}</p>
                        </div>
                        <span className="text-xs text-gray-500 flex-shrink-0">{alert.timestamp}</span>
                      </div>

                      <div className="flex items-center gap-3 mt-3">
                        <AlertBadge type={alert.type} />
                        {['danger', 'warning'].includes(alert.type) && (
                          <button className="text-xs px-3 py-1 bg-white rounded border border-gray-300 text-gray-700 hover:bg-gray-50 transition-colors">
                            Take Action
                          </button>
                        )}
                      </div>
                    </div>

                    <button
                      onClick={() => dismissAlert(alert.id)}
                      className="flex-shrink-0 text-gray-400 hover:text-gray-600 transition-colors"
                    >
                      <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                      </svg>
                    </button>
                  </div>
                );
              })}
            </div>
          )}
        </ChartCard>
      </div>
    </MainLayout>
  );
};
