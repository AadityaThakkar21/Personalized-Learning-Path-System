import streamlit as st
import math
import pandas as pd

# --- Configuration Constants (Defaults) ---
R_TARGET_DEFAULT = 0.85
BETA_DEFAULT = 0.2

# --- Core Functions ---
def calculate_optimal_interval(decay_rate: float, ln_r_target_adj: float) -> float:
    """Calculates the optimal review interval (t_i in days) for a concept."""
    # We use -ln_r_target_adj because math.log(R_TARGET) is negative.
    if decay_rate <= 0:
        return float('inf')
    
    optimal_interval = -ln_r_target_adj / decay_rate
    return optimal_interval

def update_decay_rate(old_decay_rate: float, quiz_score: float, beta: float) -> float:
    """
    Updates the personalized decay rate (lambda) based on a new quiz score.
    Formula: lambda_new = lambda_old * (1 + BETA * (1 - Score))
    """
    # Ensure score is between 0 and 1
    score = max(0.0, min(1.0, quiz_score))
    
    # The term (1 - Score) determines the magnitude of the update.
    lambda_new = old_decay_rate * (1 + beta * (1 - score))
    return lambda_new

# Helper function to convert days to hours for display
def format_interval_to_hours(interval_days: float) -> str:
    """Converts days to hours, rounds down to the lowest whole hour, and handles infinity for display."""
    if interval_days == float('inf'):
        return '∞'
    # Convert days to hours and round down to the lowest whole number (floor)
    interval_hours = math.floor(interval_days * 24)
    return f"{interval_hours}"

# --- Streamlit UI ---

st.set_page_config(
    page_title="Spaced Repetition System (SRS) Model",
    layout="wide"
)

st.title("🧠 Spaced Repetition System (SRS) Interval Calculator")
st.markdown(r"A simple model for calculating optimal review intervals based on a personalized decay rate ($\lambda$).")

# --- User Manual Expander ---
st.markdown("---")
with st.expander("📚 User Manual & Variable Descriptions"):
    st.markdown(r"""
        This tool uses a simple exponential decay model to calculate your optimal review intervals ($t_i$).

        ### Core Formulas
        
        The core formula for calculating the optimal interval ($t_i$) is:
        $$t_i = \frac{-ln(R_{target})}{\lambda}$$
        
        The formula for updating the personalized decay rate ($\lambda$) is:
        $$\lambda_{new} = \lambda_{old} \times (1 + \beta \times (1 - \text{Score}))$$

        ### Model Configuration

        * **Target Retention Rate ($R_{{target}}$):**
            * **Description:** The percentage of knowledge you aim to retain *just* before the next review.
            * **Usage:** Higher $R_{{target}}$ means shorter, more frequent intervals.

        * **Decay Rate Tuning Parameter ($\beta$):**
            * **Description:** Controls how quickly your personalized forgetting curve ($\lambda$) adjusts after a quiz score.
            * **Usage:** Higher $\beta$ means $\lambda$ adjusts more aggressively based on the score.

        ### Concept Table Variables

        * **Forgetting Rate ($\lambda_{{old}}$):**
            * **Description:** The personalized forgetting rate for a concept *before* the latest quiz.
            * **Usage:** You estimate this when you first add a concept: **low $\lambda$ for easy concepts, high $\lambda$ for hard concepts.**
            * *The system updates this value to the "New $\lambda$" after each simulation.*

        * **New Quiz Score (0-1):**
            * **Description:** Your score from the most recent test/review of that concept (1.0 = 100%).
            * **Usage:** Your score from the most recent test/review of that concept (1.0 = 100%).
        
        * **Deletion:** Checkboxes for deletion will appear when you enter **Deletion Mode**.
        """)
st.markdown("---")

# --- Model Configuration Inputs ---
st.header("1. Model Configuration")
config_col1, config_col2 = st.columns(2)

with config_col1:
    st.markdown(r"### Target Retention Rate ($R_{target}$):")
    r_target = st.slider(
        'Set $R_{target}$ (decimal)',
        min_value=0.75, max_value=0.99, value=R_TARGET_DEFAULT, step=0.01,
        label_visibility="collapsed"
    )
    # Calculate the natural log of the target retention rate
    LN_R_TARGET_ADJ = math.log(r_target)
    st.info(f"What percentage of the content do you wish to memorize")

with config_col2:
    st.markdown(r"### Decay Rate Tuning ($\beta$)")
    beta = st.slider(
        r'Set Decay Tuning Parameter ($\beta$)',
        min_value=0.05, max_value=0.50, value=BETA_DEFAULT, step=0.01,
        label_visibility="collapsed"
    )
    st.info(r"A higher $\beta$ means the rate at which you forget adjusts more aggressively based on the quiz score to calculate the interval hours of revision")

st.markdown("---")

# --- Main App: Input Table ---

st.header("2. Define Your Concepts")

# Initialize session state for the dataframe if it doesn't exist
if 'df_srs' not in st.session_state:
    st.session_state.df_srs = pd.DataFrame({
        'Concept': ['T-tests (Hard)', 'Linear Algebra Basics (Easy)'],
        'Initial Lambda': [0.15, 0.05], # FIXED: Must use 'Initial Lambda' as the internal key
        'New Quiz Score (0-1)': [0.70, 0.98],
        'Delete?': [False, False] # Added the new boolean column for deletion
    })
    # Ensure the 'Delete?' column is explicitly boolean for the checkbox to work correctly
    st.session_state.df_srs['Delete?'] = st.session_state.df_srs['Delete?'].astype(bool)

# Initialize delete mode state
if 'delete_mode' not in st.session_state:
    st.session_state.delete_mode = False
       
def toggle_delete_mode():
    """Toggles the state between edit mode and delete mode."""
    st.session_state.delete_mode = not st.session_state.delete_mode
    # Reset deletion marks when changing mode
    if 'df_srs' in st.session_state and 'Delete?' in st.session_state.df_srs.columns:
         st.session_state.df_srs['Delete?'] = False
    st.rerun()

# --- Row Deletion Logic (New Checkbox-based Logic) ---

def delete_marked_rows():
    """Filters the dataframe to remove all rows where 'Delete?' is True and exits delete mode."""
    
    if st.session_state.df_srs.empty:
        st.warning("The table is empty. Nothing to delete.")
        st.session_state.delete_mode = False # Exit delete mode
        st.rerun()
        return
        
    # Get the number of rows marked for deletion
    rows_to_delete_count = st.session_state.df_srs['Delete?'].sum()
    
    if rows_to_delete_count > 0:
        # Filter the DataFrame to keep only the rows where 'Delete?' is False
        df_retained = st.session_state.df_srs[st.session_state.df_srs['Delete?'] == False].copy()
        
        # Reset the 'Delete?' column on the retained rows to False to unmark them
        df_retained['Delete?'] = False
        
        st.session_state.df_srs = df_retained
        
        st.success(f"Successfully deleted {rows_to_delete_count} concept(s).")
    else:
        st.warning("No rows were marked for deletion. Check the 'Mark to Delete' column to select rows.")
    
    st.session_state.delete_mode = False # Exit delete mode after operation
    st.rerun()

# --- Display Header based on mode ---

if st.session_state.delete_mode:
    st.markdown("### 🗑️ Delete Mode: Check rows to remove, then confirm.")
else:
    st.markdown("### 📝 Edit Mode: Edit concepts and scores")

# --- Data Editor Configuration (Dynamic based on mode) ---

# Base column configurations
base_config = {
    "Concept": st.column_config.TextColumn("Concept Name", required=True),
    "Initial Lambda": st.column_config.NumberColumn(
        r"Initial Forgetting Rate", 
        help="Higher value means faster initial forgetting (e.g., 0.05 for easy, 0.15 for hard).",
        min_value=0.001,
        step=0.01
    ),
    "New Quiz Score (0-1)": st.column_config.NumberColumn(
        "New Quiz Score",
        help="Score from the latest review (0.0 to 1.0).",
        min_value=0.0,
        max_value=1.0,
        step=0.01
    )
}

# Full config including the deletion checkbox
full_config = base_config.copy()
full_config["Delete?"] = st.column_config.CheckboxColumn(
    "Mark to Delete",
    default=False,
    help="Check this box to delete the row."
)

df_to_edit = st.session_state.df_srs.copy()

if st.session_state.delete_mode:
    # In Delete Mode: Show all columns, and disable editing on non-delete columns
    editor_config = full_config.copy()
    
    # Disable editing on the core columns
    # We must explicitly redefine the columns to set 'disabled=True'
    editor_config["Concept"] = st.column_config.TextColumn("Concept Name", required=True, disabled=True)
    editor_config["Initial Lambda"] = st.column_config.NumberColumn(r"Initial Forgetting Rate", disabled=True)
    editor_config["New Quiz Score (0-1)"] = st.column_config.NumberColumn("New Quiz Score", disabled=True)
    
    editor_key = "data_editor_delete_mode"
    
else:
    # In Edit Mode: Hide the Delete? column by dropping it from the DataFrame passed to the editor
    df_to_edit = df_to_edit.drop(columns=['Delete?'])
    editor_config = base_config
    editor_key = "data_editor_edit_mode"

# Editable Dataframe
edited_df = st.data_editor(
    df_to_edit,
    num_rows="dynamic",
    column_config=editor_config,
    hide_index=True,
    key=editor_key
)

# --- Session State Update Logic ---
# CRITICAL: Always update the session state with the latest edited data, handling column presence.

if st.session_state.delete_mode:
    # If in delete mode, the editor output contains the full dataframe (including the updated 'Delete?' state)
    st.session_state.df_srs = edited_df.copy()
    
else: 
    # If in edit mode, the editor output is missing the 'Delete?' column (it was dropped for display).
    # We must re-add the 'Delete?' column from the previous state, carefully handling row changes (additions/deletions).
    
    new_length = len(edited_df)
    old_delete_data = st.session_state.df_srs['Delete?'].values
    old_length = len(old_delete_data)

    # 1. Determine the correct new state for the 'Delete?' column
    if new_length > old_length:
        # Rows were added: Extend with False for the new rows
        new_delete_data = list(old_delete_data) + [False] * (new_length - old_length)
    elif new_length < old_length:
        # Rows were deleted: Truncate the delete column data
        
        # Simple deletion handling (assuming most operations are append/remove last):
        new_delete_data = old_delete_data[:new_length].tolist()
        
    else:
        # Same length: Keep the old data
        new_delete_data = old_delete_data.tolist()

    # 2. Create the new full DataFrame and update session state
    new_df = edited_df.copy().reset_index(drop=True)
    
    # Ensure the length matches before assigning
    if len(new_delete_data) != len(new_df):
        # This catch is for complex deletions/reorderings in edit mode. Reset to all False if length mismatch.
        new_df['Delete?'] = [False] * len(new_df)
    else:
        new_df['Delete?'] = new_delete_data
        
    st.session_state.df_srs = new_df


# --- Display Buttons based on mode (NEW POSITION BELOW TABLE) ---
btn_col1, btn_col2, _ = st.columns([1.5, 1.5, 3])

if st.session_state.delete_mode:
    
    btn_col1.button("✅ Confirm Deletion", 
                    on_click=delete_marked_rows, 
                    type="primary", 
                    key="confirm_delete_btn",
                    help="Permanently deletes all rows marked with a checkmark.")
    
    btn_col2.button("❌ Cancel Deletion Mode", 
                    on_click=toggle_delete_mode, 
                    type="secondary",
                    key="cancel_delete_btn",
                    help="Go back to the editing mode without deleting.")
    
else:
    btn_col1.button("🗑️ Enter Deletion Mode", 
                    on_click=toggle_delete_mode, 
                    type="secondary",
                    key="enter_delete_btn",
                    help="Click to show checkboxes and select rows for deletion.")


st.markdown("---") 

# --- Calculation Logic ---

# Use the data directly from the updated session state for calculation
current_df_for_calc = st.session_state.df_srs 

if not current_df_for_calc.empty:
    st.header("3. Simulation Results")
    
    # Calculation
    results = []
    # List to store all raw optimal intervals (in hours) for finding the minimum
    raw_intervals_hours = [] 

    for index, row in current_df_for_calc.iterrows():
        # Ensure data is valid before processing and skip marked rows
        try:
            concept = row['Concept']
            # IMPORTANT: Skip calculation for rows marked for deletion (if still in delete mode)
            if row['Delete?'] == True:
                continue
                
            old_lambda = float(row['Initial Lambda']) # FIXED: Access the data using the correct internal column name 'Initial Lambda'
            new_score = float(row['New Quiz Score (0-1)'])
        except (ValueError, TypeError):
            # Skip rows where input is invalid (e.g., empty string in a number field)
            continue 

        # Calculate initial optimal interval (result is in Days)
        initial_interval_days = calculate_optimal_interval(old_lambda, LN_R_TARGET_ADJ)
        
        # Calculate new lambda and new interval (result is in Days)
        new_lambda = update_decay_rate(old_lambda, new_score, beta)
        new_interval_days = calculate_optimal_interval(new_lambda, LN_R_TARGET_ADJ)
        
        # Convert to raw hours for finding the minimum. Store 'inf' if applicable.
        if new_interval_days != float('inf'):
            new_interval_hours_raw = new_interval_days * 24
            raw_intervals_hours.append(new_interval_hours_raw)
        else:
             raw_intervals_hours.append(float('inf'))
        
        # Determine the change in interval (comparison uses days)
        if new_interval_days == float('inf') and initial_interval_days != float('inf'):
             interval_change = 'Stopped Forgetting'
        elif new_interval_days > initial_interval_days:
             interval_change = 'Increased ⬆️'
        elif new_interval_days < initial_interval_days:
             interval_change = 'Decreased ⬇️'
        else:
             interval_change = 'No Change'
        
        results.append({
            'Concept': concept,
            r'Initial Forgetting Rate': f"{old_lambda:.4f}",
            # Apply format_interval_to_hours for output display
            'Initial Interval (Hours)': format_interval_to_hours(initial_interval_days),
            'New Score': f"{new_score:.2f}",
            r'New Forgetting Rate': f"{new_lambda:.4f}",
            # Apply format_interval_to_hours for output display
            'New Optimal Interval (Hours)': format_interval_to_hours(new_interval_days),
            'Interval Change': interval_change
        })
        
    df_results = pd.DataFrame(results)

    # --- New Minimum Interval Calculation & Display ---
    st.subheader("📚 Next Actionable Review Time")
    
    col_min, col_spacer = st.columns([1, 2])
    
    with col_min:
        if raw_intervals_hours:
            # Find the minimum interval (in hours). float('inf') will be ignored if real numbers exist.
            min_raw_interval = min(raw_intervals_hours)
            
            # Round down to the lowest integer hour, or keep infinity symbol
            if min_raw_interval == float('inf'):
                 st.metric(
                     label="Earliest Required Review (Hours)", 
                     value="∞",
                     help="All concepts have an infinite interval, meaning you've effectively mastered them based on current settings."
                 )
            else:
                 # Round down to the lowest number using math.floor()
                 min_rounded_down_hours = math.floor(min_raw_interval)
                 st.metric(
                     label="Earliest Required Review (Hours)", 
                     value=f"{min_rounded_down_hours} h",
                     help="This is the minimum optimal interval across all concepts, rounded down to the nearest hour."
                 )
        else:
            st.info("No valid intervals to calculate the minimum review time.")

    st.markdown("---") 
    
    # --- Display Detailed Results (existing part) ---
    st.subheader("Detailed Optimal Intervals and Decay Rate Adjustments")
    # Ensuring the Pandas index is hidden in the results table display
    st.dataframe(df_results, hide_index=True, use_container_width=True)

    # --- Summary of Impact ---
    st.subheader("Summary of Spaced Repetition Logic")
    
    st.markdown(
        r"""
        - **Low Score (e.g., 0.70):** If the user scores low, the system assumes they are forgetting the concept **faster**. The decay rate ($\lambda$) is **increased**, and the optimal review interval is **decreased** (review sooner).
        - **High Score (e.g., 0.98):** If the user scores high, the system assumes they are forgetting the concept **slower**. The decay rate ($\lambda$) is **decreased**, and the optimal review interval is **increased** (review later).
        """
    )
    
else:
    st.warning("Please add at least one concept to the table to run the simulation.")
