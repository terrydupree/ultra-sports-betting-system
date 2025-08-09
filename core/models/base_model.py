"""
Base model class for betting predictions
"""

from abc import ABC, abstractmethod
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import pickle
import os

from core.utils.logger import get_logger


class BaseModel(ABC):
    """
    Abstract base class for betting prediction models.
    """
    
    def __init__(self):
        """Initialize base model."""
        self.logger = get_logger("base_model")
        self.model = None
        self.is_trained = False
        self.feature_names = []
        self.model_metadata = {
            "created_at": datetime.now(),
            "last_trained": None,
            "training_samples": 0,
            "model_version": "1.0"
        }
    
    @abstractmethod
    def prepare_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Prepare features for model training/prediction.
        
        Args:
            data: Raw data DataFrame
        
        Returns:
            Processed features DataFrame
        """
        pass
    
    @abstractmethod
    def train(self, training_data: pd.DataFrame, target_column: str) -> None:
        """
        Train the model on provided data.
        
        Args:
            training_data: DataFrame with training data
            target_column: Name of the target column
        """
        pass
    
    @abstractmethod
    def predict(self, data: pd.DataFrame) -> np.ndarray:
        """
        Make predictions using the trained model.
        
        Args:
            data: DataFrame with features for prediction
        
        Returns:
            Array of predictions
        """
        pass
    
    def predict_proba(self, data: pd.DataFrame) -> np.ndarray:
        """
        Predict class probabilities (for classification models).
        
        Args:
            data: DataFrame with features for prediction
        
        Returns:
            Array of class probabilities
        """
        if hasattr(self.model, 'predict_proba'):
            features = self.prepare_features(data)
            return self.model.predict_proba(features)
        else:
            raise NotImplementedError("Model does not support probability prediction")
    
    def calculate_confidence(self, predictions: np.ndarray) -> np.ndarray:
        """
        Calculate prediction confidence scores.
        
        Args:
            predictions: Model predictions
        
        Returns:
            Array of confidence scores
        """
        # Default implementation for probability-based confidence
        if len(predictions.shape) > 1:  # Multi-class probabilities
            return np.max(predictions, axis=1)
        else:  # Binary classification or regression
            return np.abs(predictions - 0.5) * 2  # Convert to 0-1 scale
    
    def save_model(self, filepath: str) -> bool:
        """
        Save the trained model to disk.
        
        Args:
            filepath: Path to save the model
        
        Returns:
            True if successful, False otherwise
        """
        try:
            model_data = {
                'model': self.model,
                'feature_names': self.feature_names,
                'metadata': self.model_metadata,
                'is_trained': self.is_trained
            }
            
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            with open(filepath, 'wb') as f:
                pickle.dump(model_data, f)
            
            self.logger.info(f"Model saved successfully to {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving model: {e}")
            return False
    
    def load_model(self, filepath: str) -> bool:
        """
        Load a trained model from disk.
        
        Args:
            filepath: Path to the saved model
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if not os.path.exists(filepath):
                self.logger.error(f"Model file does not exist: {filepath}")
                return False
            
            with open(filepath, 'rb') as f:
                model_data = pickle.load(f)
            
            self.model = model_data['model']
            self.feature_names = model_data['feature_names']
            self.model_metadata = model_data['metadata']
            self.is_trained = model_data['is_trained']
            
            self.logger.info(f"Model loaded successfully from {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error loading model: {e}")
            return False
    
    def get_feature_importance(self) -> Optional[Dict[str, float]]:
        """
        Get feature importance scores if available.
        
        Returns:
            Dictionary mapping feature names to importance scores
        """
        if hasattr(self.model, 'feature_importances_'):
            importance_scores = self.model.feature_importances_
            return dict(zip(self.feature_names, importance_scores))
        else:
            self.logger.warning("Model does not support feature importance")
            return None
    
    def validate_features(self, data: pd.DataFrame) -> bool:
        """
        Validate that required features are present in the data.
        
        Args:
            data: DataFrame to validate
        
        Returns:
            True if all required features are present
        """
        if not self.feature_names:
            self.logger.warning("No feature names defined")
            return False
        
        missing_features = set(self.feature_names) - set(data.columns)
        if missing_features:
            self.logger.error(f"Missing required features: {missing_features}")
            return False
        
        return True
    
    def get_model_info(self) -> Dict:
        """
        Get information about the model.
        
        Returns:
            Dictionary with model information
        """
        return {
            "model_class": self.__class__.__name__,
            "is_trained": self.is_trained,
            "feature_count": len(self.feature_names),
            "feature_names": self.feature_names,
            "metadata": self.model_metadata
        }