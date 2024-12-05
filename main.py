import streamlit as st
import pandas as pd
import zipfile
import requests
from io import BytesIO
import plotly.express as px

@st.cache_data
def fetch_data():
    """Downloads and processes the national names dataset."""
    url = 'https://www.ssa.gov/oact/babynames/names.zip'
    response = requests.get(url)
    with zipfile.ZipFile(BytesIO(response.content)) as z:
        all_data = []
        for filename in z.namelist():
            if filename.endswith('.txt'):
                with z.open(filename) as f:
                    temp_df = pd.read_csv(f, header=None, names=['Name', 'Gender', 'Count'])
                    temp_df['Year'] = int(filename[3:7])
                    all_data.append(temp_df)
    data = pd.concat(all_data, ignore_index=True)
    return data

@st.cache_data
def filter_one_hit_wonders(data):
    """Identifies names that appeared in only one year."""
    name_year_count = data.groupby(['Name', 'Gender'])['Year'].nunique()
    one_hit_names = name_year_count[name_year_count == 1].index
    return data.set_index(['Name', 'Gender']).loc[one_hit_names].reset_index()

# Load data
names_data = fetch_data()
one_hit_wonder_data = filter_one_hit_wonders(names_data)

# App layout
st.title("National Names Analysis")

with st.sidebar:
    selected_name = st.text_input("Search a Name:")
    selected_year = st.slider("Choose a Year:", 1880, 2023, 2000)
    top_n = st.selectbox("Number of Top Names to Show:", [5, 10, 15, 20])
    selected_gender = st.radio("Filter by Gender:", options=["All", "M", "F"])

# Apply gender filter
if selected_gender != "All":
    names_data = names_data[names_data["Gender"] == selected_gender]

# Tabs
tab1, tab2 = st.tabs(["Name Trends", "Year Overview"])

with tab1:
    st.subheader("Name Popularity Over Time")
    filtered_data = names_data[names_data["Name"] == selected_name]
    if not filtered_data.empty:
        trend_chart = px.line(filtered_data, x="Year", y="Count", color="Gender", title=f"Trends for '{selected_name}'")
        st.plotly_chart(trend_chart)
    else:
        st.write("No data available for the entered name.")

    st.subheader("One-Hit Wonder Names")
    ohw_chart = px.histogram(
        one_hit_wonder_data[one_hit_wonder_data["Year"] == selected_year],
        x="Name",
        color="Gender",
        title=f"One-Hit Wonders in {selected_year}"
    )
    st.plotly_chart(ohw_chart)

with tab2:
    st.subheader("Top Names by Year")
    top_names = names_data[names_data["Year"] == selected_year].groupby(["Name", "Gender"])["Count"].sum().reset_index()
    top_names = top_names.sort_values(by="Count", ascending=False).head(top_n)
    bar_chart = px.bar(top_names, x="Name", y="Count", color="Gender", title=f"Top {top_n} Names in {selected_year}")
    st.plotly_chart(bar_chart)

    st.subheader("Detailed Name Data")
    st.dataframe(names_data[names_data["Year"] == selected_year].head(100))

# Additional container
st.container()
st.write("Explore the dataset and uncover interesting trends!")
