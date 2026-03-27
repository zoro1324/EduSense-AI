import React, { useMemo, useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { Badge } from '../ui/UIPrimitives';
import { currentDateTime } from '../../data/appData';

const navItems = [
  { label: 'Dashboard', path: '/dashboard', icon: '▦' },
  { label: 'Academic Planner', path: '/academic', icon: '⌘' },
  { label: 'Live Attendance', path: '/attendance/live', icon: '📷' },
  { label: 'Attendance Records', path: '/attendance/records', icon: '📅' },
  { label: 'Engagement Monitor', path: '/engagement', icon: '📈' },
  { label: 'Safety Monitor', path: '/safety', icon: '🛡️' },
  { label: 'Student Registry', path: '/students', icon: '👥' },
  { label: 'Data Upload', path: '/upload', icon: '⤴' },
  { label: 'Leave Management', path: '/leave', icon: '📋' },
  { label: 'Marks & Results', path: '/marks', icon: '📊' },
  { label: 'Notifications', path: '/notifications', icon: '🔔' },
  { label: 'Reports', path: '/reports', icon: '◔' },
  { label: 'Settings', path: '/settings', icon: '⚙', adminOnly: true },
];

const pageMap = {
  '/dashboard': 'Dashboard',
  '/academic': 'Academic Planner',
  '/attendance/live': 'Live Attendance',
  '/attendance/records': 'Attendance Records',
  '/engagement': 'Engagement Monitor',
  '/safety': 'Safety Monitor',
  '/students': 'Student Registry',
  '/upload': 'Data Upload',
  '/leave': 'Leave Management',
  '/marks': 'Marks & Results',
  '/notifications': 'Notifications',
  '/reports': 'Reports',
  '/settings': 'Settings',
};

export const AppShell = ({ children }) => {
  const { user, logout, isPrincipal, managedClasses, userDisplayName } = useAuth();
  const location = useLocation();
  const [now, setNow] = useState(currentDateTime());
  const [collapsed, setCollapsed] = useState(false);

  React.useEffect(() => {
    const id = setInterval(() => setNow(currentDateTime()), 30000);
    return () => clearInterval(id);
  }, []);

  const nav = useMemo(() => navItems.filter((n) => !n.adminOnly || isPrincipal), [isPrincipal]);
  const scopeLabel = isPrincipal
    ? 'All Classes'
    : managedClasses.length
      ? managedClasses.join(', ')
      : 'No Class Assigned';

  return (
    <div className="h-screen bg-bg text-text flex">
      <aside className={`${collapsed ? 'md:w-20' : 'md:w-64'} w-64 bg-slate-900 border-r border-border hidden md:flex md:flex-col transition-all`}>
        <div className="p-4 border-b border-border flex items-center justify-between">
          <div className={`flex items-center gap-2 ${collapsed ? 'md:justify-center md:w-full' : ''}`}>
            <span className="text-xl">🧠</span>
            <div className={`${collapsed ? 'md:hidden' : ''}`}>
              <h2 className="font-semibold">EduSense AI</h2>
              <p className="text-xs text-muted">AI Driven School Management</p>
            </div>
          </div>
          <button onClick={() => setCollapsed((v) => !v)} className="text-muted text-xs">⇆</button>
        </div>

        <nav className="p-3 space-y-1 flex-1 overflow-y-auto thin-scrollbar">
          {nav.map((item) => {
            const active = location.pathname === item.path || (item.path === '/students' && location.pathname.startsWith('/students/'));
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center gap-3 px-3 py-2 rounded-lg transition ${active ? 'bg-primary text-white' : 'text-muted hover:bg-slate-800 hover:text-text'}`}
              >
                <span>{item.icon}</span>
                <span className={`${collapsed ? 'md:hidden' : ''}`}>{item.label}</span>
              </Link>
            );
          })}
        </nav>

        <div className="p-3 border-t border-border">
          <div className="bg-slate-800 rounded-lg px-3 py-2 flex items-center gap-2 mb-2">
            <div className="w-8 h-8 rounded-full bg-primary/40 flex items-center justify-center">{userDisplayName[0]}</div>
            <div className={`${collapsed ? 'md:hidden' : ''}`}>
              <p className="text-sm font-medium truncate">{userDisplayName}</p>
              <p className="text-xs text-muted">{user?.email}</p>
              <p className="text-[11px] text-muted truncate">Scope: {scopeLabel}</p>
            </div>
          </div>
          <button onClick={logout} className={`w-full px-3 py-2 rounded-lg bg-red-500/20 text-red-300 hover:bg-red-500/30 text-sm ${collapsed ? 'md:px-0' : ''}`}>
            {collapsed ? '⎋' : 'Logout'}
          </button>
        </div>
      </aside>

      <div className="flex-1 min-w-0 flex flex-col">
        <header className="h-16 border-b border-border bg-slate-900/90 backdrop-blur px-4 flex items-center justify-between">
          <div>
            <h1 className="font-semibold">{pageMap[location.pathname] || 'EduSense AI'}</h1>
            <p className="text-xs text-muted">{now}</p>
          </div>
          <div className="flex items-center gap-3">
            <button className="relative w-9 h-9 rounded-lg bg-slate-800 border border-border">🔔<span className="absolute -top-1 -right-1 text-[10px] bg-danger text-white rounded-full px-1">4</span></button>
            <div className="flex items-center gap-2 bg-slate-800 border border-border rounded-lg px-2 py-1">
              <div className="w-8 h-8 rounded-full bg-indigo-500/30 flex items-center justify-center">{userDisplayName[0]}</div>
              <div className="hidden sm:block">
                <p className="text-sm">{userDisplayName}</p>
                <div className="flex items-center gap-2">
                  <Badge tone={isPrincipal ? 'primary' : 'info'}>{user?.role}</Badge>
                  <Badge tone="warning">{isPrincipal ? 'All Classes' : `${managedClasses.length} class(es)`}</Badge>
                </div>
              </div>
            </div>
          </div>
        </header>
        <main className="flex-1 overflow-auto thin-scrollbar p-4 md:p-6">{children}</main>
      </div>
    </div>
  );
};
