"""
NFL Analyzer Module for Ultra Sports Betting System
NFL-specific analysis and prediction system
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime, timedelta

from core.analysis.base_analyzer import BaseAnalyzer
from core.data_acquisition.api_manager import APIManager
from core.processing.data_processor import DataProcessor
from core.analysis.ev_calculator import EVCalculator
from core.utils.logger import get_logger


class NFLAnalyzer(BaseAnalyzer):
    """
    NFL-specific betting analysis and prediction system.
    """

    def __init__(self):
        super().__init__()
        self.logger = get_logger("nfl_analyzer")
        self.sport_name = "nfl"
        self.api_manager = APIManager()
        self.data_processor = DataProcessor()
        self.ev_calculator = EVCalculator()
        
        # NFL-specific configuration
        self.season_weeks = 18  # Regular season
        self.playoff_weeks = 4
        self.quarters_per_game = 4
        self.positions = {
            "offense": ["qb", "rb", "wr", "te", "ol"],
            "defense": ["dl", "lb", "db"],
            "special_teams": ["k", "p", "ls"]
        }

    def fetch_game_data(self, date: Optional[str] = None) -> pd.DataFrame:
        """
        Fetch NFL game data for analysis.
        
        Args:
            date: Date to fetch data for (YYYY-MM-DD format)
        
        Returns:
            DataFrame with NFL game data
        """
        try:
            if date is None:
                date = datetime.now().strftime("%Y%m%d")
            else:
                # Convert YYYY-MM-DD to YYYYMMDD
                date = datetime.strptime(date, "%Y-%m-%d").strftime("%Y%m%d")
            
            # Fetch games from ESPN API
            raw_games = self.api_manager.fetch_espn_games("nfl", date)
            
            if raw_games:
                # Process and normalize
                processed_data = self.data_processor.normalize_game_data(raw_games, "nfl")
                cleaned_data = self.data_processor.clean_data(processed_data)
                
                # Add NFL-specific features
                cleaned_data = self._add_nfl_specific_features(cleaned_data)
                
                self.logger.info(f"Fetched {len(cleaned_data)} NFL games for {date}")
                return cleaned_data
            else:
                self.logger.warning(f"No NFL games found for {date}")
                return pd.DataFrame()
                
        except Exception as e:
            self.logger.error(f"Error fetching NFL game data: {e}")
            return pd.DataFrame()

    def _add_nfl_specific_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add NFL-specific features to the DataFrame.
        
        Args:
            df: Game data DataFrame
        
        Returns:
            DataFrame with NFL-specific features
        """
        try:
            # Game timing
            df["is_primetime"] = df["date"].dt.hour >= 20  # 8 PM or later
            df["is_sunday"] = df["date"].dt.dayofweek == 6
            df["is_monday"] = df["date"].dt.dayofweek == 0
            df["is_thursday"] = df["date"].dt.dayofweek == 3
            
            # Scoring patterns
            df["points_scored_home"] = df["home_score"]
            df["points_scored_away"] = df["away_score"]
            df["total_points"] = df["total_score"]
            
            # Game competitiveness
            df["is_blowout"] = abs(df["score_differential"]) >= 21
            df["is_close_game"] = abs(df["score_differential"]) <= 7
            df["is_overtime"] = False  # Would need more detailed data
            
            # Season context (placeholder - would need week/season info)
            df["week"] = 1  # Default week
            df["is_playoff"] = False
            df["is_division_game"] = False  # Would need team division data
            
            # Weather impact (placeholder)
            df["temperature"] = 60  # Default temperature
            df["wind_speed"] = 5    # Default wind speed
            df["precipitation"] = 0  # Default no precipitation
            df["is_dome"] = False   # Would need stadium data
            
            return df
            
        except Exception as e:
            self.logger.error(f"Error adding NFL-specific features: {e}")
            return df

    def calculate_team_stats(self, team_id: str) -> Dict:
        """
        Calculate comprehensive NFL team statistics.
        
        Args:
            team_id: NFL team identifier
        
        Returns:
            Dictionary with NFL team statistics
        """
        try:
            # NFL season is shorter, so look at last 10 games or current season
            end_date = datetime.now()
            start_date = end_date - timedelta(days=120)  # ~17 weeks
            
            # Get team games
            team_games = []
            current_date = start_date
            while current_date <= end_date:
                date_str = current_date.strftime("%Y-%m-%d")
                daily_games = self.fetch_game_data(date_str)
                
                if not daily_games.empty:
                    team_daily_games = daily_games[
                        (daily_games["home_team"] == team_id) | 
                        (daily_games["away_team"] == team_id)
                    ]
                    if not team_daily_games.empty:
                        team_games.append(team_daily_games)
                
                current_date += timedelta(days=7)  # Weekly games
            
            if team_games:
                all_team_games = pd.concat(team_games, ignore_index=True)
                
                # Use data processor for basic stats
                base_stats = self.data_processor.aggregate_team_stats(all_team_games, team_id)
                
                # Add NFL-specific stats
                nfl_stats = self._calculate_nfl_specific_stats(all_team_games, team_id)
                
                # Combine stats
                base_stats.update(nfl_stats)
                return base_stats
            else:
                return {"team_name": team_id, "error": "No recent games found"}
                
        except Exception as e:
            self.logger.error(f"Error calculating NFL team stats for {team_id}: {e}")
            return {"team_name": team_id, "error": str(e)}

    def _calculate_nfl_specific_stats(self, games_df: pd.DataFrame, team_id: str) -> Dict:
        """
        Calculate NFL-specific team statistics.
        
        Args:
            games_df: DataFrame with team's games
            team_id: Team identifier
        
        Returns:
            Dictionary with NFL-specific statistics
        """
        try:
            # Home/Away performance
            home_games = games_df[games_df["home_team"] == team_id]
            away_games = games_df[games_df["away_team"] == team_id]
            
            # Points statistics
            points_scored = []
            points_allowed = []
            
            for _, game in games_df.iterrows():
                if game["home_team"] == team_id:
                    points_scored.append(game["home_score"])
                    points_allowed.append(game["away_score"])
                else:
                    points_scored.append(game["away_score"])
                    points_allowed.append(game["home_score"])
            
            # Calculate NFL-specific metrics
            stats = {
                "points_per_game": np.mean(points_scored) if points_scored else 0,
                "points_allowed_per_game": np.mean(points_allowed) if points_allowed else 0,
                "point_differential_per_game": np.mean(points_scored) - np.mean(points_allowed) if points_scored and points_allowed else 0,
                "home_record": f"{len(home_games[home_games['home_team_result'] == 'Win'])}-{len(home_games[home_games['home_team_result'] == 'Loss'])}",
                "away_record": f"{len(away_games[away_games['home_team_result'] == 'Loss'])}-{len(away_games[away_games['home_team_result'] == 'Win'])}",
                "games_over_45_points": len(games_df[games_df["total_points"] > 45]),
                "games_under_35_points": len(games_df[games_df["total_points"] < 35]),
                "blowout_wins": len(games_df[
                    ((games_df["home_team"] == team_id) & (games_df["score_differential"] >= 21)) |
                    ((games_df["away_team"] == team_id) & (games_df["score_differential"] <= -21))
                ]),
                "blowout_losses": len(games_df[
                    ((games_df["home_team"] == team_id) & (games_df["score_differential"] <= -21)) |
                    ((games_df["away_team"] == team_id) & (games_df["score_differential"] >= 21))
                ]),
                "close_games": len(games_df[abs(games_df["score_differential"]) <= 7]),
                "primetime_games": len(games_df[games_df["is_primetime"]]),
                "division_games": len(games_df[games_df["is_division_game"]]),
                "recent_form": self._calculate_recent_form(games_df, team_id, 4)  # Last 4 games
            }
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error calculating NFL-specific stats: {e}")
            return {}

    def _calculate_recent_form(self, games_df: pd.DataFrame, team_id: str, num_games: int) -> str:
        """
        Calculate recent form for the team.
        
        Args:
            games_df: DataFrame with team's games
            team_id: Team identifier
            num_games: Number of recent games to consider
        
        Returns:
            Recent form string (e.g., "W-L-W-W")
        """
        try:
            # Sort by date and get recent games
            sorted_games = games_df.sort_values("date", ascending=False).head(num_games)
            
            form = []
            for _, game in sorted_games.iterrows():
                if game["home_team"] == team_id:
                    result = "W" if game["home_team_result"] == "Win" else "L"
                else:
                    result = "W" if game["home_team_result"] == "Loss" else "L"
                form.append(result)
            
            return "-".join(form) if form else "No recent games"
            
        except Exception as e:
            self.logger.error(f"Error calculating recent form: {e}")
            return "Unknown"

    def predict_game_outcome(self, game_data: Dict) -> Dict:
        """
        Predict NFL game outcome with confidence intervals.
        
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
            
            # Calculate prediction based on team performance
            home_ppg = home_stats.get("points_per_game", 21.0)
            away_ppg = away_stats.get("points_per_game", 21.0)
            home_points_allowed = home_stats.get("points_allowed_per_game", 21.0)
            away_points_allowed = away_stats.get("points_allowed_per_game", 21.0)
            
            # Predict points scored (considering both offense and opponent defense)
            predicted_home_points = (home_ppg + away_points_allowed) / 2
            predicted_away_points = (away_ppg + home_points_allowed) / 2
            
            # Home field advantage (approximately 3 points in NFL)
            predicted_home_points += 3.0
            
            # Calculate spread
            predicted_spread = predicted_home_points - predicted_away_points
            
            # Calculate win probabilities using logistic model
            # NFL games are more predictable than other sports
            home_win_prob = 1 / (1 + np.exp(-predicted_spread * 0.15))
            away_win_prob = 1 - home_win_prob
            
            # Calculate total points prediction
            predicted_total = predicted_home_points + predicted_away_points
            
            # Confidence based on consistency and sample size
            home_consistency = 1 / (1 + abs(home_stats.get("point_differential_per_game", 0)) / 10)
            away_consistency = 1 / (1 + abs(away_stats.get("point_differential_per_game", 0)) / 10)
            sample_size_factor = min(home_stats.get("total_games", 0) / 16, 1.0)
            confidence = min((home_consistency + away_consistency) * sample_size_factor, 0.95)
            
            prediction = {
                "game_id": game_data.get("game_id", ""),
                "home_team": home_team,
                "away_team": away_team,
                "predicted_home_score": round(predicted_home_points, 1),
                "predicted_away_score": round(predicted_away_points, 1),
                "predicted_total_points": round(predicted_total, 1),
                "predicted_spread": round(predicted_spread, 1),
                "home_win_probability": round(home_win_prob, 4),
                "away_win_probability": round(away_win_prob, 4),
                "confidence_score": round(confidence, 4),
                "prediction_date": datetime.now().isoformat(),
                "model_version": "nfl_basic_v1.0"
            }
            
            return prediction
            
        except Exception as e:
            self.logger.error(f"Error predicting NFL game outcome: {e}")
            return {"error": str(e)}

    def calculate_expected_value(self, odds: Dict, predictions: Dict) -> float:
        """
        Calculate expected value for NFL betting opportunities.
        
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
            
            # Calculate EV for moneyline bets
            home_odds = odds.get("home_moneyline", 0)
            away_odds = odds.get("away_moneyline", 0)
            
            home_ev = self.ev_calculator.calculate_expected_value(home_prob, home_odds)
            away_ev = self.ev_calculator.calculate_expected_value(away_prob, away_odds)
            
            # Calculate EV for spread bets
            predicted_spread = predictions.get("predicted_spread", 0)
            book_spread = odds.get("spread", 0)
            
            # Simple spread EV calculation
            spread_edge = abs(predicted_spread - book_spread)
            spread_ev = spread_edge * 5  # Rough conversion to EV
            
            # Return the best EV opportunity
            return max(home_ev, away_ev, spread_ev)
            
        except Exception as e:
            self.logger.error(f"Error calculating NFL expected value: {e}")
            return 0.0

    def get_required_columns(self) -> List[str]:
        """
        Get list of required columns for NFL data.
        
        Returns:
            List of required column names
        """
        return [
            "game_id", "date", "home_team", "away_team", 
            "home_score", "away_score", "is_completed",
            "total_points", "point_differential", "week", "is_playoff"
        ]

    def analyze_matchup_factors(self, home_team: str, away_team: str, game_data: Dict) -> Dict:
        """
        Analyze key matchup factors for the NFL game.
        
        Args:
            home_team: Home team identifier
            away_team: Away team identifier
            game_data: Additional game information
        
        Returns:
            Matchup analysis
        """
        try:
            home_stats = self.calculate_team_stats(home_team)
            away_stats = self.calculate_team_stats(away_team)
            
            analysis = {
                "offensive_matchup": {
                    "home_offense_vs_away_defense": self._compare_units(
                        home_stats.get("points_per_game", 0),
                        away_stats.get("points_allowed_per_game", 0)
                    ),
                    "away_offense_vs_home_defense": self._compare_units(
                        away_stats.get("points_per_game", 0),
                        home_stats.get("points_allowed_per_game", 0)
                    )
                },
                "recent_form": {
                    "home_team": home_stats.get("recent_form", "Unknown"),
                    "away_team": away_stats.get("recent_form", "Unknown")
                },
                "situational_factors": {
                    "is_primetime": game_data.get("is_primetime", False),
                    "is_division_game": game_data.get("is_division_game", False),
                    "weather_impact": self._assess_weather_impact(game_data),
                    "rest_advantage": self._calculate_rest_advantage(game_data)
                },
                "key_advantages": {
                    "home_team": self._identify_advantages(home_stats, away_stats),
                    "away_team": self._identify_advantages(away_stats, home_stats)
                }
            }
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing NFL matchup factors: {e}")
            return {}

    def _compare_units(self, offensive_stat: float, defensive_stat: float) -> str:
        """Compare offensive and defensive units."""
        difference = offensive_stat - defensive_stat
        if difference > 5:
            return "significant_advantage"
        elif difference > 2:
            return "moderate_advantage"
        elif difference > -2:
            return "even_matchup"
        elif difference > -5:
            return "moderate_disadvantage"
        else:
            return "significant_disadvantage"

    def _assess_weather_impact(self, game_data: Dict) -> str:
        """Assess weather impact on the game."""
        # Placeholder implementation
        temp = game_data.get("temperature", 60)
        wind = game_data.get("wind_speed", 5)
        precipitation = game_data.get("precipitation", 0)
        
        if precipitation > 0.5 or wind > 20:
            return "high_impact"
        elif temp < 32 or temp > 90 or wind > 15:
            return "moderate_impact"
        else:
            return "low_impact"

    def _calculate_rest_advantage(self, game_data: Dict) -> str:
        """Calculate rest advantage between teams."""
        # Placeholder - would need days since last game data
        return "even"

    def _identify_advantages(self, team_stats: Dict, opponent_stats: Dict) -> List[str]:
        """Identify key advantages for a team."""
        advantages = []
        
        # Scoring advantage
        if team_stats.get("points_per_game", 0) > opponent_stats.get("points_per_game", 0) + 3:
            advantages.append("offensive_advantage")
        
        # Defensive advantage
        if team_stats.get("points_allowed_per_game", 50) < opponent_stats.get("points_allowed_per_game", 50) - 3:
            advantages.append("defensive_advantage")
        
        # Recent form advantage
        team_form = team_stats.get("recent_form", "")
        if team_form.count("W") > team_form.count("L"):
            advantages.append("recent_form")
        
        return advantages

    def get_betting_recommendations(self, game_data: Dict, odds_data: Dict) -> List[Dict]:
        """
        Get betting recommendations for an NFL game.
        
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
                # Spread recommendations
                predicted_spread = prediction["predicted_spread"]
                book_spread = odds_data.get("spread", 0)
                
                if abs(predicted_spread - book_spread) > 2.5:  # Significant edge
                    spread_bet = prediction["home_team"] if predicted_spread > book_spread else prediction["away_team"]
                    recommendations.append({
                        "bet_type": "spread",
                        "team": spread_bet,
                        "book_line": book_spread,
                        "predicted_line": predicted_spread,
                        "edge": abs(predicted_spread - book_spread),
                        "confidence": prediction["confidence_score"],
                        "recommendation": "BET" if abs(predicted_spread - book_spread) > 4 else "CONSIDER"
                    })
                
                # Total points recommendations
                predicted_total = prediction["predicted_total_points"]
                book_total = odds_data.get("total", 42.5)
                
                if abs(predicted_total - book_total) > 3:
                    total_recommendation = "OVER" if predicted_total > book_total else "UNDER"
                    recommendations.append({
                        "bet_type": "total",
                        "selection": total_recommendation,
                        "book_line": book_total,
                        "predicted_total": predicted_total,
                        "edge": abs(predicted_total - book_total),
                        "recommendation": "BET" if abs(predicted_total - book_total) > 5 else "CONSIDER"
                    })
                
                # Moneyline recommendations (for underdog value)
                if prediction["away_win_probability"] > 0.45:  # Good underdog value
                    away_ml_ev = self.ev_calculator.calculate_ev_percentage(
                        prediction["away_win_probability"],
                        odds_data.get("away_moneyline", 0)
                    )
                    
                    if away_ml_ev > 2.0:
                        recommendations.append({
                            "bet_type": "moneyline",
                            "team": prediction["away_team"],
                            "odds": odds_data.get("away_moneyline", 0),
                            "expected_value": away_ml_ev,
                            "confidence": prediction["confidence_score"],
                            "recommendation": "BET" if away_ml_ev > 5.0 else "CONSIDER"
                        })
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error generating NFL betting recommendations: {e}")
            return []