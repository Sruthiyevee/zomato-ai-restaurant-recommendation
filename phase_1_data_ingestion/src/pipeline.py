"""
Main Pipeline for Phase 1 Data Ingestion
Orchestrates the complete data ingestion, cleaning, preprocessing, and storage process
"""

import logging
from pathlib import Path
from typing import Optional
import pandas as pd

from loader import ZomatoDataLoader
from cleaner import ZomatoDataCleaner
from preprocessor import ZomatoDataPreprocessor
from storage import ZomatoDataStorage

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Phase1Pipeline:
    """Complete pipeline for Phase 1 data ingestion"""
    
    def __init__(
        self,
        dataset_name: str = "ManikaSaini/zomato-restaurant-recommendation",
        db_path: str = "phase_1_data_ingestion/data/processed/zomato_restaurants.db",
        save_raw: bool = True,
        save_processed: bool = True
    ):
        """
        Initialize the pipeline
        
        Args:
            dataset_name: Hugging Face dataset identifier
            db_path: Path to SQLite database
            save_raw: Whether to save raw data to CSV
            save_processed: Whether to save processed data to CSV/JSON
        """
        self.dataset_name = dataset_name
        self.db_path = db_path
        self.save_raw = save_raw
        self.save_processed = save_processed
        
        self.loader = None
        self.cleaner = None
        self.preprocessor = None
        self.storage = None
        
        self.raw_data = None
        self.cleaned_data = None
        self.processed_data = None
    
    def run(self) -> pd.DataFrame:
        """
        Run the complete pipeline
        
        Returns:
            Processed pandas DataFrame
        """
        logger.info("=" * 60)
        logger.info("Starting Phase 1 Data Ingestion Pipeline")
        logger.info("=" * 60)
        
        try:
            # Step 1: Load data
            logger.info("\n[STEP 1] Loading dataset from Hugging Face...")
            self.loader = ZomatoDataLoader(dataset_name=self.dataset_name)
            self.raw_data = self.loader.load_dataset()
            
            # Display dataset info
            info = self.loader.get_dataset_info()
            logger.info(f"Dataset loaded: {info['shape'][0]} rows, {info['shape'][1]} columns")
            logger.info(f"Memory usage: {info['memory_usage_mb']:.2f} MB")
            
            # Save raw data if requested
            if self.save_raw:
                raw_path = "phase_1_data_ingestion/data/raw/zomato_raw_data.csv"
                self.loader.save_raw_data(raw_path)
            
            # Step 2: Clean data
            logger.info("\n[STEP 2] Cleaning data...")
            self.cleaner = ZomatoDataCleaner(self.raw_data)
            self.cleaned_data = self.cleaner.clean()
            
            # Display cleaning stats
            cleaning_stats = self.cleaner.get_cleaning_stats()
            logger.info(f"Cleaning complete:")
            logger.info(f"  - Initial records: {cleaning_stats['initial_count']}")
            logger.info(f"  - Final records: {cleaning_stats['final_count']}")
            logger.info(f"  - Removed: {cleaning_stats['removed_count']} ({cleaning_stats['removal_percentage']:.2f}%)")
            
            # Step 3: Preprocess data
            logger.info("\n[STEP 3] Preprocessing data...")
            self.preprocessor = ZomatoDataPreprocessor(self.cleaned_data)
            self.processed_data = self.preprocessor.preprocess()
            
            # Display preprocessing stats
            preprocessing_stats = self.preprocessor.get_preprocessing_stats()
            logger.info(f"Preprocessing complete:")
            logger.info(f"  - Total restaurants: {preprocessing_stats['total_restaurants']}")
            logger.info(f"  - Unique cities: {preprocessing_stats['unique_cities']}")
            logger.info(f"  - Average rating: {preprocessing_stats['average_rating']:.2f}")
            logger.info(f"  - Total reviews: {preprocessing_stats['total_reviews']}")
            
            # Step 4: Store data
            logger.info("\n[STEP 4] Storing processed data...")
            self.storage = ZomatoDataStorage(db_path=self.db_path)
            self.storage.connect()
            self.storage.create_schema()
            self.storage.store_data(self.processed_data)
            
            # Display storage stats
            storage_stats = self.storage.get_storage_stats()
            logger.info(f"Storage complete:")
            logger.info(f"  - Stored restaurants: {storage_stats['total_restaurants']}")
            logger.info(f"  - Cities: {storage_stats['cities']}")
            logger.info(f"  - Average rating: {storage_stats['average_rating']:.2f}")
            
            # Save processed data if requested
            if self.save_processed:
                processed_csv_path = "phase_1_data_ingestion/data/processed/zomato_processed_data.csv"
                processed_json_path = "phase_1_data_ingestion/data/processed/zomato_processed_data.json"
                
                self.storage.save_to_csv(self.processed_data, processed_csv_path)
                self.storage.save_to_json(self.processed_data, processed_json_path)
                logger.info(f"Processed data saved to CSV and JSON")
            
            self.storage.disconnect()
            
            logger.info("\n" + "=" * 60)
            logger.info("Phase 1 Pipeline Completed Successfully!")
            logger.info("=" * 60)
            
            return self.processed_data
            
        except Exception as e:
            logger.error(f"Pipeline failed: {str(e)}", exc_info=True)
            raise
    
    def get_summary(self) -> dict:
        """Get summary of pipeline execution"""
        summary = {
            'raw_data_shape': self.raw_data.shape if self.raw_data is not None else None,
            'cleaned_data_shape': self.cleaned_data.shape if self.cleaned_data is not None else None,
            'processed_data_shape': self.processed_data.shape if self.processed_data is not None else None,
            'cleaning_stats': self.cleaner.get_cleaning_stats() if self.cleaner else None,
            'preprocessing_stats': self.preprocessor.get_preprocessing_stats() if self.preprocessor else None,
            'storage_stats': self.storage.get_storage_stats() if self.storage else None
        }
        return summary


def main():
    """Main entry point for the pipeline"""
    pipeline = Phase1Pipeline()
    processed_data = pipeline.run()
    
    # Display summary
    summary = pipeline.get_summary()
    print("\n" + "=" * 60)
    print("PIPELINE SUMMARY")
    print("=" * 60)
    print(f"Raw data: {summary['raw_data_shape']}")
    print(f"Cleaned data: {summary['cleaned_data_shape']}")
    print(f"Processed data: {summary['processed_data_shape']}")
    print("=" * 60)


if __name__ == "__main__":
    main()
