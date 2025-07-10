import React, { useState, useEffect } from 'react';
import { Activity, TrendingUp, TrendingDown, Clock, Moon, Sun, Trophy, X } from 'lucide-react';
import { CompetitionData } from '../types';
import { subscribeToLatestData } from '../firebase';

const ActivityFeed: React.FC = () => {
  const [data, setData] = useState<CompetitionData | null>(null);
  const [loading, setLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isDarkMode, setIsDarkMode] = useState(() => {
    const saved = localStorage.getItem('isDarkMode');
    return saved ? JSON.parse(saved) : false;
  });
  const [showLeaderboard, setShowLeaderboard] = useState(false);

  useEffect(() => {
    setLoading(true);
    
    // Subscribe to Firebase real-time updates
    const unsubscribe = subscribeToLatestData((competitionData) => {
      if (competitionData) {
        setData(competitionData);
        setLastUpdated(new Date());
        setError(null);
      } else {
        setError('No data available. Waiting for next update...');
      }
      setLoading(false);
    });
    
    // Cleanup subscription on unmount
    return () => unsubscribe();
  }, []);

  // Update body class for dark mode and save to localStorage
  useEffect(() => {
    if (isDarkMode) {
      document.body.classList.add('dark');
    } else {
      document.body.classList.remove('dark');
    }
    localStorage.setItem('isDarkMode', JSON.stringify(isDarkMode));
  }, [isDarkMode]);

  // Handle ESC key to close modal
  useEffect(() => {
    const handleEsc = (event: KeyboardEvent) => {
      if (event.key === 'Escape' && showLeaderboard) {
        setShowLeaderboard(false);
      }
    };
    window.addEventListener('keydown', handleEsc);
    return () => window.removeEventListener('keydown', handleEsc);
  }, [showLeaderboard]);

  const getActionIcon = (action: string) => {
    switch (action.toLowerCase()) {
      case 'buy':
        return <TrendingUp className="activity-icon" style={{ color: '#10b981' }} />;
      case 'sell':
        return <TrendingDown className="activity-icon" style={{ color: '#ef4444' }} />;
      case 'short':
        return <TrendingDown className="activity-icon" style={{ color: '#f97316' }} />;
      case 'cover':
        return <TrendingUp className="activity-icon" style={{ color: '#3b82f6' }} />;
      default:
        return <Activity className="activity-icon" style={{ color: '#6b7280' }} />;
    }
  };

  const getActionClass = (action: string) => {
    switch (action.toLowerCase()) {
      case 'buy':
        return 'action-badge action-buy';
      case 'sell':
        return 'action-badge action-sell';
      case 'short':
        return 'action-badge action-short';
      case 'cover':
        return 'action-badge action-cover';
      default:
        return 'action-badge';
    }
  };

  const formatNumber = (num: number) => {
    return new Intl.NumberFormat('en-US').format(num);
  };

  const formatCurrency = (num: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(num);
  };

  const calculateTradeSize = (amount: number, price: string) => {
    // Remove $ and convert to number
    const priceNum = parseFloat(price.replace('$', ''));
    return amount * priceNum;
  };

  if (loading) {
    return (
      <div className="loading">
        <div className="spinner"></div>
        <span>Loading competition data...</span>
      </div>
    );
  }

  return (
    <div className={`container ${isDarkMode ? 'dark' : ''}`}>
      {/* Header */}
      <div className="header">
        <div className="header-content">
          <div>
            <h1>Baird PWM Intern Stock Market Competition</h1>
            <p>Real-time activity feed</p>
          </div>
          
          <div className="header-buttons">
            {/* Leaderboard Button */}
            <button
              onClick={() => setShowLeaderboard(true)}
              className="leaderboard-button"
              aria-label="Show leaderboard"
            >
              <Trophy size={20} />
              <span>Leaderboard</span>
            </button>
            
            {/* Theme Toggle */}
            <button
              onClick={() => setIsDarkMode(!isDarkMode)}
              className="theme-toggle"
              aria-label="Toggle theme"
            >
              {isDarkMode ? <Sun size={20} /> : <Moon size={20} />}
            </button>
          </div>
        </div>
        
        {lastUpdated && (
          <div className="last-updated">
            <Clock className="last-updated-icon" />
            <span>Last updated: {lastUpdated.toLocaleTimeString()}</span>
          </div>
        )}
      </div>


      {/* Activity Feed */}
      <div className="activity-feed">
        <div className="activity-table">
          <div className="table-header">
            <div className="table-cell">Rank</div>
            <div className="table-cell">Player</div>
            <div className="table-cell">Action</div>
            <div className="table-cell">Symbol</div>
            <div className="table-cell">Amount</div>
            <div className="table-cell">Price</div>
            <div className="table-cell">Trade Size</div>
            <div className="table-cell">Portfolio</div>
            <div className="table-cell">Time</div>
          </div>
          
          {data?.activity_feed?.map((activity, index) => (
            <div key={index} className="table-row">
              <div className="table-cell rank-cell">
                <span className={`rank-bubble rank-${activity.player_rank}`}>
                  {activity.player_rank}
                </span>
              </div>
              <div className="table-cell player-cell">
                <span className="player-name">{activity.player_name}</span>
              </div>
              <div className="table-cell action-cell">
                {getActionIcon(activity.action)}
                <span className={getActionClass(activity.action)}>
                  {activity.action}
                </span>
              </div>
              <div className="table-cell symbol-cell">
                <span className="symbol-bubble">
                  {activity.symbol}
                </span>
              </div>
              <div className="table-cell amount-cell">
                {formatNumber(activity.amount)}
              </div>
              <div className="table-cell price-cell">
                {activity.price}
              </div>
              <div className="table-cell trade-size-cell">
                {formatCurrency(calculateTradeSize(activity.amount, activity.price))}
              </div>
              <div className="table-cell portfolio-cell">
                {formatCurrency(activity.portfolio_value)}
              </div>
              <div className="table-cell time-cell">
                {activity.timestamp}
              </div>
            </div>
          ))}
          
          {!data?.activity_feed?.length && (
            <div className="no-activity">
              <Activity className="no-activity-icon" />
              <p>No recent activity</p>
            </div>
          )}
        </div>
      </div>


      {/* Leaderboard Modal */}
      {showLeaderboard && (
        <div 
          className="modal-overlay"
          onClick={() => setShowLeaderboard(false)}
        >
          <div 
            className="modal-content leaderboard-modal"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="modal-header">
              <h2>Competition Leaderboard</h2>
              <button
                onClick={() => setShowLeaderboard(false)}
                className="modal-close"
                aria-label="Close modal"
              >
                <X size={24} />
              </button>
            </div>
            
            <div className="modal-body">
              <div className="leaderboard-table">
                <div className="leaderboard-header">
                  <div className="leaderboard-cell rank-col">Rank</div>
                  <div className="leaderboard-cell name-col">Player</div>
                  <div className="leaderboard-cell value-col">Portfolio Value</div>
                  <div className="leaderboard-cell return-col">Return %</div>
                  <div className="leaderboard-cell return-col">Return $</div>
                </div>
                
                {data?.competitors
                  .sort((a, b) => a.rank - b.rank)
                  .map((competitor) => (
                    <div key={competitor.public_id} className="leaderboard-row">
                      <div className="leaderboard-cell rank-col">
                        <span className={`rank-bubble rank-${competitor.rank}`}>
                          {competitor.rank}
                        </span>
                      </div>
                      <div className="leaderboard-cell name-col">
                        {competitor.name}
                      </div>
                      <div className="leaderboard-cell value-col">
                        {formatCurrency(competitor.portfolio_value)}
                      </div>
                      <div className={`leaderboard-cell return-col ${competitor.return_percentage >= 0 ? 'positive' : 'negative'}`}>
                        {competitor.return_percentage >= 0 ? '+' : ''}{competitor.return_percentage.toFixed(2)}%
                      </div>
                      <div className={`leaderboard-cell return-col ${competitor.return_dollars >= 0 ? 'positive' : 'negative'}`}>
                        {competitor.return_dollars >= 0 ? '+' : ''}{formatCurrency(Math.abs(competitor.return_dollars))}
                      </div>
                    </div>
                  ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ActivityFeed;