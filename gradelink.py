import streamlit as st
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import plotly.graph_objects as go
import plotly.express as px

# Configuration
DEFAULT_COURSE_NAME = 'Calculus I'
DEFAULT_TARGET_GRADE = 90.0
DEFAULT_COURSE_CREDITS = 3.0

def initialize_data():
    """Initialize session state with default data"""
    if 'gpa_scale' not in st.session_state:
        st.session_state.gpa_scale = pd.DataFrame({
            'Letter Grade': ['A+', 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D', 'F'],
            'Min Grade (%)': [97.0, 93.0, 90.0, 87.0, 83.0, 80.0, 77.0, 73.0, 70.0, 67.0, 60.0, 0.0],
            'GPA Value': [4.0, 4.0, 3.7, 3.3, 3.0, 2.7, 2.3, 2.0, 1.7, 1.3, 1.0, 0.0]
        })

    if 'gpa_data' not in st.session_state:
        st.session_state.gpa_data = {}

    if not st.session_state.gpa_data:
        st.session_state.gpa_data[DEFAULT_COURSE_NAME] = {
            'Course Credits': DEFAULT_COURSE_CREDITS,
            'Target Course Grade (%)': DEFAULT_TARGET_GRADE,
            'assignments': pd.DataFrame({
                'Type': ['Homework', 'Quiz', 'Midterm', 'Final Exam', 'Project'],
                'Weight (%)': [20, 15, 25, 30, 10],
                'Assignment Name': ['HW Average', 'Quiz 1', 'Midterm 1', 'Final Exam', 'Term Project'],
                'Grade (%)': [85.0, 92.0, 88.0, None, None],
                'Completed': [True, True, True, False, False],
                'Study Hours': [10, 3, 15, None, None]
            })
        }

    if 'current_course' not in st.session_state:
        st.session_state.current_course = DEFAULT_COURSE_NAME
    if 'manage_mode' not in st.session_state:
        st.session_state.manage_mode = 'details'

# ML Feature 1: Grade Trend Prediction
def predict_final_grade_ml(course_data):
    """Use Linear Regression to predict final grade based on performance trend"""
    df = course_data['assignments'].copy()
    completed = df[df['Completed'] == True].copy()
    
    if len(completed) < 2:
        return None, None, "Need more data"
    
    completed['sequence'] = range(len(completed))
    X = completed[['sequence']].values
    y = completed['Grade (%)'].values
    
    model = LinearRegression()
    model.fit(X, y)
    
    future_sequence = len(df) - 1
    predicted_grade = model.predict([[future_sequence]])[0]
    
    slope = model.coef_[0]
    
    if slope > 1:
        trend = "📈 Improving"
    elif slope < -1:
        trend = "📉 Declining"
    else:
        trend = "➡️ Stable"
    
    return max(0, min(100, predicted_grade)), slope, trend

# ML Feature 2: Goal Achievement Assessment
def assess_goal_achievement(course_data, target_grade):
    """
    Simple assessment: Will you likely meet your target?
    Green = On track, Yellow = At risk, Red = Unlikely without major improvement
    """
    df = course_data['assignments'].copy()
    completed = df[df['Completed'] == True]
    
    if len(completed) == 0:
        return "⚪ No Data Yet", "Start completing assignments to see your progress"
    
    # Calculate current average
    avg_grade = completed['Grade (%)'].mean()
    
    # Simple logic: compare average to target
    gap = target_grade - avg_grade
    
    if gap <= 0:
        return "🟢 On Track", f"Your average ({avg_grade:.1f}%) meets or exceeds target ({target_grade:.1f}%)"
    elif gap <= 10:
        return "🟡 Close to Target", f"You're {gap:.1f}% away from target. Keep pushing!"
    else:
        return "🔴 Need Improvement", f"You're {gap:.1f}% below target. Focus on upcoming assignments!"

# ML Feature 3: Optimal Study Time Allocation
def optimize_study_time(course_data, available_hours):
    """Allocate study time optimally across remaining assignments"""
    df = course_data['assignments'].copy()
    remaining = df[df['Completed'] == False].copy()
    
    if len(remaining) == 0:
        return None
    
    remaining['priority_score'] = remaining['Weight (%)']
    total_priority = remaining['priority_score'].sum()
    remaining['recommended_hours'] = (remaining['priority_score'] / total_priority) * available_hours
    remaining['recommended_hours'] = remaining['recommended_hours'].round(1)
    
    return remaining[['Assignment Name', 'Weight (%)', 'recommended_hours']]

# ML Feature 4: Performance Insights
def generate_ml_insights(course_data, target_grade):
    """Generate insights and recommendations"""
    df = course_data['assignments'].copy()
    completed = df[df['Completed'] == True]
    
    insights = []
    
    if len(completed) > 0:
        avg_grade = completed['Grade (%)'].mean()
        
        if avg_grade >= target_grade:
            insights.append(f"✅ Your average ({avg_grade:.1f}%) exceeds your target ({target_grade:.1f}%)")
        else:
            gap = target_grade - avg_grade
            insights.append(f"⚠️ You're {gap:.1f}% below your target on average")
        
        std = completed['Grade (%)'].std()
        if std > 10:
            insights.append("📊 Your grades vary significantly. Try to be more consistent")
        else:
            insights.append("📊 Your performance is consistent - great job!")
        
        if len(completed) > 1:
            best_assignment = completed.loc[completed['Grade (%)'].idxmax(), 'Assignment Name']
            worst_assignment = completed.loc[completed['Grade (%)'].idxmin(), 'Assignment Name']
            insights.append(f"🌟 Best: {best_assignment} | 📚 Study more: {worst_assignment}")
        
        if 'Study Hours' in completed.columns and completed['Study Hours'].notna().any():
            completed_with_hours = completed[completed['Study Hours'].notna()]
            if len(completed_with_hours) > 0:
                completed_with_hours['efficiency'] = completed_with_hours['Grade (%)'] / completed_with_hours['Study Hours']
                avg_efficiency = completed_with_hours['efficiency'].mean()
                insights.append(f"⏱️ Avg efficiency: {avg_efficiency:.1f} points per study hour")
    
    return insights

# Core Calculations
def calculate_course_grade(course_data):
    """Calculate current and projected grades"""
    df = course_data['assignments'].copy()
    
    total_weight = df['Weight (%)'].sum()
    if total_weight == 0:
        return 0.0, 0.0, 0.0, 0.0
    
    df['Normalized Weight'] = df['Weight (%)'] / 100
    df['Weighted Score'] = np.where(df['Completed'], df['Normalized Weight'] * df['Grade (%)'], 0.0)
    
    weighted_completed_grade = df['Weighted Score'].sum()
    total_completed_weight = df[df['Completed'] == True]['Weight (%)'].sum()
    
    if total_completed_weight > 0:
        current_grade = (weighted_completed_grade / (total_completed_weight / 100))
    else:
        current_grade = 0.0
    
    projected_final_grade = weighted_completed_grade
    
    return current_grade, weighted_completed_grade, total_completed_weight, projected_final_grade

def optimize_required_score(course_data, target_grade):
    """Calculate required score on remaining work"""
    df = course_data['assignments'].copy()
    
    df['Normalized Weight'] = df['Weight (%)'] / 100
    df['Weighted Completed Grade'] = np.where(df['Completed'], df['Normalized Weight'] * df['Grade (%)'], 0.0)
    weighted_completed_grade = df['Weighted Completed Grade'].sum()
    
    remaining_weight_percent = df[df['Completed'] == False]['Weight (%)'].sum()
    remaining_weight_normalized = remaining_weight_percent / 100

    if remaining_weight_normalized == 0:
        _, _, _, final_grade = calculate_course_grade(course_data)
        required_score = final_grade
    else:
        required_weighted_remaining = target_grade - weighted_completed_grade
        required_score = required_weighted_remaining / remaining_weight_normalized
    
    return max(0.0, required_score), remaining_weight_percent, weighted_completed_grade

# UI Components
def render_ml_dashboard(course_data, target_grade):
    """Render ML-powered analytics dashboard"""
    st.subheader("🤖 AI Analytics Dashboard")
    
    predicted_grade, slope, trend = predict_final_grade_ml(course_data)
    goal_status, goal_message = assess_goal_achievement(course_data, target_grade)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if predicted_grade:
            st.metric("🎯 Predicted Final Grade", f"{predicted_grade:.1f}%", trend)
        else:
            st.metric("🎯 Predicted Final Grade", "N/A", "Complete 2+ assignments")
    
    with col2:
        st.metric("📊 Goal Status", goal_status)
        st.caption(goal_message)
    
    with col3:
        completed_pct = (course_data['assignments']['Completed'].sum() / len(course_data['assignments'])) * 100
        st.metric("✅ Progress", f"{completed_pct:.0f}%", f"{course_data['assignments']['Completed'].sum()}/{len(course_data['assignments'])} done")
    
    st.markdown("#### 💡 AI Insights")
    insights = generate_ml_insights(course_data, target_grade)
    for insight in insights:
        st.info(insight)

def render_study_optimizer():
    """Render study time optimization tool"""
    course_data = st.session_state.gpa_data[st.session_state.current_course]
    
    st.subheader("⏰ Smart Study Time Allocator")
    st.markdown("AI will distribute your study hours optimally based on assignment weights!")
    
    available_hours = st.slider("Available study hours per week", 1, 40, 15, 1, key="study_hours_slider")
    
    if st.button("🧠 Calculate Optimal Allocation", type="primary", key="calc_study_btn"):
        allocation = optimize_study_time(course_data, available_hours)
        
        if allocation is not None:
            st.success("✅ Recommended study time allocation:")
            st.dataframe(allocation, use_container_width=True)
            
            fig = px.bar(allocation, x='Assignment Name', y='recommended_hours',
                        color='Weight (%)', title='Recommended Study Hours by Assignment',
                        labels={'recommended_hours': 'Recommended Hours'})
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("All assignments completed! No study time allocation needed.")

def render_performance_chart(course_data):
    """Render performance visualization"""
    df = course_data['assignments'].copy()
    completed = df[df['Completed'] == True]
    
    if len(completed) > 0:
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=completed['Assignment Name'],
            y=completed['Grade (%)'],
            mode='lines+markers',
            name='Your Grades',
            line=dict(color='#1f77b4', width=3),
            marker=dict(size=10)
        ))
        
        target = course_data['Target Course Grade (%)']
        fig.add_hline(y=target, line_dash="dash", line_color="red", 
                     annotation_text=f"Target: {target}%")
        
        fig.update_layout(
            title="Grade Performance Trend",
            xaxis_title="Assignment",
            yaxis_title="Grade (%)",
            yaxis_range=[0, 100],
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)

def render_subject_details():
    """Main course details view"""
    course_name = st.session_state.current_course
    course_data = st.session_state.gpa_data[course_name]
    
    st.header(f"📚 {course_name}")
    
    # Course metadata - Direct update, NO RERUN
    col1, col2 = st.columns(2)
    with col1:
        course_data['Course Credits'] = st.number_input(
            "Credits", 
            value=float(course_data['Course Credits']), 
            min_value=0.5, 
            step=0.5, 
            key=f'credits_{course_name}'
        )
    
    with col2:
        course_data['Target Course Grade (%)'] = st.number_input(
            "Target Grade (%)", 
            value=float(course_data['Target Course Grade (%)']),
            min_value=0.0, 
            max_value=100.0, 
            step=0.1, 
            key=f'target_{course_name}'
        )
    
    st.divider()
    
    # ML Dashboard
    render_ml_dashboard(course_data, course_data['Target Course Grade (%)'])
    
    st.divider()
    
    # Grade calculation
    current_grade, weighted_completed, total_completed_weight, projected_final = calculate_course_grade(course_data)
    target_grade = course_data['Target Course Grade (%)']
    required_score, remaining_weight, _ = optimize_required_score(course_data, target_grade)
    
    st.subheader("🎯 Grade Optimization Analysis")
    
    col1, col2, col3 = st.columns(3)
    
    grade_display = current_grade if total_completed_weight < 100 else projected_final
    grade_label = "Current Grade" if total_completed_weight < 100 else "Final Grade"
    
    with col1:
        st.metric(grade_label, f"{grade_display:.1f}%")
    with col2:
        st.metric("Target Grade", f"{target_grade:.1f}%")
    with col3:
        st.metric("Remaining Weight", f"{remaining_weight:.0f}%")
    
    if remaining_weight > 0:
        if required_score > 100:
            st.error(f"❌ Need {required_score:.1f}% average on remaining work - Target unachievable")
        elif weighted_completed >= target_grade:
            st.success(f"✅ Target secured! You can score 0% on remaining work and still hit your target")
        else:
            st.warning(f"📌 Need {required_score:.1f}% average on remaining {remaining_weight:.0f}% of work")
    else:
        if projected_final >= target_grade:
            st.success(f"✅ Final grade ({projected_final:.1f}%) meets target!")
        else:
            st.error(f"❌ Final grade ({projected_final:.1f}%) below target")
    
    st.divider()
    
    # Performance chart
    render_performance_chart(course_data)
    
    st.divider()
    
    # Study optimizer
    render_study_optimizer()
    
    st.divider()
    
    # Assignment editor
    st.subheader("📝 Assignment Manager")
    
    edited_df = st.data_editor(
        course_data['assignments'],
        num_rows="dynamic",
        column_config={
            'Type': st.column_config.TextColumn("Type"),
            'Weight (%)': st.column_config.NumberColumn("Weight (%)", min_value=0, max_value=100),
            'Assignment Name': st.column_config.TextColumn("Name", required=True),
            'Grade (%)': st.column_config.NumberColumn("Grade (%)", min_value=0.0, max_value=100.0),
            'Completed': st.column_config.CheckboxColumn("Done?"),
            'Study Hours': st.column_config.NumberColumn("Study Hours", min_value=0.0)
        },
        hide_index=True,
        key=f"editor_{course_name}"
    )
    
    # Auto-complete based on grade entry
    edited_df['Completed'] = edited_df['Grade (%)'].apply(lambda x: True if pd.notna(x) else False)
    course_data['assignments'] = edited_df
    
    if edited_df['Weight (%)'].sum() != 100:
        st.error(f"⚠️ Total weight is {edited_df['Weight (%)'].sum()}% - should be 100%")
    
    st.caption("💡 Tip: You can delete rows by clicking the ❌ icon on the left of each row in the table above")

def render_sidebar():
    """Render sidebar"""
    st.sidebar.header("📊 Your Courses")
    
    for course_name in list(st.session_state.gpa_data.keys()):
        grade, _, _, _ = calculate_course_grade(st.session_state.gpa_data[course_name])
        
        col1, col2 = st.sidebar.columns([4, 1])
        
        with col1:
            if st.button(
                f"{course_name} ({grade:.1f}%)", 
                use_container_width=True,
                type="primary" if course_name == st.session_state.current_course else "secondary",
                key=f"course_btn_{course_name}"
            ):
                st.session_state.current_course = course_name
                st.session_state.manage_mode = 'details'
        
        with col2:
            if st.button("🗑️", key=f"del_{course_name}", help="Delete course"):
                if len(st.session_state.gpa_data) > 1:
                    del st.session_state.gpa_data[course_name]
                    if st.session_state.current_course == course_name:
                        st.session_state.current_course = list(st.session_state.gpa_data.keys())[0]
                else:
                    st.sidebar.error("Cannot delete last course")
    
    st.sidebar.divider()
    
    if st.sidebar.button("➕ Add New Course", use_container_width=True, key="add_course_btn"):
        st.session_state.manage_mode = 'add'
        st.session_state.current_course = None

def render_add_course():
    """Add new course"""
    st.header("➕ Add New Course")
    
    with st.form("add_course_form"):
        name = st.text_input("Course Name")
        credits = st.number_input("Credits", value=3.0, min_value=0.5, step=0.5)
        target = st.number_input("Target Grade (%)", value=90.0, min_value=0.0, max_value=100.0)
        
        col1, col2 = st.columns(2)
        submitted = col1.form_submit_button("✅ Create Course", type="primary")
        cancelled = col2.form_submit_button("❌ Cancel")
        
        if submitted:
            if name and name not in st.session_state.gpa_data:
                st.session_state.gpa_data[name] = {
                    'Course Credits': credits,
                    'Target Course Grade (%)': target,
                    'assignments': pd.DataFrame({
                        'Type': ['Assignment'],
                        'Weight (%)': [100],
                        'Assignment Name': ['New Assignment'],
                        'Grade (%)': [None],
                        'Completed': [False],
                        'Study Hours': [None]
                    })
                }
                st.session_state.current_course = name
                st.session_state.manage_mode = 'details'
                st.success(f"Created course: {name}")
            elif not name:
                st.error("Please enter a course name")
            else:
                st.error("Course name already exists")
        
        if cancelled:
            st.session_state.manage_mode = 'details'
            if st.session_state.gpa_data:
                st.session_state.current_course = list(st.session_state.gpa_data.keys())[0]

def main():
    st.set_page_config(page_title="GradeLink Pro", layout="wide", page_icon="📚")
    
    initialize_data()
    
    st.title("📚 GradeLink Pro - AI Grade Tracker")
    st.markdown("*AI-powered insights to help you achieve your academic goals*")
    
    render_sidebar()
    
    if st.session_state.manage_mode == 'add':
        render_add_course()
    elif st.session_state.current_course:
        render_subject_details()
    else:
        st.info("Add a course to get started!")

if __name__ == '__main__':
    main()