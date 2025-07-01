import streamlit as st
import pandas as pd
import os
import plotly.express as px

# 定義 CSV 檔案路徑
CSV_FILE_PATH = "charts/nba_fantasy_ranking_top150.csv"

# --- Streamlit 應用程式介面 --- 
st.set_page_config(layout="wide")
st.title('🏀 Yahoo Fantasy Basketball 2025 Draft Ranking')
st.markdown('This dashboard provides a predicted ranking of NBA players for your Yahoo Fantasy Basketball league (9-category format), based on the provided 2025 player stats.')

# 載入數據
@st.cache_data # 使用 Streamlit 的緩存功能，避免每次運行都重新載入數據
def load_data(path):
    if not os.path.exists(path):
        st.error(f"Error: CSV file not found at {path}. Please ensure 'nba_fantasy_ranking_top150.csv' exists in the 'charts' directory.")
        return pd.DataFrame()
    df = pd.read_csv(path)
    return df

df_ranked = load_data(CSV_FILE_PATH)

if not df_ranked.empty:
    st.sidebar.header('Filter Options')

    # 位置篩選器
    all_positions = ['All Positions'] + sorted(df_ranked['primary_position'].unique().tolist())
    selected_position = st.sidebar.selectbox('Select Primary Position', all_positions)

    # 球員搜尋器
    search_query = st.sidebar.text_input('Search Player Name', '')

    # 應用篩選
    filtered_df = df_ranked.copy()
    if selected_position != 'All Positions':
        filtered_df = filtered_df[filtered_df['primary_position'] == selected_position]
    if search_query:
        filtered_df = filtered_df[filtered_df['full_name'].str.contains(search_query, case=False, na=False)]

    st.subheader('Top 150 Fantasy Players')
    st.write(f'Displaying {len(filtered_df)} of {len(df_ranked)} players.')
    st.dataframe(filtered_df)

    st.subheader('Top 20 Players by Fantasy Score')
    # 確保數據不為空，避免繪圖錯誤
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
