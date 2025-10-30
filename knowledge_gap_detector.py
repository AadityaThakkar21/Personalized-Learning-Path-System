import pandas as pd
import streamlit as st
import os
from sklearn.cluster import KMeans
from sklearn.tree import DecisionTreeClassifier
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

# --------------------------------------------------
# Streamlit Setup
# --------------------------------------------------
st.set_page_config(page_title="Personalized Learning Insights", page_icon="🎓", layout="centered")

st.title("🎓 Personalized Learning Insights")
st.write("""
Welcome! This tool reviews your quiz results and gives you clear guidance on how you're doing across subjects.  
It also helps you see where to focus next — using smart pattern recognition in the background.
""")

# --------------------------------------------------
# Load Quiz Results
# --------------------------------------------------
csv_path = "quiz_results.csv"

if not os.path.exists(csv_path):
    st.error(f"❌ File not found: {csv_path}")
    st.stop()

df = pd.read_csv(csv_path)
df.columns = [c.strip().lower() for c in df.columns]

required_cols = {"user_id", "subject", "difficulty", "score", "total"}
if not required_cols.issubset(set(df.columns)):
    st.error(f"⚠ Missing required columns. Expected: {required_cols}")
    st.stop()

df["accuracy"] = df["score"] / df["total"]

# --------------------------------------------------
# User Input
# --------------------------------------------------
st.subheader("👤 Enter Your User ID")
user_id_input = st.text_input("Enter your User ID (e.g., 101, 102, 103):").strip()

if not user_id_input:
    st.info("Please enter your User ID to see your learning insights.")
    st.stop()

try:
    if df["user_id"].dtype != object:
        user_data = df[df["user_id"] == int(user_id_input)]
    else:
        user_data = df[df["user_id"].astype(str) == user_id_input]
except ValueError:
    st.error("⚠ Invalid input! Please enter a valid User ID number.")
    st.stop()

if user_data.empty:
    st.warning("No quiz data found for this User ID.")
    st.stop()

# --------------------------------------------------
# Subject Accuracy Summary
# --------------------------------------------------
subject_summary = (
    user_data.groupby("subject")["accuracy"]
    .mean()
    .reset_index()
    .sort_values(by="accuracy", ascending=False)
)

st.subheader("📘 Your Subject Performance")
st.dataframe(subject_summary.style.format({"accuracy": "{:.2%}"}), use_container_width=True)

# --------------------------------------------------
# Personalized Recommendations (simple rule-based)
# --------------------------------------------------
def get_recommendation(acc):
    if acc >= 0.9:
        return "🌟 Excellent! Keep maintaining your high performance."
    elif acc >= 0.75:
        return "👍 Good work! A little more practice can make you perfect."
    elif acc >= 0.5:
        return "🟡 You can do better — revise your notes and take more practice quizzes."
    else:
        return "🔴 Needs improvement — focus on basics and regular revision."

subject_summary["Recommendation"] = subject_summary["accuracy"].apply(get_recommendation)

st.subheader("💡 Personalized Recommendations")
st.dataframe(subject_summary.style.format({"accuracy": "{:.2%}"}), use_container_width=True)

# --------------------------------------------------
# Study Focus Analysis (K-Means Clustering)
# --------------------------------------------------
st.divider()
st.subheader("🎯 Your Study Focus Levels")
st.write("""
We’ve analyzed your results and grouped your subjects into **focus levels**.  
These levels show which subjects you’re strong in and which ones may need more attention.
""")

# Run K-Means
X = subject_summary[["accuracy"]].values
kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
subject_summary["cluster"] = kmeans.fit_predict(X)

# Sort clusters by mean accuracy and relabel
cluster_means = subject_summary.groupby("cluster")["accuracy"].mean().sort_values().index
labels = {cluster_means[0]: "Focus First", cluster_means[1]: "Needs Attention", cluster_means[2]: "Strong Area"}
subject_summary["Focus_Level"] = subject_summary["cluster"].map(labels)

st.dataframe(
    subject_summary[["subject", "accuracy", "Focus_Level", "Recommendation"]]
    .style.format({"accuracy": "{:.2%}"}),
    use_container_width=True
)

# Add color-coded interpretation
st.markdown("""
### 🧠 What This Means for You:
- **Strong Area** → You're confident here! Keep practicing to stay sharp.  
- **Needs Attention** → You're doing fine but could use some extra review.  
- **Focus First** → Spend more time here — this will help you improve fastest.
""")

# Optional visual chart
fig, ax = plt.subplots(figsize=(6, 4))
sns.barplot(data=subject_summary, x="subject", y="accuracy", hue="Focus_Level", palette="coolwarm", ax=ax)
ax.set_title("Your Study Focus Overview")
st.pyplot(fig)

# --------------------------------------------------
# Predict Future Strength (Decision Tree)
# --------------------------------------------------
st.divider()
st.subheader("🔮 Predicted Future Performance")
st.write("""
We’ve reviewed how you and other students performed to **predict your likely strong and weak areas**  
in upcoming quizzes. Think of this as your “next-step learning forecast.”
""")

df["label"] = (df["accuracy"] >= 0.75).astype(int)
X = pd.get_dummies(df[["subject", "difficulty"]], drop_first=True)
y = df["label"]

model = DecisionTreeClassifier(max_depth=3, random_state=42)
model.fit(X, y)

user_features = pd.get_dummies(user_data[["subject", "difficulty"]], drop_first=True)
user_features = user_features.reindex(columns=X.columns, fill_value=0)
preds = model.predict(user_features)
user_data["Predicted_Strength"] = ["Strong" if p == 1 else "Needs Improvement" for p in preds]

st.dataframe(user_data[["subject", "difficulty", "score", "total", "Predicted_Strength"]])

st.markdown("""
### 📋 Tip:
Subjects predicted as **"Needs Improvement"** are the best places to invest your next few study hours.  
These are areas where small effort can lead to big progress!
""")

# --------------------------------------------------
# Export Option
# --------------------------------------------------
st.divider()
save_csv = st.checkbox("📂 Save this personalized report")
if save_csv:
    report_name = f"learning_report_{user_id_input}.csv"
    subject_summary.to_csv(report_name, index=False)
    st.success(f"✅ Report saved as {report_name}")

# --------------------------------------------------
# Summary Section (friendly version)
# --------------------------------------------------
st.divider()
st.markdown("""
## 🌟 Summary of Your Learning Insights

- You now know **which subjects are your strongest**, and where to **focus more time**.  
- Your **Study Focus Levels** were determined based on how you perform across all topics.  
- A simple **forecast** also predicts which areas may need more practice in future.  

Keep challenging yourself with new quizzes and review the “Focus First” subjects often —  
that’s how real improvement happens! 💪
""")
