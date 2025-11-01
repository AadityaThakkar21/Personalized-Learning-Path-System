import streamlit as st
import pandas as pd


def get_subject_icon(subject):
    s = subject.lower()
    if "math" in s:
        return "🧮"
    elif "english" in s or "literature" in s:
        return "📖"
    elif "science" in s or "physics" in s or "chemistry" in s or "biology" in s:
        return "🔬"
    elif "social" in s or "history" in s or "civics" in s or "geography" in s:
        return "🏛️"  
    else:
        return "📘"  


class AdaptiveLeaderboard:
    def __init__(self):
        self.data = pd.DataFrame(columns=["userid", "subject", "score", "difficulty"])

        # 🎯 Base weights (start balanced)
        self.subject_weights = {
            "Maths": {"Easy": 1.0, "Intermediate": 1.3, "Hard": 1.6},
            "Science": {"Easy": 1.0, "Intermediate": 1.3, "Hard": 1.6},
            "Social Studies": {"Easy": 1.0, "Intermediate": 1.3, "Hard": 1.6},
            "English": {"Easy": 1.0, "Intermediate": 1.3, "Hard": 1.6},
        }

    # 🔄 Dynamic Difficulty Weight Optimization
    def update_weights(self, subject, difficulty, score, total):
        """Adjusts difficulty weights based on user performance."""
        if subject not in self.subject_weights:
            return  # skip unknown subjects

        performance_ratio = score / total if total > 0 else 0
        learning_rate = 0.05  # 5% change rate

        # Increase weight if user performs well (>= 60%)
        if performance_ratio >= 0.6:
            self.subject_weights[subject][difficulty] *= (1 + learning_rate)
        else:
            self.subject_weights[subject][difficulty] *= (1 - learning_rate)

    def load_quiz_data(self, filepath):
        try:
            df = pd.read_csv(filepath)
            if "user_id" in df.columns:
                df = df.rename(columns={"user_id": "userid"})

            # Keep required columns
            df = df[["userid", "subject", "score", "difficulty", "total"]]

            # 📈 Update weights dynamically for every new quiz record
            for _, row in df.iterrows():
                self.update_weights(row["subject"], row["difficulty"], row["score"], row["total"])

            self.data = pd.concat([self.data, df], ignore_index=True)
            return True
        except FileNotFoundError:
            st.error(f"File not found: {filepath}")
            return False
        except Exception as e:
            st.error(f"⚠ Error loading quiz data: {e}")
            return False

    def weighted_score(self, row):
        subject = row["subject"]
        difficulty = row["difficulty"]
        base_weight = self.subject_weights.get(subject, {}).get(difficulty, 1.0)
        return row["score"] * base_weight

    def get_subject_leaderboard(self, subject):
        df = self.data[self.data["subject"] == subject].copy()
        if df.empty:
            return pd.DataFrame(columns=["Rank", "userid", "weighted_score", "Attempts"])

        df["weighted_score"] = df.apply(self.weighted_score, axis=1)

        # 🔹 Count number of attempts per user for this subject
        attempt_counts = df.groupby("userid")["weighted_score"].count().reset_index(name="Attempts")

        # 🔹 Take best (maximum) weighted score per user for this subject
        best_attempts = df.groupby("userid", as_index=False)["weighted_score"].max()

        # Merge attempt counts with best scores
        leaderboard = pd.merge(best_attempts, attempt_counts, on="userid")

        # Sort and rank
        leaderboard = leaderboard.sort_values(by="weighted_score", ascending=False).reset_index(drop=True)
        leaderboard.insert(0, "Rank", leaderboard.index + 1)
        return leaderboard

    def get_overall_leaderboard(self):
        if self.data.empty:
            return pd.DataFrame(columns=["Rank", "userid", "Average_Best_Score", "Attempts"])

        df = self.data.copy()
        df["weighted_score"] = df.apply(self.weighted_score, axis=1)

        # 🔹 Get best attempt per user per subject
        best_attempts = df.groupby(["userid", "subject"], as_index=False)["weighted_score"].max()

        # 🔹 Take average of best attempts across all subjects
        leaderboard = best_attempts.groupby("userid", as_index=False)["weighted_score"].mean()
        leaderboard = leaderboard.rename(columns={"weighted_score": "Average_Best_Score"})

        # 🔹 Count total number of attempts across all subjects
        attempt_counts = df.groupby("userid")["weighted_score"].count().reset_index(name="Attempts")

        leaderboard = pd.merge(leaderboard, attempt_counts, on="userid")

        # Sort and rank
        leaderboard = leaderboard.sort_values(by="Average_Best_Score", ascending=False).reset_index(drop=True)
        leaderboard.insert(0, "Rank", leaderboard.index + 1)
        return leaderboard


def render_centered_table(df):
    """Renders a dataframe without index and centered text."""
    st.markdown(
        df.to_html(index=False, justify="center", classes="dataframe", escape=False),
        unsafe_allow_html=True
    )


def run():
    st.set_page_config(page_title="Adaptive Leaderboard", layout="centered")

    st.markdown("""
        <style>
            table {
                margin-left: auto !important;
                margin-right: auto !important;
                text-align: center !important;
            }
            th, td {
                text-align: center !important;
                padding: 8px 16px !important;
            }
            thead th {
                background-color: #222 !important;
                color: white !important;
            }
        </style>
    """, unsafe_allow_html=True)

    st.title("🏆 Adaptive Leaderboard System (Dynamic Weight Optimization)")

    lb = AdaptiveLeaderboard()
    file_path = "quiz_results.csv"

    if lb.load_quiz_data(file_path):
        st.success(f"✅ Loaded data from `{file_path}` successfully!")


        for subject in lb.data["subject"].unique():
            icon = get_subject_icon(subject)
            st.markdown(f"<h2 style='text-align:center;'>{icon} {subject} Leaderboard</h2>", unsafe_allow_html=True)
            leaderboard = lb.get_subject_leaderboard(subject)
            render_centered_table(leaderboard)
            st.markdown("<p style='text-align:center;color:gray;'>Only the best attempt per subject is considered. 'Attempts' show how many times the quiz was taken.</p>", unsafe_allow_html=True)

        st.markdown("<h2 style='text-align:center;'>🌍 Overall Leaderboard</h2>", unsafe_allow_html=True)
        overall = lb.get_overall_leaderboard()
        render_centered_table(overall)
        st.markdown("<p style='text-align:center;color:gray;'>Overall leaderboard shows the <b>average of your best attempts</b> across all subjects, along with total attempts.</p>", unsafe_allow_html=True)

    else:
        st.warning("⚠ No data found or failed to load file.")


if __name__ == "__main__":
    run()
