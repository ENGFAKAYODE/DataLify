
from datetime import datetime
import base64

import pandas as pd
import plotly.express as px
import streamlit as st


def render_quality_lab():
    # =================================================
    # CHECK FOR A LOADED DATASET
    # =================================================
    if st.session_state.working_df is None:
        st.info(
            "No dataset is loaded. Open Data Intake to upload "
            "a CSV or Excel file before using this workspace."
        )
        return

    df = st.session_state.working_df.copy(deep=True)

    # =================================================
    # HEADER AND CONSTANT KPIs
    # =================================================
    st.markdown("## Data Quality Lab")

    st.caption(
        "Profile column-level quality, investigate distributions "
        "and relationships, and identify potential "
        "numeric outliers."
    )

    row_count = len(df)
    column_count = len(df.columns)
    missing_count = int(df.isna().sum().sum())
    duplicate_count = int(df.duplicated().sum())

    missing_percent = missing_count / (row_count * column_count) * 100 if row_count and column_count else 0.0
    duplicate_percent = duplicate_count / row_count * 100 if row_count else 0.0
    data_health = max(0.0, 100 - missing_percent * 0.7 - duplicate_percent * 0.3)
    health_label = "Strong" if data_health >= 90 else "Review" if data_health >= 70 else "At risk"

    kpis = [
        ("Rows", f"{row_count:,}", "observations", "rows"),
        ("Columns", f"{column_count:,}", "fields in this dataset", "columns"),
        ("Missing %", f"{missing_percent:.1f}%", f"{missing_count:,} missing cells", "missing"),
        ("Duplicates", f"{duplicate_count:,}", f"{duplicate_percent:.1f}% of rows", "duplicates"),
        ("Data health", f"{data_health:.0f}%", health_label, "health"),
    ]
    for column, (label, value, detail, kind) in zip(st.columns(5, gap="medium"), kpis):
        column.markdown(
            f'<div class="quality-kpi quality-kpi-{kind}">'
            f'<div class="quality-kpi-label">{label}</div>'
            f'<div class="quality-kpi-value">{value}</div>'
            f'<div class="quality-kpi-detail">{detail}</div>'
            f'{f"<div class=\"quality-health-track\"><span style=\"width:{data_health:.1f}%\"></span></div>" if kind == "health" else ""}'
            '</div>',
            unsafe_allow_html=True,
        )

    # =================================================
    # MAIN TABS
    # =================================================
    profile_tab, missing_tab, duplicate_tab, outlier_tab = st.tabs(
        ["Profile", "Missing", "Duplicates", "Outliers"],
        key="quality_lab_tabs",
    )

    # =================================================
    # PROFILE TAB
    # =================================================
    with profile_tab:
        missing_by_column = df.isna().sum()

        completeness = (
            (1 - missing_by_column / row_count) * 100
            if row_count
            else pd.Series(100.0, index=df.columns)
        )

        # ---------------------------------------------
        # MISSINGNESS BY COLUMN
        # ---------------------------------------------
        st.markdown("### Missingness by columns")

        missing_chart = pd.DataFrame({
            "Column": df.columns,
            "Missingness (%)": [
                round(
                    df[column].isna().sum()
                    / max(row_count, 1)
                    * 100,
                    2,
                )
                for column in df.columns
            ],
        })

        missing_chart = (
            missing_chart[
                missing_chart["Missingness (%)"] > 0
            ]
            .sort_values(
                "Missingness (%)",
                ascending=True,
            )
        )

        if missing_chart.empty:
            st.success(
                "No missing values were found in the dataset."
            )
        else:
            # Scale to the observed maximum so the tallest bar fills the plot.
            axis_max = max(float(missing_chart["Missingness (%)"].max()) * 1.10, 0.1)
            fig = px.bar(
                missing_chart,
                x="Missingness (%)",
                y="Column",
                orientation="h",
                range_x=[0, axis_max],
                text="Missingness (%)",
                labels={
                    "Missingness (%)": "Missing values (%)",
                    "Column": "Column",
                },
                title="Percentage of missing values by column",
            )

            fig.update_traces(
                texttemplate="%{text:.2f}%",
                textposition="inside",
                insidetextanchor="end",
                textfont=dict(color="#FFFFFF", size=12),
                cliponaxis=False,
            )

            fig.update_layout(
                xaxis=dict(
                    range=[0, axis_max],
                    ticksuffix="%",
                    title="Missing values (%)",
                    dtick=axis_max / 4,
                    gridcolor="#E8EDF5",
                    zerolinecolor="#D7E0ED",
                ),
                yaxis=dict(
                    title="",
                    automargin=True,
                ),
                showlegend=False,
                margin=dict(l=10, r=20, t=60, b=10),
            )

            st.plotly_chart(
                fig,
                width="stretch",
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
            correlation_matrix = numeric_df.corr(
                method="pearson"
            )

            pairs = []

            for i, column_a in enumerate(
                correlation_matrix.columns
            ):
                for column_b in correlation_matrix.columns[
                    i + 1:
                ]:
                    correlation = correlation_matrix.loc[
                        column_a,
                        column_b,
                    ]

                    if pd.notna(correlation):
                        pairs.append({
                            "Feature_A": column_a,
                            "Feature_B": column_b,
                            "Correlation": round(
                                float(correlation),
                                3,
                            ),
                            "Absolute correlation": abs(
                                float(correlation)
                            ),
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
                    chart_data.set_index("Pair")[
                        ["Correlation"]
                    ],
                    horizontal=True,
                    width="stretch",
                )

                st.dataframe(
                    correlation_profile[
                        [
                            "Feature_A",
                            "Feature_B",
                            "Correlation",
                        ]
                    ],
                    width="stretch",
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
                    / max(row_count, 1)
                    * 100,
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
            width="stretch",
            hide_index=True,
        )

        st.divider()

        # ---------------------------------------------
        # NUMERIC AND CATEGORICAL PROFILE TABS
        # ---------------------------------------------
        with st.expander("Numeric profile", expanded=True):
            st.markdown("#### Numeric column profile")

            numeric_columns = df.select_dtypes(
                include="number"
            ).columns.tolist()

            if not numeric_columns:
                st.info("No numeric columns were detected.")
            else:
                numeric_summary = (
                    df[numeric_columns]
                    .describe()
                    .T
                    .reset_index()
                    .rename(columns={"index": "Column"})
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
                    width="stretch",
                    hide_index=True,
                )

        with st.expander("Categorical profile", expanded=False):
            st.markdown("#### Categorical column profile")

            categorical_columns = df.select_dtypes(
                include=[
                    "object",
                    "string",
                    "category",
                    "bool",
                ]
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
                    width="stretch",
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
                    width="stretch",
                )

    # =================================================
    # MISSING VALUES TAB
    # =================================================
    with missing_tab:
        st.markdown("### Missing values")
        st.caption("See how much data is missing and which fields need attention.")

        total_cells = row_count * column_count
        missing_rate = missing_count / total_cells * 100 if total_cells else 0.0
        affected_columns = int(df.isna().any(axis=0).sum())
        complete_rows = int((~df.isna().any(axis=1)).sum()) if row_count else 0

        missing_kpis = st.columns(3)
        missing_kpis[0].metric("Missing %", f"{missing_rate:.2f}%", help="Missing cells divided by all cells in this dataset.")
        missing_kpis[1].metric("Fields affected", f"{affected_columns:,}")
        missing_kpis[2].metric("Complete records", f"{complete_rows:,}", help="Rows with no missing values in any field.")

        missing_records = []
        for column in df.columns:
            count = int(df[column].isna().sum())
            if count:
                missing_records.append({
                    "Column": str(column),
                    "Missing %": round(count / max(row_count, 1) * 100, 2),
                    "Missing values": count,
                    "Present values": row_count - count,
                })

        if not missing_records:
            st.success("This dataset has no missing values.")
        else:
            missing_table = pd.DataFrame(missing_records).sort_values(
                "Missing %", ascending=False
            )
            chart_column, table_column = st.columns([1.15, 1], gap="large")
            with chart_column:
                axis_max = max(float(missing_table["Missing %"].max()) * 1.10, 0.1)
                missing_chart = px.bar(
                    missing_table.sort_values("Missing %"),
                    x="Missing %",
                    y="Column",
                    orientation="h",
                    range_x=[0, axis_max],
                    text="Missing %",
                    title="Missing share by field",
                    color_discrete_sequence=["#356AE6"],
                )
                missing_chart.update_traces(
                    texttemplate="%{text:.1f}%", textposition="inside",
                    insidetextanchor="end", textfont=dict(color="#FFFFFF", size=12),
                    cliponaxis=False,
                )
                missing_chart.update_layout(
                    template="plotly_white",
                    height=max(300, min(520, 42 * len(missing_table) + 100)),
                    margin=dict(l=10, r=45, t=55, b=20),
                    xaxis=dict(
                        range=[0, axis_max], ticksuffix="%", title="Missing values",
                        dtick=axis_max / 4, gridcolor="#E8EDF5", zerolinecolor="#D7E0ED",
                    ),
                    yaxis_title="",
                    showlegend=False,
                )
                st.plotly_chart(missing_chart, width="stretch", config={"displaylogo": False})
            with table_column:
                st.dataframe(missing_table, width="stretch", hide_index=True)

    # =================================================
    # DUPLICATES TAB
    # =================================================
    with duplicate_tab:
        st.markdown("### Duplicate records")
        st.caption("Exact row matches are detected across all columns. Review them before removing anything.")

        duplicate_rate = duplicate_count / max(row_count, 1) * 100
        dup_kpis = st.columns(2)
        dup_kpis[0].metric("Duplicate rate", f"{duplicate_rate:.2f}%")
        dup_kpis[1].metric("Additional duplicate rows", f"{duplicate_count:,}", help="Rows that would be removed by keeping the first copy.")

        duplicate_mask = df.duplicated(keep=False)
        repeated_records = df.loc[duplicate_mask]
        if repeated_records.empty:
            st.success("No exact duplicate records were found.")
        else:
            st.info(f"{len(repeated_records):,} records belong to duplicate groups. The table includes the first copy and each repeated copy.")
            st.dataframe(repeated_records.head(500), width="stretch", hide_index=True)
            if len(repeated_records) > 500:
                st.caption("Showing the first 500 records in duplicate groups.")
            st.download_button(
                "Download duplicate records (CSV)",
                data=repeated_records.to_csv(index=False).encode("utf-8-sig"),
                file_name="datalify_duplicate_records.csv",
                mime="text/csv",
                width="content",
                key="quality_download_duplicates",
            )
            if st.button(
                "Remove duplicate rows",
                type="primary",
                icon=":material/delete_sweep:",
                key="quality_remove_duplicates",
            ):
                cleaned_df = df.drop_duplicates().reset_index(drop=True)
                removed_count = len(df) - len(cleaned_df)
                if removed_count:
                    st.session_state.prepare_history.append(df.copy(deep=True))
                    st.session_state.working_df = cleaned_df
                    recipe_entry = {
                        "description": f"Remove {removed_count} duplicate rows from Quality Lab",
                        "timestamp": datetime.now().isoformat(timespec="seconds"),
                        "python_code": "df = df.drop_duplicates().reset_index(drop=True)",
                    }
                    recipe = st.session_state.prepare_recipe
                    if (any(not item.get("python_code") for item in recipe)
                            and not any(item.get("python_baseline_csv") for item in recipe)):
                        recipe_entry["python_baseline_csv"] = base64.b64encode(
                            df.to_csv(index=False).encode("utf-8")
                        ).decode("ascii")
                    recipe.append(recipe_entry)
                    st.session_state.prepare_updated_at = datetime.now().strftime(
                        "%Y-%m-%d %H:%M"
                    )
                    st.rerun()

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

            outlier_table = (
                outlier_table
                .sort_values(
                    "outlier_percent",
                    ascending=False,
                )
                .reset_index(drop=True)
            )

            st.markdown(
                "#### IQR outlier rate by numeric column"
            )

            st.dataframe(
                outlier_table,
                width="stretch",
                hide_index=True,
            )

            st.markdown("#### Outlier rate comparison")

            st.bar_chart(
                outlier_table.set_index("column")[
                    ["outlier_percent"]
                ],
                horizontal=True,
                width="stretch",
            )

            csv_data = outlier_table.to_csv(
                index=False
            ).encode("utf-8")

            st.download_button(
                "Download outlier report",
                data=csv_data,
                file_name="datalify_outlier_report.csv",
                mime="text/csv",
                width="content",
            )
