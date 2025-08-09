#!/usr/bin/env python3
"""
Script to create new sport modules in the Ultra Sports Betting System
"""

import os
import sys
from pathlib import Path
import argparse

def create_sport_module(sport_name: str):
    """
    Create a new sport module with all necessary files.
    
    Args:
        sport_name: Name of the sport (e.g., 'cricket', 'volleyball')
    """
    print(f"🏗️  Creating sport module for {sport_name.upper()}...")
    
    # Create sport directory
    sport_dir = Path(f"sports/{sport_name}")
    sport_dir.mkdir(exist_ok=True)
    
    # Create analyzer file
    analyzer_content = f'''"""
{sport_name.upper()} Analyzer Module for Ultra Sports Betting System
{sport_name.title()}-specific analysis and prediction system
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime

from core.analysis.base_analyzer import BaseAnalyzer
from core.data_acquisition.api_manager import APIManager
from core.processing.data_processor import DataProcessor
from core.analysis.ev_calculator import EVCalculator
from core.utils.logger import get_logger


class {sport_name.title()}Analyzer(BaseAnalyzer):
    """
    {sport_name.title()}-specific betting analysis and prediction system.
    """

    def __init__(self):
        super().__init__()
        self.logger = get_logger("{sport_name}_analyzer")
        self.sport_name = "{sport_name}"
        self.api_manager = APIManager()
        self.data_processor = DataProcessor()
        self.ev_calculator = EVCalculator()

    def fetch_game_data(self, date: Optional[str] = None) -> pd.DataFrame:
        """
        Fetch {sport_name.title()} game data for analysis.
        
        Args:
            date: Date to fetch data for (YYYY-MM-DD format)
        
        Returns:
            DataFrame with {sport_name.title()} game data
        """
        try:
            if date is None:
                date = datetime.now().strftime("%Y%m%d")
            else:
                date = datetime.strptime(date, "%Y-%m-%d").strftime("%Y%m%d")
            
            # Fetch games from API
            raw_games = self.api_manager.fetch_espn_games("{sport_name}", date)
            
            if raw_games:
                processed_data = self.data_processor.normalize_game_data(raw_games, "{sport_name}")
                cleaned_data = self.data_processor.clean_data(processed_data)
                
                self.logger.info(f"Fetched {{len(cleaned_data)}} {sport_name.title()} games for {{date}}")
                return cleaned_data
            else:
                self.logger.warning(f"No {sport_name.title()} games found for {{date}}")
                return pd.DataFrame()
                
        except Exception as e:
            self.logger.error(f"Error fetching {sport_name.title()} game data: {{e}}")
            return pd.DataFrame()

    def calculate_team_stats(self, team_id: str) -> Dict:
        """
        Calculate comprehensive {sport_name.title()} team statistics.
        
        Args:
            team_id: {sport_name.title()} team identifier
        
        Returns:
            Dictionary with {sport_name.title()} team statistics
        """
        try:
            # Implement team statistics calculation
            # This is a placeholder implementation
            return {{
                "team_name": team_id,
                "games_played": 0,
                "wins": 0,
                "losses": 0,
                "win_percentage": 0.0
            }}
            
        except Exception as e:
            self.logger.error(f"Error calculating {sport_name.title()} team stats for {{team_id}}: {{e}}")
            return {{"team_name": team_id, "error": str(e)}}

    def predict_game_outcome(self, game_data: Dict) -> Dict:
        """
        Predict {sport_name.title()} game outcome with confidence intervals.
        
        Args:
            game_data: Game data dictionary
        
        Returns:
            Prediction results with confidence scores
        """
        try:
            # Implement prediction logic
            # This is a placeholder implementation
            prediction = {{
                "game_id": game_data.get("game_id", ""),
                "home_team": game_data.get("home_team", ""),
                "away_team": game_data.get("away_team", ""),
                "home_win_probability": 0.5,
                "away_win_probability": 0.5,
                "confidence_score": 0.7,
                "prediction_date": datetime.now().isoformat(),
                "model_version": "{sport_name}_basic_v1.0"
            }}
            
            return prediction
            
        except Exception as e:
            self.logger.error(f"Error predicting {sport_name.title()} game outcome: {{e}}")
            return {{"error": str(e)}}

    def calculate_expected_value(self, odds: Dict, predictions: Dict) -> float:
        """
        Calculate expected value for {sport_name.title()} betting opportunities.
        
        Args:
            odds: Betting odds dictionary
            predictions: Model predictions dictionary
        
        Returns:
            Expected value as float
        """
        try:
            # Implement EV calculation
            return 0.0
            
        except Exception as e:
            self.logger.error(f"Error calculating {sport_name.title()} expected value: {{e}}")
            return 0.0

    def get_required_columns(self) -> List[str]:
        """
        Get list of required columns for {sport_name.title()} data.
        
        Returns:
            List of required column names
        """
        return [
            "game_id", "date", "home_team", "away_team", 
            "home_score", "away_score", "is_completed"
        ]
'''
    
    analyzer_file = sport_dir / f"{sport_name}_analyzer.py"
    with open(analyzer_file, 'w') as f:
        f.write(analyzer_content)
    
    # Create __init__.py
    init_content = f'''"""
{sport_name.title()} module for Ultra Sports Betting System
"""

from .{sport_name}_analyzer import {sport_name.title()}Analyzer

__all__ = ["{sport_name.title()}Analyzer"]
'''
    
    init_file = sport_dir / "__init__.py"
    with open(init_file, 'w') as f:
        f.write(init_content)
    
    # Create test file
    test_dir = Path("tests") / sport_name
    test_dir.mkdir(parents=True, exist_ok=True)
    
    test_content = f'''"""
Test cases for {sport_name.title()} Analyzer
"""

import unittest
import pandas as pd
from unittest.mock import Mock, patch

from sports.{sport_name}.{sport_name}_analyzer import {sport_name.title()}Analyzer


class Test{sport_name.title()}Analyzer(unittest.TestCase):
    """
    Test cases for {sport_name.title()}Analyzer.
    """

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.analyzer = {sport_name.title()}Analyzer()

    def test_initialization(self):
        """Test analyzer initialization."""
        self.assertEqual(self.analyzer.sport_name, "{sport_name}")
        self.assertIsNotNone(self.analyzer.logger)

    def test_fetch_game_data_empty(self):
        """Test fetch_game_data with no games."""
        with patch.object(self.analyzer.api_manager, 'fetch_espn_games') as mock_fetch:
            mock_fetch.return_value = []
            result = self.analyzer.fetch_game_data()
            self.assertTrue(result.empty)

    def test_calculate_team_stats(self):
        """Test calculate_team_stats functionality."""
        result = self.analyzer.calculate_team_stats("TEST_TEAM")
        self.assertIsInstance(result, dict)
        self.assertIn("team_name", result)

    def test_predict_game_outcome(self):
        """Test predict_game_outcome functionality."""
        game_data = {{
            "game_id": "test_game",
            "home_team": "Team A",
            "away_team": "Team B"
        }}
        result = self.analyzer.predict_game_outcome(game_data)
        self.assertIsInstance(result, dict)
        self.assertIn("game_id", result)

    def tearDown(self):
        """Clean up after each test method."""
        pass


if __name__ == '__main__':
    unittest.main()
'''
    
    test_file = test_dir / f"test_{sport_name}_analyzer.py"
    with open(test_file, 'w') as f:
        f.write(test_content)
    
    # Add API endpoint to main.py (create a note file for manual addition)
    api_note_content = f'''
# Add these endpoints to api/main.py:

from sports.{sport_name}.{sport_name}_analyzer import {sport_name.title()}Analyzer

# Initialize analyzer
{sport_name}_analyzer = {sport_name.title()}Analyzer()

@app.get("/api/{sport_name}/games")
async def get_{sport_name}_games(date: Optional[str] = None):
    """Get {sport_name.title()} games for a specific date."""
    try:
        games_data = {sport_name}_analyzer.fetch_game_data(date)
        
        if games_data.empty:
            return {{"games": [], "count": 0, "date": date or "today"}}
        
        games_list = games_data.to_dict('records')
        
        return {{
            "games": games_list,
            "count": len(games_list),
            "date": date or "today",
            "sport": "{sport_name}"
        }}
        
    except Exception as e:
        logger.error(f"Error fetching {sport_name.title()} games: {{e}}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/{sport_name}/teams/{{team_id}}/stats")
async def get_{sport_name}_team_stats(team_id: str):
    """Get {sport_name.title()} team statistics."""
    try:
        stats = {sport_name}_analyzer.calculate_team_stats(team_id)
        
        if "error" in stats:
            raise HTTPException(status_code=404, detail=stats["error"])
        
        return {{
            "team_stats": stats,
            "sport": "{sport_name}",
            "team_id": team_id
        }}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching {sport_name.title()} team stats: {{e}}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/{sport_name}/predict")
async def predict_{sport_name}_game(game_data: Dict):
    """Predict {sport_name.title()} game outcome."""
    try:
        prediction = {sport_name}_analyzer.predict_game_outcome(game_data)
        
        if "error" in prediction:
            raise HTTPException(status_code=400, detail=prediction["error"])
        
        return {{
            "prediction": prediction,
            "sport": "{sport_name}"
        }}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error predicting {sport_name.title()} game: {{e}}")
        raise HTTPException(status_code=500, detail=str(e))
'''
    
    api_note_file = sport_dir / f"api_endpoints_{sport_name}.txt"
    with open(api_note_file, 'w') as f:
        f.write(api_note_content)
    
    print(f"✅ Created {sport_name.title()} sport module with:")
    print(f"   - Analyzer: {analyzer_file}")
    print(f"   - Init file: {init_file}")
    print(f"   - Test file: {test_file}")
    print(f"   - API endpoints note: {api_note_file}")
    print(f"\n📝 Next steps:")
    print(f"   1. Implement sport-specific logic in {analyzer_file}")
    print(f"   2. Add API endpoints from {api_note_file} to api/main.py")
    print(f"   3. Run tests: python -m pytest tests/{sport_name}/")
    print(f"   4. Update Google Apps Script to include {sport_name.title()}")

def main():
    """Main function for sport module creation."""
    parser = argparse.ArgumentParser(description="Create new sport module for Ultra Sports Betting System")
    parser.add_argument("sport_name", type=str, help="Name of the sport (e.g., cricket, volleyball)")
    
    args = parser.parse_args()
    
    # Validate sport name
    sport_name = args.sport_name.lower().strip()
    if not sport_name.isalpha():
        print("❌ Error: Sport name should contain only letters")
        sys.exit(1)
    
    # Check if sport already exists
    sport_dir = Path(f"sports/{sport_name}")
    if sport_dir.exists():
        print(f"⚠️  Warning: Sport module '{sport_name}' already exists")
        response = input("Do you want to overwrite it? (y/N): ")
        if response.lower() != 'y':
            print("Operation cancelled")
            sys.exit(0)
    
    try:
        create_sport_module(sport_name)
        print(f"\n🎉 Sport module '{sport_name}' created successfully!")
        
    except Exception as e:
        print(f"❌ Error creating sport module: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()