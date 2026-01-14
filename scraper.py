import os
import requests
import pandas as pd
import time
from datetime import datetime, timedelta

# API Configuration
try:
    import streamlit as st
    API_TOKEN = os.getenv('FOOTBALL_DATA_API_TOKEN') or st.secrets.get("FOOTBALL_DATA_API_TOKEN")
except:
    API_TOKEN = os.getenv('FOOTBALL_DATA_API_TOKEN')

BASE_URL = "https://api.football-data.org/v4/"
HEADERS = {'X-Auth-Token': API_TOKEN}

# Competition IDs
COMPETITIONS = ['PL', 'BL1', 'PD', 'SA', 'FL1', 'CL']

def make_request(url):
    """Makes an API request with basic error handling and rate limiting check."""
    for _ in range(3):  # Simple retry logic
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 429:
            print("Rate limit reached. Waiting 60 seconds...")
            time.sleep(60)
        else:
            print(f"Error {response.status_code}: {response.text}")
            return None
    return None

def get_historical_data(competition):
    """Fetches historical match data for a competition to calculate 'Over 1.5' rates."""
    url = f"{BASE_URL}competitions/{competition}/matches?status=FINISHED"
    data = make_request(url)
    if not data:
        return []
    return data.get('matches', [])

def get_fixtures(competition):
    """Fetches upcoming fixtures for a competition."""
    url = f"{BASE_URL}competitions/{competition}/matches?status=SCHEDULED"
    data = make_request(url)
    if not data:
        return []
    return data.get('matches', [])

def calculate_over15_rate(matches, team_name):
    """Calculates the percentage of matches involving a team that had over 1.5 goals."""
    relevant_matches = [
        m for m in matches 
        if m['homeTeam']['name'] == team_name or m['awayTeam']['name'] == team_name
    ]
    if not relevant_matches:
        return 0.5  # Default to 50% if no data
    
    over15_count = 0
    for m in relevant_matches:
        score = m['score']['fullTime']
        if score['home'] is not None and score['away'] is not None:
            if (score['home'] + score['away']) >= 2:
                over15_count += 1
    
    return over15_count / len(relevant_matches)

def run_scraper():
    if not API_TOKEN:
        print("Error: FOOTBALL_DATA_API_TOKEN not found.")
        return

    all_data = []
    
    # Dates for result fetching
    today_dt = datetime.now()
    yesterday_str = (today_dt - timedelta(days=1)).strftime('%Y-%m-%d')
    tomorrow_plus_2 = (today_dt + timedelta(days=2)).strftime('%Y-%m-%d')
    
    for comp in COMPETITIONS:
        print(f"Processing {comp}...")
        historical = get_historical_data(comp)
        
        # 1. Fetch recently finished matches (past 2 days) to show results
        url_results = f"{BASE_URL}competitions/{comp}/matches?status=FINISHED&dateFrom={yesterday_str}&dateTo={today_dt.strftime('%Y-%m-%d')}"
        recent_results = make_request(url_results)
        if recent_results:
            for match in recent_results.get('matches', []):
                all_data.append({
                    'Date': match['utcDate'].split('T')[0],
                    'League': match['competition']['name'],
                    'HomeTeam': match['homeTeam']['name'],
                    'AwayTeam': match['awayTeam']['name'],
                    'Time': match['utcDate'].split('T')[1][:5],
                    'Over15_Rate_Home': round(calculate_over15_rate(historical, match['homeTeam']['name']), 2),
                    'Over15_Rate_Away': round(calculate_over15_rate(historical, match['awayTeam']['name']), 2),
                    'Model_Prob': 0, # Prob 0 for finished matches
                    'HomeScore': match['score']['fullTime']['home'],
                    'AwayScore': match['score']['fullTime']['away']
                })

        # 2. Fetch scheduled matches
        fixtures = get_fixtures(comp)
        for fixture in fixtures:
            home_team = fixture['homeTeam']['name']
            away_team = fixture['awayTeam']['name']
            match_date = fixture['utcDate'].split('T')[0]
            match_time = fixture['utcDate'].split('T')[1][:5]
            
            # Simple check to only predict for next 3 days
            date_obj = datetime.strptime(match_date, '%Y-%m-%d')
            if date_obj > today_dt + timedelta(days=3):
                continue
                
            rate_home = calculate_over15_rate(historical, home_team)
            rate_away = calculate_over15_rate(historical, away_team)
            
            # Combined internal probability
            model_prob = (rate_home + rate_away) / 2
            
            all_data.append({
                'Date': match_date,
                'League': fixture['competition']['name'],
                'HomeTeam': home_team,
                'AwayTeam': away_team,
                'Time': match_time,
                'Over15_Rate_Home': round(rate_home, 2),
                'Over15_Rate_Away': round(rate_away, 2),
                'Model_Prob': round(model_prob, 2),
                'HomeScore': '', 
                'AwayScore': ''
            })
            
    # Save to CSV
    if all_data:
        df = pd.DataFrame(all_data)
        # Drop duplicates if any (e.g., if a match transitioned status during run)
        df = df.drop_duplicates(subset=['Date', 'HomeTeam', 'AwayTeam'])
        df.to_csv('predictions.csv', index=False)
        print(f"Scraper finished. Saved {len(all_data)} entries.")
    else:
        print("No data fetched.")

if __name__ == "__main__":
    run_scraper()
