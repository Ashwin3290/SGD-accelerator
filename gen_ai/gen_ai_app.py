import streamlit as st
import pandas as pd
from synthetic_data import DataGenerationPipeline
from industry_data import generate_synthetic_dataset
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

    with st.sidebar:
        generation_type = st.radio(
            "Select Generation Type",
            ["Industry Specific Synthetic Data Generation", "Synthetic Data Generation"]
        )

    if generation_type == "Industry Specific Synthetic Data Generation":
        st.session_state.industry_name = st.text_input("Enter Industry Name", "Aerospace")
        
        if st.button("Generate Industry Data"):
            with st.spinner("Generating Industry Data..."):
                st.session_state.synthetic_data = generate_synthetic_dataset(st.session_state.industry_name)
                if st.session_state.synthetic_data:
                    st.session_state.synthetic_data=st.session_state.synthetic_data.raw
                    st.write("Generated Industry Data:")
                    match = re.search(r"```(?:python)?\n(.*?)```", str(st.session_state.synthetic_data), re.DOTALL | re.IGNORECASE)
                    if match:
                        st.session_state.synthetic_data = match.group(1).strip()
                    with open('run.py', 'w') as file:
                            file.write(st.session_state.synthetic_data)
            
        if st.session_state.synthetic_data:                  
            if st.button("Show Generated Data") :
                try:
                    print("Running run.py")
                    result = subprocess.run([sys.executable, 'run.py'],
                                        capture_output=True,
                                        text=True)
                    
                    st.subheader("Execution Results:")
                    if result.stdout:
                        st.text("Output:")
                        st.code(result.stdout)
                        
                        try:
                            data = ast.literal_eval(result.stdout)
                            if isinstance(data, (list, dict)):
                                df = pd.DataFrame(data)
                                st.write("Data as DataFrame:")
                                st.dataframe(df)
                        except:
                            pass
                            
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
        
        st.session_state.data_input = st.text_area("Enter your DataFrame structure (JSON format)", default_data, height=200)
        
        if st.button("Generate Synthetic Data"):
            with st.spinner("Generating Synthetic Data..."):
                try:
                    input_dict = json.loads(st.session_state.data_input)
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
                        st.code(result.stdout)
                        
                        try:
                            data = ast.literal_eval(result.stdout)
                            if isinstance(data, (list, dict)):
                                df = pd.DataFrame(data)
                                st.write("Data as DataFrame:")
                                st.dataframe(df)
                        except:
                            pass
                            
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
            