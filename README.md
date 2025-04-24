# Test Data Management System

A comprehensive test data management solution that leverages both GAN (Generative Adversarial Networks) and Generative AI approaches to create high-quality synthetic data for testing purposes.

## Overview

This application provides a streamlined interface for generating synthetic data with two distinct methodologies:

1. **GAN-based Generation**: Utilizes statistical techniques and GANs to produce synthetic data that preserves the statistical properties of real data sources.
   
2. **Generative AI-based Generation**: Employs large language models to intelligently create domain-specific synthetic data with realistic patterns and relationships.

## Features

### GAN-based Generation
- Direct SQL query integration for data source input
- Support for both single-table and multi-table synthetic data generation
- Comprehensive data quality evaluation metrics and visualizations
- Multiple synthesizer options (CTGAN, GaussianCopula, PAR, HMA)
- Detailed distribution plots for comparing real vs. synthetic data

### Generative AI-based Generation
- Industry-specific synthetic data generation
- Custom synthetic data generation from JSON schema
- Semantic, numerical, and logical data validation
- Advanced comparison between original and synthetic datasets
- Comprehensive analysis reports

## Technical Architecture

The system is built on:
- **Streamlit**: For the web interface
- **SDV (Synthetic Data Vault)**: For GAN-based generation
- **CrewAI**: For orchestrating generative AI agents
- **Pandas/NumPy**: For data manipulation and generation
- **MySQL**: For direct database connection

## Getting Started

### Prerequisites
- Python 3.8+
- MySQL server (for database connection)

### Installation

1. Clone the repository
```bash
git clone https://github.com/yourusername/test-data-management-system.git
cd test-data-management-system
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Configure database connection
   - Update `gan/database_config.json` with your database credentials

4. Run the application
```bash
streamlit run app.py
```

## Usage

### GAN-based Generation

1. Select "GAN based generation" from the sidebar
2. Choose a synthesizer type and table type (Single/Multi)
3. Enter your SQL queries to extract source data
4. Set the number of synthetic samples to generate
5. Click "Generate Synthetic Data"
6. Explore generated data and quality metrics

### Generative AI-based Generation

1. Select "Gen-ai based generation" from the sidebar
2. Choose between industry-specific or custom generation
3. For industry-specific: Enter industry name and generate
4. For custom: Upload a JSON schema file with sample data
5. Examine the generated data and comparison reports

## Project Structure

```
├── app.py                 # Main application entry point
├── gan/                   # GAN-based generation modules
│   ├── base.py            # Base synthesizer abstract class
│   ├── database_config.json  # Database connection configuration
│   ├── gan_app.py         # GAN interface module
│   ├── synthetic.py       # Synthesizer manager and registry
│   └── synthesizers/      # Various synthesizer implementations
├── gen_ai/                # Generative AI modules
│   ├── data.json          # Sample data for gen-ai
│   ├── gen_ai_app.py      # Gen-AI interface module
│   ├── industry_data.py   # Industry-specific generation
│   └── synthetic_data.py  # Gen-AI data pipeline
└── requirements.txt       # Project dependencies
```
