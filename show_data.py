import pandas as pd

# Adjust display options to show more data
pd.set_option('display.max_rows', 100) # Show up to 100 rows
pd.set_option('display.max_columns', 50) # Show up to 50 columns
pd.set_option('display.width', 200) # Adjust width to prevent line wrapping
pd.set_option('display.max_colwidth', 40) # Adjust max column width

file_path = "data/nba_player_stats_2025.csv"

try:
    df = pd.read_csv(file_path)
    if df.empty:
        print(f"The file '{file_path}' is empty.")
    else:
        print(f"Displaying data from '{file_path}':")
        print(df.to_string()) # Use to_string() to ensure the whole dataframe is printed
except FileNotFoundError:
    print(f"Error: The file '{file_path}' was not found.")
    print("Please make sure the main script ran successfully and generated the CSV file.")
except Exception as e:
    print(f"An error occurred while reading the file: {e}")
