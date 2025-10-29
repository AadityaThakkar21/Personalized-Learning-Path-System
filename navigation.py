import streamlit as st

# Define the pages
main_page = st.Page("main.py", title="Home", icon="🏠")
TimeTable = st.Page("Time_table.py", title="Time Table", icon="📅")
QuizMaker = st.Page("quiz_maker.py", title="Quiz Maker", icon="📝")
Leaderboard = st.Page("leaderboard.py", title="Leaderboard", icon="🏆")
StudyGroup = st.Page("study_group.py", title="Study Group", icon="👥")
SpacedRepetition = st.Page("spaced_repetition_system.py", title="Spaced Repetition", icon="🧠")

# Set up navigation
pg = st.navigation([main_page, TimeTable, QuizMaker, Leaderboard, StudyGroup, SpacedRepetition])

# Run the selected page
pg.run()