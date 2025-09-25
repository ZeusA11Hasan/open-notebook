import React, { useState, useEffect } from 'react';
import { formatDistanceToNow } from 'date-fns';
import '../styles/ActivityFeed.css';

const ActivityFeed = () => {
  const [activities, setActivities] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Simulate fetching recent activity data
    // In real implementation, this would fetch from your API
    const fetchActivities = async () => {
      try {
        // Mock data - replace with actual API call
        const mockActivities = [
          {
            id: 1,
            type: 'source_added',
            icon: '📄',
            text: 'New source added to AI Research Papers',
            timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000), // 2 hours ago
            notebookId: 'notebook1'
          },
          {
            id: 2,
            type: 'insight_generated',
            icon: '🤖',
            text: 'AI insight generated for Climate Change Research',
            timestamp: new Date(Date.now() - 4 * 60 * 60 * 1000), // 4 hours ago
            notebookId: 'notebook2'
          },
          {
            id: 3,
            type: 'podcast_created',
            icon: '🎙️',
            text: 'Podcast created from Market Analysis Q1',
            timestamp: new Date(Date.now() - 24 * 60 * 60 * 1000), // 1 day ago
            notebookId: 'notebook3'
          },
          {
            id: 4,
            type: 'note_created',
            icon: '📝',
            text: 'Note created in AI Research Papers',
            timestamp: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000), // 2 days ago
            notebookId: 'notebook1'
          }
        ];

        setActivities(mockActivities);
      } catch (error) {
        console.error('Failed to fetch activities:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchActivities();
  }, []);

  if (loading) {
    return (
      <section className="activity-section">
        <h2 className="section-title">Recent Activity</h2>
        <div className="activity-feed">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="activity-item-skeleton" />
          ))}
        </div>
      </section>
    );
  }

  return (
    <section className="activity-section">
      <h2 className="section-title">Recent Activity</h2>
      <div className="activity-feed">
        {activities.map(activity => (
          <div key={activity.id} className="activity-item">
            <div className="activity-icon">{activity.icon}</div>
            <div className="activity-content">
              <div className="activity-text">
                <strong>{activity.text}</strong>
              </div>
              <div className="activity-time">
                {formatDistanceToNow(activity.timestamp, { addSuffix: true })}
              </div>
            </div>
            <div className="activity-glow"></div>
          </div>
        ))}
      </div>
    </section>
  );
};

export default ActivityFeed;