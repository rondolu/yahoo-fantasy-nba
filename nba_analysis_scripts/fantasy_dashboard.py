"""
This module provides a Streamlit dashboard for visualizing NBA fantasy basketball rankings.

It loads player ranking data from a CSV file and presents it in an interactive table
and a bar chart, allowing users to filter by position and search for players.
"""

import streamlit as st
import pandas as pd
import os
import plotly.express as px

# Get the project root directory
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, os.pardir))
# Define the absolute path to the CSV file
CSV_FILE_PATH = os.path.join(project_root, "data", "nba_fantasy_ranking_top150.csv")

st.set_page_config(layout="wide")
st.title('🏀 Yahoo Fantasy Basketball 2025 Draft Ranking')
st.markdown('This dashboard provides a predicted ranking of NBA players for your Yahoo Fantasy Basketball league (9-category format), based on the provided 2025 player stats.')

@st.cache_data
def load_data(path):
    """
    Loads player ranking data from a CSV file.

    Args:
        path (str): The path to the CSV file.

    Returns:
        pd.DataFrame: A DataFrame containing the player ranking data.
    """
    if not os.path.exists(path):
        st.error(f"Error: CSV file not found at {path}. Running analysis script to generate it.")
        import subprocess
        subprocess.run(["python", os.path.join(project_root, "nba_analysis_scripts", "nba_analysis.py")])
        if not os.path.exists(path):
            st.error(f"Failed to generate CSV file. Please check the logs.")
            return pd.DataFrame()
    df = pd.read_csv(path)
    return df

df_ranked = load_data(CSV_FILE_PATH)

if not df_ranked.empty:
    st.sidebar.header('Filter Options')

    # Position filter
    all_positions = ['All Positions'] + sorted(df_ranked['primary_position'].unique().tolist())
    selected_position = st.sidebar.selectbox('Select Primary Position', all_positions)

    # Player search
    search_query = st.sidebar.text_input('Search Player Name', '')

    # Apply filters
    filtered_df = df_ranked.copy()
    if selected_position != 'All Positions':
        filtered_df = filtered_df[filtered_df['primary_position'] == selected_position]
    if search_query:
        filtered_df = filtered_df[filtered_df['full_name'].str.contains(search_query, case=False, na=False)]

    st.subheader('Top 150 Fantasy Players')
    st.write(f'Displaying {len(filtered_df)} of {len(df_ranked)} players.')
    st.dataframe(filtered_df)

    st.subheader('Top 20 Players by Fantasy Score')
    if not filtered_df.empty:
        top_20_players = filtered_df.head(20)
        fig = px.bar(top_20_players, x='full_name', y='Fantasy_Score', 
                     color='Fantasy_Score', color_continuous_scale=px.colors.sequential.Viridis,
                     title='Fantasy Score Distribution for Top 20 Players')
        fig.update_layout(xaxis_title='Player Name', yaxis_title='Fantasy Score')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No players to display for the selected filters.")
else:
    st.warning("No data loaded. Please ensure 'nba_fantasy_ranking_top150.csv' is generated and accessible.")