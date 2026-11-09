import streamlit as st


def render_navigation():
    """Render Datalify's sidebar navigation."""

    pages = [
        ("Overview", "space_dashboard"),
        ("Data Intake", "database"),
        ("Quality Lab", "health_and_safety"),
        ("Prepare", "fact_check"),
        ("Visualization Studio", "bar_chart"),
        ("Decision Lab", "query_stats"),
        ("AI Brief", "psychology"),
        ("Export Center", "download"),
    ]

    for name, icon_name in pages:
        is_selected = (
            st.session_state.main_navigation == name
        )

        if st.button(
            name,
            key=f"nav_{name}",
            icon=f":material/{icon_name}:",
            width="stretch",
            type="primary" if is_selected else "secondary",
        ):
            st.session_state.main_navigation = name
            st.rerun()
