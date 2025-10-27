
from Time_table import run as timetable_run
# from course_suggestor import run as course_run
from quiz_maker import run as quiz_run
from leaderboard import run as leaderboard_run

def main():
    while True:
        print("\n--- Personalized Learning System ---")
        print("1. Create Timetable")
        print("2. Get Course Suggestions")
        print("3. Take a Quiz")
        print("4. Leaderboard")
        print("5. Exit")

        choice = input("Enter your choice (1-5): ")

        if choice == '1':
            timetable_run()
        elif choice == '2':
            # course_run()
            print("Course Suggestor is currently unavailable.")
        elif choice == '3':
            quiz_run()
        elif choice == '4':
            leaderboard_run()
        elif choice == '5':
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
