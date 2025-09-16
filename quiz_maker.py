import csv
import random
import sys
import os
from datetime import datetime

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

def ensure_results_header(path: str):
	if not os.path.exists(path) or os.path.getsize(path) == 0:
		with open(path, "w", newline="", encoding="utf-8") as f:
			writer = csv.writer(f)
			writer.writerow(["timestamp", "user_id", "subject", "difficulty", "score", "total", "dataset"])

def log_result(user_id: str, subject: str, difficulty: str, sco
