import React, { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    // Check for existing authentication
    const checkAuth = async () => {
      try {
        const token = localStorage.getItem('auth_token');
        const password = localStorage.getItem('app_password');
        
        if (token || password) {
          // Verify token/password with API
          const response = await fetch('/api/health', {
            headers: password ? { 'Authorization': `Bearer ${password}` } : {}
          });
          
          if (response.ok) {
            setUser({ name: 'User', authenticated: true });
            setIsAuthenticated(true);
          } else {
            localStorage.removeItem('auth_token');
            localStorage.removeItem('app_password');
          }
        }
      } catch (error) {
        console.error('Auth check failed:', error);
      } finally {
        setLoading(false);
      }
    };

    checkAuth();
  }, []);

  const login = async (password) => {
    try {
      // Test authentication with the API
      const response = await fetch('/api/health', {
        headers: { 'Authorization': `Bearer ${password}` }
      });

      if (response.ok) {
        localStorage.setItem('app_password', password);
        setUser({ name: 'User', authenticated: true });
        setIsAuthenticated(true);
        return true;
      } else {
        throw new Error('Invalid password');
      }
    } catch (error) {
      console.error('Login failed:', error);
      return false;
    }
  };

  const logout = () => {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('app_password');
    setUser(null);
    setIsAuthenticated(false);
  };

  const value = {
    user,
    loading,
    isAuthenticated,
    login,
    logout
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};