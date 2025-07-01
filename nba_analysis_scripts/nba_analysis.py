import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os
from sklearn.preprocessing import MinMaxScaler

# 定義圖片保存路徑
CHARTS_DIR = "charts"

# 確保圖片保存目錄存在
os.makedirs(CHARTS_DIR, exist_ok=True)

# --- 數據載入和初步清洗 ---
# 獲取當前腳本的目錄
script_dir = os.path.dirname(__file__)
# 構建數據檔案的絕對路徑
# 從 script_dir (nba_analysis_scripts) 向上一個目錄 (yahoo-fantasy-mlb)，然後進入 data 資料夾
data_file_path = os.path.join(script_dir, "..", "data", "nba_player_stats_2025.csv")

# 載入數據
df = pd.read_csv(data_file_path)

# 處理 FGM/A 和 FTM/A 這種 'X/Y' 格式的數據
def parse_fraction(s):
    if isinstance(s, str) and '/' in s:
        try:
            numerator, denominator = map(float, s.split('/'))
            return numerator, denominator
        except ValueError:
            return None, None
    return None, None

df['FGM'], df['FGA'] = zip(*df['FGM/A'].apply(parse_fraction))
df['FTM'], df['FTA'] = zip(*df['FTM/A'].apply(parse_fraction))

# 將相關列轉換為數值型，無法轉換的設為 NaN
numeric_cols = ['3PTM', 'AST', 'BLK', 'FG%', 'FT%', 'PTS', 'REB', 'ST', 'TO', 'FGM', 'FGA', 'FTM', 'FTA']
for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors='coerce')
    # 將數值欄位轉換為整數
    if col in ['FG%', 'FT%']:
        # 百分比欄位先乘以100，然後四捨五入取整
        df[col] = (df[col] * 100).round().astype(pd.Int64Dtype()) # 使用 pd.Int64Dtype() 以便處理 NaN
    else:
        # 其他欄位直接填充0後取整
        df[col] = df[col].fillna(0).astype(int)

print("數據框前5行：")
print(df.head())
print("\n數據類型：")
print(df[numeric_cols].info())

# --- 第一部分：球員表現排行榜 (Player Performance Leaderboards) ---
print("\n--- Generating Player Performance Leaderboard Charts ---")

# 獲取得分排行榜前10名
top_10_pts = df[['full_name', 'editorial_team_abbr', 'PTS']].sort_values(by='PTS', ascending=False).head(10)
top_10_pts['player_team'] = top_10_pts['full_name'] + ' (' + top_10_pts['editorial_team_abbr'] + ')'

sns.set_style("whitegrid")
plt.figure(figsize=(12, 8))
# X軸：總得分 (PTS)，Y軸：球員名稱 (player_team)
sns.barplot(x='PTS', y='player_team', data=top_10_pts, palette='viridis')
plt.title('NBA 2025 Season Top 10 Points Leaderboard', fontsize=16)
plt.xlabel('Total Points (PTS)', fontsize=12) # X-axis label
plt.ylabel('Player (Team)', fontsize=12) # Y-axis label
plt.yticks(fontsize=10)
plt.xticks(fontsize=10)
for index, value in enumerate(top_10_pts['PTS']):
    plt.text(value, index, f'{value:.0f}', va='center', ha='left', fontsize=9)
plt.tight_layout()
plt.savefig(os.path.join(CHARTS_DIR, 'nba_top_10_pts_leaderboard.png'), dpi=300)
plt.close() # Close the plot to free memory

# --- 第二部分：球員效率分析 (Player Efficiency Analysis) ---
print("\n--- Generating Player Efficiency Analysis Charts ---")

# 散佈圖 1: 得分 (PTS) vs 投籃命中率 (FG%)
df_filtered_fg = df.dropna(subset=['PTS', 'FG%'])
plt.figure(figsize=(12, 8))
# X軸：投籃命中率 (FG%)，Y軸：總得分 (PTS)
sns.scatterplot(x='FG%', y='PTS', data=df_filtered_fg, hue='primary_position', size='PTS', sizes=(50, 800), alpha=0.7)
plt.title('NBA 2025 Season Player Points vs. Field Goal Percentage', fontsize=16)
plt.xlabel('Field Goal Percentage (FG%)', fontsize=12) # X-axis label
plt.ylabel('Total Points (PTS)', fontsize=12) # Y-axis label
plt.xlim(0, 100) 
plt.ylim(0, df_filtered_fg['PTS'].max() * 1.1)
plt.legend(title='Primary Position', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.savefig(os.path.join(CHARTS_DIR, 'nba_pts_vs_fg_efficiency.png'), dpi=300)
plt.close()

# 散佈圖 2: 助攻 (AST) vs 失誤 (TO)
df['AST_TO_Ratio'] = df.apply(lambda row: row['AST'] / row['TO'] if row['TO'] > 0 else float('inf'), axis=1)
df_filtered_ast_to = df.dropna(subset=['AST', 'TO'])
plt.figure(figsize=(12, 8))
# X軸：總失誤 (TO)，Y軸：總助攻 (AST)
sns.scatterplot(x='TO', y='AST', data=df_filtered_ast_to, hue='primary_position', size='AST_TO_Ratio', sizes=(50, 800), alpha=0.7)
plt.title('NBA 2025 Season Player Assists vs. Turnovers', fontsize=16)
plt.xlabel('Total Turnovers (TO)', fontsize=12) # X-axis label
plt.ylabel('Total Assists (AST)', fontsize=12) # Y-axis label
plt.xlim(0, df_filtered_ast_to['TO'].max() * 1.1)
plt.ylim(0, df_filtered_ast_to['AST'].max() * 1.1)
plt.legend(title='Primary Position', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.savefig(os.path.join(CHARTS_DIR, 'nba_ast_vs_to_efficiency.png'), dpi=300)
plt.close()

# --- 移除位置數據趨勢圖表 (Positional Data Trends) ---
# 根據用戶要求，此部分程式碼已移除

# --- 第五部分：找出聯盟綜合數據優秀的側翼球員 ---
print("\n--- Finding Top Comprehensive Wing Players in NBA ---")

# 1. 定義側翼球員位置
wing_positions = ['SF', 'SG', 'PF'] # 更新為包含PF
df_wings = df[df['primary_position'].isin(wing_positions)].copy()

# 2. 選擇用於綜合評分的關鍵統計數據
scoring_stats = ['PTS', 'AST', 'REB', 'ST', 'BLK', 'FG%', '3PTM']
negative_stats = ['TO'] # 失誤是負向指標

# 確保所有相關列都是數值型，並處理可能存在的NaN值 (例如用0填充，或直接dropna)
df_wings_cleaned = df_wings.dropna(subset=scoring_stats + negative_stats).copy()

# 3. 數據標準化 (Min-Max Scaling)
scaler = MinMaxScaler()

# 標準化正向指標
df_wings_cleaned[['norm_PTS', 'norm_AST', 'norm_REB', 'norm_ST', 'norm_BLK', 'norm_FG%', 'norm_3PTM']] = \
    scaler.fit_transform(df_wings_cleaned[scoring_stats])

# 標準化負向指標 (失誤，越低越好，所以標準化後需要反轉，或者在加權時給負權重)
df_wings_cleaned['norm_TO'] = scaler.fit_transform(df_wings_cleaned[negative_stats])

# 4. 計算綜合評分 (加權求和)
weights = {
    'norm_PTS': 0.25,
    'norm_AST': 0.15,
    'norm_REB': 0.15,
    'norm_ST': 0.10,
    'norm_BLK': 0.10,
    'norm_FG%': 0.15,
    'norm_3PTM': 0.10,
    'norm_TO': -0.10 # 失誤為負向權重
}

df_wings_cleaned['Comprehensive_Score'] = (
    df_wings_cleaned['norm_PTS'] * weights['norm_PTS'] +
    df_wings_cleaned['norm_AST'] * weights['norm_AST'] +
    df_wings_cleaned['norm_REB'] * weights['norm_REB'] +
    df_wings_cleaned['norm_ST'] * weights['norm_ST'] +
    df_wings_cleaned['norm_BLK'] * weights['norm_BLK'] +
    df_wings_cleaned['norm_FG%'] * weights['norm_FG%'] +
    df_wings_cleaned['norm_3PTM'] * weights['norm_3PTM'] +
    df_wings_cleaned['norm_TO'] * weights['norm_TO']
)

# 5. 找出綜合評分最高的側翼球員 (前15名)
top_wings = df_wings_cleaned.sort_values(by='Comprehensive_Score', ascending=False).head(15)

print("\n--- Top 15 Comprehensive Wing Players ---")
print(top_wings[['full_name', 'editorial_team_abbr', 'primary_position', 'Comprehensive_Score', 'PTS', 'AST', 'REB', 'ST', 'BLK', 'FG%', '3PTM', 'TO']])

# 6. 視覺化：長條圖展示綜合評分
plt.figure(figsize=(14, 9))
sns.barplot(x='Comprehensive_Score', y='full_name', data=top_wings, palette='coolwarm')
plt.title('NBA 2025 Season Top Comprehensive Wing Players', fontsize=18)
plt.xlabel('Comprehensive Score', fontsize=14) # X-axis label
plt.ylabel('Player Name', fontsize=14) # Y-axis label
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)
plt.tight_layout()
plt.savefig(os.path.join(CHARTS_DIR, 'nba_top_comprehensive_wings.png'), dpi=300)
plt.close()

# --- Yahoo Fantasy Basketball 9-Category Ranking ---
print("\n--- Generating Yahoo Fantasy Basketball 9-Category Ranking (Top 150) ---")

# 選擇用於排名的9項數據
fantasy_categories = ['PTS', 'REB', 'AST', 'ST', 'BLK', '3PTM', 'FG%', 'FT%', 'TO']

# 複製數據框以避免SettingWithCopyWarning
df_fantasy = df.copy()

# 計算Z-scores
for category in fantasy_categories:
    df_fantasy[category] = pd.to_numeric(df_fantasy[category], errors='coerce').fillna(0)
    
    mean = df_fantasy[category].mean()
    std = df_fantasy[category].std()
    
    if std == 0:
        df_fantasy[f'Z_{category}'] = 0 
    else:
        df_fantasy[f'Z_{category}'] = (df_fantasy[category] - mean) / std

# 處理負面數據 (Turnovers) - Z-score取負值
df_fantasy['Z_TO'] = -df_fantasy['Z_TO']

# 計算綜合Fantasy Score (所有Z-score的總和)
df_fantasy['Fantasy_Score'] = df_fantasy[[f'Z_{cat}' for cat in fantasy_categories]].sum(axis=1)

# 根據Fantasy Score進行排名
df_fantasy_ranked = df_fantasy.dropna(subset=['Fantasy_Score']).sort_values(by='Fantasy_Score', ascending=False).reset_index(drop=True)

# 新增 'rank' 欄位
df_fantasy_ranked['rank'] = df_fantasy_ranked.index + 1

# 選擇要輸出到CSV的列，將 'rank' 放在最前面
output_cols_csv = ['rank', 'full_name', 'editorial_team_abbr', 'primary_position', 'Fantasy_Score'] + fantasy_categories

# 將前150名球員的數據保存到CSV檔案
csv_output_path = os.path.join(CHARTS_DIR, 'nba_fantasy_ranking_top150.csv')
df_fantasy_ranked[output_cols_csv].head(150).to_csv(csv_output_path, index=False)

print(f"\nYahoo Fantasy Basketball 9-Category Top 150 Players saved to: {csv_output_path}")