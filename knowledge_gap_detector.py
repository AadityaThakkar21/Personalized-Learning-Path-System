import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# =====================================================
# Knowledge Gap Detector (Enhanced with Difficulty Weighting)
# =====================================================

def run():
    st.set_page_config(page_title="Knowledge Gap Detector", layout="wide")
    st.title("🧩 Knowledge Gap & Performance Predictor")

    st.write("Analyze your quiz results, and predict your future performance.")

    # Load results file
    try:
        df = pd.read_csv("quiz_results.csv")
    except FileNotFoundError:
        st.error("⚠ No quiz_results.csv found. Please take some quizzes first.")
        return

    # Check required columns
    required_cols = ["timestamp", "user_id", "subject", "difficulty", "score", "total"]
    if not all(col in df.columns for col in required_cols):
        st.error("CSV file missing required columns.")
        return

    user_id = st.text_input("Enter your User ID (e.g., 101):")
    if not user_id:
        st.info("Please enter your User ID to see your analysis.")
        return

    try:
        user_id = int(user_id)
    except ValueError:
        st.error("User ID must be numeric.")
        return

    user_df = df[df["user_id"] == user_id]

    if user_df.empty:
        st.warning("No records found for this user.")
        return

    st.write(f"### 📊 Performance Summary for User {user_id}")

    # Difficulty weighting
    difficulty_weights = {"Easy": 0.8, "Intermediate": 1.0, "Hard": 1.2}

    all_predictions = []
    score_trends = []

    for subject in user_df["subject"].unique():
        sub_df = user_df[user_df["subject"] == subject].sort_values(by="timestamp")
        if len(sub_df) < 1:
            continue

        # Apply difficulty-based weighting
        sub_df["weighted_score"] = sub_df.apply(
            lambda row: row["score"] * difficulty_weights.get(row["difficulty"], 1.0),
            axis=1
        )

        scores = sub_df["weighted_score"].tolist()
        raw_scores = sub_df["score"].tolist()

        # Weighted time-average prediction
        weights = np.linspace(1, 2, len(scores))
        weighted_avg = np.average(scores, weights=weights)

        # Linear trend (time slope)
        x = np.arange(len(scores))
        if len(scores) > 1:
            slope = np.polyfit(x, scores, 1)[0]
        else:
            slope = 0

        predicted_score = max(0, min(5, round(weighted_avg + slope, 0)))

        # Determine trend text
        if slope > 0.1:
            trend = "Improving"
            reason = "Your recent scores show steady improvement — great job!"
        elif slope < -0.1:
            trend = "Declining"
            reason = "Your performance dipped slightly; revise weak topics and review harder questions."
        else:
            trend = "Stable"
            reason = "Your performance is consistent; keep practicing to maintain it."

        # Adjust reasoning with difficulty insight
        if sub_df["difficulty"].iloc[-1] == "Hard" and slope >= 0:
            reason += " You’re handling harder questions effectively, which shows real progress."
        elif sub_df["difficulty"].iloc[-1] == "Easy" and slope < 0:
            reason += " Since the difficulty was easier, aim for higher accuracy next time."

        # Percentile estimation across subjects
        all_predictions.append(predicted_score)
        score_trends.append((subject, raw_scores, predicted_score, trend, reason))

    if not score_trends:
        st.warning("Not enough data to analyze.")
        return

    overall_pred = np.mean(all_predictions)
    percentile = round((overall_pred / 5) * 100, 1)
    if percentile > 100: percentile = 100
    if percentile < 0: percentile = 0

    # ---- Display Results ----
    st.markdown("### 🧠 Subject-Wise Analysis")
    for subject, raw_scores, predicted_score, trend, reason in score_trends:
        score_path = " → ".join(map(str, raw_scores))
        st.markdown(f"""
        **📘 {subject}**
        - Past Scores: {score_path}
        - Predicted Next Score: **{int(predicted_score)}/5**
        - Trend: **{trend}**
        - Why: {reason}
        """)

    st.markdown("---")
    st.markdown(f"### 🎯 Overall Predicted Percentile: **{percentile}%**")
    if percentile >= 85:
        st.success("Excellent performance! Keep maintaining this level of consistency.")
    elif percentile >= 60:
        st.info("Good performance! Keep working on your weaker areas to reach the top percentile.")
    else:
        st.warning("You can do better. Focus on your weak subjects and practice more challenging questions.")


if __name__ == "__main__":
    run()
