"""Datalify's local-first dataset overview and automatic data signals."""

from html import escape

import pandas as pd
import plotly.express as px
import streamlit as st

from src.data_utils import get_dataset_summary


def _set_page(page: str) -> None:
    st.session_state.main_navigation = page
    st.rerun()


def _overview_hero(title: str, copy: str, eyebrow: str = "DATA WORKSPACE") -> None:
    st.markdown(
        f"""
        <section class="overview-hero">
          <div class="overview-eyebrow">{escape(eyebrow)}</div>
          <div class="overview-title">{escape(title)}</div>
          <p class="overview-copy">{escape(copy)}</p>
        </section>
        """,
        unsafe_allow_html=True,
    )


def _insight_card(label: str, value: str, copy: str) -> None:
    st.markdown(
        f"""
        <div class="insight-card">
          <div class="insight-card-label">{escape(label)}</div>
          <div class="insight-card-value">{escape(value)}</div>
          <div class="insight-card-copy">{escape(copy)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _strongest_correlation(df: pd.DataFrame) -> tuple[str, str, float] | None:
    numeric = df.select_dtypes(include="number")
    if numeric.shape[1] < 2:
        return None

    corr = numeric.corr(min_periods=2)
    pairs: list[tuple[str, str, float]] = []
    for index, left in enumerate(corr.columns):
        for right in corr.columns[index + 1:]:
            value = corr.loc[left, right]
            if pd.notna(value):
                pairs.append((str(left), str(right), float(value)))
    return max(pairs, key=lambda pair: abs(pair[2])) if pairs else None


def _outlier_profile(df: pd.DataFrame) -> pd.DataFrame:
    records = []
    for column in df.select_dtypes(include="number").columns:
        values = df[column].dropna()
        if len(values) < 4:
            continue
        q1, q3 = values.quantile([0.25, 0.75])
        spread = q3 - q1
        if not spread or pd.isna(spread):
            continue
        flags = (values < q1 - 1.5 * spread) | (values > q3 + 1.5 * spread)
        count = int(flags.sum())
        if count:
            records.append({
                "Column": str(column),
                "Flagged values": count,
                "Share of valid values": round(count / len(values) * 100, 2),
            })
    return pd.DataFrame(records).sort_values(
        "Share of valid values", ascending=False
    ).reset_index(drop=True) if records else pd.DataFrame(
        columns=["Column", "Flagged values", "Share of valid values"]
    )


def render_overview() -> None:
    """Show a compact, evidence-based summary of the active dataset."""
    df = st.session_state.get("working_df")
    if df is None:
        _overview_hero(
            "Make your data easier to understand.",
            "Bring a spreadsheet into Datalify to inspect quality, uncover useful patterns, and prepare a clean dataset for analysis.",
            "WELCOME TO DATALIFY",
        )
        st.markdown("### Start with a dataset")
        st.write("Your analysis stays in this workspace. Upload a CSV or Excel file to begin.")
        if st.button("Open Data Intake", type="primary", icon=":material/upload_file:", key="overview_open_intake"):
            _set_page("Data Intake")

        st.markdown("#### Your analysis workflow")
        cards = st.columns(3)
        with cards[0]:
            _insight_card("01 · Understand", "Profile your data", "Review columns, coverage, distributions, and data quality.")
        with cards[1]:
            _insight_card("02 · Prepare", "Make it analysis-ready", "Clean missing values, reshape tables, and combine files.")
        with cards[2]:
            _insight_card("03 · Explore", "Turn signals into decisions", "Build charts, create an AI Brief, and export your findings.")
        return

    source_name = st.session_state.get("dataset_name") or "Active dataset"
    summary = get_dataset_summary(df)
    type_counts = df.dtypes.astype(str).value_counts()
    numeric_count = int(len(df.select_dtypes(include="number").columns))
    text_count = int(len(df.select_dtypes(include=["object", "string", "category"]).columns))
    missing_by_column = df.isna().sum()
    missing_by_column = missing_by_column[missing_by_column > 0].sort_values(ascending=False).head(8)
    outliers = _outlier_profile(df)
    strongest = _strongest_correlation(df)

    _overview_hero(
        "Your data, at a glance.",
        f"{source_name} · {summary['rows']:,} rows · {summary['columns']:,} columns. Explore quality signals and decide what to do next.",
    )

    metrics = st.columns(4)
    metrics[0].metric("Records", f"{summary['rows']:,}")
    metrics[1].metric("Fields", f"{summary['columns']:,}")
    metrics[2].metric("Completeness", f"{summary['completeness']:.1f}%", help="Share of dataset cells that are not missing.")
    metrics[3].metric("Duplicate rows", f"{summary['duplicate_rows']:,}")

    st.markdown("<div class='section-kicker'>Automatic data signals · calculated locally</div>", unsafe_allow_html=True)
    left, right = st.columns([1.15, 1], gap="large")

    with left:
        st.markdown("### Quality watchlist")
        if missing_by_column.empty and summary["duplicate_rows"] == 0:
            st.success("No missing cells or exact duplicate rows were found.")
        else:
            if summary["duplicate_rows"]:
                st.warning(f"{summary['duplicate_rows']:,} exact duplicate rows are present.")
            if not missing_by_column.empty:
                missing_table = pd.DataFrame({
                    "Column": [str(name) for name in missing_by_column.index],
                    "Missing values": missing_by_column.astype(int).values,
                    "Missing share": [
                        f"{(count / max(len(df), 1) * 100):.1f}%"
                        for count in missing_by_column.values
                    ],
                })
                st.dataframe(missing_table, width="stretch", hide_index=True)
        if not outliers.empty:
            st.caption("Potential outliers use the 1.5×IQR rule; review them before deciding whether to change the data.")
            st.dataframe(outliers.head(5), width="stretch", hide_index=True)
        elif numeric_count:
            st.caption("No potential outliers were flagged by the 1.5×IQR scan.")

    with right:
        st.markdown("### Dataset profile")
        _insight_card("FIELD MIX", f"{numeric_count} numeric · {text_count} text", f"{len(df.columns) - numeric_count - text_count} other fields · {len(type_counts)} detected data types")
        st.markdown("<div style='height:.65rem'></div>", unsafe_allow_html=True)
        if strongest:
            relation = "positive" if strongest[2] > 0 else "negative"
            _insight_card("STRONGEST NUMERIC RELATIONSHIP", f"{strongest[0]} and {strongest[1]}", f"Pearson r = {strongest[2]:+.2f} · {relation} association, not evidence of causation.")
        else:
            _insight_card("NUMERIC RELATIONSHIPS", "More data needed", "At least two varying numeric fields are needed to calculate a correlation.")
        st.markdown("<div style='height:.65rem'></div>", unsafe_allow_html=True)
        _insight_card("DATA READINESS", f"{summary['completeness']:.1f}% complete", "Completeness reports missing cells only. It does not judge whether values are accurate or appropriate.")

    st.markdown("### Explore a field")
    if not len(df.columns):
        st.info("This dataset has no columns to chart yet.")
    else:
        selected = st.selectbox("Choose a field for a quick distribution", df.columns.tolist(), key="overview_distribution_field")
        series = df[selected]
        if pd.api.types.is_numeric_dtype(series):
            values = pd.to_numeric(series, errors="coerce").dropna()
            if values.empty:
                st.info("This field has no valid numeric values to chart.")
            else:
                fig = px.histogram(values, x=values, nbins=30, title=f"Distribution of {selected}", labels={"x": str(selected), "count": "Records"})
                fig.update_layout(template="plotly_white", height=360, margin=dict(l=20, r=20, t=55, b=20), font=dict(family="Inter, Segoe UI, sans-serif", color="#52617A"), title_font_color="#17243B", showlegend=False)
                st.plotly_chart(fig, width="stretch", config={"displaylogo": False})
        else:
            counts = series.fillna("(Missing)").astype(str).value_counts().head(15).rename_axis("Value").reset_index(name="Records")
            fig = px.bar(counts, x="Records", y="Value", orientation="h", title=f"Most common values in {selected}", color_discrete_sequence=["#356AE6"])
            fig.update_layout(template="plotly_white", height=max(300, min(520, 28 * len(counts) + 100)), margin=dict(l=20, r=20, t=55, b=20), font=dict(family="Inter, Segoe UI, sans-serif", color="#52617A"), title_font_color="#17243B", yaxis={"categoryorder": "total ascending"}, showlegend=False)
            st.plotly_chart(fig, width="stretch", config={"displaylogo": False})

    st.markdown("### Recommended next steps")
    actions = st.columns(3)
    for column, label, page, detail, icon in [
        (actions[0], "Review quality", "Quality Lab", "Inspect missing values, relationships, and outliers.", ":material/health_and_safety:"),
        (actions[1], "Prepare data", "Prepare", "Clean fields, reshape records, and combine datasets.", ":material/tune:"),
        (actions[2], "Build a chart", "Visualization Studio", "Filter records and create an interactive visualization.", ":material/monitoring:"),
    ]:
        with column:
            _insight_card("CONTINUE WORK", label, detail)
            if st.button(label, icon=icon, width="stretch", key=f"overview_go_{page}"):
                _set_page(page)
