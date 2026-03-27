import React, { createContext, useEffect, useState, useContext, useMemo } from 'react';

import { api } from '../lib/api';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [token, setToken] = useState(localStorage.getItem('edusense_token') || '');
  const [refreshToken, setRefreshToken] = useState(localStorage.getItem('edusense_refresh') || '');
  const [user, setUser] = useState(() => {
    const raw = localStorage.getItem('edusense_user');
    return raw ? JSON.parse(raw) : null;
  });
  const [authLoading, setAuthLoading] = useState(false);

  const login = async (email, password) => {
    setAuthLoading(true);
    try {
      const data = await api.post('/auth/login/', { email, password });
      const nextToken = data?.access || '';
      const nextRefresh = data?.refresh || '';
      const nextUser = data?.user || null;

      if (!nextToken || !nextUser) {
        return { ok: false, error: 'Invalid login response from server' };
      }

      setToken(nextToken);
      setRefreshToken(nextRefresh);
      setUser(nextUser);
      localStorage.setItem('edusense_token', nextToken);
      if (nextRefresh) {
        localStorage.setItem('edusense_refresh', nextRefresh);
      }
      localStorage.setItem('edusense_user', JSON.stringify(nextUser));
      return { ok: true };
    } catch (error) {
      return { ok: false, error: error.message || 'Login failed' };
    } finally {
      setAuthLoading(false);
    }
  };

  const logout = async () => {
    try {
      await api.post('/auth/logout/', { refresh: refreshToken || undefined });
    } catch (error) {
      // Local cleanup still proceeds even when backend logout fails.
    }
    setToken('');
    setRefreshToken('');
    setUser(null);
    localStorage.removeItem('edusense_token');
    localStorage.removeItem('edusense_refresh');
    localStorage.removeItem('edusense_user');
  };

  useEffect(() => {
    const syncCurrentUser = async () => {
      if (!token) {
        return;
      }
      try {
        const me = await api.get('/auth/me/');
        setUser(me);
        localStorage.setItem('edusense_user', JSON.stringify(me));
      } catch (error) {
        setToken('');
        setRefreshToken('');
        setUser(null);
        localStorage.removeItem('edusense_token');
        localStorage.removeItem('edusense_refresh');
        localStorage.removeItem('edusense_user');
      }
    };

    syncCurrentUser();
  }, [token]);

  const isLoggedIn = Boolean(token);
  const managedClasses = Array.isArray(user?.managed_classes) ? user.managed_classes : [];
  const isPrincipal = ['principal', 'admin'].includes(user?.role || '');
  const isIncharge = !isPrincipal && managedClasses.length > 0;
  const userDisplayName =
    [user?.first_name, user?.last_name].filter(Boolean).join(' ') || user?.username || user?.email || 'User';
  const isAdmin = isPrincipal;

  const value = useMemo(
    () => ({
      isLoggedIn,
      token,
      user,
      isAdmin,
      isPrincipal,
      isIncharge,
      managedClasses,
      userDisplayName,
      authLoading,
      login,
      logout,
    }),
    [isLoggedIn, token, user, isAdmin, isPrincipal, isIncharge, managedClasses, userDisplayName, authLoading]
  );

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};
