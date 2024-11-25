import os
import inspect
import importlib.util
from typing import Dict, Type, Any, List
import pandas as pd
import numpy as np
from sdv.metadata import SingleTableMetadata
from sdv.evaluation.single_table import evaluate_quality, get_column_plot, get_column_pair_plot
import json
from base import BaseSynthesizer

class SynthesizerRegistry:
    """
    Registry for managing and discovering available synthetic data generators
    """
    
    def __init__(self, synthesizers_dir: str = "synthesizers"):
        """
        Initialize the synthesizer registry
        
        Args:
            synthesizers_dir (str): Path to directory containing synthesizer implementations
        """
        self.synthesizers: Dict[str, Type[BaseSynthesizer]] = {}
        self.synthesizers_dir = synthesizers_dir
        
        self._discover_synthesizers()
    
    def _import_module_from_file(self, file_path: str):
        """
        Dynamically import a Python module from a file path
        
        Args:
            file_path (str): Path to the Python file to import
        
        Returns:
            Imported module object
        """
        module_name = os.path.splitext(os.path.basename(file_path))[0]
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        
        if spec is None or spec.loader is None:
            return None
        
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    
    def _discover_synthesizers(self) -> None:
        """
        Automatically discover and register all synthesizer classes from the synthesizers directory.
        Looks for any Python files in the synthesizers directory and its subdirectories.
        """
        synthesizers_dir = os.path.abspath(self.synthesizers_dir)
        
        if not os.path.exists(synthesizers_dir):
            raise ValueError(f"Synthesizers directory '{synthesizers_dir}' does not exist")

        for root, _, files in os.walk(synthesizers_dir):
            for file in files:
                if file.endswith('.py') and not file.startswith('__'):
                    file_path = os.path.join(root, file)
                    
                    try:
                        module = self._import_module_from_file(file_path)
                        if module is None:
                            continue

                        for name, obj in inspect.getmembers(module):
                            if (inspect.isclass(obj) and 
                                issubclass(obj, BaseSynthesizer) and 
                                obj != BaseSynthesizer):
                                synthesizer_name = name.lower()
                                self.synthesizers[synthesizer_name] = obj
                                
                    except Exception as e:
                        print(f"Error loading synthesizer from {file_path}: {str(e)}")
    
    def register_synthesizer(self, name: str, synthesizer_class: Type[BaseSynthesizer]):
        """
        Manually register a new synthesizer
        
        Args:
            name (str): Name to register the synthesizer under
            synthesizer_class (Type[BaseSynthesizer]): The synthesizer class to register
        """
        if not issubclass(synthesizer_class, BaseSynthesizer):
            raise ValueError("Synthesizer must inherit from BaseSynthesizer")
        
        self.synthesizers[name.lower()] = synthesizer_class
    
    def get_synthesizer(self, name: str) -> Type[BaseSynthesizer]:
        """
        Get a synthesizer class by name
        
        Args:
            name (str): Name of the synthesizer to retrieve
        
        Returns:
            The synthesizer class if found
        """
        return self.synthesizers.get(name.lower())
    
    def list_synthesizers(self) -> list:
        """
        List all registered synthesizers
        
        Returns:
            List of registered synthesizer names
        """
        return list(self.synthesizers.keys())

class TableAnalyzer:
    """Analyzes table characteristics to recommend appropriate synthesizer types"""
    
    @staticmethod
    def analyze_table(df: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze table characteristics to determine suitable synthesizer types
        
        Args:
            df (pd.DataFrame): Input table
            
        Returns:
            Dict with table analysis results
        """
        analysis = {
            'size': len(df),
            'columns': len(df.columns),
            'categorical_columns': len(df.select_dtypes(include=['object', 'category']).columns),
            'numerical_columns': len(df.select_dtypes(include=['int64', 'float64']).columns),
            'null_percentage': df.isnull().mean().mean() * 100,
            'unique_value_ratios': {col: df[col].nunique() / len(df) for col in df.columns}
        }
        
        # Recommend synthesizer based on characteristics
        if analysis['categorical_columns'] > analysis['numerical_columns']:
            analysis['recommended_synthesizer'] = 'ctgan'
        else:
            analysis['recommended_synthesizer'] = 'gaussian_copula'
            
        return analysis

class MultiTableSynthesisCoordinator:
    """Coordinates synthesis of multiple related tables"""
    
    def __init__(self, registry: SynthesizerRegistry):
        """
        Initialize coordinator with synthesizer registry
        
        Args:
            registry (SynthesizerRegistry): Registry of available synthesizers
        """
        self.registry = registry
        self.table_relationships = {}
        self.synthesizers = {}
        self.metadata = {}
        self.analyzer = TableAnalyzer()
        
    def identify_relationships(self, tables: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """
        Identify relationships between tables
        
        Args:
            tables (Dict[str, pd.DataFrame]): Dictionary of tables
            
        Returns:
            Dict containing relationship information
        """
        relationships = {
            'primary_keys': {},
            'foreign_keys': {},
            'dependencies': {}
        }
        
        # Identify primary keys
        for table_name, df in tables.items():
            for col in df.columns:
                if df[col].is_unique and df[col].nunique() == len(df):
                    relationships['primary_keys'][table_name] = col
                    break
        
        # Identify foreign keys and dependencies
        for table_name, df in tables.items():
            if table_name not in relationships['primary_keys']:
                for col in df.columns:
                    for pk_table, pk_col in relationships['primary_keys'].items():
                        if set(df[col].unique()).issubset(set(tables[pk_table][pk_col].unique())):
                            if table_name not in relationships['foreign_keys']:
                                relationships['foreign_keys'][table_name] = {}
                            relationships['foreign_keys'][table_name][col] = (pk_table, pk_col)
                            
                            # Track dependencies for ordering
                            if table_name not in relationships['dependencies']:
                                relationships['dependencies'][table_name] = set()
                            relationships['dependencies'][table_name].add(pk_table)
        
        return relationships
    
        
    def create_metadata(self, df: pd.DataFrame, table_name: str) -> SingleTableMetadata:
        """
        Create metadata for a table with appropriate constraints
        
        Args:
            df (pd.DataFrame): Input table
            table_name (str): Name of the table
            
        Returns:
            SingleTableMetadata: Configured metadata
        """
        metadata = SingleTableMetadata()
        metadata.detect_from_dataframe(data=df)
        
 
            
        # Set primary key if exists
        if table_name in self.table_relationships['primary_keys']:
            pk_col = self.table_relationships['primary_keys'][table_name]
            metadata.set_primary_key(pk_col)
       
        return metadata
    
    def setup_synthesizers(self, 
                          tables: Dict[str, pd.DataFrame], 
                          synthesizer_choices: Dict[str, str] = None,
                          synthesizer_params: Dict[str, Dict[str, Any]] = None) -> None:
        """
        Set up synthesizers for all tables
        
        Args:
            tables (Dict[str, pd.DataFrame]): Dictionary of tables
            synthesizer_choices (Dict[str, str]): Optional manual synthesizer choices
            synthesizer_params (Dict[str, Dict]): Optional parameters for synthesizers
        """
        self.table_relationships = self.identify_relationships(tables)
        
        # Determine processing order based on dependencies
        processing_order = self._determine_processing_order()
        
        for table_name in processing_order:
            df = tables[table_name]
            
            # Analyze table and get recommended synthesizer if not manually specified
            analysis = self.analyzer.analyze_table(df)
            synthesizer_type = synthesizer_choices.get(table_name, analysis['recommended_synthesizer']) if synthesizer_choices else analysis['recommended_synthesizer']
            
            # Get synthesizer class and parameters
            SynthesizerClass = self.registry.get_synthesizer(synthesizer_type)
            params = synthesizer_params.get(table_name, {}) if synthesizer_params else {}
            
            metadata = self.create_metadata(df, table_name)
            self.metadata[table_name] = metadata
            
            # Initialize and store synthesizer
            self.synthesizers[table_name] = SynthesizerClass(
                table_type='single',
                metadata_config=metadata,
                **params
            )
            
    def _determine_processing_order(self) -> List[str]:
        """
        Determine the order in which tables should be processed
        
        Returns:
            List[str]: Ordered list of table names
        """
        dependencies = self.table_relationships['dependencies']
        order = []
        processed = set()
        
        def process_table(table):
            if table in processed:
                return
            if table in dependencies:
                for dep in dependencies[table]:
                    process_table(dep)
            order.append(table)
            processed.add(table)
        
        # Process all tables
        tables = set(self.table_relationships['primary_keys'].keys()) | \
                set(self.table_relationships['foreign_keys'].keys())
        for table in tables:
            process_table(table)
            
        return order
    
    def train(self, tables: Dict[str, pd.DataFrame]) -> None:
        """
        Train all synthesizers
        
        Args:
            tables (Dict[str, pd.DataFrame]): Dictionary of tables
        """
        for table_name, synthesizer in self.synthesizers.items():
            synthesizer.train(tables[table_name])
    
    def generate(self, num_samples: int) -> Dict[str, pd.DataFrame]:
        """
        Generate synthetic data for all tables
        
        Args:
            num_samples (int): Number of samples to generate
            
        Returns:
            Dict[str, pd.DataFrame]: Dictionary of synthetic tables
        """
        synthetic_tables = {}
        processing_order = self._determine_processing_order()
        
        for table_name in processing_order:
            synthetic_df = self.synthesizers[table_name].generate(num_samples)
            
            # Adjust foreign keys if necessary
            if table_name in self.table_relationships['foreign_keys']:
                for fk_col, (pk_table, pk_col) in self.table_relationships['foreign_keys'][table_name].items():
                    valid_keys = synthetic_tables[pk_table][pk_col].values
                    synthetic_df[fk_col] = np.random.choice(valid_keys, size=len(synthetic_df))
            
            synthetic_tables[table_name] = synthetic_df
        
        return synthetic_tables
    
    def save(self, directory: str) -> None:
        """
        Save all synthesizers and metadata
        
        Args:
            directory (str): Directory to save synthesizers
        """
        os.makedirs(directory, exist_ok=True)
        
        # Save synthesizers
        for table_name, synthesizer in self.synthesizers.items():
            synthesizer_dir = os.path.join(directory, table_name)
            os.makedirs(synthesizer_dir, exist_ok=True)
            synthesizer.save(os.path.join(synthesizer_dir, "synthesizer.pkl"))
        
        # Save relationships and metadata
        with open(os.path.join(directory, "relationships.json"), "w") as f:
            json.dump(self.table_relationships, f)
    
    @classmethod
    def load(cls, directory: str, registry: SynthesizerRegistry) -> 'MultiTableSynthesisCoordinator':
        """
        Load saved coordinator
        
        Args:
            directory (str): Directory containing saved synthesizers
            registry (SynthesizerRegistry): Registry of available synthesizers
            
        Returns:
            MultiTableSynthesisCoordinator: Loaded coordinator
        """
        coordinator = cls(registry)
        
        # Load relationships
        with open(os.path.join(directory, "relationships.json"), "r") as f:
            coordinator.table_relationships = json.load(f)
        
        # Load synthesizers
        for table_dir in os.listdir(directory):
            if os.path.isdir(os.path.join(directory, table_dir)):
                synthesizer_path = os.path.join(directory, table_dir, "synthesizer.pkl")
                if os.path.exists(synthesizer_path):
                    coordinator.synthesizers[table_dir] = coordinator.registry.get_synthesizer(
                        'gaussian_copula'
                    ).load(synthesizer_path)
        
        return coordinator


class SynthesizerManager:
    def __init__(self):
        self.registry = SynthesizerRegistry()
        
    def handle_single_table(self, data: pd.DataFrame, synthesizer_name: str, num_samples: int) -> Dict[str, Any]:
        """Handle single table synthesis"""
        synth_class = self.registry.get_synthesizer(synthesizer_name)
        synthesizer = synth_class(table_type='single')
        
        # Create metadata
        metadata = SingleTableMetadata()
        metadata.detect_from_dataframe(data=data)

        for column_name, column_metadata in metadata.columns.items():
            if column_metadata['sdtype'] == 'unknown':
                metadata.update_column(column_name, sdtype='categorical')
        synthesizer.metadata_config = metadata
        synthesizer.train(data)
        return synthesizer.generate_and_evaluate(num_samples)
    
    def handle_multi_table(self, tables: Dict[str, pd.DataFrame], synthesizer_name: str, num_samples: int) -> Dict[str, Any]:
        """Handle multi-table synthesis"""
        from synthetic import MultiTableSynthesisCoordinator
        
        coordinator = MultiTableSynthesisCoordinator(self.registry)
        synthesizer_choices = {name: synthesizer_name for name in tables.keys()}
        
        coordinator.setup_synthesizers(tables, synthesizer_choices=synthesizer_choices)
        coordinator.train(tables)
        
        synthetic_tables = coordinator.generate(num_samples)
        
        return {
            'synthetic_data': synthetic_tables,
            'reports': self._generate_multi_table_reports(tables, synthetic_tables)
        }
    def _generate_multi_table_reports(self, original_tables: Dict[str, pd.DataFrame], 
                                    synthetic_tables: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """Generate reports for multi-table synthesis with robust error handling"""
        table_analysis_reports = {'quality_report': {'tables': {}}}
        
        for table_identifier in original_tables.keys():
            original_dataset = original_tables[table_identifier]
            synthetic_dataset = synthetic_tables[table_identifier]
            
            # Get metadata for current table
            table_metadata = SingleTableMetadata()
            table_metadata.detect_from_dataframe(data=original_dataset)
            
            # Filter columns excluding sensitive data types
            column_metadata = table_metadata.columns
            analysis_columns = []
            for column_name in column_metadata:
                if column_metadata[column_name]['sdtype'] not in ['id', 'first_name', 'last_name', 'email', 'phone_number']:
                    analysis_columns.append(column_name)
            
            current_table_report = {
                'quality_metrics': evaluate_quality(original_dataset, synthetic_dataset,table_metadata),
                'column_plots': {},
                'pair_plots': {}
            }
            
            # Generate column plots with error handling
            for column_name in analysis_columns:
                try:
                    distribution_plot = get_column_plot(original_dataset, synthetic_dataset, 
                                                    column_name=column_name, 
                                                    metadata=table_metadata)
                    current_table_report['column_plots'][column_name] = distribution_plot
                except Exception as error_msg:
                    print(f"Skipping column plot for {column_name} due to: {str(error_msg)}")
                    continue
            
            # Generate pair plots with error handling
            for first_col_index in range(len(analysis_columns)):
                for second_col_index in range(first_col_index + 1, len(analysis_columns)):
                    first_column = analysis_columns[first_col_index]
                    second_column = analysis_columns[second_col_index]
                    try:
                        correlation_plot = get_column_pair_plot(original_dataset, synthetic_dataset, 
                                                            column_names=[first_column, second_column], 
                                                            metadata=table_metadata)
                        pair_key = f"{first_column}_{second_column}"
                        current_table_report['pair_plots'][pair_key] = correlation_plot
                    except Exception as error_msg:
                        print(f"Skipping pair plot for {first_column}_{second_column} due to: {str(error_msg)}")
                        continue
            
            table_analysis_reports['quality_report']['tables'][table_identifier] = current_table_report
        
        return table_analysis_reports
