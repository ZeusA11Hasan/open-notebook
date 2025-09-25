import React, { useState, useEffect } from 'react';
import '../styles/Modal.css';

const CreateNotebookModal = ({ onClose, onCreate }) => {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // Focus on name input when modal opens
    const nameInput = document.querySelector('.modal input[type="text"]');
    if (nameInput) {
      nameInput.focus();
    }

    // Handle escape key
    const handleEscape = (e) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };

    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, [onClose]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!name.trim()) {
      return;
    }

    setLoading(true);
    try {
      await onCreate({
        name: name.trim(),
        description: description.trim()
      });
    } catch (error) {
      console.error('Failed to create notebook:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleBackdropClick = (e) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  return (
    <div className="modal-overlay" onClick={handleBackdropClick}>
      <div className="modal-content">
        <div className="modal-header">
          <h3>Create New Notebook</h3>
          <button className="modal-close" onClick={onClose}>
            ×
          </button>
        </div>
        
        <form onSubmit={handleSubmit} className="modal-body">
          <div className="form-group">
            <label htmlFor="notebookName">Notebook Name</label>
            <input
              id="notebookName"
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Enter notebook name..."
              required
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="notebookDescription">Description</label>
            <textarea
              id="notebookDescription"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Describe your research project..."
              rows={4}
            />
          </div>
          
          <div className="modal-footer">
            <button 
              type="button" 
              className="btn-secondary" 
              onClick={onClose}
              disabled={loading}
            >
              Cancel
            </button>
            <button 
              type="submit" 
              className="btn-primary" 
              disabled={!name.trim() || loading}
            >
              {loading ? (
                <>
                  <span className="loading-spinner"></span>
                  Creating...
                </>
              ) : (
                'Create Notebook'
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CreateNotebookModal;