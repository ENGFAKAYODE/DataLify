
import hashlib
from pathlib import Path
import plotly.express as px
import pandas as pd
import streamlit as st

from src.data_utils import (
    load_dataset,
    get_dataset_summary,
    get_schema,
)


# =========================================================
# PAGE CONFIGURATION
# =========================================================
BASE_DIR = Path(__file__).resolve().parent
LOGO_PATH = BASE_DIR / "assets" / "insightprovider.png"

st.set_page_config(
    page_title="Datalify | InsightProvider",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)



# =========================================================
# CUSTOM DESIGN: DATALIFY PRO
# =========================================================
st.markdown(
    """
    <style>
    /* ---------- GLOBAL ---------- */
    .stApp {
        background: #F6F8FC;
        color: #17233B;
        font-family: "Inter", "Segoe UI", sans-serif;
    }

    .block-container {
        padding-top: 1.8rem;
        padding-bottom: 2rem;
        max-width: 1800px;
    }

    h1, h2, h3, h4 {
        color: #14213D;
        letter-spacing: -0.45px;
        font-weight: 700;
    }

    h1 {
        font-size: 2rem !important;
    }

    h2 {
        font-size: 1.35rem !important;
    }

    h3 {
        font-size: 1.05rem !important;
    }

    p, li, label {
        line-height: 1.65;
    }

    /* ---------- SIDEBAR ---------- */
    [data-testid="stSidebar"] {
        background: linear-gradient(
            180deg,
            #0E1B32 0%,
            #142743 100%
        );
        border-right: 1px solid #223755;
    }

    [data-testid="stSidebar"] > div {
        padding-top: 1.5rem;
    }

    [data-testid="stSidebar"] * {
        color: #E8EFFB;
    }

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] h4 {
        color: #FFFFFF;
    }

    [data-testid="stSidebar"] [data-testid="stRadio"] label {
        border-radius: 10px;
        padding: 9px 12px;
        margin-bottom: 5px;
        transition: background 0.2s ease;
    }

    [data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
        background: #223B61;
    }

    [data-testid="stSidebar"] hr {
        border-color: #2A3E5B;
    }

    [data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
        color: #AFC2DE;
    }

    /* ---------- WORKSPACE DESCRIPTION ---------- */
    .workspace-caption {
        color: #687993;
        font-size: 0.94rem;
        margin-top: -9px;
        margin-bottom: 25px;
        line-height: 1.6;
    }

    .brand-caption {
        color: #B8C9E2;
        font-size: 0.83rem;
        line-height: 1.6;
    }

    /* ---------- METRIC CARDS ---------- */
    [data-testid="stMetric"] {
        background: #FFFFFF;
        border: 1px solid #E4EAF4;
        border-radius: 14px;
        padding: 18px 20px;
        box-shadow: 0 3px 12px rgba(24, 43, 77, 0.035);
        min-height: 110px;
    }

    [data-testid="stMetricLabel"] {
        color: #64748B;
        font-size: 0.84rem;
        font-weight: 600;
    }

    [data-testid="stMetricValue"] {
        color: #172B4D;
        font-size: 1.75rem;
        font-weight: 750;
    }

    [data-testid="stMetricDelta"] {
        font-size: 0.8rem;
    }

    /* ---------- DATA TABLES ---------- */
    [data-testid="stDataFrame"] {
        background: #FFFFFF;
        border: 1px solid #E1E8F2;
        border-radius: 12px;
        overflow: hidden;
    }

    /* ---------- INPUTS ---------- */
    [data-testid="stTextInput"] input,
    [data-testid="stTextArea"] textarea,
    [data-testid="stSelectbox"] > div > div,
    [data-testid="stNumberInput"] input {
        background: #FFFFFF;
        border-color: #D9E2EF;
        border-radius: 9px;
    }

    [data-testid="stFileUploader"] {
        background: #FFFFFF;
        border: 1px dashed #9EB2CF;
        border-radius: 14px;
        padding: 18px;
    }

    /* ---------- BUTTONS ---------- */
    div.stButton > button,
    div[data-testid="stDownloadButton"] > button {
        border-radius: 9px;
        min-height: 42px;
        font-weight: 600;
        border: 1px solid #D8E2F0;
        transition: all 0.2s ease;
    }

    div.stButton > button:hover,
    div[data-testid="stDownloadButton"] > button:hover {
        border-color: #4678D7;
        color: #2859B9;
        box-shadow: 0 3px 10px rgba(40, 89, 185, 0.08);
    }

    /* ---------- TABS ---------- */
    [data-testid="stTabs"] [data-baseweb="tab-list"] {
        gap: 8px;
        border-bottom: 1px solid #E1E8F2;
    }

    [data-testid="stTabs"] [data-baseweb="tab"] {
        background: transparent;
        border-radius: 8px 8px 0 0;
        padding: 10px 16px;
        color: #61718A;
        font-weight: 600;
    }

    [data-testid="stTabs"] [aria-selected="true"] {
        color: #2859B9;
        border-bottom: 2px solid #4678D7;
    }

    /* ---------- ALERTS ---------- */
    [data-testid="stAlert"] {
        border-radius: 11px;
        border: 1px solid #DCE6F4;
    }

    /* ---------- SEPARATORS AND FOOTER ---------- */
    hr {
        border-color: #E3EAF4;
        margin-top: 1.4rem;
        margin-bottom: 1.4rem;
    }

    [data-testid="stCaptionContainer"] {
        color: #70819B;
    }

    /* ---------- RESPONSIVE ---------- */
    @media (max-width: 768px) {
        .block-container {
            padding-top: 1rem;
            padding-left: 1rem;
            padding-right: 1rem;
        }

        h1 {
            font-size: 1.6rem !important;
        }

        [data-testid="stMetric"] {
            padding: 13px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# SESSION STATE
# =========================================================
defaults = {
    "original_df": None,
    "working_df": None,
    "dataset_name": None,
    "loaded_file_signature": None,
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


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
        ):
            st.session_state.pop(key, None)

        st.session_state["upload_error"] = None

    except Exception as exc:
        st.session_state["upload_error"] = str(exc)


# =========================================================
# LEFT SIDEBAR: BRANDING AND NAVIGATION
# =========================================================
with st.sidebar:

    if LOGO_PATH.is_file():
        st.image(
            str(LOGO_PATH),
            use_container_width=True,
        )
    else:
        st.markdown("##  InsightProvider")
        st.warning(f"Logo not found at: {LOGO_PATH}")

    st.markdown(
        '<div class="brand-caption">'
        'Datalify · Intelligent Data Analysis'
        '</div>',
        unsafe_allow_html=True,
    )

    st.divider()
    st.markdown("##### WORKSPACE")

    pages = [
        "Command Center",
        "Data Intake",
        "Quality Lab",
        "Visualization Studio",
        "AI Analyst",
        "Export Center",
    ]

    icons = {
        "Command Center": "",
        "Data Intake": "",
        "Quality Lab": "",
        "Visualization Studio": "",
        "AI Analyst": "",
        "Export Center": "",
    }

    page = st.radio(
        "Main navigation",
        pages,
        format_func=lambda name: f"{icons[name]}  {name}",
        label_visibility="collapsed",
        key="main_navigation",
    )

    st.divider()

    # Dataset status is displayed in the sidebar only.
    if st.session_state.working_df is not None:
        current_df = st.session_state.working_df

        st.markdown("##### ACTIVE DATASET")
        st.caption(f" {st.session_state.dataset_name}")
        st.caption(
            f"{len(current_df):,} rows · "
            f"{len(current_df.columns):,} columns"
        )
    else:
        st.markdown("##### NO ACTIVE DATASET")
        st.caption(
            "Open Data Intake to upload a dataset."
        )

    st.divider()

    st.markdown(
        '<div class="brand-caption">'
        'Turn your data into clear, actionable insights.'
        '</div>',
        unsafe_allow_html=True,
    )


# =========================================================
# MAIN WORKSPACE HEADER
# =========================================================
descriptions = {
    "Command Center":
        "Your guide to Datalify and its workspaces.",
    "Data Intake":
        "Upload, preview, and understand the structure of your data.",
    "Quality Lab":
        "Profile, validate, and prepare data before drawing conclusions.",
    "Visualization Studio":
        "Explore distributions, relationships, and business patterns.",
    "AI Analyst":
        "Generate evidence-based, business-readable analysis.",
    "Export Center":
        "Package cleaned data and analysis into shareable deliverables.",
}

st.title(page)

st.markdown(
    f'<div class="workspace-caption">'
    f'{descriptions[page]}'
    f'</div>',
    unsafe_allow_html=True,
)


# =========================================================
# PAGE ROUTING
# =========================================================

# 1. COMMAND CENTER
# Documentation only. No uploader or dataset metrics.
if page == "Command Center":

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
        st.markdown("####  Data Intake")
        st.write(
            "Upload CSV or Excel files, preview records, "
            "and inspect dataset structure."
        )

        st.markdown("####  Quality Lab")
        st.write(
            "Investigate missing values, duplicates, "
            "outliers, and data-quality issues."
        )

        st.markdown("####  Visualization Studio")
        st.write(
            "Explore distributions, charts, and relationships."
        )

    with col2:
        st.markdown("####  AI Analyst")
        st.write(
            "Ask questions and explore findings from your data."
        )

        st.markdown("####  Export Center")
        st.write(
            "Prepare cleaned datasets and analysis reports."
        )

    st.divider()
    st.markdown("### Recommended workflow")
    st.markdown(
        """
        **Understand → Validate → Explore → Analyze → Export**
        """
    )


# 2. DATA INTAKE
elif page == "Data Intake":

    st.markdown("### Bring your data into Datalify")

    st.write(
        "Upload a CSV or Excel workbook to inspect, clean, "
        "visualize, and analyze your data."
    )

    uploaded_file = st.file_uploader(
        "Choose a CSV or Excel file",
        type=["csv", "xlsx", "xls"],
        key="main_dataset_uploader",
    )

    if uploaded_file is not None:
        import_dataset(uploaded_file)

    if st.session_state.get("upload_error"):
        st.error(
            f"Could not load the dataset: "
            f"{st.session_state['upload_error']}"
        )

    if st.session_state.working_df is None:

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("####  Data quality")
            st.write(
                "Identify missing values, duplicates, "
                "and potential data problems."
            )

        with col2:
            st.markdown("####  Explore patterns")
            st.write(
                "Explore distributions, relationships, "
                "and trends."
            )

        with col3:
            st.markdown("####  Business insights")
            st.write(
                "Translate evidence into useful findings "
                "and next actions."
            )

    else:

        df = st.session_state.working_df
        summary = get_dataset_summary(df)

        st.success(
            f"Loaded: {st.session_state.dataset_name}"
        )

        c1, c2, c3, c4 = st.columns(4)

        c1.metric("Rows", f"{summary['rows']:,}")
        c2.metric("Columns", f"{summary['columns']:,}")
        c3.metric(
            "Completeness",
            f"{summary['completeness']:.1f}%"
        )
        c4.metric(
            "Memory usage",
            f"{summary['memory_bytes'] / 1024:.1f} KB"
        )

        preview_tab, schema_tab = st.tabs(
            ["Preview Data", "Schema"]
        )

        with preview_tab:
            st.dataframe(
                df.head(100),
                use_container_width=True,
                hide_index=True,
            )

        with schema_tab:
            st.dataframe(
                get_schema(df),
                use_container_width=True,
                hide_index=True,
            )


# 3. ALL OTHER WORKSPACES
else:

    # Pages that require a dataset must check for one first.
    if st.session_state.working_df is None:

        st.info(
            "No dataset is loaded. Open Data Intake to upload "
            "a CSV or Excel file before using this workspace."
        )

    else:

        df = st.session_state.working_df



        if page == "Quality Lab":

            # =================================================
            # QUALITY LAB: HELPERS
            # =================================================
            def quality_metrics(data):
                rows = len(data)
                total_cells = rows * len(data.columns)

                missing = int(data.isna().sum().sum())
                duplicates = int(data.duplicated().sum())

                missing_percent = (
                    missing / total_cells * 100
                    if total_cells else 0
                )

                duplicate_percent = (
                    duplicates / rows * 100
                    if rows else 0
                )

                score = max(
                    0,
                    100
                    - missing_percent * 0.7
                    - duplicate_percent * 0.3,
                )

                return {
                    "Rows": rows,
                    "Missing values": missing,
                    "Duplicate rows": duplicates,
                    "Quality score": round(score, 2),
                }

            def build_cleaned_preview(
                data,
                remove_duplicates,
                trim_whitespace,
                fill_missing,
                fill_strategy,
            ):
                result = data.copy(deep=True)

                if trim_whitespace:
                    text_columns = result.select_dtypes(
                        include=["object", "string"]
                    ).columns

                    for column in text_columns:
                        result[column] = result[column].map(
                            lambda value: (
                                value.strip()
                                if isinstance(value, str)
                                else value
                            )
                        )

                if fill_missing:
                    for column in result.columns:
                        if not result[column].isna().any():
                            continue

                        series = result[column]

                        if fill_strategy == "Median" and (
                            pd.api.types.is_numeric_dtype(series)
                        ):
                            value = series.median()

                        elif fill_strategy == "Mode":
                            modes = series.mode(dropna=True)
                            value = (
                                modes.iloc[0]
                                if not modes.empty
                                else None
                            )

                        else:
                            value = None

                        if value is not None and not pd.isna(value):
                            result[column] = series.fillna(value)

                if remove_duplicates:
                    result = result.drop_duplicates()

                return result.reset_index(drop=True)


            # =================================================
            # QUALITY LAB HEADER AND CONSTANT KPIs
            # =================================================
            st.markdown("## Data Quality Lab")

            st.caption(
            "Profile column-level quality, investigate distributions "
            "and relationships, clean your data, and identify potential "
            "numeric outliers."
            )

            # Always use the latest working dataset.
            df = st.session_state.working_df.copy(deep=True)

            # KPIs appear above the tabs, so they are shared by all three.
            row_count = len(df)
            column_count = len(df.columns)
            missing_count = int(df.isna().sum().sum())
            duplicate_count = int(df.duplicated().sum())

            k1, k2, k3, k4 = st.columns(4)

            k1.metric("Rows", f"{row_count:,}")
            k2.metric("Columns", f"{column_count:,}")
            k3.metric("Missing cells", f"{missing_count:,}")
            k4.metric("Duplicate rows", f"{duplicate_count:,}")


            # =================================================
            # MAIN TABS
            # =================================================
            profile_tab, clean_tab, outlier_tab = st.tabs(
                ["Profile", "Clean", "Outlier"]
            )

            # =================================================
            # PROFILE TAB
            # =================================================
            with profile_tab:

                st.markdown("### Column-level quality profile")

                st.write(
                    "Column-level quality, distribution, "
                    "uniqueness, and relationship checks."
                )

                missing_by_column = df.isna().sum()

                completeness = (
                    (1 - missing_by_column / row_count) * 100
                    if row_count
                    else pd.Series(100.0, index=df.columns)
                )



                # ---------------------------------------------
                # MISSINGNESS BY COLUMN: FIXED 0–100% SCALE
                # ---------------------------------------------
                st.markdown("### Missingness by columns")

                missing_chart = pd.DataFrame({
                    "Column": df.columns,
                    "Missingness (%)": [
                        round(
                            df[column].isna().sum() / max(row_count, 1) * 100,
                            2,
                        )
                        for column in df.columns
                    ],
                })

                missing_chart = (
                    missing_chart[
                        missing_chart["Missingness (%)"] > 0
                    ]
                    .sort_values("Missingness (%)", ascending=True)
                )

                if missing_chart.empty:
                    st.success("No missing values were found in the dataset.")
                else:
                    fig = px.bar(
                        missing_chart,
                        x="Missingness (%)",
                        y="Column",
                        orientation="h",
                        range_x=[0, 100],
                        text="Missingness (%)",
                        labels={
                            "Missingness (%)": "Missing values (%)",
                            "Column": "Column",
                        },
                        title="Percentage of missing values by column",
                    )

                    fig.update_traces(
                        texttemplate="%{text:.2f}%",
                        textposition="outside",
                        cliponaxis=False,
                    )

                    fig.update_layout(
                        xaxis=dict(
                            range=[0, 100],
                            ticksuffix="%",
                            dtick=10,
                            title="Missing values (%)",
                        ),
                        yaxis=dict(
                            title="",
                            automargin=True,
                        ),
                        showlegend=False,
                        margin=dict(l=10, r=45, t=60, b=10),
                    )

                    st.plotly_chart(
                        fig,
                        use_container_width=True,
                    )


                # ---------------------------------------------
                # STRONGEST CORRELATIONS
                # ---------------------------------------------
                st.markdown("### Strongest correlations")

                numeric_df = df.select_dtypes(include="number")

                if numeric_df.shape[1] < 2:
                    st.info(
                        "At least two numeric columns are required "
                        "to calculate correlations."
                    )
                else:
                    correlation_matrix = numeric_df.corr(method="pearson")

                    pairs = []

                    for i, column_a in enumerate(correlation_matrix.columns):
                        for column_b in correlation_matrix.columns[i + 1:]:
                            correlation = correlation_matrix.loc[
                                column_a, column_b
                            ]

                            if pd.notna(correlation):
                                pairs.append({
                                    "Feature_A": column_a,
                                    "Feature_B": column_b,
                                    "Correlation": round(float(correlation), 3),
                                    "Absolute correlation": abs(float(correlation)),
                                })

                    if pairs:
                        correlation_profile = pd.DataFrame(pairs)

                        correlation_profile = (
                            correlation_profile
                            .sort_values(
                                "Absolute correlation",
                                ascending=False,
                            )
                            .head(10)
                        )

                        chart_data = correlation_profile.copy()

                        chart_data["Pair"] = (
                            chart_data["Feature_A"].astype(str)
                            + " ↔ "
                            + chart_data["Feature_B"].astype(str)
                        )

                        st.bar_chart(
                            chart_data.set_index("Pair")[["Correlation"]],
                            horizontal=True,
                            use_container_width=True,
                        )

                        st.dataframe(
                            correlation_profile[
                                ["Feature_A", "Feature_B", "Correlation"]
                            ],
                            use_container_width=True,
                            hide_index=True,
                        )

                        st.caption(
                            "Pearson correlation ranges from -1 to +1. "
                            "Correlation does not establish causation."
                        )
                    else:
                        st.info(
                            "No valid numeric column pairs are "
                            "available for correlation analysis."
                        )

                st.divider()


                # ---------------------------------------------
                # COLUMN QUALITY TABLE
                # ---------------------------------------------
                st.markdown("### Column quality table")

                quality_table = pd.DataFrame({
                    "Column": df.columns,
                    "Data Type": [
                        str(df[column].dtype)
                        for column in df.columns
                    ],
                    "Missing Values": [
                        int(df[column].isna().sum())
                        for column in df.columns
                    ],
                    "Completeness (%)": [
                        round(float(completeness[column]), 2)
                        for column in df.columns
                    ],
                    "Unique Values": [
                        int(df[column].nunique(dropna=True))
                        for column in df.columns
                    ],
                    "Unique (%)": [
                        round(
                            df[column].nunique(dropna=True)
                            / max(row_count, 1) * 100,
                            2,
                        )
                        for column in df.columns
                    ],
                })

                quality_table["Status"] = quality_table[
                    "Completeness (%)"
                ].apply(
                    lambda value: (
                        "Complete"
                        if value == 100
                        else "Needs attention"
                        if value > 0
                        else "Empty"
                    )
                )

                st.dataframe(
                    quality_table,
                    use_container_width=True,
                    hide_index=True,
                )

                st.divider()

                # ---------------------------------------------
                # NUMERIC AND CATEGORICAL PROFILE TABS
                # ---------------------------------------------
                numeric_profile_tab, categorical_profile_tab = (
                    st.tabs(
                        ["Numeric Profile", "Categorical Profile"]
                    )
                )

                with numeric_profile_tab:

                    st.markdown("#### Numeric column profile")

                    numeric_columns = df.select_dtypes(
                        include="number"
                    ).columns.tolist()

                    if not numeric_columns:
                        st.info(
                            "No numeric columns were detected."
                        )
                    else:
                        numeric_summary = (
                            df[numeric_columns]
                            .describe()
                            .T
                            .reset_index()
                            .rename(
                                columns={"index": "Column"}
                            )
                        )

                        numeric_summary["Missing"] = [
                            int(df[column].isna().sum())
                            for column in numeric_columns
                        ]

                        numeric_summary["Unique"] = [
                            int(df[column].nunique())
                            for column in numeric_columns
                        ]

                        st.dataframe(
                            numeric_summary,
                            use_container_width=True,
                            hide_index=True,
                        )

                with categorical_profile_tab:

                    st.markdown("#### Categorical column profile")

                    categorical_columns = df.select_dtypes(
                        include=["object", "string", "category", "bool"]
                    ).columns.tolist()

                    if not categorical_columns:
                        st.info(
                            "No categorical or text columns "
                            "were detected."
                        )
                    else:
                        categorical_rows = []

                        for column in categorical_columns:
                            values = df[column].dropna()
                            counts = values.value_counts()

                            categorical_rows.append({
                                "Column": column,
                                "Unique Values": int(
                                    values.nunique()
                                ),
                                "Most Frequent Value": (
                                    str(counts.index[0])
                                    if not counts.empty
                                    else "N/A"
                                ),
                                "Most Frequent Count": (
                                    int(counts.iloc[0])
                                    if not counts.empty
                                    else 0
                                ),
                                "Missing Values": int(
                                    df[column].isna().sum()
                                ),
                            })

                        st.dataframe(
                            pd.DataFrame(categorical_rows),
                            use_container_width=True,
                            hide_index=True,
                        )

                        selected_category = st.selectbox(
                            "Inspect category distribution",
                            categorical_columns,
                            key="quality_category_distribution",
                        )

                        category_counts = (
                            df[selected_category]
                            .fillna("(Missing)")
                            .astype(str)
                            .value_counts()
                            .head(15)
                        )

                        st.bar_chart(
                            category_counts,
                            horizontal=True,
                            use_container_width=True,
                        )

            # =================================================
            # CLEAN TAB
            # =================================================
            with clean_tab:

                st.markdown("### Clean your dataset")

                st.write(
                    "Apply reversible session-level cleanup. "
                    "You can reset to the original upload any time."
                )

                original_df = st.session_state.original_df

                if original_df is None:
                    st.warning(
                        "The original upload is unavailable. "
                        "Upload the dataset again to enable reset."
                    )
                else:
                    current_df = (
                        st.session_state.working_df.copy(deep=True)
                    )

                    before_metrics = quality_metrics(current_df)

                    # -----------------------------------------
                    # CLEANING OPTIONS
                    # -----------------------------------------
                    st.markdown("#### Choose cleanup operations")

                    remove_duplicates = st.checkbox(
                        "Remove duplicate rows",
                        value=True,
                        key="clean_preview_duplicates",
                    )

                    trim_whitespace = st.checkbox(
                        "Trim leading and trailing text whitespace",
                        value=True,
                        key="clean_preview_whitespace",
                    )

                    fill_missing = st.checkbox(
                        "Fill missing values",
                        value=False,
                        key="clean_preview_missing",
                    )

                    fill_strategy = st.selectbox(
                        "Missing-value strategy",
                        ["Median", "Mode"],
                        help=(
                            "Median fills numeric columns. Mode fills "
                            "columns with their most frequent value. "
                            "Columns without a suitable fill value "
                            "are left unchanged."
                        ),
                        key="clean_preview_fill_strategy",
                    )

                    preview_df = build_cleaned_preview(
                        current_df,
                        remove_duplicates,
                        trim_whitespace,
                        fill_missing,
                        fill_strategy,
                    )

                    after_metrics = quality_metrics(preview_df)

                    st.divider()

                    # -----------------------------------------
                    # CLEANUP IMPACT PREVIEW
                    # -----------------------------------------
                    st.markdown("### Cleanup impact preview")

                    st.caption(
                        "Compare the current working dataset with "
                        "the proposed result before applying changes."
                    )

                    impact_table = pd.DataFrame({
                        "Metric": [
                            "Rows",
                            "Missing values",
                            "Duplicate rows",
                            "Quality score",
                        ],
                        "Before": [
                            f"{before_metrics['Rows']:,}",
                            f"{before_metrics['Missing values']:,}",
                            f"{before_metrics['Duplicate rows']:,}",
                            f"{before_metrics['Quality score']:.2f}%",
                        ],
                        "After": [
                            f"{after_metrics['Rows']:,}",
                            f"{after_metrics['Missing values']:,}",
                            f"{after_metrics['Duplicate rows']:,}",
                            f"{after_metrics['Quality score']:.2f}%",
                        ],
                    })

                    st.dataframe(
                        impact_table,
                        use_container_width=True,
                        hide_index=True,
                    )

                    m1, m2, m3, m4 = st.columns(4)

                    m1.metric(
                        "Rows",
                        f"{after_metrics['Rows']:,}",
                        delta=(
                            after_metrics["Rows"]
                            - before_metrics["Rows"]
                        ),
                    )

                    m2.metric(
                        "Missing values",
                        f"{after_metrics['Missing values']:,}",
                        delta=(
                            after_metrics["Missing values"]
                            - before_metrics["Missing values"]
                        ),
                        delta_color="inverse",
                    )

                    m3.metric(
                        "Duplicate rows",
                        f"{after_metrics['Duplicate rows']:,}",
                        delta=(
                            after_metrics["Duplicate rows"]
                            - before_metrics["Duplicate rows"]
                        ),
                        delta_color="inverse",
                    )

                    m4.metric(
                        "Quality score",
                        f"{after_metrics['Quality score']:.2f}%",
                        delta=round(
                            after_metrics["Quality score"]
                            - before_metrics["Quality score"],
                            2,
                        ),
                    )

                    st.caption(
                        "This quality score is an indicative measure "
                        "based on missing cells and duplicate rows. "
                        "It does not assess factual correctness."
                    )

                    # -----------------------------------------
                    # APPLY OR RESET
                    # -----------------------------------------
                    apply_col, reset_col = st.columns(2)

                    with apply_col:
                        if st.button(
                            "Apply cleanup",
                            type="primary",
                            use_container_width=True,
                            key="apply_quality_cleanup",
                        ):
                            st.session_state.working_df = (
                                preview_df.copy(deep=True)
                            )

                            st.success(
                                "Cleanup applied to the working dataset."
                            )

                            st.rerun()

                    with reset_col:
                        if st.button(
                            "Reset to original upload",
                            use_container_width=True,
                            key="reset_quality_cleanup",
                        ):
                            st.session_state.working_df = (
                                original_df.copy(deep=True)
                            )

                            for state_key in (
                                "cleanup_history",
                                "clean_preview",
                                "ai_analysis",
                            ):
                                st.session_state.pop(
                                    state_key, None
                                )

                            st.success(
                                "Restored the original uploaded dataset."
                            )

                            st.rerun()

                    # -----------------------------------------
                    # CLEANUP PREVIEW
                    # -----------------------------------------
                    with st.expander(
                        "Preview the first 20 rows after cleanup"
                    ):
                        st.dataframe(
                            preview_df.head(20),
                            use_container_width=True,
                            hide_index=True,
                        )

            # =================================================
            # OUTLIER TAB
            # =================================================
            with outlier_tab:

                st.markdown("### IQR outlier analysis")

                st.write(
                    "Review potential outliers in numeric columns "
                    "using the interquartile range method."
                )

                st.caption(
                    "An observation is flagged when it is below "
                    "Q1 − 1.5 × IQR or above Q3 + 1.5 × IQR. "
                    "Flagged values are not automatically removed."
                )

                numeric_columns = df.select_dtypes(
                    include="number"
                ).columns.tolist()

                outlier_records = []

                for column in numeric_columns:

                    values = df[column].dropna()

                    if values.empty:
                        continue

                    q1 = values.quantile(0.25)
                    q3 = values.quantile(0.75)
                    iqr = q3 - q1

                    lower_bound = q1 - 1.5 * iqr
                    upper_bound = q3 + 1.5 * iqr

                    outlier_mask = (
                        (values < lower_bound)
                        | (values > upper_bound)
                    )

                    outlier_count = int(outlier_mask.sum())

                    outlier_records.append({
                        "column": column,
                        "outliers": outlier_count,
                        "outlier_percent": round(
                            outlier_count / len(values) * 100,
                            2,
                        ),
                        "lower_bound": lower_bound,
                        "upper_bound": upper_bound,
                    })

                if not outlier_records:

                    st.info(
                        "No numeric columns with valid observations "
                        "were available for outlier analysis."
                    )

                else:

                    outlier_table = pd.DataFrame(
                        outlier_records,
                        columns=[
                            "column",
                            "outliers",
                            "outlier_percent",
                            "lower_bound",
                            "upper_bound",
                        ],
                    )

                    outlier_table = outlier_table.sort_values(
                        "outlier_percent",
                        ascending=False,
                    ).reset_index(drop=True)

                    st.markdown("#### IQR outlier rate by numeric column")

                    st.dataframe(
                        outlier_table,
                        use_container_width=True,
                        hide_index=True,
                    )

                    st.markdown("#### Outlier rate comparison")

                    st.bar_chart(
                        outlier_table.set_index("column")[
                            ["outlier_percent"]
                        ],
                        horizontal=True,
                        use_container_width=True,
                    )

                    csv_data = outlier_table.to_csv(
                        index=False
                    ).encode("utf-8")

                    st.download_button(
                        "Download outlier report",
                        data=csv_data,
                        file_name="datalify_outlier_report.csv",
                        mime="text/csv",
                        use_container_width=False,
                    )



        elif page == "Visualization Studio":

            # =============================================
            # VISUALIZATION STUDIO
            # =============================================
            st.markdown("## Interactive Data Visualization")

            st.write(
                "Build charts from your dataset, filter records, "
                "explore patterns, and download the data you're viewing."
            )

            # Always work on a copy. Do not modify working_df.
            source_df = st.session_state.working_df.copy(deep=True)

            if source_df.empty or len(source_df.columns) == 0:
                st.warning("The dataset has no data to visualize.")

            else:



                # =========================================
                # COLLAPSIBLE MULTIPLE FILTERS
                # =========================================
                source_df = st.session_state.working_df.copy(deep=True)
                filtered_df = source_df.copy(deep=True)

                available_columns = source_df.columns.tolist()

                if "viz_filter_count" not in st.session_state:
                    st.session_state.viz_filter_count = 1

                filter_count = st.session_state.viz_filter_count

                with st.expander(
                    f" Data filters ({filter_count} configured)",
                    expanded=False,
                ):
                    st.caption(
                        "Add multiple filters to narrow your data. "
                        "All active filters are applied together."
                    )

                    add_col, remove_col, reset_col = st.columns(3)

                    with add_col:
                        if st.button(
                            "＋ Add filter",
                            use_container_width=True,
                            key="viz_add_filter",
                        ):
                            st.session_state.viz_filter_count += 1
                            st.rerun()

                    with remove_col:
                        if st.button(
                            "− Remove filter",
                            disabled=filter_count == 0,
                            use_container_width=True,
                            key="viz_remove_filter",
                        ):
                            last_index = filter_count - 1

                            for suffix in (
                                "column",
                                "range",
                                "values",
                            ):
                                st.session_state.pop(
                                    f"viz_filter_{suffix}_{last_index}",
                                    None,
                                )

                            st.session_state.viz_filter_count -= 1
                            st.rerun()

                    with reset_col:
                        if st.button(
                            "Reset filters",
                            use_container_width=True,
                            key="viz_reset_filters",
                        ):
                            for key in list(st.session_state.keys()):
                                if key.startswith("viz_filter_"):
                                    del st.session_state[key]

                            st.session_state.viz_filter_count = 1
                            st.rerun()

                    for filter_index in range(filter_count):
                        st.markdown(f"**Filter {filter_index + 1}**")

                        filter_col1, filter_col2 = st.columns(2)

                        with filter_col1:
                            selected_column = st.selectbox(
                                "Column",
                                available_columns,
                                key=f"viz_filter_column_{filter_index}",
                            )

                        series = source_df[selected_column]

                        with filter_col2:
                            if pd.api.types.is_numeric_dtype(series):
                                numeric_values = series.dropna()

                                if numeric_values.empty:
                                    st.caption(
                                        "No numeric values available."
                                    )
                                else:
                                    minimum = float(numeric_values.min())
                                    maximum = float(numeric_values.max())

                                    if minimum < maximum:
                                        selected_range = st.slider(
                                            "Value range",
                                            min_value=minimum,
                                            max_value=maximum,
                                            value=(minimum, maximum),
                                            key=f"viz_filter_range_{filter_index}",
                                        )

                                        filtered_df = filtered_df[
                                            filtered_df[selected_column].between(
                                                selected_range[0],
                                                selected_range[1],
                                            )
                                            | filtered_df[selected_column].isna()
                                        ]
                                    else:
                                        st.caption(
                                            "Only one distinct numeric value."
                                        )
                            else:
                                available_values = sorted(
                                    series.dropna().unique().tolist(),
                                    key=lambda value: str(value),
                                )

                                selected_values = st.multiselect(
                                    "Values to keep",
                                    options=available_values,
                                    default=available_values,
                                    format_func=lambda value: str(value),
                                    key=f"viz_filter_values_{filter_index}",
                                )

                                filtered_df = filtered_df[
                                    filtered_df[selected_column].isin(
                                        selected_values
                                    )
                                    | filtered_df[selected_column].isna()
                                ]

                # =========================================
                # FILTER SUMMARY (ALWAYS VISIBLE)
                # =========================================
                total_rows = len(source_df)
                visible_rows = len(filtered_df)
                excluded_rows = total_rows - visible_rows

                metric1, metric2, metric3 = st.columns(3)

                metric1.metric("Original rows", f"{total_rows:,}")
                metric2.metric("Filtered rows", f"{visible_rows:,}")
                metric3.metric("Excluded rows", f"{excluded_rows:,}")

                if filtered_df.empty:
                    st.warning(
                        "No rows match all selected filters. "
                        "Expand Data filters and adjust your selections."
                    )


                    # =====================================
                    # CHART CONFIGURATION
                    # =====================================
                    st.markdown("### 2. Configure your chart")

                    numeric_columns = filtered_df.select_dtypes(
                        include="number"
                    ).columns.tolist()

                    all_columns = filtered_df.columns.tolist()

                    chart_options = [
                        "Bar",
                        "Line",
                        "Area",
                        "Scatter",
                        "Histogram",
                        "Box",
                        "Pie",
                    ]

                    config1, config2, config3 = st.columns(3)

                    with config1:
                        chart_type = st.selectbox(
                            "Chart type",
                            chart_options,
                            key="viz_chart_type",
                        )

                    with config2:
                        if chart_type == "Histogram":
                            x_options = numeric_columns or all_columns
                        elif chart_type == "Scatter":
                            x_options = numeric_columns or all_columns
                        else:
                            x_options = all_columns

                        x_column = st.selectbox(
                            "X-axis / Category",
                            x_options,
                            key="viz_x_column",
                        )

                    with config3:
                        if chart_type in [
                            "Scatter",
                            "Histogram",
                            "Box",
                        ]:
                            y_options = numeric_columns
                        else:
                            y_options = numeric_columns

                        if y_options:
                            y_column = st.selectbox(
                                "Y-axis / Numeric value",
                                y_options,
                                key="viz_y_column",
                            )
                        else:
                            y_column = None
                            st.info(
                                "No numeric columns detected. "
                                "A numeric measure is needed for this chart."
                            )

                    config4, config5 = st.columns(2)

                    with config4:
                        if chart_type in [
                            "Bar",
                            "Line",
                            "Area",
                        ] and y_column is not None:
                            aggregation = st.selectbox(
                                "Aggregation",
                                [
                                    "Sum",
                                    "Mean",
                                    "Median",
                                    "Count",
                                ],
                                key="viz_aggregation",
                            )
                        else:
                            aggregation = "Sum"

                    with config5:
                        if chart_type in [
                            "Bar",
                            "Line",
                            "Area",
                            "Scatter",
                            "Box",
                        ]:
                            color_options = [
                                "No grouping"
                            ] + all_columns

                            color_column = st.selectbox(
                                "Color / Group by",
                                color_options,
                                key="viz_color_column",
                            )

                            if color_column == "No grouping":
                                color_column = None
                        else:
                            color_column = None

                    # =====================================
                    # BUILD CHART
                    # =====================================
                    st.divider()
                    st.markdown("### 3. Visualization")

                    if chart_type == "Histogram":
                        if not pd.api.types.is_numeric_dtype(
                            filtered_df[x_column]
                        ):
                            st.warning(
                                "Select a numeric column for a histogram."
                            )
                        else:
                            fig = px.histogram(
                                filtered_df,
                                x=x_column,
                                color=color_column,
                                title=f"Distribution of {x_column}",
                                labels={x_column: x_column},
                            )

                            st.plotly_chart(
                                fig,
                                use_container_width=True,
                            )

                    elif chart_type == "Scatter":
                        if y_column is None:
                            st.warning(
                                "A numeric Y-axis column is required."
                            )
                        elif not pd.api.types.is_numeric_dtype(
                            filtered_df[x_column]
                        ):
                            st.warning(
                                "Select a numeric X-axis column "
                                "for a scatter plot."
                            )
                        elif not pd.api.types.is_numeric_dtype(
                            filtered_df[y_column]
                        ):
                            st.warning(
                                "Select a numeric Y-axis column."
                            )
                        else:
                            scatter_df = filtered_df.dropna(
                                subset=[x_column, y_column]
                            )

                            if len(scatter_df) > 10000:
                                st.caption(
                                    "Showing a sample of 10,000 records "
                                    "to keep the scatter plot responsive."
                                )
                                scatter_df = scatter_df.sample(
                                    n=10000,
                                    random_state=42,
                                )

                            fig = px.scatter(
                                scatter_df,
                                x=x_column,
                                y=y_column,
                                color=color_column,
                                title=f"{y_column} vs {x_column}",
                            )

                            st.plotly_chart(
                                fig,
                                use_container_width=True,
                            )

                    elif chart_type == "Box":
                        if y_column is None:
                            st.warning(
                                "A numeric column is required for a box plot."
                            )
                        else:
                            fig = px.box(
                                filtered_df,
                                x=(
                                    x_column
                                    if x_column != y_column
                                    else None
                                ),
                                y=y_column,
                                color=color_column,
                                title=f"Distribution of {y_column}",
                                points="outliers",
                            )

                            st.plotly_chart(
                                fig,
                                use_container_width=True,
                            )

                    elif chart_type == "Pie":
                        if y_column is None:
                            st.warning(
                                "A numeric column is required for a pie chart."
                            )
                        else:
                            pie_data = (
                                filtered_df
                                .groupby(
                                    x_column,
                                    dropna=False,
                                )[y_column]
                                .sum()
                                .reset_index()
                            )

                            pie_data[x_column] = (
                                pie_data[x_column]
                                .fillna("(Missing)")
                                .astype(str)
                            )

                            pie_data = pie_data[
                                pie_data[y_column] >= 0
                            ]

                            if pie_data.empty:
                                st.warning(
                                    "No non-negative values are available "
                                    "to create a pie chart."
                                )
                            else:
                                fig = px.pie(
                                    pie_data,
                                    names=x_column,
                                    values=y_column,
                                    title=f"{y_column} by {x_column}",
                                )

                                st.plotly_chart(
                                    fig,
                                    use_container_width=True,
                                )

                    elif chart_type in ["Bar", "Line", "Area"]:
                        if y_column is None:
                            st.warning(
                                "A numeric column is required for this chart."
                            )
                        else:
                            group_columns = [x_column]

                            if (
                                color_column
                                and color_column != x_column
                            ):
                                group_columns.append(color_column)

                            if aggregation == "Sum":
                                chart_data = (
                                    filtered_df
                                    .groupby(
                                        group_columns,
                                        dropna=False,
                                    )[y_column]
                                    .sum()
                                    .reset_index()
                                )

                            elif aggregation == "Mean":
                                chart_data = (
                                    filtered_df
                                    .groupby(
                                        group_columns,
                                        dropna=False,
                                    )[y_column]
                                    .mean()
                                    .reset_index()
                                )

                            elif aggregation == "Median":
                                chart_data = (
                                    filtered_df
                                    .groupby(
                                        group_columns,
                                        dropna=False,
                                    )[y_column]
                                    .median()
                                    .reset_index()
                                )

                            else:
                                chart_data = (
                                    filtered_df
                                    .groupby(
                                        group_columns,
                                        dropna=False,
                                    )[y_column]
                                    .count()
                                    .reset_index()
                                )

                            chart_data[x_column] = (
                                chart_data[x_column]
                                .fillna("(Missing)")
                                .astype(str)
                            )

                            if (
                                color_column
                                and color_column != x_column
                            ):
                                chart_data[color_column] = (
                                    chart_data[color_column]
                                    .fillna("(Missing)")
                                    .astype(str)
                                )

                            color_arg = (
                                color_column
                                if color_column != x_column
                                else None
                            )

                            chart_title = (
                                f"{aggregation} of {y_column} "
                                f"by {x_column}"
                            )

                            if chart_type == "Bar":
                                fig = px.bar(
                                    chart_data,
                                    x=x_column,
                                    y=y_column,
                                    color=color_arg,
                                    barmode="group",
                                    title=chart_title,
                                )

                            elif chart_type == "Line":
                                fig = px.line(
                                    chart_data,
                                    x=x_column,
                                    y=y_column,
                                    color=color_arg,
                                    markers=True,
                                    title=chart_title,
                                )

                            else:
                                fig = px.area(
                                    chart_data,
                                    x=x_column,
                                    y=y_column,
                                    color=color_arg,
                                    title=chart_title,
                                )

                            st.plotly_chart(
                                fig,
                                use_container_width=True,
                            )

                    # =====================================
                    # CHART DATA AND EXPORTS
                    # =====================================
                    st.divider()

                    with st.expander("View filtered data"):
                        st.dataframe(
                            filtered_df.head(1000),
                            use_container_width=True,
                            hide_index=True,
                        )

                        st.caption(
                            "Showing up to 1,000 rows in this preview."
                        )

                    csv_data = filtered_df.to_csv(
                        index=False
                    ).encode("utf-8")

                    st.download_button(
                        "Download filtered data (CSV)",
                        data=csv_data,
                        file_name="datalify_filtered_data.csv",
                        mime="text/csv",
                        key="viz_download_filtered_data",
                    )

                    st.caption(
                        "Charts use the filtered dataset. "
                        "Filtering here does not modify your working dataset."
                    )


        elif page == "AI Analyst":

            st.markdown("### Analyze your data")
            st.info(
                "Next: executive summaries, data-quality audits, "
                "business opportunities, and risk reviews."
            )

        elif page == "Export Center":

            st.markdown("### Export your work")
            st.info(
                "Next: downloadable cleaned datasets and "
                "structured analyst reports."
            )

# =========================================================
# FOOTER
# =========================================================
st.divider()
st.caption("Datalify · InsightProvider")