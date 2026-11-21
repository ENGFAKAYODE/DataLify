"""Decision support tools for investigating a Datalify dataset."""

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.palette import DATALIFY_COLORS


def _numeric_fields(df: pd.DataFrame) -> list:
    return df.select_dtypes(include="number").columns.tolist()


def _render_segments(df: pd.DataFrame) -> None:
    st.markdown("### Build and compare segments")
    st.write(
        "Compare a decision measure across customer, product, or other groups. "
        "Use the table and share of total to see which segments drive the result."
    )
    numeric = _numeric_fields(df)
    categories = [column for column in df.columns if column not in numeric]
    if not numeric:
        st.info("Segment comparison needs at least one numeric measure.")
        return

    if categories:
        segment_field = st.selectbox("Segment by", categories, key="decision_segment_field")
    else:
        st.info("No descriptive fields found. Choose a numeric field to create value bands.")
        band_source = st.selectbox("Create bands from", numeric, key="decision_segment_band_field")
        segment_field = f"{band_source} band"
    measure = st.selectbox("Measure", numeric, key="decision_segment_measure")
    calculation = st.selectbox("Calculation", ["Sum", "Average", "Median", "Record count"], key="decision_segment_calculation")

    segment_data = df.copy()
    if categories:
        segment_data[segment_field] = segment_data[segment_field].fillna("(Missing)").astype(str)
    else:
        try:
            segment_data[segment_field] = pd.qcut(
                pd.to_numeric(segment_data[band_source], errors="coerce"),
                q=4, duplicates="drop", labels=False,
            ).map(lambda value: f"Band {int(value) + 1}" if pd.notna(value) else "(Missing)")
        except ValueError:
            st.info("This field does not have enough distinct values to create meaningful bands.")
            return

    segment_data[measure] = pd.to_numeric(segment_data[measure], errors="coerce")
    grouped = segment_data.groupby(segment_field, dropna=False)[measure]
    if calculation == "Sum":
        result = grouped.sum(min_count=1)
    elif calculation == "Average":
        result = grouped.mean()
    elif calculation == "Median":
        result = grouped.median()
    else:
        result = grouped.count()

    result = result.dropna().sort_values(ascending=False).head(30)
    if result.empty:
        st.info("No valid values are available for this segment comparison.")
        return
    output = result.rename("Value").reset_index()
    if calculation in ("Sum", "Record count"):
        total = output["Value"].sum()
        output["Share of displayed total (%)"] = (
            output["Value"] / total * 100 if total > 0 else np.nan
        ).round(1)
    chart = px.bar(
        output, x=segment_field, y="Value", color_discrete_sequence=DATALIFY_COLORS,
        title=f"{calculation} of {measure} by {segment_field}",
    )
    chart.update_layout(template="plotly_white", height=390, margin=dict(l=20, r=20, t=55, b=35), showlegend=False)
    st.plotly_chart(chart, width="stretch", config={"displaylogo": False})
    st.dataframe(output, width="stretch", hide_index=True)
    st.download_button(
        "Download segment comparison",
        output.to_csv(index=False).encode("utf-8-sig"),
        file_name="datalify_segment_comparison.csv", mime="text/csv",
        key="decision_segments_download",
    )


def _render_statistical_test(df: pd.DataFrame) -> None:
    st.markdown("### Confidence interval for an average")
    st.write(
        "Estimate a range for the population average and check whether it is "
        "consistent with a benchmark you want to test."
    )
    numeric = _numeric_fields(df)
    if not numeric:
        st.info("This analysis needs a numeric measure.")
        return

    with st.form("decision_mean_test_form"):
        question = st.text_input(
            "Question to test",
            placeholder="Example: Is average order value above $50?",
            key="decision_test_question",
        )
        measure = st.selectbox("Measure", numeric, key="decision_test_measure")
        confidence = st.selectbox("Confidence level", [90, 95, 99], index=1, format_func=lambda value: f"{value}%", key="decision_test_confidence")
        benchmark_text = st.text_input(
            "Benchmark average (optional)", placeholder="Enter the value in your question to compare against",
            key="decision_test_benchmark",
        )
        run = st.form_submit_button("Estimate average range", type="primary", icon=":material/query_stats:")

    if not run:
        st.caption("The interval uses bootstrap resampling. A clear question and a meaningful benchmark make the result easier to interpret.")
        return
    if not question.strip():
        st.error("Enter the question or assumption you want to test.")
        return
    values = pd.to_numeric(df[measure], errors="coerce").replace([np.inf, -np.inf], np.nan).dropna().to_numpy(dtype=float)
    if len(values) < 2:
        st.warning("At least two valid records are needed to estimate an interval for an average.")
        return
    benchmark = None
    if benchmark_text.strip():
        try:
            benchmark = float(benchmark_text.replace(",", "").strip())
        except ValueError:
            st.error("The benchmark must be a number, or left blank.")
            return

    sampled = values
    if len(sampled) > 5000:
        sampled = np.random.default_rng(42).choice(sampled, size=5000, replace=False)
    rng = np.random.default_rng(2026)
    bootstrap_means = np.empty(1200)
    for start in range(0, len(bootstrap_means), 100):
        count = min(100, len(bootstrap_means) - start)
        resamples = rng.choice(sampled, size=(count, len(sampled)), replace=True)
        bootstrap_means[start:start + count] = resamples.mean(axis=1)
    alpha = (100 - confidence) / 2
    lower, upper = np.percentile(bootstrap_means, [alpha, 100 - alpha])
    mean = float(sampled.mean())

    st.markdown(f"**Question:** {question.strip()}")
    metric_cols = st.columns(4)
    metric_cols[0].metric("Average", f"{mean:,.3f}")
    metric_cols[1].metric(f"{confidence}% lower bound", f"{lower:,.3f}")
    metric_cols[2].metric(f"{confidence}% upper bound", f"{upper:,.3f}")
    metric_cols[3].metric("Records used", f"{len(sampled):,}", help="For datasets above 5,000 valid values, a reproducible random sample is used for calculation.")
    if benchmark is not None:
        if lower <= benchmark <= upper:
            st.info(f"The benchmark ({benchmark:,.3f}) falls inside the estimated interval. The data do not clearly distinguish the average from this value at the selected confidence level.")
        else:
            st.success(f"The benchmark ({benchmark:,.3f}) falls outside the estimated interval. The observed average is inconsistent with that value at the selected confidence level.")
    st.caption(
        "Bootstrap interval assumes records are representative and independent. "
        "It does not establish cause and effect; review sampling, outliers, and domain context before acting."
    )


def _render_anomalies(df: pd.DataFrame) -> None:
    st.markdown("### Find unusual records")
    st.write(
        "Flag unusually low or high numeric values with the interquartile range rule. "
        "Review flagged records before treating them as errors or removing them."
    )
    numeric = _numeric_fields(df)
    if not numeric:
        st.info("Anomaly review needs a numeric field.")
        return
    measure = st.selectbox("Measure to inspect", numeric, key="decision_anomaly_measure")
    sensitivity = st.selectbox(
        "Detection sensitivity", [1.5, 3.0], format_func=lambda value: "Review (1.5 × IQR)" if value == 1.5 else "Extreme only (3 × IQR)",
        key="decision_anomaly_sensitivity",
    )
    values = pd.to_numeric(df[measure], errors="coerce")
    valid = values.dropna()
    if len(valid) < 4:
        st.info("At least four numeric records are recommended for an interquartile range review.")
        return
    q1, q3 = valid.quantile([.25, .75])
    spread = q3 - q1
    if spread == 0:
        st.info("This field has no interquartile spread, so the selected rule cannot identify unusual values.")
        return
    lower, upper = q1 - sensitivity * spread, q3 + sensitivity * spread
    mask = values.lt(lower) | values.gt(upper)
    if not mask.any():
        st.success("No records exceed the selected thresholds.")
        st.caption(f"Review range: {lower:,.3f} to {upper:,.3f}")
        return
    flagged = df.loc[mask].copy()
    output_names = ["Source row", "Observed value", "Review flag"]
    for position, base_name in enumerate(output_names):
        name = base_name
        suffix = 2
        while name in flagged.columns:
            name = f"{base_name} ({suffix})"
            suffix += 1
        output_names[position] = name
    flagged.insert(0, output_names[0], flagged.index.astype(str))
    flagged.insert(1, output_names[1], values.loc[mask].to_numpy())
    flagged.insert(2, output_names[2], np.where(values.loc[mask].to_numpy() < lower, "Below range", "Above range"))
    st.metric("Records flagged for review", f"{len(flagged):,}", delta=f"{len(flagged) / len(df) * 100:.1f}% of rows", delta_color="inverse")
    st.caption(f"Values outside {lower:,.3f} to {upper:,.3f} are flagged. This statistical rule is a review aid, not a judgment that a record is wrong.")
    st.dataframe(flagged.head(500), width="stretch", hide_index=True)
    st.download_button(
        "Download flagged records", flagged.to_csv(index=False).encode("utf-8-sig"),
        file_name="datalify_records_for_review.csv", mime="text/csv",
        key="decision_anomalies_download",
    )


def _datetime_fields(df: pd.DataFrame) -> dict:
    candidates = {}
    for column in df.columns:
        series = df[column]
        if pd.api.types.is_datetime64_any_dtype(series):
            parsed = pd.to_datetime(series, errors="coerce")
        elif pd.api.types.is_object_dtype(series) or pd.api.types.is_string_dtype(series):
            parsed = pd.to_datetime(series, errors="coerce", format="mixed")
            nonblank = series.notna().sum()
            if not nonblank or parsed.notna().sum() / nonblank < .8:
                continue
        else:
            continue
        if parsed.notna().nunique() >= 3:
            candidates[column] = parsed
    return candidates


def _render_forecast(df: pd.DataFrame) -> None:
    st.markdown("### Look ahead with a trend estimate")
    st.write(
        "Project a historical measure forward using a simple linear trend. "
        "Use it as an early planning signal and compare it with operational forecasts."
    )
    numeric = _numeric_fields(df)
    dates = _datetime_fields(df)
    if not numeric or not dates:
        st.info("Forecasting needs a numeric measure and a date or time field with at least three distinct periods.")
        return
    date_field = st.selectbox("Time field", list(dates), key="decision_forecast_date")
    measure = st.selectbox("Measure", numeric, key="decision_forecast_measure")
    period_label = st.selectbox("Time interval", ["Day", "Week", "Month", "Quarter", "Year"], index=2, key="decision_forecast_period")
    aggregation = st.selectbox("Calculation", ["Sum", "Average", "Record count"], key="decision_forecast_aggregation")
    horizon = st.slider("Periods to estimate ahead", 1, 12, 3, key="decision_forecast_horizon")
    frequency = {"Day": "D", "Week": "W", "Month": "MS", "Quarter": "QS", "Year": "YS"}[period_label]

    trend_data = pd.DataFrame({"date": dates[date_field], "measure": pd.to_numeric(df[measure], errors="coerce")})
    trend_data = trend_data.dropna().set_index("date").sort_index()
    if aggregation == "Sum":
        history = trend_data["measure"].resample(frequency).sum(min_count=1).dropna()
    elif aggregation == "Average":
        history = trend_data["measure"].resample(frequency).mean().dropna()
    else:
        history = trend_data["measure"].resample(frequency).count().astype(float).dropna()
    if len(history) < 3:
        st.warning("At least three non-empty time intervals are required for a trend estimate. Try a broader time interval.")
        return
    x_values = np.arange(len(history), dtype=float)
    slope, intercept = np.polyfit(x_values, history.to_numpy(dtype=float), 1)
    future_x = np.arange(len(history), len(history) + horizon, dtype=float)
    future_dates = pd.date_range(start=history.index[-1], periods=horizon + 1, freq=frequency)[1:]
    fitted = slope * x_values + intercept
    forecast = slope * future_x + intercept
    figure = go.Figure()
    figure.add_trace(go.Scatter(x=history.index, y=history.values, mode="lines+markers", name="Observed", line={"color": DATALIFY_COLORS[0]}))
    figure.add_trace(go.Scatter(x=history.index, y=fitted, mode="lines", name="Trend fit", line={"color": DATALIFY_COLORS[1], "dash": "dot"}))
    figure.add_trace(go.Scatter(x=future_dates, y=forecast, mode="lines+markers", name="Trend estimate", line={"color": DATALIFY_COLORS[2], "dash": "dash"}))
    figure.update_layout(template="plotly_white", height=390, title=f"{aggregation} of {measure} by {period_label.lower()}", xaxis_title="Period", yaxis_title=str(measure), margin=dict(l=20, r=20, t=55, b=25))
    st.plotly_chart(figure, width="stretch", config={"displaylogo": False})
    st.dataframe(pd.DataFrame({"Period": future_dates, "Estimated value": forecast.round(3)}), width="stretch", hide_index=True)
    st.warning("This is a straight-line extrapolation, not a validated forecasting model. It does not account for seasonality, structural changes, uncertainty, or business drivers. Do not use it alone for high-impact decisions.")


def render_decision_lab() -> None:
    """Render practical investigation tools for decision makers."""
    df = st.session_state.get("working_df")
    if df is None:
        st.info("Load a dataset in Data Intake to use Decision Lab.")
        return
    st.markdown("## Decision Lab")
    st.markdown(
        "### Test assumptions, find unusual records, build segments, and look ahead"
    )
    st.write(
        "These tools support investigation. Results should be reviewed with business "
        "and domain knowledge before action."
    )
    segments_tab, tests_tab, anomalies_tab, forecast_tab = st.tabs(
        ["Segments", "Statistical tests", "Anomalies", "Forecast"],
        key="decision_lab_tabs",
    )
    with segments_tab:
        _render_segments(df)
    with tests_tab:
        _render_statistical_test(df)
    with anomalies_tab:
        _render_anomalies(df)
    with forecast_tab:
        _render_forecast(df)
