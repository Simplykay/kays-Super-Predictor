import streamlit as st
import pandas as pd
from scipy.stats import poisson
import datetime
import os

# Page configuration
st.set_page_config(
    page_title="Kay's Super Predictor",
    page_icon="⚽",
    layout="wide", # Changed to wide for better dashboard view
    initial_sidebar_state="expanded"
)

# Custom CSS for Midnight Black & Neon Green Theme
st.markdown("""
<style>
    /* Main Background */
    .stApp {
        background-color: #0e1117;
        color: #e0e0e0;
    }
    
    /* Headings */
    h1, h2, h3 {
        color: #00ff41 !important; /* Neon Green */
        font-family: 'Segoe UI', sans-serif;
    }
    
    /* Cards for Top Picks */
    .pick-card {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        transition: transform 0.2s;
    }
    .pick-card:hover {
        transform: translateY(-2px);
        border-color: #00ff41;
    }
    
    /* Metrics */
    .metric-value {
        font-size: 1.5rem;
        font-weight: bold;
        color: #00ff41;
    }
    
    /* Buttons */
    .stButton>button {
        color: #0e1117;
        background-color: #00ff41;
        border: none;
        border-radius: 5px;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #00cc33;
        color: #fff;
    }
    
    /* Selectbox */
    .stSelectbox label {
        color: #00ff41;
    }
    
    /* Divider */
    hr {
        border-color: #30363d;
    }
    
    /* Progress Bar */
    .stProgress > div > div > div > div {
        background-color: #00ff41;
    }
    
    /* Mobile Optimization */
    @media (max-width: 768px) {
        .pick-card {
            margin-bottom: 20px;
        }
    }
</style>
""", unsafe_allow_html=True)

# Logo and Title Layout
l_col1, l_col2 = st.columns([1, 4])
with l_col1:
    try:
        st.image("logo.png", width=100)
    except:
        st.write("⚽") # Fallback
with l_col2:
    st.title("Kay's Super Predictor")
    st.caption("AI-Powered Over 1.5 Goals Forecasting")

# --- Top 3 Picks Dashboard Logic ---

@st.cache_data(ttl=300)
def load_predictions(mtime):
    try:
        df = pd.read_csv('predictions.csv')
        # Ensure correct types
        df['Date'] = pd.to_datetime(df['Date'])
        # Ensure Score columns are numeric or handle them as objects
        df['HomeScore'] = pd.to_numeric(df['HomeScore'], errors='coerce')
        df['AwayScore'] = pd.to_numeric(df['AwayScore'], errors='coerce')
        return df
    except FileNotFoundError:
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error loading predictions: {e}")
        return pd.DataFrame()

def get_top_picks(df):
    if df.empty:
        return pd.DataFrame()
    
    # Filter criteria
    # 1. Historical Over 1.5 rate > 70% (0.70) for both teams
    stats_mask = (df['Over15_Rate_Home'] >= 0.70) & (df['Over15_Rate_Away'] >= 0.70)
    
    # 2. Model internal probability >= 70% (0.70)
    prob_mask = df['Model_Prob'] >= 0.70
    
    filtered_df = df[stats_mask & prob_mask].copy()
    
    # Sort by confidence descending and take top 3
    top_picks = filtered_df.sort_values(by='Model_Prob', ascending=False).head(3)
    return top_picks

# Display Dashboard
st.header("🔥 Daily Top 3 Picks")

# Get file modification time to force cache refresh when file changes
try:
    predictions_mtime = os.path.getmtime('predictions.csv')
except:
    predictions_mtime = 0

picks_df = load_predictions(predictions_mtime)

# Get Today's Date (Simulated as Jan 13 2026 if needed, but using real system time is safer if user is strictly 2026. 
# However, user wants "new days pick at exactly midnight".
# We will use pd.Timestamp.now().normalize() for robustness.)
today = pd.Timestamp.now().normalize()

# Filter for today
todays_games = picks_df[picks_df['Date'] == today]
top_picks = get_top_picks(todays_games)

if top_picks.empty:
    st.info(f"No high-confidence picks available for today ({today.strftime('%d %b %Y')}). Check back later!")
else:
    cols = st.columns(3)
    for index, (col, row) in enumerate(zip(cols, top_picks.iterrows())):
        row_data = row[1]
        with col:
            # Format date: "Mon 20 May 2024"
            match_date = row_data['Date'].strftime('%a %d %b %Y')
            
            st.markdown(f"""
            <div class="pick-card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                    <span style="color: #8b949e; font-size: 0.9em;">{row_data['League']}</span>
                    <span style="background-color: rgba(0, 255, 65, 0.1); color: #00ff41; padding: 2px 8px; border-radius: 12px; font-size: 0.8em; border: 1px solid #00ff41;">
                        {int(row_data['Model_Prob']*100)}% Conf.
                    </span>
                </div>
                <h3 style="margin: 0; font-size: 1.2em; color: white !important;">{row_data['HomeTeam']}</h3>
                <div style="text-align: center; color: #8b949e; margin: 5px 0;">vs</div>
                <h3 style="margin: 0; font-size: 1.2em; color: white !important;">{row_data['AwayTeam']}</h3>
                <div style="margin-top: 15px; display: flex; justify-content: space-between; align-items: flex-end;">
                    <div style="display: flex; flex-direction: column;">
                        <span style="color: #00ff41; font-weight: bold;">Over 1.5 Goals</span>
                        <span style="color: #8b949e; font-size: 0.8em;">📅 {match_date}</span>
                    </div>
                    <span style="color: #8b949e;">🕒 {row_data['Time']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)


st.markdown("---")
# --- Previous Day's Results ---
st.header("📉 Yesterday's Results")
yesterday = today - pd.Timedelta(days=1)
yesterdays_games = picks_df[picks_df['Date'] == yesterday]

if yesterdays_games.empty:
    st.info(f"No results found for yesterday ({yesterday.strftime('%d %b %Y')}).")
else:
    # We display these in a smaller format or a simple table
    for _, result in yesterdays_games.iterrows():
        # Check if score exists in CSV
        h_score = result.get('HomeScore')
        a_score = result.get('AwayScore')
        
        has_score = not pd.isna(h_score) and not pd.isna(a_score)
        
        h_score_disp = int(h_score) if has_score else "-"
        a_score_disp = int(a_score) if has_score else "-"
        
        status = "✅" if (has_score and (h_score + a_score) >= 2) else "❌" if has_score else "⏳"
        
        st.markdown(f"""
        <div style="background-color: #161b22; padding: 10px; border-radius: 8px; margin-bottom: 8px; border-left: 5px solid {'#00ff41' if status == '✅' else '#ff4d4d' if status == '❌' else '#8b949e'};">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="color: #8b949e; font-size: 0.9em;">{result['League']}</span>
                <span style="font-weight: bold; color: {'#00ff41' if status == '✅' else '#ff4d4d' if status == '❌' else 'white'};">{status} Over 1.5</span>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 5px;">
                <span style="font-size: 1.1em; flex: 1; text-align: right; padding-right: 15px;">{result['HomeTeam']}</span>
                <span style="background-color: #0e1117; padding: 2px 10px; border-radius: 4px; font-weight: bold; font-family: monospace; font-size: 1.2em;">{h_score_disp} - {a_score_disp}</span>
                <span style="font-size: 1.1em; flex: 1; text-align: left; padding-left: 15px;">{result['AwayTeam']}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")
st.header("🧮 Match Calculator")

# --- Existing Calculator Logic ---

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

if not df.empty:
    # sort teams for better UX
    teams = sorted(df['HomeTeam'].unique())
    
    # Use columns for layout
    c1, c2 = st.columns(2)
    with c1:
        home_team = st.selectbox("Select Home Team", teams, index=0)
    
    # Filter out the selected home team from the away team options
    away_teams_options = [team for team in teams if team != home_team]
    
    with c2:
        away_team = st.selectbox("Select Away Team", away_teams_options, index=0)

    # Initialize session state for storing predictions
    if 'prediction_made' not in st.session_state:
        st.session_state.prediction_made = False
        st.session_state.home_win_prob = 0.0
        st.session_state.draw_prob = 0.0
        st.session_state.away_win_prob = 0.0
        st.session_state.home_exp = 0.0
        st.session_state.away_exp = 0.0

    if st.button("Calculate Prediction", type="primary"):
        # Calculate goal expectancy
        home_exp = df[df['HomeTeam'] == home_team]['FTHG'].mean()
        away_exp = df[df['AwayTeam'] == away_team]['FTAG'].mean()
        
        if pd.isna(home_exp) or pd.isna(away_exp):
            st.error("Insufficient data to calculate predictions for one or both teams.")
        else:
            # Poisson
            home_win_prob, draw_prob, away_win_prob = 0, 0, 0
            for i in range(10): 
                for j in range(10):
                    prob = poisson.pmf(i, home_exp) * poisson.pmf(j, away_exp)
                    if i > j: home_win_prob += prob
                    elif i == j: draw_prob += prob
                    else: away_win_prob += prob
            
            st.session_state.home_win_prob = home_win_prob
            st.session_state.draw_prob = draw_prob
            st.session_state.away_win_prob = away_win_prob
            st.session_state.prediction_made = True

    # Display Prediction Results
    if st.session_state.prediction_made:
        st.divider()
        st.subheader("Match Outcome Probability")
        
        m_col1, m_col2, m_col3 = st.columns(3)
        m_col1.metric(f"{home_team} Win", f"{st.session_state.home_win_prob:.1%}")
        m_col2.metric("Draw", f"{st.session_state.draw_prob:.1%}")
        m_col3.metric(f"{away_team} Win", f"{st.session_state.away_win_prob:.1%}")
        
        st.caption("Probability Distribution")
        st.progress(st.session_state.home_win_prob, text=f"{home_team} Win Chance")
        st.progress(st.session_state.draw_prob, text="Draw Chance")
        st.progress(st.session_state.away_win_prob, text=f"{away_team} Win Chance")

    st.divider()
    st.subheader("📊 Recent Form")

    # Only show tabs if we have data to avoid errors
    if not df.empty:
        tab1, tab2 = st.tabs([f"{home_team} Recent", f"{away_team} Recent"])

        with tab1:
            home_recent = df[(df['HomeTeam'] == home_team) | (df['AwayTeam'] == home_team)].tail(5)
            if not home_recent.empty:
                st.dataframe(home_recent[['Date', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG']], use_container_width=True, hide_index=True)
            else:
                st.info("No recent games found.")

        with tab2:
            away_recent = df[(df['HomeTeam'] == away_team) | (df['AwayTeam'] == away_team)].tail(5)
            if not away_recent.empty:
                st.dataframe(away_recent[['Date', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG']], use_container_width=True, hide_index=True)
            else:
                st.info("No recent games found.")