
import hashlib
from html import escape
from pathlib import Path

import streamlit as st

from src.styles import load_styles
from src.session_state import initialize_session_state
from src.data_utils import load_dataset

from views.data_intake import render_data_intake
from views.prepare import render_prepare
from views.visualization_studio import render_visualization_studio
from views.ai_analyst import render_ai_brief
from views.quality_lab import render_quality_lab
from views.overview import render_overview
from views.decision_lab import render_decision_lab
from src.navigation import render_navigation

BASE_DIR = Path(__file__).resolve().parent
LOGO_PATH = BASE_DIR / "assets" / "insightprovider.png"


# =========================================================
# PAGE CONFIGURATION
# =========================================================
st.set_page_config(
    page_title="Datalify | Data Intelligence",
    page_icon=str(Path(__file__).resolve().parent / "assets" / "insightprovider.png"),
    layout="wide",
    initial_sidebar_state="expanded",
)

load_styles()


# =========================================================
# SESSION STATE
# =========================================================
initialize_session_state()

# Define navigation before rendering the sidebar.
pages = [
    "Overview",
    "Data Intake",
    "Quality Lab",
    "Prepare",
    "Visualization Studio",
    "Decision Lab",
    "AI Brief",
    "Export Center",
]



# Initialize the selected page without overwriting an existing selection.
if st.session_state.get("main_navigation") not in pages:
    st.session_state.main_navigation = "Overview"


# =========================================================
# DATASET IMPORT
# =========================================================
def import_dataset(uploaded_file):
    """Load a dataset while preserving an untouched original."""

    file_bytes = uploaded_file.getvalue()
    signature = hashlib.sha256(file_bytes).hexdigest()

    # Avoid importing the same file repeatedly.
    if signature == st.session_state.loaded_file_signature:
        return

    try:
        df = load_dataset(uploaded_file)

        st.session_state.original_df = df.copy(deep=True)
        st.session_state.working_df = df.copy(deep=True)
        st.session_state.dataset_name = uploaded_file.name
        st.session_state.loaded_file_signature = signature

        # Clear state belonging to the previous dataset.
        for key in (
            "cleanup_history",
            "clean_preview",
            "ai_analysis",
            "prepare_history",
            "prepare_recipe",
            "prepare_updated_at",
            "business_kpis",
            "decision_log",
            "viz_export_items",
        ):
            st.session_state.pop(key, None)

        st.session_state["upload_error"] = None

    except Exception as exc:
        st.session_state["upload_error"] = str(exc)



# =========================================================
# LEFT SIDEBAR: BRANDING AND NAVIGATION
# =========================================================
with st.sidebar:

    # ---------- BRANDING ----------
    if LOGO_PATH.is_file():
        st.image(str(LOGO_PATH), width="stretch")
    else:
        st.markdown("<div class='brand-mark'><span class='brand-glyph'>D</span>Datalify</div>", unsafe_allow_html=True)

    st.markdown(
        """
        <div class="brand-tagline">
            Data workspace · from raw data to clear decisions
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("")

    # ---------- NAVIGATION ----------
    render_navigation()

    # ---------- DATASET STATUS ----------
    if st.session_state.working_df is not None:
        current_df = st.session_state.working_df
        dataset_name = escape(str(st.session_state.dataset_name or "Dataset"))
        st.markdown(
            f"""<div class="sidebar-dataset">
              <div class="sidebar-dataset-label">ACTIVE DATASET</div>
              <div class="sidebar-dataset-name">{dataset_name}</div>
              <div style="margin-top:.42rem;color:#AFC0D8;font-size:.74rem">
                {len(current_df):,} rows | {len(current_df.columns):,} columns
              </div>
            </div>""",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            "<div class='sidebar-dataset'><div class='sidebar-dataset-label'>WORKSPACE</div><div class='sidebar-dataset-name'>No dataset loaded</div><div style='margin-top:.42rem;color:#AFC0D8;font-size:.74rem'>Start in Data Intake when you are ready.</div></div>",
            unsafe_allow_html=True,
        )



# =========================================================
# MAIN WORKSPACE HEADER
# =========================================================
page = st.session_state.main_navigation

if page != "Data Intake":
    active_name = st.session_state.get("dataset_name") or "No dataset loaded"
    active_df = st.session_state.get("working_df")
    dimensions = (
        f"{len(active_df):,} rows | {len(active_df.columns):,} columns"
        if active_df is not None
        else "Upload a file in Data Intake to begin"
    )
    st.markdown(
        f"""<div class="workspace-dataset-header">
          <div class="workspace-dataset-mark">D</div>
          <div class="workspace-dataset-copy">
            <div class="workspace-dataset-label">CURRENT DATASET</div>
            <div class="workspace-dataset-name">{escape(str(active_name))}</div>
          </div>
          <div class="workspace-dataset-details">{escape(dimensions)}</div>
        </div>""",
        unsafe_allow_html=True,
    )



# =========================================================
# PAGE ROUTING
# =========================================================

if page == "Overview":
    render_overview()

elif page == "Data Intake":
    render_data_intake(import_dataset)

elif page == "Prepare":
    if st.session_state.working_df is None:
        st.info("Open Data Intake to upload a dataset first.")
    else:
        render_prepare()

elif page == "Quality Lab":
    render_quality_lab()

elif page == "Visualization Studio":
    if st.session_state.working_df is None:
        st.info("Open Data Intake to upload a dataset first.")
    else:
        render_visualization_studio()

elif page == "Decision Lab":
    if st.session_state.working_df is None:
        st.info("Open Data Intake to upload a dataset first.")
    else:
        render_decision_lab()

elif page == "AI Brief":
    if st.session_state.working_df is None:
        st.info("Open Data Intake to upload a dataset first.")
    else:
        render_ai_brief()

elif page == "Export Center":
    if st.session_state.working_df is None:
        st.info("Open Data Intake to upload a dataset first.")
    else:
        from views.export_center import render_export_center

        render_export_center()

# =========================================================
# FOOTER
# =========================================================
st.divider()
st.caption("Datalify | Data Intelligence")
