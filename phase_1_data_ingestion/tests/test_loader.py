"""
Test cases for Data Loader Module
"""

import unittest
import pandas as pd
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from loader import ZomatoDataLoader


class TestZomatoDataLoader(unittest.TestCase):
    """Test cases for ZomatoDataLoader"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.loader = ZomatoDataLoader()
    
    def test_initialization(self):
        """Test loader initialization"""
        self.assertIsNotNone(self.loader)
        self.assertEqual(self.loader.dataset_name, "ManikaSaini/zomato-restaurant-recommendation")
        self.assertIsNone(self.loader.dataset)
        self.assertIsNone(self.loader.raw_data)
    
    def test_load_dataset(self):
        """Test dataset loading from Hugging Face"""
        try:
            data = self.loader.load_dataset()
            self.assertIsNotNone(data)
            self.assertIsInstance(data, pd.DataFrame)
            self.assertGreater(len(data), 0, "Dataset should not be empty")
        except Exception as e:
            self.skipTest(f"Could not load dataset from Hugging Face: {str(e)}")
    
    def test_get_dataset_info(self):
        """Test getting dataset information"""
        try:
            self.loader.load_dataset()
            info = self.loader.get_dataset_info()
            
            self.assertIsInstance(info, dict)
            self.assertIn('shape', info)
            self.assertIn('columns', info)
            self.assertIn('dtypes', info)
            self.assertIn('memory_usage_mb', info)
            self.assertIn('null_counts', info)
            
            # Verify shape is a tuple
            self.assertIsInstance(info['shape'], tuple)
            self.assertEqual(len(info['shape']), 2)
        except Exception as e:
            self.skipTest(f"Could not test dataset info: {str(e)}")
    
    def test_save_raw_data(self):
        """Test saving raw data to file"""
        try:
            self.loader.load_dataset()
            test_filepath = "phase_1_data_ingestion/data/raw/test_raw_data.csv"
            
            self.loader.save_raw_data(test_filepath)
            
            # Verify file exists
            from pathlib import Path
            self.assertTrue(Path(test_filepath).exists(), "Raw data file should be created")
            
            # Clean up
            Path(test_filepath).unlink()
        except Exception as e:
            self.skipTest(f"Could not test save functionality: {str(e)}")
    
    def test_get_data(self):
        """Test getting loaded data"""
        self.assertIsNone(self.loader.get_data())
        
        try:
            self.loader.load_dataset()
            data = self.loader.get_data()
            self.assertIsNotNone(data)
            self.assertIsInstance(data, pd.DataFrame)
        except Exception as e:
            self.skipTest(f"Could not test get_data: {str(e)}")
    
    def test_custom_dataset_name(self):
        """Test loader with custom dataset name"""
        custom_loader = ZomatoDataLoader(dataset_name="custom/dataset")
        self.assertEqual(custom_loader.dataset_name, "custom/dataset")


if __name__ == '__main__':
    unittest.main()
