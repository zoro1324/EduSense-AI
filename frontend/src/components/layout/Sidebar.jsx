import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { IconMenu, IconX } from '../common/Icons';

const MenuItem = ({ icon: Icon, label, path, isActive }) => (
  <Link
    to={path}
    className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200 ${
      isActive
        ? 'bg-blue-600 text-white shadow-md'
        : 'text-gray-700 hover:bg-gray-100'
    }`}
  >
    <Icon className="w-5 h-5" />
    <span className="font-medium">{label}</span>
  </Link>
);

export const Sidebar = ({ isOpen, onClose }) => {
  const menuItems = [
    { icon: DashboardIcon, label: 'Dashboard', path: '/dashboard' },
    { icon: AttendanceIcon, label: 'Attendance', path: '/attendance' },
    { icon: EngagementIcon, label: 'Engagement Analytics', path: '/engagement' },
    { icon: ParticipationIcon, label: 'Participation Insights', path: '/participation' },
    { icon: AlertIcon, label: 'Alerts', path: '/alerts' },
    { icon: SettingsIcon, label: 'Settings', path: '/settings' },
  ];

  const currentPath = window.location.pathname;

  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 md:hidden z-30"
          onClick={onClose}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`fixed left-0 top-0 h-screen w-64 bg-white border-r border-gray-200 overflow-y-auto transition-transform duration-300 z-40 md:translate-x-0 ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <div className="p-6">
          <h1 className="text-2xl font-bold text-blue-600">EduSense AI</h1>
          <p className="text-xs text-gray-500 mt-1">Classroom Intelligence</p>
        </div>

        {/* Close button for mobile */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 md:hidden text-gray-500 hover:text-gray-700"
        >
          <IconX className="w-6 h-6" />
        </button>

        {/* Menu items */}
        <nav className="space-y-2 px-4 mt-8">
          {menuItems.map((item) => (
            <MenuItem
              key={item.path}
              {...item}
              isActive={currentPath === item.path}
            />
          ))}
        </nav>

        {/* Footer info */}
        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-gray-200 bg-gray-50">
          <p className="text-xs text-gray-500">EduSense AI v1.0</p>
        </div>
      </aside>
    </>
  );
};

// Simple menu icons
const DashboardIcon = (props) => (
  <svg {...props} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-3m2 3l2-3m2 3l2-3m2 3l2-3m2 3l2-3M3 20l2-3m2 3l2-3m2 3l2-3m2 3l2-3m2 3l2-3M3 7l2-3m2 3l2-3m2 3l2-3m2 3l2-3m2 3l2-3" />
  </svg>
);

const AttendanceIcon = (props) => (
  <svg {...props} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
  </svg>
);

const EngagementIcon = (props) => (
  <svg {...props} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8L5.757 18.243M1 11v11a2 2 0 002 2h18a2 2 0 002-2v-5" />
  </svg>
);

const ParticipationIcon = (props) => (
  <svg {...props} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.856-1.487M15 10a3 3 0 11-6 0 3 3 0 016 0zM6.5 20H7a4 4 0 014-4h.5" />
  </svg>
);

const AlertIcon = (props) => (
  <svg {...props} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4v.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
  </svg>
);

const SettingsIcon = (props) => (
  <svg {...props} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
  </svg>
);
