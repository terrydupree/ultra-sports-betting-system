"""
API Manager for data acquisition across multiple sports APIs
"""

import requests
import pandas as pd
from typing import Dict, List, Optional, Any
from datetime import datetime
import json

from core.utils.rate_limiter import RateLimiter
from core.utils.logger import get_logger


class APIManager:
    """
    Centralized API management for multiple sports data sources.
    """
    
    def __init__(self):
        """Initialize API manager with rate limiting and logging."""
        self.logger = get_logger("api_manager")
        self.rate_limiters = {}
        self.api_configs = self._load_api_configs()
        self.session = requests.Session()
        
        # Setup default headers
        self.session.headers.update({
            'User-Agent': 'Ultra-Sports-Betting-System/1.0',
            'Accept': 'application/json'
        })
    
    def _load_api_configs(self) -> Dict:
        """
        Load API configurations for different providers.
        
        Returns:
            Dictionary with API configurations
        """
        return {
            "espn": {
                "base_url": "https://site.api.espn.com/apis/site/v2/sports",
                "rate_limit": 60,  # calls per minute
                "timeout": 30
            },
            "sportsradar": {
                "base_url": "https://api.sportradar.us",
                "rate_limit": 60,
                "timeout": 30
            },
            "odds_api": {
                "base_url": "https://api.the-odds-api.com",
                "rate_limit": 500,  # varies by plan
                "timeout": 30
            }
        }
    
    def get_rate_limiter(self, provider: str) -> RateLimiter:
        """
        Get or create rate limiter for specific provider.
        
        Args:
            provider: API provider name
        
        Returns:
            RateLimiter instance
        """
        if provider not in self.rate_limiters:
            config = self.api_configs.get(provider, {})
            rate_limit = config.get("rate_limit", 60)
            self.rate_limiters[provider] = RateLimiter(rate_limit)
        
        return self.rate_limiters[provider]
    
    def make_request(
        self, 
        provider: str, 
        endpoint: str, 
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None
    ) -> Optional[Dict]:
        """
        Make API request with rate limiting and error handling.
        
        Args:
            provider: API provider name
            endpoint: API endpoint
            params: Query parameters
            headers: Additional headers
        
        Returns:
            API response data or None if failed
        """
        try:
            # Rate limiting
            rate_limiter = self.get_rate_limiter(provider)
            rate_limiter.wait_if_needed()
            
            # Build URL
            config = self.api_configs.get(provider, {})
            base_url = config.get("base_url", "")
            url = f"{base_url}/{endpoint.lstrip('/')}"
            
            # Merge headers
            request_headers = {}
            if headers:
                request_headers.update(headers)
            
            # Make request
            timeout = config.get("timeout", 30)
            response = self.session.get(
                url, 
                params=params or {}, 
                headers=request_headers,
                timeout=timeout
            )
            
            response.raise_for_status()
            
            self.logger.info(f"Successfully fetched data from {provider}: {endpoint}")
            return response.json()
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"API request failed for {provider}: {e}")
            return None
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON decode error for {provider}: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error for {provider}: {e}")
            return None
    
    def fetch_espn_games(self, sport: str, date: Optional[str] = None) -> List[Dict]:
        """
        Fetch games from ESPN API.
        
        Args:
            sport: Sport name (mlb, nfl, nba, etc.)
            date: Date in YYYYMMDD format
        
        Returns:
            List of game dictionaries
        """
        endpoint = f"{sport}/scoreboard"
        params = {}
        
        if date:
            params["dates"] = date
        
        data = self.make_request("espn", endpoint, params)
        
        if data and "events" in data:
            return data["events"]
        
        return []
    
    def fetch_team_stats(self, provider: str, sport: str, team_id: str) -> Optional[Dict]:
        """
        Fetch team statistics from specified provider.
        
        Args:
            provider: API provider name
            sport: Sport name
            team_id: Team identifier
        
        Returns:
            Team statistics dictionary or None
        """
        if provider == "espn":
            endpoint = f"{sport}/teams/{team_id}/statistics"
            return self.make_request("espn", endpoint)
        
        return None
    
    def fetch_odds(self, sport: str, bookmaker: Optional[str] = None) -> List[Dict]:
        """
        Fetch current odds from odds API.
        
        Args:
            sport: Sport key (e.g., 'baseball_mlb', 'americanfootball_nfl')
            bookmaker: Specific bookmaker to filter by
        
        Returns:
            List of odds dictionaries
        """
        endpoint = f"v4/sports/{sport}/odds"
        params = {
            "regions": "us",
            "markets": "h2h,spreads,totals",
            "oddsFormat": "american"
        }
        
        if bookmaker:
            params["bookmakers"] = bookmaker
        
        data = self.make_request("odds_api", endpoint, params)
        
        if data and isinstance(data, list):
            return data
        
        return []
    
    def get_available_sports(self, provider: str = "espn") -> List[str]:
        """
        Get list of available sports from provider.
        
        Args:
            provider: API provider name
        
        Returns:
            List of available sport names
        """
        if provider == "espn":
            # ESPN supports these major sports
            return ["mlb", "nfl", "nba", "nhl", "soccer", "tennis", "golf"]
        elif provider == "odds_api":
            endpoint = "v4/sports"
            data = self.make_request("odds_api", endpoint)
            if data:
                return [sport["key"] for sport in data]
        
        return []
    
    def health_check(self) -> Dict[str, bool]:
        """
        Check health status of all configured APIs.
        
        Returns:
            Dictionary with provider health status
        """
        health_status = {}
        
        for provider in self.api_configs.keys():
            try:
                # Make a simple request to test connectivity
                if provider == "espn":
                    result = self.make_request("espn", "mlb/scoreboard")
                    health_status[provider] = result is not None
                elif provider == "odds_api":
                    result = self.make_request("odds_api", "v4/sports")
                    health_status[provider] = result is not None
                else:
                    health_status[provider] = False
                    
            except Exception as e:
                self.logger.error(f"Health check failed for {provider}: {e}")
                health_status[provider] = False
        
        return health_status