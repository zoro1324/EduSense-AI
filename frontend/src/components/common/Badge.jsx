import React from 'react';

export const StatusBadge = ({ status, className = '' }) => {
  const getStyles = (status) => {
    switch (status.toLowerCase()) {
      case 'present':
        return 'bg-green-100 text-green-800';
      case 'absent':
        return 'bg-red-100 text-red-800';
      case 'late':
        return 'bg-yellow-100 text-yellow-800';
      case 'verified':
        return 'bg-blue-100 text-blue-800';
      case 'not detected':
        return 'bg-gray-100 text-gray-800';
      case 'high':
        return 'bg-green-100 text-green-800';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800';
      case 'low':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getStyles(status)} ${className}`}>
      {status}
    </span>
  );
};

export const AlertBadge = ({ type, className = '' }) => {
  const getStyles = (type) => {
    switch (type.toLowerCase()) {
      case 'danger':
        return 'bg-red-100 text-red-800 border border-red-300';
      case 'warning':
        return 'bg-yellow-100 text-yellow-800 border border-yellow-300';
      case 'success':
        return 'bg-green-100 text-green-800 border border-green-300';
      case 'info':
        return 'bg-blue-100 text-blue-800 border border-blue-300';
      default:
        return 'bg-gray-100 text-gray-800 border border-gray-300';
    }
  };

  return (
    <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getStyles(type)} ${className}`}>
      {type}
    </span>
  );
};
