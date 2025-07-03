
"""
This module performs analysis on NBA player stats for the 2025 season.

It includes functions for data loading and cleaning, and generates a 9-category
fantasy basketball ranking.
"""

import pandas as pd
import numpy as np
import os
from sklearn.preprocessing import MinMaxScaler

# Get the directory of the current script
script_dir = os.path.dirname(__file__)

# Define the path for saving data, relative to the script's directory
DATA_DIR = os.path.join(script_dir, "..", "data")

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
csv_output_path = os.path.join(DATA_DIR, 'nba_fantasy_ranking_top150.csv')
df_fantasy_ranked[output_cols_csv].head(150).to_csv(csv_output_path, index=False)

print(f"\nYahoo Fantasy Basketball 9-Category Top 150 Players saved to: {csv_output_path}")

print("\n--- NBA Player Analysis Script Finished ---")
