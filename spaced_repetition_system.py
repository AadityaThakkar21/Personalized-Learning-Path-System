import streamlit as st
import math
import pandas as pd

# --- Configuration Constants (Defaults) ---
R_TARGET_DEFAULT = 0.85
BETA_DEFAULT = 0.2

# --- Core Functions ---
# Modified to accept the adjusted LN_R_TARGET value
def calculate_optimal_interval(decay_rate: float, ln_r_target_adj: float) -> float:
    """Calculates the optimal review interval (t_i in days) for a concept."""
    # We use -ln_r_target_adj because math.log(R_TARGET) is negative.
    if decay_rate <= 0:
        return float('inf')
    
    optimal_interval = -ln_r_target_adj / decay_rate
    return optimal_interval

# Modified to accept the adjusted beta value
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
    """Converts days to hours and handles infinity for display."""
    if interval_days == float('inf'):
        return '∞'
    # Convert days to hours and format to two decimal places
    return f"{interval_days * 24:.2f}"

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
    st.markdown(f"""
        This tool uses a simple exponential decay model to calculate your optimal review intervals ($t_i$).

        ### Model Configuration

        * **Target Retention Rate ($R_{{target}}$):**
            * **Description:** The percentage of knowledge you aim to retain *just* before the next review.
            * **Usage:** Higher $R_{{target}}$ means shorter, more frequent intervals.

        * **Decay Rate Tuning Parameter ($\beta$):**
            * **Description:** Controls how quickly your personalized forgetting curve ($\lambda$) adjusts after a quiz score.
            * **Usage:** Higher $\beta$ means $\lambda$ adjusts more aggressively based on the score.

        ### Concept Table Variables

        * **Initial Lambda ($\lambda_{{old}}$):**
            * **Description:** The personalized forgetting rate for a concept *before* the latest quiz.
            * **Usage:** You estimate this when you first add a concept: **low $\lambda$ for easy concepts, high $\lambda$ for hard concepts.**
            * *The system updates this value to the "New $\lambda$" after each simulation.*

        * **New Quiz Score (0-1):**
            * **Description:** Your score from the most recent test/review of that concept (1.0 = 100%).
        """)
st.markdown("---")

# --- Model Configuration Inputs ---
st.header("1. Model Configuration")
config_col1, config_col2 = st.columns(2)

with config_col1:
    st.markdown(r"### Target Retention Rate ($R_{target}$)")
    r_target = st.slider(
        'Set $R_{target}$ (decimal)',
        min_value=0.75, max_value=0.99, value=R_TARGET_DEFAULT, step=0.01,
        label_visibility="collapsed"
    )
    # Calculate the natural log of the target retention rate
    LN_R_TARGET_ADJ = math.log(r_target)
    st.info(f"The system aims to keep knowledge retention at **{r_target * 100:.0f}%**.")

with config_col2:
    st.markdown(r"### Decay Rate Tuning ($\beta$)")
    beta = st.slider(
        r'Set Decay Tuning Parameter ($\beta$)',
        min_value=0.05, max_value=0.50, value=BETA_DEFAULT, step=0.01,
        label_visibility="collapsed"
    )
    st.info(r"A higher $\beta$ means the decay rate adjusts more aggressively based on the quiz score.")

st.markdown("---")

# --- Main App: Input Table ---

st.header("2. Define Your Concepts")

# Initialize session state for the dataframe if it doesn't exist
if 'df_srs' not in st.session_state:
    st.session_state.df_srs = pd.DataFrame({
        'Concept': ['T-tests (Hard)', 'Linear Algebra Basics (Easy)'],
        'Initial Lambda': [0.15, 0.05],
        'New Quiz Score (0-1)': [0.70, 0.98]
    })

# Editable Dataframe
st.markdown("Edit the table below to simulate different concepts and quiz scores.")
edited_df = st.data_editor(
    st.session_state.df_srs,
    num_rows="dynamic",
    column_config={
        "Concept": st.column_config.TextColumn("Concept Name", required=True),
        "Initial Lambda": st.column_config.NumberColumn(
            r"Initial Lambda ($\lambda_{old}$)", 
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
        ),
    },
    hide_index=True,
    key="data_editor_srs"
)

st.session_state.df_srs = edited_df

# --- Row Deletion Logic ---
# Add a button to delete the last row
if st.button("🗑️ Delete Latest Row", help="Removes the last row from the table."):
    if not st.session_state.df_srs.empty:
        # Check if we can safely delete a row (i.e., if there are any rows to delete)
        if len(st.session_state.df_srs) > 0:
            # Remove the last row using iloc
            st.session_state.df_srs = st.session_state.df_srs.iloc[:-1]
            st.rerun() # Rerun to update the display immediately
        else:
            st.warning("The table is already empty.")
    else:
        st.warning("The table is already empty.")

# --- Calculation Logic ---

if not edited_df.empty:
    st.header("3. Simulation Results")
    
    # Calculation
    results = []
    for index, row in edited_df.iterrows():
        # Ensure data is valid before processing
        try:
            concept = row['Concept']
            old_lambda = float(row['Initial Lambda'])
            new_score = float(row['New Quiz Score (0-1)'])
        except (ValueError, TypeError):
            # Skip rows where input is invalid (e.g., empty string in a number field)
            continue 

        # Calculate initial optimal interval (result is in Days)
        initial_interval = calculate_optimal_interval(old_lambda, LN_R_TARGET_ADJ)
        
        # Calculate new lambda and new interval (result is in Days)
        new_lambda = update_decay_rate(old_lambda, new_score, beta)
        new_interval = calculate_optimal_interval(new_lambda, LN_R_TARGET_ADJ)
        
        # Determine the change in interval (comparison uses days)
        if new_interval == float('inf') and initial_interval != float('inf'):
             interval_change = 'Stopped Forgetting'
        elif new_interval > initial_interval:
             interval_change = 'Increased ⬆️'
        elif new_interval < initial_interval:
             interval_change = 'Decreased ⬇️'
        else:
             interval_change = 'No Change'
        
        results.append({
            'Concept': concept,
            r'Initial $\lambda$': f"{old_lambda:.4f}",
            # Apply format_interval_to_hours for output display
            'Initial Interval (Hours)': format_interval_to_hours(initial_interval),
            'New Score': f"{new_score:.2f}",
            r'New $\lambda$': f"{new_lambda:.4f}",
            # Apply format_interval_to_hours for output display
            'New Optimal Interval (Hours)': format_interval_to_hours(new_interval),
            'Interval Change': interval_change
        })
        
    df_results = pd.DataFrame(results)
    
    # --- Display Results ---
    st.subheader("Optimal Intervals and Decay Rate Adjustments")
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

st.markdown("---")
st.caption(r"The core formula for the optimal interval $t_i$ is $t_i = \frac{-ln(R_{target})}{\lambda}$.")
