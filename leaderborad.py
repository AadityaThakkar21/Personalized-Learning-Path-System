import pandas as pd  

class AdaptiveLeaderboard:
    def __init__(self):
        # Store quiz results
        self.data = pd.DataFrame(columns=["userid", "subject", "score", "difficulty"])
        
        # Initialize weights equally
        self.weights = {"Easy": 1.0, "Intermediate": 1.0, "Hard": 1.0}
        
        # Difficulty ordering (used for target ranking)
        self.difficulty_map = {"Easy": 0, "Intermediate": 1, "Hard": 2}

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
            return pd.DataFrame(columns=["userid", "weighted_score"])
        df["weighted_score"] = df.apply(self.weighted_score, axis=1)
        leaderboard = df.groupby("userid")["weighted_score"].sum().reset_index()
        leaderboard = leaderboard.sort_values(by="weighted_score", ascending=False).reset_index(drop=True)
        leaderboard.index += 1
        return leaderboard

    def get_overall_leaderboard(self):
        """Overall leaderboard across all subjects."""
        if self.data.empty:
            return pd.DataFrame(columns=["userid", "weighted_score"])
        df = self.data.copy()
        df["weighted_score"] = df.apply(self.weighted_score, axis=1)
        leaderboard = df.groupby("userid")["weighted_score"].sum().reset_index()
        leaderboard = leaderboard.sort_values(by="weighted_score", ascending=False).reset_index(drop=True)
        leaderboard.index += 1
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


# ---------------- Example Usage ----------------
if __name__ == "__main__":
    lb = AdaptiveLeaderboard()

    # Add quiz results (userid starts from 101)
    lb.add_quiz_result(101, "Optimization", 80, "Easy")
    lb.add_quiz_result(102, "Optimization", 90, "Intermediate")
    lb.add_quiz_result(101, "GameTheory", 70, "Hard")
    lb.add_quiz_result(103, "GameTheory", 85, "Intermediate")
    lb.add_quiz_result(102, "Transportation", 75, "Hard")
    lb.add_quiz_result(103, "Transportation", 65, "Easy")


    print("\n📊 Subject Leaderboard: Optimization")
    print(lb.get_subject_leaderboard("Optimization"))

    print("\n📊 Subject Leaderboard: GameTheory")
    print(lb.get_subject_leaderboard("GameTheory"))

    print("\n🌍 Overall Leaderboard")
    print(lb.get_overall_leaderboard())
