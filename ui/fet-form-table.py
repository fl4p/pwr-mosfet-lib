import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ['PYTHONPATH'] = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
import pandas as pd
import pickle
from dslib.digikey.partsSearch import search_digikey_parts
from dslib.parts_discovery import digikey
from dslib.spec_models import DcDcSpecs, MosfetSpecs
from dslib.powerloss import dcdc_buck_hs, dcdc_buck_ls
from dslib.store import load_parts as _load_parts, Part

# Set page config to dark mode
st.set_page_config(page_title="MOSFET Component Selector", layout="wide", initial_sidebar_state="expanded")


def convert_to_dcdc_specs(vi, vo, io, f, vgs, ripple_factor, tDead):
    """
    Convert input parameters to create a DcDcSpecs object.

    :param vi: Input voltage (V)
    :param vo: Output voltage (V)
    :param io: Output current (A)
    :param f: Switching frequency (kHz)
    :param vgs: Gate drive voltage (V)
    :param ripple_factor: Ripple factor
    :param tDead: Dead time (ns)
    :return: DcDcSpecs object
    """
    return DcDcSpecs(vi=vi, vo=vo, io=io, f=f * 1000, Vgs=vgs, ripple_factor=ripple_factor, tDead=tDead * 1e-9)


@st.cache_resource
def load_parts():
    parts = _load_parts()
    return parts


@st.cache_data
def fetch_digikey_parts(search_params):
    """
    Fetch MOSFET parts from DigiKey API based on search parameters.

    :param search_params: Dictionary containing search parameters
    :return: DataFrame of DigiKey part results
    """
    return search_digikey_parts(search_params)


@st.cache_data
def process_csv_data(csv_file):
    """
    Process uploaded CSV file containing MOSFET data.

    :param csv_file: Uploaded CSV file
    :return: Processed DataFrame
    """
    df = pd.read_csv(csv_file)
    # Add any necessary processing steps here
    return df


def combine_mosfet_data(api_data, csv_data):
    """
    Combine MOSFET data from DigiKey API and uploaded CSV.

    :param api_data: List of DigiKey part results
    :param csv_data: DataFrame of CSV data
    :return: Combined DataFrame of MOSFET data
    """
    # Convert api_data to DataFrame if it's not already
    if not isinstance(api_data, pd.DataFrame):
        api_df = pd.DataFrame(api_data)
    else:
        api_df = api_data

    # Combine the DataFrames
    combined_df = pd.concat([api_df, csv_data], ignore_index=True)

    # Remove duplicates if any
    combined_df.drop_duplicates(subset=['Mfr Part #'], keep='first', inplace=True)

    return combined_df


@st.cache_data
def analyze_mosfets(_dcdc_specs, mosfet_data=None):
    """
    Perform MOSFET analysis based on DC-DC converter specifications and MOSFET data.

    :param _dcdc_specs: DcDcSpecs object containing converter specifications
    :param mosfet_data: DataFrame containing MOSFET data (optional)
    :return: DataFrame with analysis results
    """
    if mosfet_data is None:
        parts = load_parts()
        st.write(f"Loaded {len(parts)} parts from existing database")
    else:
        parts = [digikey([row]) for _, row in mosfet_data.iterrows()]
        st.write(f"Processed {len(parts)} parts from uploaded data")

    results = []
    error_logs = []
    processed_count = 0
    error_count = 0

    for i, part in enumerate(parts):
        try:
            if isinstance(part, list) and len(part) > 0:
                part = part[0]  # Take the first item if it's a list

            if isinstance(part, Part):
                mpn, mfr, specs = part.mpn, part.mfr, part.specs
            elif isinstance(part, tuple):
                if len(part) == 2:
                    mfr, mpn = part
                    specs = MosfetSpecs.from_mpn(mpn, mfr)
                else:
                    raise ValueError(f"Unexpected tuple length: {part}")
            else:
                raise ValueError(f"Unexpected part structure: {type(part)}")

            if specs is None:
                raise ValueError(f"None specs for part {mpn}")

            # Perform MOSFET analysis
            hs_loss = dcdc_buck_hs(_dcdc_specs, specs, rg_total=6)
            ls_loss = dcdc_buck_ls(_dcdc_specs, specs)
            results.append({
                "Part Number": mpn,
                "Manufacturer": mfr,
                "VDS (V)": specs.Vds,
                "RDS(on) (mΩ)": specs.Rds_on * 1e3,  # specs.Rds_max,
                # "ID_25 (A)": specs.ID_25,
                "Qg (nC)": specs.Qg * 1e9,  # specs.Qg_max,
                "Qrr (nC)": specs.Qrr * 1e9,  # specs.Qrr_max,
                "tRise (ns)": round(specs.tRise * 1e9, 1),
                "tFall (ns)": round(specs.tFall * 1e9, 1),
                "FOM": specs.Rds_on * 1000 * (specs.Qg * 1e9),
                "FOMrr": specs.Rds_on * 1000 * (specs.Qrr * 1e9),
                "P_on (W)": hs_loss.P_on,
                "P_sw (W)": hs_loss.P_sw,
                "P_rr (W)": ls_loss.P_rr,
                "Total Loss (W)": hs_loss.buck_hs() + ls_loss.buck_ls(),

            })
            processed_count += 1
        except Exception as e:
            error_logs.append(f"Error processing part {i} ({mpn if 'mpn' in locals() else 'Unknown'}): {str(e)}")
            error_count += 1

    df = pd.DataFrame(results)

    # Display summary and error logs in an expander
    st.write(f"Successfully analyzed {processed_count} parts. Encountered {error_count} errors.")
    if error_count > 0:
        with st.expander("View Error Logs"):
            for log in error_logs:
                st.write(log)

    return df


# Function to save user inputs
def save_inputs(inputs):
    with open('user_inputs.pkl', 'wb') as f:
        pickle.dump(inputs, f)


# Function to load user inputs
def load_inputs():
    if os.path.exists('user_inputs.pkl'):
        with open('user_inputs.pkl', 'rb') as f:
            return pickle.load(f)
    return {}


# Load previous inputs
previous_inputs = load_inputs()

st.title('MOSFET Component Selector for a DC-DC Converter')

# Sidebar for user input
st.sidebar.header('Input Parameters')
st.sidebar.write('Please enter the DC-DC operating point parameters below:')

vi = st.sidebar.number_input('Input Voltage (V)', min_value=0.0, step=0.1, value=previous_inputs.get('vi', 12.0),
                             help="DC-DC converter input voltage")
vo = st.sidebar.number_input('Output Voltage (V)', min_value=0.0, step=0.1, value=previous_inputs.get('vo', 5.0),
                             help="DC-DC converter output voltage")
io = st.sidebar.number_input('Output current (A)', min_value=0.0, step=0.1, value=previous_inputs.get('io', 10.0),
                             help="Output current of the DC-DC converter")
f = st.sidebar.number_input('Switching Frequency (kHz)', min_value=1.0, max_value=1000.0, step=1.0,
                            value=previous_inputs.get('f', 100.0), help="Switching frequency of the DC-DC converter")
vgs = st.sidebar.number_input('Gate Drive Voltage (V)', min_value=0.0, step=0.1, value=previous_inputs.get('vgs', 10.0),
                              help="Gate drive voltage for both (HS) high-side and (LS) low-side MOSFETs")
ripple_factor = st.sidebar.number_input('Ripple Factor', min_value=0.0, max_value=1.0, step=0.01,
                                        value=previous_inputs.get('ripple_factor', 0.2),
                                        help="Peak-to-peak coil current divided by mean coil current (assuming Continuous Conduction Mode)")
tDead = st.sidebar.number_input('Dead Time (ns)', min_value=0.0, max_value=1000.0, step=1.0,
                                value=previous_inputs.get('tDead', 100.0),
                                help="Gate driver dead-time (occurs twice per switching period)")

# Save inputs button
if st.sidebar.button('Save Inputs'):
    inputs = {'vi': vi, 'vo': vo, 'io': io, 'f': f, 'vgs': vgs, 'ripple_factor': ripple_factor, 'tDead': tDead}
    save_inputs(inputs)
    st.sidebar.success('Inputs saved successfully!')

# Clear inputs button
if st.sidebar.button('Clear Saved Inputs'):
    if os.path.exists('user_inputs.pkl'):
        os.remove('user_inputs.pkl')
        st.sidebar.success('Saved inputs cleared!')
    else:
        st.sidebar.info('No saved inputs to clear.')


# # Add file uploader for CSV
# uploaded_file = st.sidebar.file_uploader("Upload CSV file with MOSFET data", type="csv")

# Function to display analysis results
def display_analysis_results(df):
    # Sort the dataframe by Total Loss
    df = df.sort_values('Total Loss (W)')

    # Ensure numeric columns are of the correct type
    numeric_columns = ['VDS (V)', 'RDS(on) (mΩ)', 'Qg (nC)', 'Qrr (nC)', 'tRise (ns)', 'tFall (ns)', 'FOM', 'FOMrr',
                       'P_on (W)', 'P_sw (W)', 'P_rr (W)', 'Total Loss (W)']  # 'ID_25 (A)',

    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')  # Convert to numeric, coerce errors to NaN

    # Format numeric columns for display
    formatted_df = df.copy()
    formatted_df['VDS (V)'] = df['VDS (V)'].map(lambda x: f"{x:.2f}" if pd.notnull(x) else "")
    formatted_df['RDS(on) (mΩ)'] = df['RDS(on) (mΩ)'].map(lambda x: f"{x:.2f}" if pd.notnull(x) else "")
    # formatted_df['ID_25 (A)'] = df['ID_25 (A)'].map(lambda x: f"{x:.2f}" if pd.notnull(x) else "")
    formatted_df['Qg (nC)'] = df['Qg (nC)'].map(lambda x: f"{x:.0f}" if pd.notnull(x) else "")
    formatted_df['Qrr (nC)'] = df['Qrr (nC)'].map(lambda x: f"{x:.1f}" if pd.notnull(x) else "")
    formatted_df['tRise (ns)'] = df['tRise (ns)'].map(lambda x: f"{x:.2f}" if pd.notnull(x) else "")
    formatted_df['tFall (ns)'] = df['tFall (ns)'].map(lambda x: f"{x:.2f}" if pd.notnull(x) else "")
    formatted_df['FOM'] = df['FOM'].map(lambda x: f"{x:.1f}" if pd.notnull(x) else "")
    formatted_df['FOMrr'] = df['FOMrr'].map(lambda x: f"{x:.0f}" if pd.notnull(x) else "")
    formatted_df['P_on (W)'] = df['P_on (W)'].map(lambda x: f"{x:.2f}" if pd.notnull(x) else "")
    formatted_df['P_sw (W)'] = df['P_sw (W)'].map(lambda x: f"{x:.2f}" if pd.notnull(x) else "")
    formatted_df['P_rr (W)'] = df['P_rr (W)'].map(lambda x: f"{x:.2f}" if pd.notnull(x) else "")
    formatted_df['Total Loss (W)'] = df['Total Loss (W)'].map(lambda x: f"{x:.2f}" if pd.notnull(x) else "")

    # Function to color code cells
    def color_cells(val, column):
        if column in ['FOM', 'FOMrr', 'P_on (W)', 'P_sw (W)', 'P_rr (W)', 'Total Loss (W)']:
            if pd.notnull(val) and val != "":
                val = float(val)  # Convert string to float for comparison
                if val <= df[column].quantile(0.25):
                    return 'background-color: #92D050; color: black;'
                elif val <= df[column].quantile(0.75):
                    return 'background-color: #FFFF00; color: black;'
                else:
                    return 'background-color: #FF0000; color: black;'
        return ''

    # Apply color coding
    styled_df = formatted_df.style.apply(lambda x: [color_cells(x[col], col) for col in formatted_df.columns], axis=1)

    # Display the table with full width
    st.subheader('MOSFET Analysis Results')
    st.dataframe(styled_df, use_container_width=True)

    # Add download button for CSV
    csv = df.to_csv(index=False)
    st.download_button(
        label="Download results as CSV",
        data=csv,
        file_name="mosfet_analysis_results.csv",
        mime="text/csv",
    )


# Create two columns for the buttons
col2, col1 = st.columns(2)

# Find Components by specs button
# if col1.button('Find Components by specs'):
#     with st.spinner('Fetching and Analyzing MOSFETs...'):
#         try:
#             # Fetch DigiKey parts
#             search_params = {
#                 "keywords": "mosfet",
#                 "voltage_min": vi,
#                 "voltage_max": vi * 1.5,  # Adjust as needed
#                 "current_min": io,
#                 "current_max": io * 1.5  # Adjust as needed
#             }
#             digikey_parts = fetch_digikey_parts(search_params)

#             # Process uploaded CSV if available
#             csv_data = pd.DataFrame()
#             if uploaded_file is not None:
#                 csv_data = process_csv_data(uploaded_file)

#             # Combine data
#             combined_data = combine_mosfet_data(digikey_parts, csv_data)

#             # Perform analysis
#             _dcdc_specs = convert_to_dcdc_specs(vi, vo, io, f, vgs, ripple_factor, tDead)
#             df = analyze_mosfets(_dcdc_specs, combined_data)

#             # Display results
#             display_analysis_results(df)
#         except Exception as e:
#             st.error(f"An error occurred during analysis: {str(e)}")

# Load existing components list button
if st.sidebar.button('Load existing components list', type='primary'):
    with st.spinner('Analyzing existing components...'):
        try:
            # Perform analysis on existing components
            _dcdc_specs = convert_to_dcdc_specs(vi, vo, io, f, vgs, ripple_factor, tDead)
            df = analyze_mosfets(_dcdc_specs)

            # Display results
            display_analysis_results(df)
        except Exception as e:
            st.error(f"An error occurred during analysis: {str(e)}")

if 'df' not in locals() or df.empty:
    st.write("""
    Finding the right switches for your DC-DC converter can be more complex than it initially appears. 
    The two switches in a converter operate under different conditions, and factors like reverse recovery loss 
    are often overlooked.
    """)
    st.write("""
    This tool aims to assist you in making an informed selection by considering these 
    crucial aspects and providing a comprehensive comparison of MOSFET options.
    """)

    # Add a brief tutorial or guide for first-time users
    with st.expander("How to use this tool"):
        st.write("""
        Welcome to the MOSFET Component Selector for DC-DC Converters! Here's a quick guide to get you started:
        This tool considers various crucial aspects of MOSFET selection for DC-DC converters, including reverse recovery loss, to help you make an informed decision.
        It is an estimation and you should always double check the datasheet of manufactured components before making final decision.

        1. Enter Parameters: Use the sidebar on the left to input your DC-DC converter parameters.
           - Input Voltage (V): The input voltage of your DC-DC converter.
           - Output Voltage (V): The desired output voltage.
           - Output Current (A): The output current of your converter.
           - Switching Frequency (kHz): The switching frequency of your converter.
           - Gate Drive Voltage (V): The gate drive voltage for both high-side and low-side MOSFETs.
           - Ripple Factor: The peak-to-peak coil current divided by mean coil current (assuming Continuous Conduction Mode).
           - Dead Time (ns): The gate driver dead-time (occurs twice per switching period).

        2. Find Components: 
           - Click the 'Find Components by specs' button to search for and analyze MOSFETs based on your inputs and DigiKey data.
           - Click the 'Load existing components list' button to analyze MOSFETs from the existing database.

        3. View Results: The results table will show various MOSFET options with their specifications and estimated power losses.
           - The table is sorted by Total Loss (W) in ascending order.
           - Color coding helps identify better performing MOSFETs (green is better, red is worse).

        4. Download Results: Use the 'Download results as CSV' button to save the analysis for further review.

        5. Save Inputs: You can save your inputs for future sessions using the 'Save Inputs' button in the sidebar.

        6. Clear Inputs: To start fresh, use the 'Clear Saved Inputs' button in the sidebar.
        """)
        # 2. Upload CSV (Optional): You can upload a CSV file with additional MOSFET data using the file uploader in the sidebar.

st.markdown("""
<style>
    [data-testid="stMetricLabel"] {
        overflow: visible;
    }
    [data-testid="stMetricLabel"]::after {
        content: attr(title);
        visibility: hidden;
        position: absolute;
        padding: 5px;
        top: 100%;
        left: 50%;
        transform: translateX(-50%);
        background-color: rgba(0,0,0,0.8);
        color: white;
        border-radius: 5px;
        white-space: nowrap;
        z-index: 1;
    }
    [data-testid="stMetricLabel"]:hover::after {
        visibility: visible;
    }

    button[kind="primary"] {
        background-color: green;
    }

    button[kind="seondary"] {
        background-color: purple;
    }
</style>
""", unsafe_allow_html=True)
