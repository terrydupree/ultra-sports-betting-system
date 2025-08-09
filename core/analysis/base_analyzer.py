"""
Base analyzer class for all sports
"""

from abc import ABC, abstractmethod
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime

from core.utils.logger import get_logger


class BaseAnalyzer(ABC):
    """
    Abstract base class for sport-specific analyzers.
    """
    
    def __init__(self):
        """Initialize base analyzer."""
        self.logger = get_logger(f"base_analyzer")
        self.sport_name = "base"
        self.last_update: Optional[datetime] = None
    
    @abstractmethod
    def fetch_game_data(self, date: Optional[str] = None) -> pd.DataFrame:
        """
        Fetch game data for analysis.
        
        Args:
            date: Date to fetch data for (YYYY-MM-DD format)
        
        Returns:
            DataFrame with game data
        """
        pass
    
    @abstractmethod
    def calculate_team_stats(self, team_id: str) -> Dict:
        """
        Calculate comprehensive team statistics.
        
        Args:
            team_id: Unique team identifier
        
        Returns:
            Dictionary with team statistics
        """
        pass
    
    @abstractmethod
    def predict_game_outcome(self, game_data: Dict) -> Dict:
        """
        Predict game outcome with confidence intervals.
        
        Args:
            game_data: Game data dictionary
        
        Returns:
            Prediction results with confidence scores
        """
        pass
    
    @abstractmethod
    def calculate_expected_value(self, odds: Dict, predictions: Dict) -> float:
        """
        Calculate expected value for betting opportunities.
        
        Args:
            odds: Betting odds dictionary
            predictions: Model predictions dictionary
        
        Returns:
            Expected value as float
        """
        pass
    
    def get_sport_info(self) -> Dict:
        """
        Get basic information about this sport analyzer.
        
        Returns:
            Dictionary with sport information
        """
        return {
            "sport_name": self.sport_name,
            "last_update": self.last_update,
            "analyzer_class": self.__class__.__name__
        }
    
    def validate_data(self, data: pd.DataFrame) -> bool:
        """
        Validate data quality and completeness.
        
        Args:
            data: DataFrame to validate
        
        Returns:
            True if data is valid, False otherwise
        """
        if data is None or data.empty:
            self.logger.warning("Data is empty or None")
            return False
        
        required_columns = self.get_required_columns()
        missing_columns = set(required_columns) - set(data.columns)
        
        if missing_columns:
            self.logger.warning(f"Missing required columns: {missing_columns}")
            return False
        
        return True
    
    def get_required_columns(self) -> List[str]:
        """
        Get list of required columns for this sport.
        
        Returns:
            List of required column names
        """
        return ["game_id", "date", "home_team", "away_team"]
    
    def update_timestamp(self) -> None:
        """Update the last update timestamp."""
        self.last_update = datetime.now()