import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from bs4 import BeautifulSoup

# Streamlit UI setup
st.set_page_config(page_title="Battery Report Analyzer", layout="wide")
st.title("🔋 Battery Report Analyzer")
st.sidebar.header("Upload Battery Report")

# File uploader
uploaded_file = st.sidebar.file_uploader("Upload Battery Report (HTML)", type=["html"])

if uploaded_file is not None:
    # Parse HTML file
    soup = BeautifulSoup(uploaded_file, "html.parser")
    
    # Extract recent usage table
    recent_usage = []
    for row in soup.find_all("tr", class_=["even", "odd"]):
        cols = row.find_all("td")
        if len(cols) >= 5:
            time = cols[0].get_text(strip=True)
            state = cols[1].get_text(strip=True)
            source = cols[2].get_text(strip=True)
            percent = cols[3].get_text(strip=True).replace('%', '').strip()
            power = cols[4].get_text(strip=True).replace('mWh', '').strip()
            
            try:
                percent = int(percent) if percent.isdigit() else None
                power = int(power) if power.isdigit() else None
                recent_usage.append([time, state, source, percent, power])
            except ValueError as e:
                st.error(f"Data conversion error at time {time}: {e}")
    
    # Convert to DataFrame
    df = pd.DataFrame(recent_usage, columns=["Time", "State", "Source", "Battery %", "Power (mWh)"])
    df["Time"] = pd.to_datetime(df["Time"], errors='coerce')
    df = df.dropna()
    df = df.sort_values("Time")
    
    # Sidebar filters
    st.sidebar.subheader("Filters")
    selected_state = st.sidebar.selectbox("Select State", ["All"] + list(df["State"].unique()))
    if selected_state != "All":
        df = df[df["State"] == selected_state]
    
    # Display DataFrame
    st.write("### Extracted Data")
    st.dataframe(df)
    
    # Tabs for different visualizations
    tab1, tab2 = st.tabs(["📊 Battery Usage", "⚡ Power Consumption"])
    
    with tab1:
        st.write("### Battery Usage Over Time")
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(df["Time"], df["Battery %"], marker="o", linestyle="-", color="b", label="Battery %")
        ax.set_xlabel("Time")
        ax.set_ylabel("Battery %")
        ax.set_title("Battery Usage Over Time")
        ax.legend()
        ax.grid()
        plt.xticks(rotation=45)
        st.pyplot(fig)
    
    with tab2:
        st.write("### Power Consumption Over Time")
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(df["Time"], df["Power (mWh)"], marker="s", linestyle="--", color="r", label="Power (mWh)")
        ax.set_xlabel("Time")
        ax.set_ylabel("Power (mWh)")
        ax.set_title("Power Consumption Over Time")
        ax.legend()
        ax.grid()
        plt.xticks(rotation=45)
        st.pyplot(fig)
    
    # Insights
    average_drain = df[df["Source"] == "Battery"]["Battery %"].diff().mean()
    st.sidebar.write(f"**⚡ Average battery drain per session:** {-average_drain:.2f}%")