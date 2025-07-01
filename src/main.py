import pandas as pd
from api_handler import YahooAPI
import json

def get_game_id(api, year=2024):
    """Fetches the game ID for the specified NBA season."""
    try:
        print("Fetching game information for NBA...")
        response = api.get("game/nba")
        fantasy_content = response.get('fantasy_content', {})
        if 'game' in fantasy_content:
            game_data = fantasy_content['game'][0]
            if game_data.get('season') == str(year):
                game_key = game_data.get('game_key')
                print(f"Found Game ID for {year} NBA: {game_key}")
                return game_key
        print(f"Warning: Could not find a specific game ID for NBA season {year}.")
        print("Using the generic 'nba' game key as a fallback.")
        return "nba"
    except Exception as e:
        print(f"An error occurred while fetching the game ID: {e}")
        return None

def get_league_id(api, game_id):
    """Fetches the user's first available league ID for the given game."""
    try:
        response = api.get(f"users;use_login=1/games;game_keys={game_id}/leagues")
        leagues = response['fantasy_content']['users']['0']['user'][1]['games']['0']['game'][1]['leagues']
        if leagues['0']['league']:
            league_id = leagues['0']['league'][0]['league_key']
            print(f"Found League ID: {league_id}")
            return league_id
        print("Error: No leagues found for the user in this game.")
        return None
    except Exception as e:
        print(f"An error occurred while fetching the league ID: {e}")
        return None

def get_stat_categories(api, league_id):
    """Fetches the mapping of stat_id to human-readable names."""
    print("Fetching stat categories...")
    try:
        response = api.get(f"league/{league_id}/settings")
        settings = response['fantasy_content']['league'][1]['settings'][0]
        stat_info = settings['stat_categories']['stats']
        stat_map = {str(stat['stat']['stat_id']): stat['stat']['display_name'] for stat in stat_info}
        print(f"Successfully fetched {len(stat_map)} stat categories.")
        return stat_map
    except Exception as e:
        print(f"An error occurred while fetching stat categories: {e}")
        return {}

def get_all_player_data(api, league_id, stat_map):
    """Fetches all players, their basic info, and their stats from a given league."""
    all_players_data = []
    start = 0
    count = 25

    while True:
        try:
            print(f"Fetching players from index {start} (with stats)...")
            response = api.get(f"league/{league_id}/players;start={start};count={count};sort=AR;out=stats")
            players_list = response['fantasy_content']['league'][1]['players']
            if not players_list or players_list['count'] == 0:
                print("No more players found.")
                break

            for i in range(players_list['count']):
                player_container = players_list[str(i)]['player']
                
                player_info = {}
                basic_info_list = player_container[0]
                stats_info_list = player_container[1]

                # Process basic info
                for item in basic_info_list:
                    if isinstance(item, dict):
                        for key, value in item.items():
                            if key == 'name': # The name dict is nested
                                player_info['full_name'] = value['full']
                            else:
                                player_info[key] = value
                
                # Process stats
                if 'player_stats' in stats_info_list:
                    stats_list = stats_info_list['player_stats']['stats']
                    for stat_item in stats_list:
                        stat_id = str(stat_item['stat']['stat_id'])
                        stat_value = stat_item['stat']['value']
                        stat_name = stat_map.get(stat_id, f"stat_{stat_id}")
                        player_info[stat_name] = stat_value

                all_players_data.append(player_info)

            start += count

        except Exception as e:
            print(f"An error occurred while fetching players: {e}")
            break
            
    print(f"Total players with stats fetched: {len(all_players_data)}")
    return all_players_data

def main():
    """Main function to run the data fetching and processing."""
    print("Starting Yahoo Fantasy API script for NBA 2024-2025...")
    api = YahooAPI()

    game_id = get_game_id(api, year=2024)
    if not game_id: return

    league_id = get_league_id(api, game_id)
    if not league_id: return

    stat_map = get_stat_categories(api, league_id)
    if not stat_map: return

    players_data = get_all_player_data(api, league_id, stat_map)
    if not players_data: 
        print("No players data to process.")
        return

    try:
        df = pd.DataFrame(players_data)
        # Reorder columns to have basic info first
        basic_cols = ['player_key', 'full_name', 'editorial_team_abbr', 'display_position']
        stat_cols = [col for col in df.columns if col not in basic_cols]
        ordered_cols = [col for col in basic_cols if col in df.columns] + sorted(stat_cols)
        df = df[ordered_cols]

        output_path = "data/nba_player_stats_2025.csv"
        df.to_csv(output_path, index=False)
        print(f"Successfully saved player data with stats to {output_path}")
    except Exception as e:
        print(f"Failed to save data to CSV: {e}")

if __name__ == "__main__":
    main()
