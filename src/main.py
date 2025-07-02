"""
Main entry point for the Yahoo Fantasy MLB application.

This script initializes the API handler and retrieves user's fantasy leagues.
"""

from api_handler import YahooApiHandler

def main():
    """
    Main function to run the application.
    """
    try:
        api = YahooApiHandler()
        leagues = api.get_user_leagues()
        print("Available Leagues:")
        # Simplified parsing for demonstration
        for league in leagues['fantasy_content']['users']['0']['user'][1]['games']['0']['game'][1]['leagues']:
            if 'league' in league:
                league_info = league['league'][0]
                print(f"  - {league_info['name']} (ID: {league_info['league_id']})")

    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Please ensure your 'config/config.yaml' is set up correctly.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()