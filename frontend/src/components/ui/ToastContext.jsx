import React, { createContext, useCallback, useContext, useMemo, useState } from 'react';

const ToastContext = createContext();

export const ToastProvider = ({ children }) => {
  const [toasts, setToasts] = useState([]);

  const pushToast = useCallback((message, type = 'success') => {
    const id = Date.now() + Math.random();
    setToasts((prev) => [...prev, { id, message, type }]);
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 3000);
  }, []);

  const value = useMemo(() => ({ pushToast }), [pushToast]);

  return (
    <ToastContext.Provider value={value}>
      {children}
      <div className="fixed top-4 right-4 z-[120] space-y-2">
        {toasts.map((toast) => {
          const tone = {
            success: 'bg-green-500/20 border-green-500/40 text-green-200',
            error: 'bg-red-500/20 border-red-500/40 text-red-200',
            warning: 'bg-yellow-500/20 border-yellow-500/40 text-yellow-200',
          }[toast.type] || 'bg-slate-700 text-slate-100 border-border';
          return (
            <div key={toast.id} className={`min-w-[260px] px-3 py-2 rounded-lg border text-sm backdrop-blur ${tone}`}>
              {toast.message}
            </div>
          );
        })}
      </div>
    </ToastContext.Provider>
  );
};

export const useToast = () => {
  const ctx = useContext(ToastContext);
  if (!ctx) throw new Error('useToast must be used within ToastProvider');
  return ctx;
};
