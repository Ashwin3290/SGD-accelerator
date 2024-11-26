from sdv.sequential import PARSynthesizer
from typing import Dict, Any, List
import pandas as pd
from gan.base import BaseSynthesizer

class PAR(BaseSynthesizer):
    """Specific implementation for PAR (Parallel Auto-Regressive) Synthesizer for sequential data"""
    
    def __init__(self, 
                 table_type: str = 'single', 
                 metadata_config: Dict[str, Any] = None,
                 context_columns: List[str] = None,
                 sequence_key: str = None,
                 sequence_index: str = None,
                 **par_params):
        """
        Initialize PAR Synthesizer
        
        Args:
            table_type (str): Type of table generation
            metadata_config (dict): Configuration for metadata
            context_columns (List[str]): Columns that remain constant within a sequence
            sequence_key (str): Column that identifies each sequence
            sequence_index (str): Column that defines the order within sequences
            **par_params: Additional PAR specific parameters
        """
        super().__init__(table_type, metadata_config)
        self.par_params = par_params
        self.context_columns = context_columns
        self.sequence_key = sequence_key
        self.sequence_index = sequence_index
        self.original_data = None
    
    def detect_metadata(self, data: pd.DataFrame):
        """
        Detect metadata for sequential data
        
        Args:
            data (pd.DataFrame): Input sequential data
        """
        from sdv.metadata import SingleTableMetadata
        
        self.metadata = SingleTableMetadata()
        self.metadata.detect_from_dataframe(data=data)
        self.original_data = data
        
        # Set sequence-specific metadata
        if self.sequence_key:
            self.metadata.set_sequence_key(self.sequence_key)
        if self.sequence_index:
            self.metadata.set_sequence_index(self.sequence_index)
            
        return self.metadata
    
    def train(self, data: pd.DataFrame):
        """
        Train PAR Synthesizer
        
        Args:
            data (pd.DataFrame): Training data
        """
        processed_data = self.preprocess(data)
        if self.metadata is None:
            self.detect_metadata(processed_data)
        
        self.synthesizer = PARSynthesizer(
            metadata=self.metadata,
            context_columns=self.context_columns,
            **self.par_params
        )
        self.synthesizer.fit(processed_data)
    
    def generate(self, num_samples: int, sequence_length: int = None) -> pd.DataFrame:
        """
        Generate synthetic sequential data
        
        Args:
            num_samples (int): Number of sequences to generate
            sequence_length (int, optional): Fixed length for generated sequences
        
        Returns:
            pd.DataFrame: Synthetic sequential data
        """
        if self.synthesizer is None:
            raise ValueError("Model must be trained before generating data")
        
        if sequence_length:
            synthetic_data = self.synthesizer.sample(
                num_sequences=num_samples,
                sequence_length=sequence_length
            )
        else:
            synthetic_data = self.synthesizer.sample(num_sequences=num_samples)
            
        return synthetic_data

    def generate_with_context(self, context_data: pd.DataFrame, sequence_length: int = None) -> pd.DataFrame:
        """
        Generate synthetic data based on specific context values
        
        Args:
            context_data (pd.DataFrame): DataFrame containing context values for each sequence
            sequence_length (int, optional): Fixed length for generated sequences
        
        Returns:
            pd.DataFrame: Synthetic sequential data
        """
        if self.synthesizer is None:
            raise ValueError("Model must be trained before generating data")
            
        if sequence_length:
            return self.synthesizer.sample_sequential_columns(
                context_columns=context_data,
                sequence_length=sequence_length
            )
        return self.synthesizer.sample_sequential_columns(context_columns=context_data)

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
        loaded_synthesizer = PARSynthesizer.load(filepath)
        
        # Create a new instance of the wrapper
        wrapper = cls(
            table_type='single',
            context_columns=loaded_synthesizer.context_columns
        )
        wrapper.synthesizer = loaded_synthesizer
        wrapper.metadata = loaded_synthesizer.metadata
        
        return wrapper
