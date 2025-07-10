export interface Transaction {
  symbol: string;
  order_date: string;
  transaction_date: string;
  action: 'Buy' | 'Sell' | 'Short' | 'Cover';
  amount: number;
  price: string;
  status: 'Completed' | 'Canceled';
}

export interface Competitor {
  public_id: string;
  name: string;
  rank: number;
  portfolio_value: number;
  return_percentage: number;
  return_dollars: number;
  transactions: Transaction[];
  last_updated: string;
}

export interface ActivityFeedItem {
  timestamp: string;
  player_name: string;
  player_rank: number;
  action: string;
  symbol: string;
  amount: number;
  price: string;
  portfolio_value: number;
}

export interface CompetitionData {
  competition: string;
  scraped_at: string;
  competitors: Competitor[];
  activity_feed: ActivityFeedItem[];
}