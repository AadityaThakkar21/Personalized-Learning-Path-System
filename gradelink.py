import streamlit as st
import pandas as pd
import uuid
import math

# --- Global State Initialization ---

def init_session_state():
    """Initializes all necessary session state variables."""
    if 'gpa_scale' not in st.session_state:
        st.session_state.gpa_scale = {
            'A+': 4.0, 'A': 4.0, 'A-': 3.7, 
            'B+': 3.3, 'B': 3.0, 'B-': 2.7, 
            'C+': 2.3, 'C': 2.0, 'C-': 1.7, 
            'D+': 1.3, 'D': 1.0, 'D-': 0.7, 
            'F': 0.0
        }
    
    if 'subjects' not in st.session_state:
        st.session_state.subjects = [
            {
                'id': str(uuid.uuid4()),
                'name': 'Calculus I',
                'credits': 3.0,
                'target_grade': 90.0,
                'assignments': [
                    {'id': str(uuid.uuid4()), 'type': 'Homework', 'weight': 30.0, 'name': 'Weekly HW Average', 'grade': 85.0},
                    {'id': str(uuid.uuid4()), 'type': 'Test', 'weight': 50.0, 'name': 'Midterm Exam', 'grade': 92.0},
                    {'id': str(uuid.uuid4()), 'type': 'Final', 'weight': 20.0, 'name': 'Final Exam', 'grade': None},
                ]
            },
            {
                'id': str(uuid.uuid4()),
                'name': 'Intro to Python',
                'credits': 4.0,
                'target_grade': 80.0,
                'assignments': [
                    {'id': str(uuid.uuid4()), 'type': 'Project', 'weight': 60.0, 'name': 'Final Project', 'grade': 78.0},
                    {'id': str(uuid.uuid4()), 'type': 'Quiz', 'weight': 40.0, 'name': 'Quiz Average', 'grade': 85.0},
                ]
            }
        ]

    if 'selected_subject_id' not in st.session_state:
        st.session_state.selected_subject_id = None
        if st.session_state.subjects:
            st.session_state.selected_subject_id = st.session_state.subjects[0]['id']

    if 'deletion_mode' not in st.session_state:
        st.session_state.deletion_mode = False
    
    if 'subjects_to_delete' not in st.session_state:
        st.session_state.subjects_to_delete = set()
    
    # Track previous state to detect changes
    if 'prev_assignments_state' not in st.session_state:
        st.session_state.prev_assignments_state = {}


init_session_state()

# --- Calculation Functions ---

def calculate_subject_grade(subject_data):
    """Calculates the weighted average grade for a single subject."""
    total_weighted_points_earned = 0.0
    total_weight_graded = 0.0
    total_course_weight = 0.0

    for assignment in subject_data['assignments']:
        weight = float(assignment.get('weight', 0.0) or 0.0)
        total_course_weight += weight
        
        grade_value = assignment.get('grade')
        if grade_value is not None and isinstance(grade_value, (int, float)) and not math.isnan(grade_value):
            grade = grade_value
            total_weighted_points_earned += (grade * weight)
            total_weight_graded += weight
    
    current_percentage = None
    if total_weight_graded > 0:
        current_percentage = total_weighted_points_earned / total_weight_graded
        
    target_grade = subject_data['target_grade']
    remaining_weight = total_course_weight - total_weight_graded
    
    required_grade = None
    
    if remaining_weight > 0 and target_grade is not None and total_course_weight > 0:
        desired_total_weighted_points = target_grade * total_course_weight
        required_points_from_remaining = desired_total_weighted_points - total_weighted_points_earned
        required_grade = required_points_from_remaining / remaining_weight
        required_grade = max(0.0, required_grade)

    return {
        'current_percentage': current_percentage,
        'total_weight_graded': total_weight_graded, 
        'total_course_weight': total_course_weight,
        'required_grade': required_grade
    }

def calculate_gpa(subjects, gpa_scale):
    """Calculates the overall GPA using the current subject grades and credits."""
    total_quality_points = 0.0
    total_credits = 0.0
    
    for subject in subjects:
        grade_results = calculate_subject_grade(subject)
        percentage = grade_results['current_percentage']
        credits = subject.get('credits', 0.0)

        if percentage is not None and credits > 0:
            if percentage >= 93: letter = 'A+'
            elif percentage >= 90: letter = 'A'
            elif percentage >= 87: letter = 'A-'
            elif percentage >= 83: letter = 'B+'
            elif percentage >= 80: letter = 'B'
            elif percentage >= 77: letter = 'B-'
            elif percentage >= 73: letter = 'C+'
            elif percentage >= 70: letter = 'C'
            elif percentage >= 67: letter = 'C-'
            elif percentage >= 63: letter = 'D+'
            elif percentage >= 60: letter = 'D'
            elif percentage >= 57: letter = 'D-'
            else: letter = 'F'
            
            gpa_value = gpa_scale.get(letter, 0.0)
            total_quality_points += (gpa_value * credits)
            total_credits += credits

    if total_credits > 0:
        return total_quality_points / total_credits
    return 0.0

# --- UI Helper Functions ---

def add_new_subject():
    """Adds a new default subject to the list."""
    new_subject = {
        'id': str(uuid.uuid4()),
        'name': 'New Course',
        'credits': 3.0,
        'target_grade': 85.0,
        'assignments': [
            {'id': str(uuid.uuid4()), 'type': 'Test', 'weight': 50.0, 'name': 'Exam 1', 'grade': None},
        ]
    }
    st.session_state.subjects.append(new_subject)
    st.session_state.selected_subject_id = new_subject['id']

def select_subject(subject_id):
    """Handles subject selection via sidebar buttons."""
    st.session_state.selected_subject_id = subject_id

def toggle_deletion_mode():
    """Toggles the deletion mode on and off."""
    st.session_state.deletion_mode = not st.session_state.deletion_mode
    if not st.session_state.deletion_mode:
        st.session_state.subjects_to_delete = set()

def confirm_delete_subjects():
    """Deletes all subjects marked for deletion."""
    ids_to_delete = st.session_state.subjects_to_delete
    if ids_to_delete:
        st.session_state.subjects = [
            s for s in st.session_state.subjects 
            if s['id'] not in ids_to_delete
        ]
        
        if st.session_state.selected_subject_id in ids_to_delete:
            if st.session_state.subjects:
                st.session_state.selected_subject_id = st.session_state.subjects[0]['id']
            else:
                st.session_state.selected_subject_id = None
        
        st.session_state.deletion_mode = False
        st.session_state.subjects_to_delete = set()

def render_gpa_config():
    """Renders the GPA scale configuration using a data editor."""
    st.subheader("School GPA Scale Configuration")
    
    gpa_data = pd.DataFrame([
        {'Letter Grade': k, 'GPA Value': v} 
        for k, v in st.session_state.gpa_scale.items()
    ])
    
    edited_gpa_df = st.data_editor(
        gpa_data,
        num_rows="dynamic",
        column_config={
            "Letter Grade": st.column_config.TextColumn("Letter Grade (e.g., A, B+)", required=True),
            "GPA Value": st.column_config.NumberColumn("GPA Value (4.0 Scale)", min_value=0.0, max_value=4.3, step=0.1, required=True),
        },
        hide_index=True,
        key="gpa_editor"
    )

    new_gpa_scale = {}
    for index, row in edited_gpa_df.iterrows():
        grade = str(row['Letter Grade']).strip().upper()
        value = row['GPA Value']
        if grade and value is not None:
            new_gpa_scale[grade] = float(value)
            
    if new_gpa_scale:
        st.session_state.gpa_scale = new_gpa_scale

def render_subject_selector(current_gpa):
    """Renders the list of subjects and overall GPA."""
    st.sidebar.markdown("## 📈 Overall Performance")
    st.sidebar.metric("Calculated GPA", f"{current_gpa:.2f}")
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("Registered Subjects")
    
    if st.session_state.deletion_mode:
        st.sidebar.warning("Check the box next to subjects you wish to delete.")
        
        for subject in st.session_state.subjects:
            subject_id = subject['id']
            is_checked = subject_id in st.session_state.subjects_to_delete
            
            checkbox_state = st.sidebar.checkbox(
                f"Delete: **{subject['name']}**", 
                value=is_checked, 
                key=f"del_check_{subject_id}"
            )
            
            if checkbox_state and subject_id not in st.session_state.subjects_to_delete:
                st.session_state.subjects_to_delete.add(subject_id)
            elif not checkbox_state and subject_id in st.session_state.subjects_to_delete:
                st.session_state.subjects_to_delete.remove(subject_id)
        
        if st.session_state.subjects_to_delete:
            num_to_delete = len(st.session_state.subjects_to_delete)
            st.sidebar.markdown("---")
            st.sidebar.button(
                f"✅ Confirm Delete {num_to_delete} Subject{'s' if num_to_delete > 1 else ''}", 
                on_click=confirm_delete_subjects, 
                use_container_width=True, 
                type="primary"
            )
            
    else:
        for subject in st.session_state.subjects:
            grade_results = calculate_subject_grade(subject)
            percentage = grade_results['current_percentage']
            
            grade_status = f"({percentage:.1f}%)" if percentage is not None else "(No Grades)"
            button_label = f"{subject['name']} {grade_status}"
            
            is_selected = st.session_state.selected_subject_id == subject['id']
            button_type = "primary" if is_selected else "secondary"
            
            if st.sidebar.button(
                button_label, 
                key=f"select_sub_{subject['id']}", 
                on_click=select_subject, 
                args=(subject['id'],), 
                use_container_width=True,
                type=button_type
            ):
                pass

    st.sidebar.markdown("---")
    col_add, col_del = st.sidebar.columns(2)
    
    col_add.button("➕ Add New Course", on_click=add_new_subject, use_container_width=True)
    
    delete_label = "❌ Cancel Deletion" if st.session_state.deletion_mode else "🗑️ Manage Subjects"
    col_del.button(delete_label, on_click=toggle_deletion_mode, use_container_width=True)


def assignments_to_comparable_string(assignments):
    """Convert assignments to a string representation for comparison."""
    return str(sorted([(a['name'], a['weight'], a['grade']) for a in assignments]))


def render_subject_details():
    """Renders the assignments, target grade, and required score for the selected subject."""
    selected_id = st.session_state.selected_subject_id
    if not selected_id:
        st.info("Select a subject from the sidebar to view details.")
        return

    try:
        subject_index = next((i for i, s in enumerate(st.session_state.subjects) if s['id'] == selected_id))
    except StopIteration:
        st.info("The previously selected subject was deleted. Please select a new subject from the sidebar.")
        st.session_state.selected_subject_id = None
        return

    subject = st.session_state.subjects[subject_index]
    
    subject['name'] = st.text_input("Course Name", value=subject['name'], key=f"name_{selected_id}")
    st.header(f"Subject: {subject['name']}")

    col_c, col_t = st.columns(2)
    
    new_credits = col_c.number_input("Course Credits", min_value=0.0, max_value=10.0, value=subject['credits'], step=0.5, key=f"credits_{selected_id}")
    new_target = col_t.number_input("Target Course Grade (%)", min_value=0.0, max_value=100.0, value=subject['target_grade'], step=0.1, key=f"target_{selected_id}")
    
    subject['credits'] = new_credits
    subject['target_grade'] = new_target

    st.subheader("Assignment Weights and Grades")
    
    # Store current state snapshot before editor
    prev_state_key = f"prev_{selected_id}"
    prev_state = st.session_state.prev_assignments_state.get(prev_state_key, "")
    
    # Create DataFrame directly from session state
    assignments_data = []
    for assignment in subject['assignments']:
        assignments_data.append({
            'Type': assignment['type'],
            'Weight': assignment['weight'],
            'Assignment Name': assignment['name'],
            'Grade (%)': assignment['grade']
        })
    
    df_display = pd.DataFrame(assignments_data) if assignments_data else pd.DataFrame(
        columns=['Type', 'Weight', 'Assignment Name', 'Grade (%)']
    )

    # Render the data editor
    edited_df = st.data_editor(
        df_display,
        num_rows="dynamic",
        column_config={
            "Type": st.column_config.SelectboxColumn(
                "Type", 
                options=["Homework", "Test", "Quiz", "Project", "Final", "General"], 
                required=True
            ),
            "Weight": st.column_config.NumberColumn(
                "Weight", 
                min_value=0, 
                max_value=100, 
                step=0.1, 
                required=True, 
                help="The weight of this assignment category."
            ),
            "Assignment Name": st.column_config.TextColumn("Assignment Name", required=True),
            "Grade (%)": st.column_config.NumberColumn(
                "Grade (%)", 
                min_value=0, 
                max_value=100, 
                step=0.1, 
                help="Leave blank for ungraded assignments."
            ),
        },
        hide_index=True,
        key=f"assignments_editor_{selected_id}"
    )

    # Process edited data and update session state
    updated_assignments = []
    original_ids = [a['id'] for a in subject['assignments']]
    
    for i, row in edited_df.iterrows():
        # Skip empty rows
        if not str(row['Assignment Name']).strip():
            continue
            
        # Preserve ID if row existed, otherwise create new
        assignment_id = original_ids[i] if i < len(original_ids) else str(uuid.uuid4())
        
        assignment_type = str(row['Type']).strip() if pd.notna(row['Type']) else "General"
        assignment_name = str(row['Assignment Name']).strip() if pd.notna(row['Assignment Name']) else "New Item"
        weight_value = float(row['Weight']) if pd.notna(row['Weight']) else 0.0
        
        # Handle grade value - preserve None for ungraded
        grade_value = None
        if pd.notna(row['Grade (%)']):
            try:
                grade_value = float(row['Grade (%)'])
            except (ValueError, TypeError):
                grade_value = None

        updated_assignments.append({
            'id': assignment_id,
            'type': assignment_type,
            'weight': weight_value,
            'name': assignment_name,
            'grade': grade_value
        })

    # Check if assignments changed
    new_state = assignments_to_comparable_string(updated_assignments)
    assignments_changed = (new_state != prev_state)
    
    # Update session state
    st.session_state.subjects[subject_index]['assignments'] = updated_assignments
    st.session_state.prev_assignments_state[prev_state_key] = new_state
    
    # Force rerun if data changed
    if assignments_changed and prev_state != "":
        st.rerun()

    # Calculate and display results
    grade_results = calculate_subject_grade(subject)
    
    current_grade_pct = grade_results['current_percentage']
    total_weight_graded = grade_results['total_weight_graded']
    total_course_weight = grade_results['total_course_weight']
    required_grade = grade_results['required_grade']

    st.markdown("---")
    st.subheader("Current Grade & Target Projection")
    
    col1, col2, col3 = st.columns(3)
    
    if current_grade_pct is not None:
        graded_pct_of_course = (total_weight_graded / total_course_weight) * 100.0 if total_course_weight > 0 else 0
        col1.metric("Current Grade", f"{current_grade_pct:.1f}%", help=f"Based on {graded_pct_of_course:.0f}% of the total course weight.")
    else:
        col1.metric("Current Grade", "N/A", help="No assignments have been graded yet.")

    col2.metric("Target Grade", f"{subject['target_grade']:.1f}%")

    remaining_pct_of_course = ((total_course_weight - total_weight_graded) / total_course_weight) * 100.0 if total_course_weight > 0 else 0

    if remaining_pct_of_course == 0:
        col3.metric("Required on Remaining", "N/A", help="All course weight is accounted for.")
    elif required_grade is not None:
        if required_grade > 100.0:
            col3.metric("Required on Remaining", "Impossible", delta=f"Need >100%", delta_color="inverse", help="It is mathematically impossible to reach your target grade.")
        elif required_grade < 0.0:
            col3.metric("Required on Remaining", "0.0%", delta="Target already met!", delta_color="normal", help="You have already exceeded your target grade!")
        else:
            col3.metric("Required on Remaining", f"{required_grade:.1f}%", help=f"You need a {required_grade:.1f}% average on the remaining {remaining_pct_of_course:.0f}% of the course.")
    else:
        col3.metric("Required on Remaining", "N/A", help="Cannot calculate. Ensure all assignments have a valid weight.")


# --- Main App Execution ---

st.title("📚 Personalized Learning Path: Grade Tracker")
st.markdown("Set your school's GPA scale, track your assignments, and project the score you need on remaining work to hit your grade targets.")

# Calculate GPA first
current_gpa = calculate_gpa(st.session_state.subjects, st.session_state.gpa_scale)

main_col, config_col = st.columns([2.5, 1.5])

render_subject_selector(current_gpa)

with config_col:
    render_gpa_config()

with main_col:
    render_subject_details()