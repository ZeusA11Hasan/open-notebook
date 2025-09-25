import React, { useState } from 'react';
import { formatDistanceToNow } from 'date-fns';
import '../styles/NotebookCard.css';

const NotebookCard = ({ notebook, onOpen, onDelete, onUpdate }) => {
  const [showMenu, setShowMenu] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [editName, setEditName] = useState(notebook.name);
  const [editDescription, setEditDescription] = useState(notebook.description || '');

  const handleSave = async () => {
    try {
      await onUpdate({
        name: editName,
        description: editDescription
      });
      setIsEditing(false);
    } catch (error) {
      console.error('Failed to update notebook:', error);
    }
  };

  const handleCancel = () => {
    setEditName(notebook.name);
    setEditDescription(notebook.description || '');
    setIsEditing(false);
  };

  const getNotebookIcon = (name) => {
    const icons = ['🧠', '🌍', '💼', '🔬', '📊', '🎯', '💡', '🚀'];
    const index = name.length % icons.length;
    return icons[index];
  };

  return (
    <div className="notebook-card" onClick={!isEditing ? onOpen : undefined}>
      <div className="notebook-header">
        <div className="notebook-icon">{getNotebookIcon(notebook.name)}</div>
        <div className="notebook-menu" onClick={(e) => e.stopPropagation()}>
          <button 
            className="menu-trigger"
            onClick={() => setShowMenu(!showMenu)}
          >
            ⋯
          </button>
          {showMenu && (
            <div className="menu-dropdown">
              <button onClick={() => { setIsEditing(true); setShowMenu(false); }}>
                ✏️ Edit
              </button>
              <button onClick={() => { onDelete(); setShowMenu(false); }}>
                🗑️ Delete
              </button>
              <button onClick={() => setShowMenu(false)}>
                ❌ Cancel
              </button>
            </div>
          )}
        </div>
      </div>

      <div className="notebook-content">
        {isEditing ? (
          <div className="edit-form" onClick={(e) => e.stopPropagation()}>
            <input
              type="text"
              value={editName}
              onChange={(e) => setEditName(e.target.value)}
              className="edit-input"
              placeholder="Notebook name"
            />
            <textarea
              value={editDescription}
              onChange={(e) => setEditDescription(e.target.value)}
              className="edit-textarea"
              placeholder="Description"
              rows={3}
            />
            <div className="edit-actions">
              <button className="btn-save" onClick={handleSave}>
                💾 Save
              </button>
              <button className="btn-cancel" onClick={handleCancel}>
                ❌ Cancel
              </button>
            </div>
          </div>
        ) : (
          <>
            <h3 className="notebook-title">{notebook.name}</h3>
            <p className="notebook-description">
              {notebook.description || 'No description provided'}
            </p>
            <div className="notebook-stats">
              <span className="stat">{notebook.sourcesCount || 0} sources</span>
              <span className="stat">{notebook.notesCount || 0} notes</span>
              <span className="stat">{notebook.insightsCount || 0} insights</span>
            </div>
          </>
        )}
      </div>

      {!isEditing && (
        <div className="notebook-footer">
          <span className="notebook-date">
            Updated {formatDistanceToNow(new Date(notebook.updated), { addSuffix: true })}
          </span>
          <div className="notebook-actions" onClick={(e) => e.stopPropagation()}>
            <button 
              className="btn-icon"
              onClick={() => navigate(`/notebooks/${notebook.id}?tab=chat`)}
              title="Chat"
            >
              💬
            </button>
            <button 
              className="btn-icon"
              onClick={() => navigate(`/podcasts?notebook=${notebook.id}`)}
              title="Generate Podcast"
            >
              🎙️
            </button>
          </div>
        </div>
      )}

      <div className="card-glow"></div>
    </div>
  );
};

export default NotebookCard;