import streamlit as st
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
from datetime import datetime, timedelta
import io
import os

# Set page config
st.set_page_config(page_title="Smart Revision Scheduler", page_icon="📚", layout="wide")

# Title and description
st.title("📚 Smart Quiz Revision Scheduler")
st.markdown("""
Get personalized revision intervals based on your performance!
This ML-powered tool analyzes your study patterns to optimize your quiz preparation.
""")

# Try to load the CSV file automatically
csv_file = "quiz_results.csv"

if os.path.exists(csv_file):
    try:
        # Read the CSV file
        df = pd.read_csv(csv_file)
        
        st.success(f"✅ Successfully loaded {csv_file}")
        
        # Check required columns
        required_cols = ['timestamp', 'user_id', 'subject', 'difficulty', 'score', 
                        'total', 'dataset', 'attempt_no', 'time_spent(mins)']
        
        if not all(col in df.columns for col in required_cols):
            st.error(f"Missing required columns. Please ensure your CSV has: {', '.join(required_cols)}")
        else:
            # Sidebar filters
            st.sidebar.header("🔍 Filter Your Data")
            
            # Get unique values for filters
            users = sorted(df['user_id'].unique())
            subjects = sorted(df['subject'].unique())
            difficulties = sorted(df['difficulty'].unique())
            
            st.sidebar.info(f"📌 Available Users: {len(users)}\n📌 Available Subjects: {len(subjects)}")
            
            # Filter inputs
            selected_user = st.sidebar.selectbox("Select User ID", users)
            selected_subject = st.sidebar.selectbox("Select Subject", subjects)
            selected_difficulty = st.sidebar.selectbox("Select Difficulty", difficulties)
            
            # Filter data
            filtered_df = df[
                (df['user_id'] == selected_user) & 
                (df['subject'] == selected_subject) & 
                (df['difficulty'] == selected_difficulty)
            ].copy()
            
            # Show filtered data
            st.subheader("🔎 Filtered Data")
            st.markdown(f"**Selected:** User: `{selected_user}` | Subject: `{selected_subject}` | Difficulty: `{selected_difficulty}`")
            
            # Check if data exists for selected filters
            is_prediction_mode = False
            training_data = filtered_df.copy()
            
            if len(filtered_df) == 0:
                st.warning(f"⚠️ No data found for {selected_difficulty} difficulty in {selected_subject}")
                st.info("💡 Don't worry! We'll use your performance data from other difficulties to predict optimal intervals.")
                
                # Get data for same user and subject but all difficulties
                training_data = df[
                    (df['user_id'] == selected_user) & 
                    (df['subject'] == selected_subject)
                ].copy()
                
                if len(training_data) == 0:
                    st.error("❌ No data found for this user and subject combination. Please try different selections.")
                    st.stop()
                else:
                    st.success(f"✅ Found {len(training_data)} records from other difficulties to train the model")
                    
                    # Display available difficulties for this subject
                    available_diffs = training_data['difficulty'].unique()
                    st.info(f"📊 Using your performance data from: {', '.join(available_diffs)}")
                    
                    is_prediction_mode = True
            else:
                st.success(f"✅ Found {len(filtered_df)} records matching your filters")
                
                # Display filtered data in expandable section
                with st.expander("📋 View Filtered Data", expanded=True):
                    st.dataframe(filtered_df, use_container_width=True)
            
            st.divider()
            
            # Show different message for prediction mode
            if is_prediction_mode:
                st.info(f"🎯 Predicting optimal intervals for **{selected_difficulty}** difficulty based on your performance in other difficulties")
            
            # Display performance summary
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📈 Your Performance Summary")
                
                if is_prediction_mode:
                    # Show aggregate performance from other difficulties
                    avg_score = (training_data['score'] / training_data['total'] * 100).mean()
                    total_attempts = len(training_data)
                    avg_time = training_data['time_spent(mins)'].mean()
                    st.caption("(Based on other difficulties)")
                else:
                    # Show performance for selected difficulty
                    avg_score = (filtered_df['score'] / filtered_df['total'] * 100).mean()
                    total_attempts = len(filtered_df)
                    avg_time = filtered_df['time_spent(mins)'].mean()
                
                metric_col1, metric_col2, metric_col3 = st.columns(3)
                metric_col1.metric("Average Score", f"{avg_score:.1f}%")
                metric_col2.metric("Total Attempts", total_attempts)
                metric_col3.metric("Avg Time (mins)", f"{avg_time:.1f}")
            
            with col2:
                st.subheader("📋 Recent Attempts")
                
                if is_prediction_mode:
                    recent_data = training_data.tail(5)[['timestamp', 'difficulty', 'score', 'total', 'time_spent(mins)']].copy()
                    st.caption("(From other difficulties)")
                else:
                    recent_data = filtered_df.tail(5)[['timestamp', 'score', 'total', 'time_spent(mins)']].copy()
                
                recent_data['percentage'] = (recent_data['score'] / recent_data['total'] * 100).round(1)
                st.dataframe(recent_data, use_container_width=True)
            
            st.divider()
            
            # ML Model Section
            st.subheader("🤖 ML-Powered Revision Scheduler")
            
            # Time until quiz input
            days_until_quiz = st.slider(
                "⏰ How many days until your quiz?",
                min_value=1,
                max_value=90,
                value=14,
                help="Select the number of days remaining until your quiz"
            )
            
            if st.button("🎯 Generate Optimal Revision Schedule", type="primary"):
                with st.spinner("Analyzing your study patterns..."):
                    # Prepare training data with difficulty encoding
                    training_data['score_percentage'] = (training_data['score'] / training_data['total']) * 100
                    training_data['attempt_no'] = training_data['attempt_no'].astype(int)
                    
                    # Encode difficulty levels
                    le = LabelEncoder()
                    training_data['difficulty_encoded'] = le.fit_transform(training_data['difficulty'])
                    
                    # Prepare training data - now including difficulty as a feature
                    X = training_data[['score_percentage', 'attempt_no', 'time_spent(mins)', 'difficulty_encoded']].values
                    
                    # Calculate ideal interval based on performance
                    # Better performance = longer intervals (spaced repetition)
                    y = []
                    for _, row in training_data.iterrows():
                        score_pct = row['score_percentage']
                        if score_pct >= 90:
                            ideal_gap = 7  # Strong retention
                        elif score_pct >= 75:
                            ideal_gap = 5  # Good retention
                        elif score_pct >= 60:
                            ideal_gap = 3  # Moderate retention
                        else:
                            ideal_gap = 2  # Needs frequent review
                        y.append(ideal_gap)
                    
                    # Train model
                    model = RandomForestRegressor(n_estimators=100, random_state=42)
                    model.fit(X, y)
                    
                    # Predict optimal interval for current performance
                    if is_prediction_mode:
                        # For prediction mode, use average performance from other difficulties
                        avg_performance = training_data.groupby('difficulty').agg({
                            'score_percentage': 'mean',
                            'attempt_no': 'max',
                            'time_spent(mins)': 'mean'
                        }).mean()
                        
                        # Encode the target difficulty
                        if selected_difficulty in le.classes_:
                            target_difficulty_encoded = le.transform([selected_difficulty])[0]
                        else:
                            # If difficulty not seen before, use medium difficulty encoding
                            target_difficulty_encoded = le.transform([le.classes_[len(le.classes_)//2]])[0]
                        
                        prediction_input = [[
                            avg_performance['score_percentage'],
                            avg_performance['attempt_no'],
                            avg_performance['time_spent(mins)'],
                            target_difficulty_encoded
                        ]]
                        
                        st.info(f"📊 Using average performance metrics to predict for {selected_difficulty} difficulty")
                    else:
                        # Use actual latest performance
                        latest_performance = training_data.iloc[-1]
                        prediction_input = [[
                            latest_performance['score_percentage'],
                            latest_performance['attempt_no'],
                            latest_performance['time_spent(mins)'],
                            latest_performance['difficulty_encoded']
                        ]]
                    
                    base_interval = model.predict(prediction_input)[0]
                    
                    # Adjust based on days until quiz
                    num_sessions = max(2, int(days_until_quiz / base_interval))
                    optimal_interval = days_until_quiz / num_sessions
                    
                    # Round the optimal interval
                    # If decimal part <= 0.5, round to nearest 0.5, otherwise round up
                    decimal_part = optimal_interval - int(optimal_interval)
                    if decimal_part <= 0.5:
                        rounded_interval = int(optimal_interval) + (0.5 if decimal_part > 0 else 0)
                    else:
                        rounded_interval = int(optimal_interval) + 1
                    
                    # Display results
                    st.success("✅ Your personalized revision schedule is ready!")
                    
                    result_col1, result_col2 = st.columns(2)
                    
                    with result_col1:
                        st.metric(
                            "Optimal Revision Interval (Exact)",
                            f"{optimal_interval:.1f} days",
                            help="Precise recommended gap between study sessions"
                        )
                        st.metric(
                            "Optimal Revision Interval (Rounded)",
                            f"{rounded_interval} days" if rounded_interval == int(rounded_interval) else f"{rounded_interval:.1f} days",
                            help="Practical rounded interval for easier scheduling"
                        )
                        st.metric(
                            "Recommended Sessions",
                            f"{num_sessions} sessions",
                            help="Total number of revision sessions before quiz"
                        )
                    
                    with result_col2:
                        # Performance indicator
                        if avg_score >= 80:
                            performance_emoji = "🌟"
                            performance_text = "Excellent"
                            color = "green"
                        elif avg_score >= 60:
                            performance_emoji = "👍"
                            performance_text = "Good"
                            color = "blue"
                        else:
                            performance_emoji = "📖"
                            performance_text = "Needs Practice"
                            color = "orange"
                        
                        st.markdown(f"### {performance_emoji} Performance: {performance_text}")
                        st.progress(min(avg_score / 100, 1.0))
                    
                    # Generate schedule
                    st.subheader("📅 Your Revision Schedule")
                    
                    schedule_data = []
                    current_date = datetime.now()
                    
                    for i in range(num_sessions):
                        session_date = current_date + timedelta(days=i * optimal_interval)
                        schedule_data.append({
                            'Session': f"Session {i+1}",
                            'Date': session_date.strftime('%Y-%m-%d'),
                            'Day': session_date.strftime('%A'),
                            'Days Until Quiz': int(days_until_quiz - (i * optimal_interval))
                        })
                    
                    schedule_df = pd.DataFrame(schedule_data)
                    st.dataframe(schedule_df, use_container_width=True)
                    
                    # Recommendations
                    st.subheader("💡 Personalized Recommendations")
                    
                    recommendations = []
                    
                    if avg_score < 60:
                        recommendations.append("📌 Focus on fundamentals - your scores suggest more practice is needed")
                        recommendations.append("📌 Consider shorter, more frequent sessions")
                    elif avg_score < 80:
                        recommendations.append("📌 You're doing well! Focus on challenging areas")
                        recommendations.append("📌 Mix practice with theory review")
                    else:
                        recommendations.append("📌 Excellent performance! Focus on maintaining knowledge")
                        recommendations.append("📌 Use spaced repetition to optimize retention")
                    
                    if avg_time < 10:
                        recommendations.append("📌 Try extending your study sessions for deeper learning")
                    elif avg_time > 45:
                        recommendations.append("📌 Consider taking breaks to maintain focus")
                    
                    for rec in recommendations:
                        st.info(rec)
                    
                    # Download schedule
                    csv_buffer = io.StringIO()
                    schedule_df.to_csv(csv_buffer, index=False)
                    
                    st.download_button(
                        label="📥 Download Schedule as CSV",
                        data=csv_buffer.getvalue(),
                        file_name=f"revision_schedule_{selected_subject}_{selected_difficulty}.csv",
                        mime="text/csv"
                    )
    
    except Exception as e:
        st.error(f"Error processing file: {str(e)}")
        st.info("Please ensure your CSV file has the correct format and columns.")

else:
    # Error message when file is not found
    st.error(f"❌ Could not find '{csv_file}' in the current directory")
    st.info("""
    **Please ensure:**
    1. The file `quiz_results.csv` is in the same directory as this script
    2. The file has the correct name (case-sensitive)
    3. The file is not corrupted
    """)
    
    st.subheader("📋 Required CSV Format")
    st.markdown("""
    Your CSV file should contain the following columns:
    - **timestamp**: Date/time of the attempt
    - **user_id**: Unique identifier for the user
    - **subject**: Subject name (e.g., Math, Science)
    - **difficulty**: Difficulty level (e.g., Easy, Medium, Hard)
    - **score**: Points scored
    - **total**: Total possible points
    - **dataset**: Dataset identifier
    - **attempt_no**: Attempt number
    - **time_spent(mins)**: Time spent in minutes
    """)
    
    # Sample data
    sample_data = {
        'timestamp': ['2024-01-01 10:00', '2024-01-05 14:30'],
        'user_id': ['user123', 'user123'],
        'subject': ['Math', 'Math'],
        'difficulty': ['Medium', 'Medium'],
        'score': [8, 9],
        'total': [10, 10],
        'dataset': ['quiz1', 'quiz1'],
        'attempt_no': [1, 2],
        'time_spent(mins)': [15, 12]
    }
    
    sample_df = pd.DataFrame(sample_data)
    st.subheader("📝 Sample Data Format")
    st.dataframe(sample_df)