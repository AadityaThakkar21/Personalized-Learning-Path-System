import streamlit as st
import csv
import random
import os
from datetime import datetime, timedelta

QUESTIONS_PER_QUIZ = 5
DEFAULT_DATASET = "quiz_data.csv"
RESULTS_CSV = "quiz_results.csv"


def load_quiz_data(filename: str):
    quiz_data = {}
    with open(filename, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            subject = row["Subject"].title()
            difficulty = row["Difficulty"].title()
            question = row["Question"]
            options = [row["Option1"], row["Option2"], row["Option3"], row["Option4"]]
            answer = row["Answer"]
            if subject not in quiz_data:
                quiz_data[subject] = {}
            if difficulty not in quiz_data[subject]:
                quiz_data[subject][difficulty] = []
            quiz_data[subject][difficulty].append((question, options, answer))
    return quiz_data


def ensure_results_header(path: str):
    """Ensure the results file exists and has the correct columns."""
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "timestamp", "user_id", "subject", "difficulty",
                "score", "total", "dataset", "attempt_no", "time_spent(mins)"
            ])


def log_result(user_id: str, subject: str, difficulty: str, score: int, total: int,
               dataset_path: str, start_time: datetime):
    """Log quiz result with attempt tracking and time spent."""
    ensure_results_header(RESULTS_CSV)

    # Determine current attempt number for this user & subject
    attempt_no = 1
    if os.path.exists(RESULTS_CSV):
        with open(RESULTS_CSV, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            attempts = [
                row for row in reader
                if row["user_id"] == user_id and row["subject"].title() == subject.title()
            ]
            if attempts:
                attempt_no = len(attempts) + 1

    # Calculate real time spent (in minutes)
    end_time = datetime.now()
    time_spent = round((end_time - start_time).total_seconds() / 60, 2)

    # Write result row
    with open(RESULTS_CSV, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            end_time.isoformat(timespec="seconds"),
            user_id,
            subject,
            difficulty,
            score,
            total,
            os.path.basename(dataset_path),
            attempt_no,
            time_spent
        ])


def run():
    st.set_page_config(page_title="Personalized Learning Quiz", layout="centered")
    st.title("📝 Personalized Learning Quiz")
    st.write("Take quizzes by selecting a subject and difficulty level!")

    # --- Load quiz data ---
    try:
        quiz_data = load_quiz_data(DEFAULT_DATASET)
    except FileNotFoundError:
        st.error(f"Dataset not found: `{DEFAULT_DATASET}`. Please upload it first.")
        return

    # --- User info ---
    user_id = st.text_input("Enter your User ID (e.g., 101)")
    if not user_id:
        st.info("Please enter your User ID to begin.")
        return
    if not user_id.isdigit():
        st.error("User ID must be numeric.")
        return

    # --- Subject & difficulty selection ---
    subjects = list(quiz_data.keys())
    subject = st.selectbox("Choose a Subject", subjects)

    difficulties = list(quiz_data[subject].keys())
    difficulty = st.selectbox("Choose Difficulty", difficulties)

    # Store quiz state in Streamlit session
    if "quiz_state" not in st.session_state:
        st.session_state.quiz_state = None

    # --- Start quiz ---
    if st.button("Start Quiz"):
        questions = quiz_data[subject][difficulty]
        if len(questions) == 0:
            st.warning("No questions available for this selection.")
            return
        asked = random.sample(questions, min(QUESTIONS_PER_QUIZ, len(questions)))
        st.session_state.quiz_state = {
            "questions": asked,
            "current": 0,
            "score": 0,
            "subject": subject,
            "difficulty": difficulty,
            "user_id": user_id,
            "start_time": datetime.now()
        }

    # --- Quiz in progress ---
    if st.session_state.quiz_state:
        state = st.session_state.quiz_state
        current = state["current"]
        total = len(state["questions"])

        if current < total:
            q, options, answer = state["questions"][current]
            st.subheader(f"Question {current+1}/{total}")
            st.write(q)
            choice = st.radio("Select your answer:", options, key=f"q{current}")

            if st.button("Submit Answer", key=f"submit{current}"):
                if choice == answer:
                    st.success("✅ Correct!")
                    state["score"] += 1
                else:
                    st.error(f"❌ Wrong! Correct Answer: {answer}")
                state["current"] += 1
                st.rerun()

        else:
            st.subheader("🎯 Quiz Finished!")
            st.write(f"**Score:** {state['score']} / {total}")

            log_result(
                state["user_id"],
                state["subject"],
                state["difficulty"],
                state["score"],
                total,
                DEFAULT_DATASET,
                state["start_time"],
            )

            st.success("Results saved successfully!")
            if st.button("Take another quiz"):
                st.session_state.quiz_state = None
                st.rerun()


if __name__ == "__main__":
    run()
