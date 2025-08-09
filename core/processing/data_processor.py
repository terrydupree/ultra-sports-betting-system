"""
Data processing engine for normalizing and cleaning sports data
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
import json

from core.utils.logger import get_logger


class DataProcessor:
    """
    Main data processing engine for sports betting analysis.
    """
    
    def __init__(self):
        """Initialize data processor with logging."""
        self.logger = get_logger("data_processor")
        self.sport_mappings = self._load_sport_mappings()
    
    def _load_sport_mappings(self) -> Dict:
        """
        Load sport-specific data mappings and transformations.
        
        Returns:
            Dictionary with sport mappings
        """
        return {
            "mlb": {
                "team_name_mappings": {
                    "LAA": "Los Angeles Angels",
                    "LAD": "Los Angeles Dodgers",
                    "NYY": "New York Yankees",
                    "NYM": "New York Mets",
                    # Add more mappings as needed
                },
                "stat_mappings": {
                    "runs": "points_scored",
                    "era": "pitcher_era",
                    "avg": "batting_average"
                }
            },
            "nfl": {
                "team_name_mappings": {
                    "NE": "New England Patriots",
                    "GB": "Green Bay Packers",
                    "KC": "Kansas City Chiefs",
                    # Add more mappings as needed
                },
                "stat_mappings": {
                    "touchdowns": "points_scored",
                    "yards": "total_yards",
                    "turnovers": "turnovers"
                }
            },
            "nba": {
                "team_name_mappings": {
                    "LAL": "Los Angeles Lakers",
                    "GSW": "Golden State Warriors",
                    "BOS": "Boston Celtics",
                    # Add more mappings as needed
                },
                "stat_mappings": {
                    "points": "points_scored",
                    "rebounds": "total_rebounds",
                    "assists": "assists"
                }
            }
        }
    
    def normalize_team_name(self, team_name: str, sport: str) -> str:
        """
        Normalize team name using sport-specific mappings.
        
        Args:
            team_name: Original team name
            sport: Sport name
        
        Returns:
            Normalized team name
        """
        mappings = self.sport_mappings.get(sport, {}).get("team_name_mappings", {})
        return mappings.get(team_name, team_name)
    
    def normalize_game_data(self, raw_data: List[Dict], sport: str) -> pd.DataFrame:
        """
        Normalize game data from API responses.
        
        Args:
            raw_data: Raw game data from API
            sport: Sport name
        
        Returns:
            Normalized DataFrame
        """
        try:
            normalized_games = []
            
            for game in raw_data:
                normalized_game = self._normalize_single_game(game, sport)
                if normalized_game:
                    normalized_games.append(normalized_game)
            
            if normalized_games:
                df = pd.DataFrame(normalized_games)
                df = self._add_derived_features(df, sport)
                return df
            else:
                return pd.DataFrame()
                
        except Exception as e:
            self.logger.error(f"Error normalizing game data for {sport}: {e}")
            return pd.DataFrame()
    
    def _normalize_single_game(self, game: Dict, sport: str) -> Optional[Dict]:
        """
        Normalize a single game record.
        
        Args:
            game: Single game dictionary
            sport: Sport name
        
        Returns:
            Normalized game dictionary or None
        """
        try:
            # Extract common fields
            normalized = {
                "game_id": game.get("id", ""),
                "sport": sport,
                "date": self._extract_game_date(game),
                "status": game.get("status", {}).get("type", {}).get("name", ""),
                "home_team": "",
                "away_team": "",
                "home_score": 0,
                "away_score": 0,
                "is_completed": False
            }
            
            # Extract teams (ESPN format)
            if "competitions" in game and len(game["competitions"]) > 0:
                competition = game["competitions"][0]
                competitors = competition.get("competitors", [])
                
                for competitor in competitors:
                    team_name = competitor.get("team", {}).get("displayName", "")
                    team_name = self.normalize_team_name(team_name, sport)
                    score = int(competitor.get("score", 0))
                    
                    if competitor.get("homeAway") == "home":
                        normalized["home_team"] = team_name
                        normalized["home_score"] = score
                    else:
                        normalized["away_team"] = team_name
                        normalized["away_score"] = score
                
                # Check if game is completed
                normalized["is_completed"] = competition.get("status", {}).get("type", {}).get("completed", False)
            
            # Validate required fields
            if normalized["home_team"] and normalized["away_team"]:
                return normalized
            else:
                self.logger.warning(f"Missing team information for game {normalized['game_id']}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error normalizing single game: {e}")
            return None
    
    def _extract_game_date(self, game: Dict) -> str:
        """
        Extract and normalize game date.
        
        Args:
            game: Game dictionary
        
        Returns:
            Normalized date string (YYYY-MM-DD)
        """
        try:
            date_str = game.get("date", "")
            if date_str:
                # Parse ISO format date
                dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                return dt.strftime("%Y-%m-%d")
            else:
                return datetime.now().strftime("%Y-%m-%d")
        except Exception as e:
            self.logger.warning(f"Error parsing game date: {e}")
            return datetime.now().strftime("%Y-%m-%d")
    
    def _add_derived_features(self, df: pd.DataFrame, sport: str) -> pd.DataFrame:
        """
        Add derived features to the DataFrame.
        
        Args:
            df: Game data DataFrame
            sport: Sport name
        
        Returns:
            DataFrame with derived features
        """
        try:
            # Add total score
            df["total_score"] = df["home_score"] + df["away_score"]
            
            # Add score differential
            df["score_differential"] = df["home_score"] - df["away_score"]
            
            # Add winner
            df["winner"] = np.where(
                df["home_score"] > df["away_score"],
                df["home_team"],
                np.where(
                    df["away_score"] > df["home_score"],
                    df["away_team"],
                    "Tie"
                )
            )
            
            # Add game result for home team
            df["home_team_result"] = np.where(
                df["home_score"] > df["away_score"],
                "Win",
                np.where(
                    df["away_score"] > df["home_score"],
                    "Loss",
                    "Tie"
                )
            )
            
            # Add sport-specific derived features
            if sport == "mlb":
                df = self._add_mlb_features(df)
            elif sport == "nfl":
                df = self._add_nfl_features(df)
            elif sport == "nba":
                df = self._add_nba_features(df)
            
            return df
            
        except Exception as e:
            self.logger.error(f"Error adding derived features: {e}")
            return df
    
    def _add_mlb_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add MLB-specific derived features."""
        # High/low scoring game classification
        df["is_high_scoring"] = df["total_score"] > 9
        df["is_low_scoring"] = df["total_score"] < 7
        return df
    
    def _add_nfl_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add NFL-specific derived features."""
        # High/low scoring game classification
        df["is_high_scoring"] = df["total_score"] > 45
        df["is_low_scoring"] = df["total_score"] < 35
        df["is_blowout"] = abs(df["score_differential"]) > 14
        return df
    
    def _add_nba_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add NBA-specific derived features."""
        # High/low scoring game classification
        df["is_high_scoring"] = df["total_score"] > 220
        df["is_low_scoring"] = df["total_score"] < 200
        df["is_close_game"] = abs(df["score_differential"]) <= 5
        return df
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and validate data quality.
        
        Args:
            df: Input DataFrame
        
        Returns:
            Cleaned DataFrame
        """
        try:
            original_length = len(df)
            
            # Remove duplicates
            df = df.drop_duplicates(subset=["game_id"], keep="first")
            
            # Remove rows with missing critical data
            df = df.dropna(subset=["home_team", "away_team", "date"])
            
            # Validate scores are non-negative
            df = df[(df["home_score"] >= 0) & (df["away_score"] >= 0)]
            
            # Convert data types
            df["date"] = pd.to_datetime(df["date"])
            df["home_score"] = df["home_score"].astype(int)
            df["away_score"] = df["away_score"].astype(int)
            
            cleaned_length = len(df)
            removed_count = original_length - cleaned_length
            
            if removed_count > 0:
                self.logger.info(f"Removed {removed_count} invalid records during cleaning")
            
            return df
            
        except Exception as e:
            self.logger.error(f"Error cleaning data: {e}")
            return df
    
    def aggregate_team_stats(self, df: pd.DataFrame, team_name: str) -> Dict:
        """
        Aggregate statistics for a specific team.
        
        Args:
            df: Game data DataFrame
            team_name: Name of the team
        
        Returns:
            Dictionary with aggregated team statistics
        """
        try:
            # Filter games for this team
            team_games = df[
                (df["home_team"] == team_name) | (df["away_team"] == team_name)
            ].copy()
            
            if team_games.empty:
                return {}
            
            # Calculate basic stats
            total_games = len(team_games)
            
            # Home/away splits
            home_games = team_games[team_games["home_team"] == team_name]
            away_games = team_games[team_games["away_team"] == team_name]
            
            # Win/loss record
            wins = len(team_games[
                ((team_games["home_team"] == team_name) & (team_games["home_team_result"] == "Win")) |
                ((team_games["away_team"] == team_name) & (team_games["home_team_result"] == "Loss"))
            ])
            
            losses = len(team_games[
                ((team_games["home_team"] == team_name) & (team_games["home_team_result"] == "Loss")) |
                ((team_games["away_team"] == team_name) & (team_games["home_team_result"] == "Win"))
            ])
            
            # Scoring stats
            team_scores = []
            opponent_scores = []
            
            for _, game in team_games.iterrows():
                if game["home_team"] == team_name:
                    team_scores.append(game["home_score"])
                    opponent_scores.append(game["away_score"])
                else:
                    team_scores.append(game["away_score"])
                    opponent_scores.append(game["home_score"])
            
            stats = {
                "team_name": team_name,
                "total_games": total_games,
                "wins": wins,
                "losses": losses,
                "win_percentage": wins / total_games if total_games > 0 else 0,
                "home_games": len(home_games),
                "away_games": len(away_games),
                "avg_points_scored": np.mean(team_scores) if team_scores else 0,
                "avg_points_allowed": np.mean(opponent_scores) if opponent_scores else 0,
                "total_points_scored": sum(team_scores),
                "total_points_allowed": sum(opponent_scores),
                "point_differential": sum(team_scores) - sum(opponent_scores)
            }
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error aggregating team stats for {team_name}: {e}")
            return {}