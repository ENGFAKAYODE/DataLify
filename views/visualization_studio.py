from itertools import combinations
from datetime import datetime
from io import BytesIO
from pathlib import Path
import re
import textwrap
from zipfile import ZIP_DEFLATED, ZipFile

import numpy as np
import pandas as pd
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.image import imread
from matplotlib.figure import Figure
import plotly.express as px
import streamlit as st

from src.palette import DATALIFY_COLORS


def _clear_visualization_filter_state():
    """Remove saved filter widget values."""
    for key in list(st.session_state.keys()):
        if key.startswith("viz_filter_"):
            del st.session_state[key]


def _kpi_measure(dataframe, definition):
    field_name = definition.get("measure_field")
    field = next((column for column in dataframe.columns if str(column) == field_name), None)
    if field is None:
        return None

    series = dataframe[field]
    calculation = definition.get("calculation", "Sum")
    if calculation == "Count":
        return int(series.count())
    values = pd.to_numeric(series, errors="coerce").dropna()
    if values.empty:
        return None
    operations = {
        "Sum": values.sum,
        "Average": values.mean,
        "Median": values.median,
        "Minimum": values.min,
        "Maximum": values.max,
    }
    return float(operations[calculation]()) if calculation in operations else None


def _date_columns(dataframe):
    result = []
    for column in dataframe.columns:
        series = dataframe[column]
        if pd.api.types.is_datetime64_any_dtype(series):
            result.append(column)
        elif pd.api.types.is_object_dtype(series) or pd.api.types.is_string_dtype(series):
            parsed = pd.to_datetime(series, errors="coerce", format="mixed")
            nonmissing = series.notna().sum()
            if nonmissing and parsed.notna().sum() / nonmissing >= .8 and parsed.nunique() >= 3:
                result.append(column)
    return result


def _kpi_comparison(dataframe, definition):
    """Return the value and readable comparison status for a KPI card."""
    comparison = definition.get("comparison_type", "Target")
    if comparison == "Period over period":
        date_field = next((column for column in dataframe.columns if str(column) == definition.get("period_field")), None)
        if date_field is None:
            return _kpi_measure(dataframe, definition), "Date field unavailable", "off"
        dates = pd.to_datetime(dataframe[date_field], errors="coerce", format="mixed")
        frequency = definition.get("period_frequency", "Month")
        period_code = {"Week": "W", "Month": "M", "Quarter": "Q", "Year": "Y"}.get(frequency, "M")
        periods = dates.dt.to_period(period_code)
        latest = periods.max()
        if pd.isna(latest):
            return None, "No dated records", "off"
        current = _kpi_measure(dataframe.loc[periods == latest], definition)
        previous = _kpi_measure(dataframe.loc[periods == latest - 1], definition)
        if current is None or previous is None:
            return current, "Prior period unavailable", "off"
        if previous == 0:
            return current, "Prior period is zero", "off"
        change = (current - previous) / abs(previous) * 100
        return current, f"{change:+.1f}% vs prior {frequency.lower()}", "normal"

    if comparison == "Industry benchmark":
        target = definition.get("benchmark")
        status_label = "Industry benchmark"
    else:
        target = definition.get("target")
        status_label = "Target"
    if target is None:
        return _kpi_measure(dataframe, definition), f"{status_label} not set", "off"
    actual = _kpi_measure(dataframe, definition)
    if actual is None:
        return None, "No valid values", "off"
    direction = definition.get("target_direction", "At least")
    if direction.startswith("Greater than"):
        met = actual > target
    elif direction.startswith("At most"):
        met = actual <= target
    elif direction.startswith("Less than"):
        met = actual < target
    elif direction.startswith("Exactly"):
        met = np.isclose(actual, target)
    else:
        met = actual >= target
    if comparison == "Target":
        status = "Target met" if met else "Target missed"
    else:
        status = "Benchmark met" if met else "Benchmark missed"
    return actual, status, "normal" if met else "inverse"


def _format_kpi(value, definition):
    if value is None or pd.isna(value):
        return "N/A"
    number = f"{value:,.2f}".rstrip("0").rstrip(".")
    return f"{definition.get('prefix', '')}{number}{definition.get('suffix', '')}"


def _correlation(dataframe, method):
    """Calculate Pearson or rank-based Spearman correlation without SciPy."""
    if method.lower() == "spearman":
        ranked = dataframe.rank(method="average")
        return ranked.corr(method="pearson")
    return dataframe.corr(method="pearson")


def _chart_png(chart_type, dataframe, x_field, y_field, color_field, aggregation):
    """Render a saved chart as a PNG using Datalify's installed Matplotlib."""
    figure = Figure(figsize=(10, 5.6), dpi=170, facecolor="white")
    FigureCanvasAgg(figure)
    axis = figure.subplots()
    colors = list(DATALIFY_COLORS)

    if chart_type == "Histogram":
        values = pd.to_numeric(dataframe[x_field], errors="coerce").dropna()
        axis.hist(values, bins="auto", color=colors[0], edgecolor="white")
        axis.set_title(f"Distribution of {x_field}")
        axis.set_xlabel(str(x_field))
        axis.set_ylabel("Records")
    elif chart_type == "Scatter":
        clean = dataframe.dropna(subset=[x_field, y_field])
        axis.scatter(clean[x_field], clean[y_field], color=colors[0], alpha=.72, s=24)
        axis.set_title(f"{y_field} vs {x_field}")
        axis.set_xlabel(str(x_field))
        axis.set_ylabel(str(y_field))
    elif chart_type == "Box":
        clean = dataframe[[x_field, y_field]].copy()
        clean[y_field] = pd.to_numeric(clean[y_field], errors="coerce")
        clean = clean.dropna()
        if x_field == y_field:
            groups = [clean[y_field].to_numpy()]
            labels = [str(y_field)]
        else:
            clean[x_field] = clean[x_field].fillna("(Missing)").astype(str)
            labels = list(clean[x_field].unique())[:20]
            groups = [clean.loc[clean[x_field] == label, y_field].to_numpy() for label in labels]
        axis.boxplot(groups, patch_artist=True,
                     boxprops={"facecolor": colors[0], "alpha": .7})
        axis.set_xticks(range(1, len(labels) + 1), labels)
        axis.set_title(f"Distribution of {y_field}")
        axis.set_ylabel(str(y_field))
    elif chart_type == "Pie":
        pie_data = dataframe.groupby(x_field, dropna=False)[y_field].sum(min_count=1).dropna()
        pie_data = pie_data[pie_data >= 0].sort_values(ascending=False).head(12)
        if pie_data.empty or pie_data.sum() <= 0:
            axis.text(.5, .5, "No non-negative values to chart", ha="center", va="center")
            axis.set_axis_off()
        else:
            axis.pie(pie_data.values, labels=[str(value) for value in pie_data.index],
                     colors=colors * (len(pie_data) // len(colors) + 1),
                     autopct="%1.0f%%", startangle=90)
            axis.set_title(f"{y_field} by {x_field}")
    else:
        clean = dataframe[[x_field, y_field] + ([color_field] if color_field and color_field != x_field else [])].copy()
        clean[y_field] = pd.to_numeric(clean[y_field], errors="coerce")
        clean = clean.dropna(subset=[y_field])
        if color_field and color_field != x_field:
            clean[color_field] = clean[color_field].fillna("(Missing)").astype(str)
            pivot = clean.pivot_table(index=x_field, columns=color_field, values=y_field,
                                      aggfunc=aggregation.lower(), observed=False)
            pivot = pivot.sort_index().iloc[:50]
        else:
            grouped = clean.groupby(x_field, dropna=False)[y_field]
            operation = {"Sum": "sum", "Mean": "mean", "Median": "median", "Count": "count"}.get(aggregation, "sum")
            pivot = getattr(grouped, operation)().to_frame(name=str(y_field)).sort_index().iloc[:50]
        if chart_type == "Bar":
            pivot.plot(kind="bar", ax=axis, color=colors, width=.78)
        elif chart_type == "Line":
            pivot.plot(kind="line", ax=axis, color=colors, marker="o")
        else:
            pivot.plot(kind="area", ax=axis, color=colors, alpha=.58)
        axis.set_title(f"{aggregation} of {y_field} by {x_field}")
        axis.set_xlabel(str(x_field))
        axis.set_ylabel(str(y_field))
        axis.legend(title=str(color_field) if color_field else None, frameon=False)

    axis.grid(axis="y", color="#E8EDF5", linewidth=.7)
    axis.set_axisbelow(True)
    if chart_type not in ("Pie", "Scatter"):
        axis.tick_params(axis="x", labelrotation=25)
    figure.tight_layout()
    image = BytesIO()
    figure.savefig(image, format="png", dpi=170, bbox_inches="tight", facecolor="white")
    return image.getvalue()


def _kpi_dashboard_png(dataframe, definitions):
    """Create a clean PNG scorecard for all saved business KPIs."""
    columns = 2
    rows = max(1, (len(definitions) + columns - 1) // columns)
    figure = Figure(figsize=(12, max(3.5, rows * 2.25)), dpi=170, facecolor="#F5F7FB")
    FigureCanvasAgg(figure)
    for index, definition in enumerate(definitions):
        axis = figure.add_subplot(rows, columns, index + 1)
        axis.set_facecolor("white")
        for spine in axis.spines.values():
            spine.set_edgecolor("#DCE5F2")
            spine.set_linewidth(1.1)
        axis.set_xticks([])
        axis.set_yticks([])
        actual, status, _ = _kpi_comparison(dataframe, definition)
        value = _format_kpi(actual, definition)
        status_color = "#16836F" if status in ("On target", "Target met", "Benchmark met") else "#2857A7" if "vs prior" in status else "#64748B" if "not set" in status.lower() or "unavailable" in status.lower() else "#C44955"
        axis.text(.06, .78, definition.get("name", "Business KPI"), transform=axis.transAxes,
                  fontsize=13, weight="bold", color="#34445F")
        axis.text(.06, .44, value, transform=axis.transAxes, fontsize=24,
                  weight="bold", color="#17243B")
        axis.text(.06, .16, status, transform=axis.transAxes, fontsize=10,
                  weight="medium", color=status_color)
    figure.suptitle("Datalify | Business KPI scorecard", fontsize=17, weight="bold", color="#17243B", y=.99)
    figure.tight_layout(rect=(0, 0, 1, .95))
    image = BytesIO()
    figure.savefig(image, format="png", dpi=170, bbox_inches="tight", facecolor="#F5F7FB")
    return image.getvalue()


def _applied_filter_descriptions(dataframe):
    """Summarize applied filters without dumping high-cardinality selections."""
    descriptions = []
    count = int(st.session_state.get("viz_filter_count", 0))
    for index in range(count):
        column = st.session_state.get(f"viz_filter_column_{index}")
        if column not in dataframe.columns:
            continue
        series = dataframe[column]
        if pd.api.types.is_numeric_dtype(series):
            selected_range = st.session_state.get(f"viz_filter_range_{index}")
            if selected_range and (selected_range[0] > series.min() or selected_range[1] < series.max()):
                descriptions.append(f"{column}: {selected_range[0]:g} to {selected_range[1]:g}")
        else:
            options = sorted(series.dropna().unique().tolist(), key=lambda value: str(value))
            selected = st.session_state.get(f"viz_filter_values_{index}", options)
            excluded = [value for value in options if value not in selected]
            if excluded:
                if len(selected) <= 5:
                    descriptions.append(f"{column}: {', '.join(map(str, selected)) or 'no values'} selected")
                elif len(excluded) <= 5:
                    descriptions.append(f"{column}: excluding {', '.join(map(str, excluded))}")
                else:
                    descriptions.append(f"{column}: {len(selected):,} of {len(options):,} values selected ({len(excluded):,} excluded)")
    return descriptions or ["No active filters"]


def _dashboard_png(dataframe, definitions, visualizations, filters):
    """Compose KPI cards above saved charts with a branded, filter-aware header."""
    kpi_columns = 4
    kpi_rows = max(1, (len(definitions) + kpi_columns - 1) // kpi_columns)
    chart_rows = max(1, (len(visualizations) + 1) // 2)
    filter_lines = []
    for item in filters:
        filter_lines.extend(textwrap.wrap(str(item), width=145) or [""])
    header_height = max(1.55, 1.0 + .17 * len(filter_lines))
    row_heights = [header_height] + [1.35] * kpi_rows + [3.35] * chart_rows
    figure = Figure(figsize=(14, sum(row_heights) + .45), dpi=170, facecolor="#F4F7FB")
    FigureCanvasAgg(figure)
    grid = figure.add_gridspec(len(row_heights), 4, height_ratios=row_heights,
                               left=.035, right=.965, top=.985, bottom=.035,
                               hspace=.24, wspace=.16)

    header = figure.add_subplot(grid[0, :])
    header.set_facecolor("white")
    header.set_xticks([])
    header.set_yticks([])
    for spine in header.spines.values():
        spine.set_edgecolor("#DCE5F2")
    logo_path = Path(__file__).resolve().parents[1] / "assets" / "insightprovider.png"
    if logo_path.is_file():
        logo_axis = header.inset_axes([.012, .40, .13, .48])
        logo_axis.imshow(imread(logo_path))
        logo_axis.axis("off")
    header.text(.17, .75, "Datalify analysis dashboard", transform=header.transAxes,
                fontsize=17, fontweight="bold", color="#17243B", va="center")
    generated = datetime.now().astimezone().strftime("%b %d, %Y at %I:%M %p %Z")
    header.text(.98, .78, f"Generated {generated}", transform=header.transAxes,
                ha="right", va="center", fontsize=9, color="#64748B")
    header.text(.17, .48, "Filters applied", transform=header.transAxes,
                fontsize=9, fontweight="bold", color="#2857A7", va="top")
    header.text(.17, .38, "\n".join(filter_lines), transform=header.transAxes,
                fontsize=8.2, color="#42516A", va="top", linespacing=1.3)

    for index in range(kpi_rows * kpi_columns):
        row, col = divmod(index, kpi_columns)
        axis = figure.add_subplot(grid[1 + row, col])
        axis.set_facecolor("white")
        axis.set_xticks([])
        axis.set_yticks([])
        for spine in axis.spines.values():
            spine.set_edgecolor("#DCE5F2")
        if index >= len(definitions):
            if index == 0 and not definitions:
                axis.text(.5, .5, "No KPI cards added", ha="center", va="center",
                          transform=axis.transAxes, fontsize=10, color="#64748B")
            continue
        definition = definitions[index]
        actual, status, _ = _kpi_comparison(dataframe, definition)
        status_color = "#16836F" if status in ("On target", "Target met", "Benchmark met") else "#2857A7" if "vs prior" in status else "#64748B" if "not set" in status.lower() or "unavailable" in status.lower() else "#C44955"
        axis.text(.07, .76, definition.get("name", "Business KPI"), transform=axis.transAxes,
                  fontsize=10, fontweight="bold", color="#34445F", va="center")
        axis.text(.07, .45, _format_kpi(actual, definition), transform=axis.transAxes,
                  fontsize=19, fontweight="bold", color="#17243B", va="center")
        axis.text(.07, .16, status, transform=axis.transAxes,
                  fontsize=8, color=status_color, va="center")

    for index in range(chart_rows * 2):
        row, col = divmod(index, 2)
        axis = figure.add_subplot(grid[1 + kpi_rows + row, col * 2:(col + 1) * 2])
        axis.set_facecolor("white")
        for spine in axis.spines.values():
            spine.set_edgecolor("#DCE5F2")
        axis.set_xticks([])
        axis.set_yticks([])
        if index >= len(visualizations):
            if index == 0 and not visualizations:
                axis.text(.5, .5, "No charts added", ha="center", va="center",
                          transform=axis.transAxes, fontsize=11, color="#64748B")
            continue
        saved = visualizations[index]
        axis.imshow(imread(BytesIO(saved["png"])))
        axis.set_title(saved.get("title", f"Visualization {index + 1}"),
                       loc="left", fontsize=10, color="#34445F", pad=5)
        axis.axis("off")

    image = BytesIO()
    figure.savefig(image, format="png", dpi=170, bbox_inches="tight", facecolor="#F4F7FB")
    return image.getvalue()


def _png_export_bundle(dataframe):
    definitions = st.session_state.get("business_kpis", [])
    visualizations = st.session_state.get("viz_export_items", [])
    current_filters = _applied_filter_descriptions(st.session_state.get("working_df", dataframe))
    filter_details = [f"KPI dashboard: {', '.join(current_filters)}"]
    for visualization in visualizations:
        chart_filters = visualization.get("filters", ["No filters applied"])
        filter_details.append(f"{visualization['title']}: {', '.join(chart_filters)}")

    bundle = BytesIO()
    with ZipFile(bundle, "w", ZIP_DEFLATED) as archive:
        archive.writestr("datalify_dashboard.png", _dashboard_png(dataframe, definitions, visualizations, filter_details))
        if definitions:
            archive.writestr("datalify_kpis.png", _kpi_dashboard_png(dataframe, definitions))
        for index, visualization in enumerate(visualizations, start=1):
            safe_title = re.sub(r"[^A-Za-z0-9_-]+", "_", visualization["title"]).strip("_")[:45] or "visualization"
            archive.writestr(f"charts/visualization_{index:02d}_{safe_title}.png", visualization["png"])
    return bundle.getvalue()


def _render_relationships(dataframe):
    st.markdown("### Relationships")
    st.caption("Correlation is a signal for investigation—not proof of causation.")

    numeric_fields = dataframe.select_dtypes(include="number").columns.tolist()
    if len(numeric_fields) < 2:
        st.info("Relationships need at least two numeric fields. Add numeric fields to your dataset to compare them here.")
        return

    st.markdown("#### Correlation matrix")
    matrix_fields = st.multiselect(
        "Fields in correlation matrix",
        options=numeric_fields,
        default=numeric_fields,
        key="viz_relationship_matrix_fields",
        help="Select the exact numeric fields to include.",
    )
    method_label = st.selectbox(
        "Correlation method", ["Pearson", "Spearman"], key="viz_relationship_method"
    )
    matrix = None
    if len(matrix_fields) < 2:
        st.info("Select at least two numeric fields to display the correlation matrix.")
    else:
        matrix = _correlation(dataframe[matrix_fields], method_label)
        st.caption("Each cell shows how strongly a pair of numeric fields moves together. Values range from −1 to +1.")
        matrix_figure = px.imshow(
            matrix,
            text_auto=".2f",
            zmin=-1,
            zmax=1,
            color_continuous_scale="RdBu",
            color_continuous_midpoint=0,
            aspect="auto",
            labels={"x": "Field", "y": "Field", "color": "Correlation"},
        )
        matrix_figure.update_layout(
            template="plotly_white",
            height=min(760, max(380, 70 * len(matrix_fields))),
            margin=dict(l=20, r=20, t=25, b=20),
        )
        st.plotly_chart(matrix_figure, width="stretch", config={"displaylogo": False})

    st.markdown("**Find variables that move together**")
    st.caption("Correlation is a signal for investigation—not proof of causation.")

    categorical_fields = [column for column in dataframe.columns if column not in numeric_fields]
    control_x, control_y, control_color = st.columns([1, 1, 1.1])
    with control_x:
        x_field = st.selectbox("X axis", numeric_fields, key="viz_relationship_x")
    with control_y:
        y_options = [column for column in numeric_fields if column != x_field]
        # Clear a stale choice if changing X would otherwise select the same field twice.
        if st.session_state.get("viz_relationship_y") not in y_options:
            st.session_state.pop("viz_relationship_y", None)
        y_field = st.selectbox("Y axis", y_options, key="viz_relationship_y")
    with control_color:
        segment_options = ["None"] + categorical_fields
        segment = st.selectbox("Color by segment", segment_options, key="viz_relationship_segment")

    pair = dataframe[[x_field, y_field]].apply(pd.to_numeric, errors="coerce").dropna()
    if len(pair) < 2 or pair[x_field].nunique() < 2 or pair[y_field].nunique() < 2:
        st.info("These fields need at least two valid, varying pairs to calculate a relationship.")
        return

    correlation = float(_correlation(pair[[x_field, y_field]], method_label).iloc[0, 1])
    strength = "very weak" if abs(correlation) < .2 else "weak" if abs(correlation) < .4 else "moderate" if abs(correlation) < .7 else "strong"
    direction = "positive" if correlation > 0 else "negative"
    result_col, chart_col = st.columns([.7, 1.8], gap="large")
    with result_col:
        st.metric(f"{method_label} correlation", f"{correlation:+.3f}")
        st.caption(f"{strength.title()} {direction} association across {len(pair):,} valid pairs.")
        st.info("Association alone does not establish why values change together.")
    with chart_col:
        plot_data = dataframe.loc[pair.index].copy()
        plot_data[x_field] = pair[x_field]
        plot_data[y_field] = pair[y_field]
        color_field = None
        if segment != "None":
            plot_data[segment] = plot_data[segment].fillna("(Missing)").astype(str)
            color_field = segment
        figure = px.scatter(
            plot_data, x=x_field, y=y_field, color=color_field,
            color_discrete_sequence=DATALIFY_COLORS,
            title=f"{x_field} and {y_field}", opacity=.78,
        )
        if method_label == "Pearson":
            slope, intercept = np.polyfit(pair[x_field], pair[y_field], 1)
            trend_x = np.linspace(pair[x_field].min(), pair[x_field].max(), 60)
            figure.add_scatter(
                x=trend_x, y=slope * trend_x + intercept, mode="lines",
                name="Linear trend", line={"color": "#17243B", "dash": "dash"},
            )
        figure.update_layout(template="plotly_white", height=360, margin=dict(l=20, r=20, t=55, b=20))
        st.plotly_chart(figure, width="stretch", config={"displaylogo": False})

    if matrix is not None and len(matrix_fields) > 2:
        rows = []
        for first, second in combinations(matrix_fields, 2):
            value = matrix.loc[first, second]
            if pd.notna(value):
                rows.append({"Field 1": str(first), "Field 2": str(second), "Correlation": float(value)})
        if rows:
            top_pairs = pd.DataFrame(rows)
            top_pairs["Absolute strength"] = top_pairs["Correlation"].abs()
            top_pairs = top_pairs.sort_values("Absolute strength", ascending=False).drop(columns="Absolute strength").head(10)
            with st.expander("Explore the strongest field relationships"):
                st.dataframe(top_pairs, width="stretch", hide_index=True)


def _render_kpi_builder(dataframe):
    st.markdown("### Business KPIs")
    st.markdown("**Define the numbers leadership should watch**")
    st.caption("KPIs you add here are collected into a dashboard-style scorecard and included in the PNG export.")
    definitions = st.session_state.setdefault("business_kpis", [])
    numeric_fields = dataframe.select_dtypes(include="number").columns.tolist()
    measure_fields = numeric_fields or dataframe.columns.tolist()
    if not measure_fields:
        st.info("Add fields to this dataset before defining a KPI.")
        return

    st.markdown("#### Create a KPI")
    name_col, field_col, calculation_col = st.columns([1.2, 1, .9])
    with name_col:
        business_name = st.text_input("Business name", value="Total revenue", key="viz_kpi_name")
    with field_col:
        measure_field = st.selectbox("Measure field", measure_fields, key="viz_kpi_measure")
    with calculation_col:
        calculations = ["Sum", "Average", "Median", "Count", "Minimum", "Maximum"] if measure_field in numeric_fields else ["Count"]
        calculation = st.selectbox("Calculation", calculations, key="viz_kpi_calculation")

    prefix_col, suffix_col = st.columns([.8, .8])
    with prefix_col:
        prefix = st.text_input("Prefix", value="$", key="viz_kpi_prefix")
    with suffix_col:
        suffix = st.text_input("Suffix", value="", key="viz_kpi_suffix", help="Optional unit after the value, such as %, orders, or customers.")
    date_fields = _date_columns(dataframe)
    comparison_type = st.selectbox(
        "Compare against",
        ["Target", "Period over period", "Industry benchmark"],
        key="viz_kpi_comparison_type",
    )

    comparison_value = None
    period_field = None
    period_frequency = "Month"
    target_direction = "At least"
    if comparison_type == "Target":
        value_col, direction_col = st.columns([1.2, 1])
        with value_col:
            comparison_value_text = st.text_input(
                "Target value", placeholder="Enter the target to compare against",
                key="viz_kpi_target_value",
            )
        with direction_col:
            target_direction = st.selectbox(
                "Target is met when",
                ["At least (≥)", "Greater than (>)", "At most (≤)", "Less than (<)", "Exactly (=)"],
                key="viz_kpi_target_direction",
            )
    elif comparison_type == "Industry benchmark":
        value_col, direction_col = st.columns([1.2, 1])
        with value_col:
            comparison_value_text = st.text_input(
                "Industry benchmark", placeholder="Enter the benchmark value",
                key="viz_kpi_industry_benchmark",
            )
        with direction_col:
            target_direction = st.selectbox(
                "Benchmark is met when",
                ["At least (≥)", "Greater than (>)", "At most (≤)", "Less than (<)", "Exactly (=)"],
                key="viz_kpi_benchmark_direction",
            )
    else:
        period_col, frequency_col = st.columns([1.2, .8])
        with period_col:
            period_field = st.selectbox(
                "Date field for period comparison",
                date_fields or ["No date field detected"],
                key="viz_kpi_period_field",
                help="The latest available period is compared with the one immediately before it.",
            )
        with frequency_col:
            period_frequency = st.selectbox(
                "Period", ["Week", "Month", "Quarter", "Year"], index=1,
                key="viz_kpi_period_frequency",
            )
    create = st.button("Create KPI", type="primary", icon=":material/add_chart:", key="viz_create_business_kpi")
    if create:
        if not business_name.strip():
            st.error("Enter a business name for this KPI.")
        else:
            if comparison_type in ("Target", "Industry benchmark"):
                try:
                    comparison_value = float(comparison_value_text.replace(",", "").strip()) if comparison_value_text.strip() else None
                except ValueError:
                    st.error("The target or benchmark must be a number, or left blank.")
                    comparison_value = "invalid"
            if comparison_value == "invalid":
                return
            if comparison_type == "Industry benchmark" and comparison_value is None:
                st.error("Enter the industry benchmark value to compare against.")
                return
            if comparison_type == "Period over period" and period_field not in date_fields:
                st.error("Add or select a valid date field for period-over-period comparison.")
                return
            if comparison_value is not None or comparison_type in ("Target", "Period over period"):
                definition = {
                    "name": business_name.strip(), "measure_field": str(measure_field),
                    "calculation": calculation, "prefix": prefix, "suffix": suffix,
                    "comparison_type": comparison_type,
                    "target": comparison_value if comparison_type == "Target" else None,
                    "benchmark": comparison_value if comparison_type == "Industry benchmark" else None,
                    "target_direction": target_direction,
                    "period_field": str(period_field) if period_field in date_fields else None,
                    "period_frequency": period_frequency,
                }
                existing = next((i for i, item in enumerate(definitions) if item.get("name", "").casefold() == definition["name"].casefold()), None)
                if existing is None:
                    definitions.append(definition)
                else:
                    definitions[existing] = definition
                st.rerun()

    if not definitions:
        st.info("Create your first KPI below. KPI definitions are included in exported project recipes.")
        return

    st.markdown("#### KPI scorecard")
    for start in range(0, len(definitions), 3):
        card_columns = st.columns(3, gap="medium")
        for offset, column in enumerate(card_columns):
            index = start + offset
            if index >= len(definitions):
                continue
            definition = definitions[index]
            actual, status, delta_color = _kpi_comparison(dataframe, definition)
            formatted = _format_kpi(actual, definition)
            with column:
                st.metric(
                    definition["name"], formatted, delta=status, delta_color=delta_color,
                    help=f"{definition['calculation']} of {definition['measure_field']} in the current filtered data.",
                )
                segment_field = definition.get("segment_field")
                if segment_field in dataframe.columns:
                    grouped = dataframe.groupby(segment_field, dropna=False)[definition["measure_field"]]
                    if definition["calculation"] == "Count":
                        values = grouped.count()
                    else:
                        numeric = dataframe.assign(**{definition["measure_field"]: pd.to_numeric(dataframe[definition["measure_field"]], errors="coerce")})
                        grouped = numeric.groupby(segment_field, dropna=False)[definition["measure_field"]]
                        operation = {"Sum": "sum", "Average": "mean", "Median": "median", "Minimum": "min", "Maximum": "max"}.get(definition["calculation"], "sum")
                        values = getattr(grouped, operation)()
                    segment_data = values.rename("Value").reset_index().sort_values("Value", ascending=False).head(10)
                    segment_data[segment_field] = segment_data[segment_field].fillna("(Missing)").astype(str)
                    chart = px.bar(segment_data, x=segment_field, y="Value", color_discrete_sequence=DATALIFY_COLORS, title=f"{definition['name']} by {segment_field}")
                    chart.update_layout(template="plotly_white", height=260, margin=dict(l=8, r=8, t=45, b=15), showlegend=False)
                    st.plotly_chart(chart, width="stretch", config={"displaylogo": False})
                if st.button("Remove KPI", key=f"viz_remove_kpi_{index}"):
                    definitions.pop(index)
                    st.rerun()


def render_visualization_studio():
    """Render Datalify's interactive Visualization Studio."""

    st.markdown("## Visualization Studio")
    px.defaults.color_discrete_sequence = list(DATALIFY_COLORS)
    st.write(
        "Filter records, explore patterns with charts and KPIs, download the filtered data, "
        "or export saved KPIs and charts as dashboard-ready PNGs."
    )

    if st.session_state.get("working_df") is None:
        st.info("Import a dataset in Data Intake before creating visualizations.")
        return

    source_df = st.session_state.working_df.copy(deep=True)

    if source_df.empty or len(source_df.columns) == 0:
        st.warning("The dataset has no data to visualize.")
        return

    filtered_df = source_df.copy(deep=True)
    available_columns = source_df.columns.tolist()

    # Keep the filter count available across Streamlit reruns.
    if "viz_filter_count" not in st.session_state:
        st.session_state.viz_filter_count = 1

    # Filter controls
    filter_count = int(st.session_state.viz_filter_count)

    with st.expander(
        f"Data filters ({filter_count} configured)",
        expanded=st.session_state.get("viz_show_filters", False),
    ):
        st.caption(
            "Add multiple filters to narrow your data. "
            "All active filters are applied together."
        )

        add_col, remove_col, reset_col = st.columns(3)

        with add_col:
            if st.button(
                "＋ Add filter",
                width="stretch",
                key="viz_add_filter",
            ):
                st.session_state.viz_filter_count += 1
                st.session_state.viz_show_filters = True
                st.rerun()

        with remove_col:
            if st.button(
                "− Remove filter",
                disabled=filter_count <= 0,
                width="stretch",
                key="viz_remove_filter",
            ):
                last_index = filter_count - 1
                for suffix in ("column", "range", "values"):
                    st.session_state.pop(
                        f"viz_filter_{suffix}_{last_index}", None
                    )
                st.session_state.viz_filter_count = max(0, filter_count - 1)
                st.session_state.viz_show_filters = True
                st.rerun()

        with reset_col:
            if st.button(
                "Reset filters",
                width="stretch",
                key="viz_reset_filters",
            ):
                _clear_visualization_filter_state()
                st.session_state.viz_filter_count = 1
                st.session_state.viz_show_filters = True
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
                        st.caption("No numeric values available in this column.")
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
                                    selected_range[0], selected_range[1]
                                )
                                | filtered_df[selected_column].isna()
                            ]
                        else:
                            st.caption(
                                "This column has only one distinct numeric value."
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
                        filtered_df[selected_column].isin(selected_values)
                        | filtered_df[selected_column].isna()
                    ]

    with st.expander("View filtered data", expanded=False):
        st.dataframe(filtered_df.head(1000), width="stretch", hide_index=True)
        st.caption("Showing up to 1,000 rows in this preview.")
        csv_data = filtered_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download filtered data (CSV)",
            data=csv_data,
            file_name="datalify_filtered_data.csv",
            mime="text/csv",
            key="viz_download_filtered_data",
        )

    # Row counts
    total_rows = len(source_df)
    visible_rows = len(filtered_df)
    excluded_rows = total_rows - visible_rows

    metric1, metric2, metric3 = st.columns(3)
    metric1.metric("Original rows", f"{total_rows:,}")
    metric2.metric("Filtered rows", f"{visible_rows:,}")
    metric3.metric("Excluded rows", f"{excluded_rows:,}")

    if filtered_df.empty:
        st.warning(
            "No rows match all selected filters. Expand Data filters and adjust "
            "your selections."
        )
        return

    _render_kpi_builder(filtered_df)

    # Chart configuration
    st.markdown("### Visualization")

    numeric_columns = filtered_df.select_dtypes(include="number").columns.tolist()
    all_columns = filtered_df.columns.tolist()

    chart_options = ["Bar", "Line", "Area", "Scatter", "Histogram", "Box", "Pie"]

    config1, config2, config3 = st.columns(3)

    with config1:
        chart_type = st.selectbox(
            "Chart type",
            chart_options,
            key="viz_chart_type",
        )

    with config2:
        if chart_type in ("Histogram", "Scatter"):
            x_options = numeric_columns or all_columns
        else:
            x_options = all_columns
        category_columns = [column for column in all_columns if column not in numeric_columns]
        preferred_x = next((column for column in category_columns if column in x_options), x_options[0])
        if st.session_state.get("viz_x_column") not in x_options:
            st.session_state["viz_x_column"] = preferred_x

        x_column = st.selectbox(
            "X-axis / Category",
            x_options,
            key="viz_x_column",
        )

    with config3:
        y_options = numeric_columns
        if chart_type in ("Bar", "Line", "Area", "Pie") and x_column in y_options and len(y_options) > 1:
            y_options = [column for column in y_options if column != x_column]
        elif chart_type in ("Bar", "Line", "Area", "Pie") and x_column in y_options and len(y_options) == 1:
            y_options = []
        if y_options:
            if st.session_state.get("viz_y_column") not in y_options:
                st.session_state["viz_y_column"] = y_options[0]
            y_column = st.selectbox(
                "Y-axis / Numeric value",
                y_options,
                key="viz_y_column",
            )
        else:
            y_column = None
            st.info(
                "No numeric columns detected. A numeric measure is needed "
                "for this chart."
            )

    config4, config5 = st.columns(2)

    with config4:
        if chart_type in ("Bar", "Line", "Area") and y_column is not None:
            aggregation = st.selectbox(
                "Aggregation",
                ["Sum", "Mean", "Median", "Count"],
                key="viz_aggregation",
            )
        else:
            aggregation = "Sum"

    with config5:
        if chart_type in ("Bar", "Line", "Area", "Scatter", "Box"):
            color_options = ["No grouping"] + all_columns
            color_column = st.selectbox(
                "Color / Group by",
                color_options,
                key="viz_color_column",
            )
            if color_column == "No grouping":
                color_column = None
        else:
            color_column = None

    # Build and render the chart using the configuration above.
    fig = None

    if chart_type == "Histogram":
        if not pd.api.types.is_numeric_dtype(filtered_df[x_column]):
            st.warning("Select a numeric column for a histogram.")
        else:
            fig = px.histogram(
                filtered_df,
                x=x_column,
                color=color_column,
                title=f"Distribution of {x_column}",
                labels={x_column: x_column},
            )
            st.plotly_chart(fig, width="stretch")

    elif chart_type == "Scatter":
        if y_column is None:
            st.warning("A numeric Y-axis column is required.")
        elif not pd.api.types.is_numeric_dtype(filtered_df[x_column]):
            st.warning("Select a numeric X-axis column for a scatter plot.")
        else:
            scatter_df = filtered_df.dropna(subset=[x_column, y_column])
            if len(scatter_df) > 10000:
                st.caption(
                    "Showing a sample of 10,000 records to keep the scatter plot responsive."
                )
                scatter_df = scatter_df.sample(n=10000, random_state=42)

            fig = px.scatter(
                scatter_df,
                x=x_column,
                y=y_column,
                color=color_column,
                title=f"{y_column} vs {x_column}",
            )
            st.plotly_chart(fig, width="stretch")

    elif chart_type == "Box":
        if y_column is None:
            st.warning("A numeric column is required for a box plot.")
        else:
            fig = px.box(
                filtered_df,
                x=x_column if x_column != y_column else None,
                y=y_column,
                color=color_column,
                title=f"Distribution of {y_column}",
                points="outliers",
            )
            st.plotly_chart(fig, width="stretch")

    elif chart_type == "Pie":
        if y_column is None:
            st.warning("A numeric column is required for a pie chart.")
        else:
            pie_data = (
                filtered_df.groupby(x_column, dropna=False)[y_column]
                .sum()
                .reset_index()
            )
            pie_data[x_column] = pie_data[x_column].fillna("(Missing)").astype(str)
            pie_data = pie_data[pie_data[y_column] >= 0]

            if pie_data.empty:
                st.warning(
                    "No non-negative values are available to create a pie chart."
                )
            else:
                fig = px.pie(
                    pie_data,
                    names=x_column,
                    values=y_column,
                    title=f"{y_column} by {x_column}",
                )
                st.plotly_chart(fig, width="stretch")

    elif chart_type in ("Bar", "Line", "Area"):
        if y_column is None:
            st.warning("A numeric column is required for this chart.")
        else:
            group_columns = [x_column]
            if color_column and color_column != x_column:
                group_columns.append(color_column)

            grouped = filtered_df.groupby(group_columns, dropna=False)[y_column]
            if aggregation == "Sum":
                chart_data = grouped.sum().reset_index()
            elif aggregation == "Mean":
                chart_data = grouped.mean().reset_index()
            elif aggregation == "Median":
                chart_data = grouped.median().reset_index()
            else:
                chart_data = grouped.count().reset_index()

            chart_data[x_column] = chart_data[x_column].fillna("(Missing)").astype(str)
            if color_column and color_column != x_column:
                chart_data[color_column] = (
                    chart_data[color_column].fillna("(Missing)").astype(str)
                )

            color_arg = color_column if color_column != x_column else None
            chart_title = f"{aggregation} of {y_column} by {x_column}"

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

            st.plotly_chart(fig, width="stretch")

    if fig is not None:
        chart_title = getattr(getattr(fig.layout, "title", None), "text", None) or f"{chart_type} visualization"
        if st.button(
            "Add viz to dashboard export",
            type="primary",
            icon=":material/add_photo_alternate:",
            key="viz_add_current_export",
        ):
            st.session_state.setdefault("viz_export_items", []).append({
                "title": str(chart_title),
                "png": _chart_png(
                    chart_type, filtered_df, x_column, y_column,
                    color_column, aggregation,
                ),
                "filters": _applied_filter_descriptions(source_df),
            })
            st.rerun()

    st.markdown("### Export KPIs and visualizations")
    st.write("Add as many KPIs and charts as you need. Export them together as a ZIP of PNG images.")
    saved_visualizations = st.session_state.setdefault("viz_export_items", [])
    if saved_visualizations:
        for index, saved in enumerate(saved_visualizations):
            asset_col, remove_col = st.columns([5, 1])
            asset_col.caption(f"Visualization {index + 1}: {saved['title']}")
            if remove_col.button("Remove", key=f"viz_remove_export_{index}"):
                saved_visualizations.pop(index)
                st.rerun()
    else:
        st.caption("No visualizations have been added to the export yet.")

    have_export_assets = bool(st.session_state.get("business_kpis") or saved_visualizations)
    st.download_button(
        "Export added KPIs and visualizations as PNGs",
        data=_png_export_bundle(filtered_df),
        file_name="datalify_visuals_and_kpis.zip",
        mime="application/zip",
        disabled=not have_export_assets,
        type="primary",
        icon=":material/download:",
        key="viz_export_png_bundle",
    )

    # Filtered data preview and download are kept together in the disclosure above.

    # Relationship analysis stays at the end, after charting and exports.
    st.divider()
    _render_relationships(filtered_df)

    st.caption(
        "Charts use the filtered dataset. Filtering here does not modify "
        "your working dataset."
    )
