import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import '../styles/AuthGuard.css';

const AuthGuard = ({ children }) => {
  const { isAuthenticated, loading, login } = useAuth();
  const [password, setPassword] = useState('');
  const [loginError, setLoginError] = useState('');
  const [isLoggingIn, setIsLoggingIn] = useState(false);

  // Check if password protection is enabled
  const [needsAuth, setNeedsAuth] = useState(null);

  React.useEffect(() => {
    const checkAuthRequired = async () => {
      try {
        const response = await fetch('/api/health');
        if (response.status === 401) {
          setNeedsAuth(true);
        } else {
          setNeedsAuth(false);
        }
      } catch (error) {
        // If we can't reach the API, assume auth is needed
        setNeedsAuth(true);
      }
    };

    if (needsAuth === null) {
      checkAuthRequired();
    }
  }, [needsAuth]);

  const handleLogin = async (e) => {
    e.preventDefault();
    setIsLoggingIn(true);
    setLoginError('');

    try {
      const success = await login(password);
      if (!success) {
        setLoginError('Invalid password. Please try again.');
      }
    } catch (error) {
      setLoginError('Authentication failed. Please try again.');
    } finally {
      setIsLoggingIn(false);
    }
  };

  if (loading || needsAuth === null) {
    return (
      <div className="auth-loading">
        <div className="loading-spinner"></div>
        <p>Loading Open Notebook...</p>
      </div>
    );
  }

  // If no auth is needed, show the app
  if (needsAuth === false) {
    return children;
  }

  // If auth is needed but user is not authenticated, show login
  if (!isAuthenticated) {
    return (
      <div className="auth-container">
        <div className="auth-background">
          <div className="animated-bg"></div>
          <div className="particles-container">
            {Array.from({ length: 30 }).map((_, i) => (
              <div 
                key={i} 
                className="particle"
                style={{
                  left: `${Math.random() * 100}%`,
                  top: `${Math.random() * 100}%`,
                  animationDelay: `${Math.random() * 6}s`,
                  width: `${Math.random() * 3 + 1}px`,
                  height: `${Math.random() * 3 + 1}px`
                }}
              />
            ))}
          </div>
        </div>

        <div className="auth-card">
          <div className="auth-header">
            <div className="auth-logo">
              <span className="logo-icon">📒</span>
              <span className="logo-text">Open Notebook</span>
            </div>
            <h2>Authentication Required</h2>
            <p>This Open Notebook instance is password protected.</p>
          </div>

          <form onSubmit={handleLogin} className="auth-form">
            <div className="form-group">
              <label htmlFor="password">Password</label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter password"
                required
                autoFocus
              />
            </div>

            {loginError && (
              <div className="auth-error">
                {loginError}
              </div>
            )}

            <button 
              type="submit" 
              className="btn-primary auth-submit"
              disabled={!password || isLoggingIn}
            >
              {isLoggingIn ? (
                <>
                  <span className="loading-spinner"></span>
                  Authenticating...
                </>
              ) : (
                'Login'
              )}
            </button>
          </form>
        </div>
      </div>
    );
  }

  // User is authenticated, show the app
  return children;
};

export default AuthGuard;