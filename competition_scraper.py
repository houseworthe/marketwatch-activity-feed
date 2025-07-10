#!/usr/bin/env python3
"""
MarketWatch Trading Competition Activity Feed Scraper

Scrapes portfolio and transaction data for all participants in a trading competition.
"""

import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import json
import time


@dataclass
class Transaction:
    """Single transaction record."""
    symbol: str
    order_date: str
    transaction_date: str
    action: str  # 'Buy', 'Sell', 'Short', 'Cover'
    amount: int
    price: str  # Price as string (could be 'N/A' for canceled)
    status: str = "Completed"  # 'Completed', 'Canceled'
    
    def to_dict(self) -> dict:
        return {
            'symbol': self.symbol,
            'order_date': self.order_date,
            'transaction_date': self.transaction_date,
            'action': self.action,
            'amount': self.amount,
            'price': self.price,
            'status': self.status
        }


@dataclass
class Competitor:
    """Competitor profile with portfolio data."""
    public_id: str
    name: str
    rank: int
    portfolio_value: float
    return_percentage: float
    return_dollars: float
    transactions: List[Transaction]
    last_updated: datetime
    
    def to_dict(self) -> dict:
        return {
            'public_id': self.public_id,
            'name': self.name,
            'rank': self.rank,
            'portfolio_value': self.portfolio_value,
            'return_percentage': self.return_percentage,
            'return_dollars': self.return_dollars,
            'transactions': [t.to_dict() for t in self.transactions],
            'last_updated': self.last_updated.isoformat()
        }


class CompetitionScraper:
    """Scraper for MarketWatch trading competition data."""
    
    def __init__(self, game_uri: str, auth_cookies: str):
        """
        Initialize scraper with competition details.
        
        Args:
            game_uri: The game URI (e.g., 'baird-pwm-intern-stock-market-competition')
            auth_cookies: Authentication cookie string from browser
        """
        self.game_uri = game_uri
        self.base_url = "https://vse-api.marketwatch.com/v1"
        
        # Headers for API requests
        self.api_headers = {
            'accept': 'application/json',
            'accept-language': 'en-US,en;q=0.9',
            'dnt': '1',
            'origin': 'https://www.marketwatch.com',
            'priority': 'u=1, i',
            'referer': f'https://www.marketwatch.com/games/{game_uri}',
            'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36'
        }
        
        # Headers for HTML requests with authentication
        self.html_headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'en-US,en;q=0.9',
            'cache-control': 'max-age=0',
            'cookie': auth_cookies,
            'dnt': '1',
            'priority': 'u=0, i',
            'referer': f'https://www.marketwatch.com/games/{game_uri}',
            'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36'
        }
    
    def get_leaderboard(self) -> List[Tuple[str, str]]:
        """
        Get list of all competitors from the leaderboard.
        
        Returns:
            List of tuples (public_id, name)
        """
        # TODO: Implement leaderboard scraping
        # For now, return empty list - you'll need to add the leaderboard URL
        return []
    
    def get_competitor_name(self, soup: BeautifulSoup) -> str:
        """Extract competitor name from portfolio page."""
        # Look for the player name in the page
        # This might be in a header or profile section
        name_elem = soup.find('h1', {'class': 'player-name'})
        if name_elem:
            return name_elem.get_text(strip=True)
        
        # Try alternative locations
        profile_elem = soup.find('div', {'class': 'profile-name'})
        if profile_elem:
            return profile_elem.get_text(strip=True)
        
        # Default fallback
        return "Unknown Player"
    
    def get_portfolio_data(self, public_id: str) -> Optional[Dict]:
        """
        Fetch portfolio performance data from API.
        
        Args:
            public_id: The public ID for the portfolio
            
        Returns:
            Portfolio data dict or None if error
        """
        url = f"{self.base_url}/statistics/portfolioPerformance"
        params = {
            'gameUri': self.game_uri,
            'publicId': public_id
        }
        
        try:
            response = requests.get(url, params=params, headers=self.api_headers)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching portfolio data for {public_id}: {e}")
            return None
    
    def parse_transactions(self, soup: BeautifulSoup) -> List[Transaction]:
        """
        Parse transaction data from HTML.
        
        Args:
            soup: BeautifulSoup object of the portfolio page
            
        Returns:
            List of Transaction objects
        """
        transactions = []
        
        # Look for vse-module with view="transactions"
        vse_modules = soup.find_all(attrs={'is': 'vse-module'})
        for module in vse_modules:
            if module.get('view') == 'transactions':
                # Look for transaction table inside this module
                tables = module.find_all('table', {'class': 'table--primary'})
                for table in tables:
                    transactions.extend(self._parse_transaction_table(table))
        
        # Also try to find transaction tables directly
        tables = soup.find_all('table', {'class': ['table--primary', 'ranking']})
        for table in tables:
            # Check if this is a transaction table by looking at headers
            headers = []
            header_row = table.find('tr')
            if header_row:
                header_cells = header_row.find_all(['th', 'td'])
                headers = [cell.get_text(strip=True) for cell in header_cells]
                
                # Check if this looks like a transaction table
                if any('Symbol' in h for h in headers) and any('Order' in h for h in headers):
                    transactions.extend(self._parse_transaction_table(table))
        
        # Remove duplicates (same transaction might be found multiple times)
        seen = set()
        unique_transactions = []
        for t in transactions:
            key = (t.symbol, t.order_date, t.action, t.amount)
            if key not in seen:
                seen.add(key)
                unique_transactions.append(t)
        
        return unique_transactions
    
    def _parse_transaction_table(self, table) -> List[Transaction]:
        """Parse transactions from a specific table."""
        transactions = []
        
        rows = table.find_all('tr')
        for row in rows[1:]:  # Skip header row
            cells = row.find_all(['td', 'th'])
            if len(cells) >= 6:  # Expected columns
                try:
                    symbol = cells[0].get_text(strip=True)
                    order_date = cells[1].get_text(strip=True)
                    transaction_date = cells[2].get_text(strip=True)
                    
                    # Parse action type and status
                    action_cell = cells[3]
                    action_text = action_cell.get_text(strip=True)
                    
                    # Check if transaction was canceled
                    status = "Completed"
                    if "Canceled" in action_text:
                        status = "Canceled"
                        # Extract the actual action (Buy/Sell/Short) before "Canceled"
                        action = action_text.split()[0] if action_text.split() else action_text
                    else:
                        action = action_text
                    
                    amount_text = cells[4].get_text(strip=True).replace(',', '')
                    amount = int(amount_text) if amount_text.isdigit() else 0
                    
                    price = cells[5].get_text(strip=True)
                    
                    transaction = Transaction(
                        symbol=symbol,
                        order_date=order_date,
                        transaction_date=transaction_date,
                        action=action,
                        amount=amount,
                        price=price,
                        status=status
                    )
                    transactions.append(transaction)
                except (ValueError, IndexError) as e:
                    continue
        
        return transactions
    
    def scrape_competitor(self, public_id: str) -> Optional[Competitor]:
        """
        Scrape all data for a single competitor.
        
        Args:
            public_id: The public ID for the competitor
            
        Returns:
            Competitor object or None if error
        """
        # Get portfolio performance data from API
        portfolio_data = self.get_portfolio_data(public_id)
        if not portfolio_data:
            return None
        
        # Extract latest performance metrics
        values = portfolio_data.get('data', {}).get('values', [])
        if not values:
            return None
        
        latest = values[-1]  # Most recent data
        
        # Get HTML page for transactions and name
        portfolio_url = f"https://www.marketwatch.com/games/{self.game_uri}/portfolio?pub={public_id}"
        try:
            response = requests.get(portfolio_url, headers=self.html_headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Get competitor name
            name = self.get_competitor_name(soup)
            
            # Get transactions
            transactions = self.parse_transactions(soup)
            
        except requests.RequestException as e:
            print(f"Error fetching HTML for {public_id}: {e}")
            name = "Unknown"
            transactions = []
        
        # Create Competitor object
        competitor = Competitor(
            public_id=public_id,
            name=name,
            rank=latest.get('r', 0),
            portfolio_value=latest.get('w', 0.0),
            return_percentage=latest.get('p', 0.0),
            return_dollars=latest.get('g', 0.0),
            transactions=transactions,
            last_updated=datetime.now()
        )
        
        return competitor
    
    def scrape_all_competitors(self, public_ids: List[str], delay: float = 1.0) -> List[Competitor]:
        """
        Scrape data for all competitors.
        
        Args:
            public_ids: List of public IDs to scrape
            delay: Delay between requests in seconds
            
        Returns:
            List of Competitor objects
        """
        competitors = []
        total = len(public_ids)
        
        for i, public_id in enumerate(public_ids, 1):
            print(f"Scraping competitor {i}/{total}: {public_id}")
            
            competitor = self.scrape_competitor(public_id)
            if competitor:
                competitors.append(competitor)
                print(f"  ✓ {competitor.name} - Rank #{competitor.rank} - ${competitor.portfolio_value:,.2f}")
            else:
                print(f"  ✗ Failed to scrape {public_id}")
            
            # Be nice to the server
            if i < total:
                time.sleep(delay)
        
        return competitors
    
    def create_activity_feed(self, competitors: List[Competitor]) -> List[Dict]:
        """
        Create a unified activity feed from all competitors' transactions.
        
        Args:
            competitors: List of Competitor objects
            
        Returns:
            List of activity feed items sorted by date
        """
        activities = []
        
        for competitor in competitors:
            for transaction in competitor.transactions:
                # Skip canceled transactions for the feed
                if transaction.status == "Canceled":
                    continue
                
                activity = {
                    'timestamp': transaction.order_date,
                    'player_name': competitor.name,
                    'player_rank': competitor.rank,
                    'action': transaction.action,
                    'symbol': transaction.symbol,
                    'amount': transaction.amount,
                    'price': transaction.price,
                    'portfolio_value': competitor.portfolio_value
                }
                activities.append(activity)
        
        # Sort by timestamp (newest first)
        # Parse date strings for proper sorting
        def parse_date(date_str):
            try:
                # Handle format like "7/9/25 10:45a ET"
                if not date_str or date_str.strip() == "":
                    return datetime.min
                
                # Remove "ET" and clean up
                date_str = date_str.replace(" ET", "").strip()
                
                # Split date and time
                date_part, time_part = date_str.split(" ")
                
                # Parse date (7/9/25 -> 2025-07-09)
                month, day, year = date_part.split("/")
                year = f"20{year}"  # Convert 25 to 2025
                
                # Parse time (10:45a -> 10:45 AM)
                time_part = time_part.replace("a", " AM").replace("p", " PM")
                
                # Combine and parse
                full_date_str = f"{year}-{month.zfill(2)}-{day.zfill(2)} {time_part}"
                return datetime.strptime(full_date_str, "%Y-%m-%d %I:%M %p")
            except Exception:
                return datetime.min
        
        activities.sort(key=lambda x: parse_date(x['timestamp']), reverse=True)
        
        return activities


def main():
    """Example usage."""
    
    # Your authentication cookies
    auth_cookies = 'refresh=off; letsGetMikey=enabled; refresh=off; letsGetMikey=enabled; _pctx=%7Bu%7DN4IgrgzgpgThIC4B2YA2qA05owMoBcBDfSREQpAeyRCwgEt8oBJAE0RXQF8g; _pcid=%7B%22browserId%22%3A%22mc4yzz5cvpxw07b3%22%7D; cX_P=mc4yzz5cvpxw07b3; djcs_route=966396ea-5edb-4ce1-a7a5-26117bf651a0; TR=V2-c9d47073af3b9588751977fe4fbcf20f724a9bc94c79daba415c2eeb74a88ae0; djcs_auto=M1750367024%2FvqcMb8aJqCyDvD%2Bp4%2Fvy%2BJiAFKg5fZvadNlW5%2B6tPob1Ux%2F8CxJVZxpM3o7j2vhZOAMILVme9%2FLQlzzu9y8IKXamsLI7pQb%2FQ5M1MihrPMEk3sF9GGfMqFopxSs3%2BIt%2B1DUxn82dVaLUw7uKUk%2FiDTjS%2BzmL1XBKGa94d6bhelFEArIjIwCRNSZ2GAuc07sfEiDsMOrV8J1clJPuxicJ3dT879yl2tTfW2PxOI%2FfaIj6asUD0iUKcDIHsTi0HUv7%2F5qVvr76vbBnMftizItPBra55qpyQNAo8SNb2H0eBMD05Qkn0PRW%2Fuwi2gP2m6aO7QR%2BmMGp6HOUTU2sDzPUDB%2Bi5aJjS%2Fa0sYi0Djc446J79jy0mgplfbnJ%2BG32U%2BH0235i4ZIQdOnYwPoK5gR%2FJ%2FdJhA6Z%2BUMFTa%2FP3iYgc6Yv%2BWqeDBSaV5%2BVF%2BiTEr7sCa1uKl8JP3pg82rvoUB1gQ%3D%3DG; djcs_session=M1750430628%2F59I8D%2Bl49KcBfDxwh6Bp6FxgsnCYIPy6KL%2FM2PeI%2By7uZtzgKNyoQi6T2%2B0dCheRYYyxH29OJyBE3%2FeAX%2FjxxQoq2xitSco3%2F1Yu98h8iT1ea%2BUDtUMutK6qEqEhdTdjv8b0AAomqZw9HvBNkUIiZdc%2BFk16EsM0dYEzQaikaR7eD6HPTdt8jjVguKTFPc9mDM9bGBXKSftZN4iREbJ7prR%2Fkyy1gp3KD8WhH4jIfFBihOZRFdfcfxDLPdIL0wiPwhDWC%2BX0u75dHAQTtWBtf7ZgmKnMYBXrET4F5A3f17HQKOFNIIXERXF9RUzpxuRqHKR6CzK9dI6jElmJ9RiVuBp92HnnDglpM4RSiMyYNXyhP412z7m%2FL%2BfETluZNmbEK1j0mLOqIVkyhJbrNYjdCXDTDZmqH1BY03rXvN%2F5Hy17x%2F2BIoV9ayTyIYhVBC%2B9urxtiNHh66W1lyCqzLw8ETsxvw%2F9CvH8DrL8x1OU%2BOnM2%2FPhtdZnnbny0lmVyz%2FC3Lba8Jfhm1FCdjmIB%2F3cdvB9AoI6c6X0qixmGLJiRwz6%2FltWTlkv8bQzjrKIwSoNQ8amCyipAt4OdsJygpz7zw%3D%3DG; ab_uuid=05588ce5-0f6c-487b-8ab8-1426ce30f17d; wsjregion=na%2Cus; gdprApplies=false; ccpaApplies=false; vcdpaApplies=false; regulationApplies=gdpr%3Afalse%2Ccpra%3Afalse%2Cvcdpa%3Afalse; refresh=off; letsGetMikey=enabled; ca_rt=IXv-C9jkFcy69fAikw1gqQ._JN4amJoBEkZaLYOCmOf4FgJ_QMP9UsJgIiVG650EAEARkpvB2Uv7qoK26shrmbCz7JTQqbZw6fvODc8Gz6M1Y9DpnkxJesQ9ImPL1iXK00; datadome=~F9hNrk0f_vF7i04F4qXVPSkq5tnV4~PETGvgBlCfxSAw1uuyDsRaXhSU0Q6N0_lM1n6vcvQMjEB09yBTaKyCCe_FJjeyvXTzRIFHW50r2pjWnZ3rQG8g4QFPxcm3QkA; mw_loc=%7B%22Region%22%3A%22WI%22%2C%22Country%22%3A%22US%22%2C%22Continent%22%3A%22NA%22%2C%22ApplicablePrivacy%22%3A0%7D; ca_id=0f7b9586-b922-4403-8396-039962f63385.eJw9kFFTwjAQhP9Lnim0acolPNmRIjgKiKIjjsNc04RGSsE2UNHxvxtw9PW7vd29-yIrc1DlssSNIj2S2BxL0iIaN6Y4_tHhdl-rZlvZ3I3UBk3hoMr_6UXVpGiqrC23G6fY703mBJSikj5DL4PU95hPucdRUi8QPk8lDyHTwqlthXJ9XpAiY-BDiDpMRcQ5RIEA0IrpVGrqa6AMRSoFkyAyTJEFkaRKpcCQc1S-M6u2hapJ74UMZkkyS6680bg_ehz15_ENeW0R3Nt8ac3pqAAin4UhB2iR-hz_qSdGHxfjYjmZjrzZqoTo4SmOg9tDsTP5MHMbRz25vly_w3wa30MyeMbFnQuVlUKrsiXaky0TEdBu5GzNL4gCLrquq3vdx-4MaEj5GZjalSW5tbu61-k0TdNu6rfTFzuyMKq05PsHv4596Q.LM5NCaU8KolC1aMqQPq7IAn2KVUV412PMHi2EeqQN2c-nQLSN8DtUvYE8bkT4Ou4WUpwHm94nJVkniYt1zYG_NdGWBnOMcAruqnjVtpdRwkLRVM-ACeoPuAPL9W341xCNrDUDYOHBeMKSZRIJe7jCG3rj5zxrsHKs4qrsArOOtDWMKPqNxGNeXBYcOVoMgbTEY4Yn5RKxn2EF7IaAq9HOmP4d44l4D8ZaQ8SafuOajVTF9B5o1r7hQ8O9j4i96rVYb9Ehzk2Y6dj1UHiYXgjdUYPY5vQ4KmrjC4mIAgXMhP5pjkDH66AFIa2Mr_yJ9QLv_vY24npiKXVGjuRvkuJrA; icons-loaded=true; usr_prof_v2=eyJpYyI6NH0%3D'
    
    # Competition details
    game_uri = "baird-pwm-intern-stock-market-competition"
    
    # Create scraper
    scraper = CompetitionScraper(game_uri, auth_cookies)
    
    # For testing, let's just scrape your portfolio
    # In production, you'd get this list from the leaderboard
    test_public_ids = ["-Ct8JFv9TYip"]  # Your public ID
    
    # Scrape all competitors
    print("Scraping competition data...")
    competitors = scraper.scrape_all_competitors(test_public_ids)
    
    # Create activity feed
    print("\nCreating activity feed...")
    feed = scraper.create_activity_feed(competitors)
    
    # Display results
    print(f"\nScraped {len(competitors)} competitors")
    print(f"Total activities: {len(feed)}")
    
    # Show sample of activity feed
    print("\nRecent Activity:")
    for activity in feed[:10]:
        print(f"  {activity['timestamp']} - {activity['player_name']} (Rank #{activity['player_rank']}) "
              f"{activity['action']} {activity['amount']:,} {activity['symbol']} @ {activity['price']}")
    
    # Save data
    with open('competition_data.json', 'w') as f:
        data = {
            'competition': game_uri,
            'scraped_at': datetime.now().isoformat(),
            'competitors': [c.to_dict() for c in competitors],
            'activity_feed': feed
        }
        json.dump(data, f, indent=2)
    print("\nData saved to competition_data.json")


if __name__ == "__main__":
    main()