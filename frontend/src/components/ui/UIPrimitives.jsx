import React from 'react';

export const PageContainer = ({ children }) => <div className="space-y-6">{children}</div>;

export const PageTitle = ({ title, subtitle }) => (
  <div className="flex items-center justify-between gap-3">
    <div>
      <h1 className="text-2xl font-semibold text-text">{title}</h1>
      {subtitle && <p className="text-sm text-muted mt-1">{subtitle}</p>}
    </div>
  </div>
);

export const Card = ({ children, className = '' }) => (
  <div className={`bg-card border border-border rounded-2xl shadow-card ${className}`}>{children}</div>
);

export const CardHeader = ({ title, right }) => (
  <div className="px-4 py-3 border-b border-border flex items-center justify-between gap-3">
    <h3 className="text-sm font-semibold text-text">{title}</h3>
    {right}
  </div>
);

export const CardBody = ({ children, className = '' }) => <div className={`p-4 ${className}`}>{children}</div>;

export const Badge = ({ children, tone = 'default' }) => {
  const styles = {
    default: 'bg-slate-700 text-slate-200',
    primary: 'bg-indigo-500/20 text-indigo-300 border border-indigo-500/30',
    success: 'bg-green-500/20 text-green-300 border border-green-500/30',
    danger: 'bg-red-500/20 text-red-300 border border-red-500/30',
    warning: 'bg-yellow-500/20 text-yellow-300 border border-yellow-500/30',
    info: 'bg-blue-500/20 text-blue-300 border border-blue-500/30',
  };
  return <span className={`inline-flex px-2 py-1 rounded-md text-xs font-medium ${styles[tone]}`}>{children}</span>;
};

export const Button = ({ children, variant = 'primary', className = '', loading = false, ...props }) => {
  const styles = {
    primary: 'bg-primary hover:bg-indigo-400 text-white',
    danger: 'bg-danger hover:bg-red-400 text-white',
    success: 'bg-success hover:bg-green-400 text-white',
    warning: 'bg-warning hover:bg-yellow-400 text-slate-900',
    ghost: 'bg-slate-700 hover:bg-slate-600 text-slate-100',
    outline: 'border border-border bg-transparent hover:bg-slate-800 text-slate-100',
  };
  return (
    <button className={`px-3 py-2 rounded-lg text-sm font-medium transition inline-flex items-center justify-center gap-2 disabled:opacity-60 ${styles[variant]} ${className}`} {...props}>
      {loading ? <span className="w-4 h-4 rounded-full border-2 border-white/40 border-t-white animate-spin" /> : null}
      {children}
    </button>
  );
};

export const Input = ({ className = '', ...props }) => (
  <input
    className={`w-full bg-slate-900 border border-border text-text rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 ${className}`}
    {...props}
  />
);

export const Select = ({ className = '', children, ...props }) => (
  <select
    className={`w-full bg-slate-900 border border-border text-text rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 ${className}`}
    {...props}
  >
    {children}
  </select>
);

export const TextArea = ({ className = '', ...props }) => (
  <textarea
    className={`w-full bg-slate-900 border border-border text-text rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 ${className}`}
    {...props}
  />
);

export const EmptyState = ({ title = 'No data', subtitle = 'Nothing to show here yet.' }) => (
  <div className="p-10 text-center text-muted">
    <div className="text-3xl mb-2">🗂️</div>
    <h4 className="text-text font-medium">{title}</h4>
    <p className="text-sm mt-1">{subtitle}</p>
  </div>
);

export const Skeleton = ({ className = '' }) => <div className={`animate-pulse bg-slate-700/70 rounded-lg ${className}`} />;
