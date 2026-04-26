import streamlit as st
import re
import math
import pandas as pd
from urllib.parse import urlparse, parse_qs
import streamlit.components.v1 as components

# -------------------------------
# Page Config
# -------------------------------
st.set_page_config(page_title="Concrete Calculator", layout="wide")

# -------------------------------
# Custom CSS
# -------------------------------
st.markdown("""
<style>
.main-title {
    font-size: 40px;
    font-weight: bold;
    color: #1F618D;
    text-align: center;
}
.card {
    background-color: #F4F6F7;
    padding: 20px;
    border-radius: 10px;
    box-shadow: 2px 2px 8px rgba(0,0,0,0.1);
}
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-title">🛣️ Concrete Recommendation System</p>', unsafe_allow_html=True)

# -------------------------------
# Session State
# -------------------------------
if "data" not in st.session_state:
    st.session_state.data = {}

# -------------------------------
# Extract Lat/Lon
# -------------------------------
def extract_lat_long(url):
    try:
        match = re.search(r'@(-?\d+\.\d+),(-?\d+\.\d+)', url)
        if match:
            return float(match.group(1)), float(match.group(2))

        parsed = urlparse(url)
        query = parse_qs(parsed.query)
        if "q" in query:
            coords = query["q"][0].split(",")
            return float(coords[0]), float(coords[1])

        return None, None
    except:
        return None, None

# -------------------------------
# Tabs
# -------------------------------
tab1, tab2, tab3 = st.tabs(["📥 Input", "📊 Data View", "🧮 Concrete Needed"])

# ===============================
# TAB 1 - INPUT
# ===============================
with tab1:
    st.subheader("Enter Pothole Details")

    depth = st.number_input("Depth (meters)", min_value=0.0)
    width = st.number_input("Width (meters)", min_value=0.0)
    length = st.number_input("Length (meters)", min_value=0.0)
    location_url = st.text_input("Google Maps URL")

    if st.button("Submit"):
        lat, lon = extract_lat_long(location_url)

        # Volume & Concrete
        volume = depth * width * length
        concrete_kg = volume * 2400

        st.session_state.data = {
            "depth": depth,
            "width": width,
            "length": length,
            "latitude": lat,
            "longitude": lon,
            "concrete_kg": concrete_kg
        }

        # Save to Excel automatically
        df = pd.DataFrame([st.session_state.data])

        try:
            existing = pd.read_excel("pothole_data.xlsx")
            df = pd.concat([existing, df], ignore_index=True)
        except:
            pass

        df.to_excel("pothole_data.xlsx", index=False)

        st.success("Data Saved Successfully!!")

# ===============================
# TAB 2 - DISPLAY + EXCEL SAVE
# ===============================
with tab2:
    st.subheader("Stored Data")

    data = st.session_state.data

    if data:

        col1, col2 = st.columns(2)

        with col1:
            st.write(f"**Depth:** {data.get('depth')} m")
            st.write(f"**Width:** {data.get('width')} m")
            st.write(f"**Length:** {data.get('length')} m")

        with col2:
            st.write(f"**Latitude:** {data.get('latitude')}")
            st.write(f"**Longitude:** {data.get('longitude')}")
            
        st.markdown('</div>', unsafe_allow_html=True)

    else:
        st.warning("No data available.")

# ===============================
# TAB 3 - MAP + CONCRETE IN KG
# ===============================
with tab3:
    st.subheader("Concrete Requirement")

    data = st.session_state.data

    if data:
        depth = data.get("depth", 0)
        width = data.get("width", 0)
        length = data.get("length", 0)
        lat = data.get("latitude")
        lon = data.get("longitude")

        # Volume (m³)
        volume = depth * width * length

        # Concrete density ≈ 2400 kg/m³
        concrete_kg = volume * 2400

        # Map display
        if lat and lon:
            st.map({"lat": [lat], "lon": [lon]})
        else:
            st.warning("Location not available for map.")

        st.write(f"📦 Volume: {volume:.3f} m³")
        st.write(f"🧱 Concrete Required: {concrete_kg:.2f} KG")

        st.markdown('</div>', unsafe_allow_html=True)

    else:
        st.warning("Please enter data first.")

# -------------------------------
# JS Enhancement
# -------------------------------
components.html("""
<script>
console.log("Interactive Dashboard Loaded");
</script>
""", height=0)