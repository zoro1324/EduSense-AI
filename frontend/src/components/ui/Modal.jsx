import React from 'react';

export const Modal = ({ isOpen, onClose, title, children, width = 'max-w-xl' }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/70 animate-[fadein_0.2s_ease-out]" onClick={onClose}>
      <div className={`w-full ${width} bg-card border border-border rounded-2xl shadow-hover`} onClick={(e) => e.stopPropagation()}>
        <div className="px-4 py-3 border-b border-border flex items-center justify-between">
          <h3 className="text-text font-semibold">{title}</h3>
          <button onClick={onClose} className="text-muted hover:text-text">✕</button>
        </div>
        <div className="p-4">{children}</div>
      </div>
    </div>
  );
};
