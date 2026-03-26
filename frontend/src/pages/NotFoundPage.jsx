import React from 'react';
import { Link } from 'react-router-dom';

export const NotFoundPage = () => {
  return (
    <div className="min-h-screen flex items-center justify-center bg-bg px-4">
      <div className="text-center">
        <h1 className="text-8xl font-bold text-text mb-4">404</h1>
        <h2 className="text-2xl font-bold text-text mb-2">Page Not Found</h2>
        <p className="text-muted mb-8 text-sm">Sorry, the page you're looking for doesn't exist.</p>

        <div className="space-y-4">
          <Link
            to="/dashboard"
            className="inline-block px-6 py-2 bg-primary text-white font-semibold rounded-lg"
          >
            Go to Dashboard
          </Link>
          <p className="text-muted">or</p>
          <Link
            to="/"
            className="inline-block px-6 py-2 border border-border text-text font-semibold rounded-lg"
          >
            Return to Login
          </Link>
        </div>
      </div>
    </div>
  );
};
