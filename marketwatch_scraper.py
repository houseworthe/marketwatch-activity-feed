#!/usr/bin/env python3
"""
MarketWatch Trading Competition Portfolio Scraper

Scrapes portfolio performance data from MarketWatch trading competition API.
"""

import requests
import json
from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from typing import List
from bs4 import BeautifulSoup
import re


@dataclass
class Transaction:
    """Data structure for a single transaction."""
    symbol: str
    order_date: str
    transaction_date: str
    action: str  # 'Buy', 'Sell', 'Short', etc.
    amount: int
    price: str  # Price as string (could be 'N/A' for canceled orders)
    status: str = "Completed"  # 'Completed', 'Canceled', etc.


@dataclass
class DailyPerformance:
    """Data structure for daily portfolio performance."""
    date: str
    portfolio_value: float
    percentage_return: float
    dollar_gain: float
    rank: int


@dataclass
class PortfolioData:
    """Data structure for portfolio performance information."""
    public_id: str
    current_value: float
    current_return_percentage: float
    current_dollar_gain: float
    current_rank: int
    daily_performance: List[DailyPerformance]
    transactions: List[Transaction]
    timestamp: datetime


class MarketWatchScraper:
    """Scraper for MarketWatch trading competition data."""
    
    def __init__(self, game_uri: str, public_id: str):
        """
        Initialize scraper with competition details.
        
        Args:
            game_uri: The game URI (e.g., 'baird-pwm-intern-stock-market-competition')
            public_id: The public ID for the portfolio (e.g., '-Ct8JFv9TYip')
        """
        self.game_uri = game_uri
        self.public_id = public_id
        self.base_url = "https://vse-api.marketwatch.com/v1"
        self.portfolio_url = f"https://www.marketwatch.com/games/{game_uri}/portfolio?pub={public_id}"
        
        # Headers for API requests
        self.api_headers = {
            'accept': 'application/json',
            'accept-language': 'en-US,en;q=0.9',
            'dnt': '1',
            'origin': 'https://www.marketwatch.com',
            'priority': 'u=1, i',
            'referer': self.portfolio_url,
            'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36'
        }
        
        # Headers for HTML requests with authentication cookies
        self.html_headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'en-US,en;q=0.9',
            'cache-control': 'max-age=0',
            'cookie': 'refresh=off; letsGetMikey=enabled; refresh=off; letsGetMikey=enabled; _pctx=%7Bu%7DN4IgrgzgpgThIC4B2YA2qA05owMoBcBDfSREQpAeyRCwgEt8oBJAE0RXQF8g; _pcid=%7B%22browserId%22%3A%22mc4yzz5cvpxw07b3%22%7D; cX_P=mc4yzz5cvpxw07b3; djcs_route=966396ea-5edb-4ce1-a7a5-26117bf651a0; TR=V2-c9d47073af3b9588751977fe4fbcf20f724a9bc94c79daba415c2eeb74a88ae0; djcs_auto=M1750367024%2FvqcMb8aJqCyDvD%2Bp4%2Fvy%2BJiAFKg5fZvadNlW5%2B6tPob1Ux%2F8CxJVZxpM3o7j2vhZOAMILVme9%2FLQlzzu9y8IKXamsLI7pQb%2FQ5M1MihrPMEk3sF9GGfMqFopxSs3%2BIt%2B1DUxn82dVaLUw7uKUk%2FiDTjS%2BzmL1XBKGa94d6bhelFEArIjIwCRNSZ2GAuc07sfEiDsMOrV8J1clJPuxicJ3dT879yl2tTfW2PxOI%2FfaIj6asUD0iUKcDIHsTi0HUv7%2F5qVvr76vbBnMftizItPBra55qpyQNAo8SNb2H0eBMD05Qkn0PRW%2Fuwi2gP2m6aO7QR%2BmMGp6HOUTU2sDzPUDB%2Bi5aJjS%2Fa0sYi0Djc446J79jy0mgplfbnJ%2BG32U%2BH0235i4ZIQdOnYwPoK5gR%2FJ%2FdJhA6Z%2BUMFTa%2FP3iYgc6Yv%2BWqeDBSaV5%2BVF%2BiTEr7sCa1uKl8JP3pg82rvoUB1gQ%3D%3DG; djcs_session=M1750430628%2F59I8D%2Bl49KcBfDxwh6Bp6FxgsnCYIPy6KL%2FM2PeI%2By7uZtzgKNyoQi6T2%2B0dCheRYYyxH29OJyBE3%2FeAX%2FjxxQoq2xitSco3%2F1Yu98h8iT1ea%2BUDtUMutK6qEqEhdTdjv8b0AAomqZw9HvBNkUIiZdc%2BFk16EsM0dYEzQaikaR7eD6HPTdt8jjVguKTFPc9mDM9bGBXKSftZN4iREbJ7prR%2Fkyy1gp3KD8WhH4jIfFBihOZRFdfcfxDLPdIL0wiPwhDWC%2BX0u75dHAQTtWBtf7ZgmKnMYBXrET4F5A3f17HQKOFNIIXERXF9RUzpxuRqHKR6CzK9dI6jElmJ9RiVuBp92HnnDglpM4RSiMyYNXyhP412z7m%2FL%2BfETluZNmbEK1j0mLOqIVkyhJbrNYjdCXDTDZmqH1BY03rXvN%2F5Hy17x%2F2BIoV9ayTyIYhVBC%2B9urxtiNHh66W1lyCqzLw8ETsxvw%2F9CvH8DrL8x1OU%2BOnM2%2FPhtdZnnbny0lmVyz%2FC3Lba8Jfhm1FCdjmIB%2F3cdvB9AoI6c6X0qixmGLJiRwz6%2FltWTlkv8bQzjrKIwSoNQ8amCyipAt4OdsJygpz7zw%3D%3DG; ab_uuid=05588ce5-0f6c-487b-8ab8-1426ce30f17d; wsjregion=na%2Cus; gdprApplies=false; ccpaApplies=false; vcdpaApplies=false; regulationApplies=gdpr%3Afalse%2Ccpra%3Afalse%2Cvcdpa%3Afalse; refresh=off; letsGetMikey=enabled; ca_rt=IXv-C9jkFcy69fAikw1gqQ._JN4amJoBEkZaLYOCmOf4FgJ_QMP9UsJgIiVG650EAEARkpvB2Uv7qoK26shrmbCz7JTQqbZw6fvODc8Gz6M1Y9DpnkxJesQ9ImPL1iXK00; datadome=~F9hNrk0f_vF7i04F4qXVPSkq5tnV4~PETGvgBlCfxSAw1uuyDsRaXhSU0Q6N0_lM1n6vcvQMjEB09yBTaKyCCe_FJjeyvXTzRIFHW50r2pjWnZ3rQG8g4QFPxcm3QkA; mw_loc=%7B%22Region%22%3A%22WI%22%2C%22Country%22%3A%22US%22%2C%22Continent%22%3A%22NA%22%2C%22ApplicablePrivacy%22%3A0%7D; ca_id=0f7b9586-b922-4403-8396-039962f63385.eJw9kFFTwjAQhP9Lnim0acolPNmRIjgKiKIjjsNc04RGSsE2UNHxvxtw9PW7vd29-yIrc1DlssSNIj2S2BxL0iIaN6Y4_tHhdl-rZlvZ3I3UBk3hoMr_6UXVpGiqrC23G6fY703mBJSikj5DL4PU95hPucdRUi8QPk8lDyHTwqlthXJ9XpAiY-BDiDpMRcQ5RIEA0IrpVGrqa6AMRSoFkyAyTJEFkaRKpcCQc1S-M6u2hapJ74UMZkkyS6680bg_ehz15_ENeW0R3Nt8ac3pqAAin4UhB2iR-hz_qSdGHxfjYjmZjrzZqoTo4SmOg9tDsTP5MHMbRz25vly_w3wa30MyeMbFnQuVlUKrsiXaky0TEdBu5GzNL4gCLrquq3vdx-4MaEj5GZjalSW5tbu61-k0TdNu6rfTFzuyMKq05PsHv4596Q.LM5NCaU8KolC1aMqQPq7IAn2KVUV412PMHi2EeqQN2c-nQLSN8DtUvYE8bkT4Ou4WUpwHm94nJVkniYt1zYG_NdGWBnOMcAruqnjVtpdRwkLRVM-ACeoPuAPL9W341xCNrDUDYOHBeMKSZRIJe7jCG3rj5zxrsHKs4qrsArOOtDWMKPqNxGNeXBYcOVoMgbTEY4Yn5RKxn2EF7IaAq9HOmP4d44l4D8ZaQ8SafuOajVTF9B5o1r7hQ8O9j4i96rVYb9Ehzk2Y6dj1UHiYXgjdUYPY5vQ4KmrjC4mIAgXMhP5pjkDH66AFIa2Mr_yJ9QLv_vY24npiKXVGjuRvkuJrA; icons-loaded=true; usr_prof_v2=eyJpYyI6NH0%3D',
            'dnt': '1',
            'priority': 'u=0, i',
            'referer': 'https://www.marketwatch.com/games/baird-pwm-intern-stock-market-competition',
            'sec-ch-device-memory': '8',
            'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138"',
            'sec-ch-ua-arch': '"arm"',
            'sec-ch-ua-full-version-list': '"Not)A;Brand";v="8.0.0.0", "Chromium";v="138.0.7204.93"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-model': '""',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36'
        }
    
    def get_portfolio_performance(self) -> Optional[PortfolioData]:
        """
        Fetch portfolio performance data from MarketWatch API.
        
        Returns:
            PortfolioData object containing portfolio metrics, or None if error
        """
        url = f"{self.base_url}/statistics/portfolioPerformance"
        params = {
            'gameUri': self.game_uri,
            'publicId': self.public_id
        }
        
        try:
            response = requests.get(url, params=params, headers=self.api_headers)
            response.raise_for_status()
            
            data = response.json()
            
            # Also fetch transaction data from HTML and CSV
            transactions = self.get_transactions()
            
            # Try to get CSV data if HTML parsing fails
            if not transactions:
                csv_transactions = self.get_transactions_csv()
                if csv_transactions:
                    transactions = csv_transactions
            
            portfolio_data = self._parse_portfolio_data(data)
            portfolio_data.transactions = transactions or []
            
            return portfolio_data
            
        except requests.RequestException as e:
            print(f"Error fetching portfolio data: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            return None
    
    def _parse_portfolio_data(self, data: Dict[str, Any]) -> PortfolioData:
        """
        Parse API response into PortfolioData object.
        
        Args:
            data: JSON response from API
            
        Returns:
            PortfolioData object
        """
        # Extract basic info
        public_id = data.get('data', {}).get('publicId', '')
        values = data.get('data', {}).get('values', [])
        
        # Parse daily performance data
        daily_performance = []
        for value in values:
            daily_performance.append(DailyPerformance(
                date=value.get('d', ''),
                portfolio_value=value.get('w', 0.0),
                percentage_return=value.get('p', 0.0),
                dollar_gain=value.get('g', 0.0),
                rank=value.get('r', 0)
            ))
        
        # Get latest values (most recent entry)
        if daily_performance:
            latest = daily_performance[-1]
            current_value = latest.portfolio_value
            current_return_percentage = latest.percentage_return
            current_dollar_gain = latest.dollar_gain
            current_rank = latest.rank
        else:
            current_value = 0.0
            current_return_percentage = 0.0
            current_dollar_gain = 0.0
            current_rank = 0
        
        return PortfolioData(
            public_id=public_id,
            current_value=current_value,
            current_return_percentage=current_return_percentage,
            current_dollar_gain=current_dollar_gain,
            current_rank=current_rank,
            daily_performance=daily_performance,
            transactions=[],  # Will be populated by get_portfolio_performance
            timestamp=datetime.now()
        )
    
    def get_portfolio_json(self) -> Optional[Dict[str, Any]]:
        """
        Get raw JSON response from portfolio performance API.
        
        Returns:
            Raw JSON data or None if error
        """
        url = f"{self.base_url}/statistics/portfolioPerformance"
        params = {
            'gameUri': self.game_uri,
            'publicId': self.public_id
        }
        
        try:
            response = requests.get(url, params=params, headers=self.api_headers)
            response.raise_for_status()
            return response.json()
            
        except requests.RequestException as e:
            print(f"Error fetching portfolio data: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            return None
    
    def get_transactions(self, debug: bool = False) -> Optional[List[Transaction]]:
        """
        Fetch transaction history from MarketWatch HTML page.
        
        Args:
            debug: If True, print debugging information
        
        Returns:
            List of Transaction objects, or None if error
        """
        try:
            response = requests.get(self.portfolio_url, headers=self.html_headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            return self._parse_transactions(soup, debug=debug)
            
        except requests.RequestException as e:
            print(f"Error fetching portfolio HTML: {e}")
            return None
        except Exception as e:
            print(f"Error parsing transactions: {e}")
            return None
    
    def get_transactions_csv(self) -> Optional[List[Transaction]]:
        """
        Fetch transaction data from CSV download endpoint.
        
        Returns:
            List of Transaction objects, or None if error
        """
        csv_url = f"https://www.marketwatch.com/games/{self.game_uri}/download"
        params = {
            'view': 'transactions',
            'pub': self.public_id,
            'isDownload': 'true'
        }
        
        try:
            response = requests.get(csv_url, params=params, headers=self.html_headers)
            response.raise_for_status()
            
            return self._parse_transactions_csv(response.text)
            
        except requests.RequestException as e:
            print(f"Error fetching CSV transaction data: {e}")
            return None
        except Exception as e:
            print(f"Error parsing CSV transactions: {e}")
            return None
    
    def _parse_transactions_csv(self, csv_content: str) -> List[Transaction]:
        """Parse transactions from CSV content."""
        transactions = []
        
        try:
            import csv
            from io import StringIO
            
            csv_reader = csv.DictReader(StringIO(csv_content))
            
            for row in csv_reader:
                # Parse CSV row into Transaction object
                # This will need to be adjusted based on actual CSV structure
                transaction = Transaction(
                    symbol=row.get('Symbol', ''),
                    order_date=row.get('Order Date/Time', ''),
                    transaction_date=row.get('Transaction Date/Time', ''),
                    action=row.get('Type', ''),
                    amount=int(row.get('Amount', '0').replace(',', '')) if row.get('Amount', '0').replace(',', '').isdigit() else 0,
                    price=row.get('Ex. Price', ''),
                    status="Completed"  # Default status
                )
                transactions.append(transaction)
                
        except Exception as e:
            print(f"Error parsing CSV: {e}")
            return []
        
        return transactions
    
    def _parse_transactions(self, soup: BeautifulSoup, debug: bool = False) -> List[Transaction]:
        """
        Parse transaction data from HTML.
        
        Args:
            soup: BeautifulSoup object of the portfolio page
            debug: If True, print debugging information
            
        Returns:
            List of Transaction objects
        """
        transactions = []
        
        if debug:
            print("=== Transaction Parsing Debug ===")
            # Analyze all tables
            tables = soup.find_all('table')
            print(f"Found {len(tables)} tables total:")
            for i, table in enumerate(tables):
                table_classes = table.get('class', [])
                table_id = table.get('id', 'None')
                rows = table.find_all('tr')
                print(f"  Table {i+1}: classes={table_classes}, id={table_id}, rows={len(rows)}")
                
                if rows:
                    # Show first row (headers)
                    first_row_cells = rows[0].find_all(['th', 'td'])
                    headers = [cell.get_text(strip=True) for cell in first_row_cells]
                    print(f"    Headers: {headers}")
                    
                    # Check if this looks like a transaction table
                    table_text = table.get_text().lower()
                    transaction_keywords = ['symbol', 'order', 'transaction', 'buy', 'sell', 'short', 'amount', 'price', 'type']
                    matching_keywords = [kw for kw in transaction_keywords if kw in table_text]
                    if matching_keywords:
                        print(f"    *** POTENTIAL TRANSACTION TABLE: keywords={matching_keywords} ***")
            
            # Look for vse-module elements
            vse_modules = soup.find_all(attrs={'is': 'vse-module'})
            print(f"\nFound {len(vse_modules)} vse-module elements:")
            for i, module in enumerate(vse_modules):
                view = module.get('view', 'None')
                module_classes = module.get('class', [])
                print(f"  Module {i+1}: view={view}, classes={module_classes}")
                if view == 'transactions':
                    print(f"    *** TRANSACTION MODULE FOUND ***")
        
        # Look for script tags that might contain transaction data
        for script in soup.find_all('script'):
            if script.string:
                # Look for JSON data that might contain transactions
                if 'transactions' in script.string.lower() or 'orders' in script.string.lower():
                    # Try to extract JSON from script
                    try:
                        # Find JSON-like patterns in the script
                        json_match = re.search(r'({.*?})', script.string, re.DOTALL)
                        if json_match:
                            json_str = json_match.group(1)
                            data = json.loads(json_str)
                            # Parse transaction data from JSON
                            transactions.extend(self._parse_transaction_json(data))
                    except (json.JSONDecodeError, Exception):
                        continue
        
        # Look for HTML table with transaction data
        # First, look for the specific table structure with class "table table--primary ranking"
        table = soup.find('table', {'class': 'table table--primary ranking'})
        if not table:
            # Fallback to broader search
            table = soup.find('table', {'class': re.compile(r'.*transaction.*|.*order.*|.*trade.*', re.I)})
        
        if table:
            if debug:
                print(f"\nParsing transaction table with classes: {table.get('class', [])}")
            transactions.extend(self._parse_transaction_table(table))
        
        # Look for div containers with transaction data
        for div in soup.find_all('div', {'class': re.compile(r'.*transaction.*|.*order.*|.*trade.*', re.I)}):
            transactions.extend(self._parse_transaction_div(div))
        
        # Look specifically for vse-module with view="transactions"
        for module in soup.find_all(attrs={'is': 'vse-module'}):
            if module.get('view') == 'transactions':
                if debug:
                    print(f"\nFound vse-module with view=transactions")
                # Look for tables inside this module
                module_tables = module.find_all('table')
                for table in module_tables:
                    transactions.extend(self._parse_transaction_table(table))
        
        return transactions
    
    def _parse_transaction_json(self, data: Dict[str, Any]) -> List[Transaction]:
        """Parse transactions from JSON data."""
        transactions = []
        # This will need to be implemented based on the actual JSON structure
        return transactions
    
    def _parse_transaction_table(self, table) -> List[Transaction]:
        """Parse transactions from HTML table."""
        transactions = []
        
        rows = table.find_all('tr')
        for row in rows[1:]:  # Skip header row
            cells = row.find_all(['td', 'th'])
            if len(cells) >= 6:  # Expected columns: Symbol, Order Date, Transaction Date, Type, Amount, Price
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
                    print(f"Error parsing transaction row: {e}")
                    continue
        
        return transactions
    
    def _parse_transaction_div(self, div) -> List[Transaction]:
        """Parse transactions from div containers."""
        transactions = []
        # This will need to be implemented based on the actual HTML structure
        return transactions


def main():
    """Example usage of the MarketWatch scraper."""
    
    # Your competition details from the curl request
    game_uri = "baird-pwm-intern-stock-market-competition"
    public_id = "-Ct8JFv9TYip"
    
    # Create scraper instance
    scraper = MarketWatchScraper(game_uri, public_id)
    
    # Get portfolio performance data
    portfolio_data = scraper.get_portfolio_performance()
    
    if portfolio_data:
        print("Portfolio Performance:")
        print(f"  Public ID: {portfolio_data.public_id}")
        print(f"  Current Value: ${portfolio_data.current_value:,.2f}")
        print(f"  Current Return: ${portfolio_data.current_dollar_gain:,.2f}")
        print(f"  Current Return %: {portfolio_data.current_return_percentage:.2f}%")
        print(f"  Current Rank: {portfolio_data.current_rank}")
        print(f"  Timestamp: {portfolio_data.timestamp}")
        
        print(f"\nTransaction History ({len(portfolio_data.transactions)} transactions):")
        for i, transaction in enumerate(portfolio_data.transactions[:10]):  # Show first 10
            price_str = transaction.price if transaction.price != 'N/A' else 'N/A'
            status_str = f" [{transaction.status}]" if transaction.status != "Completed" else ""
            print(f"  {i+1}. {transaction.symbol} - {transaction.action} {transaction.amount:,} shares at {price_str}{status_str}")
            print(f"     Order: {transaction.order_date} | Transaction: {transaction.transaction_date}")
        
        if len(portfolio_data.transactions) > 10:
            print(f"  ... and {len(portfolio_data.transactions) - 10} more transactions")
    else:
        print("Failed to fetch portfolio data")
    
    # Get raw JSON for inspection
    print("\nRaw JSON Response:")
    raw_data = scraper.get_portfolio_json()
    if raw_data:
        print(json.dumps(raw_data, indent=2))


if __name__ == "__main__":
    main()