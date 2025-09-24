# Live Air Quality Index (AQI) Dashboard for Major Indian Cities
### [https://aqidashboard-23578.streamlit.app/]) <!-- You will add this URL in the final step -->

## 1. Project Overview

This project is an end-to-end data engineering showcase that provides a real-time, interactive dashboard for monitoring the Air Quality Index (AQI) across major cities in India. The application fetches live data from a public API, processes it, and presents it through an intuitive web interface, demonstrating a complete data product lifecycle.

The primary goal is to make critical environmental data accessible and understandable to a general audience, while demonstrating core data engineering and visualization skills.

## 2. Technical Stack

* **Data Acquisition:** `requests` library to fetch data from the [AQICN](https://aqicn.org/api/) public API.
* **Data Processing:** `pandas` for data cleaning, transformation, and structuring.
* **Web Framework & Visualization:** `streamlit` for building the interactive web dashboard, including maps and data tables.
* **Deployment:** The application is deployed on Streamlit Community Cloud for public access.

## 3. Key Features

* **Live Data:** Fetches and displays real-time AQI data, with a 10-minute caching mechanism to manage API usage.
* **Interactive Map:** Geospatial visualization of cities with color-coded markers based on AQI severity levels.
* **Data Table:** A sortable and searchable table for detailed city-by-city comparison.
* **Robust Error Handling:** The application gracefully handles potential API and network errors.

## 4. How to Run Locally

1.  Clone the repository: `git clone https://github.com/23578aniket/Indian-AQI-Dashboard.git` <!-- **CHANGE your username here** -->
2.  Navigate to the project directory: `cd Indian-AQI-Dashboard`
3.  Install dependencies: `pip install -r requirements.txt`
4.  Set the API Token as an environment variable: `export AQI_API_TOKEN="YOUR_TOKEN_HERE"`
5.  Run the Streamlit app: `streamlit run aqi_dashboard.py`
