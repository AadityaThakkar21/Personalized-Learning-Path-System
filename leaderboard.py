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


def get_subject_color(subject):
    colors = {
        "Maths": "#FF6B6B",
        "Science": "#4ECDC4",
        "Social Studies": "#FFE66D",
        "English": "#A8E6CF"
    }
    return colors.get(subject, "#95E1D3")


def get_rank_badge(rank):
    """Returns emoji badge for top 3 ranks"""
    if rank == 1:
        return "🥇"
    elif rank == 2:
        return "🥈"
    elif rank == 3:
        return "🥉"
    else:
        return f"#{rank}"


class AdaptiveLeaderboard:
    def __init__(self):
        self.data = pd.DataFrame(columns=["userid", "subject", "score", "difficulty"])

        # 🎯 Base weights
        self.subject_weights = {
            "Maths": {"Easy": 1.0, "Intermediate": 1.3, "Hard": 1.6},
            "Science": {"Easy": 1.0, "Intermediate": 1.3, "Hard": 1.6},
            "Social Studies": {"Easy": 1.0, "Intermediate": 1.3, "Hard": 1.6},
            "English": {"Easy": 1.0, "Intermediate": 1.3, "Hard": 1.6},
        }

    def update_weights(self, subject, difficulty, score, total):
        """Adjusts difficulty weights based on user performance."""
        if subject not in self.subject_weights:
            return

        performance_ratio = score / total if total > 0 else 0
        learning_rate = 0.05

        if performance_ratio >= 0.6:
            self.subject_weights[subject][difficulty] *= (1 + learning_rate)
        else:
            self.subject_weights[subject][difficulty] *= (1 - learning_rate)

    def load_quiz_data(self, filepath):
        try:
            df = pd.read_csv(filepath)
            if "user_id" in df.columns:
                df = df.rename(columns={"user_id": "userid"})

            df = df[["userid", "subject", "score", "difficulty", "total"]]

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

        attempt_counts = df.groupby("userid")["weighted_score"].count().reset_index(name="Attempts")
        best_attempts = df.groupby("userid", as_index=False)["weighted_score"].max()

        leaderboard = pd.merge(best_attempts, attempt_counts, on="userid")
        leaderboard = leaderboard.sort_values(by="weighted_score", ascending=False).reset_index(drop=True)
        leaderboard.insert(0, "Rank", leaderboard.index + 1)
        return leaderboard

    def get_overall_leaderboard(self):
        if self.data.empty:
            return pd.DataFrame(columns=["Rank", "userid", "Average_Best_Score", "Attempts"])

        df = self.data.copy()
        df["weighted_score"] = df.apply(self.weighted_score, axis=1)

        best_attempts = df.groupby(["userid", "subject"], as_index=False)["weighted_score"].max()
        leaderboard = best_attempts.groupby("userid", as_index=False)["weighted_score"].mean()
        leaderboard = leaderboard.rename(columns={"weighted_score": "Average_Best_Score"})

        attempt_counts = df.groupby("userid")["weighted_score"].count().reset_index(name="Attempts")

        leaderboard = pd.merge(leaderboard, attempt_counts, on="userid")
        leaderboard = leaderboard.sort_values(by="Average_Best_Score", ascending=False).reset_index(drop=True)
        leaderboard.insert(0, "Rank", leaderboard.index + 1)
        return leaderboard

    def get_progress_leaderboard(self, subject):
        """Shows user improvement for the selected subject, considering difficulty weights."""
        df = self.data[self.data["subject"] == subject].copy()
        if df.empty:
            return pd.DataFrame(columns=["Rank", "userid", "Progress (%)", "Attempts"])

        df["weighted_score"] = df.apply(self.weighted_score, axis=1)
        progress_list = []

        for user, user_df in df.groupby("userid"):
            user_df = user_df.sort_index()
            if len(user_df) > 1:
                earliest_weighted = (user_df.iloc[0]["weighted_score"] / max(user_df.iloc[0]["total"], 1)) * 100
                latest_weighted = (user_df.iloc[-1]["weighted_score"] / max(user_df.iloc[-1]["total"], 1)) * 100

                improvement = latest_weighted - earliest_weighted
                improvement = max(min(improvement, 100), -100)

                progress_list.append({
                    "userid": user,
                    "Progress (%)": round(improvement, 2),
                    "Attempts": len(user_df)
                })

        if not progress_list:
            return pd.DataFrame(columns=["Rank", "userid", "Progress (%)", "Attempts"])

        progress_df = pd.DataFrame(progress_list)
        progress_df = progress_df.sort_values(by="Progress (%)", ascending=False).reset_index(drop=True)
        progress_df.insert(0, "Rank", progress_df.index + 1)
        return progress_df


def render_modern_card(title, value, icon, color):
    """Render a modern stat card"""
    st.markdown(f"""
        <div style='background: linear-gradient(135deg, {color}15 0%, {color}30 100%);
                    padding: 20px; border-radius: 15px; border-left: 4px solid {color};
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin: 10px 0;'>
            <div style='display: flex; align-items: center; justify-content: space-between;'>
                <div>
                    <h3 style='margin: 0; color: {color}; font-size: 2.5em;'>{icon}</h3>
                </div>
                <div style='text-align: right;'>
                    <p style='margin: 0; color: #666; font-size: 0.9em; font-weight: 500;'>{title}</p>
                    <h2 style='margin: 5px 0 0 0; color: #333; font-size: 1.8em;'>{value}</h2>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)


def render_leaderboard_table(df, subject=None):
    """Render an enhanced leaderboard using Streamlit components"""
    if df.empty:
        st.info("📊 No data available yet. Complete some quizzes to see the leaderboard!")
        return
    
    color = get_subject_color(subject) if subject else "#6C5CE7"
    
    # Display each row as a card
    for _, row in df.iterrows():
        rank = int(row['Rank'])
        badge = get_rank_badge(rank)
        
        score_col = 'weighted_score' if 'weighted_score' in row else 'Average_Best_Score'
        if score_col in row:
            score_val = f"{row[score_col]:.2f}"
            score_label = "Score"
        else:
            score_val = f"{row['Progress (%)']:.1f}%"
            score_label = "Progress"
        
        # Special styling for top 3
        if rank <= 3:
            bg_color = "#fff9e6"
            border_color = "#ffd700"
        else:
            bg_color = "#ffffff"
            border_color = color
        
        st.markdown(f"""
        <div style='background: {bg_color}; padding: 15px; margin: 10px 0; 
                    border-radius: 12px; border-left: 5px solid {border_color};
                    box-shadow: 0 2px 8px rgba(0,0,0,0.1); 
                    display: flex; align-items: center; justify-content: space-between;'>
            <div style='display: flex; align-items: center; gap: 20px;'>
                <div style='background: {color}; color: white; padding: 12px 18px; 
                           border-radius: 8px; font-size: 1.3em; font-weight: bold; min-width: 60px; text-align: center;'>
                    {badge}
                </div>
                <div style='font-size: 1.2em; font-weight: 600; color: #2c3e50;'>
                    👤 User {row['userid']}
                </div>
            </div>
            <div style='display: flex; align-items: center; gap: 30px;'>
                <div style='text-align: center;'>
                    <div style='font-size: 0.85em; color: #7f8c8d; font-weight: 500;'>{score_label}</div>
                    <div style='font-size: 1.4em; font-weight: bold; color: {color};'>{score_val}</div>
                </div>
                <div style='text-align: center;'>
                    <div style='font-size: 0.85em; color: #7f8c8d; font-weight: 500;'>Attempts</div>
                    <div style='font-size: 1.4em; font-weight: bold; color: #95a5a6;'>🎯 {row['Attempts']}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)


def render_progress_bars(df, subject):
    """Render CSS-based progress visualization"""
    if df.empty:
        return
    
    st.markdown(f"<h3 style='text-align: center;'>📊 Top 10 Most Improved Users</h3>", unsafe_allow_html=True)
    
    top_10 = df.head(10)
    max_progress = max(abs(top_10['Progress (%)']).max(), 1)
    
    for _, row in top_10.iterrows():
        progress = row['Progress (%)']
        width = abs(progress) / max_progress * 100
        
        # Color coding: green for positive, red for negative
        if progress > 0:
            color = "#43e97b"
            bar_color = "linear-gradient(90deg, #43e97b 0%, #38f9d7 100%)"
        else:
            color = "#ff6b6b"
            bar_color = "linear-gradient(90deg, #ff6b6b 0%, #ee5a6f 100%)"
        
        st.markdown(f"""
            <div style='margin: 15px 0; padding: 10px; background: #f8f9fa; border-radius: 10px;'>
                <div style='display: flex; justify-content: space-between; margin-bottom: 5px;'>
                    <span style='font-weight: 600; color: #2c3e50;'>{row['userid']}</span>
                    <span style='font-weight: bold; color: {color};'>{progress:+.1f}%</span>
                </div>
                <div style='background: #e0e0e0; height: 20px; border-radius: 10px; overflow: hidden;'>
                    <div style='background: {bar_color}; width: {width}%; height: 100%; 
                               transition: width 0.5s ease;'></div>
                </div>
            </div>
        """, unsafe_allow_html=True)


def render_subject_distribution(data):
    """Render subject participation with CSS bars"""
    st.markdown("<h3 style='text-align: center;'>📚 Participation by Subject</h3>", unsafe_allow_html=True)
    
    subject_counts = data.groupby('subject')['userid'].nunique().reset_index()
    subject_counts.columns = ['Subject', 'Participants']
    max_participants = subject_counts['Participants'].max()
    
    for _, row in subject_counts.iterrows():
        subject = row['Subject']
        count = row['Participants']
        percentage = (count / max_participants) * 100
        color = get_subject_color(subject)
        icon = get_subject_icon(subject)
        
        st.markdown(f"""
            <div style='margin: 15px 0; padding: 15px; background: white; border-radius: 10px; 
                       box-shadow: 0 2px 8px rgba(0,0,0,0.08);'>
                <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;'>
                    <span style='font-weight: 600; color: #2c3e50; font-size: 1.1em;'>
                        {icon} {subject}
                    </span>
                    <span style='font-weight: bold; color: {color}; font-size: 1.2em;'>{count} users</span>
                </div>
                <div style='background: #f0f0f0; height: 25px; border-radius: 12px; overflow: hidden;'>
                    <div style='background: linear-gradient(90deg, {color} 0%, {color}dd 100%); 
                               width: {percentage}%; height: 100%; transition: width 0.5s ease;
                               display: flex; align-items: center; padding-left: 10px;'>
                        <span style='color: white; font-weight: 600; font-size: 0.85em;'>
                            {percentage:.0f}%
                        </span>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)


def render_difficulty_chart(data):
    """Render difficulty distribution with CSS"""
    st.markdown("<h3 style='text-align: center;'>🎚️ Attempts by Difficulty Level</h3>", unsafe_allow_html=True)
    
    diff_counts = data['difficulty'].value_counts()
    total = diff_counts.sum()
    
    colors = {
        'Easy': '#95E1D3',
        'Intermediate': '#FFD93D',
        'Hard': '#FF6B6B'
    }
    
    for difficulty in ['Easy', 'Intermediate', 'Hard']:
        count = diff_counts.get(difficulty, 0)
        percentage = (count / total * 100) if total > 0 else 0
        color = colors[difficulty]
        
        st.markdown(f"""
            <div style='margin: 15px 0; padding: 15px; background: white; border-radius: 10px;
                       box-shadow: 0 2px 8px rgba(0,0,0,0.08);'>
                <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;'>
                    <span style='font-weight: 600; color: #2c3e50; font-size: 1.1em;'>{difficulty}</span>
                    <span style='font-weight: bold; color: {color}; font-size: 1.2em;'>{count} attempts</span>
                </div>
                <div style='background: #f0f0f0; height: 25px; border-radius: 12px; overflow: hidden;'>
                    <div style='background: linear-gradient(90deg, {color} 0%, {color}dd 100%); 
                               width: {percentage}%; height: 100%; transition: width 0.5s ease;
                               display: flex; align-items: center; padding-left: 10px;'>
                        <span style='color: white; font-weight: 600; font-size: 0.85em;'>
                            {percentage:.1f}%
                        </span>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)


def run():
    st.set_page_config(
        page_title="🏆 Adaptive Leaderboard", 
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Custom CSS
    st.markdown("""
        <style>
            .main { padding: 2rem; }
            .stTabs [data-baseweb="tab-list"] {
                gap: 10px;
            }
            .stTabs [data-baseweb="tab"] {
                height: 60px;
                padding: 0 30px;
                background-color: #f0f2f6;
                border-radius: 10px 10px 0 0;
                font-weight: 600;
            }
            .stTabs [aria-selected="true"] {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white !important;
            }
            h1, h2, h3 { font-family: 'Segoe UI', sans-serif; }
        </style>
    """, unsafe_allow_html=True)

    # Header
    st.markdown("""
        <div style='text-align: center; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    border-radius: 15px; margin-bottom: 30px; box-shadow: 0 10px 25px rgba(102,126,234,0.3);'>
            <h1 style='color: white; margin: 0; font-size: 2.5em;'>🏆 Adaptive Leaderboard System</h1>
            <p style='color: rgba(255,255,255,0.9); margin: 10px 0 0 0; font-size: 1.1em;'>
                Dynamic Weight Optimization • Real-time Rankings • Progress Tracking
            </p>
        </div>
    """, unsafe_allow_html=True)

    lb = AdaptiveLeaderboard()
    file_path = "quiz_results.csv"

    if lb.load_quiz_data(file_path):
        # Dashboard Stats
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            render_modern_card("Total Users", lb.data['userid'].nunique(), "👥", "#667eea")
        with col2:
            render_modern_card("Total Attempts", len(lb.data), "🎯", "#f093fb")
        with col3:
            render_modern_card("Subjects", lb.data['subject'].nunique(), "📚", "#4facfe")
        with col4:
            avg_score = lb.data['score'].mean()
            render_modern_card("Avg Score", f"{avg_score:.1f}", "⭐", "#43e97b")

        st.markdown("<br>", unsafe_allow_html=True)

        # Tabs for different views
        tab1, tab2, tab3, tab4 = st.tabs([
            "📊 Subject Leaderboards", 
            "🌍 Overall Rankings", 
            "📈 Progress Tracker",
            "📉 Analytics"
        ])

        with tab1:
            st.markdown("### 🎯 Subject-Wise Performance")
            
            subjects = sorted(lb.data["subject"].unique())
            selected_subject = st.selectbox(
                "Choose a subject:", 
                subjects,
                key="subject_selector"
            )
            
            icon = get_subject_icon(selected_subject)
            st.markdown(f"<h2 style='text-align: center; color: {get_subject_color(selected_subject)};'>{icon} {selected_subject}</h2>", 
                       unsafe_allow_html=True)
            
            leaderboard = lb.get_subject_leaderboard(selected_subject)
            render_leaderboard_table(leaderboard, selected_subject)
            
            st.info("💡 Only the best attempt per subject is considered. Scores are weighted by difficulty level.")

        with tab2:
            st.markdown("### 🌍 Overall Champion Board")
            st.markdown("<p style='text-align: center; color: #7f8c8d;'>Rankings based on average performance across all subjects</p>", 
                       unsafe_allow_html=True)
            
            overall = lb.get_overall_leaderboard()
            render_leaderboard_table(overall)
            
            st.success("🎓 The overall leaderboard shows the average of your best attempts across all subjects!")

        with tab3:
            st.markdown("### 📈 Growth & Improvement Tracking")
            
            progress_subject = st.selectbox(
                "Select subject to track progress:", 
                sorted(lb.data["subject"].unique()),
                key="progress_selector"
            )
            
            progress_lb = lb.get_progress_leaderboard(progress_subject)
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                render_leaderboard_table(progress_lb, progress_subject)
            
            with col2:
                render_progress_bars(progress_lb, progress_subject)
            
            st.info("📊 Progress is calculated using weighted improvement between first and latest attempts.")

        with tab4:
            st.markdown("### 📉 Platform Analytics")
            
            col1, col2 = st.columns(2)
            
            with col1:
                render_subject_distribution(lb.data)
            
            with col2:
                render_difficulty_chart(lb.data)

    else:
        st.error("⚠️ Unable to load quiz data. Please ensure 'quiz_results.csv' exists in the correct location.")
        st.info("💡 The file should contain columns: userid, subject, score, difficulty, total")


if __name__ == "__main__":
    run()