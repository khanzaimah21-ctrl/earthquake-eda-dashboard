import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="USGS Earthquakes 2024 - USA", layout="wide")

st.title("🌍 USGS Earthquakes 2024 - USA Explorer")
st.markdown("This dashboard explores **US earthquakes in 2024** from USGS data. Most earthquakes happened in **California**, especially The Geysers region. Use the filters on the left to explore!")

@st.cache_data
def load_data():
    df = pd.read_csv("all_month_2024.csv")
    df['time'] = pd.to_datetime(df['time'], errors='coerce')
    df['date'] = df['time'].dt.date
    return df

df = load_data()

st.sidebar.header("🔍 Filters")
mag_min, mag_max = st.sidebar.slider("Select Magnitude Range",
    float(df['mag'].min()), float(df['mag'].max()), (float(df['mag'].min()), float(df['mag'].max())))

mag_type = st.sidebar.multiselect("Select Magnitude Type",
    options=sorted(df['magType'].dropna().unique()),
    default=sorted(df['magType'].dropna().unique()))

search = st.sidebar.text_input("Search Place (e.g. California, Alaska)")

filtered = df[(df['mag'] >= mag_min) & (df['mag'] <= mag_max) & (df['magType'].isin(mag_type))]
if search:
    filtered = filtered[filtered['place'].str.contains(search, case=False, na=False)]

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Earthquakes", len(filtered))
c2.metric("Strongest Earthquake", round(filtered['mag'].max(), 2) if len(filtered)>0 else 0)
c3.metric("Deepest (km)", round(filtered['depth'].max(), 2) if len(filtered)>0 else 0)
c4.metric("Average Magnitude", round(filtered['mag'].mean(), 2) if len(filtered)>0 else 0)

st.markdown("---")
st.subheader("1. Distribution of Magnitude (Univariate)")
fig1, ax1 = plt.subplots()
sns.histplot(filtered['mag'], bins=30, kde=True, ax=ax1, color="#FF4B4B")
ax1.set_xlabel("Magnitude")
st.pyplot(fig1)

col1, col2 = st.columns(2)
with col1:
    st.subheader("2. Top 10 Places (Comparison)")
    top = filtered['place'].value_counts().head(10)
    fig2, ax2 = plt.subplots(figsize=(6,4))
    sns.barplot(x=top.values, y=top.index, palette="viridis", ax=ax2)
    st.pyplot(fig2)
with col2:
    st.subheader("3. Depth vs Magnitude (Bivariate)")
    fig3, ax3 = plt.subplots(figsize=(6,4))
    sns.scatterplot(data=filtered, x='mag', y='depth', alpha=0.5, color="#1f77b4", ax=ax3)
    ax3.invert_yaxis()
    st.pyplot(fig3)

st.subheader("4. Earthquakes Over Time")
daily = filtered.groupby('date').size().reset_index(name='count')
fig4, ax4 = plt.subplots(figsize=(10,3))
sns.lineplot(data=daily, x='date', y='count', ax=ax4, color="orange")
st.pyplot(fig4)

st.subheader("5. 🗺️ Interactive Earthquake Map (Plotly)")
fig5 = px.scatter_map(filtered.sample(min(2000, len(filtered))),
    lat="latitude", lon="longitude", color="mag",
    hover_name="place", hover_data=["mag","depth","time"],
    color_continuous_scale="Reds", zoom=3, height=500)
fig5.update_layout(map_style="carto-positron", margin={"r":0,"t":0,"l":0,"b":0})
st.plotly_chart(fig5, use_container_width=True) 

st.subheader("6. Average Magnitude by Type")
avg_type = filtered.groupby('magType')['mag'].mean().reset_index()
fig6, ax6 = plt.subplots()
sns.barplot(data=avg_type, x='magType', y='mag', palette="coolwarm", ax=ax6)
st.pyplot(fig6)

st.markdown("---")
if st.checkbox("Show Raw Data"):
    st.dataframe(filtered)

st.markdown("---")
st.subheader("📌 Key Findings")
st.markdown("""
- **Most earthquakes are small:** Most magnitudes are between 1.0 and 3.0.
- **California is most active:** The Geysers, California has the highest number of earthquakes in the USA.
- **Depth vs Magnitude:** Deeper earthquakes are not always stronger.
- **Magnitude type ml** is the most common type in this dataset.
- **2024 had frequent activity:** Earthquakes happened almost every day in the USA.
""")