import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# =====================================================
# Knowledge Gap Detector (Enhanced with Difficulty Weighting + Smart Trend Detection)
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
    subject_slopes = {}

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

        subject_slopes[subject] = slope  # store for later comparison

        predicted_score = max(0, min(5, round(weighted_avg + slope, 0)))

        # =====================================================
        # Enhanced Trend Detection and Reasoning
        # =====================================================
        avg_score = np.mean(raw_scores)
        last_score = raw_scores[-1]
        recent_scores = raw_scores[-3:] if len(raw_scores) >= 3 else raw_scores
        recent_avg = np.mean(recent_scores)

        # Micro-trend detection
        micro_slope = 0
        if len(recent_scores) > 1:
            x_recent = np.arange(len(recent_scores))
            micro_slope = np.polyfit(x_recent, recent_scores, 1)[0]

        if slope > 0.1:
            trend = "Improving"
            reason = "Your recent scores show steady improvement — great job!"
        elif slope < -0.1:
            trend = "Declining"
            reason = "Your performance dipped slightly; revise weak topics and review harder questions."
        else:
            trend = "Stable"

            if micro_slope > 0.05 and avg_score < 3:
                reason = "Your overall trend is stable but with slight improvement — good signs of progress!"
            elif avg_score < 2:
                reason = "Your performance is stable but below average — focus on understanding core concepts."
            elif recent_avg <= avg_score and avg_score < 3:
                reason = "Your performance is stable but not showing progress — try reviewing problem areas and attempting varied questions."
            elif avg_score < 4:
                reason = "Your performance is consistent; a bit more practice can boost your scores."
            else:
                reason = "Your performance is consistently strong; keep it up!"

               # =========================================
        # Difficulty-based contextual reasoning (timestamp-aware)
        # =========================================

        # Ensure the data is sorted chronologically (oldest → newest)
        sub_df = sub_df.sort_values(by="timestamp")

        # Difficulty levels (numeric scale)
        diff_levels = {"Easy": 1, "Intermediate": 2, "Hard": 3}

        # Compute average difficulty value
        avg_diff_val = np.mean([diff_levels.get(d, 2) for d in sub_df["difficulty"]])

        # Get last attempt difficulty based on most recent timestamp
        last_diff = sub_df.iloc[-1]["difficulty"]
        last_diff_val = diff_levels.get(last_diff, 2)

        # Compare last difficulty to average
        if last_diff_val > avg_diff_val + 0.3:  # harder than usual
            if slope >= 0:
                reason += " Despite tackling harder questions recently, your performance is holding steady — nice work!"
            else:
                reason += " Your recent quiz was harder than usual, which may explain the slight dip in your performance."
        elif last_diff_val < avg_diff_val - 0.3:  # easier than usual
            if slope < 0:
                reason += " Since your most recent quiz was easier than your usual level, aim for higher accuracy next time."

        # Percentile estimation across subjects
        all_predictions.append(predicted_score)
        score_trends.append((subject, raw_scores, predicted_score, trend, reason))

    if not score_trends:
        st.warning("Not enough data to analyze.")
        return

    overall_pred = np.mean(all_predictions)
    percentile = round((overall_pred / 5) * 100, 1)
    percentile = max(0, min(100, percentile))

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

    # ---- Most Improved Subject ----
    if subject_slopes:
        best_subject = max(subject_slopes, key=subject_slopes.get)
        best_slope = subject_slopes[best_subject]
        if best_slope > 0.1:
            st.success(f"🏆 **Most Improved Subject:** {best_subject} — showing strong upward progress!")
        else:
            st.info(f"📘 **Most Consistent Subject:** {best_subject} — maintaining steady performance.")

    # ---- Overall Prediction ----
    st.markdown(f"### 🎯 Overall Predicted Percentile: **{percentile}%**")
    if percentile >= 85:
        st.success("Excellent performance! Keep maintaining this level of consistency.")
    elif percentile >= 60:
        st.info("Good performance! Keep working on your weaker areas to reach the top percentile.")
    else:
        st.warning("You can do better. Focus on your weak subjects and practice more challenging questions.")


if __name__ == "__main__":
    run()
