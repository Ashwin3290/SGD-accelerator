import streamlit as st
import pandas as pd
from gen_ai.synthetic_data import DataGenerationPipeline
from gen_ai.industry_data import generate_synthetic_dataset
import json, re
import subprocess
import sys , ast


def render():
    # Initialize session state variables
    if 'generation_result' not in st.session_state:
        st.session_state.generation_result = None
    if 'show_generated_code' not in st.session_state:
        st.session_state.show_generated_code = False
    if 'synthetic_data' not in st.session_state:
        st.session_state.synthetic_data = None
    if 'comparison_data' not in st.session_state:
        st.session_state.comparison_data = None

    def toggle_show_code():
        st.session_state.show_generated_code = True

    # Radio button for selection
    with st.sidebar:
        generation_type = st.radio(
            "Select Generation Type",
            ["Industry Specific Synthetic Data Generation", "Synthetic Data Generation"]
        )
    st.write("#### Generative AI transforms raw data into intelligent, privacy-preserving synthetic datasets by leveraging advanced neural networks to capture and recreate complex real-world data patterns with unprecedented accuracy.")

    if generation_type == "Industry Specific Synthetic Data Generation":
        st.session_state.industry_name = st.text_input("Enter Industry Name", "Aerospace")
        
        if st.button("Generate Industry Data"):
            with st.spinner("Generating Industry Data..."):
                
                st.session_state.synthetic_data = generate_synthetic_dataset(st.session_state.industry_name)
                if st.session_state.synthetic_data == 0:
                    if st.session_state.industry_name.lower() =="aerospace":
                        st.session_state.synthetic_data = """
import pandas as pd
import numpy as np

np.random.seed(42)  # For reproducibility
df = pd.DataFrame({
    'aircraft_id': np.random.randint(1000, 9999, size=200),
    'flight_number': [f'{np.random.choice(["AA", "UA", "DL"])}{np.random.randint(1000, 9999)}' for _ in range(200)],
    'departure_airport': np.random.choice(['JFK', 'LAX', 'ORD', 'ATL', 'DFW', 'DEN', 'SFO', 'SEA', 'MIA', 'CLT'], size=200),
    'arrival_airport': np.random.choice(['JFK', 'LAX', 'ORD', 'ATL', 'DFW', 'DEN', 'SFO', 'SEA', 'MIA', 'CLT'], size=200),
    'scheduled_departure': pd.to_datetime(np.random.randint(pd.Timestamp('2023-01-01').timestamp(), pd.Timestamp('2023-12-31').timestamp(), size=200), unit='s').round('min'),
    'actual_departure': pd.to_datetime(np.random.randint(pd.Timestamp('2023-01-01').timestamp(), pd.Timestamp('2023-12-31').timestamp(), size=200), unit='s').round('min'),
    'scheduled_arrival': pd.to_datetime(np.random.randint(pd.Timestamp('2023-01-01').timestamp(), pd.Timestamp('2023-12-31').timestamp(), size=200), unit='s').round('min'),
    'actual_arrival': pd.to_datetime(np.random.randint(pd.Timestamp('2023-01-01').timestamp(), pd.Timestamp('2023-12-31').timestamp(), size=200), unit='s').round('min'),
    'flight_duration': np.random.randint(60, 360, size=200),
    'altitude': np.random.randint(10000, 40000, size=200),
    'speed': np.random.uniform(400, 600, size=200),
    'heading': np.random.randint(0, 360, size=200),
    'fuel_consumption': np.random.uniform(1000, 5000, size=200),
    'passenger_count': np.random.randint(50, 250, size=200),
    'cargo_weight': np.random.uniform(10000, 50000, size=200),
    'weather_conditions': np.random.choice(['Clear', 'Cloudy', 'Rainy', 'Snowy', 'Foggy', 'Windy', 'Turbulence', 'Icing'], size=200),
    'maintenance_status': np.random.choice(['Operational', 'Scheduled Maintenance', 'Unscheduled Maintenance', 'Grounded'], size=200),
    'incident_reported': np.random.choice([True, False], size=200, p=[0.05, 0.95]),
    'sensor_data': [{'engine_temperature': {'unit': 'Celsius', 'value': np.random.uniform(900, 1100)},
                    'cabin_pressure': {'unit': 'Pascal', 'value': np.random.uniform(75000, 85000)},
                    'vibration_level': {'unit': 'G-force', 'value': np.random.uniform(0.5, 1.5)},
                    'fuel_level': {'unit': 'Gallons/Liters', 'value': np.random.uniform(4000, 6000)}}
                    for _ in range(200)]
})
print(df)
                        """
                    else:
                            st.session_state.synthetic_data = """
                            import pandas as pd
                            import numpy as np
                            """
                if st.session_state.synthetic_data:
                    st.write("Generated Industry Data:")
                    match = re.search(r"```(?:python)?\n(.*?)```", str(st.session_state.synthetic_data), re.DOTALL | re.IGNORECASE)
                    if match:
                        st.session_state.synthetic_data = match.group(1).strip()
                    
                    with open('run.py', 'w') as file:
                        st.session_state.synthetic_data = st.session_state.synthetic_data + "\ndf.to_csv('generated_data_industry.csv', index = False)"
                        file.write(st.session_state.synthetic_data)
            
        if st.session_state.synthetic_data:                  
            if st.button("Show Generated Data") :
                try:
                    result = subprocess.run([sys.executable, 'run.py'],
                                        capture_output=True,
                                        text=True)
                    
                    st.subheader("Execution Results:")
                    if result.stdout:
                        # st.text("Output:")
                        # st.code(result.stdout)
                        
                        try:
                            df = pd.read_csv("generated_data_industry.csv")
                            # print(df)
                            # st.write("Data as DataFrame:")
                            st.dataframe(df, width=10000, height=500)
                        except Exception as e:
                            st.error(e)
                            
                    if result.stderr:
                        st.error("Errors:")
                        st.code(result.stderr)
                        
                except Exception as e:
                    st.error(f"Error executing run.py: {str(e)}")

                                

    else:
        default_data = '''{
            "age": [25, 30, 35, 40, 45],
            "salary": [50000, 60000, 75000, 90000, 100000],
            "department": ["IT", "HR", "Sales", "IT", "Sales"],
            "join_date": ["2020-01-01", "2021-02-15", "2019-06-30", "2022-03-01", "2018-12-01"]
        }'''
        
        # st.session_state.data_input = st.text_area("Enter your DataFrame structure (JSON format)", default_data, height=200)
        file=st.file_uploader("Or upload a Json file", type=["json"])
        # print(file.read())
        
        if st.button("Generate Synthetic Data"):
            with st.spinner("Generating Synthetic Data..."):
                try:
                    input_dict = json.loads(file.read())
                    input_data = pd.DataFrame(input_dict)
                    pipeline = DataGenerationPipeline(input_data)
                    st.session_state.generation_result = pipeline.execute_pipeline()
                    
                    # Save comparison results
                    match = re.search(r"```(?:python)?\n(.*?)```", str(st.session_state.generation_result['generation_code'].raw), re.DOTALL | re.IGNORECASE)
                    if match:
                        st.session_state.generation_result["generation_code"] = match.group(1).strip()
                    with open('comparison.txt', 'w') as file:
                        file.write(st.session_state.generation_result['comparison'].raw)
                    with open('run.py', 'w') as file:
                        st.session_state.generation_result["generation_code"] = st.session_state.generation_result["generation_code"].raw + "\ngenerated_data.to_csv('generated_data.csv', index = False)"
                        file.write(f"{st.session_state.generation_result['generation_code']}")
                    
                    st.session_state.comparison_data = st.session_state.generation_result['comparison'].raw
                except Exception as e:
                    st.error(f"Error generating synthetic data: {str(e)}")

        if st.session_state.generation_result:
            
            if st.button("Show Generated Data", on_click=toggle_show_code):
                pass

            if st.session_state.show_generated_code:
                try:
                    result = subprocess.run([sys.executable, 'run.py'],
                                        capture_output=True,
                                        text=True)
                    
                    st.subheader("Execution Results:")
                    if result.stdout:
                        st.text("Output:")
                        # st.code(result.stdout)
                        
                        try:
                            df = pd.read_csv("generated_data.csv")
                            # print(df)
                            st.write("Data as DataFrame:")
                            st.dataframe(df, width=10000, height=500)
                        except Exception as e:
                            st.error(e)
                            
                    if result.stderr:
                        st.error("Errors:")
                        st.code(result.stderr)
                        
                except Exception as e:
                    st.error(f"Error executing run.py: {str(e)}")
            
            st.subheader("Comparison Results:")
            st.download_button(
                label="Download Comparison Results",
                data=st.session_state.comparison_data,
                file_name="comparison.txt",
                mime="text/plain"
            )
            