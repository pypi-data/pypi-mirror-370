import json
import os
import time
import requests


def get_authorization_url(credentials_path, redirect_uri, scopes, log):
    """
    Build the Google OAuth authorization URL using the provided credentials file, redirect URI, and scopes.
    """
    with open(credentials_path, 'r') as credentials_file:
        credentials = json.load(credentials_file)
    client_id = credentials['web']['client_id']
    auth_url = (
        "https://accounts.google.com/o/oauth2/v2/auth?"
        "response_type=code&"
        "client_id={}&"
        "redirect_uri={}&"
        "scope={}&"
        "access_type=offline&"
        "prompt=consent"
    ).format(client_id, redirect_uri, scopes)
    log("Generated authorization URL: {}".format(auth_url))
    return auth_url


def exchange_code_for_token(auth_code, credentials_path, redirect_uri, log, retries=3):
    """
    Exchange an authorization code for tokens using credentials; retries a few times on failure.
    """
    for attempt in range(retries):
        try:
            with open(credentials_path, 'r') as credentials_file:
                credentials = json.load(credentials_file)
            token_url = "https://oauth2.googleapis.com/token"
            data = {
                'code': auth_code,
                'client_id': credentials['web']['client_id'],
                'client_secret': credentials['web']['client_secret'],
                'redirect_uri': redirect_uri,
                'grant_type': 'authorization_code'
            }
            response = requests.post(token_url, data=data)
            log("Token exchange response: Status code {}, Body: {}".format(response.status_code, response.text))
            token_response = response.json()
            if response.status_code == 200:
                token_response['token_time'] = time.time()
                return token_response
            else:
                log("Token exchange failed: {}".format(token_response))
                if attempt < retries - 1:
                    log("Retrying token exchange... (Attempt {}/{})".format(attempt + 1, retries))
        except Exception as e:
            log("Error during token exchange: {}".format(e))
    return {}


def refresh_access_token(refresh_token, credentials_path, log):
    """
    Refresh an access token using the stored client credentials.
    """
    log("Refreshing access token.")
    with open(credentials_path, 'r') as credentials_file:
        credentials = json.load(credentials_file)
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        'client_id': credentials['web']['client_id'],
        'client_secret': credentials['web']['client_secret'],
        'refresh_token': refresh_token,
        'grant_type': 'refresh_token'
    }
    response = requests.post(token_url, data=data)
    log("Refresh token response: Status code {}, Body:\n {}".format(response.status_code, response.text))
    if response.status_code == 200:
        log("Access token refreshed successfully.")
        return response.json()
    else:
        log("Failed to refresh access token. Status code: {}".format(response.status_code))
        return {}


def is_valid_authorization_code(auth_code, log):
    """
    Validate auth code shape without side effects.
    """
    if auth_code and isinstance(auth_code, str) and len(auth_code) > 0:
        return True
    log("Invalid authorization code format: {}".format(auth_code))
    return False


def clear_token_cache(token_path, log):
    """
    Delete token cache file if present.
    """
    if os.path.exists(token_path):
        os.remove(token_path)
        log("Cleared token cache.")