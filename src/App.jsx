import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { NotebookProvider } from './contexts/NotebookContext';
import Dashboard from './components/Dashboard';
import NotebookView from './components/NotebookView';
import SearchPage from './components/SearchPage';
import ModelsPage from './components/ModelsPage';
import SettingsPage from './components/SettingsPage';
import PodcastsPage from './components/PodcastsPage';
import TransformationsPage from './components/TransformationsPage';
import Sidebar from './components/Sidebar';
import AuthGuard from './components/AuthGuard';
import './styles/globals.css';

function App() {
  return (
    <AuthProvider>
      <NotebookProvider>
        <Router>
          <div className="app">
            <AuthGuard>
              <Sidebar />
              <main className="main-content">
                <Routes>
                  <Route path="/" element={<Dashboard />} />
                  <Route path="/notebooks/:id" element={<NotebookView />} />
                  <Route path="/search" element={<SearchPage />} />
                  <Route path="/models" element={<ModelsPage />} />
                  <Route path="/settings" element={<SettingsPage />} />
                  <Route path="/podcasts" element={<PodcastsPage />} />
                  <Route path="/transformations" element={<TransformationsPage />} />
                </Routes>
              </main>
            </AuthGuard>
          </div>
        </Router>
      </NotebookProvider>
    </AuthProvider>
  );
}

export default App;