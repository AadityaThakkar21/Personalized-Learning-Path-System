import pandas as pd  

class AdaptiveLeaderboard:
    def __init__(self):
        # Store quiz results
        self.data = pd.DataFrame(columns=["User_ID", "Subject", "Score", "Difficulty"])
        
        # Initialize weights equally
        self.weights = {"Easy": 1.0, "Intermediate": 1.0, "Hard": 1.0}
        
        # Difficulty ordering (used for target ranking)
        self.Difficulty_map = {"Easy": 0, "Intermediate": 1, "Hard": 2}

    def add_quiz_result(self, User_ID, Subject, Score, Difficulty):
        """Add new quiz result to the system."""
        new_entry = {"User_ID": User_ID, "Subject": Subject, "Score": Score, "Difficulty": Difficulty}
        self.data = pd.concat([self.data, pd.DataFrame([new_entry])], ignore_index=True)

    def weighted_Score(self, row):
        """Compute weighted Score for a quiz attempt."""
        return row["Score"] * self.weights[row["Difficulty"]]

    def get_Subject_leaderboard(self, Subject):
        """Leaderboard for a specific Subject."""
        df = self.data[self.data["Subject"] == Subject].copy()
        if df.empty:
            return pd.DataFrame(columns=["User_ID", "weighted_Score"])
        df["weighted_Score"] = df.apply(self.weighted_Score, axis=1)
        leaderboard = df.groupby("User_ID")["weighted_Score"].sum().reset_index()
        leaderboard = leaderboard.sort_values(by="weighted_Score", ascending=False).reset_index(drop=True)
        leaderboard.index += 1
        return leaderboard

    def get_overall_leaderboard(self):
        """Overall leaderboard across all Subjects."""
        if self.data.empty:
            return pd.DataFrame(columns=["User_ID", "weighted_Score"])
        df = self.data.copy()
        df["weighted_Score"] = df.apply(self.weighted_Score, axis=1)
        leaderboard = df.groupby("User_ID")["weighted_Score"].sum().reset_index()
        leaderboard = leaderboard.sort_values(by="weighted_Score", ascending=False).reset_index(drop=True)
        leaderboard.index += 1
        return leaderboard

    def train_weights(self, lr=0.0001, epochs=500):
        """
        Train Difficulty weights using Gradient Descent.
        Objective: Ensure higher Difficulty → proportionally higher effective Score.
        """
        difficulties = list(self.weights.keys())
        
        for _ in range(epochs):
            grads = {d: 0.0 for d in difficulties}

            # Compute gradients
            for _, row in self.data.iterrows():
                diff_index = self.Difficulty_map[row["Difficulty"]]
                weighted = row["Score"] * self.weights[row["Difficulty"]]
                target = (diff_index + 1) * row["Score"]  # ideal scaling
                error = weighted - target
                grads[row["Difficulty"]] += error * row["Score"]

            # Update weights
            for d in difficulties:
                self.weights[d] -= lr * grads[d]

        return self.weights

if __name__ == "__main__":
    lb = AdaptiveLeaderboard()

    # Load quiz results from external file
    lb.load_quiz_data("quiz_results.csv")



    print("\n📊 Subject Leaderboard: Optimization")
    print(lb.get_Subject_leaderboard("Optimization"))

    print("\n📊 Subject Leaderboard: GameTheory")
    print(lb.get_Subject_leaderboard("GameTheory"))

    print("\n🌍 Overall Leaderboard")
    print(lb.get_overall_leaderboard())


