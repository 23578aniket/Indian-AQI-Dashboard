# main.py
import streamlit as st
import pandas as pd
import requests
import time
from datetime import datetime
import os

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Live India AQI Dashboard",
    page_icon="💨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- API & DATA CONFIGURATION ---
# IMPORTANT: You need to get your own free API token from https://aqicn.org/data-platform/token/
# After getting the token, it is recommended to set it as an environment variable.
# For local testing, you can uncomment the line below and paste your token.
os.environ['AQI_API_TOKEN'] = 'b8a98b4df9ea8410319e6beaeab5a8729da1efd9'

API_TOKEN = os.environ.get('AQI_API_TOKEN')

# List of major Indian cities with their geographic coordinates for mapping
CITIES = {
    "Delhi": "delhi",
    "Mumbai": "mumbai",
    "Kolkata": "kolkata",
    "Chennai": "chennai",
    "Bengaluru": "bangalore",
    "Hyderabad": "hyderabad",
    "Pune": "pune",
    "Ahmedabad": "ahmedabad",
    "Jaipur": "jaipur",
    "Lucknow": "lucknow",
    "Bhopal": "bhopal",
    "Patna": "patna"
}


# --- HELPER FUNCTIONS ---

def get_aqi_data(city_name):
    """Fetches AQI data for a given city from the AQICN API."""
    if not API_TOKEN:
        return None, "API Token not configured. Please set the AQI_API_TOKEN environment variable."

    url = f"https://api.waqi.info/feed/{city_name}/?token={API_TOKEN}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        data = response.json()
        if data.get("status") == "ok":
            return data["data"], None
        else:
            return None, data.get("data", "Unknown error from API.")
    except requests.exceptions.RequestException as e:
        return None, f"Network error: {e}"
    except Exception as e:
        return None, f"An unexpected error occurred: {e}"


def get_aqi_category(aqi):
    """Categorizes AQI value into a health level and assigns a color."""
    if aqi is None or not isinstance(aqi, (int, float)):
        return "Unknown", "#808080"  # Grey for unknown
    if 0 <= aqi <= 50:
        return "Good", "#009966"
    if 51 <= aqi <= 100:
        return "Moderate", "#FFDE33"
    if 101 <= aqi <= 150:
        return "Unhealthy for Sensitive Groups", "#FF9933"
    if 151 <= aqi <= 200:
        return "Unhealthy", "#CC0033"
    if 201 <= aqi <= 300:
        return "Very Unhealthy", "#660099"
    if aqi > 300:
        return "Hazardous", "#7E0023"
    return "Unknown", "#808080"


@st.cache_data(ttl=600)  # Cache data for 10 minutes to avoid hitting API rate limits
def fetch_all_cities_data():
    """Fetches AQI data for all cities defined in the CITIES constant."""
    all_data = []
    errors = []

    city_list = list(CITIES.keys())
    progress_bar = st.progress(0, text="Fetching data for all cities...")

    for i, (city_display_name, city_api_name) in enumerate(CITIES.items()):
        aqi_data, error = get_aqi_data(city_api_name)
        if error:
            errors.append(f"Could not fetch data for {city_display_name}: {error}")
        elif aqi_data:
            data_point = {
                "City": city_display_name,
                "AQI": aqi_data.get("aqi", None),
                "Latitude": aqi_data.get("city", {}).get("geo", [None, None])[0],
                "Longitude": aqi_data.get("city", {}).get("geo", [None, None])[1],
                "Timestamp": aqi_data.get("time", {}).get("s", "N/A")
            }
            all_data.append(data_point)

        # Update progress bar
        progress_bar.progress((i + 1) / len(city_list), text=f"Fetching data for {city_display_name}...")
        time.sleep(0.5)  # Small delay to be gentle on the API

    progress_bar.empty()  # Remove progress bar after completion

    if not all_data and not API_TOKEN:
        st.error(
            "FATAL: AQI_API_TOKEN is not set. The application cannot fetch data. Please get a token from [aqicn.org](https://aqicn.org/data-platform/token/) and set it as an environment variable or in the script.",
            icon="🚨")
        return pd.DataFrame(), []

    return pd.DataFrame(all_data), errors


# --- UI LAYOUT ---

# --- Header ---
st.title("💨 Live Air Quality Index (AQI) Dashboard for Major Indian Cities")
st.markdown(f"""
This dashboard provides real-time Air Quality Index (AQI) data from various monitoring stations across India. 
Data is automatically refreshed every 10 minutes. Last updated: **{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} IST**
""")

# --- Main Data Fetching and Display ---
df, fetch_errors = fetch_all_cities_data()

if fetch_errors:
    for error in fetch_errors:
        st.warning(error, icon="⚠️")

if df.empty:
    st.info("No data available to display. This could be due to API issues or a missing API token.")
else:
    # --- Data Processing for Display ---
    df.dropna(subset=['AQI', 'Latitude', 'Longitude'], inplace=True)
    df['AQI'] = pd.to_numeric(df['AQI'], errors='coerce')
    df['Category'], df['Color'] = zip(*df['AQI'].apply(get_aqi_category))

    # --- MAIN VISUALIZATIONS ---
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("📍 AQI Map of India")
        st.map(df,
               latitude='Latitude',
               longitude='Longitude',
               color='Color',
               size='AQI'
               )
        st.caption(
            "Map markers are colored based on AQI level. The size of the marker also corresponds to the AQI value.")

    with col2:
        st.subheader("📊 City AQI Levels")
        # Displaying a styled dataframe
        st.dataframe(
            df[['City', 'AQI', 'Category']].sort_values('AQI', ascending=False).reset_index(drop=True),
            use_container_width=True,
            column_config={
                "AQI": st.column_config.ProgressColumn(
                    "AQI Value",
                    help="Air Quality Index: Lower is better.",
                    format="%d",
                ),
            },
            hide_index=True
        )

    # --- Detailed Data View ---
    with st.expander("Show Detailed Data Table"):
        st.dataframe(df)

# --- SIDEBAR ---
st.sidebar.header("About this Project")
st.sidebar.info(
    """
    This dashboard was built to demonstrate a complete, end-to-end data engineering pipeline:
    - **Data Acquisition:** Fetches real-time data from the public AQICN API.
    - **Data Processing:** Cleans and transforms the data using Pandas.
    - **Data Visualization:** Displays insights on an interactive map and tables using Streamlit.

    This is an example of an 'A-Grade' portfolio project for a Data Scientist/Engineer role.
    """
)

st.sidebar.header("AQI Health Levels")
st.sidebar.markdown("""
- **0-50 (Good):** 💚 Minimal impact.
- **51-100 (Moderate):** 💛 Minor breathing discomfort to sensitive people.
- **101-150 (Unhealthy for Sensitive Groups):** 🧡 Breathing discomfort to the sensitive population.
- **151-200 (Unhealthy):** ❤️ Breathing discomfort to most people.
- **201-300 (Very Unhealthy):** 💜 Respiratory illness on prolonged exposure.
- **>300 (Hazardous):** 🤎 Affects healthy people and seriously impacts those with existing diseases.
""")

st.sidebar.markdown("---")
st.sidebar.markdown("Built by Aniket Dhania.")
st.sidebar.markdown(
    "[GitHub](https://github.com/23578aniket) | [LinkedIn](https://linkedin.com/in/aniket-dhania-649715261/)")

# --- Footer ---
st.markdown("---")
st.markdown("Data Source: [World Air Quality Index Project](https://aqicn.org/)")
