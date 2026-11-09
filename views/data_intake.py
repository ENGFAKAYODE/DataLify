from html import escape

import streamlit as st
import pandas as pd
import plotly.express as px

from src.data_utils import get_dataset_summary, get_schema
from src.palette import DATALIFY_COLORS


def get_field_types(df):
    """Classify columns into numeric, date, text, and other."""
    numeric = df.select_dtypes(include="number").columns.tolist()

    dates = [
        col for col in df.columns
        if pd.api.types.is_datetime64_any_dtype(df[col])
    ]

    text = [
        col for col in df.select_dtypes(
            include=["object", "string", "category"]
        ).columns
        if col not in dates
    ]

    other = [
        col for col in df.columns
        if col not in numeric + dates + text
    ]

    return {
        "Numeric": numeric,
        "Date": dates,
        "Text": text,
        "Other": other,
    }


def render_pulse_card(label, value, detail):
    st.markdown(
        f"""<div class="pulse-card">
          <div class="pulse-label">{escape(str(label))}</div>
          <div class="pulse-value">{escape(str(value))}</div>
          <div class="pulse-detail">{escape(str(detail))}</div>
        </div>""",
        unsafe_allow_html=True,
    )


def render_data_intake(import_dataset):

    # =========================================
    # HERO / BRANDING
    # =========================================

    st.markdown(
        "<div style='height: 40px;'></div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div style="
            color: #64748B;
            font-size: 1.76rem;
            font-weight: 750;
            letter-spacing: 2px;
            margin-bottom: 0.8rem;
        ">DATALIFY</div>

        <div style="
            color: #64748B;
            font-size: 0.76rem;
            font-weight: 750;
            letter-spacing: 2px;
            margin-bottom: 0.8rem;
        ">AI-ASSISTED BUSINESS INTELLIGENCE</div>

        <div style="
            font-size: clamp(2.2rem, 4vw, 3.5rem);
            font-weight: 800;
            line-height: 1.12;
            letter-spacing: -1.8px;
            background: linear-gradient(
                100deg, #173B78 0%, #3978D8 50%, #7B61D1 100%
            );
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 1rem;
        ">From raw spreadsheet to clear decisions.</div>

        <div style="
            color: #64748B;
            font-size: 1.02rem;
            line-height: 1.8;
            max-width: 850px;
            margin-bottom: 1.8rem;
        ">
            Upload a dataset and explore its shape, quality,
            relationships, and business signals in minutes-then
            turn the evidence into an executive-ready brief.
        </div>
        """,
        unsafe_allow_html=True,
    )

    # =========================================
    # DATA UPLOAD
    # =========================================

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

    # =========================================
    # BEFORE UPLOAD
    # =========================================

    if st.session_state.working_df is None:

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("#### Data quality")
            st.write(
                "Identify missing values, duplicates, "
                "and potential data problems."
            )

        with col2:
            st.markdown("#### Explore patterns")
            st.write(
                "Explore distributions, relationships, "
                "and trends."
            )

        with col3:
            st.markdown("#### Business insights")
            st.write(
                "Translate evidence into useful findings "
                "and next actions."
            )

        return

    # =========================================
    # LOADED DATASET
    # =========================================

    df = st.session_state.working_df
    summary = get_dataset_summary(df)

    st.markdown(
        f"""
        <div style="
            font-size: 1.7rem;
            font-weight: 500;
            color: #64748B;
            margin: 1.5rem 0 1rem 0;
        ">
            Loaded:
            <strong style="color: #172B4D;">
                {st.session_state.dataset_name}
            </strong>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Rows", f"{summary['rows']:,}")
    c2.metric("Columns", f"{summary['columns']:,}")
    c3.metric(
        "Completeness", f"{summary['completeness']:.1f}%",
        help="Share of dataset cells that are not missing.",
    )
    c4.metric(
        "Memory usage",
        f"{summary['memory_bytes'] / 1024:.1f} KB",
    )

    # =========================================
    # DATASET PULSE
    # =========================================

    st.divider()

    st.markdown("### Dataset pulse")
    st.markdown("#### What stands out in this dataset")
    st.caption(
        "A fast structural read before deeper exploration."
    )

    field_types = get_field_types(df)

    cardinality = {col: int(df[col].nunique(dropna=True)) for col in df.columns}
    highest_field = max(cardinality, key=cardinality.get) if cardinality else "N/A"
    highest_count = cardinality.get(highest_field, 0)
    total_cells = len(df) * len(df.columns)
    missing_count = int(df.isna().sum().sum())
    missing_percent = missing_count / total_cells * 100 if total_cells else 0.0
    duplicate_count = int(df.duplicated().sum())
    duplicate_percent = duplicate_count / max(len(df), 1) * 100

    numeric_df = df.select_dtypes(include="number")
    strongest_pair = None
    if numeric_df.shape[1] >= 2:
        correlation = numeric_df.corr(min_periods=2)
        pairs = []
        for index, left in enumerate(correlation.columns):
            for right in correlation.columns[index + 1:]:
                value = correlation.loc[left, right]
                if pd.notna(value):
                    pairs.append((str(left), str(right), float(value)))
        if pairs:
            strongest_pair = max(pairs, key=lambda pair: abs(pair[2]))

    pulse_cards = st.columns(4, gap="medium")
    with pulse_cards[0]:
        if missing_count and df.shape[1]:
            missing_by_field = df.isna().sum().sort_values(ascending=False)
            highest_missing_field = missing_by_field.index[0]
            field_missing_percent = missing_by_field.iloc[0] / max(len(df), 1) * 100
            render_pulse_card("Most missing values", str(highest_missing_field), f"{field_missing_percent:.1f}% missing · {int(missing_by_field.iloc[0]):,} cells")
        else:
            render_pulse_card("Missing values", "None found", "Every dataset cell has a value.")
    with pulse_cards[1]:
        render_pulse_card("Duplicates", f"{duplicate_count:,}", f"additional rows · {duplicate_percent:.1f}% of records")
    with pulse_cards[2]:
        render_pulse_card("Most distinct values", str(highest_field), f"{highest_count:,} unique values")
    with pulse_cards[3]:
        if strongest_pair:
            relation = "positive" if strongest_pair[2] > 0 else "negative"
            render_pulse_card("Strongest numeric relationship", f"{strongest_pair[0]} ↔ {strongest_pair[1]}", f"Pearson r = {strongest_pair[2]:+.2f} · {relation}")
        else:
            render_pulse_card("Field mix", f"{len(field_types['Numeric'])} numeric", f"{len(field_types['Text'])} text · {len(field_types['Date'])} date · {len(field_types['Other'])} other")

    # =========================================
    # DISTRIBUTION + FIELD TYPE DONUT
    # =========================================

    st.divider()

    st.markdown("### Distribution")
    st.caption(
        "Select a field to explore its distribution and spread."
    )

    distribution_col, donut_col = st.columns(
        [1.8, 1],
        gap="large",
    )

    with distribution_col:

        selected_field = st.selectbox(
            "Distribution metric",
            options=df.columns.tolist(),
            key="intake_distribution_field",
        )

        selected_series = df[selected_field]
        is_numeric = pd.api.types.is_numeric_dtype(
            selected_series
        )

        if is_numeric:

            numeric_values = pd.to_numeric(
                selected_series,
                errors="coerce",
            ).dropna()

            if numeric_values.empty:
                st.info("No valid numeric observations in this field.")
            else:
                box_fig = px.box(
                    x=numeric_values,
                    y=[""] * len(numeric_values),
                    orientation="h",
                    points="outliers",
                    title=f"{selected_field} · Box plot",
                )

                box_fig.update_layout(
                    showlegend=False,
                    xaxis_title=selected_field,
                    yaxis_title="",
                    height=240,
                    margin=dict(l=20, r=20, t=55, b=35),
                )
                box_fig.update_yaxes(showticklabels=False, showgrid=False, zeroline=False)
                box_fig.update_traces(
                    fillcolor="rgba(40, 87, 167, 0.28)",
                    line={"color": "#2857A7", "width": 2},
                    marker={"color": "#C44955", "size": 6},
                )

                st.plotly_chart(
                    box_fig,
                    width="stretch",
                )

                hist_fig = px.histogram(
                    numeric_values,
                    x=numeric_values,
                    nbins=30,
                    title=f"{selected_field} · Distribution",
                    labels={"x": selected_field},
                )

                hist_fig.update_layout(
                    height=350,
                    xaxis_title=selected_field,
                    yaxis_title="Frequency",
                    showlegend=False,
                )

                st.plotly_chart(
                    hist_fig,
                    width="stretch",
                )

        else:

            category_counts = (
                selected_series
                .fillna("(Missing)")
                .astype(str)
                .value_counts()
                .head(20)
                .rename_axis(selected_field)
                .reset_index(name="Count")
            )

            category_fig = px.bar(
                category_counts,
                x="Count",
                y=selected_field,
                orientation="h",
                title=f"{selected_field} · Value distribution",
            )

            category_fig.update_layout(
                height=450,
                yaxis={"categoryorder": "total ascending"},
            )

            st.plotly_chart(
                category_fig,
                width="stretch",
            )

            st.caption(
                "Showing the 20 most frequent values."
            )

    with donut_col:

        st.markdown("##### FIELD COMPOSITION")

        composition = pd.DataFrame({
            "Field type": list(field_types.keys()),
            "Fields": [
                len(fields)
                for fields in field_types.values()
            ],
        })

        composition = composition[
            composition["Fields"] > 0
        ]

        if composition.empty:
            st.info("No fields are available.")
        else:
            donut_fig = px.pie(
                composition,
                names="Field type",
                values="Fields",
                hole=0.68,
                color_discrete_sequence=DATALIFY_COLORS,
            )

            donut_fig.update_traces(
                textposition="none",
                hovertemplate=(
                    "%{label}: %{value} fields"
                    "<extra></extra>"
                ),
            )

            donut_fig.update_layout(
                height=350,
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="top",
                    y=-0.08,
                    xanchor="center",
                    x=0.5,
                ),
                margin=dict(t=20, b=70, l=10, r=10),
                annotations=[{
                    "text": (
                        f"<b>{len(df.columns)}</b>"
                        "<br><sup>Fields</sup>"
                    ),
                    "showarrow": False,
                    "font": {"size": 22},
                }],
            )

            st.plotly_chart(
                donut_fig,
                width="stretch",
            )

    # =========================================
    # PREVIEW AND SCHEMA
    # =========================================

    st.divider()

    preview_tab, schema_tab = st.tabs(
        ["Preview Data", "Schema"],
        key="data_preview_tabs",
    )

    with preview_tab:
        st.dataframe(
            df.head(100),
            width="stretch",
            hide_index=True,
        )

    with schema_tab:
        st.dataframe(
            get_schema(df),
            width="stretch",
            hide_index=True,
        )
