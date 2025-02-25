import streamlit as st
import dropbox
import requests
import json
import time

# Store token expiration time in session state
if "dropbox_token_expiry" not in st.session_state:
    st.session_state["dropbox_token_expiry"] = 0

def refresh_access_token():
    """Requests a new access token using the refresh token."""
    url = "https://api.dropbox.com/oauth2/token"
    data = {
        "grant_type": "refresh_token",
        "refresh_token": st.secrets["dropbox"]["refresh_token"],
        "client_id": st.secrets["dropbox"]["app_key"],
        "client_secret": st.secrets["dropbox"]["app_secret"]
    }

    response = requests.post(url, data=data)
    
    if response.status_code == 200:
        new_token = response.json()["access_token"]
        
        # Update the session state with the new token and expiration time
        st.session_state["dropbox_access_token"] = new_token
        st.session_state["dropbox_token_expiry"] = time.time() + 14400  # Token lasts 4 hours
        
        return new_token
    else:
        st.error("Failed to refresh Dropbox access token. Please check your credentials.")
        return None

def get_access_token():
    """Ensures that the access token is valid before returning it."""
    if (
        "dropbox_access_token" not in st.session_state or 
        time.time() >= st.session_state["dropbox_token_expiry"]
    ):
        return refresh_access_token()
    
    return st.session_state["dropbox_access_token"]

def authenticate_dropbox():
    """Authenticate Dropbox with an up-to-date access token."""
    access_token = get_access_token()
    if access_token:
        return dropbox.Dropbox(access_token)
    return None

dbx = authenticate_dropbox()

def upload_teams(teams):
    """Uploads teams.json to Dropbox."""
    if dbx is None:
        return  # Prevent upload if authentication failed

    file_path = "/teams.json"
    json_data = json.dumps(teams, indent=4)

    dbx.files_upload(json_data.encode(), file_path, mode=dropbox.files.WriteMode("overwrite"))

def load_teams():
    """Retrieves teams.json from Dropbox."""
    if dbx is None:
        return {}  # Prevent crash if authentication failed

    file_path = "/teams.json"

    try:
        metadata, res = dbx.files_download(file_path)
        teams = json.loads(res.content.decode("utf-8"))
        return teams
    except dropbox.exceptions.ApiError:
        return {}  # Return an empty dictionary if file doesn't exist
