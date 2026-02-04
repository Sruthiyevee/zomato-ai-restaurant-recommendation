"""
Data Loader Module for Phase 1
Handles ingestion of Zomato dataset from Hugging Face
"""

import logging
from typing import Dict, List, Optional
from datasets import load_dataset
import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ZomatoDataLoader:
    """Loads Zomato restaurant dataset from Hugging Face"""
    
    def __init__(self, dataset_name: str = "ManikaSaini/zomato-restaurant-recommendation"):
        """
        Initialize the data loader
        
        Args:
            dataset_name: Hugging Face dataset identifier
        """
        self.dataset_name = dataset_name
        self.dataset = None
        self.raw_data = None
        
    def load_dataset(self) -> pd.DataFrame:
        """
        Load dataset from Hugging Face
        
        Returns:
            pandas DataFrame containing the raw dataset
            
        Raises:
            Exception: If dataset loading fails
        """
        try:
            logger.info(f"Loading dataset: {self.dataset_name}")
            self.dataset = load_dataset(self.dataset_name)
            
            # Handle different dataset structures
            if isinstance(self.dataset, dict):
                # If dataset has splits, use 'train' or first split
                split_name = 'train' if 'train' in self.dataset else list(self.dataset.keys())[0]
                dataset_split = self.dataset[split_name]
            else:
                dataset_split = self.dataset
            
            # Convert to pandas DataFrame
            self.raw_data = dataset_split.to_pandas()
            
            logger.info(f"Dataset loaded successfully. Shape: {self.raw_data.shape}")
            logger.info(f"Columns: {list(self.raw_data.columns)}")
            
            return self.raw_data
            
        except Exception as e:
            logger.error(f"Error loading dataset: {str(e)}")
            raise
    
    def get_dataset_info(self) -> Dict:
        """
        Get information about the loaded dataset
        
        Returns:
            Dictionary with dataset metadata
        """
        if self.raw_data is None:
            raise ValueError("Dataset not loaded. Call load_dataset() first.")
        
        info = {
            'shape': self.raw_data.shape,
            'columns': list(self.raw_data.columns),
            'dtypes': self.raw_data.dtypes.to_dict(),
            'memory_usage_mb': self.raw_data.memory_usage(deep=True).sum() / 1024**2,
            'null_counts': self.raw_data.isnull().sum().to_dict()
        }
        
        return info
    
    def save_raw_data(self, filepath: str) -> None:
        """
        Save raw data to file
        
        Args:
            filepath: Path to save the raw data (CSV format)
        """
        if self.raw_data is None:
            raise ValueError("No data to save. Load dataset first.")
        
        self.raw_data.to_csv(filepath, index=False)
        logger.info(f"Raw data saved to: {filepath}")
    
    def get_data(self) -> Optional[pd.DataFrame]:
        """
        Get the loaded raw data
        
        Returns:
            pandas DataFrame or None if not loaded
        """
        return self.raw_data
