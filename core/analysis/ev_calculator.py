"""
Expected Value Calculator for sports betting analysis
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import math

from core.utils.logger import get_logger


class EVCalculator:
    """
    Calculate Expected Value (EV) for sports betting opportunities.
    """
    
    def __init__(self):
        """Initialize EV calculator."""
        self.logger = get_logger("ev_calculator")
    
    def american_to_decimal(self, american_odds: int) -> float:
        """
        Convert American odds to decimal format.
        
        Args:
            american_odds: American odds (e.g., -110, +150)
        
        Returns:
            Decimal odds
        """
        if american_odds > 0:
            return (american_odds / 100) + 1
        else:
            return (100 / abs(american_odds)) + 1
    
    def decimal_to_american(self, decimal_odds: float) -> int:
        """
        Convert decimal odds to American format.
        
        Args:
            decimal_odds: Decimal odds (e.g., 1.91, 2.50)
        
        Returns:
            American odds
        """
        if decimal_odds >= 2.0:
            return int((decimal_odds - 1) * 100)
        else:
            return int(-100 / (decimal_odds - 1))
    
    def implied_probability(self, american_odds: int) -> float:
        """
        Calculate implied probability from odds.
        
        Args:
            american_odds: American odds
        
        Returns:
            Implied probability (0-1)
        """
        decimal_odds = self.american_to_decimal(american_odds)
        return 1 / decimal_odds
    
    def calculate_expected_value(
        self, 
        predicted_probability: float, 
        odds: int, 
        bet_amount: float = 100
    ) -> float:
        """
        Calculate expected value for a bet.
        
        Args:
            predicted_probability: Model's predicted probability (0-1)
            odds: American odds
            bet_amount: Amount to bet
        
        Returns:
            Expected value in dollars
        """
        try:
            # Convert odds to decimal
            decimal_odds = self.american_to_decimal(odds)
            
            # Calculate potential profit
            potential_profit = bet_amount * (decimal_odds - 1)
            
            # Calculate expected value
            # EV = (probability of win * profit) - (probability of loss * bet amount)
            ev = (predicted_probability * potential_profit) - ((1 - predicted_probability) * bet_amount)
            
            return ev
            
        except Exception as e:
            self.logger.error(f"Error calculating EV: {e}")
            return 0.0
    
    def calculate_ev_percentage(
        self, 
        predicted_probability: float, 
        odds: int
    ) -> float:
        """
        Calculate expected value as a percentage of the bet.
        
        Args:
            predicted_probability: Model's predicted probability (0-1)
            odds: American odds
        
        Returns:
            Expected value as percentage
        """
        ev_dollar = self.calculate_expected_value(predicted_probability, odds, 100)
        return ev_dollar  # Already as percentage for $100 bet
    
    def find_positive_ev_bets(
        self, 
        predictions: Dict, 
        odds_data: List[Dict],
        min_ev: float = 1.0
    ) -> List[Dict]:
        """
        Find all positive expected value betting opportunities.
        
        Args:
            predictions: Dictionary of game predictions
            odds_data: List of odds dictionaries
            min_ev: Minimum EV threshold (default 1%)
        
        Returns:
            List of positive EV opportunities
        """
        positive_ev_bets = []
        
        try:
            for odds_entry in odds_data:
                game_id = odds_entry.get("id", "")
                
                # Skip if no prediction for this game
                if game_id not in predictions:
                    continue
                
                game_prediction = predictions[game_id]
                bookmakers = odds_entry.get("bookmakers", [])
                
                for bookmaker in bookmakers:
                    markets = bookmaker.get("markets", [])
                    
                    for market in markets:
                        if market.get("key") == "h2h":  # Head-to-head market
                            outcomes = market.get("outcomes", [])
                            
                            for outcome in outcomes:
                                team_name = outcome.get("name", "")
                                odds = outcome.get("price", 0)
                                
                                # Get predicted probability for this team
                                pred_prob = self._get_team_probability(
                                    game_prediction, team_name
                                )
                                
                                if pred_prob > 0:
                                    ev = self.calculate_ev_percentage(pred_prob, odds)
                                    
                                    if ev >= min_ev:
                                        positive_ev_bets.append({
                                            "game_id": game_id,
                                            "bookmaker": bookmaker.get("title", ""),
                                            "team": team_name,
                                            "odds": odds,
                                            "predicted_probability": pred_prob,
                                            "expected_value": ev,
                                            "market": "moneyline",
                                            "timestamp": datetime.now()
                                        })
            
            # Sort by EV descending
            positive_ev_bets.sort(key=lambda x: x["expected_value"], reverse=True)
            
            self.logger.info(f"Found {len(positive_ev_bets)} positive EV opportunities")
            return positive_ev_bets
            
        except Exception as e:
            self.logger.error(f"Error finding positive EV bets: {e}")
            return []
    
    def _get_team_probability(self, prediction: Dict, team_name: str) -> float:
        """
        Extract team probability from prediction dictionary.
        
        Args:
            prediction: Game prediction dictionary
            team_name: Name of the team
        
        Returns:
            Predicted probability for the team
        """
        # Look for team in home/away predictions
        if prediction.get("home_team") == team_name:
            return prediction.get("home_win_probability", 0)
        elif prediction.get("away_team") == team_name:
            return prediction.get("away_win_probability", 0)
        else:
            # Try to find partial match
            for key, value in prediction.items():
                if team_name.lower() in key.lower() and "probability" in key.lower():
                    return value
        
        return 0
    
    def calculate_kelly_criterion(
        self, 
        predicted_probability: float, 
        odds: int,
        bankroll: float
    ) -> float:
        """
        Calculate optimal bet size using Kelly Criterion.
        
        Args:
            predicted_probability: Model's predicted probability (0-1)
            odds: American odds
            bankroll: Total bankroll
        
        Returns:
            Recommended bet amount
        """
        try:
            # Convert to decimal odds
            decimal_odds = self.american_to_decimal(odds)
            
            # Kelly formula: f = (bp - q) / b
            # Where: b = odds - 1, p = probability, q = 1 - p
            b = decimal_odds - 1
            p = predicted_probability
            q = 1 - p
            
            kelly_fraction = (b * p - q) / b
            
            # Cap at 25% of bankroll for safety
            kelly_fraction = min(kelly_fraction, 0.25)
            kelly_fraction = max(kelly_fraction, 0)  # No negative bets
            
            recommended_bet = bankroll * kelly_fraction
            
            return recommended_bet
            
        except Exception as e:
            self.logger.error(f"Error calculating Kelly criterion: {e}")
            return 0.0
    
    def calculate_arbitrage_opportunities(
        self, 
        odds_data: List[Dict]
    ) -> List[Dict]:
        """
        Find arbitrage opportunities across different bookmakers.
        
        Args:
            odds_data: List of odds from different bookmakers
        
        Returns:
            List of arbitrage opportunities
        """
        arbitrage_opportunities = []
        
        try:
            # Group odds by game
            games_odds = {}
            
            for odds_entry in odds_data:
                game_id = odds_entry.get("id", "")
                if game_id not in games_odds:
                    games_odds[game_id] = []
                games_odds[game_id].append(odds_entry)
            
            # Check each game for arbitrage
            for game_id, game_odds in games_odds.items():
                arb_opportunity = self._check_arbitrage_for_game(game_id, game_odds)
                if arb_opportunity:
                    arbitrage_opportunities.append(arb_opportunity)
            
            return arbitrage_opportunities
            
        except Exception as e:
            self.logger.error(f"Error calculating arbitrage opportunities: {e}")
            return []
    
    def _check_arbitrage_for_game(
        self, 
        game_id: str, 
        game_odds: List[Dict]
    ) -> Optional[Dict]:
        """
        Check for arbitrage opportunity in a single game.
        
        Args:
            game_id: Game identifier
            game_odds: List of odds for this game
        
        Returns:
            Arbitrage opportunity dictionary or None
        """
        try:
            best_odds = {}  # team -> (bookmaker, odds)
            
            # Find best odds for each team across all bookmakers
            for odds_entry in game_odds:
                bookmakers = odds_entry.get("bookmakers", [])
                
                for bookmaker in bookmakers:
                    markets = bookmaker.get("markets", [])
                    
                    for market in markets:
                        if market.get("key") == "h2h":
                            outcomes = market.get("outcomes", [])
                            
                            for outcome in outcomes:
                                team = outcome.get("name", "")
                                odds = outcome.get("price", 0)
                                bookmaker_name = bookmaker.get("title", "")
                                
                                if team not in best_odds or odds > best_odds[team][1]:
                                    best_odds[team] = (bookmaker_name, odds)
            
            # Check if arbitrage exists
            if len(best_odds) >= 2:
                implied_probs = []
                for team, (bookmaker, odds) in best_odds.items():
                    implied_prob = self.implied_probability(odds)
                    implied_probs.append(implied_prob)
                
                total_implied_prob = sum(implied_probs)
                
                # Arbitrage exists if total implied probability < 1
                if total_implied_prob < 1.0:
                    profit_margin = (1 - total_implied_prob) * 100
                    
                    return {
                        "game_id": game_id,
                        "profit_margin": profit_margin,
                        "total_implied_probability": total_implied_prob,
                        "best_odds": best_odds,
                        "timestamp": datetime.now()
                    }
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error checking arbitrage for game {game_id}: {e}")
            return None
    
    def calculate_portfolio_risk(
        self, 
        bets: List[Dict], 
        correlation_matrix: Optional[np.ndarray] = None
    ) -> Dict:
        """
        Calculate portfolio risk metrics for multiple bets.
        
        Args:
            bets: List of bet dictionaries
            correlation_matrix: Optional correlation matrix between bets
        
        Returns:
            Dictionary with risk metrics
        """
        try:
            if not bets:
                return {}
            
            bet_amounts = [bet.get("amount", 0) for bet in bets]
            expected_values = [bet.get("expected_value", 0) for bet in bets]
            
            # Portfolio metrics
            total_bet_amount = sum(bet_amounts)
            total_expected_value = sum(expected_values)
            
            # Simple variance calculation (assuming independence if no correlation matrix)
            if correlation_matrix is None:
                portfolio_variance = sum([
                    (bet.get("amount", 0) ** 2) * 
                    (bet.get("predicted_probability", 0.5) * (1 - bet.get("predicted_probability", 0.5)))
                    for bet in bets
                ])
            else:
                # Use correlation matrix for more accurate variance calculation
                portfolio_variance = 0  # Simplified for now
            
            portfolio_std = math.sqrt(portfolio_variance)
            
            return {
                "total_bet_amount": total_bet_amount,
                "total_expected_value": total_expected_value,
                "portfolio_ev_percentage": (total_expected_value / total_bet_amount * 100) if total_bet_amount > 0 else 0,
                "portfolio_variance": portfolio_variance,
                "portfolio_std_deviation": portfolio_std,
                "number_of_bets": len(bets),
                "average_bet_size": total_bet_amount / len(bets) if bets else 0
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating portfolio risk: {e}")
            return {}