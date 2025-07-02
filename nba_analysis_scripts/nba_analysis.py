"""
This module performs analysis on NBA player stats for the 2025 season.

It includes functions for data loading and cleaning, generating player performance
leaderboard charts, analyzing player efficiency, and identifying top comprehensive
wing players. It also generates a 9-category fantasy basketball ranking.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os
from sklearn.preprocessing import MinMaxScaler

# Get the directory of the current script
script_dir = os.path.dirname(__file__)

# Define the path for saving charts, relative to the script's directory
CHARTS_DIR = os.path.join(script_dir, "charts")

# Ensure the charts directory exists
os.makedirs(CHARTS_DIR, exist_ok=True)

# --- Data Loading and Initial Cleaning ---
# Build the absolute path to the data file
data_file_path = os.path.join(script_dir, "..", "data", "nba_player_stats_2025.csv")

# Load the data
df = pd.read_csv(data_file_path)

def parse_fraction(s):
    """
    Parses a string in 'X/Y' format into a numerator and denominator.

    Args:
        s (str): The string to parse.

    Returns:
        tuple: A tuple containing the numerator and denominator as floats.
               Returns (None, None) if parsing fails.
    """
    if isinstance(s, str) and '/' in s:
        try:
            numerator, denominator = map(float, s.split('/'))
            return numerator, denominator
        except ValueError:
            return None, None
    return None, None

df['FGM'], df['FGA'] = zip(*df['FGM/A'].apply(parse_fraction))
df['FTM'], df['FTA'] = zip(*df['FTM/A'].apply(parse_fraction))

# Convert relevant columns to numeric, setting errors to NaN
numeric_cols = ['3PTM', 'AST', 'BLK', 'FG%', 'FT%', 'PTS', 'REB', 'ST', 'TO', 'FGM', 'FGA', 'FTM', 'FTA']
for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors='coerce')
    if col in ['FG%', 'FT%']:
        df[col] = (df[col] * 100).round().astype(pd.Int64Dtype())
    else:
        df[col] = df[col].fillna(0).astype(int)

print("First 5 rows of the DataFrame:")
print(df.head())
print("\nData types:")
print(df[numeric_cols].info())

# --- Player Performance Leaderboards ---
print("\n--- Generating Player Performance Leaderboard Charts ---")

# Top 10 points leaderboard
top_10_pts = df[['full_name', 'editorial_team_abbr', 'PTS']].sort_values(by='PTS', ascending=False).head(10)
top_10_pts['player_team'] = top_10_pts['full_name'] + ' (' + top_10_pts['editorial_team_abbr'] + ')'

sns.set_style("whitegrid")
plt.figure(figsize=(12, 8))
sns.barplot(x='PTS', y='player_team', data=top_10_pts, palette='viridis')
plt.title('NBA 2025 Season Top 10 Points Leaderboard', fontsize=16)
plt.xlabel('Total Points (PTS)', fontsize=12)
plt.ylabel('Player (Team)', fontsize=12)
plt.yticks(fontsize=10)
plt.xticks(fontsize=10)
for index, value in enumerate(top_10_pts['PTS']):
    plt.text(value, index, f'{value:.0f}', va='center', ha='left', fontsize=9)
plt.tight_layout()
plt.savefig(os.path.join(CHARTS_DIR, 'nba_top_10_pts_leaderboard.png'), dpi=300)
plt.close()

# --- Player Efficiency Analysis ---
print("\n--- Generating Player Efficiency Analysis Charts ---")

# Scatter plot 1: Points vs. Field Goal Percentage
df_filtered_fg = df.dropna(subset=['PTS', 'FG%'])
plt.figure(figsize=(12, 8))
sns.scatterplot(x='FG%', y='PTS', data=df_filtered_fg, hue='primary_position', size='PTS', sizes=(50, 800), alpha=0.7)
plt.title('NBA 2025 Season Player Points vs. Field Goal Percentage', fontsize=16)
plt.xlabel('Field Goal Percentage (FG%)', fontsize=12)
plt.ylabel('Total Points (PTS)', fontsize=12)
plt.xlim(0, 100)
plt.ylim(0, df_filtered_fg['PTS'].max() * 1.1)
plt.legend(title='Primary Position', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.savefig(os.path.join(CHARTS_DIR, 'nba_pts_vs_fg_efficiency.png'), dpi=300)
plt.close()

# Scatter plot 2: Assists vs. Turnovers
df['AST_TO_Ratio'] = df.apply(lambda row: row['AST'] / row['TO'] if row['TO'] > 0 else float('inf'), axis=1)
df_filtered_ast_to = df.dropna(subset=['AST', 'TO'])
plt.figure(figsize=(12, 8))
sns.scatterplot(x='TO', y='AST', data=df_filtered_ast_to, hue='primary_position', size='AST_TO_Ratio', sizes=(50, 800), alpha=0.7)
plt.title('NBA 2025 Season Player Assists vs. Turnovers', fontsize=16)
plt.xlabel('Total Turnovers (TO)', fontsize=12)
plt.ylabel('Total Assists (AST)', fontsize=12)
plt.xlim(0, df_filtered_ast_to['TO'].max() * 1.1)
plt.ylim(0, df_filtered_ast_to['AST'].max() * 1.1)
plt.legend(title='Primary Position', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.savefig(os.path.join(CHARTS_DIR, 'nba_ast_vs_to_efficiency.png'), dpi=300)
plt.close()

# --- Finding Top Comprehensive Wing Players ---
print("\n--- Finding Top Comprehensive Wing Players in NBA ---")

# 1. Define wing positions
wing_positions = ['SF', 'SG', 'PF']
df_wings = df[df['primary_position'].isin(wing_positions)].copy()

# 2. Select key stats for comprehensive score
scoring_stats = ['PTS', 'AST', 'REB', 'ST', 'BLK', 'FG%', '3PTM']
negative_stats = ['TO']

# Ensure all relevant columns are numeric and handle NaNs
df_wings_cleaned = df_wings.dropna(subset=scoring_stats + negative_stats).copy()

# 3. Normalize data using Min-Max Scaling
scaler = MinMaxScaler()

# Normalize positive stats
df_wings_cleaned[['norm_PTS', 'norm_AST', 'norm_REB', 'norm_ST', 'norm_BLK', 'norm_FG%', 'norm_3PTM']] = \
    scaler.fit_transform(df_wings_cleaned[scoring_stats])

# Normalize negative stats (turnovers)
df_wings_cleaned['norm_TO'] = scaler.fit_transform(df_wings_cleaned[negative_stats])

# 4. Calculate comprehensive score
weights = {
    'norm_PTS': 0.25,
    'norm_AST': 0.15,
    'norm_REB': 0.15,
    'norm_ST': 0.10,
    'norm_BLK': 0.10,
    'norm_FG%': 0.15,
    'norm_3PTM': 0.10,
    'norm_TO': -0.10
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

# 5. Find top 15 wing players by comprehensive score
top_wings = df_wings_cleaned.sort_values(by='Comprehensive_Score', ascending=False).head(15)

print("\n--- Top 15 Comprehensive Wing Players ---")
print(top_wings[['full_name', 'editorial_team_abbr', 'primary_position', 'Comprehensive_Score', 'PTS', 'AST', 'REB', 'ST', 'BLK', 'FG%', '3PTM', 'TO']])

# 6. Visualize comprehensive scores
plt.figure(figsize=(14, 9))
sns.barplot(x='Comprehensive_Score', y='full_name', data=top_wings, palette='coolwarm')
plt.title('NBA 2025 Season Top Comprehensive Wing Players', fontsize=18)
plt.xlabel('Comprehensive Score', fontsize=14)
plt.ylabel('Player Name', fontsize=14)
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)
plt.tight_layout()
plt.savefig(os.path.join(CHARTS_DIR, 'nba_top_comprehensive_wings.png'), dpi=300)
plt.close()

# --- Yahoo Fantasy Basketball 9-Category Ranking ---
print("\n--- Generating Yahoo Fantasy Basketball 9-Category Ranking (Top 150) ---")

# Select 9 categories for ranking
fantasy_categories = ['PTS', 'REB', 'AST', 'ST', 'BLK', '3PTM', 'FG%', 'FT%', 'TO']

# Create a copy to avoid SettingWithCopyWarning
df_fantasy = df.copy()

# Calculate Z-scores
for category in fantasy_categories:
    df_fantasy[category] = pd.to_numeric(df_fantasy[category], errors='coerce').fillna(0)
    
    mean = df_fantasy[category].mean()
    std = df_fantasy[category].std()
    
    if std == 0:
        df_fantasy[f'Z_{category}'] = 0 
    else:
        df_fantasy[f'Z_{category}'] = (df_fantasy[category] - mean) / std

# Invert Z-score for turnovers (negative stat)
df_fantasy['Z_TO'] = -df_fantasy['Z_TO']

# Calculate total fantasy score
df_fantasy['Fantasy_Score'] = df_fantasy[[f'Z_{cat}' for cat in fantasy_categories]].sum(axis=1)

# Rank players by fantasy score
df_fantasy_ranked = df_fantasy.dropna(subset=['Fantasy_Score']).sort_values(by='Fantasy_Score', ascending=False).reset_index(drop=True)

# Add rank column
df_fantasy_ranked['rank'] = df_fantasy_ranked.index + 1

# Select columns for CSV output
output_cols_csv = ['rank', 'full_name', 'editorial_team_abbr', 'primary_position', 'Fantasy_Score'] + fantasy_categories

# Save top 150 players to CSV
csv_output_path = os.path.join(CHARTS_DIR, 'nba_fantasy_ranking_top150.csv')
df_fantasy_ranked[output_cols_csv].head(150).to_csv(csv_output_path, index=False)

print(f"\nYahoo Fantasy Basketball 9-Category Top 150 Players saved to: {csv_output_path}")

print("\n--- NBA Player Analysis Script Finished ---")
print(f"All charts have been saved to the '{CHARTS_DIR}' directory.")