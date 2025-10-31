import streamlit as st
import pandas as pd
from sklearn.linear_model import LinearRegression
from datetime import datetime
import numpy as np
import os

RESULTS_CSV = "quiz_results.csv"

def predict_future_score(df_user, subject):
    """Predict next score using linear regression on past attempts."""
    df_sub = df_user[df_user["subject"] == subject].copy()
    df_sub = df_sub.sort_values("timestamp").reset_index(drop=True)

    if len(df_sub) < 2:
        return 0, None  # not enough data for regression

    X = np.arange(len(df_sub)).reshape(-1, 1)
    y = df_sub["score"].astype(float).values
    model = LinearRegression()
    model.fit(X, y)

    next_index = np.array([[len(df_sub)]])
    predicted = model.predict(next_index)[0]
    trend = model.coef_[0]  # slope of the line

    return predicted, trend


def calculate_weekly_progress(df_user):
    """Compare average scores in recent vs. past quizzes (based on timestamps)."""
    if "timestamp" not in df_user.columns or df_user.empty:
        return None, None

    df_user["timestamp"] = pd.to_datetime(df_user["timestamp"], errors="coerce")
    df_user = df_user.dropna(subset=["timestamp"])

    if df_user.empty:
        return None, None

    # Split data: recent (last 7 days) vs past
    latest_date = df_user["timestamp"].max()
    cutoff = latest_date - pd.Timedelta(days=7)

    recent = df_user[df_user["timestamp"] >= cutoff]
    past = df_user[df_user["timestamp"] < cutoff]

    if recent.empty or past.empty:
        return None, None

    avg_recent = recent["score"].mean()
    avg_past = past["score"].mean()
    diff = avg_recent - avg_past
    return diff, (avg_recent, avg_past)


def run():
    st.set_page_config(page_title="Knowledge Gap Detector", layout="centered")
    st.title("🧩 Knowledge Gap Detector")
    st.write("Analyze your quiz performance and get personalized recommendations to improve!")

    if not os.path.exists(RESULTS_CSV):
        st.warning(f"⚠️ No quiz results found yet! Please take some quizzes first.")
        return

    df = pd.read_csv(RESULTS_CSV)
    if df.empty:
        st.warning("⚠️ Your results file is empty.")
        return

    # Ensure necessary columns exist
    required_cols = {"timestamp", "user_id", "subject", "score", "total"}
    if not required_cols.issubset(df.columns):
        st.error(f"Results CSV is missing columns: {required_cols - set(df.columns)}")
        return

    user_id = st.text_input("Enter your User ID:")
    if not user_id:
        st.info("Please enter your User ID to view personalized analysis.")
        return

    df_user = df[df["user_id"].astype(str) == str(user_id)]
    if df_user.empty:
        st.warning("No data found for this user yet.")
        return

    # --- Assign attempt numbers for each subject ---
    df_user = df_user.sort_values("timestamp").copy()
    df_user["attempt_no"] = df_user.groupby("subject").cumcount() + 1

    st.subheader(f"📚 Summary for User {user_id}")

    # 🟢 Motivation Tracker — based on weekly progress
    diff, averages = calculate_weekly_progress(df_user)
    if diff is not None:
        avg_recent, avg_past = averages
        if diff > 0:
            st.success(f"👏 Great job! Your average score improved by +{diff:.1f} since last week! "
                       f"(Now {avg_recent:.1f} vs {avg_past:.1f})")
        elif diff < 0:
            st.warning(f"😌 Slight dip detected — your average score dropped by {abs(diff):.1f} since last week. "
                       f"Try revising weaker topics to recover.")
        else:
            st.info(f"📈 Your performance is stable this week. Keep up your consistency!")
    else:
        st.info("📊 Not enough data yet for weekly trend analysis — complete more quizzes to track progress!")

    # --- Analyze each subject ---
    subjects = df_user["subject"].unique()

    for subject in subjects:
        df_sub = df_user[df_user["subject"] == subject].sort_values("attempt_no")
        current_score = int(df_sub["score"].iloc[-1])
        predicted_score, trend = predict_future_score(df_user, subject)
        predicted_score = max(0, int(round(predicted_score)))  # avoid negatives & decimals

        # --- Get recent score history (last 3 attempts) ---
        recent_scores = df_sub["score"].tolist()[-3:]
        score_history = " → ".join(str(int(s)) for s in recent_scores)

        # --- Explain based on recent pattern ---
        if len(recent_scores) < 2:
            trend_explanation = "Not enough attempts yet to analyze your learning pattern."
        elif all(s == recent_scores[0] for s in recent_scores):
            trend_explanation = f"Your scores ({score_history}) are consistent — great stability!"
        elif recent_scores[-1] > recent_scores[0]:
            trend_explanation = f"Your scores ({score_history}) show steady improvement — keep it up!"
        elif recent_scores[-1] < recent_scores[0]:
            trend_explanation = f"Your scores ({score_history}) show a small drop — revise weak areas to recover."
        else:
            trend_explanation = f"Your scores ({score_history}) vary slightly — maintain steady effort."

        # --- Add context for predicted trend ---
        if trend is None:
            trend_label = "Stable"
        elif trend > 0:
            trend_label = "Improving"
        elif trend < 0:
            trend_label = "Declining"
        else:
            trend_label = "Stable"

        # --- Recommendation logic ---
        if predicted_score >= 4:
            recommendation = "You’re performing strongly — challenge yourself with harder quizzes!"
        elif predicted_score >= 2:
            recommendation = "You’re doing okay — focus on practice quizzes to strengthen core topics."
        else:
            recommendation = "Performance is low — revise key concepts to rebuild confidence."

        # --- Display for the user ---
        st.markdown(f"""
        ### 🧠 {subject}
        **Current Score:** {current_score}/5  
        **Predicted Next Score:** {predicted_score}/5  
        **Trend:** {trend_label}  
        **Why:** {trend_explanation}  
        **Recommendation:** {recommendation}
        """)


if __name__ == "__main__":
    run()
