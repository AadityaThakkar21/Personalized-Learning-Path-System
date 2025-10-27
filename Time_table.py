import streamlit as st
import pulp

def run():
    st.title("Personalized Study Timetable Generator")

    # --- Input section ---
    hours = st.number_input("Enter the number of free hours you have today:", min_value=0.5, step=0.5)
    subjects = st.number_input("Enter the number of subjects you wish to cover:", min_value=1, step=1)

    names = []
    priorities = []

    st.subheader("Enter details for each subject:")
    for i in range(subjects):
        col1, col2 = st.columns([3, 1])
        with col1:
            name = st.text_input(f"Subject {i+1} Name:", key=f"name_{i}")
        with col2:
            priority = st.number_input(f"Priority (1–5):", 1, 5, key=f"priority_{i}")
        names.append(name)
        priorities.append(priority)

    # --- Run optimization on button click ---
    if st.button("Generate Timetable"):
        try:
            M = float(hours)
            prob1 = pulp.LpProblem("stage1_max_count", pulp.LpMaximize)

            x1 = {i: pulp.LpVariable(f"x1_{i}", lowBound=0) for i in range(subjects)}
            y1 = {i: pulp.LpVariable(f"y1_{i}", cat="Binary") for i in range(subjects)}
            t1 = pulp.LpVariable("t1", lowBound=0)

            # maximize number of chosen subjects
            prob1 += pulp.lpSum(y1[i] for i in range(subjects))
            prob1 += pulp.lpSum(x1[i] for i in range(subjects)) <= hours

            for i in range(subjects):
                prob1 += x1[i] >= 0.5 * y1[i]
                prob1 += x1[i] <= hours * y1[i]
                p = priorities[i]
                prob1 += x1[i] - p * t1 <= M * (1 - y1[i])
                prob1 += -(x1[i] - p * t1) <= M * (1 - y1[i])

            prob1.solve(pulp.PULP_CBC_CMD(msg=0))
            k = int(round(sum(pulp.value(y1[i]) for i in range(subjects))))

            if k == 0:
                st.error("Not enough time to allocate at least 0.5 hour to any subject proportionally.")
                return

            # --- Stage 2 ---
            prob2 = pulp.LpProblem("stage2_max_time_given_k", pulp.LpMaximize)
            x2 = {i: pulp.LpVariable(f"x2_{i}", lowBound=0) for i in range(subjects)}
            y2 = {i: pulp.LpVariable(f"y2_{i}", cat="Binary") for i in range(subjects)}
            t2 = pulp.LpVariable("t2", lowBound=0)

            prob2 += pulp.lpSum(x2[i] for i in range(subjects))
            prob2 += pulp.lpSum(x2[i] for i in range(subjects)) <= hours
            prob2 += pulp.lpSum(y2[i] for i in range(subjects)) == k

            for i in range(subjects):
                prob2 += x2[i] >= 0.5 * y2[i]
                prob2 += x2[i] <= hours * y2[i]
                p = priorities[i]
                prob2 += x2[i] - p * t2 <= M * (1 - y2[i])
                prob2 += -(x2[i] - p * t2) <= M * (1 - y2[i])

            prob2.solve(pulp.PULP_CBC_CMD(msg=0))
            print('\n')
            st.success("✅ Optimal Study Plan:")
            for i in range(subjects):
                if pulp.value(y2[i]) is not None and pulp.value(y2[i]) > 0.5:
                    x = pulp.value(x2[i])
                    temp = int(x)
                    if (x - temp > 0.5):
                        x = temp + 0.5
                    else:
                        x = temp
                    st.write(f"📖 **{names[i]}:** {x} hours (Priority {priorities[i]})")

        except Exception as e:
            st.error(f"Error: {e}")

if __name__ == "__main__":
    run()
