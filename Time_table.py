import streamlit as st
import pulp
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

def logical_optimization(total_hours, subjects, names, priorities, min_times):
    """Your existing two-stage linear optimization method."""
    M = float(total_hours)

    # Stage 1: Max subjects possible
    prob1 = pulp.LpProblem("Stage1_Max_Subjects", pulp.LpMaximize)
    x1 = {i: pulp.LpVariable(f"x1_{i}", lowBound=0) for i in range(subjects)}
    y1 = {i: pulp.LpVariable(f"y1_{i}", cat="Binary") for i in range(subjects)}
    t1 = pulp.LpVariable("t1", lowBound=0)

    prob1 += pulp.lpSum(y1[i] for i in range(subjects))
    prob1 += pulp.lpSum(x1[i] for i in range(subjects)) <= total_hours

    for i in range(subjects):
        prob1 += x1[i] >= min_times[i] * y1[i]
        prob1 += x1[i] <= total_hours * y1[i]
        p = priorities[i]
        prob1 += x1[i] - p * t1 <= M * (1 - y1[i])
        prob1 += -(x1[i] - p * t1) <= M * (1 - y1[i])

    prob1.solve(pulp.PULP_CBC_CMD(msg=0))
    k = int(round(sum(pulp.value(y1[i]) for i in range(subjects))))

    if k == 0:
        st.error("Not enough total hours to satisfy the minimum time constraints.")
        return []

    # Stage 2: Allocate hours to maximize utilization
    prob2 = pulp.LpProblem("Stage2_Max_Time", pulp.LpMaximize)
    x2 = {i: pulp.LpVariable(f"x2_{i}", lowBound=0) for i in range(subjects)}
    y2 = {i: pulp.LpVariable(f"y2_{i}", cat="Binary") for i in range(subjects)}
    t2 = pulp.LpVariable("t2", lowBound=0)

    prob2 += pulp.lpSum(x2[i] for i in range(subjects))
    prob2 += pulp.lpSum(x2[i] for i in range(subjects)) <= total_hours
    prob2 += pulp.lpSum(y2[i] for i in range(subjects)) == k

    for i in range(subjects):
        prob2 += x2[i] >= min_times[i] * y2[i]
        prob2 += x2[i] <= total_hours * y2[i]
        p = priorities[i]
        prob2 += x2[i] - p * t2 <= M * (1 - y2[i])
        prob2 += -(x2[i] - p * t2) <= M * (1 - y2[i])

    prob2.solve(pulp.PULP_CBC_CMD(msg=0))

    results = []
    for i in range(subjects):
        if pulp.value(y2[i]) > 0.5:
            raw_time = pulp.value(x2[i])
            rounded_time = round(raw_time * 2) / 2
            results.append((names[i] or f"Subject {i+1}", rounded_time))
    return results


def entropy_distribution(total_hours, names, priorities, min_times):
    """New Mode: Entropy-based (Softmax) direct allocation."""
    n = len(names)
    min_total = sum(min_times)

    if min_total > total_hours:
        st.error("Total hours too small for minimum time requirements.")
        return []

    remaining = total_hours - min_total
    weights = np.exp(priorities)
    softmax_weights = weights / np.sum(weights)

    extra_time = remaining * softmax_weights
    final_times = np.array(min_times) + extra_time
    final_times = np.round(final_times * 2) / 2  # round to nearest 0.5 hr

    return list(zip(names, final_times))


def run():
    st.title("📅 Personalized Study Timetable Generator")

    # --- Input section ---
    total_hours = st.number_input("Enter the number of free hours you have today:", min_value=0.5, step=0.5)
    subjects = st.number_input("Enter the number of subjects you wish to cover:", min_value=1, step=1)

    names, priorities, min_times = [], [], []
    st.subheader("Enter details for each subject:")

    for i in range(subjects):
        col1, col2, col3 = st.columns([3, 1, 2])
        with col1:
            name = st.text_input(f"Subject {i+1} Name:", key=f"name_{i}")
        with col2:
            priority = st.number_input("Priority (1–5):", 1, 5, key=f"priority_{i}")
        with col3:
            min_time = st.number_input("Min time (hrs):", min_value=0.0, step=0.5, key=f"min_{i}")
        names.append(name or f"Subject {i+1}")
        priorities.append(priority)
        min_times.append(min_time)

    # --- Mode selection ---
    st.subheader("⚙️ Select Optimization Mode:")
    mode = st.radio(
        "",
        ["Default (Smart Auto - Logical Optimization)", "Entropy (Softmax Priority Distribution)"],
        captions=[
            "Mathematical LP-based exact allocation (two-stage optimization).",
            "Smooth, instant, exponential priority-based time allocation."
        ]
    )

    # --- Run the chosen method ---
    if st.button("Generate Timetable"):
        try:
            if mode == "Default (Smart Auto - Logical Optimization)":
                results = logical_optimization(total_hours, subjects, names, priorities, min_times)
                mode_name = "Smart Auto (Logical Optimization)"
            else:
                results = entropy_distribution(total_hours, names, priorities, min_times)
                mode_name = "Entropy (Softmax Distribution)"

            if not results:
                return

            # --- Display results ---
            st.success(f"✅ Optimal Study Plan ({mode_name})")
            for subj, hrs in results:
                st.write(f"📖 **{subj}:** {hrs} hours")

            # --- Pie chart visualization ---
            labels = [f"{r[0]} ({r[1]} hrs)" for r in results]
            sizes = [r[1] for r in results]

            fig, ax = plt.subplots()
            ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
            ax.axis('equal')
            st.pyplot(fig)

            # --- Table output ---
            df = pd.DataFrame(results, columns=["Subject", "Allocated Hours"])
            st.markdown(df.to_html(index=False, justify="center", classes="center-table"), unsafe_allow_html=True)
            st.markdown("""
                <style>
                .center-table {
                    margin-left: auto;
                    margin-right: auto;
                    text-align: center !important;
                    border-collapse: collapse;
                }
                .center-table th, .center-table td {
                    text-align: center !important;
                    padding: 8px 16px;
                    border: 1px solid #ddd;
                }
                .center-table th {
                    font-weight: 600;
                }
                </style>
            """, unsafe_allow_html=True)

            # --- Download button ---
            st.markdown(
                f"""
                <div style="display: flex; justify-content: center; margin-bottom: 2rem;">
                    <a href="data:file/csv;base64,{df.to_csv(index=False).encode('utf-8').decode('latin1')}" download="study_plan_{mode_name.lower().replace(' ', '_')}.csv">
                        <button style="
                            color:white;
                            background-color: black;
                            border:none;
                            padding:10px 20px;
                            border-radius:8px;
                            cursor:pointer;
                            font-size:16px;">
                            📥 Download Study Plan
                        </button>
                    </a>
                </div>
                """,
                unsafe_allow_html=True
            )

            if mode == "Entropy (Softmax Priority Distribution)":
                st.info("💡 Entropy mode uses exponential weighting — higher priorities grow rapidly.")
            else:
                st.info("💡 Smart Auto mode uses constraint-based optimization to balance priorities and time limits.")

        except Exception as e:
            st.error(f"Error: {e}")


if __name__ == "__main__":
    run()
