"""
Handles all interactions with the Yahoo Fantasy Sports API.

This module provides a class to authenticate with the Yahoo API using OAuth2
and to make requests to various fantasy sports endpoints.
"""

import os
import yaml
from yahoo_oauth import OAuth2

class YahooApiHandler:
    """
A class to handle authentication and requests to the Yahoo Fantasy API.
    """
    def __init__(self, config_path='config/config.yaml'):
        """
        Initializes the YahooApiHandler.

        Args:
            config_path (str): Path to the configuration file.
        """
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Configuration file not found at {config_path}")
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.oauth = self._authenticate()

    def _authenticate(self):
        """
        Authenticates with the Yahoo API using OAuth2.

        Returns:
            OAuth2: An authenticated OAuth2 object.
        """
        oauth = OAuth2(self.config['yahoo_api']['consumer_key'],
                       self.config['yahoo_api']['consumer_secret'])
        if not oauth.token_is_valid():
            oauth.refresh_access_token()
        return oauth

    def get_user_leagues(self):
        """
        Retrieves the user's fantasy baseball leagues.

        Returns:
            dict: A dictionary containing the user's league information.
        """
        url = "https://fantasysports.yahooapis.com/fantasy/v2/users;use_login=1/games;game_keys=mlb/leagues"
        response = self.oauth.session.get(url, params={'format': 'json'})
        response.raise_for_status()
        return response.json()

    def get_league_details(self, league_id):
        """
        Retrieves details for a specific fantasy league.

        Args:
            league_id (str): The ID of the league to retrieve.

        Returns:
            dict: A dictionary containing the league details.
        """
        url = f"https://fantasysports.yahooapis.com/fantasy/v2/league/mlb.l.{league_id}"
        response = self.oauth.session.get(url, params={'format': 'json'})
        response.raise_for_status()
        return response.json()