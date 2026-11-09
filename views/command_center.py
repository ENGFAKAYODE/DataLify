import streamlit as st


def render_command_center():
    st.markdown(
        """
        ## Welcome to Datalify

        Datalify helps you understand, prepare, visualize,
        and analyze data in one place.

        Use the workspaces below to explore the platform.
        """
    )

    st.divider()
    st.markdown("### Explore the workspaces")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Data Intake")
        st.write(
            "Upload CSV or Excel files, preview records, "
            "and inspect dataset structure."
        )

        st.markdown("#### Quality Lab")
        st.write(
            "Investigate missing values, duplicates, "
            "outliers, and data-quality issues."
        )

        st.markdown("#### Visualization Studio")
        st.write(
            "Explore distributions, charts, and relationships."
        )

    with col2:
        st.markdown("#### AI Analyst")
        st.write(
            "Ask questions and explore findings from your data."
        )

        st.markdown("#### Export Center")
        st.write(
            "Prepare cleaned datasets and analysis reports."
        )

    st.divider()
    st.markdown("### Recommended workflow")
    st.markdown(
        "**Understand → Validate → Explore → Analyze → Export**"
    )
