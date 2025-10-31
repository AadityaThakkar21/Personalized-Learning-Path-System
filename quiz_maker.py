import streamlit as st
import pandas as pd
import numpy as np

def run():
    st.set_page_config(page_title="Knowledge Gap Detector", layout="wide")
    st.title("🧩 Knowledge Gap Detector")
    st.write("""
    This system analyzes your quiz performance using **Adaptive Weighted Optimization**,
    predicts your next scores, your percentile, and gives personalized recommendations.
    """)

    uploaded_file = "quiz_results.csv"

    try:
        df = pd.read_csv(uploaded_file)
    except FileNotFoundError:
        st.error("No quiz results found. Please take a few quizzes first!")
        return

    if df.empty:
        st.warning("No data available yet.")
        return

    user_id = st.text_input("Enter your User ID:")
    if not user_id:
        st.info("Please enter your User ID to continue.")
        return

    df_user = df[df["user_id"].astype(str) == user_id]
    if df_user.empty:
        st.warning("No quiz history found for this User ID.")
        return

    st.subheader(f"📚 Performance Summary for User {user_id}")

    subjects = df_user["subject"].unique()
    overall_avg = df_user["score"].mean()
    total_attempts = len(df_user)

    st.markdown(f"**Total Quizzes Taken:** {total_attempts}")
    st.markdown(f"**Overall Average Score:** {overall_avg:.2f}/5")

    predicted_scores = []

    for subject in subjects:
        df_sub = df_user[df_user["subject"] == subject].sort_values("timestamp")
        scores = df_sub["score"].tolist()

        if len(scores) == 0:
            continue

        current_score = int(scores[-1])
        n = len(scores)

        # ✅ Adaptive Weighted Prediction (uses all attempts fairly)
        if n <= 3:
            weights = [0.1, 0.3, 0.6][:n]
        else:
            weights = np.linspace(0.4, 1.0, n)
            weights = weights / weights.sum()

        predicted_score = sum(w * s for w, s in zip(weights, scores))
        predicted_score = max(0, int(round(predicted_score)))
        predicted_scores.append(predicted_score)

        # Trend detection based on entire score history
        if len(scores) >= 2:
            if scores[-1] > scores[-2]:
                trend = "Improving"
                reason = "your recent improvement suggests you're learning effectively."
            elif scores[-1] < scores[-2]:
                trend = "Declining"
                reason = "recent drop may be due to harder questions or less revision."
            else:
                trend = "Stable"
                reason = "your performance has remained consistent."
        else:
            trend = "Stable"
            reason = "not enough attempts yet to detect a clear trend."

        # Generate readable history summary
        score_history = " → ".join(str(int(s)) for s in scores)
        if len(scores) > 3:
            trend_comment = "You’ve shown steady participation with these scores."
        else:
            trend_comment = "Good start — continue to attempt more quizzes for stability."

        # Recommendations
        if predicted_score >= 4:
            recommendation = "Excellent performance — consider taking harder quizzes to challenge yourself."
        elif predicted_score >= 2:
            recommendation = "Good effort — focus on revision to reach top levels."
        else:
            recommendation = "You need improvement — revisit the core concepts and practice daily."

        st.markdown(f"""
        ### 🧠 {subject}
        **Current Score:** {current_score}/5  
        **Predicted Next Score:** {predicted_score}/5  
        **Trend:** {trend}  
        **Why:** Your attempt history ({score_history}) shows this pattern; {reason}  
        **Observation:** {trend_comment}  
        **Recommendation:** {recommendation}
        """)

    # 🎯 Predicted Percentile (All Subjects)
    st.divider()
    st.subheader("📊 Predicted Percentile (All Subjects Combined)")

    if len(predicted_scores) > 0:
        user_pred_avg = np.mean(predicted_scores)
        avg_scores_per_user = df.groupby("user_id")["score"].mean()
        user_list = avg_scores_per_user.values

        percentile = (np.sum(user_list < user_pred_avg) / len(user_list)) * 100
        percentile = round(percentile, 2)

        st.markdown(f"**Predicted Percentile:** {percentile:.2f}%")

        # Motivation text
        if percentile >= 90:
            st.success("🥇 Top-tier performance — you're among the best! Keep this consistency.")
        elif percentile >= 70:
            st.info("💪 You’re performing very well — a little more effort can get you into the top group.")
        elif percentile >= 40:
            st.warning("⚙️ You’re making progress — consistent study will lift you further.")
        else:
            st.error("📘 You’re currently below average — focus on revision and retake key quizzes.")

        st.markdown(f"💡 If you improve each subject by +1, your percentile could reach **{min(100, percentile + 10):.2f}%!**")

    else:
        st.info("Not enough data to calculate percentile yet.")

    # 💪 Motivation Tracker
    st.divider()
    st.subheader("💪 Motivation Tracker")

    early_avg = df_user.head(3)["score"].mean() if len(df_user) >= 3 else df_user["score"].mean()
    recent_avg = df_user.tail(3)["score"].mean()
    change = recent_avg - early_avg

    if change > 0:
        st.success(f"👏 You’ve improved by +{change:.1f} points recently! Keep going.")
    elif change < 0:
        st.warning(f"⚠️ Your average dropped by {abs(change):.1f} points — time to reinforce weak areas.")
    else:
        st.info("📘 Your performance is steady — aim higher in your next quiz!")

if __name__ == "__main__":
    run()
