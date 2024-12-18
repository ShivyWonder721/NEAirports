"""
Name: Shiv Patel
CS230: Section 3
Data: airports.csv
URL: [Your Streamlit Cloud URL]

Description: This program provides an interactive visualization and analysis tool for airport data from New England states (MA, CT, RI, NH, VT, ME).
The goal of this website is to provide a specialized and comprehensive filter search engine for all possible air travel locations within the area.
"""

import streamlit as st
import pandas as pd
import pydeck as pdk
import matplotlib.pyplot as plt
import seaborn as sns

# [PY1] Function with default parameters
def load_data(filepath, delimiter=","):
#Loads and cleans data from a CSV file
    data = pd.read_csv(filepath, delimiter=delimiter)
    return data

# [PY2] Function that returns multiple values
def calculate_stats(df, column):
#Calculates max, min, and mean for a column
    max_val = df[column].max()
    min_val = df[column].min()
    mean_val = df[column].mean()
    return max_val, min_val, mean_val

# Load the CSV file
file_path = 'airports.csv'  #On the basis that the file is in the same folder as code
# Use load_data function to load csv file
airports_data = load_data(file_path)

# [DA1] Clean the data
# Dropped rows that have missing values
airports_data = airports_data.dropna(subset=["latitude_deg", "longitude_deg", "elevation_ft"])

# Filter data for New England states
new_england_states = ['MA', 'CT', 'RI', 'NH', 'VT', 'ME']
# Ensure no rows are skipped, filter by state abbreviations from the iso_region
airports_data = airports_data[airports_data["iso_country"] == "US"]
airports_data = airports_data[airports_data["iso_region"].str[-2:].isin(new_england_states)]

# Introduction/Title
st.title("New England Airport Data Analysis and Visualization")
st.write("Welcome to the New England Airport Data Analysis and Visualization website. The goal of this website is to provide a specialized and comprehensive search engine for all possible air travel locations within the New England area.")
st.write(f"Total Airports in New England: {len(airports_data)}")
st.write("**Fun Fact:** Rhode Island’s T.F. Green Airport, opened in July 1929, was the first state-owned and operated airport in the entire United States.")

# Header for sidebar filtering
st.sidebar.header("Filters")

# [ST1] Dropdown for selecting airport types
# Create a mapping from actual types to display labels
# Replace underscored with spaces and Uppercasing for words
airport_type_mapping = {atype: atype.replace('_', ' ').title() for atype in airports_data["type"].unique()}
# Create a list of display labels
display_labels = list(airport_type_mapping.values())
# Putting back formatted labels to original airport type
reverse_mapping = {v: k for k, v in airport_type_mapping.items()}

# Multiselect with display labels
selected_types_display = st.sidebar.multiselect(
    "Select Airport Types:",
    options=display_labels,
    default=display_labels
)
# Takes formatted user selection label back to the original airport type strings to filter correctly
selected_types = [reverse_mapping[label] for label in selected_types_display]

# [ST2] Slider for filtering elevation
selected_elevation = st.sidebar.slider(
    "Select Elevation Range (ft):",
    int(airports_data["elevation_ft"].min()),
    int(airports_data["elevation_ft"].max()),
    (int(airports_data["elevation_ft"].min()), int(airports_data["elevation_ft"].max()))
)
# [ST3] User Input to filter by Airport Name
keyword = st.sidebar.text_input("Filter by Keyword in Airport Name (optional):", "")

# [DA4], [DA5] Filter data based on user selection
filtered_data = airports_data[
    (airports_data["type"].isin(selected_types)) &
    (airports_data["elevation_ft"].between(*selected_elevation))
]

# Apply keyword filtering if provided
if keyword.strip():
    filtered_data = filtered_data[filtered_data["name"].str.contains(keyword, case=False, na=False)]

# Another user input box to filter by Town Name
town_name = st.sidebar.text_input("Filter by Town Name (optional):", "")
if town_name.strip():
    filtered_data = filtered_data[filtered_data["municipality"].str.contains(town_name, case=False, na=False)]

st.write("### Filtered Data Overview")
st.dataframe(filtered_data)

st.write("Filtered Data Overview neatly organized from the raw data set.")

# [VIZ1] Bar chart for airport types
st.write("### Distribution of Airport Types")
type_counts = filtered_data["type"].value_counts()
fig, ax = plt.subplots()
type_counts.plot(kind="bar", color="skyblue", ax=ax)

# Change labels for the bar chart and rotate 45 degrees
new_labels = [label.replace("_", " ").title() for label in type_counts.index]
ax.set_xticklabels(new_labels, rotation=45)

ax.set_title("Airport Types Distribution")
ax.set_xlabel("Type")
ax.set_ylabel("Count")
st.pyplot(fig)

# Get state abbreviations from the iso_region column
filtered_data["state"] = filtered_data["iso_region"].str[-2:]

# Create a dictionary of dictionaries for airport types per state
state_type_counts = {}
for state in filtered_data["state"].unique():
    state_df = filtered_data[filtered_data["state"] == state]
    type_counts_state = state_df["type"].value_counts().to_dict()
    state_type_counts[state] = type_counts_state

st.write("### Airport Type Counts Per State (Dictionary Access)")
for state, types_dict in state_type_counts.items():
    with st.expander(f"View Airport Types for {state}"):
        for airport_type, count in types_dict.items():

# Convert underscores to spaces and capitalize words in airport_type
            formatted_type = airport_type.replace('_',' ').title()
            st.write(f"- {formatted_type}: {count}")

# [VIZ2] Boxplot for elevation distribution by airport type
st.write("### Elevation Distribution by Airport Type")
fig, ax = plt.subplots()
#Modules Not Used in Class, Seaborn (Extra Credit)
sns.boxplot(
    data=filtered_data,
    x="type",
    y="elevation_ft",
    ax=ax,
    palette="Set2"
)

# Format Labels
current_labels = [tick.get_text() for tick in ax.get_xticklabels()]
new_box_labels = [label.replace("_", " ").title() for label in current_labels]
ax.set_xticklabels(new_box_labels, rotation=45)

ax.set_title("Elevation Distribution by Airport Type")
ax.set_xlabel("Airport Type")
ax.set_ylabel("Elevation (ft)")
st.pyplot(fig)

# [MAP] PyDeck map for airport locations
st.write("### Map of Airports")
map_data = filtered_data[["latitude_deg", "longitude_deg", "name", "elevation_ft", "type"]]

#Map Formatting, zoomed in map and add 3D perspective on NE Area, and change visualization
st.pydeck_chart(
    pdk.Deck(
        map_style="mapbox://styles/mapbox/light-v9",
        initial_view_state=pdk.ViewState(
            latitude=map_data["latitude_deg"].mean(),
            longitude=map_data["longitude_deg"].mean(),
            zoom=6,
            pitch=50,
        ),
        layers=[
            pdk.Layer(
                "ScatterplotLayer",
                data=map_data,
                get_position="[longitude_deg, latitude_deg]",
                get_radius=1000,
                get_color=[200, 30, 0, 160],
                pickable=True,
                tooltip={
                    "html": "<b>Airport Name:</b> {name}<br><b>Elevation (ft):</b> {elevation_ft}<br><b>Type:</b> {type}",
                    "style": {
                        "backgroundColor": "black",
                        "color": "white",
                        "padding": "5px"
                    }
                }
            )
        ],
        tooltip={
            "html": "<b>Airport Name:</b> {name}<br><b>Elevation (ft):</b> {elevation_ft}<br><b>Type:</b> {type}"
        }
    )
)

#[PY4] List comprehension for elevation
elevation_info = [
    {"Name": row["name"], "Elevation (ft)": row["elevation_ft"]}
    for _, row in filtered_data.iterrows()
]

st.write("### Enhanced Elevation Information")

# Convert to a data frame and sort by elevation
elevation_df = pd.DataFrame(elevation_info).sort_values("Elevation (ft)", ascending=False)

# Define a function to highlight rows based on elevation, color coding based on elevation
def highlight_elevation(row):
    if row["Elevation (ft)"] > 1000:
        return ['background-color: #ffdddd'] * len(row)  # Light red background
    else:
        return ['background-color: #ddffdd'] * len(row)  # Light green background

# Apply styling for visualization
styled_elevation = (
    elevation_df.style
    .apply(highlight_elevation, axis=1)
    .format({"Elevation (ft)": "{:.2f}"})  # Ensure two decimal places are displayed
    .set_properties(**{
        'border': '1px solid #999999',  # Add borders to the table
        'color': '#333',                 # Dark text color for readability
        'font-size': '14px'              # Increase font size
    })
)
st.write(styled_elevation)

# [DA3] Find the top 5 highest airports
st.write("### Top 5 Highest Airports")
top_elevations = filtered_data.nlargest(5, "elevation_ft")
st.dataframe(top_elevations[["name", "elevation_ft"]])

# [PY5] Access dictionary keys and values
# Extract state abbreviations from iso_region
filtered_data["state"] = filtered_data["iso_region"].str[-2:]

# [DA7] [DA9] Add a new column and perform calculations to convert from ft to m
filtered_data["elevation_m"] = filtered_data["elevation_ft"] * 0.3048

# Create a subset of the data and round the elevation values
rounded_df = filtered_data[["name", "elevation_ft", "elevation_m"]].copy()
rounded_df["elevation_ft"] = rounded_df["elevation_ft"].round(2)
rounded_df["elevation_m"] = rounded_df["elevation_m"].round(2)

# Format columns properly
rounded_df.rename(columns=lambda c: c.replace('_', ' ').title(), inplace=True)

styled_df = (
    rounded_df.style
    .format({"Elevation Ft": "{:.2f}", "Elevation M": "{:.2f}"})
    .set_properties(**{
        "background-color": "#f0f8ff",
        "color": "#333",
        "font-size": "14px"
    })
)

st.write("### Elevation Data in Meters")
st.write(styled_df)
st.markdown("<p style='font-size:20px;'><i>(Meter conversion for all my metric system people!)</i></p>", unsafe_allow_html=True)

# [ST4] Customized page design
st.markdown(
    """
    <style>
    .reportview-container {
        background: #f7f7f7;
        color: #333;
    }
    </style>
    """,
    unsafe_allow_html=True,
)