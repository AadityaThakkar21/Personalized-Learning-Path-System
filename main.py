from PIL import Image
import streamlit as st
import base64
from io import BytesIO

# --- Page Config ---
st.set_page_config(
    page_title="Personalized Learning System",
    page_icon="🎓",
    layout="wide",
)

# --- Custom CSS ---
st.markdown("""
<style>
.stApp {
    background: linear-gradient(to bottom right, #f0f7ff, #d9e9ff);
    font-family: "Segoe UI", sans-serif;
}

.title {
    text-align: center;
    font-size: 2.8em;
    color: #003366;
    margin-bottom: 0;
}
.subtitle {
    text-align: center;
    color: #00509e;
    font-size: 1.2em;
    margin-top: 0.2em;
}
hr {
    border: 1px solid #b0c4de;
    margin: 1.5em 0;
}

/* Card Styling */
.card {
    background: rgba(255,255,255,0.9);
    border: 1px solid #ddd;
    border-radius: 16px;
    padding: 1.5em;
    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    transition: all 0.2s ease;
    width: 280px;
}
.card:hover {
    border-color: #6a5acd;
    transform: translateY(-3px);
}
.card h3 {
    color: #002b5b;
    margin-bottom: 0.3em;
}
.card p {
    color: #444;
    font-size: 0.95em;
}
.icon {
    font-size: 1.6em;
    color: #4b6cb7;
}

/* Logo Box */
.logo-box {
    background: white;
    border-radius: 20px;
    padding: 2em;
    box-shadow: 0 4px 20px rgba(0,0,0,0.08);
    text-align: center;
    border: 1px solid #ddd;
}
.logo-box img {
    width: 180px;
    border-radius: 12px;
    box-shadow: 0 0 20px rgba(0,0,0,0.1);
}
.logo-box h3 {
    color: #1a237e;
    margin-top: 1em;
}
.stats {
    display: flex;
    justify-content: center;
    gap: 2em;
    margin-top: 1.5em;
}
.stat {
    background: #f3f5ff;
    padding: 0.8em 1.2em;
    border-radius: 12px;
    border: 1px solid #e0e0ff;
}
.stat .num {
    font-size: 1.4em;
    font-weight: bold;
    color: #3f51b5;
}
.stat .label {
    font-size: 0.8em;
    color: #555;
}

/* Footer */
.footer {
    text-align: center;
    font-size: 0.9em;
    color: #444;
    margin-top: 2em;
}
</style>
""", unsafe_allow_html=True)

# --- Header Section ---
st.markdown('<h1 class="title">🎓 Personalized Learning System</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Enhance your learning experience with adaptive tools and optimization techniques</p>', unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)

# --- About Section ---
col1, col2 = st.columns([2, 1], vertical_alignment="center")

with col1:
    st.markdown("""
    <h2>About</h2>
    <p>
    This project is a Personalized Learning Path System, developed as a group project for the <b>IE402 course on Optimization</b>. The system is designed to support learners by providing a streamlined and interactive learning experience with four main features:
    </p>
    <ol>
    <li><b>Timetable Creator:</b> Helps users create personalized study schedules.</li>
    <li><b>Quiz Maker:</b> Allows users to take quizzes to assess their knowledge.</li>
    <li><b>Leaderboard:</b> Displays user rankings to motivate and encourage progress.</li>
    <li><b>Study Group:</b> Recommends courses ideal groups based on variety of data points.</li>
    <li><b>Gradelink:</b> A grade tracking system with performance indicator and study allocation</li>
    <li><b>Knowledge Gap Detector:</b>Predicts future performance to guide focused improvement.</li>
    <li><b>Spaced Repetition:</b> Helps users know how often to revise a concept until the next quiz using ML algorithms.</li>
    </ol>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
                <h2>Tech Stack:</h2>
                <ul>
                    <li>Python</li>
                    <li>Streamlit</li>
                    <li>Pandas</li>
                    <li>NumPy</li>
                    <li>Pulp</li>
                    <li>Scikit-learn</li>
                    <li>Matplotlib & Seaborn</li>
                    <li>HTML & CSS</li>
                </ul>
                """, unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

# --- Project Highlights Section ---
st.markdown("""
<div style="display:flex; flex-wrap:wrap; justify-content:center; gap:1.5em; margin-top:2em;">
    <div class="card">
        <span class="icon">🎯</span>
        <h3>Student-Built Innovation</h3>
        <p>Created by students, for students — built with real academic challenges in mind.</p>
    </div>
    <div class="card">
        <span class="icon">⚙️</span>
        <h3>Optimization Focused</h3>
        <p>Leverages algorithms to maximize learning efficiency and engagement.</p>
    </div>
    <div class="card">
        <span class="icon">🚀</span>
        <h3>Practical Application</h3>
        <p>Bridging theory and practice in modern educational technology.</p>
    </div>
</div>
""", unsafe_allow_html=True)

def image_to_base64(img_path):
    img = Image.open(img_path)
    buffer = BytesIO()
    img.save(buffer, format="WEBP")
    return base64.b64encode(buffer.getvalue()).decode()

img_base64 = image_to_base64("DAU.webp")

st.markdown(f"""
<style>
.center-container {{
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 55vh;
    gap: 40px;
}}
.divider {{
    border-left: 2px solid #ccc;
    height: 250px;
}}
.team-text {{
    text-align: left;
    line-height: 1.8;
    font-size: 1.1em;
}}
</style>

<div class="center-container">
    <img src="data:image/webp;base64,{img_base64}" width="300">
    <div class="divider"></div>
    <div class="team-text">
        <h3><u>Our Team</u></h3>
        <ul style="list-style-type:none; padding-left:0;">
            <li>202301408 Vraj Patel</li>
            <li>202301417 Aaditya Thakkar</li>
            <li>202301114 Yogesh Bagotia</li>
            <li>202301065 Vansh Padaliya</li>
            <li>202301050 Siva Suhas Thatavarthy</li>
        </ul>
    </div>
</div>
""", unsafe_allow_html=True)