import React from 'react';
import '../styles/StatsCard.css';

const StatsCard = ({ icon, value, label, trend, trendPositive = true }) => {
  return (
    <div className="stat-card">
      <div className="stat-icon">{icon}</div>
      <div className="stat-content">
        <div className="stat-number">{value}</div>
        <div className="stat-label">{label}</div>
      </div>
      {trend && (
        <div className={`stat-trend ${trendPositive ? 'positive' : 'negative'}`}>
          {trend}
        </div>
      )}
      <div className="stat-glow"></div>
    </div>
  );
};

export default StatsCard;