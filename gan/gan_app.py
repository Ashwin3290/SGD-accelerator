import streamlit as st
import pandas as pd
from gan.synthetic import SynthesizerManager
from typing import Dict, Any
import io
import zipfile
import json
import pymysql
from sqlalchemy import create_engine

def render():
    if 'data_uploaded' not in st.session_state:
        st.session_state.data_uploaded = False
    if 'uploaded_files' not in st.session_state:
        st.session_state.uploaded_files = []
    if 'results' not in st.session_state:
        st.session_state.results = None

    # Initialize manager
    manager = SynthesizerManager()

    # Sidebar configuration
    st.markdown("""
        <style>
        /* Slider Styling */
        .stSlider {
            padding: 20px 0;
        }
        .stSlider > label {
            color: #7dd3fc;
            font-weight: 500;
            margin-bottom: 10px;
        }
        .stSlider [data-baseweb="slider"] {
            margin-top: 10px;
        }
        .stSlider [data-baseweb="slider"] div {
            background-color: #334155;
        }
        .stSlider [data-baseweb="slider"] div[role="slider"] {
            background-color: #7dd3fc;
            border-color: #7dd3fc;
        }
        .stSlider [data-baseweb="slider"] div[role="slider"]:hover {
            background-color: #38bdf8;
            border-color: #38bdf8;
        }
        .stSlider [data-baseweb="slider"] div[role="slider"]:active {
            background-color: #0ea5e9;
            border-color: #0ea5e9;
        }
        .stSlider [data-baseweb="slider"] div[data-testid="stTickBar"] {
            background-color: #1e293b;
        }
        .stSlider [data-baseweb="slider"] div[data-testid="stTickBarMax"] {
            background-color: #1e293b;
        }
        </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.header("Configuration")
        synthesizer_options = manager.registry.list_synthesizers()
        selected_synthesizer = st.selectbox("### Select Synthesizer", synthesizer_options[0])
        table_type = st.radio("### Table Type", ["Single", "Multi"], horizontal=True)
        num_samples = st.slider("### Number of Synthetic Samples", 
                                    min_value=10, max_value=10000, value=200)

    st.write("#### Harness GAN technology to transform SQL database insights into intelligent, synthetic test data generation, bridging real-world complexity with innovative machine learning techniques.")
    st.header("Data Upload and Synthetic Generation")

    def handle_file_upload(files_upload):
        if files_upload:
            uploaded_files = []
            if isinstance(files_upload, list):
                for file in files_upload:
                    try:
                        df = pd.read_csv(io.StringIO(file.getvalue().decode('utf-8')))
                        uploaded_files.append(df)
                    except Exception as e:
                        st.error(f"Error reading file {file.name}: {str(e)}")
                        return False
            else:
                try:
                    df = pd.read_csv(io.StringIO(files_upload.getvalue().decode('utf-8')))
                    uploaded_files.append(df)
                except Exception as e:
                    st.error(f"Error reading file {files_upload.name}: {str(e)}")
                    return False
            
            st.session_state.uploaded_files = uploaded_files
            st.session_state.data_uploaded = True
            return True
        return False

    def handle_sql_query(host, user, password, database, queries):
        try:
            connection_string = f"mysql+pymysql://{user}:{password}@{host}/{database}"
            engine = create_engine(connection_string)
            
            uploaded_files = []
            for i, query in enumerate(queries):
                if query.strip():
                    df = pd.read_sql(query, engine)
                    uploaded_files.append(df)
                    st.write(f"Query {i+1} Results Preview:")
                    st.dataframe(df.head())
            
            if uploaded_files:
                st.session_state.uploaded_files = uploaded_files
                st.session_state.data_uploaded = True
                return True
            return False
            
        except Exception as e:
            st.error("Error executing SQL queries:")
            st.code(str(e), language="bash")
            st.exception(e)
            return False

    with st.expander("Data Input Methods", expanded=True):
        # col_upload, col_sql = st.columns(2)
        
        # with col_upload:
        #     st.subheader("File Upload")
        #     files_upload = st.file_uploader("Choose CSV files", 
        #                                 accept_multiple_files=(table_type=="Multi"),
        #                                 type='csv')
        #     if files_upload:
        #         handle_file_upload(files_upload)
        
        # with col_sql:
        st.subheader("SQL Query")
        with open("gan\database_config.json","r") as f:
            config=json.load(f)
        host = config['host']
        user = config["username"]
        password = config["password"]
        database = config["database"]
        
        query_count = st.number_input("Number of Queries", 
                                    min_value=1, 
                                    max_value=10 if table_type=="Multi" else 1, 
                                    value=1)
        queries = []
        for i in range(query_count):
            query = st.text_area(f"SQL Query {i+1}", height=100, key=f"query_{i}")
            queries.append(query)
        
        if st.button("Execute Queries"):
            
            handle_sql_query(host, user, password, database, queries)

    if st.session_state.data_uploaded and st.session_state.uploaded_files:
        try:
            if table_type == "Single":
                data = st.session_state.uploaded_files[0] if isinstance(st.session_state.uploaded_files, list) else st.session_state.uploaded_files
                st.write("### Uploaded Data Preview")
                st.dataframe(data.head())
                
                if st.button("Generate Synthetic Data"):
                    with st.spinner("Generating synthetic data..."):
                        st.session_state.results = manager.handle_single_table(data, selected_synthesizer, num_samples)

                if st.session_state.results:
                    st.write("### Synthetic Data Preview")
                    st.dataframe(st.session_state.results['synthetic_data'].head())

                    st.write("## Data Reports")
                    
                    st.write("### Diagnostic Report")
                    if 'diagnostic_report' in st.session_state.results['reports']:
                        diagnostic = st.session_state.results['reports']['diagnostic_report']
                        properties= diagnostic.get_properties().to_dict()
                        st.write("#### Data Validity")
                        validity_details = diagnostic.get_details(property_name='Data Validity')
                        st.dataframe(validity_details)
                        st.write(f"#### Overall score: {properties['Score'][0]}")
                        
                        st.write("#### Data Structure")
                        structure_details = diagnostic.get_details(property_name='Data Structure')
                        st.dataframe(structure_details)
                        st.write(f"#### Overall score: {properties['Score'][1]}")

                    st.write("### Quality Report")
                    if 'quality_report' in st.session_state.results['reports']:
                        report = st.session_state.results['reports']['quality_report']
                        
                        st.write("#### Column Shapes")
                        st.write(report.get_details(property_name='Column Shapes'))
                        
                        st.write("#### Column Pair Trends")
                        st.write(report.get_details(property_name='Column Pair Trends'))
                        
                    st.write("### Column Distribution Plots")
                    if 'column_plots' in st.session_state.results['reports']:
                        column_options = list(st.session_state.results['reports']['column_plots'].keys())
                        selected_column = st.selectbox("Select Column", column_options,index=1)
                        fig=st.session_state.results['reports']['column_plots'][selected_column]
                        fig.update_layout(
                                template='plotly_dark',  
                                paper_bgcolor='rgba(0,0,0,0)',
                                plot_bgcolor='rgba(0,0,0,0)'
                            )
                        st.plotly_chart(fig)
                        
                    st.write("### Column Pair Plots")
                    if 'pair_plots' in st.session_state.results['reports']:
                        pair_options = list(st.session_state.results['reports']['pair_plots'].keys())
                        selected_pair = st.selectbox("Select Column Pair", pair_options,index=2)
                        fig=st.session_state.results['reports']['pair_plots'][selected_pair]
                        fig.update_layout(
                                template='plotly_dark',  
                                paper_bgcolor='rgba(0,0,0,0)',
                                plot_bgcolor='rgba(0,0,0,0)'
                            )
                        st.plotly_chart(fig)
                
                    st.download_button(
                        label="Download Synthetic Data",
                        data=st.session_state.results['synthetic_data'].to_csv(index=False),
                        file_name="synthetic_data.csv",
                        mime="text/csv"
                    )
                    
            else:  # Multi-table case
                tables = {}
                for i, df in enumerate(st.session_state.uploaded_files):
                    table_name = f"table_{i+1}" if isinstance(df, pd.DataFrame) else df.name.replace('.csv', '')
                    tables[table_name] = df
                
                st.write("### Uploaded Tables")
                for name, table in tables.items():
                    st.write(f"**{name}**")
                    st.dataframe(table.head())
                
                if st.button("Generate Synthetic Data"):
                    with st.spinner("Generating synthetic data..."):
                        st.session_state.results = manager.handle_multi_table(tables, selected_synthesizer, num_samples)

                if st.session_state.results:
                    st.write("### Synthetic Tables")
                    for table in st.session_state.results["synthetic_data"].keys():
                        st.write(f"**{table}**")
                        st.dataframe(st.session_state.results['synthetic_data'][table].head())
                    
                    st.write("## Data Reports")
                    table_names = list(st.session_state.results['synthetic_data'].keys())
                    selected_table = st.selectbox("Select Table", table_names)

                    st.write("### Diagnostic Report")
                    if 'diagnostic_report' in st.session_state.results['reports']:
                        table_diagnostic = st.session_state.results['reports']['diagnostic_report']['tables'][selected_table]

                        st.write(f"#### Data Validity for {selected_table}")
                        st.dataframe(table_diagnostic['validity_details'])
                        st.write(f"#### Overall score: {table_diagnostic['validity_score']}")
                        
                        st.write(f"#### Data Structure for {selected_table}")
                        st.dataframe(table_diagnostic['structure_details'])
                        st.write(f"#### Overall score: {table_diagnostic['structure_score']}")


                    st.write("### Quality Report")
                    if 'quality_report' in st.session_state.results['reports']:
                        table_report = st.session_state.results['reports']['quality_report']['tables'][selected_table]['quality_metrics']
                        st.write(f"#### Quality Metrics for {selected_table}")
                        st.write("#### Column Shapes")
                        st.write(table_report.get_details(property_name='Column Shapes'))
                        
                        st.write("#### Column Pair Trends")
                        st.write(table_report.get_details(property_name='Column Pair Trends'))
                        
                    st.write("### Column Distribution Plots")
                    if 'quality_report' in st.session_state.results['reports']:
                        table_report = st.session_state.results['reports']['quality_report']['tables'][selected_table]
                        column_options = list(table_report['column_plots'].keys())
                        selected_column = st.selectbox("Select Column", column_options,index=1)
                        fig=table_report['column_plots'][selected_column]
                        fig.update_layout(
                                template='plotly_dark',  
                                paper_bgcolor='rgba(0,0,0,0)',
                                plot_bgcolor='rgba(0,0,0,0)'
                            )

                        st.plotly_chart(fig)
                        

                    st.write("### Column Pair Plots")
                    if 'quality_report' in st.session_state.results['reports']:
                        table_report = st.session_state.results['reports']['quality_report']['tables'][selected_table]
                        pair_options = list(table_report['pair_plots'].keys())
                        selected_pair = st.selectbox("Select Column Pair", pair_options,index=2)
                        fig=table_report['pair_plots'][selected_pair]
                        fig.update_layout(
                            template='plotly_dark',  
                            paper_bgcolor='rgba(0,0,0,0)',
                            plot_bgcolor='rgba(0,0,0,0)'
                        )
                        
                        st.plotly_chart(fig)
                        
                        # Create zip file for download
                        zip_buffer = io.BytesIO()
                        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                            for table_name, synthetic_table in st.session_state.results['synthetic_data'].items():
                                csv_buffer = io.StringIO()
                                synthetic_table.to_csv(csv_buffer, index=False)
                                zip_file.writestr(f"synthetic_{table_name}.csv", csv_buffer.getvalue())
                        
                        st.download_button(
                            label="Download All Synthetic Tables",
                            data=zip_buffer.getvalue(),
                            file_name="synthetic_tables.zip",
                            mime="application/zip"
                        )

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            st.write("Please check your input data and try again.")

    if st.session_state.data_uploaded:
        if st.button("Clear All Data"):
            st.session_state.data_uploaded = False
            st.session_state.uploaded_files = []
            st.session_state.results = None
            st.rerun()