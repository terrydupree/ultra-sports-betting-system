"""
MLB Analyzer Module for Ultra Sports Betting System
Enhanced MLB-specific analysis and prediction system
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import requests

from core.analysis.base_analyzer import BaseAnalyzer
from core.data_acquisition.api_manager import APIManager
from core.processing.data_processor import DataProcessor
from core.analysis.ev_calculator import EVCalculator
from core.utils.logger import get_logger


class MLBAnalyzer(BaseAnalyzer):
    """
    MLB-specific betting analysis and prediction system.
    """

    def __init__(self):
        super().__init__()
        self.logger = get_logger("mlb_analyzer")
        self.sport_name = "mlb"
        self.api_manager = APIManager()
        self.data_processor = DataProcessor()
        self.ev_calculator = EVCalculator()
        
        # MLB-specific configuration
        self.season_length = 162
        self.innings_per_game = 9
        self.positions = [
            "pitcher", "catcher", "first_base", "second_base", "third_base",
            "shortstop", "left_field", "center_field", "right_field", "designated_hitter"
        ]

    def fetch_game_data(self, date: Optional[str] = None) -> pd.DataFrame:
        """
        Fetch MLB game data for analysis.
        
        Args:
            date: Date to fetch data for (YYYY-MM-DD format)
        
        Returns:
            DataFrame with MLB game data
        """
        try:
            if date is None:
                date = datetime.now().strftime("%Y%m%d")
            else:
                # Convert YYYY-MM-DD to YYYYMMDD
                date = datetime.strptime(date, "%Y-%m-%d").strftime("%Y%m%d")
            
            # Fetch games from ESPN API
            raw_games = self.api_manager.fetch_espn_games("mlb", date)
            
            if raw_games:
                # Process and normalize
                processed_data = self.data_processor.normalize_game_data(raw_games, "mlb")
                cleaned_data = self.data_processor.clean_data(processed_data)
                
                # Add MLB-specific features
                cleaned_data = self._add_mlb_specific_features(cleaned_data)
                
                self.logger.info(f"Fetched {len(cleaned_data)} MLB games for {date}")
                return cleaned_data
            else:
                self.logger.warning(f"No MLB games found for {date}")
                return pd.DataFrame()
                
        except Exception as e:
            self.logger.error(f"Error fetching MLB game data: {e}")
            return pd.DataFrame()

    def _add_mlb_specific_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add MLB-specific features to the DataFrame.
        
        Args:
            df: Game data DataFrame
        
        Returns:
            DataFrame with MLB-specific features
        """
        try:
            # Game type classification
            df["is_day_game"] = df["date"].dt.hour < 18
            df["is_night_game"] = ~df["is_day_game"]
            df["is_doubleheader"] = df.duplicated(subset=["date", "home_team", "away_team"], keep=False)
            
            # Scoring patterns
            df["runs_scored_home"] = df["home_score"]
            df["runs_scored_away"] = df["away_score"]
            df["total_runs"] = df["total_score"]
            
            # Game result patterns
            df["is_shutout"] = (df["home_score"] == 0) | (df["away_score"] == 0)
            df["is_extra_innings"] = False  # Would need more detailed data
            df["run_differential"] = df["score_differential"]
            
            # Weather impact (placeholder - would need weather API)
            df["temperature"] = 72  # Default temperature
            df["wind_speed"] = 5    # Default wind speed
            df["is_dome"] = False   # Would need stadium data
            
            return df
            
        except Exception as e:
            self.logger.error(f"Error adding MLB-specific features: {e}")
            return df

    def calculate_team_stats(self, team_id: str) -> Dict:
        """
        Calculate comprehensive MLB team statistics.
        
        Args:
            team_id: MLB team identifier
        
        Returns:
            Dictionary with MLB team statistics
        """
        try:
            # Fetch recent games (last 30 days)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            
            # Get team games
            team_games = []
            for i in range(30):
                current_date = start_date + timedelta(days=i)
                date_str = current_date.strftime("%Y-%m-%d")
                daily_games = self.fetch_game_data(date_str)
                
                if not daily_games.empty:
                    team_daily_games = daily_games[
                        (daily_games["home_team"] == team_id) | 
                        (daily_games["away_team"] == team_id)
                    ]
                    team_games.append(team_daily_games)
            
            if team_games:
                all_team_games = pd.concat(team_games, ignore_index=True)
                
                # Use data processor for basic stats
                base_stats = self.data_processor.aggregate_team_stats(all_team_games, team_id)
                
                # Add MLB-specific stats
                mlb_stats = self._calculate_mlb_specific_stats(all_team_games, team_id)
                
                # Combine stats
                base_stats.update(mlb_stats)
                return base_stats
            else:
                return {"team_name": team_id, "error": "No recent games found"}
                
        except Exception as e:
            self.logger.error(f"Error calculating MLB team stats for {team_id}: {e}")
            return {"team_name": team_id, "error": str(e)}

    def _calculate_mlb_specific_stats(self, games_df: pd.DataFrame, team_id: str) -> Dict:
        """
        Calculate MLB-specific team statistics.
        
        Args:
            games_df: DataFrame with team's games
            team_id: Team identifier
        
        Returns:
            Dictionary with MLB-specific statistics
        """
        try:
            # Home/Away performance
            home_games = games_df[games_df["home_team"] == team_id]
            away_games = games_df[games_df["away_team"] == team_id]
            
            # Run statistics
            runs_scored = []
            runs_allowed = []
            
            for _, game in games_df.iterrows():
                if game["home_team"] == team_id:
                    runs_scored.append(game["home_score"])
                    runs_allowed.append(game["away_score"])
                else:
                    runs_scored.append(game["away_score"])
                    runs_allowed.append(game["home_score"])
            
            # Calculate MLB-specific metrics
            stats = {
                "runs_per_game": np.mean(runs_scored) if runs_scored else 0,
                "runs_allowed_per_game": np.mean(runs_allowed) if runs_allowed else 0,
                "run_differential_per_game": np.mean(runs_scored) - np.mean(runs_allowed) if runs_scored and runs_allowed else 0,
                "home_record": f"{len(home_games[home_games['home_team_result'] == 'Win'])}-{len(home_games[home_games['home_team_result'] == 'Loss'])}",
                "away_record": f"{len(away_games[away_games['home_team_result'] == 'Loss'])}-{len(away_games[away_games['home_team_result'] == 'Win'])}",
                "games_over_8_runs": len(games_df[games_df["total_runs"] > 8]),
                "games_under_7_runs": len(games_df[games_df["total_runs"] < 7]),
                "shutouts_pitched": len(games_df[
                    ((games_df["home_team"] == team_id) & (games_df["away_score"] == 0)) |
                    ((games_df["away_team"] == team_id) & (games_df["home_score"] == 0))
                ]),
                "shutouts_suffered": len(games_df[
                    ((games_df["home_team"] == team_id) & (games_df["home_score"] == 0)) |
                    ((games_df["away_team"] == team_id) & (games_df["away_score"] == 0))
                ]),
                "blowout_wins": len(games_df[
                    ((games_df["home_team"] == team_id) & (games_df["score_differential"] >= 5)) |
                    ((games_df["away_team"] == team_id) & (games_df["score_differential"] <= -5))
                ]),
                "one_run_games": len(games_df[abs(games_df["score_differential"]) == 1])
            }
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error calculating MLB-specific stats: {e}")
            return {}

    def predict_game_outcome(self, game_data: Dict) -> Dict:
        """
        Predict MLB game outcome with confidence intervals.
        
        Args:
            game_data: Game data dictionary
        
        Returns:
            Prediction results with confidence scores
        """
        try:
            home_team = game_data.get("home_team", "")
            away_team = game_data.get("away_team", "")
            
            # Get team statistics
            home_stats = self.calculate_team_stats(home_team)
            away_stats = self.calculate_team_stats(away_team)
            
            # Calculate basic prediction based on team performance
            home_runs_per_game = home_stats.get("runs_per_game", 4.5)
            away_runs_per_game = away_stats.get("runs_per_game", 4.5)
            home_runs_allowed = home_stats.get("runs_allowed_per_game", 4.5)
            away_runs_allowed = away_stats.get("runs_allowed_per_game", 4.5)
            
            # Predict runs scored
            predicted_home_runs = (home_runs_per_game + away_runs_allowed) / 2
            predicted_away_runs = (away_runs_per_game + home_runs_allowed) / 2
            
            # Home field advantage (approximately 0.1 runs in MLB)
            predicted_home_runs += 0.1
            
            # Calculate win probabilities
            # Using simple logistic model based on run differential
            run_diff = predicted_home_runs - predicted_away_runs
            home_win_prob = 1 / (1 + np.exp(-run_diff * 1.5))  # Sigmoid function
            away_win_prob = 1 - home_win_prob
            
            # Calculate total runs prediction
            predicted_total = predicted_home_runs + predicted_away_runs
            
            # Confidence based on team consistency
            home_consistency = 1 / (1 + home_stats.get("run_differential_per_game", 0))
            away_consistency = 1 / (1 + away_stats.get("run_differential_per_game", 0))
            confidence = min(home_consistency + away_consistency, 0.95)
            
            prediction = {
                "game_id": game_data.get("game_id", ""),
                "home_team": home_team,
                "away_team": away_team,
                "predicted_home_score": round(predicted_home_runs, 2),
                "predicted_away_score": round(predicted_away_runs, 2),
                "predicted_total_runs": round(predicted_total, 2),
                "home_win_probability": round(home_win_prob, 4),
                "away_win_probability": round(away_win_prob, 4),
                "confidence_score": round(confidence, 4),
                "prediction_date": datetime.now().isoformat(),
                "model_version": "mlb_basic_v1.0"
            }
            
            return prediction
            
        except Exception as e:
            self.logger.error(f"Error predicting MLB game outcome: {e}")
            return {"error": str(e)}

    def calculate_expected_value(self, odds: Dict, predictions: Dict) -> float:
        """
        Calculate expected value for MLB betting opportunities.
        
        Args:
            odds: Betting odds dictionary
            predictions: Model predictions dictionary
        
        Returns:
            Expected value as float
        """
        try:
            # Get predicted probabilities
            home_prob = predictions.get("home_win_probability", 0.5)
            away_prob = predictions.get("away_win_probability", 0.5)
            
            # Calculate EV for both teams
            home_odds = odds.get("home_team_odds", 0)
            away_odds = odds.get("away_team_odds", 0)
            
            home_ev = self.ev_calculator.calculate_expected_value(home_prob, home_odds)
            away_ev = self.ev_calculator.calculate_expected_value(away_prob, away_odds)
            
            # Return the better EV opportunity
            return max(home_ev, away_ev)
            
        except Exception as e:
            self.logger.error(f"Error calculating MLB expected value: {e}")
            return 0.0

    def get_required_columns(self) -> List[str]:
        """
        Get list of required columns for MLB data.
        
        Returns:
            List of required column names
        """
        return [
            "game_id", "date", "home_team", "away_team", 
            "home_score", "away_score", "is_completed",
            "total_runs", "run_differential"
        ]

    def analyze_pitcher_matchup(self, home_pitcher: str, away_pitcher: str) -> Dict:
        """
        Analyze pitcher matchup for the game.
        
        Args:
            home_pitcher: Home team starting pitcher
            away_pitcher: Away team starting pitcher
        
        Returns:
            Pitcher matchup analysis
        """
        try:
            # This would typically fetch pitcher statistics from API
            # For now, return a placeholder structure
            
            analysis = {
                "home_pitcher": {
                    "name": home_pitcher,
                    "era": 3.50,  # Placeholder
                    "whip": 1.25,  # Placeholder
                    "strikeouts_per_9": 8.5,
                    "recent_form": "average"
                },
                "away_pitcher": {
                    "name": away_pitcher,
                    "era": 3.75,  # Placeholder
                    "whip": 1.30,  # Placeholder
                    "strikeouts_per_9": 8.2,
                    "recent_form": "average"
                },
                "matchup_advantage": "home",  # Based on comparison
                "confidence": 0.7
            }
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing pitcher matchup: {e}")
            return {}

    def get_betting_recommendations(self, game_data: Dict, odds_data: Dict) -> List[Dict]:
        """
        Get betting recommendations for an MLB game.
        
        Args:
            game_data: Game information
            odds_data: Current betting odds
        
        Returns:
            List of betting recommendations
        """
        try:
            recommendations = []
            
            # Get prediction
            prediction = self.predict_game_outcome(game_data)
            
            if "error" not in prediction:
                # Moneyline recommendations
                home_ml_ev = self.ev_calculator.calculate_ev_percentage(
                    prediction["home_win_probability"],
                    odds_data.get("home_moneyline", 0)
                )
                
                away_ml_ev = self.ev_calculator.calculate_ev_percentage(
                    prediction["away_win_probability"],
                    odds_data.get("away_moneyline", 0)
                )
                
                # Add positive EV bets
                if home_ml_ev > 1.0:  # Minimum 1% EV
                    recommendations.append({
                        "bet_type": "moneyline",
                        "team": prediction["home_team"],
                        "odds": odds_data.get("home_moneyline", 0),
                        "expected_value": home_ml_ev,
                        "confidence": prediction["confidence_score"],
                        "recommendation": "BET" if home_ml_ev > 3.0 else "CONSIDER"
                    })
                
                if away_ml_ev > 1.0:
                    recommendations.append({
                        "bet_type": "moneyline",
                        "team": prediction["away_team"],
                        "odds": odds_data.get("away_moneyline", 0),
                        "expected_value": away_ml_ev,
                        "confidence": prediction["confidence_score"],
                        "recommendation": "BET" if away_ml_ev > 3.0 else "CONSIDER"
                    })
                
                # Total runs recommendations
                predicted_total = prediction["predicted_total_runs"]
                book_total = odds_data.get("total_runs", 8.5)
                
                if abs(predicted_total - book_total) > 0.5:
                    total_recommendation = "OVER" if predicted_total > book_total else "UNDER"
                    recommendations.append({
                        "bet_type": "total",
                        "selection": total_recommendation,
                        "book_line": book_total,
                        "predicted_total": predicted_total,
                        "edge": abs(predicted_total - book_total),
                        "recommendation": "BET" if abs(predicted_total - book_total) > 1.0 else "CONSIDER"
                    })
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error generating MLB betting recommendations: {e}")
            return []