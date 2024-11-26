from sdv.multi_table import HMASynthesizer
from sdv.metadata import MultiTableMetadata
from gan.base import BaseSynthesizer
from typing import Dict, Any, List
import pandas as pd

class HMA(BaseSynthesizer):
    """Specific implementation for HMA (Hierarchical Model Architecture) Synthesizer"""
    
    def __init__(self, 
                 table_type: str = 'multi', 
                 metadata_config: Dict[str, Any] = None,
                 **hma_params):
        """
        Initialize HMA Synthesizer
        
        Args:
            table_type (str): Type of table generation (should be 'multi')
            metadata_config (dict): Configuration for metadata
            **hma_params: Additional HMA specific parameters
        """
        super().__init__(table_type, metadata_config)
        self.hma_params = hma_params
        self.original_tables = None
    
    def detect_metadata(self, data: Dict[str, pd.DataFrame]):
        """
        Detect metadata for multiple tables
        
        Args:
            data (Dict[str, pd.DataFrame]): Dictionary of input tables
        """
        self.metadata = MultiTableMetadata()
        self.metadata.detect_from_dataframes(data=data)
        self.original_tables = data
        return self.metadata
    
    def train(self, data: Dict[str, pd.DataFrame]):
        """
        Train HMA Synthesizer
        
        Args:
            data (Dict[str, pd.DataFrame]): Dictionary of training tables
        """
        processed_data = self.preprocess(data)
        if self.metadata is None:
            self.detect_metadata(processed_data)
        
        self.synthesizer = HMASynthesizer(
            metadata=self.metadata, 
            **self.hma_params
        )
        self.synthesizer.fit(processed_data)
    
    def generate(self, num_samples: int) -> Dict[str, pd.DataFrame]:
        """
        Generate synthetic data using trained HMA model
        
        Args:
            num_samples (int): Scale factor for synthetic data generation
        
        Returns:
            Dict[str, pd.DataFrame]: Dictionary of synthetic tables
        """
        if self.synthesizer is None:
            raise ValueError("Model must be trained before generating data")
        
        # Generate synthetic data with scaling factor
        synthetic_data = self.synthesizer.sample(scale=num_samples)
        return synthetic_data

    def evaluate(self, real_data: Dict[str, pd.DataFrame], synthetic_data: Dict[str, pd.DataFrame]):
        """
        Evaluate synthetic data quality for multiple tables
        
        Args:
            real_data (Dict[str, pd.DataFrame]): Original tables
            synthetic_data (Dict[str, pd.DataFrame]): Synthetic tables
        
        Returns:
            Quality report for multiple tables
        """
        from sdv.evaluation.multi_table import evaluate_quality
        return evaluate_quality(real_data, synthetic_data, self.metadata)

    def save(self, filepath: str):
        """
        Save the trained synthesizer to a file
        
        Args:
            filepath (str): Path to save the synthesizer
        """
        self.synthesizer.save(filepath)
    
    @classmethod
    def load(cls, filepath: str):
        """
        Load a previously saved synthesizer
        
        Args:
            filepath (str): Path to the saved synthesizer
        
        Returns:
            Loaded synthesizer instance
        """
        loaded_synthesizer = HMASynthesizer.load(filepath)
        
        # Create a new instance of the wrapper
        wrapper = cls(table_type='multi')
        wrapper.synthesizer = loaded_synthesizer
        wrapper.metadata = loaded_synthesizer.metadata
        
        return wrapper

