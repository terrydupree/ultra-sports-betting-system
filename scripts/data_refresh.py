#!/usr/bin/env python3
"""
Data refresh script for Ultra Sports Betting System
Refreshes data for all configured sports
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, List
import argparse

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.data_acquisition.api_manager import APIManager
from core.processing.data_processor import DataProcessor
from core.utils.logger import get_logger


class DataRefreshManager:
    """
    Manages data refresh operations for all sports.
    """
    
    def __init__(self):
        """Initialize data refresh manager."""
        self.logger = get_logger("data_refresh_manager")
        self.api_manager = APIManager()
        self.data_processor = DataProcessor()
        self.supported_sports = ["mlb", "nfl", "nba", "nhl", "soccer", "tennis", "golf"]
    
    async def refresh_sport_data(self, sport: str, days_back: int = 7) -> bool:
        """
        Refresh data for a specific sport.
        
        Args:
            sport: Sport name to refresh
            days_back: Number of days back to fetch data
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.logger.info(f"Starting data refresh for {sport.upper()}")
            
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)
            
            # Fetch recent games
            games_data = []
            for i in range(days_back):
                current_date = start_date + timedelta(days=i)
                date_str = current_date.strftime("%Y%m%d")
                
                daily_games = self.api_manager.fetch_espn_games(sport, date_str)
                games_data.extend(daily_games)
                
                # Small delay to respect rate limits
                await asyncio.sleep(0.1)
            
            if games_data:
                # Process and normalize data
                processed_data = self.data_processor.normalize_game_data(games_data, sport)
                cleaned_data = self.data_processor.clean_data(processed_data)
                
                self.logger.info(f"Processed {len(cleaned_data)} games for {sport.upper()}")
                
                # Save to database (placeholder - implement based on your database choice)
                await self._save_to_database(cleaned_data, sport)
                
                return True
            else:
                self.logger.warning(f"No data found for {sport.upper()}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error refreshing data for {sport}: {e}")
            return False
    
    async def refresh_odds_data(self) -> bool:
        """
        Refresh current odds data for all sports.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.logger.info("Starting odds data refresh")
            
            # Mapping of our sport names to odds API sport keys
            odds_sport_mapping = {
                "mlb": "baseball_mlb",
                "nfl": "americanfootball_nfl",
                "nba": "basketball_nba",
                "nhl": "icehockey_nhl",
                "soccer": "soccer_epl"  # Premier League as example
            }
            
            for sport, odds_key in odds_sport_mapping.items():
                try:
                    odds_data = self.api_manager.fetch_odds(odds_key)
                    
                    if odds_data:
                        self.logger.info(f"Fetched odds for {len(odds_data)} {sport.upper()} games")
                        
                        # Save odds to database (placeholder)
                        await self._save_odds_to_database(odds_data, sport)
                        
                        # Small delay between sports
                        await asyncio.sleep(1)
                    
                except Exception as e:
                    self.logger.error(f"Error fetching odds for {sport}: {e}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error refreshing odds data: {e}")
            return False
    
    async def _save_to_database(self, data, sport: str) -> None:
        """
        Save processed data to database.
        
        Args:
            data: Processed game data DataFrame
            sport: Sport name
        """
        # Placeholder for database save operation
        # Implement based on your chosen database (PostgreSQL, SQLite, etc.)
        self.logger.info(f"Saving {len(data)} records to database for {sport}")
        
        # Example implementation would go here:
        # async with database.transaction():
        #     await database.executemany(insert_query, data.to_dict('records'))
    
    async def _save_odds_to_database(self, odds_data: List[Dict], sport: str) -> None:
        """
        Save odds data to database.
        
        Args:
            odds_data: List of odds dictionaries
            sport: Sport name
        """
        # Placeholder for odds database save operation
        self.logger.info(f"Saving odds for {len(odds_data)} games to database for {sport}")
    
    async def health_check(self) -> Dict[str, bool]:
        """
        Perform health check on all data sources.
        
        Returns:
            Dictionary with health status for each source
        """
        self.logger.info("Performing data source health check")
        
        health_status = self.api_manager.health_check()
        
        # Log results
        for source, status in health_status.items():
            status_text = "✅ Healthy" if status else "❌ Unhealthy"
            self.logger.info(f"{source}: {status_text}")
        
        return health_status
    
    async def refresh_all_sports(self, days_back: int = 7) -> Dict[str, bool]:
        """
        Refresh data for all supported sports.
        
        Args:
            days_back: Number of days back to fetch data
        
        Returns:
            Dictionary with success status for each sport
        """
        self.logger.info("Starting data refresh for all sports")
        
        results = {}
        
        # Refresh game data for each sport
        for sport in self.supported_sports:
            try:
                success = await self.refresh_sport_data(sport, days_back)
                results[sport] = success
                
                # Delay between sports to respect rate limits
                await asyncio.sleep(2)
                
            except Exception as e:
                self.logger.error(f"Failed to refresh {sport}: {e}")
                results[sport] = False
        
        # Refresh odds data
        try:
            odds_success = await self.refresh_odds_data()
            results["odds"] = odds_success
        except Exception as e:
            self.logger.error(f"Failed to refresh odds: {e}")
            results["odds"] = False
        
        # Summary
        successful_sports = sum(1 for success in results.values() if success)
        total_operations = len(results)
        
        self.logger.info(f"Data refresh completed: {successful_sports}/{total_operations} successful")
        
        return results


async def main():
    """Main function for data refresh script."""
    parser = argparse.ArgumentParser(description="Ultra Sports Betting System Data Refresh")
    parser.add_argument("--sport", type=str, help="Specific sport to refresh (mlb, nfl, nba, etc.)")
    parser.add_argument("--days", type=int, default=7, help="Number of days back to fetch (default: 7)")
    parser.add_argument("--odds-only", action="store_true", help="Refresh only odds data")
    parser.add_argument("--health-check", action="store_true", help="Perform health check only")
    
    args = parser.parse_args()
    
    # Initialize manager
    refresh_manager = DataRefreshManager()
    
    try:
        if args.health_check:
            # Health check only
            await refresh_manager.health_check()
        
        elif args.odds_only:
            # Refresh odds only
            await refresh_manager.refresh_odds_data()
        
        elif args.sport:
            # Refresh specific sport
            if args.sport in refresh_manager.supported_sports:
                await refresh_manager.refresh_sport_data(args.sport, args.days)
            else:
                print(f"❌ Unsupported sport: {args.sport}")
                print(f"Supported sports: {', '.join(refresh_manager.supported_sports)}")
                sys.exit(1)
        
        else:
            # Refresh all sports
            await refresh_manager.refresh_all_sports(args.days)
        
        print("✅ Data refresh completed successfully")
        
    except KeyboardInterrupt:
        print("\n⚠️  Data refresh interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Data refresh failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())