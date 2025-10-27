import streamlit as st

st.title("📚 Personalized Learning System")
st.subheader("Explore a variety of features to enhance your learning experience with us!")
st.text("Use the navigation menu on the left to access different tools like Study Timetable Generator, Quiz Maker, and Leaderboard.")

st.divider()
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown(
        """
        ### About Us
        This platform was developed by students of **DAU** as part of their **Optimization course project**.  
        It aims to demonstrate how optimization principles can enhance personalized learning experiences.
        """
    )

with col2:
    st.image("DAU.webp", use_container_width=True)