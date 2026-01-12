# ⚽ Kay's Super Predictor

A professional football outcome prediction dashboard built with Streamlit, specializing in "Over 1.5 Goals" probabilities.

## 🌟 Features

-   **Daily Top 3 Picks**: High-confidence recommendations (>80% Historical Rate, >85% Model Probability).
-   **Match Calculator**: Interactive tool to calculate probabilities for any match-up.
-   **Midnight & Neon Theme**: Premium dark mode UI (#0e1117) with high-contrast neon accents.
-   **Automated Updates**: Powered by GitHub Actions to refresh data daily at 06:00 UTC.

## 🚀 Quick Start

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Simplykay/kays-Super-Predictor.git
    cd kays-Super-Predictor
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the application:**
    ```bash
    streamlit run App.py
    ```

## ☁️ Deploying to Streamlit Community Cloud

This project is optimized for direct deployment from GitHub.

1.  **Push to GitHub**: Ensure your code is pushed to your GitHub repository.
2.  **Sign in**: Go to [share.streamlit.io](https://share.streamlit.io/) and sign in with GitHub.
3.  **New App**: Click **"New app"**.
4.  **Configuration**:
    -   **Repository**: Select `Simplykay/kays-Super-Predictor`
    -   **Branch**: `main`
    -   **Main file path**: `App.py`
5.  **Deploy**: Click **"Deploy!"**.

### Secrets (Optional)
If your `scraper.py` requires API keys, set them in the Streamlit Cloud dashboard:
-   Go to App Settings -> **Secrets**.
-   Add your keys in TOML format (e.g., `API_KEY = "your-key-here"`).

## 🤖 Automation

The project includes a GitHub Actions workflow (`.github/workflows/daily_scan.yml`) that:
1.  Runs daily at 06:00 UTC.
2.  Executes `scraper.py` to fetch fresh match data.
3.  Updates `predictions.csv` and auto-commits the changes.

## 📂 Project Structure

-   `App.py`: Main Streamlit application.
-   `scraper.py`: Data scraping script (runs in CI/CD).
-   `predictions.csv`: Daily generated data file.
-   `requirements.txt`: Python package dependencies.
