import os
from typing import Dict, Type, Any, List
from sdv.metadata import SingleTableMetadata
from sdv.evaluation.single_table import evaluate_quality, get_column_plot, get_column_pair_plot,run_diagnostic
from itertools import combinations

class BaseSynthesizer:
    """Base abstract class for all synthetic data generators."""
    def __init__(self,
    table_type: str = 'single',
    metadata_config: Dict[str, Any] = None):
        """
        Initialize the base synthesizer
        
        Args:
            table_type (str): Type of table generation ('single' or 'multi')
            metadata_config (dict): Configuration for metadata detection
        """
        self.table_type = table_type
        self.metadata = None
        self.synthesizer = None
        self.metadata_config = metadata_config or {}
        self.original_tables = None
    
    def detect_metadata(self, data):
        """
        Detect metadata for the input data
        
        Args:
            data (pd.DataFrame or Dict[str, pd.DataFrame]): Input data
        """
        if self.table_type == 'single':
            self.metadata = SingleTableMetadata()
            self.metadata.detect_from_dataframe(data=data)
            self.original_data=data
            for column_name, column_metadata in self.metadata.columns.items():
                if column_metadata['sdtype'] == 'unknown':
                    self.metadata.update_column(column_name, sdtype='categorical')
            return self.metadata
    
    def preprocess(self, data):
        """
        Preprocess data before synthetic data generation
        
        Args:
            data (pd.DataFrame or Dict[str, pd.DataFrame]): Input data
        
        Returns:
            Preprocessed data
        """
        if self.table_type == 'multi':
            return self.detect_metadata(data)
        return data
    
    def train(self, data):
        """
        Train the synthetic data model
        
        Args:
            data (pd.DataFrame or Dict[str, pd.DataFrame]): Training data
        """
        raise NotImplementedError("Subclasses must implement training method")
    
    def generate(self, num_samples: int):
        """
        Generate synthetic data
        
        Args:
            num_samples (int): Number of synthetic samples to generate
        
        Returns:
            Synthetic data or Dict[str, pd.DataFrame]
        """
        raise NotImplementedError("Subclasses must implement generation method")
    
    def evaluate(self, real_data, synthetic_data):
        """
        Evaluate synthetic data quality
        
        Args:
            real_data (pd.DataFrame): Original data
            synthetic_data (pd.DataFrame): Synthetic data
        
        Returns:
            Quality report
        """
        return evaluate_quality(real_data, synthetic_data, self.metadata)
    
    
    def generate_and_evaluate(self, num_samples: int, include_reports: bool = True):
        """
        Generate synthetic data and produce evaluation reports
        
        Args:
            num_samples (int): Number of synthetic samples to generate
            include_reports (bool): Whether to include evaluation reports
            
        Returns:
            dict: Contains synthetic data and evaluation results
        """
        synthetic_data = self.generate(num_samples)
        
        if not include_reports:
            return {'synthetic_data': synthetic_data}
        
        results = {
            'synthetic_data': synthetic_data,
            'reports': {}
        }
        
        # Add diagnostic report
        diagnostic_report = run_diagnostic(
            real_data=self.original_data,
            synthetic_data=synthetic_data,
            metadata=self.metadata
        )
        results['reports']['diagnostic_report'] = diagnostic_report
        
        # Quality evaluation
        quality_report = self.evaluate(self.original_data, synthetic_data)
        results['reports']['quality_report'] = quality_report
        
        # Column plots
        columns = self.metadata.columns
        columns = [col for col in columns if columns[col]['sdtype'] not in ['id', "first_name", "last_name", "email", "phone_number"]]
        results['reports']['column_plots'] = {

            col: get_column_plot(self.original_data, synthetic_data, column_name=col, metadata=self.metadata) 
            for col in columns
        }
        

        # Pair plots
        results['reports']['pair_plots'] = {

            f"{col1}_{col2}": get_column_pair_plot(self.original_data, synthetic_data, column_names=[col1, col2], metadata=self.metadata)
            for col1, col2 in combinations(columns, 2)
        }
    
        return results

    def save_results(self, results, output_dir: str):
        """
        Save synthetic data and evaluation results

    
        Args:
            results (dict): Results from generate_and_evaluate
            output_dir (str): Directory to save results
        """
        os.makedirs(output_dir, exist_ok=True)
    
        # Save synthetic data
        if self.table_type == 'multi':
            for table_name, df in results['synthetic_data'].items():
                df.to_csv(f"{output_dir}/{table_name}_synthetic.csv", index=False)
        else:
            results['synthetic_data'].to_csv(f"{output_dir}/synthetic_data.csv", index=False)
    
        # Save reports
        if 'reports' in results:
            # Save diagnostic report
            diagnostic_report = results['reports']['diagnostic_report']
            diagnostic_report.save(f"{output_dir}/diagnostic_report.json")
        
            # Save data validity details
            validity_details = diagnostic_report.get_details('Data Validity')
            validity_details.to_csv(f"{output_dir}/validity_details.csv")
        
            # Save quality report
            quality_report = results['reports']['quality_report']
            quality_report.save(f"{output_dir}/quality_report.json")
        
            # Save visualizations
            for plot_type, plots in results['reports'].items():
                if plot_type in ['column_plots', 'pair_plots']:
                    plot_dir = f"{output_dir}/{plot_type}"
                    os.makedirs(plot_dir, exist_ok=True)
                    for name, plot in plots.items():
                        plot.write_html(f"{plot_dir}/{name}.html")
