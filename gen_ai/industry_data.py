from crewai import Agent, Task, Crew, LLM
import os

os.environ['GROQ_API_KEY'] = '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'
 
llm = LLM(
    model="groq/llama3-70b-8192",
    temperature=0.15,
    base_url="https://api.groq.com/openai/v1",
    api_key=os.environ['GROQ_API_KEY']
)

class SyntheticDataGenerator:
    def __init__(self, industry: str):
        """
        Initialize the Synthetic Data Generation Framework
        
        Args:
            industry (str): Industry name for data generation
        """
        self.industry = industry
        self.synthetic_dataset = None
        
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
                self.data_analyst_agent, 
                self.synthetic_data_creator_agent
            ],
            tasks=[
                self.industry_template_task,
                self.scout_task, 
                self.analysis_task, 
                self.synthetic_generation_task
            ]
        )
    
    def _create_industry_expert_agent(self):
        """Create agent responsible for generating industry-specific dataset template"""
        return Agent(
            role='Industry Data Expert',
            goal=f'Generate a comprehensive dataset template for the {self.industry} industry',
            backstory='An AI specialist with deep knowledge of industry-specific data structures and characteristics',
            llm=llm,
            verbose=True
        )
    
    def _create_industry_template_task(self):
        """Create task for generating industry-specific dataset template"""
        return Task(
            description=f'Create a detailed dataset template for the {self.industry} industry. ' +
                        'Provide a JSON structure that includes:' +
                        '1. Recommended columns for this industry' +
                        '2. Data types for each column' +
                        '3. Realistic ranges or categories for each column' +
                        '4. Rationale for including each column',
            agent=self.industry_expert_agent,
            expected_output='A comprehensive JSON describing the dataset template'
        )
    
    def create_dataset_scout_agent(self):
        """Create agent responsible for initial dataset investigation"""
        return Agent(
            role='Dataset Scout',
            goal='Investigate and prepare initial dataset for synthetic data generation',
            backstory='An expert in data exploration and preliminary analysis',
            llm=llm,
            verbose=True
        )
    
    def create_data_analyst_agent(self):
        """Create agent responsible for detailed data analysis"""
        return Agent(
            role='Data Analyst',
            goal='Perform in-depth statistical analysis of the dataset',
            backstory='A statistical expert who understands data distributions and patterns',
            llm=llm,
            verbose=True
        )
    
    def create_synthetic_data_creator_agent(self):
        """Create agent responsible for generating synthetic data"""
        return Agent(
            role='Synthetic Data Creator',
            goal='Generate new synthetic dataset pandas code maintaining original data characteristics',
            backstory='An AI specialist in generating statistically similar synthetic datasets pandas code',
            llm=llm,
            verbose=True
        )
    
    def create_scout_task(self):
        """Create initial scouting task"""
        return Task(
            description=f'Scout and prepare dataset for {self.industry} industry. ' +
                        'create a sample dataset. ' +
                        'Identify key characteristics and potential columns. ensuring proper datatype and range',
            agent=self.dataset_scout_agent,
            expected_output='A dictionary containing initial dataset information and column details'
        )
    
    def create_analysis_task(self):
        """Create data analysis task"""
        return Task(
            description='Perform detailed statistical analysis of the dataset. ' +
                        '200 rows code should be thier. ' +
                        'Analyze distributions, correlations, and key statistical properties. and datatype of column and range according to industry standards',
            agent=self.data_analyst_agent,
            expected_output='Comprehensive statistical summary of the dataset'
        )
    
    def create_synthetic_generation_task(self):
        """Create synthetic data generation task"""
        return Task(
            description="create a pandas code for data frame generation with 200 rows. " +
                        "check the code once , check all column have same number of inputs and use proper function as per the datatype of column"+
                        "treat date time columns properly . only apply the functions that are applicable to the datatype of column"+
                        "give code for the creation only no other statistics or analysis on that data ",
            agent=self.synthetic_data_creator_agent,
            expected_output='A pandas code for 200 rows synthetic data only the dataframe creation code'
        )
    
    def generate_synthetic_data(self):
        """
        Main method to generate synthetic data
        
        Returns:
            pd.DataFrame: Synthetic dataset
        """
        
        # Run crew
        result = self.crew.kickoff()
        
        return result
    

def generate_synthetic_dataset(industry: str):
    """
    Main function to generate synthetic dataset
    
    Args:
        industry (str): Industry name
    
    Returns:
        pd.DataFrame: Synthetic dataset
    """
    generator = SyntheticDataGenerator(industry)
    return generator.generate_synthetic_data()