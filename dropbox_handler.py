import streamlit as st
import dropbox
import requests
import json

def refresh_access_token():
    """Refreshes and returns a new Dropbox access token."""
    url = "https://api.dropbox.com/oauth2/token"
    data = {
        "grant_type": "refresh_token",
        "refresh_token": st.secrets["dropbox"]["refresh_token"],
        "client_id": st.secrets["dropbox"]["app_key"],
        "client_secret": st.secrets["dropbox"]["app_secret"]
    }

    response = requests.post(url, data=data)
    
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        st.error("Failed to refresh Dropbox access token. Please check your credentials.")
        return None

def authenticate_dropbox():
    """Authenticate Dropbox using a valid access token, refreshing if needed."""
    access_token = refresh_access_token()
    
    if access_token:
        return dropbox.Dropbox(access_token)
    return None

def upload_teams(teams):
    """Uploads teams.json to Dropbox."""
    try:
        dbx = authenticate_dropbox()
        if dbx is None:
            return  # Prevent upload if authentication failed

        file_path = "/teams.json"
        json_data = json.dumps(teams, indent=4)

        dbx.files_upload(json_data.encode(), file_path, mode=dropbox.files.WriteMode("overwrite"))
    except dropbox.exceptions.AuthError:
        st.warning("Dropbox authentication failed. Attempting token refresh...")
        dbx = authenticate_dropbox()
        if dbx:
            upload_teams(teams)  # Retry the upload

def load_teams():
    """Retrieves teams.json from Dropbox."""
    try:
        dbx = authenticate_dropbox()
        if dbx is None:
            return {}  # Prevent crash if authentication failed

        file_path = "/teams.json"
        metadata, res = dbx.files_download(file_path)
        teams = json.loads(res.content.decode("utf-8"))
        return teams
    except dropbox.exceptions.AuthError:
        st.warning("Dropbox authentication failed. Attempting token refresh...")
        dbx = authenticate_dropbox()
        if dbx:
            return load_teams()  # Retry loading teams
        return {}
