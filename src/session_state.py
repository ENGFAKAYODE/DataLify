
import streamlit as st


def initialize_session_state():
    defaults = {
        # Navigation
        "main_navigation": "Overview",

        # Dataset management
        "original_df": None,
        "working_df": None,
        "dataset_name": None,
        "loaded_file_signature": None,
        "upload_error": None,

        # Prepare workspace
        "prepare_history": [],
        "prepare_recipe": [],
        "prepare_updated_at": None,
        "business_kpis": [],
        "decision_log": [],
        "viz_export_items": [],

        # Other workspace state
        "cleanup_history": [],
        "clean_preview": None,
        "ai_analysis": None,
        "ai_agentic_brief": None,
        "ai_agent_messages": [],
        "ai_agent_evidence": {},
        "ai_brief_agent_messages": [],
        "ai_brief_agent_evidence": {},
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    # Prevent invalid navigation values without
    # resetting the user's current page on reruns.
    valid_pages = [
        "Overview",
        "Data Intake",
        "Quality Lab",
        "Prepare",
        "Visualization Studio",
        "Decision Lab",
        "AI Brief",
        "Export Center",
    ]

    if st.session_state.main_navigation not in valid_pages:
        st.session_state.main_navigation = "Overview"
