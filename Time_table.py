import streamlit as st
import pulp
import matplotlib.pyplot as plt
import pandas as pd

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
        names.append(name)
        priorities.append(priority)
        min_times.append(min_time)

    # --- Run optimization ---
    if st.button("Generate Timetable"):
        try:
            M = float(total_hours)

            # Stage 1: choose max subjects possible
            prob1 = pulp.LpProblem("Stage1_Max_Subjects", pulp.LpMaximize)
            x1 = {i: pulp.LpVariable(f"x1_{i}", lowBound=0) for i in range(subjects)}
            y1 = {i: pulp.LpVariable(f"y1_{i}", cat="Binary") for i in range(subjects)}
            t1 = pulp.LpVariable("t1", lowBound=0)

            prob1 += pulp.lpSum(y1[i] for i in range(subjects))  # objective
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
                return

            # Stage 2: allocate hours to maximize utilization
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

            # --- Display results ---
            st.success("✅ Optimal Study Plan:")
            results = []
            for i in range(subjects):
                if pulp.value(y2[i]) > 0.5:
                    raw_time = pulp.value(x2[i])

                    # Round to nearest multiple of 0.5
                    rounded_time = round(raw_time * 2) / 2

                    results.append((names[i] or f"Subject {i+1}", rounded_time))
                    st.write(f"📖 **{names[i] or f'Subject {i+1}'}:** {rounded_time} hours (Priority {priorities[i]})")

            # --- Pie chart visualization ---
            if results:
                labels = [f"{r[0]} ({r[1]} hrs)" for r in results]
                sizes = [r[1] for r in results]

                fig, ax = plt.subplots()
                ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
                ax.axis('equal')
                st.pyplot(fig)
                
                df = pd.DataFrame(results, columns=["Subject", "Allocated Hours"])

                # Convert DataFrame to HTML and style it
                st.markdown(
                    df.to_html(index=False, justify="center", classes="center-table"),
                    unsafe_allow_html=True
                )

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
                
                
                if results:
                    st.markdown(
                    """
                    <div style="display: flex; justify-content: center; margin-bottom: 2rem;">
                        <a href="data:file/csv;base64,{csv_data}" download="study_plan.csv">
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
                    """.format(
                        csv_data=df.to_csv(index=False).encode('utf-8').decode('latin1')
                    ),
                    unsafe_allow_html=True
                )



                st.info("💡 Tip: Start with the highest priority subjects when your energy is highest!")
            
        except Exception as e:
            st.error(f"Error: {e}")

       

if __name__ == "__main__":
    run()
