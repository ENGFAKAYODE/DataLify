"""Download cleaned Datalify datasets and analysis summaries."""

from io import BytesIO
import base64
import json

import pandas as pd
import streamlit as st

from src.data_utils import get_dataset_summary


def _excel_bytes(df: pd.DataFrame) -> bytes:
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Datalify data")
    return buffer.getvalue()


def _python_export(original_df: pd.DataFrame, current_df: pd.DataFrame, recipe: list, visualizations: list) -> bytes:
    """Build a runnable script that replays recorded steps and saved charts."""
    baseline = next((item.get("python_baseline_csv") for item in recipe if item.get("python_baseline_csv")), None)
    all_steps_replayable = all(item.get("python_code") for item in recipe)
    original_payload = base64.b64encode(original_df.to_csv(index=False).encode("utf-8")).decode("ascii")
    if baseline:
        start_payload = baseline
        replay_steps = recipe
        data_note = "Starting from the dataset state before the first replayable step."
    elif all_steps_replayable:
        start_payload = original_payload
        replay_steps = recipe
        data_note = "Starting from the original uploaded dataset."
    elif recipe:
        start_payload = base64.b64encode(current_df.to_csv(index=False).encode("utf-8")).decode("ascii")
        replay_steps = []
        data_note = "Earlier transformations have no executable record; this is the current data snapshot."
    else:
        start_payload = original_payload
        replay_steps = []
        data_note = "No transformations were recorded; starting from the original uploaded dataset."
    chart_payload = [
        {"title": item.get("title", f"Visualization {index + 1}"),
         "figure_json": item.get("figure_json")}
        for index, item in enumerate(visualizations)
        if item.get("figure_json")
    ]
    charts_json = json.dumps(chart_payload, ensure_ascii=False, default=str)
    steps = [
        {"description": item.get("description", "Transformation"), "python_code": item.get("python_code")}
        for item in replay_steps
    ]
    steps_json = json.dumps(steps, ensure_ascii=False, default=str)
    script = f'''"""Datalify export: replay transformations and saved visualizations.

Requirements: pandas and plotly (pip install pandas plotly)
{data_note}
"""

import base64
import io
import json

import pandas as pd
import plotly.io as pio

ORIGINAL_CSV_BASE64 = {original_payload!r}
START_CSV_BASE64 = {start_payload!r}
TRANSFORMATION_STEPS = json.loads({steps_json!r})
SAVED_CHARTS = json.loads({charts_json!r})

original_df = pd.read_csv(io.BytesIO(base64.b64decode(ORIGINAL_CSV_BASE64)))
df = pd.read_csv(io.BytesIO(base64.b64decode(START_CSV_BASE64)))

for index, step in enumerate(TRANSFORMATION_STEPS, start=1):
    print(f"{{index}}. {{step['description']}}")
    if not step.get("python_code"):
        print("   Skipped: this step predates executable transformation capture.")
        continue
    scope = {{"pd": pd, "df": df, "original_df": original_df}}
    exec(step["python_code"], scope)
    df = scope["df"]

for chart in SAVED_CHARTS:
    figure = pio.from_json(chart["figure_json"])
    figure.update_layout(title=chart["title"])
    figure.show()
'''
    return script.encode("utf-8")


def render_export_center() -> None:
    """Render downloadable dataset, recipe, and analyst report exports."""
    df = st.session_state.working_df
    if df is None:
        st.info("Upload a dataset in Data Intake before exporting.")
        return

    dataset_name = st.session_state.get("dataset_name") or "dataset.csv"
    base_name = dataset_name.rsplit(".", 1)[0]
    summary = get_dataset_summary(df)
    original = st.session_state.get("original_df")
    recipe = st.session_state.get("prepare_recipe", [])
    visualizations = st.session_state.get("viz_export_items", [])
    analysis = st.session_state.get("ai_analysis")

    st.markdown("## Export Center")
    st.write("Download the current Datalify working dataset and its supporting records.")

    metrics = st.columns(4)
    metrics[0].metric("Rows", f"{summary['rows']:,}")
    metrics[1].metric("Columns", f"{summary['columns']:,}")
    metrics[2].metric("Missing cells", f"{summary['missing_values']:,}")
    metrics[3].metric(
        "Completeness", f"{summary['completeness']:.1f}%",
        help="Share of dataset cells that are not missing.",
    )

    st.markdown("### Working dataset")
    st.caption("Exports use the current working copy, including changes from Prepare or Quality Lab.")
    csv_col, excel_col = st.columns(2)
    csv_col.download_button(
        "Download as CSV",
        data=df.to_csv(index=False).encode("utf-8-sig"),
        file_name=f"{base_name}_datalify.csv",
        mime="text/csv",
        width="stretch",
        key="export_working_csv",
    )
    excel_col.download_button(
        "Download as Excel",
        data=_excel_bytes(df),
        file_name=f"{base_name}_datalify.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        width="stretch",
        key="export_working_xlsx",
    )

    if original is not None:
        with st.expander("Original upload"):
            st.caption("This is the untouched dataset from Data Intake.")
            st.download_button(
                "Download original as CSV",
                data=original.to_csv(index=False).encode("utf-8-sig"),
                file_name=f"{base_name}_original.csv",
                mime="text/csv",
                key="export_original_csv",
            )

    st.markdown("### Transformation recipe")
    recipe_data = {
        "product": "Datalify",
        "source_dataset": dataset_name,
        "working_rows": summary["rows"],
        "working_columns": summary["columns"],
        "transformations": recipe,
        "business_kpis": st.session_state.get("business_kpis", []),
    }
    st.download_button(
        "Download recipe (JSON)",
        data=json.dumps(recipe_data, indent=2, ensure_ascii=False, default=str),
        file_name=f"{base_name}_datalify_recipe.json",
        mime="application/json",
        key="export_recipe_json",
    )
    st.download_button(
        "Download Python script (.py)",
        data=_python_export(original if original is not None else df, df, recipe, visualizations),
        file_name=f"{base_name}_datalify_export.py",
        mime="text/x-python",
        key="export_python_script",
    )
    missing_code_steps = sum(not item.get("python_code") for item in recipe)
    if missing_code_steps:
        st.caption(
            f"{missing_code_steps} earlier transformation(s) have descriptions only and cannot be replayed. "
            "New transformations save executable steps for this export."
        )
    if not recipe:
        st.caption("No Prepare transformations have been recorded for this dataset yet.")

    st.markdown("### Dataset report")
    report_lines = [
        "# Datalify Dataset Report",
        "",
        f"**Source:** {dataset_name}",
        f"**Working size:** {summary['rows']:,} rows × {summary['columns']:,} columns",
        f"**Completeness:** {summary['completeness']:.2f}%",
        f"**Missing cells:** {summary['missing_values']:,}",
        f"**Duplicate rows:** {summary['duplicate_rows']:,}",
        "",
        "## Transformations",
    ]
    report_lines.extend(
        [f"- {item.get('description', 'Transformation')} ({item.get('timestamp', 'time not recorded')})" for item in recipe]
        or ["- No Prepare transformations recorded."]
    )
    if analysis:
        report_lines.extend([
            "",
            "## AI Analyst",
            f"**Question:** {analysis.get('question', '')}",
            f"**Model:** {analysis.get('model', '')}",
            "",
            analysis.get("answer", ""),
        ])
    else:
        report_lines.extend(["", "## AI Analyst", "No AI analysis has been generated for this session."])

    st.download_button(
        "Download dataset report (Markdown)",
        data="\n".join(report_lines).encode("utf-8"),
        file_name=f"{base_name}_datalify_report.md",
        mime="text/markdown",
        key="export_report_markdown",
    )
