# MarketWatch Activity Feed

Real-time activity feed for MarketWatch trading competition showing live trades and portfolio performance.

## Overview

This project creates a live activity feed for the Baird PWM Intern Stock Market Competition, featuring:
- 📊 **Real-time trading activity** from all 19 participants
- 🏆 **Live leaderboard** with portfolio values and rankings
- 📈 **Clean, responsive React frontend** with dark/light mode
- 🔄 **Auto-refresh** every 5 minutes during market hours
- ⏰ **Market hours checking** (8 AM - 4 PM CST, weekdays only)

## Architecture

### Backend (Python)
- **Competition Scraper**: Orchestrates data collection for all participants
- **Leaderboard Scraper**: Gets all competitor public IDs and names
- **Portfolio Data Scraper**: Fetches performance data from MarketWatch API
- **Transaction Scraper**: Parses HTML to extract transaction history

### Frontend (React TypeScript)
- Real-time activity feed with auto-refresh
- Competitor rankings with rank bubbles (gold/silver/bronze)
- Dark/light mode toggle
- Trade size calculations (amount × price)
- Responsive grid layout

## Quick Start

### Backend Setup
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Test scraper (update auth cookies in script)
python update_frontend_data.py
```

### Frontend Setup
```bash
cd frontend
npm install
npm start
```

## Files Structure

```
marketwatch-activity-feed/
├── README.md                    # This file
├── requirements.txt             # Python dependencies
├── competition_scraper.py       # Multi-user competition scraper
├── leaderboard_scraper.py       # Leaderboard extraction
├── marketwatch_scraper.py       # Core scraper implementation
├── update_frontend_data.py      # Main script to update frontend data
├── frontend/                    # React TypeScript frontend
│   ├── src/
│   │   ├── components/
│   │   │   └── ActivityFeed.tsx # Main activity feed component
│   │   ├── types.ts            # TypeScript interfaces
│   │   └── index.css           # Custom CSS styles
│   ├── public/
│   │   └── competition_data.json # Generated data file
│   ├── package.json
│   └── netlify.toml            # Netlify deployment config
└── venv/                       # Python virtual environment
```

## Authentication

The scraper requires authentication cookies from a logged-in MarketWatch session:

**To get cookies:**
1. Log into MarketWatch competition page
2. Open browser dev tools (F12)
3. Go to Network tab
4. Refresh page
5. Find request to competition page
6. Copy cookie header value
7. Update the `auth_cookies` variable in `update_frontend_data.py`

## Deployment

### Netlify (Recommended)
1. Push code to GitHub
2. Connect repo to Netlify
3. Build settings are already configured in `netlify.toml`
4. Deploy!

### Auto-Update Setup
Set up a cron job to refresh data every 5 minutes during market hours:

```bash
# Add to crontab (crontab -e)
*/5 8-16 * * 1-5 cd /path/to/marketwatch-activity-feed && source venv/bin/activate && python update_frontend_data.py
```

## Data Structures

### Transaction
```python
@dataclass
class Transaction:
    symbol: str           # Stock symbol (e.g., "TSLA")
    order_date: str       # When order was placed
    transaction_date: str # When trade executed
    action: str           # "Buy", "Sell", "Short", "Cover"
    amount: int           # Number of shares
    price: str            # Execution price
    status: str           # "Completed" or "Canceled"
```

### Competitor
```python
@dataclass
class Competitor:
    public_id: str            # MarketWatch public ID
    name: str                 # Participant name
    rank: int                 # Current ranking
    portfolio_value: float    # Current portfolio value
    return_percentage: float  # Return percentage
    return_dollars: float     # Return in dollars
    transactions: List[Transaction]
    last_updated: datetime
```

## API Endpoints Used

- **Portfolio Performance**: `https://vse-api.marketwatch.com/v1/statistics/portfolioPerformance`
- **Portfolio Page**: `https://www.marketwatch.com/games/{game_uri}/portfolio?pub={public_id}`
- **Leaderboard**: `https://www.marketwatch.com/games/{game_uri}/rankings`

## Features

- ✅ **Market Hours Validation**: Only scrapes during 8 AM - 4 PM CST weekdays
- ✅ **Real-time Updates**: Auto-refresh every 5 minutes
- ✅ **All 19 Competitors**: Complete competition coverage
- ✅ **Trade Size Calculation**: Shows dollar value of each trade
- ✅ **Responsive Design**: Works on desktop and mobile
- ✅ **Dark/Light Mode**: Theme toggle
- ✅ **Rank Visualization**: Gold/silver/bronze bubbles for top 3

## License

This tool is for educational purposes only. Please respect MarketWatch's terms of service and rate limits.