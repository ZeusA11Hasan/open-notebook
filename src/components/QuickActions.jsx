import React from 'react';
import { useNavigate } from 'react-router-dom';
import '../styles/QuickActions.css';

const QuickActions = ({ onCreateNotebook }) => {
  const navigate = useNavigate();

  const actions = [
    {
      id: 'new-notebook',
      icon: '📒',
      title: 'Create Notebook',
      description: 'Start a new research project',
      onClick: onCreateNotebook
    },
    {
      id: 'upload-source',
      icon: '📤',
      title: 'Upload Source',
      description: 'Add documents, PDFs, or links',
      onClick: () => navigate('/notebooks?action=upload')
    },
    {
      id: 'generate-podcast',
      icon: '🎙️',
      title: 'Generate Podcast',
      description: 'Create audio from your research',
      onClick: () => navigate('/podcasts')
    },
    {
      id: 'search-knowledge',
      icon: '🔍',
      title: 'Search Knowledge',
      description: 'Find insights across all notebooks',
      onClick: () => navigate('/search')
    }
  ];

  return (
    <section className="quick-actions">
      <h2 className="section-title">Quick Actions</h2>
      <div className="actions-grid">
        {actions.map(action => (
          <div
            key={action.id}
            className="action-card"
            onClick={action.onClick}
          >
            <div className="action-icon">{action.icon}</div>
            <div className="action-content">
              <h3>{action.title}</h3>
              <p>{action.description}</p>
            </div>
            <div className="action-arrow">→</div>
            <div className="action-glow"></div>
          </div>
        ))}
      </div>
    </section>
  );
};

export default QuickActions;