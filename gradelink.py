import streamlit as st
import pandas as pd
import numpy as np
import math

# --- Configuration Constants (Defaults) ---
DEFAULT_COURSE_NAME = 'Calculus I'
DEFAULT_TARGET_GRADE = 90.0
DEFAULT_COURSE_CREDITS = 3.0

# --- Grade Tracking Data Structure Initialization ---
def initialize_data():
    """Initializes all necessary data structures in Streamlit session state."""
    # 1. GPA Scale Configuration (Key: Letter Grade, Value: Min Percent)
    if 'gpa_scale' not in st.session_state:
        st.session_state.gpa_scale = pd.DataFrame({
            'Letter Grade (e.g., A, B+)': ['A+', 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D', 'F'],
            'Min Grade (%)': [97.0, 93.0, 90.0, 87.0, 83.0, 80.0, 77.0, 73.0, 70.0, 67.0, 60.0, 0.0],
            'GPA Value': [4.0, 4.0, 3.7, 3.3, 3.0, 2.7, 2.3, 2.0, 1.7, 1.3, 1.0, 0.0]
        })

    # 2. Main Course Data Structure
    if 'gpa_data' not in st.session_state:
        st.session_state.gpa_data = {}

    # 3. Initialize a default course if none exist
    if not st.session_state.gpa_data:
        st.session_state.gpa_data[DEFAULT_COURSE_NAME] = {
            'Course Credits': DEFAULT_COURSE_CREDITS,
            'Target Course Grade (%)': DEFAULT_TARGET_GRADE,
            'assignments': pd.DataFrame({
                'Type': ['Homework', 'Midterm', 'Final Exam', 'Project'],
                'Weight (%)': [30, 30, 30, 10],
                'Assignment Name': ['HW Average', 'Midterm 1', 'Final Exam', 'Term Project'],
                'Grade (%)': [85.0, 92.0, None, None], # None means ungraded/remaining
                'Completed': [True, True, False, False],
                'Delete?': [False, False, False, False]
            })
        }

    # 4. State for current selection and mode
    if 'current_course' not in st.session_state:
        st.session_state.current_course = DEFAULT_COURSE_NAME
    if 'manage_mode' not in st.session_state:
        st.session_state.manage_mode = 'details' # 'details', 'add', 'delete'
    if 'delete_mode' not in st.session_state:
        st.session_state.delete_mode = False

    # 5. NEW: State for change detection
    if 'prev_assignments_state' not in st.session_state:
        st.session_state.prev_assignments_state = {}

    # 6. Ensure rerun flag exists
    if '_force_rerun' not in st.session_state:
        st.session_state['_force_rerun'] = False

# --- Core Calculation Functions ---

def calculate_course_grade(course_data: dict) -> tuple[float, float, float, float]:
    """
    Calculates the current, weighted completed grade, total weight completed, and *projected final grade*.
    Returns: (Current Grade on Completed Work, Weighted Completed Grade, Total Weight Completed, Projected Final Grade)
    """
    df = course_data['assignments'].copy()
    
    # Ensure weights sum to 100
    total_weight = df['Weight (%)'].sum()
    if total_weight == 0:
        return 0.0, 0.0, 0.0, 0.0
    
    df['Normalized Weight'] = df['Weight (%)'] / 100
    
    # 1. Calculate Weighted Completed Grade (Score achieved out of 100)
    # Weighted Score = (Weight / 100) * Grade
    df['Weighted Score'] = np.where(df['Completed'], df['Normalized Weight'] * df['Grade (%)'], 0.0)
    weighted_completed_grade = df['Weighted Score'].sum()
    
    # 2. Calculate Total Weight Completed
    total_completed_weight = df[df['Completed'] == True]['Weight (%)'].sum()
    
    # 3. Calculate Current Grade (only completed assignments, scaled to 100%)
    if total_completed_weight > 0:
        current_grade = (weighted_completed_grade / (total_completed_weight / 100))
    else:
        current_grade = 0.0
        
    # 4. Calculate Projected Final Grade (The grade out of 100 achieved if all assignments have grades)
    projected_final_grade = weighted_completed_grade
        
    return current_grade, weighted_completed_grade, total_completed_weight, projected_final_grade


def calculate_overall_gpa(gpa_data: dict, gpa_scale_df: pd.DataFrame) -> float:
    """Calculates the overall GPA weighted by course credits."""
    total_credits = 0
    total_gpa_points = 0
    
    for course_name, data in gpa_data.items():
        # Handle cases where the data might be corrupted or empty
        if 'assignments' not in data or data['assignments'].empty:
            continue
            
        # Use the grade based on completion status
        current_grade_on_completed, _, total_completed_weight, projected_final_grade = calculate_course_grade(data)
        
        # If all work is complete, use the projected final grade, otherwise use current grade on completed work
        final_grade_used = projected_final_grade if total_completed_weight >= 100 else current_grade_on_completed

        course_credits = data['Course Credits']
        
        # Find the GPA value corresponding to the current grade
        gpa_value = 0.0
        # Sort scale descending to ensure we pick the highest letter grade achieved
        for _, row in gpa_scale_df.sort_values(by='Min Grade (%)', ascending=False).iterrows():
            if final_grade_used >= row['Min Grade (%)']:
                gpa_value = row['GPA Value']
                break
        
        total_credits += course_credits
        total_gpa_points += gpa_value * course_credits
        
    if total_credits > 0:
        return total_gpa_points / total_credits
    return 0.0


def optimize_required_score(course_data: dict, target_grade: float) -> tuple[float, float, float]:
    """
    Calculates the minimum required average score on remaining assignments to hit the target.
    Returns: (required_score, remaining_weight_percent, weighted_completed_grade)
    """
    df = course_data['assignments'].copy()
    
    # Ensure target grade is between 0 and 100
    target_grade = max(0.0, min(100.0, target_grade))

    # 1. Calculate weighted completed grade
    df['Normalized Weight'] = df['Weight (%)'] / 100
    df['Weighted Completed Grade'] = np.where(df['Completed'], df['Normalized Weight'] * df['Grade (%)'], 0.0)
    weighted_completed_grade = df['Weighted Completed Grade'].sum()
    
    # 2. Calculate remaining weight
    remaining_assignments = df[df['Completed'] == False]
    remaining_weight_percent = remaining_assignments['Weight (%)'].sum()
    remaining_weight_normalized = remaining_weight_percent / 100

    if remaining_weight_normalized == 0:
        # If all assignments are completed, the required score is just the final projected grade
        _, _, _, final_grade = calculate_course_grade(course_data)
        required_score = final_grade
    else:
        # 3. Calculate the required weighted score from the remaining work
        required_weighted_remaining = target_grade - weighted_completed_grade
        
        # 4. Calculate the required average grade on remaining work
        required_score = required_weighted_remaining / remaining_weight_normalized
    
    # Cap score at 100% and provide feedback
    score_to_hit = max(0.0, required_score)
        
    return score_to_hit, remaining_weight_percent, weighted_completed_grade

# --- NEW: Change Detection Helper ---

def assignments_to_comparable_string(df: pd.DataFrame) -> str:
    """
    Converts the essential assignment data into a hashable string for change detection.
    Focuses on columns that drive calculations: Weight, Grade, and Completion status.
    """
    if df.empty:
        return ""
    
    # Select critical columns, convert to string, fill NaNs (for Grade)
    df_compare = df[['Assignment Name', 'Weight (%)', 'Grade (%)', 'Completed']].copy()
    df_compare['Grade (%)'] = df_compare['Grade (%)'].fillna(-1.0) # Use a sentinel value for NaNs
    
    return df_compare.astype(str).to_csv(index=False)


# --- UI Components ---

def render_overall_performance():
    """Renders the sidebar with overall GPA and course selection/management."""
    
    st.sidebar.markdown("## 📈 Overall Performance")
    overall_gpa = calculate_overall_gpa(st.session_state.gpa_data, st.session_state.gpa_scale)
    st.sidebar.metric("Calculated GPA", f"{overall_gpa:.2f}")

    st.sidebar.markdown("---")
    st.sidebar.markdown("## 📚 Registered Subjects")
    
    # List all courses and their current grades
    current_grades_list = []
    for course_name, data in st.session_state.gpa_data.items():
        # Using the grade on completed work for the sidebar display
        current_grade, _, _, _ = calculate_course_grade(data) 
        current_grades_list.append((course_name, current_grade))
    
    # Display buttons for each course
    for course_name, grade in current_grades_list:
        # Show the grade based on completed work, unless all is done, then it's the final grade
        display_grade, _, total_completed_weight, projected_final_grade = calculate_course_grade(st.session_state.gpa_data[course_name])
        if total_completed_weight >= 100:
             display_grade = projected_final_grade
             
        if st.sidebar.button(f"{course_name} ({display_grade:.1f}%)", 
                             use_container_width=True, 
                             type="primary" if course_name == st.session_state.current_course else "secondary"):
            st.session_state.current_course = course_name
            st.session_state.manage_mode = 'details' # Go to details view
            st.session_state.delete_mode = False # Exit delete mode
            # safe to rerun here because this is main flow (not a callback)
            st.rerun() # Force rerun to load new course details

    st.sidebar.markdown("---")
    
    # Management Buttons
    col1, col2 = st.sidebar.columns(2)
    if col1.button("➕ Add New Course", use_container_width=True):
        st.session_state.manage_mode = 'add'
        st.session_state.current_course = None # Deselect current course
        st.session_state.delete_mode = False
        st.rerun()
    
    if col2.button("🗑️ Manage Subjects", use_container_width=True):
        st.session_state.manage_mode = 'delete'
        st.session_state.current_course = None # Deselect current course
        st.session_state.delete_mode = False
        st.rerun()


def render_subject_details():
    """Renders the main content area for the current subject's details and assignments."""
    
    course_name = st.session_state.current_course
    course_data = st.session_state.gpa_data[course_name]
    
    st.header(f"Subject: {course_name}")

    # Calculate Grades
    current_grade_on_completed, weighted_completed_grade, total_completed_weight, projected_final_grade = calculate_course_grade(course_data)
    target_grade = course_data['Target Course Grade (%)']
    
    # Metadata and Target Grade Inputs
    meta_col1, meta_col2 = st.columns([1, 1])
    
    with meta_col1:
        new_credits = st.number_input("Course Credits", value=course_data['Course Credits'], min_value=0.5, step=0.5, key=f'credits_{course_name}')
        # Update credits if changed
        if new_credits != course_data['Course Credits']:
            st.session_state.gpa_data[course_name]['Course Credits'] = new_credits

    with meta_col2:
        new_target = st.number_input("Target Course Grade (%)", value=target_grade, min_value=0.0, max_value=100.0, step=0.1, key=f'target_{course_name}')
        # Update target if changed
        if new_target != course_data['Target Course Grade (%)']:
            st.session_state.gpa_data[course_name]['Target Course Grade (%)'] = new_target
            # safe rerun in main flow
            st.rerun() 
            
    st.markdown("---")

    # --- Feature 1: Grade Optimization Result ---
    st.subheader("🎯 Optimization: Score Needed to Hit Target")
    
    target_grade = st.session_state.gpa_data[course_name]['Target Course Grade (%)']

    required_score, remaining_weight, weighted_completed_grade = optimize_required_score(course_data, target_grade)
    
    col_req_1, col_req_2, col_req_3 = st.columns(3)
    
    # Display logic for Current Grade / Final Grade
    grade_to_display = current_grade_on_completed
    grade_label = "Current Grade (Completed Work)"
    
    if total_completed_weight >= 100:
        grade_to_display = projected_final_grade
        grade_label = "Final Grade"
        
    with col_req_1:
        st.metric(grade_label, f"**{grade_to_display:.1f}%**")
        
    with col_req_2:
        st.metric("Target Grade", f"**{target_grade:.1f}%**")
    with col_req_3:
        st.metric("Remaining Weight", f"**{remaining_weight:.0f}%**")

    if remaining_weight > 0:
        # Calculate the minimum possible final grade (if the student scores 0% on all remaining work)
        min_possible_final_grade = weighted_completed_grade
        
        if required_score > 100.0:
            st.error(f"**Goal Unachievable:** You currently need an average of **{required_score:.1f}%** on the remaining **{remaining_weight:.0f}%** of work to hit your target. Since a score above 100% is impossible, you should adjust your target grade.")
        
        # Check if the target is secured (even with 0% on remaining work)
        # Added check for target_grade > 0.0 to prevent confusing "Target Secured" messages for a 0% target
        elif min_possible_final_grade >= target_grade and target_grade > 0.0:
            st.success(f"**Target Secured!** You currently need an average of **0.0%** on remaining work to hit your target of **{target_grade:.1f}%** (i.e., you can skip the remaining assignments and still hit the target).")
        
        # Handle the confusing 0.0% target scenario
        elif target_grade == 0.0 and min_possible_final_grade >= 0.0:
             st.success(f"**Target Hit:** Your current weighted score of **{min_possible_final_grade:.1f}%** already surpasses your target of **0.0%**. You need 0.0% average on remaining work.")
             
        # Check if the target is 0% and the goal is not secured, meaning they missed too many assignments (this is unlikely unless grades are negative)
        elif target_grade == 0.0 and min_possible_final_grade < 0.0: 
             st.error(f"**Goal Unachievable:** Your current weighted score is **{min_possible_final_grade:.1f}%**, which is below your target of 0.0%. You can no longer achieve your target, even if you score 100% on the remaining work.")

        else:
            # The required score is between 0% and 100% (or the target is 0.0% and they haven't secured it)
            st.warning(f"**Required Average:** You need to score an average of **{required_score:.1f}%** on the remaining **{remaining_weight:.0f}%** of assignments to hit your target grade.")
            
    else:
        # When all work is completed (Remaining Weight is 0%), show the comparison to the target
        if projected_final_grade >= target_grade:
            st.success(f"**All Work Graded:** Your final course grade is **{projected_final_grade:.1f}%**, which **meets or exceeds** your target of {target_grade:.1f}%.")
        else:
            st.error(f"**All Work Graded:** Your final course grade is **{projected_final_grade:.1f}%**, which is **below** your target of {target_grade:.1f}%.")

    st.markdown("---")
    
    # --- Feature 2: Assignment Tracker ---
    st.subheader("📝 Assignment Weights and Grades")
    
    # Toggle Delete Mode
    def toggle_delete_mode():
        # toggle delete mode and request a safe rerun
        st.session_state.delete_mode = not st.session_state.delete_mode
        # Reset deletion marks when changing mode
        if 'Delete?' in st.session_state.gpa_data[course_name]['assignments'].columns:
            st.session_state.gpa_data[course_name]['assignments']['Delete?'] = False
        # set rerun flag (do NOT call st.rerun() directly here)
        st.session_state['_force_rerun'] = True

    def delete_marked_rows():
        df = st.session_state.gpa_data[course_name]['assignments']
        rows_to_delete_count = int(df['Delete?'].sum()) if 'Delete?' in df.columns else 0
        if rows_to_delete_count > 0:
            df_retained = df[df['Delete?'] == False].copy()
            df_retained['Delete?'] = False
            st.session_state.gpa_data[course_name]['assignments'] = df_retained
            # show feedback (OK inside callback)
            st.success(f"Successfully deleted {rows_to_delete_count} assignment(s).")
        # leave delete mode
        st.session_state.delete_mode = False
        # set rerun flag instead of calling st.rerun() inside callback
        st.session_state['_force_rerun'] = True

    if st.session_state.delete_mode:
        st.markdown("### 🗑️ Delete Mode: Check assignments to remove, then confirm.")
    else:
        st.markdown("### Edit Assignments:")

    # Column Configuration
    base_config = {
        'Type': st.column_config.TextColumn("Type (e.g., HW, Quiz)"),
        'Weight (%)': st.column_config.NumberColumn("Weight (%)", min_value=0, max_value=100, step=1, required=True),
        'Assignment Name': st.column_config.TextColumn("Assignment Name", required=True),
        'Grade (%)': st.column_config.NumberColumn("Grade (%)", min_value=0.0, max_value=100.0, step=0.1, help="Leave blank for remaining/ungraded assignments."),
        'Completed': st.column_config.CheckboxColumn("Completed?", default=False)
    }

    df_assignments = course_data['assignments'].copy()

    if st.session_state.delete_mode:
        # In Delete Mode: Show all columns and disable editing on non-delete columns
        # Build a fresh editor_config so we don't mutate base_config
        editor_config = {}
        for col, cfg in base_config.items():
            # attempt to copy config dict if possible; otherwise use as-is
            try:
                cfg_copy = cfg.copy()
            except Exception:
                cfg_copy = cfg
            # set disabled flag in dict style
            try:
                cfg_copy['disabled'] = True
            except Exception:
                # If cfg_copy isn't dict-like, just assign directly (best-effort)
                pass
            editor_config[col] = cfg_copy

        # Add Delete checkbox column (editable)
        editor_config["Delete?"] = st.column_config.CheckboxColumn("Mark to Delete", default=False)
        df_to_edit = df_assignments
        editor_key = f"assignment_editor_{course_name}_delete"

    else:
        # In Edit Mode: Hide the Delete? column
        # If 'Delete?' doesn't exist for any reason, pad with False earlier
        if 'Delete?' not in df_assignments.columns:
            df_assignments['Delete?'] = False
        df_to_edit = df_assignments.drop(columns=['Delete?'])
        editor_config = base_config
        editor_key = f"assignment_editor_{course_name}_edit"

    # Editable Dataframe
    edited_df = st.data_editor(
        df_to_edit,
        num_rows="dynamic",
        column_config=editor_config,
        hide_index=True,
        key=editor_key
    )

    # CRITICAL: Session State Update Logic and Change Detection
    
    # 1. Update the Completed status based on Grade (%) field
    edited_df['Completed'] = edited_df['Grade (%)'].apply(lambda x: True if pd.notna(x) else False)
    
    # Ensure the 'Delete?' column is maintained across edits/deletions
    df_assignments_current = st.session_state.gpa_data[course_name]['assignments']
    
    if st.session_state.delete_mode:
        # In delete mode, the editor output is the full dataframe
        new_df = edited_df.copy()
    else: 
        # In edit mode, merge back the 'Delete?' column data
        new_length = len(edited_df)
        old_delete_data = df_assignments_current['Delete?'].values
        old_length = len(old_delete_data)

        # Rebuild the 'Delete?' list for the new dataframe length
        if new_length > old_length:
            new_delete_data = list(old_delete_data) + [False] * (new_length - old_length)
        elif new_length < old_length:
            new_delete_data = old_delete_data[:new_length].tolist()
        else:
            new_delete_data = old_delete_data.tolist()

        new_df = edited_df.copy().reset_index(drop=True)
        
        if len(new_delete_data) == len(new_df):
            new_df['Delete?'] = new_delete_data
        else:
            # Fallback: if lengths mismatch unexpectedly
            new_df['Delete?'] = [False] * len(new_df) 
            
    # 2. Update session state with the new DataFrame
    st.session_state.gpa_data[course_name]['assignments'] = new_df
    
    # 3. Change Detection and Rerun Logic
    current_state_string = assignments_to_comparable_string(new_df)
    prev_state_key = f'prev_assignments_state_{course_name}'
    
    # Check if a state change occurred
    if prev_state_key not in st.session_state.prev_assignments_state or \
       st.session_state.prev_assignments_state[prev_state_key] != current_state_string:
        
        # Update the tracked state
        st.session_state.prev_assignments_state[prev_state_key] = current_state_string
        
        # Check if the change was substantial enough to warrant a rerun 
        if not df_assignments_current.equals(new_df):
            # request a safe rerun (we're in main flow here)
            st.session_state['_force_rerun'] = True

    # Buttons for delete mode management
    btn_col1, btn_col2, _ = st.columns([1.5, 1.5, 3])
    if st.session_state.delete_mode:
        btn_col1.button("✅ Confirm Deletion", on_click=delete_marked_rows, type="primary")
        btn_col2.button("❌ Cancel Deletion Mode", on_click=toggle_delete_mode, type="secondary")
    else:
        btn_col1.button("🗑️ Enter Deletion Mode", on_click=toggle_delete_mode, type="secondary")
        
    # Validation Check
    if st.session_state.gpa_data[course_name]['assignments']['Weight (%)'].sum() != 100:
        st.error(f"⚠️ Warning: Total assignment weight is **{st.session_state.gpa_data[course_name]['assignments']['Weight (%)'].sum()}%**. It should ideally sum to 100%.")


def render_add_course():
    """Renders the UI for adding a new course."""
    st.header("➕ Add New Course")
    
    new_course_name = st.text_input("New Course Name", key="new_course_name_input")
    new_credits = st.number_input("Course Credits", value=3.0, min_value=0.5, step=0.5, key="new_credits_input")
    new_target = st.number_input("Target Course Grade (%)", value=90.0, min_value=0.0, max_value=100.0, step=0.1, key="new_target_input")
    
    if st.button("Add Course and Go to Details", type="primary"):
        if new_course_name in st.session_state.gpa_data:
            st.error("A course with this name already exists.")
        elif not new_course_name.strip():
            st.error("Course name cannot be empty.")
        else:
            st.session_state.gpa_data[new_course_name] = {
                'Course Credits': new_credits,
                'Target Course Grade (%)': new_target,
                'assignments': pd.DataFrame({
                    'Type': ['Homework', 'Exam'],
                    'Weight (%)': [40, 60],
                    'Assignment Name': ['New HW Avg', 'New Exam'],
                    'Grade (%)': [None, None],
                    'Completed': [False, False],
                    'Delete?': [False, False]
                })
            }
            st.session_state.current_course = new_course_name
            st.session_state.manage_mode = 'details'
            # safe to rerun in main flow
            st.rerun()

def render_manage_courses():
    """Renders the UI for deleting existing courses."""
    st.header("🗑️ Manage Existing Subjects")
    
    if not st.session_state.gpa_data:
        st.info("No courses to manage.")
        return
        
    st.warning("Select courses below to permanently delete them.")
    
    courses_to_delete = []
    
    for course_name in list(st.session_state.gpa_data.keys()):
        if st.checkbox(f"Delete {course_name}?", key=f'delete_course_{course_name}'):
            courses_to_delete.append(course_name)

    if courses_to_delete:
        if st.button(f"Confirm Delete {len(courses_to_delete)} Course(s)", type="primary"):
            for course_name in courses_to_delete:
                del st.session_state.gpa_data[course_name]
                # Also delete its change tracking state
                prev_state_key = f'prev_assignments_state_{course_name}'
                if prev_state_key in st.session_state.prev_assignments_state:
                    del st.session_state.prev_assignments_state[prev_state_key]

            # Reset current course if it was deleted
            if st.session_state.current_course in courses_to_delete or not st.session_state.gpa_data:
                st.session_state.current_course = next(iter(st.session_state.gpa_data)) if st.session_state.gpa_data else None
            
            st.success("Selected courses deleted.")
            st.session_state.manage_mode = 'details'
            st.rerun()
            
    if st.button("Cancel Management", type="secondary"):
        st.session_state.manage_mode = 'details'
        if st.session_state.gpa_data:
            st.session_state.current_course = next(iter(st.session_state.gpa_data))
        st.rerun()

def render_gpa_scale_config():
    """Renders the editable GPA scale configuration."""
    st.header("School GPA Scale Configuration")
    
    # Editable Dataframe for the GPA scale
    edited_gpa_df = st.data_editor(
        st.session_state.gpa_scale,
        column_config={
            'Letter Grade (e.g., A, B+)': st.column_config.TextColumn("Letter Grade", required=True),
            'Min Grade (%)': st.column_config.NumberColumn("Min Grade (%)", min_value=0.0, max_value=100.0, step=0.1, required=True),
            'GPA Value': st.column_config.NumberColumn("GPA Value", min_value=0.0, max_value=5.0, step=0.1, required=True)
        },
        num_rows="fixed", # GPA scale should not be dynamically added/removed
        hide_index=True,
        key='gpa_scale_editor'
    )
    # Update the session state with the edited GPA scale
    st.session_state.gpa_scale = edited_gpa_df

# --- Main App Execution ---

def app_main():
    initialize_data()

    st.set_page_config(layout="wide")

    st.title("📚 Personalized Learning Path: Grade Tracker (GradeLink)")
    st.markdown("Set your school's GPA scale, track your assignments, and project the score you need on remaining work to hit your grade targets.")
    
    # Sidebar Rendering (must be called first so all calculations reflect latest state)
    render_overall_performance()

    # Main Content Area
    main_col, scale_col = st.columns([2, 1])
    
    with scale_col:
        render_gpa_scale_config()
        
    with main_col:
        # Display the main content based on the current mode
        if st.session_state.manage_mode == 'add':
            render_add_course()
        elif st.session_state.manage_mode == 'delete':
            render_manage_courses()
        elif st.session_state.current_course and st.session_state.manage_mode == 'details':
            render_subject_details()
        else:
            st.info("Use the sidebar to add a new course to get started!")

    # --- Safe rerun handler: perform rerun right after callbacks/main flow sets the flag ---
    if st.session_state.get('_force_rerun', False):
        # reset the flag and rerun once
        st.session_state['_force_rerun'] = False
        st.rerun()

if __name__ == '__main__':
    app_main()
