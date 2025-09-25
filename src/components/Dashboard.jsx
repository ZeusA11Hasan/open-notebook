import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useNotebooks } from '../contexts/NotebookContext';
import { useAuth } from '../contexts/AuthContext';
import StatsCard from './StatsCard';
import NotebookCard from './NotebookCard';
import ActivityFeed from './ActivityFeed';
import CreateNotebookModal from './CreateNotebookModal';
import QuickActions from './QuickActions';
import '../styles/Dashboard.css';

const Dashboard = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const { 
    notebooks, 
    loading, 
    createNotebook, 
    deleteNotebook,
    updateNotebook,
    refreshNotebooks 
  } = useNotebooks();
  
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [stats, setStats] = useState({
    activeNotebooks: 0,
    totalSources: 0,
    aiInsights: 0,
    podcastsGenerated: 0
  });

  // Calculate stats from notebooks data
  useEffect(() => {
    if (notebooks.length > 0) {
      const activeNotebooks = notebooks.filter(nb => !nb.archived).length;
      const totalSources = notebooks.reduce((sum, nb) => sum + (nb.sourcesCount || 0), 0);
      const aiInsights = notebooks.reduce((sum, nb) => sum + (nb.insightsCount || 0), 0);
      const podcastsGenerated = notebooks.reduce((sum, nb) => sum + (nb.podcastsCount || 0), 0);
      
      setStats({
        activeNotebooks,
        totalSources,
        aiInsights,
        podcastsGenerated
      });
    }
  }, [notebooks]);

  const handleCreateNotebook = async (notebookData) => {
    try {
      const newNotebook = await createNotebook(notebookData);
      setShowCreateModal(false);
      navigate(`/notebooks/${newNotebook.id}`);
    } catch (error) {
      console.error('Failed to create notebook:', error);
    }
  };

  const handleDeleteNotebook = async (notebookId) => {
    try {
      await deleteNotebook(notebookId);
      await refreshNotebooks();
    } catch (error) {
      console.error('Failed to delete notebook:', error);
    }
  };

  const handleUpdateNotebook = async (notebookId, updates) => {
    try {
      await updateNotebook(notebookId, updates);
      await refreshNotebooks();
    } catch (error) {
      console.error('Failed to update notebook:', error);
    }
  };

  const recentNotebooks = notebooks
    .filter(nb => !nb.archived)
    .sort((a, b) => new Date(b.updated) - new Date(a.updated))
    .slice(0, 6);

  return (
    <div className="dashboard">
      {/* Animated Background */}
      <div className="background-container">
        <div className="animated-bg"></div>
        <div className="particles-container">
          {Array.from({ length: 50 }).map((_, i) => (
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

      {/* Header */}
      <header className="dashboard-header">
        <div className="header-content">
          <div className="header-left">
            <h1 className="dashboard-title">
              <span className="title-icon">📒</span>
              Open Notebook
            </h1>
            <p className="dashboard-subtitle">AI-Powered Research Assistant</p>
          </div>
          <div className="header-actions">
            <button 
              className="btn-secondary"
              onClick={() => navigate('/search')}
            >
              <span className="icon">🔍</span>
            </button>
            <button 
              className="btn-primary"
              onClick={() => setShowCreateModal(true)}
            >
              <span className="icon">➕</span>
              New Notebook
            </button>
          </div>
        </div>
      </header>

      {/* Stats Section */}
      <section className="stats-section">
        <div className="stats-grid">
          <StatsCard
            icon="📚"
            value={stats.activeNotebooks}
            label="Active Notebooks"
            trend="+2.3%"
            trendPositive={true}
          />
          <StatsCard
            icon="📄"
            value={stats.totalSources}
            label="Sources Added"
            trend="+15.7%"
            trendPositive={true}
          />
          <StatsCard
            icon="🤖"
            value={stats.aiInsights}
            label="AI Insights"
            trend="+8.2%"
            trendPositive={true}
          />
          <StatsCard
            icon="🎙️"
            value={stats.podcastsGenerated}
            label="Podcasts Generated"
            trend="+100%"
            trendPositive={true}
          />
        </div>
      </section>

      {/* Quick Actions */}
      <QuickActions onCreateNotebook={() => setShowCreateModal(true)} />

      {/* Recent Notebooks */}
      <section className="notebooks-section">
        <div className="section-header">
          <h2 className="section-title">Recent Notebooks</h2>
          <button 
            className="btn-secondary"
            onClick={() => navigate('/notebooks')}
          >
            View All
          </button>
        </div>
        
        {loading ? (
          <div className="loading-grid">
            {Array.from({ length: 6 }).map((_, i) => (
              <div key={i} className="notebook-card-skeleton" />
            ))}
          </div>
        ) : (
          <div className="notebooks-grid">
            {recentNotebooks.map(notebook => (
              <NotebookCard
                key={notebook.id}
                notebook={notebook}
                onOpen={() => navigate(`/notebooks/${notebook.id}`)}
                onDelete={() => handleDeleteNotebook(notebook.id)}
                onUpdate={(updates) => handleUpdateNotebook(notebook.id, updates)}
              />
            ))}
            <div 
              className="notebook-card create-new"
              onClick={() => setShowCreateModal(true)}
            >
              <div className="create-content">
                <div className="create-icon">➕</div>
                <h3>Create New Notebook</h3>
                <p>Start a new research project</p>
              </div>
            </div>
          </div>
        )}
      </section>

      {/* Recent Activity */}
      <ActivityFeed />

      {/* Floating Action Button */}
      <div className="fab" onClick={() => navigate('/search')}>
        <div className="fab-icon">💬</div>
        <div className="fab-tooltip">Quick Search</div>
      </div>

      {/* Create Notebook Modal */}
      {showCreateModal && (
        <CreateNotebookModal
          onClose={() => setShowCreateModal(false)}
          onCreate={handleCreateNotebook}
        />
      )}
    </div>
  );
};

export default Dashboard;