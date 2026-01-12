import streamlit as st
import pandas as pd
from scipy.stats import poisson

# Page configuration
st.set_page_config(
    page_title="Kay's Super Predictor",
    page_icon="⚽",
    layout="centered"
)

st.title("⚽ Kay's Super Predictor")

# Caching the data load for performance
@st.cache_data
def load_data():
    try:
        # Load the dataset
        df = pd.read_csv('E0.csv')
        # Ensure we have the necessary columns
        required_columns = ['Date', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG']
        if not all(col in df.columns for col in required_columns):
            st.error(f"Error: Missing required columns. Expected: {required_columns}")
            return pd.DataFrame()
        return df
    except FileNotFoundError:
        st.error("Error: 'E0.csv' data file not found. Please ensure the file exists in the directory.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"An unexpected error occurred loading data: {e}")
        return pd.DataFrame()

df = load_data()

if df.empty:
    st.warning("Data not available. Please check the data source.")
    st.stop()

# sort teams for better UX
teams = sorted(df['HomeTeam'].unique())

col1, col2 = st.columns(2)
with col1:
    home_team = st.selectbox("Select Home Team", teams, index=0)
with col2:
    # Try to select a different team by default if possible
    default_away_index = 1 if len(teams) > 1 else 0
    away_team = st.selectbox("Select Away Team", teams, index=default_away_index)

# Initialize session state for storing predictions
if 'prediction_made' not in st.session_state:
    st.session_state.prediction_made = False
    st.session_state.home_win_prob = 0.0
    st.session_state.draw_prob = 0.0
    st.session_state.away_win_prob = 0.0
    st.session_state.home_exp = 0.0
    st.session_state.away_exp = 0.0

if st.button("Calculate Prediction", type="primary"):
    if home_team == away_team:
        st.warning("Please select two different teams.")
    else:
        # Calculate goal expectancy
        # Using a simple average of historical performance against all teams
        # A more robust model would separate Home stats vs Away stats specifically
        home_exp = df[df['HomeTeam'] == home_team]['FTHG'].mean()
        away_exp = df[df['AwayTeam'] == away_team]['FTAG'].mean()
        
        # Handle cases where teams might not have data (e.g. new teams)
        if pd.isna(home_exp) or pd.isna(away_exp):
            st.error("Insufficient data to calculate predictions for one or both teams.")
        else:
            # Calculate Win/Draw/Loss Probabilities using Poisson distribution
            home_win_prob, draw_prob, away_win_prob = 0, 0, 0
            
            for i in range(10): # Max 9 goals modeled
                for j in range(10):
                    prob = poisson.pmf(i, home_exp) * poisson.pmf(j, away_exp)
                    if i > j: home_win_prob += prob
                    elif i == j: draw_prob += prob
                    else: away_win_prob += prob
            
            # Update session state
            st.session_state.home_win_prob = home_win_prob
            st.session_state.draw_prob = draw_prob
            st.session_state.away_win_prob = away_win_prob
            st.session_state.home_exp = home_exp
            st.session_state.away_exp = away_exp
            st.session_state.prediction_made = True

# Display Prediction Results
if st.session_state.prediction_made:
    st.divider()
    st.subheader("Match Outcome Probability")
    
    # Display metrics
    m_col1, m_col2, m_col3 = st.columns(3)
    m_col1.metric(f"{home_team} Win", f"{st.session_state.home_win_prob:.1%}")
    m_col2.metric("Draw", f"{st.session_state.draw_prob:.1%}")
    m_col3.metric(f"{away_team} Win", f"{st.session_state.away_win_prob:.1%}")
    
    # Visual Progress Bars
    st.caption("Probability Distribution")
    st.progress(st.session_state.home_win_prob, text=f"{home_team} Win Chance")
    st.progress(st.session_state.draw_prob, text="Draw Chance")
    st.progress(st.session_state.away_win_prob, text=f"{away_team} Win Chance")

st.divider()
st.subheader("📊 Recent Form & Head-to-Head")

tab1, tab2 = st.tabs([f"{home_team} Recent Games", f"{away_team} Recent Games"])

with tab1:
    # Filter for games where the selected home team played
    home_recent = df[(df['HomeTeam'] == home_team) | (df['AwayTeam'] == home_team)].tail(5)
    if not home_recent.empty:
        st.dataframe(home_recent[['Date', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG']], use_container_width=True, hide_index=True)
    else:
        st.info("No recent games found available.")

with tab2:
    # Filter for games where the selected away team played
    away_recent = df[(df['HomeTeam'] == away_team) | (df['AwayTeam'] == away_team)].tail(5)
    if not away_recent.empty:
        st.dataframe(away_recent[['Date', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG']], use_container_width=True, hide_index=True)
    else:
        st.info("No recent games found available.")