def run():
    import pandas as pd  

    class AdaptiveLeaderboard:
        def __init__(self):
            self.data = pd.DataFrame(columns=["userid", "subject", "score", "difficulty"])
            
            self.weights = {"Easy": 1.0, "Intermediate": 1.0, "Hard": 1.0}
            
            self.difficulty_map = {"Easy": 0, "Intermediate": 1, "Hard": 2}

        def load_quiz_data(self, filepath):
            """Load quiz results from a CSV file into the leaderboard."""
            try:
                df = pd.read_csv(filepath)

                if "user_id" in df.columns:
                    df = df.rename(columns={"user_id": "userid"})

                df = df[["userid", "subject", "score", "difficulty"]]
                self.data = pd.concat([self.data, df], ignore_index=True)

            except FileNotFoundError:
                print(f" File not found: {filepath}")
            except Exception as e:
                print(f"⚠ Error loading quiz data: {e}")

        def add_quiz_result(self, userid, subject, score, difficulty):
            """Add new quiz result to the system."""
            new_entry = {"userid": userid, "subject": subject, "score": score, "difficulty": difficulty}
            self.data = pd.concat([self.data, pd.DataFrame([new_entry])], ignore_index=True)

        def weighted_score(self, row):
            """Compute weighted score for a quiz attempt."""
            return row["score"] * self.weights[row["difficulty"]]

        def get_subject_leaderboard(self, subject):
            """Leaderboard for a specific subject."""
            df = self.data[self.data["subject"] == subject].copy()
            if df.empty:
                return pd.DataFrame(columns=["Rank", "userid", "weighted_score"])
            df["weighted_score"] = df.apply(self.weighted_score, axis=1)
            leaderboard = df.groupby("userid")["weighted_score"].sum().reset_index()
            leaderboard = leaderboard.sort_values(by="weighted_score", ascending=False).reset_index(drop=True)
            leaderboard.insert(0, "Rank", leaderboard.index + 1)  
            return leaderboard

        def get_overall_leaderboard(self):
            """Overall leaderboard across all subjects."""
            if self.data.empty:
                return pd.DataFrame(columns=["Rank", "userid", "weighted_score"])
            df = self.data.copy()
            df["weighted_score"] = df.apply(self.weighted_score, axis=1)
            leaderboard = df.groupby("userid")["weighted_score"].sum().reset_index()
            leaderboard = leaderboard.sort_values(by="weighted_score", ascending=False).reset_index(drop=True)
            leaderboard.insert(0, "Rank", leaderboard.index + 1)  
            return leaderboard

        def train_weights(self, lr=0.0001, epochs=500):
            """
            Train difficulty weights using Gradient Descent.
            Objective: Ensure higher difficulty → proportionally higher effective score.
            """
            difficulties = list(self.weights.keys())
            
            for _ in range(epochs):
                grads = {d: 0.0 for d in difficulties}

                # Compute gradients
                for _, row in self.data.iterrows():
                    diff_index = self.difficulty_map[row["difficulty"]]
                    weighted = row["score"] * self.weights[row["difficulty"]]
                    target = (diff_index + 1) * row["score"]  # ideal scaling
                    error = weighted - target
                    grads[row["difficulty"]] += error * row["score"]

                # Update weights
                for d in difficulties:
                    self.weights[d] -= lr * grads[d]

            return self.weights


    if __name__ == "__main__":
        lb = AdaptiveLeaderboard()

        lb.load_quiz_data("quiz_results.csv")

        if not lb.data.empty:
            for subject in lb.data["subject"].unique():
                print(f"\n Subject Leaderboard: {subject}")
                print(lb.get_subject_leaderboard(subject).to_string(index=False))  # no row index
        else:
            print("⚠ No data found in CSV.")

        # Print overall leaderboard
        print("\n Overall Leaderboard")
        print(lb.get_overall_leaderboard().to_string(index=False))  # no row index
    

# only run this when you execute Time_table.py directly:
if __name__ == "__main__":
    run()
