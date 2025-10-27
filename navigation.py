import streamlit as st

# Define the pages
main_page = st.Page("main.py", title="Home", icon="🏠")
TimeTable = st.Page("Time_table.py", title="Time Table", icon="📅")
QuizMaker = st.Page("quiz_maker.py", title="Quiz Maker", icon="📝")
Leaderboard = st.Page("leaderboard.py", title="Leaderboard", icon="🏆")
StudyGroup = st.Page("study_group.py", title="Study Group", icon="👥")
# CourseSuggestor = st.Page("course_suggestor.py", title="Course Suggestor", icon="🎉")

# Set up navigation
pg = st.navigation([main_page, TimeTable, QuizMaker, Leaderboard])

# Run the selected page
pg.run()