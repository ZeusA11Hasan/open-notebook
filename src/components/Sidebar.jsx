import React, { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import '../styles/Sidebar.css';

const Sidebar = () => {
  const [collapsed, setCollapsed] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuth();

  const menuItems = [
    { id: 'dashboard', icon: '📒', label: 'Dashboard', path: '/' },
    { id: 'search', icon: '🔍', label: 'Search', path: '/search' },
    { id: 'podcasts', icon: '🎙️', label: 'Podcasts', path: '/podcasts' },
    { id: 'models', icon: '🤖', label: 'Models', path: '/models' },
    { id: 'transformations', icon: '💱', label: 'Transformations', path: '/transformations' },
    { id: 'settings', icon: '⚙️', label: 'Settings', path: '/settings' },
  ];

  const isActive = (path) => {
    if (path === '/') {
      return location.pathname === '/';
    }
    return location.pathname.startsWith(path);
  };

  return (
    <aside className={`sidebar ${collapsed ? 'collapsed' : ''}`}>
      <div className="sidebar-toggle" onClick={() => setCollapsed(!collapsed)}>
        <span className="toggle-icon">⚡</span>
      </div>
      
      <div className="sidebar-content">
        {/* Logo Section */}
        <div className="sidebar-logo">
          <div className="logo-icon">📒</div>
          {!collapsed && <span className="logo-text">Open Notebook</span>}
        </div>

        {/* Navigation */}
        <nav className="sidebar-nav">
          <div className="nav-section">
            {menuItems.map(item => (
              <div
                key={item.id}
                className={`sidebar-item ${isActive(item.path) ? 'active' : ''}`}
                onClick={() => navigate(item.path)}
              >
                <span className="sidebar-icon">{item.icon}</span>
                {!collapsed && <span className="sidebar-label">{item.label}</span>}
                {isActive(item.path) && <div className="active-indicator" />}
              </div>
            ))}
          </div>
        </nav>

        {/* User Section */}
        <div className="sidebar-footer">
          {user && (
            <div className="user-section">
              <div className="user-avatar">
                <span>{user.name?.charAt(0) || 'U'}</span>
              </div>
              {!collapsed && (
                <div className="user-info">
                  <div className="user-name">{user.name || 'User'}</div>
                  <div className="user-status">Online</div>
                </div>
              )}
              <button 
                className="logout-btn"
                onClick={logout}
                title="Logout"
              >
                🚪
              </button>
            </div>
          )}
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;