import streamlit as st
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import string

def run():
    st.title("🎯 Student Performance Clustering Dashboard")

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
        def optimal_k(X, max_k=6):
            n_samples = X.shape[0]
            max_k = min(max_k, n_samples - 1)
            sil_scores = []
            for k in range(2, max_k + 1):
                km = KMeans(n_clusters=k, random_state=42, n_init=20)
                labels = km.fit_predict(X)
                if len(set(labels)) > 1:
                    sil_scores.append(silhouette_score(X, labels))
                else:
                    sil_scores.append(-1)
            best_k = np.argmax(sil_scores) + 2
            return best_k, sil_scores

        best_k, scores = optimal_k(scaled_data)

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

if __name__ == "__main__":
    run()
