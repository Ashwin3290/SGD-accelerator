from crewai import Agent, Task, Crew, LLM
import os
import traceback
import logging
import pandas as pd
from typing import Optional, Tuple
import re

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SyntheticDataGenerator:
    def __init__(self, industry: str):
        """
        Initialize the Synthetic Data Generation Framework
        
        Args:
            industry (str): Industry name for data generation
        """
        self.industry = industry
        self.synthetic_dataset = None
        self.max_retries = 1
        
        # Initialize LLM
        self.llm = LLM(
    model="gemini/gemini-1.5-pro-001",
    api_key="AIzaSyArhxma4TjpohVhIFYI0Qc5id9f-tsEeS8"
)
        
        # Create agents
        self.industry_expert_agent = self._create_industry_expert_agent()
        self.dataset_scout_agent = self.create_dataset_scout_agent()
        self.data_analyst_agent = self.create_data_analyst_agent()
        self.synthetic_data_creator_agent = self.create_synthetic_data_creator_agent()
        
        # Create tasks
        self.industry_template_task = self._create_industry_template_task()
        self.scout_task = self.create_scout_task()
        self.analysis_task = self.create_analysis_task()
        self.synthetic_generation_task = self.create_synthetic_generation_task()
        
        # Create crew
        self.crew = Crew(
            agents=[
                self.industry_expert_agent,
                self.dataset_scout_agent,  
                self.synthetic_data_creator_agent
            ],
            tasks=[
                self.industry_template_task,
                self.scout_task, 
                self.synthetic_generation_task
            ]
        )
    
    def _create_industry_expert_agent(self):
        """Create agent responsible for generating industry-specific dataset template"""
        return Agent(
            role='Industry Data Expert',
            goal=f'Generate a comprehensive dataset template for the {self.industry} industry',
            backstory='An AI specialist with deep knowledge of industry-specific data structures and characteristics',
            llm=self.llm,
            verbose=True
        )
    
    def create_dataset_scout_agent(self):
        """Create agent responsible for initial dataset investigation"""
        return Agent(
            role='Dataset Scout',
            goal='Investigate and prepare initial dataset for synthetic data generation',
            backstory='An expert in data exploration and preliminary analysis',
            llm=self.llm,
            verbose=True
        )
    
    def create_data_analyst_agent(self):
        """Create agent responsible for detailed data analysis"""
        return Agent(
            role='Data Analyst',
            goal='Perform in-depth statistical analysis of the dataset',
            backstory='A statistical expert who understands data distributions and patterns',
            llm=self.llm,
            verbose=True
        )
    
    def create_synthetic_data_creator_agent(self):
        """Create agent responsible for generating synthetic data"""
        return Agent(
            role='Synthetic Data Creator',
            goal='Generate new synthetic dataset pandas code maintaining original data characteristics .only use numpy and pandas librabry for creation',
            backstory='An AI specialist in generating statistically similar synthetic datasets pandas code .only use numpy and pandas librabry for creation',
            llm=self.llm,
            verbose=True
        )
    
    def _create_industry_template_task(self):
        """Create task for generating industry-specific dataset template"""
        return Task(
            description=f'''Create a detailed dataset template for the {self.industry} industry that reflects real-world data patterns.
Provide a comprehensive JSON structure including:
1. Essential and advanced columns specific to {self.industry} operations
2. Precise data types with specific formats (e.g., datetime patterns, numeric precisions)
3. Industry-standard value ranges, categories, and distributions
4. Business context and relationships between columns
5. Common data constraints and validation rules''',
            agent=self.industry_expert_agent,
            expected_output='A comprehensive JSON describing the dataset template'
        )
    
    def create_scout_task(self):
        """Create initial scouting task"""
        return Task(
            description=f'''Analyze and prepare an exemplary dataset structure for {self.industry} industry:
1. Define primary and foreign key relationships
2. Specify column constraints and business rules
3. Include industry-specific calculated fields
4. Map dependencies between different columns
5. Document typical data patterns and anomalies
6. Ensure compliance with industry standards and regulations''',
            agent=self.dataset_scout_agent,
            expected_output='A dictionary containing initial dataset information and column details'
        )
    
    def create_analysis_task(self):
        """Create data analysis task"""
        return Task(
            description='''Conduct comprehensive statistical analysis of the dataset:
1. Generate descriptive statistics for all numeric columns
2. Identify and document correlations between variables
3. Analyze seasonal patterns and trends if applicable
4. Define business-driven data distributions
5. Map hierarchical relationships in categorical variables
6. Document outlier patterns and acceptable ranges
Must generate 200 rows with realistic data patterns''',
            agent=self.data_analyst_agent,
            expected_output='Comprehensive statistical summary of the dataset'
        )
    
    def create_synthetic_generation_task(self):
        """Create synthetic data generation task"""
        return Task(
            description=f'''Generate synthetic data for {self.industry} with these requirements:
1. Exactly 200 rows of production-quality data
2. Maintain all statistical properties and correlations
3. Follow industry-specific data patterns and relationships
4. Respect all business rules and constraints
5. Include realistic noise and variations
6. Generate only valid combinations of values
7. All arrays must be of the same length while creating the columns in pandas
Output only the pandas DataFrame creation code without any explanations
only use numpy and pandas librabry for creation

Example format:
                            import pandas as pd
                            import numpy as np
                            # ... rest of the code ...
                            print(df)''',
            agent=self.synthetic_data_creator_agent,
            expected_output='A pandas code for 200 rows synthetic data only the dataframe creation code'
        )

    def save_code_to_file(self, code: str, filename: str) -> None:
        """
        Save generated code to a Python file.
        
        Args:
            code: Python code to save
            filename: Target filename
        """
        try:
            with open(filename, "w") as file:
                file.write(code)
            logger.debug(f"Successfully saved code to {filename}")
        except IOError as e:
            logger.error(f"Failed to save code to {filename}: {str(e)}")
            raise
            
    def save_output_to_log(self, output: Optional[str], log_filename: str) -> None:
        """
        Save execution output to log file.
        
        Args:
            output: Output string to log
            log_filename: Target log filename
        """
        if output is not None:
            try:
                with open(log_filename, "a") as log_file:
                    log_file.write(f"\n{'-'*50}\n{output}\n")
                logger.debug(f"Successfully wrote output to {log_filename}")
            except IOError as e:
                logger.error(f"Failed to write to log file {log_filename}: {str(e)}")

    def execute_pandas_code(self, filename: str):
        """
        Execute pandas code and return the resulting DataFrame or error message.
        
        Args:
            code: Pandas DataFrame creation code
            
        Returns:
            Tuple of (DataFrame if successful, error message if failed)
        """
        try:
            exec(open(filename).read())
            logger.info("Successfully executed code")
            return
        except Exception as e:
            error_message = traceback.format_exc()
            logger.error(f"Error executing code: {error_message}")
            return error_message

    def regenerate_with_error_context(self, error_message: str, pandas_code: str) -> str:
        """
        Advanced synthetic data regeneration method with comprehensive error handling and context.
        
        Args:
            error_message (str): Detailed error message from failed execution
            pandas_code (str): Original pandas code that failed
        
        Returns:
            str: Regenerated, error-free pandas DataFrame creation code
        """
        error_context_task = Task(
            description=f"""ADVANCED SYNTHETIC DATA REGENERATION CHALLENGE

              PREVIOUS CONTEXT:
              - Original Code Attempted: 
              {pandas_code}

              ERROR ENCOUNTERED: 
              {error_message}

              COMPREHENSIVE REGENERATION REQUIREMENTS:
              1. Diagnostic Objectives:
                - Completely resolve the previous implementation's error
                - Ensure 100% compatibility with pandas and numpy
                - Generate statistically robust and realistic synthetic data

              2. Data Generation Constraints:
                - Exactly 200 rows
                - Maintain original dataset's conceptual structure
                - Implement rigorous data validation
                - Generate only valid, consistent data combinations
                - Eliminate all potential error sources

              3. Technical Specifications:
                - ONLY use numpy and pandas libraries
                - No external data generation libraries
                - Implement safe type conversions
                - Use vectorized operations
                - Add explicit error prevention mechanisms

              4. Data Quality Criteria:
                - No NaN or None values
                - Consistent data types across columns
                - Realistic value ranges
                - Mathematically sound relationships between columns
                - Statistically representative distributions

              5. Error Prevention Strategies:
                - Use numpy's random generation with fixed seed
                - Implement type checking
                - Use safe casting methods
                - Add boundary condition handling
                - Eliminate potential division by zero
                - Prevent incompatible data type interactions

              6. Specific Remediation Goals:
                - If original error was type-related: Implement strict type casting
                - If error was value generation: Add comprehensive validation
                - If error involved complex calculations: Simplify and add safeguards
                - If error suggested inconsistent array lengths: Ensure uniform generation

              CRITICAL INSTRUCTIONS:
              - Output MUST be pure pandas/numpy code
              - No explanatory comments
              - No external library imports
              - Complete, executable code block
              - Demonstrate absolute robustness

              FORBIDDEN ACTIONS:
              - Do not use lambda functions
              - Avoid complex nested generations
              - No dynamic typing
              - No external random generators
              - No manual loops for data generation

              OUTPUT FORMAT:
              ```python
              import pandas as pd
              import numpy as np

              # COMPLETE SYNTHETIC DATA GENERATION CODE
              df = pd.DataFrame({{
                  'Columns with safe, vectorized generation'
              }})
              print(df)
              ```
              example code :
              ```python
              import pandas as pd
              import numpy as np

              # Define the columns and their respective distributions
              columns = ['account_number', 'customer_id', 'account_type', 'account_status', 'opening_date', 'balance', 'credit_limit', 'loan_amount', 'interest_rate', 'payment_frequency', 'payment_amount', 'payment_date', 'transaction_date', 'transaction_amount', 'transaction_type', 'branch_id', 'branch_name']
              distributions = {{
                  'account_number': np.random.randint(1000000000, 9999999999, 200),
                  'customer_id': np.random.randint(1000000000, 9999999999, 200),
                  'account_type': np.random.choice(['checking', 'savings', 'credit'], 200),
                  'account_status': np.random.choice(['active', 'inactive'], 200),
                  'opening_date': pd.date_range(start='2020-01-01', periods=200),
                  'balance': np.random.normal(1000, 500, 200),
                  'credit_limit': np.random.normal(5000, 2000, 200),
                  'loan_amount': np.random.normal(10000, 5000, 200),
                  'interest_rate': np.random.uniform(0, 10, 200),
                  'payment_frequency': np.random.choice(['monthly', 'quarterly', 'annually'], 200),
                  'payment_amount': np.random.normal(500, 200, 200),
                  'payment_date': pd.date_range(start='2020-01-01', periods=200),
                  'transaction_date': pd.date_range(start='2020-01-01', periods=200),
                  'transaction_amount': np.random.normal(100, 50, 200),
                  'transaction_type': np.random.choice(['deposit', 'withdrawal', 'transfer'], 200),
                  'branch_id': np.random.randint(1, 4, 200),
                  'branch_name': np.random.choice(['Main Branch', 'Branch 2', 'Branch 3'], 200)
              }}

              # Create the DataFrame
              df = pd.DataFrame(distributions)

              # Set the account_number as the index
              df.set_index('account_number', inplace=True)

              print(df)
              ```
              """,
            agent=self.synthetic_data_creator_agent,
            expected_output='Complete, error-free pandas DataFrame generation code block'
        )
        
        # Create a specialized agent for error resolution
        error_resolution_agent = Agent(
            role='Synthetic Data Error Resolution Specialist',
            goal='Generate impeccable, error-free synthetic dataset generation code using only pandas and numpy',
            backstory='''Advanced AI specialist in creating robust, statistically valid synthetic datasets.
            Expertise in diagnosing and resolving complex data generation challenges.
            Masters in preventing runtime errors and ensuring data consistency.
            Specializes in vectorized, type-safe data generation strategies.''',
            llm=self.llm,
            verbose=True
        )
        
        # Create a focused crew for error resolution
        error_resolution_crew = Crew(
            agents=[error_resolution_agent],
            tasks=[error_context_task],
            max_rpm=10  # Prevent rate limiting
        )
        
        result = error_resolution_crew.kickoff()
            
        return result.raw

    def generate_synthetic_data(self):
        """
        Generate synthetic data with error handling and code regeneration.

        """
        attempts = 0
        # Get initial results from the crew
        result = self.crew.kickoff()
        # return result
        
        # Extract the pandas code from the final task result
        pandas_code = result.raw  # Assuming the last result is the synthetic data code
        print(pandas_code)
        match = re.search(r"```(?:python)?\n(.*?)```", str(result.raw), re.DOTALL | re.IGNORECASE)
        if match:
            pandas_code = match.group(1).strip()
        # # Save the generated code
        self.save_code_to_file(pandas_code, f"{self.industry}_synthetic_data.py")
        
        # # Execute the pandas code
        error = self.execute_pandas_code(f"{self.industry}_synthetic_data.py")
        if error:
            return 0
        while error and attempts < self.max_retries:
            # Log the error
            print("****************",attempts,"**************************")
            self.save_output_to_log(error, f"{self.industry}_errors.log")
            logger.info(f"Attempt {attempts + 1} failed. Regenerating code...")
            # Regenerate code with error context
            pandas_code = self.regenerate_with_error_context(error,pandas_code)
            print("*************************************************************************************************")
            print(pandas_code)
            match = re.search(r"```(?:python)?\n(.*?)```", str(result.raw), re.DOTALL | re.IGNORECASE)
            if match:
              pandas_code = match.group(1).strip()
            self.save_code_to_file(pandas_code, f"{self.industry}_synthetic_data.py")
            print("*************************************************************************************************")
            error = self.execute_pandas_code(f"{self.industry}_synthetic_data.py")
            attempts += 1          
        logger.info("Successfully generated and executed synthetic data")
        return pandas_code
            
            
    # raise RuntimeError(f"Failed to generate synthetic data after {self.max_retries} attempts")

def generate_synthetic_dataset(industry: str) -> pd.DataFrame:
    """
    Main function to generate synthetic dataset with error handling.
    
    Args:
        industry (str): Industry name
    
    Returns:
        pd.DataFrame: Synthetic dataset
    """
    generator = SyntheticDataGenerator(industry)
    return generator.generate_synthetic_data()


