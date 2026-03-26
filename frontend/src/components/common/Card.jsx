import React from 'react';

export const Card = ({ title, value, icon: Icon, color = 'blue', subtitle = '', className = '' }) => {
  const getColorStyles = (color) => {
    switch (color) {
      case 'green':
        return 'bg-green-50 border-green-200 text-green-600';
      case 'red':
        return 'bg-red-50 border-red-200 text-red-600';
      case 'yellow':
        return 'bg-yellow-50 border-yellow-200 text-yellow-600';
      case 'purple':
        return 'bg-purple-50 border-purple-200 text-purple-600';
      default:
        return 'bg-blue-50 border-blue-200 text-blue-600';
    }
  };

  return (
    <div className={`bg-white rounded-lg border ${getColorStyles(color)} p-6 shadow-card hover:shadow-hover transition-shadow duration-300 ${className}`}>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-gray-600 text-sm font-medium">{title}</p>
          <p className="text-3xl font-bold text-gray-900 mt-2">{value}</p>
          {subtitle && <p className="text-gray-500 text-xs mt-1">{subtitle}</p>}
        </div>
        {Icon && <Icon className="w-12 h-12 opacity-20" />}
      </div>
    </div>
  );
};

export const ChartCard = ({ title, children, className = '' }) => {
  return (
    <div className={`bg-white rounded-lg border border-gray-200 p-6 shadow-card ${className}`}>
      <h3 className="text-lg font-semibold text-gray-900 mb-4">{title}</h3>
      <div className="w-full overflow-x-auto">
        {children}
      </div>
    </div>
  );
};
