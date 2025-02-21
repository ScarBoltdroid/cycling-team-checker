import streamlit as st
import json
import hashlib
import pandas as pd
from procyclingstats import RaceStartlist
from dropbox_handler import load_teams, upload_teams
import sys
sys.stdout.reconfigure(encoding='utf-8')

# --- Load Teams ---
def save_teams(updated_teams):
    upload_teams(updated_teams)

teams = load_teams()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

teams = load_teams()

# --- Load Races ---
def load_races():
    with open("races.json", "r") as file:
        return json.load(file)

races = load_races()

# --- Load All Riders ---
def load_all_riders():
    with open("allriders.json", "r") as file:
        return json.load(file)

all_riders_dict = load_all_riders()
all_riders_names = list(all_riders_dict.keys())

apps = ['Choose option', 'Do my cyclists ride?', 'Create a team', 'Update a team', 'Races to riders[experimental]']

st.title('Cycling Apps')
chosenApp = st.selectbox('Select option', apps)
st.markdown("***")

match chosenApp:
    case 'Do my cyclists ride?':
        team = st.text_input("Enter your team name:")
        password = st.text_input("Enter team password:", type="password")
        race = st.selectbox("Race:", list(races.keys()))
        
        if st.button("Go!"):
            if team in teams and teams[team]['password'] == hash_password(password):
                ploeg = teams[team]['riders']
                url = races[race]
                startlist = RaceStartlist(url)
                sl = startlist.startlist()
                active = [start['rider_name'] for start in sl if start['rider_url'] in ploeg]
                
                if active:
                    st.success(f'You have {len(active)} riders in this race\n{active}')
                else:
                    st.error('No riders in this race')
            else:
                st.error("Incorrect password or team not found.")
    
    case 'Create a team':
        new_team_name = st.text_input("Enter team name:")
        new_password = st.text_input("Set a password:", type="password")
        selected_riders_names = st.multiselect("Select up to 20 riders:", all_riders_names, max_selections=20)
        selected_riders_urls = [all_riders_dict[name] for name in selected_riders_names]
        
        if st.button("Save Team"):
            if new_team_name and new_password and selected_riders_urls:
                if new_team_name in teams:
                    st.error("Team name already exists. Choose a different name.")
                else:
                    teams[new_team_name] = {"password": hash_password(new_password), "riders": selected_riders_urls}
                    save_teams(teams)
                    st.success("Team created successfully!")
            else:
                st.error("Please fill in all fields.")
    
    case 'Update a team':
        team = st.text_input("Enter your team name:")
        password = st.text_input("Enter team password:", type="password")
        
        if st.button("Unlock Team"):
            if team in teams and teams[team]['password'] == hash_password(password):
                st.session_state["authenticated"] = True
                st.session_state["selected_team"] = team
            else:
                st.error("Incorrect password.")
        
        if "authenticated" in st.session_state and st.session_state["selected_team"] == team:
            st.markdown("### Update Team")
            current_riders_urls = teams[team]['riders']
            current_riders_names = [name for name, url in all_riders_dict.items() if url in current_riders_urls]
            selected_riders_names = st.multiselect("Update your team (Max 20 riders):", all_riders_names, default=current_riders_names, max_selections=20)
            selected_riders_urls = [all_riders_dict[name] for name in selected_riders_names]
            
            if st.button("Save Changes"):
                teams[team]['riders'] = selected_riders_urls
                save_teams(teams)
                st.success("Team updated successfully!")
    case 'Races to riders[experimental]':
        st.write('This feature is not yet optimized and might take a long time to load.\nProceed with caution!')
        selection = st.pills('Select races:', list(races.keys()), selection_mode='multi')
        if st.button('Go!'):
            race_startlists = {}  # Store pre-processed startlists
            for race in selection:
                url = races[race]
                startlist = RaceStartlist(url).startlist()  # Fetch and parse once
                race_startlists[race] = {rider['rider_url'] for rider in startlist} #create a set of rider_urls

            does_all = list(all_riders_dict.keys())  # Start with all riders

            for race in selection:
                rider_urls_in_race = race_startlists[race]
                riders_to_remove = []
                for rider in does_all:
                    if all_riders_dict[rider] not in rider_urls_in_race:
                        riders_to_remove.append(rider)
                for rider in riders_to_remove:
                    does_all.remove(rider)

                if not does_all: #if no riders remain, break
                    break

            if len(does_all) > 0:
                st.success(f'These riders do all races\n{does_all}')
            else:
                st.error('No rider does all races')
