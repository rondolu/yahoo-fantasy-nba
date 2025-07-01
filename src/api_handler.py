import os
import json
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import BackendApplicationClient
from dotenv import load_dotenv

load_dotenv()

class YahooAPI:
    def __init__(self):
        self.client_id = os.getenv("CLIENT_ID")
        self.client_secret = os.getenv("CLIENT_SECRET")
        self.redirect_uri = "oob"  # Out-of-band for installed apps
        self.token_url = "https://api.login.yahoo.com/oauth2/get_token"
        self.authorization_url = "https://api.login.yahoo.com/oauth2/request_auth"
        self.base_api_url = "https://fantasysports.yahooapis.com/fantasy/v2"
        self.token_file = "yahoo_token.json"
        self.session = self._get_session()

    def _save_token(self, token):
        with open(self.token_file, "w") as f:
            json.dump(token, f)

    def _load_token(self):
        try:
            with open(self.token_file, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return None

    def _get_session(self):
        token = self._load_token()
        if token:
            return OAuth2Session(
                self.client_id,
                token=token,
                auto_refresh_url=self.token_url,
                auto_refresh_kwargs={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                },
                token_updater=self._save_token,
            )

        # If no token, start the authorization flow
        oauth = OAuth2Session(
            self.client_id, redirect_uri=self.redirect_uri
        )
        authorization_url, state = oauth.authorization_url(self.authorization_url)

        print(f"Please go to this URL and authorize the application:\n{authorization_url}")
        authorization_code = input("Enter the authorization code: ")

        token = oauth.fetch_token(
            self.token_url,
            code=authorization_code,
            client_secret=self.client_secret,
        )
        self._save_token(token)
        return oauth

    def get(self, url):
        response = self.session.get(f"{self.base_api_url}/{url}?format=json")
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.json()
