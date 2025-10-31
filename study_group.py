import streamlit as st
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import string

def run():
    st.title("👥 Student Performance Clustering Dashboard")

    with st.spinner("⏳ Loading... please wait while we process and compute everything."):
        # 1. loading data
        data = pd.read_csv("quiz_results.csv")

        # remove spaces, lowercase them
        data.columns = data.columns.str.strip().str.lower()

        # Map difficulty
        difficulty_map = {"easy": 1, "intermediate": 2, "hard": 3}
        data["difficulty"] = data["difficulty"].str.strip().str.lower()
        data["difficulty_num"] = data["difficulty"].map(difficulty_map)
        data["score_percent"] = (data["score"] / data["total"]) * 100

        # aggregate by student
        student_perf = (
            data.groupby("user_id")
            .agg(
                Avg_Score=("score_percent", "mean"),
                Attempts=("score_percent", "count"),
                Avg_Difficulty=("difficulty_num", "mean"),
            )
            .reset_index()
        )

        # feature scaling
        features = ["Avg_Score", "Attempts", "Avg_Difficulty"]
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(student_perf[features])

        # optimal cluster finder
        def optimal_k(scaled_data):
            sil_scores = []
            possible_k = range(2, 10)  # or whatever range you use

            for k in possible_k:
                if len(scaled_data) < k:
                    continue  # skip if not enough samples for this k
                try:
                    kmeans = KMeans(n_clusters=k, random_state=42)
                    labels = kmeans.fit_predict(scaled_data)
                    score = silhouette_score(scaled_data, labels)
                    sil_scores.append(score)
                except Exception as e:
                    print(f"Skipping k={k} due to error: {e}")
                    continue

            if not sil_scores:  # nothing collected
                raise ValueError("No valid silhouette scores could be computed. "
                         "Check your data or clustering parameters.")

            best_k = np.argmax(sil_scores) + 2  # +2 since range starts from 2
            return best_k

        best_k = optimal_k(scaled_data)
        # perform K-means
        kmeans = KMeans(n_clusters=best_k, random_state=42, n_init=30)
        student_perf["Cluster"] = kmeans.fit_predict(scaled_data)
        group_labels = list(string.ascii_uppercase)
        label_map = {i: group_labels[i] for i in range(best_k)}
        student_perf["Group"] = student_perf["Cluster"].map(label_map)

        # Prepare data without cluster/group columns for display
        student_display = student_perf.drop(columns=["Cluster", "Group"])

    st.success("✅ All computations completed successfully!")

    st.subheader("📊 Aggregated Student Data")
    st.dataframe(student_display)

    st.write(f"✅ Optimal number of clusters found: {best_k}")

    # show groups and members
    st.subheader("👥 Ideal Groups with respective Student IDs")
    for grp in sorted(student_perf["Group"].unique()):
        members = student_perf.loc[student_perf["Group"] == grp, "user_id"].tolist()
        st.write(f"**Group {grp}:** {', '.join(map(str, members))}")

    # Compare Scores Feature
    
    st.subheader("📈 Compare Scores Between Two Users")

    compare_choice = st.radio(
        "Would you like to compare performance between two users?",
        ("No", "Yes"),
        index=0
    )

    if compare_choice == "Yes":
        user1 = st.selectbox("Select first User ID:", student_perf["user_id"].unique())
        user2 = st.selectbox("Select second User ID:", student_perf["user_id"].unique())


        if st.button("Compare Now"):
            try:
                user1 = int(user1)
                user2 = int(user2)
            except ValueError:
                st.error("⚠️ Please enter valid numeric User IDs.")
                return

            if user1 not in student_perf["user_id"].values or user2 not in student_perf["user_id"].values:
                st.error("❌ One or both User IDs do not exist in the dataset.")
            else:
                user1_data = student_perf[student_perf["user_id"] == user1].iloc[0]
                user2_data = student_perf[student_perf["user_id"] == user2].iloc[0]

                st.write("### 🔍 Performance Comparison")
                comparison_df = pd.DataFrame({
                    "Metric": ["Average Score (%)", "Attempts", "Average Difficulty"],
                    f"User {user1}": [round(user1_data["Avg_Score"], 2), int(user1_data["Attempts"]), round(user1_data["Avg_Difficulty"], 2)],
                    f"User {user2}": [round(user2_data["Avg_Score"], 2), int(user2_data["Attempts"]), round(user2_data["Avg_Difficulty"], 2)],
                })
                st.dataframe(comparison_df)

                st.info(f"🧩 User {user1} belongs to Group **{user1_data['Group']}**, while User {user2} belongs to Group **{user2_data['Group']}**.")

    # Peer Recommendation Feature
    
    st.subheader("🤝 Peer Recommender")

    recommend_choice = st.radio(
        "Would you like us to help you find a study partner?",
        ("No", "Yes"),
        index=0
    )

    if recommend_choice == "Yes":
        st.markdown("""
        **What does λ (lambda) mean?**  
        Lambda controls how much importance we give to *score similarity* compared to *difficulty similarity* when finding a study partner:
        - A **lower λ (e.g., 0.2)** → prioritizes students who attempt **similar difficulty** quizzes.
        - A **higher λ (e.g., 0.8)** → prioritizes students with **similar scores/performance**.
        - A **balanced λ (e.g., 0.4)** → considers both difficulty and score equally.

        Try tuning it to see which type of peer you’d prefer to collaborate with!
        """)
        target_id = st.selectbox(
            "Enter your User ID to find a suitable peer:",
            student_perf["user_id"].unique()
        )

        lambda_param = st.number_input(
            "Enter your preferred λ (lambda) value (0.0 - 1.0):",
            min_value=0.0,
            max_value=1.0,
            value=0.4,
            step=0.1,
            help="Lower λ → prioritize similar difficulty. Higher λ → prioritize similar performance."
        )

        if st.button("🔍 Recommend Peer"):
            target = student_perf[student_perf["user_id"] == target_id].iloc[0]

            def objective(row):
                difficulty_diff = abs(row["Avg_Difficulty"] - target["Avg_Difficulty"])
                score_diff = abs(row["Avg_Score"] - target["Avg_Score"])
                # Optimization goal: minimize total difference weighted by lambda
                return difficulty_diff + lambda_param * score_diff

            candidates = student_perf[student_perf["user_id"] != target_id].copy()
            candidates["match_score"] = candidates.apply(objective, axis=1)

            # Find the closest match (lowest combined distance)
            best_peer = candidates.loc[candidates["match_score"].idxmin()]

            st.success(f"💡 **Recommended Peer for User {target_id}: User {int(best_peer['user_id'])}**")

            # Show comparison table
            rec_df = pd.DataFrame({
                "Metric": ["Average Score (%)", "Attempts", "Average Difficulty"],
                f"User {target_id}": [
                    round(target["Avg_Score"], 2),
                    int(target["Attempts"]),
                    round(target["Avg_Difficulty"], 2)
                ],
                f"User {int(best_peer['user_id'])}": [
                    round(best_peer["Avg_Score"], 2),
                    int(best_peer["Attempts"]),
                    round(best_peer["Avg_Difficulty"], 2)
                ],
            })

            st.dataframe(rec_df)

        
if __name__ == "__main__":
    run()
