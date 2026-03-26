import React, { createContext, useState, useContext, useMemo } from 'react';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [token, setToken] = useState(localStorage.getItem('edusense_token') || '');
  const [user, setUser] = useState(() => {
    const raw = localStorage.getItem('edusense_user');
    return raw ? JSON.parse(raw) : null;
  });

  const login = (email, password, role) => {
    if (email && password) {
      const fakeToken = `jwt_${Date.now()}`;
      const nextUser = {
        email,
        name: email.split('@')[0].replace('.', ' ').toUpperCase(),
        role,
      };
      setToken(fakeToken);
      setUser(nextUser);
      localStorage.setItem('edusense_token', fakeToken);
      localStorage.setItem('edusense_user', JSON.stringify(nextUser));
      return true;
    }
    return false;
  };

  const logout = () => {
    setToken('');
    setUser(null);
    localStorage.removeItem('edusense_token');
    localStorage.removeItem('edusense_user');
  };

  const isLoggedIn = Boolean(token);
  const isAdmin = user?.role === 'Admin';

  const value = useMemo(
    () => ({ isLoggedIn, token, user, isAdmin, login, logout }),
    [isLoggedIn, token, user, isAdmin]
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
