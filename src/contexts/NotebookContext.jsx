import React, { createContext, useContext, useState, useEffect } from 'react';
import { useAuth } from './AuthContext';

const NotebookContext = createContext();

export const useNotebooks = () => {
  const context = useContext(NotebookContext);
  if (!context) {
    throw new Error('useNotebooks must be used within a NotebookProvider');
  }
  return context;
};

export const NotebookProvider = ({ children }) => {
  const [notebooks, setNotebooks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const { isAuthenticated } = useAuth();

  const getAuthHeaders = () => {
    const password = localStorage.getItem('app_password');
    return password ? { 'Authorization': `Bearer ${password}` } : {};
  };

  const fetchNotebooks = async () => {
    if (!isAuthenticated) return;
    
    try {
      setLoading(true);
      const response = await fetch('/api/notebooks', {
        headers: getAuthHeaders()
      });
      
      if (!response.ok) {
        throw new Error('Failed to fetch notebooks');
      }
      
      const data = await response.json();
      setNotebooks(data);
      setError(null);
    } catch (err) {
      console.error('Error fetching notebooks:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const createNotebook = async (notebookData) => {
    try {
      const response = await fetch('/api/notebooks', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...getAuthHeaders()
        },
        body: JSON.stringify(notebookData)
      });

      if (!response.ok) {
        throw new Error('Failed to create notebook');
      }

      const newNotebook = await response.json();
      setNotebooks(prev => [newNotebook, ...prev]);
      return newNotebook;
    } catch (err) {
      console.error('Error creating notebook:', err);
      throw err;
    }
  };

  const updateNotebook = async (notebookId, updates) => {
    try {
      const response = await fetch(`/api/notebooks/${notebookId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          ...getAuthHeaders()
        },
        body: JSON.stringify(updates)
      });

      if (!response.ok) {
        throw new Error('Failed to update notebook');
      }

      const updatedNotebook = await response.json();
      setNotebooks(prev => 
        prev.map(nb => nb.id === notebookId ? updatedNotebook : nb)
      );
      return updatedNotebook;
    } catch (err) {
      console.error('Error updating notebook:', err);
      throw err;
    }
  };

  const deleteNotebook = async (notebookId) => {
    try {
      const response = await fetch(`/api/notebooks/${notebookId}`, {
        method: 'DELETE',
        headers: getAuthHeaders()
      });

      if (!response.ok) {
        throw new Error('Failed to delete notebook');
      }

      setNotebooks(prev => prev.filter(nb => nb.id !== notebookId));
    } catch (err) {
      console.error('Error deleting notebook:', err);
      throw err;
    }
  };

  const refreshNotebooks = async () => {
    await fetchNotebooks();
  };

  useEffect(() => {
    if (isAuthenticated) {
      fetchNotebooks();
    }
  }, [isAuthenticated]);

  const value = {
    notebooks,
    loading,
    error,
    createNotebook,
    updateNotebook,
    deleteNotebook,
    refreshNotebooks
  };

  return (
    <NotebookContext.Provider value={value}>
      {children}
    </NotebookContext.Provider>
  );
};