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
        self.weights = {"Easy": 1.0, "Intermediate": 1.0, "Hard": 1.0}
        self.difficulty_map = {"Easy": 0, "Intermediate": 1, "Hard": 2}

    def load_quiz_data(self, filepath):
        try:
            df = pd.read_csv(filepath)
            if "user_id" in df.columns:
                df = df.rename(columns={"user_id": "userid"})
            df = df[["userid", "subject", "score", "difficulty"]]
            self.data = pd.concat([self.data, df], ignore_index=True)
            return True
        except FileNotFoundError:
            st.error(f"File not found: {filepath}")
            return False
        except Exception as e:
            st.error(f"⚠ Error loading quiz data: {e}")
            return False

    def weighted_score(self, row):
        return row["score"] * self.weights[row["difficulty"]]

    def get_subject_leaderboard(self, subject):
        df = self.data[self.data["subject"] == subject].copy()
        if df.empty:
            return pd.DataFrame(columns=["Rank", "userid", "weighted_score"])
        df["weighted_score"] = df.apply(self.weighted_score, axis=1)
        leaderboard = df.groupby("userid")["weighted_score"].sum().reset_index()
        leaderboard = leaderboard.sort_values(by="weighted_score", ascending=False).reset_index(drop=True)
        leaderboard.insert(0, "Rank", leaderboard.index + 1)
        return leaderboard

    def get_overall_leaderboard(self):
        if self.data.empty:
            return pd.DataFrame(columns=["Rank", "userid", "weighted_score"])
        df = self.data.copy()
        df["weighted_score"] = df.apply(self.weighted_score, axis=1)
        leaderboard = df.groupby("userid")["weighted_score"].sum().reset_index()
        leaderboard = leaderboard.sort_values(by="weighted_score", ascending=False).reset_index(drop=True)
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

    st.title("🏆 Adaptive Leaderboard System")

    lb = AdaptiveLeaderboard()
    file_path = "quiz_results.csv"

    if lb.load_quiz_data(file_path):
        st.success(f"✅ Loaded data from `{file_path}` successfully!")

        for subject in lb.data["subject"].unique():
            icon = get_subject_icon(subject)
            st.markdown(f"<h2 style='text-align:center;'>{icon} {subject} Leaderboard</h2>", unsafe_allow_html=True)
            leaderboard = lb.get_subject_leaderboard(subject)
            render_centered_table(leaderboard)

        st.markdown("<h2 style='text-align:center;'>🌍 Overall Leaderboard</h2>", unsafe_allow_html=True)
        overall = lb.get_overall_leaderboard()
        render_centered_table(overall)
    else:
        st.warning("⚠ No data found or failed to load file.")


if __name__ == "__main__":
    run()
