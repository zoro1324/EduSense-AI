import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export const ProtectedRoute = ({ children, adminOnly = false }) => {
  const { isLoggedIn, isPrincipal } = useAuth();

  if (!isLoggedIn) {
    return <Navigate to="/" replace />;
  }

  if (adminOnly && !isPrincipal) {
    return <Navigate to="/dashboard" replace />;
  }

  return children;
};
