import streamlit as st
import pulp
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, time

def logical_optimization(total_hours, subjects, names, priorities, min_times):
    """Two-stage linear optimization without energy levels."""
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
            results.append((names[i] or f"Subject {i+1}", rounded_time, priorities[i]))
    return results


def entropy_distribution(total_hours, names, priorities, min_times):
    """Entropy-based (Softmax) direct allocation."""
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
    final_times = np.round(final_times * 2) / 2

    results = []
    for i in range(n):
        results.append((names[i], final_times[i], priorities[i]))
    return results


def pareto_optimization(total_hours, subjects, names, priorities, min_times, difficulty_levels):
    """Multi-objective optimization balancing priority and difficulty."""
    min_total = sum(min_times)
    if min_total > total_hours:
        st.error("Total hours too small for minimum time requirements.")
        return []
    
    # Normalize priorities and difficulties
    norm_priorities = np.array(priorities) / 5.0
    norm_difficulties = np.array(difficulty_levels) / 5.0
    
    # Combined score: higher priority + higher difficulty gets more time
    combined_scores = 0.6 * norm_priorities + 0.4 * norm_difficulties
    
    remaining = total_hours - min_total
    weights = np.exp(combined_scores * 2)
    softmax_weights = weights / np.sum(weights)
    
    extra_time = remaining * softmax_weights
    final_times = np.array(min_times) + extra_time
    final_times = np.round(final_times * 2) / 2
    
    results = []
    for i in range(subjects):
        results.append((names[i], final_times[i], priorities[i]))
    return results


def schedule_with_breaks(results, start_time, break_interval=1.5, break_duration=0.25):
    """Generate time-blocked schedule with breaks."""
    schedule = []
    current_time = start_time
    
    for subj, hrs, _ in results:
        remaining = hrs
        while remaining > 0:
            study_block = min(remaining, break_interval)
            end_time = current_time + timedelta(hours=study_block)
            schedule.append({
                'subject': subj,
                'start': current_time.strftime('%I:%M %p'),
                'end': end_time.strftime('%I:%M %p'),
                'duration': study_block,
                'type': 'study'
            })
            current_time = end_time
            remaining -= study_block
            
            if remaining > 0:
                break_end = current_time + timedelta(hours=break_duration)
                schedule.append({
                    'subject': '☕ Break',
                    'start': current_time.strftime('%I:%M %p'),
                    'end': break_end.strftime('%I:%M %p'),
                    'duration': break_duration,
                    'type': 'break'
                })
                current_time = break_end
    
    return schedule


def run():
    st.title("📅 Advanced Study Timetable Generator")
    st.markdown("*Optimize your study time with AI-powered scheduling*")

    # Sidebar
    with st.sidebar:
        st.header("⚙️ Advanced Settings")
        enable_schedule = st.checkbox("Generate Time-Blocked Schedule", value=False)
        if enable_schedule:
            start_time = st.time_input("Start Time:", value=time(9, 0))
            break_interval = st.slider("Study block duration (hrs):", 0.5, 3.0, 1.5, 0.5)
            break_duration = st.slider("Break duration (hrs):", 0.1, 0.5, 0.25, 0.05)

    total_hours = st.number_input("Enter the number of free hours you have today:", min_value=0.5, step=0.5, value=6.0)
    subjects = st.number_input("Enter the number of subjects you wish to cover:", min_value=1, step=1, value=3)

    names, priorities, min_times, difficulty_levels = [], [], [], []
    
    st.subheader("Enter details for each subject:")
    for i in range(subjects):
        with st.expander(f"📚 Subject {i+1}", expanded=(i==0)):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input(f"Subject Name:", key=f"name_{i}", value=f"Subject {i+1}")
                priority = st.select_slider("Priority:", options=[1,2,3,4,5], value=3, key=f"priority_{i}")
                min_time = st.number_input("Minimum time (hrs):", min_value=0.0, step=0.5, key=f"min_{i}", value=0.5)
            with col2:
                difficulty = st.select_slider("Difficulty:", options=[1,2,3,4,5], value=3, key=f"diff_{i}")
                difficulty_levels.append(difficulty)
            
            names.append(name or f"Subject {i+1}")
            priorities.append(priority)
            min_times.append(min_time)

    # Mode selection
    st.subheader("🎯 Select Optimization Mode:")
    mode = st.radio(
        "",
        [
            "Smart Auto (Logical Optimization)",
            "Entropy (Softmax Distribution)",
            "Pareto (Multi-Objective Balance)"
        ],
        captions=[
            "Mathematical LP-based exact allocation with constraint satisfaction.",
            "Smooth exponential priority-based distribution.",
            "Balances both priority AND difficulty for optimal learning."
        ]
    )

    # Generate button
    if st.button("Generate Optimal Timetable", type="primary"):
        try:
            if mode == "Smart Auto (Logical Optimization)":
                results = logical_optimization(total_hours, subjects, names, priorities, min_times)
                mode_name = "Smart Auto"
            elif mode == "Entropy (Softmax Distribution)":
                results = entropy_distribution(total_hours, names, priorities, min_times)
                mode_name = "Entropy"
            else:
                results = pareto_optimization(total_hours, subjects, names, priorities, min_times, difficulty_levels)
                mode_name = "Pareto"

            if not results:
                return

            st.success(f"✅ Optimal Study Plan Generated ({mode_name})")

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Subjects", len(results))
            with col2:
                allocated = sum(r[1] for r in results)
                st.metric("Hours Allocated", f"{allocated:.1f}")
            with col3:
                utilization = (allocated / total_hours) * 100
                st.metric("Time Utilization", f"{utilization:.1f}%")

            st.subheader("📊 Study Allocation")
            for subj, hrs, prio in results:
                st.write(f"📖 **{subj}:** {hrs} hours | Priority: {'⭐' * prio}")

            col1, col2 = st.columns(2)
            with col1:
                labels = [r[0] for r in results]
                sizes = [r[1] for r in results]
                colors = plt.cm.Set3(range(len(results)))
                fig, ax = plt.subplots(figsize=(8, 6))
                ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors)
                ax.axis('equal')
                plt.title('Time Distribution')
                st.pyplot(fig)

            with col2:
                fig, ax = plt.subplots(figsize=(8, 6))
                subjects_names = [r[0] for r in results]
                hours = [r[1] for r in results]
                colors_bar = plt.cm.viridis(np.linspace(0, 1, len(results)))
                ax.barh(subjects_names, hours, color=colors_bar)
                ax.set_xlabel('Hours')
                ax.set_title('Hours per Subject')
                ax.grid(axis='x', alpha=0.3)
                st.pyplot(fig)

            if enable_schedule:
                st.subheader("🕐 Time-Blocked Schedule")
                schedule_start = datetime.combine(datetime.today(), start_time)
                schedule = schedule_with_breaks(results, schedule_start, break_interval, break_duration)
                
                for item in schedule:
                    if item['type'] == 'study':
                        st.info(f"**{item['start']} - {item['end']}**: {item['subject']} ({item['duration']} hrs)")
                    else:
                        st.success(f"**{item['start']} - {item['end']}**: {item['subject']} ({item['duration']} hrs)")

            df = pd.DataFrame(results, columns=["Subject", "Hours", "Priority"])
            st.subheader("📋 Summary Table")
            st.dataframe(df, use_container_width=True)

            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 Download Study Plan (CSV)",
                data=csv,
                file_name=f"study_plan_{mode_name.lower()}_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )

            st.subheader("💡 Insights")
            if mode == "Pareto (Multi-Objective Balance)":
                st.info("Pareto optimization balances priority with difficulty—harder subjects with higher priority get proportionally more time.")
            elif mode == "Entropy (Softmax Distribution)":
                st.info("Entropy mode uses exponential weighting—small priority differences create larger time allocation gaps.")
            else:
                st.info("Smart Auto ensures all minimum time requirements are met while maximizing subject coverage.")

        except Exception as e:
            st.error(f"❌ Error: {e}")
            st.exception(e)


if __name__ == "__main__":
    run()
