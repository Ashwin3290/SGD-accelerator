from sdv.single_table import GaussianCopulaSynthesizer
from base import BaseSynthesizer
from typing import Dict, Type, Any, List

class GaussianCopula(BaseSynthesizer):
    """Specific implementation for GaussianCopula Synthesizer"""
    
    def __init__(self, 
                 table_type: str = 'single', 
                 metadata_config: Dict[str, Any] = None,
                 **gaussiancopula_params):
        """
        Initialize GaussianCopula Synthesizer
        
        Args:
            table_type (str): Type of table generation
            metadata_config (dict): Configuration for metadata
            **gaussiancopula_params: Additional GaussianCopula specific parameters
        """
        super().__init__(table_type, metadata_config)
        self.gaussiancopula_params = gaussiancopula_params
    
    def train(self, data):
        """
        Train GaussianCopula Synthesizer
        
        Args:
            data (pd.DataFrame or Dict[str, pd.DataFrame]): Training data
        """
        processed_data = self.preprocess(data)
        if self.metadata is None:
            self.detect_metadata(processed_data)
        
        self.synthesizer = GaussianCopulaSynthesizer(
            metadata=self.metadata, 
            **self.gaussiancopula_params
        )
        self.synthesizer.fit(processed_data)
        
    def generate(self, num_samples: int):
        """
        Generate synthetic data using trained GaussianCopula model
        
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

    def save(self, filepath):
        """
        Save the trained synthesizer to a file
        
        Args:
            filepath (str): Path to save the synthesizer
        """
        self.synthesizer.save(filepath)
    
    @classmethod
    def load(cls, filepath):
        """
        Load a previously saved synthesizer
        
        Args:
            filepath (str): Path to the saved synthesizer
        
        Returns:
            Loaded synthesizer instance
        """
        loaded_synthesizer = GaussianCopulaSynthesizer.load(filepath)
        
        # Create a new instance of the wrapper
        wrapper = cls(table_type='single')
        wrapper.synthesizer = loaded_synthesizer
        wrapper.metadata = loaded_synthesizer.get_metadata()
        
        return wrapper
