from sdv.single_table import CTGANSynthesizer
from base import BaseSynthesizer
from typing import Dict, Type, Any, List

class CTGAN(BaseSynthesizer):
    """Specific implementation for CTGAN Synthesizer"""
    
    def __init__(self, 
                 table_type: str = 'single', 
                 metadata_config: Dict[str, Any] = None,
                 **ctgan_params):
        """
        Initialize CTGAN Synthesizer
        
        Args:
            table_type (str): Type of table generation
            metadata_config (dict): Configuration for metadata
            **ctgan_params: Additional CTGAN specific parameters
        """
        super().__init__(table_type, metadata_config)
        self.ctgan_params = ctgan_params
    
    def train(self, data):
        """
        Train CTGAN Synthesizer
        
        Args:
            data (pd.DataFrame or Dict[str, pd.DataFrame]): Training data
        """
        processed_data = self.preprocess(data)
        if self.metadata is None:
            self.detect_metadata(processed_data)
        
        self.synthesizer = CTGANSynthesizer(
            metadata=self.metadata, 
            **self.ctgan_params
        )
        self.synthesizer.fit(processed_data)
        
    def generate(self, num_samples: int):
        """
        Generate synthetic data using trained CTGAN model
        
        Args:
            num_samples (int): Number of samples to generate
        
        Returns:
            Synthetic data (single DataFrame or Dict of DataFrames)
        """
        if self.synthesizer is None:
            raise ValueError("Model must be trained before generating data")
        
        # Generate synthetic data
        synthetic_data = self.synthesizer.sample(num_rows=num_samples)

        return synthetic_data