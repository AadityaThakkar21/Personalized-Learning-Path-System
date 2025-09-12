import csv
import random
import sys

"""
===================================================
Personalized Learning Path - Quiz System
===================================================
Optimization Concepts Applied:
1. Game Theory → mixed strategy idea (randomized selection within difficulty)
2. Linear Programming / Transportation → think of allocating a fixed number
   of questions as resources (here fixed at 5 per quiz)
3. Sensitivity → change difficulty to see how results vary
===================================================
"""

# Configuration
QUESTIONS_PER_QUIZ = 5

# ---------------------------
# Load quiz data from CSV
# ---------------------------

def load_quiz_data(filename="quiz_data.csv"):
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


# ---------------------------
# Pretty helpers
# ---------------------------

def hr(char="━", width=50):
	print(char * width)


def color(text, code):
	return f"\033[{code}m{text}\033[0m"


def bold(text):
	return color(text, "1")


def cyan(text):
	return color(text, "36")


def green(text):
	return color(text, "32")


def red(text):
	return color(text, "31")


# ---------------------------
# Quiz Function
# ---------------------------

def run_quiz(user_id, subject, difficulty, quiz_data):
	questions = quiz_data[subject][difficulty]
	asked_count = min(QUESTIONS_PER_QUIZ, len(questions))
	if asked_count == 0:
		print(red("No questions available for this selection."))
		return 0, 0

	# Mixed strategy flavor: random selection within the chosen difficulty
	asked = random.sample(questions, asked_count)

	hr()
	print(bold(f"📘 {subject} Quiz — Difficulty: {difficulty}"))
	hr()

	score = 0
	for i, (q, options, ans) in enumerate(asked, start=1):
		print(cyan(f"\nQuestion {i}/{asked_count}: {q}"))
		for j, opt in enumerate(options, start=1):
			print(f"   {j}. {opt}")
		try:
			choice = int(input("Your answer (1-4): ").strip())
			if 1 <= choice <= 4 and options[choice - 1] == ans:
				print(green("✅ Correct!"))
				score += 1
			else:
				print(red(f"❌ Wrong! Correct Answer: {ans}"))
		except (ValueError, IndexError):
			print(red(f"⚠ Invalid input! Correct Answer: {ans}"))

	print(bold(f"\n🎯 {subject} Quiz Finished. Your Score: {score}/{asked_count}\n"))
	return score, asked_count


# ---------------------------
# Main Program
# ---------------------------

def main():
	print(bold("====== Personalized Learning Quiz ======"))
	user_id = input("Enter your User ID (e.g., 101, 102, 103): ").strip()

	# Load dataset
	try:
		quiz_data = load_quiz_data("quiz_data.csv")
	except FileNotFoundError:
		print(red("quiz_data.csv not found. Make sure the CSV is in the same folder."))
		sys.exit(1)

	scores = {}  # subject -> (score, asked_count)

	while True:
		available_subjects = ", ".join(quiz_data.keys())
		print("\nAvailable Subjects:", bold(available_subjects))
		subject = input("Choose a subject (or type 'exit' to quit): ").strip().title()

		if subject.lower() == "exit":
			break

		if subject not in quiz_data:
			print(red("❌ Invalid subject! Try again."))
			continue

		available_diffs = ", ".join(quiz_data[subject].keys())
		print("\nDifficulty Levels:", bold(available_diffs))
		difficulty = input("Choose difficulty: ").strip().title()
		if difficulty not in quiz_data[subject]:
			print(red("❌ Invalid difficulty! Try again."))
			continue

		score, asked = run_quiz(user_id, subject, difficulty, quiz_data)
		scores[subject] = (score, asked)

		cont = input("Do you want to continue with another subject? (yes/no): ").strip().lower()
		if cont not in {"y", "yes"}:
			break

	# Final Results
	hr()
	print(bold("===== FINAL SCORES ====="))
	for sub, (sc, asked) in scores.items():
		den = asked if asked > 0 else QUESTIONS_PER_QUIZ
		print(f"{sub}: {sc}/{den}")
	print(bold("\nThank you for playing the quiz!"))


if __name__ == "__main__":
	main()
