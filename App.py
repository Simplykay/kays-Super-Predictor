import streamlit as st
import pandas as pd

st.title("⚽ Kay's Super Predictor")

# Load data
df = pd.read_csv('E0.csv')
teams = sorted(df['HomeTeam'].unique())

home_team = st.selectbox("Select Home Team", teams)
away_team = st.selectbox("Select Away Team", teams)

import streamlit as st
import pandas as pd
from scipy.stats import poisson

# ... (your existing data loading code) ...

if st.button("Calculate Prediction"):
    # Calculate expectancy (your existing logic)
    home_exp = df[df['HomeTeam'] == home_team]['FTHG'].mean()
    away_exp = df[df['AwayTeam'] == away_team]['FTAG'].mean()
    
    # Calculate Win/Draw/Loss Probabilities
    home_win, draw, away_win = 0, 0, 0
    
    for i in range(10): # Home goals
        for j in range(10): # Away goals
            prob = poisson.pmf(i, home_exp) * poisson.pmf(j, away_exp)
            if i > j: home_win += prob
            elif i == j: draw += prob
            else: away_win += prob

    # Display professional "Probability Bars"
    st.subheader("Match Outcome Probability")
    col1, col2, col3 = st.columns(3)
    col1.metric(f"{home_team} Win", f"{home_win:.1%}")
    col2.metric("Draw", f"{draw:.1%}")
    col3.metric(f"{away_team} Win", f"{away_win:.1%}")
    
    # Visual Progress Bars
    st.progress(home_win, text="Home Win Probability")
    st.progress(draw, text="Draw Probability")
    st.progress(away_win, text="Away Win Probability")