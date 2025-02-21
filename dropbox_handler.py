import streamlit as st
import dropbox
import json

# Authenticate with Dropbox
def authenticate_dropbox():
    access_token = st.secrets["dropbox"]["access_token"]
    return dropbox.Dropbox(access_token)

dbx = authenticate_dropbox()

# Upload teams.json to Dropbox
def upload_teams(teams):
    """Uploads teams.json to Dropbox."""
    file_path = "/teams.json"
    json_data = json.dumps(teams, indent=4)

    dbx.files_upload(json_data.encode(), file_path, mode=dropbox.files.WriteMode("overwrite"))

# Load teams.json from Dropbox
def load_teams():
    """Retrieves teams.json from Dropbox."""
    file_path = "/teams.json"

    try:
        metadata, res = dbx.files_download(file_path)
        teams = json.loads(res.content.decode("utf-8"))
        return teams
    except dropbox.exceptions.ApiError:
        return {}  # Return an empty dictionary if file doesn't exist
