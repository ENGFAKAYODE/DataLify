
import base64
import json
from datetime import datetime

import pandas as pd
import streamlit as st


# =========================================================
# DESIGN SYSTEM
# =========================================================

def prepare_styles():
    st.markdown(
        """
        <style>
        /* Keep Streamlit's theme token and every primary Prepare action on-brand. */
        body .stApp {
            --st-primary-color: #356AE6 !important;
        }
        body .stApp button[kind*="primary"],
        body .stApp button[data-testid*="BaseButton-primary"],
        body .stApp [data-testid*="BaseButton-primary"] {
            background-color: #356AE6 !important;
            background-image: none !important;
            border-color: #356AE6 !important;
        }
        body .stApp button[kind*="primary"]:hover,
        body .stApp button[data-testid*="BaseButton-primary"]:hover,
        body .stApp [data-testid*="BaseButton-primary"]:hover {
            background-color: #2454C6 !important;
            border-color: #2454C6 !important;
        }

        /* Main page */
        .prep-hero {
            padding: 8px 0 20px 0;
        }

        .prep-eyebrow {
            color: #168B77;
            font-size: 0.72rem;
            font-weight: 800;
            letter-spacing: 2px;
            text-transform: uppercase;
            margin-bottom: 8px;
        }

        .prep-title {
            font-size: 2rem;
            font-weight: 800;
            letter-spacing: -1px;
            line-height: 1.15;
            margin-bottom: 8px;
            color: #17243B;
        }

        .prep-description {
            color: #64748B;
            font-size: 0.94rem;
            line-height: 1.6;
            max-width: 760px;
        }

        /* Summary cards */
        .prep-card {
            background: #FFFFFF;
            border: 1px solid #E3EAF4;
            border-radius: 16px;
            padding: 19px 20px;
            min-height: 122px;
            box-shadow: 0 8px 28px rgba(20, 41, 78, 0.045);
        }

        .prep-card-label {
            font-size: 0.76rem;
            font-weight: 650;
            color: #718096;
            margin-bottom: 12px;
        }

        .prep-card-value {
            font-size: 2rem;
            line-height: 1;
            font-weight: 800;
            letter-spacing: -1px;
            color: #17243B;
        }

        .prep-card-detail {
            font-size: 0.75rem;
            color: #718096;
            margin-top: 9px;
        }

        .prep-green-indicator {
            display: inline-flex;
            align-items: center;
            gap: 5px;
            margin-top: 9px;
            padding: 5px 9px;
            border-radius: 7px;
            background: #E5F7F2;
            color: #127A68;
            font-size: 0.73rem;
            font-weight: 750;
        }

        /* Working copy status */
        .prep-status {
            padding: 13px 15px;
            margin: 12px 0 17px 0;
            border: 1px solid #E3EAF4;
            border-radius: 12px;
            background: #FFFFFF;
            font-size: 0.81rem;
            color: #52617A;
        }

        /* Section headings */
        .prep-section-heading {
            font-size: 1.02rem;
            font-weight: 750;
            letter-spacing: -0.2px;
            margin-bottom: 4px;
        }

        .prep-section-caption {
            color: #718096;
            font-size: 0.78rem;
            margin-bottom: 14px;
        }

        .prep-subheading {
            font-size: 0.9rem;
            font-weight: 750;
            margin-bottom: 5px;
        }

        .prep-divider {
            height: 1px;
            background: #E3EAF4;
            margin: 22px 0;
        }

        /* Task button area */
        .prep-task-caption {
            font-size: 0.78rem;
            color: var(--text-color);
            opacity: 0.62;
            margin-bottom: 10px;
        }

        /* This page injects its own styles after the app theme; keep blue actions legible. */
        body .stApp [data-testid="stButton"] button[kind*="primary"],
        body .stApp [data-testid="stButton"] button[data-testid*="BaseButton-primary"],
        body .stApp [data-testid="stFormSubmitButton"] button[kind*="primary"],
        body .stApp [data-testid="stFormSubmitButton"] button[data-testid*="BaseButton-primary"],
        body .stApp [data-testid="stFormSubmitButton"] [data-testid*="BaseButton-primary"] {
            background: #356AE6 !important;
            border-color: #356AE6 !important;
        }
        body .stApp [data-testid="stButton"] button[kind*="primary"]:hover,
        body .stApp [data-testid="stButton"] button[data-testid*="BaseButton-primary"]:hover,
        body .stApp [data-testid="stFormSubmitButton"] button[kind*="primary"]:hover,
        body .stApp [data-testid="stFormSubmitButton"] button[data-testid*="BaseButton-primary"]:hover,
        body .stApp [data-testid="stFormSubmitButton"] [data-testid*="BaseButton-primary"]:hover {
            background: #2454C6 !important;
            border-color: #2454C6 !important;
        }
        [data-testid="stFormSubmitButton"] button[kind*="primary"],
        [data-testid="stFormSubmitButton"] button[data-testid*="BaseButton-primary"],
        [data-testid="stFormSubmitButton"] [data-testid*="BaseButton-primary"] {
            color: #FFFFFF !important;
            -webkit-text-fill-color: #FFFFFF !important;
        }
        [data-testid="stFormSubmitButton"] button[kind*="primary"] *,
        [data-testid="stFormSubmitButton"] button[data-testid*="BaseButton-primary"] *,
        [data-testid="stFormSubmitButton"] [data-testid*="BaseButton-primary"] * {
            color: #FFFFFF !important;
            -webkit-text-fill-color: #FFFFFF !important;
            fill: #FFFFFF !important;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# DATA HELPERS
# =========================================================

def quality_metrics(df):
    rows, columns = df.shape
    total_cells = rows * columns

    missing = int(df.isna().sum().sum())
    duplicates = int(df.duplicated().sum())

    completeness = (
        (total_cells - missing) / total_cells * 100
        if total_cells else 100.0
    )

    return {
        "Rows": rows,
        "Columns": columns,
        "Missing cells": missing,
        "Duplicate rows": duplicates,
        "Completeness %": round(completeness, 2),
    }


def get_numeric_columns(df):
    return df.select_dtypes(include="number").columns.tolist()


def initialize_prepare_state():
    defaults = {
        "prepare_history": [],
        "prepare_recipe": [],
        "prepare_updated_at": None,
        "wrangle_active_task": "Filter rows",
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def record_transformation(new_df, description, python_code=None):
    """Save the previous dataset and record one transformation."""

    previous_df = st.session_state.working_df.copy(deep=True)
    st.session_state.prepare_history.append(
        previous_df
    )

    st.session_state.working_df = new_df.copy(deep=True)

    recipe_entry = {
        "description": description,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
    }
    if python_code:
        recipe_entry["python_code"] = python_code
        existing_recipe = st.session_state.prepare_recipe
        if (any(not item.get("python_code") for item in existing_recipe)
                and not any(item.get("python_baseline_csv") for item in existing_recipe)):
            recipe_entry["python_baseline_csv"] = base64.b64encode(
                previous_df.to_csv(index=False).encode("utf-8")
            ).decode("ascii")
    st.session_state.prepare_recipe.append(recipe_entry)

    st.session_state.prepare_updated_at = datetime.now().strftime(
        "%Y-%m-%d %H:%M"
    )


# =========================================================
# SUMMARY COMPONENTS
# =========================================================

def render_summary(original_df, working_df):
    recipe = st.session_state.prepare_recipe
    history = st.session_state.prepare_history

    quality = quality_metrics(working_df)

    st.markdown("### Dataset summary")

    st.caption(f"Working copy: {len(working_df):,} rows, {len(working_df.columns):,} fields")

    transform_col, quality_col, action_col = st.columns(
        [1.05, 1.05, 1.4],
        gap="medium",
    )

    with transform_col:
        st.markdown(
            f"""
            <div class="prep-card">
                <div class="prep-card-label">TRANSFORMATIONS</div>
                <div class="prep-card-value">{len(recipe):,}</div>
                <div class="prep-green-indicator">
                    ↑ {len(recipe)} applied
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with quality_col:
        st.markdown(
            f"""
            <div class="prep-card">
                <div class="prep-card-label">COMPLETENESS</div>
                <div class="prep-card-value">
                    {quality["Completeness %"]:.1f}%
                </div>
                <div class="prep-card-detail">
                    Complete cells
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with action_col:
        st.markdown("<div style='height:5px'></div>", unsafe_allow_html=True)

        undo_col, reset_col = st.columns(2)

        with undo_col:
            if st.button(
                "↶ Undo",
                disabled=not history,
                width="stretch",
                key="prepare_undo",
            ):
                st.session_state.working_df = (
                    st.session_state.prepare_history.pop()
                )

                if st.session_state.prepare_recipe:
                    st.session_state.prepare_recipe.pop()

                st.session_state.prepare_updated_at = (
                    datetime.now().strftime("%Y-%m-%d %H:%M")
                )
                st.rerun()

        with reset_col:
            if st.button(
                "Reset all",
                disabled=not recipe,
                width="stretch",
                key="prepare_reset",
            ):
                st.session_state.working_df = (
                    original_df.copy(deep=True)
                )
                st.session_state.prepare_history = []
                st.session_state.prepare_recipe = []
                st.session_state.prepare_updated_at = (
                    datetime.now().strftime("%Y-%m-%d %H:%M")
                )
                st.rerun()

        recipe_data = {
            "dataset": st.session_state.get(
                "dataset_name", "dataset"
            ),
            "transformations": recipe,
            "business_kpis": st.session_state.get("business_kpis", []),
            "exported_at": datetime.now().isoformat(),
        }

        st.download_button(
            "↓ Export recipe",
            data=json.dumps(recipe_data, indent=4),
            file_name="datalify_transformation_recipe.json",
            mime="application/json",
            width="stretch",
            key="prepare_export",
        )

    updated_at = st.session_state.prepare_updated_at or "None"

    st.markdown(
        f"""
        <div class="prep-status">
            Last updated {updated_at}
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.expander("Before-and-after quality validation"):
        before = quality_metrics(original_df)
        after = quality_metrics(working_df)

        rows = []

        for metric in before:
            old = before[metric]
            new = after[metric]
            change = new - old

            if metric == "Completeness %":
                old_display = f"{old:.2f}%"
                new_display = f"{new:.2f}%"
                change_display = f"{change:+.2f}%"
            else:
                old_display = f"{old:,}"
                new_display = f"{new:,}"
                change_display = f"{change:+,}"

            rows.append({
                "Metric": metric,
                "Before": old_display,
                "After": new_display,
                "Change": change_display,
            })

        st.dataframe(
            pd.DataFrame(rows),
            width="stretch",
            hide_index=True,
        )


# =========================================================
# CLEAN: MISSING VALUES
# =========================================================

def render_missing_values(df):
    st.markdown(
        '<div class="prep-subheading">Missing Values</div>',
        unsafe_allow_html=True,
    )

    missing_counts = df.isna().sum()
    missing_counts = missing_counts[missing_counts > 0]

    if missing_counts.empty:
        st.success("No missing values detected.")
        return

    st.metric(
        "Missing cells",
        f"{int(missing_counts.sum()):,}",
    )

    missing_table = (
        missing_counts.rename("Missing values")
        .reset_index()
        .rename(columns={"index": "Field"})
        .sort_values("Missing values", ascending=False)
    )

    st.dataframe(
        missing_table,
        width="stretch",
        hide_index=True,
        height=150,
    )

    with st.form("missing_values_form"):
        st.markdown("**Fields to clean**")

        selected_fields = st.multiselect(
            " ",
            options=missing_counts.index.tolist(),
            default=missing_counts.index.tolist(),
            key="clean_missing_fields",
            label_visibility="collapsed",
        )

        st.markdown("**Treatment**")

        strategy = st.selectbox(
            " ",
            [
                "Fill with a constant",
                "Fill with mean",
                "Fill with median",
                "Fill with mode",
                "Remove rows with missing values",
            ],
            key="clean_missing_strategy",
            label_visibility="collapsed",
        )

        constant_value = None

        if strategy == "Fill with a constant":
            constant_value = st.text_input(
                "Replacement value",
                value="Unknown",
            )

        submitted = st.form_submit_button(
            "Apply treatment",
            type="primary",
            width="stretch",
        )

    if submitted:
        if not selected_fields:
            st.warning("Select at least one field.")
            return

        result = df.copy(deep=True)

        try:
            if strategy == "Remove rows with missing values":
                result = result.dropna(subset=selected_fields)

            else:
                for column in selected_fields:
                    series = result[column]

                    if strategy == "Fill with mean":
                        if not pd.api.types.is_numeric_dtype(series):
                            continue
                        value = series.mean()

                    elif strategy == "Fill with median":
                        if not pd.api.types.is_numeric_dtype(series):
                            continue
                        value = series.median()

                    elif strategy == "Fill with mode":
                        modes = series.mode(dropna=True)
                        value = modes.iloc[0] if not modes.empty else None

                    else:
                        value = constant_value

                    if value is not None and not pd.isna(value):
                        result[column] = series.fillna(value)

            if result.equals(df):
                st.info("No changes were necessary.")
            else:
                record_transformation(
                    result,
                    f"{strategy} on {', '.join(selected_fields)}",
                    python_code=(
                        f"df = df.dropna(subset={selected_fields!r})"
                        if strategy == "Remove rows with missing values"
                        else "for column in " + repr(selected_fields) + ":\n"
                        "    series = df[column]\n"
                        + ("    value = series.mean() if pd.api.types.is_numeric_dtype(series) else None\n"
                           if strategy == "Fill with mean" else
                           "    value = series.median() if pd.api.types.is_numeric_dtype(series) else None\n"
                           if strategy == "Fill with median" else
                           "    modes = series.mode(dropna=True)\n    value = modes.iloc[0] if not modes.empty else None\n"
                           if strategy == "Fill with mode" else
                           f"    value = {constant_value!r}\n")
                        + "    if value is not None and not pd.isna(value):\n"
                        "        df[column] = series.fillna(value)"
                    ),
                )
                st.success("Missing-value treatment applied.")
                st.rerun()

        except Exception as error:
            st.error(f"Could not apply treatment: {error}")


# =========================================================
# CLEAN: DUPLICATE RECORDS
# =========================================================

def render_duplicates(df):
    st.markdown(
        '<div class="prep-subheading">Duplicate Records</div>',
        unsafe_allow_html=True,
    )

    duplicate_count = int(df.duplicated().sum())

    st.metric(
        "Exact duplicate rows detected",
        f"{duplicate_count:,}",
    )

    if duplicate_count == 0:
        st.success("No exact duplicate rows detected.")
        return

    with st.form("duplicate_records_form"):
        st.markdown("**Fields that define a duplicate**")

        duplicate_fields = st.multiselect(
            " ",
            options=df.columns.tolist(),
            default=df.columns.tolist(),
            key="duplicate_fields",
            label_visibility="collapsed",
        )

        st.markdown("**Record to keep**")

        keep_record = st.selectbox(
            " ",
            ["First", "Last"],
            key="duplicate_keep",
            label_visibility="collapsed",
        )

        submitted = st.form_submit_button(
            "Remove duplicates",
            type="primary",
            width="stretch",
        )

    if submitted:
        if not duplicate_fields:
            st.warning("Choose at least one field.")
            return

        keep_value = "first" if keep_record == "First" else "last"

        result = df.drop_duplicates(
            subset=duplicate_fields,
            keep=keep_value,
        ).reset_index(drop=True)

        removed = len(df) - len(result)

        if removed:
            record_transformation(
                result,
                f"Remove {removed} duplicate records using "
                f"{', '.join(duplicate_fields)}; keep {keep_record}",
                python_code=f"df = df.drop_duplicates(subset={duplicate_fields!r}, keep={keep_value!r}).reset_index(drop=True)",
            )
            st.success(f"Removed {removed:,} duplicate records.")
            st.rerun()
        else:
            st.info("No duplicates found using those fields.")


# =========================================================
# CLEAN: FIELD TYPES
# =========================================================

def _parse_number_with_unit(series):
    """Parse numeric values followed by optional unit text, such as ``16 yrs``."""
    text = series.astype("string").str.strip()
    number_pattern = r"^([+-]?(?:\d[\d,]*\.?\d*|\.\d+))\s*[^\d.+-]*$"
    extracted = text.str.extract(number_pattern, expand=False)
    invalid = text.notna() & extracted.isna()
    if invalid.any():
        examples = ", ".join(repr(value) for value in text[invalid].head(3).tolist())
        raise ValueError(f"Could not find a leading number in: {examples}")
    # Keep genuinely missing values missing; non-missing unparseable strings
    # remain invalid so the caller can show a conversion error.
    extracted = extracted.where(text.notna(), pd.NA)
    extracted = extracted.str.replace(",", "", regex=False)
    return pd.to_numeric(extracted, errors="raise")

def render_field_types(df):
    st.markdown(
        '<div class="prep-subheading">Convert a Field Type</div>',
        unsafe_allow_html=True,
    )

    with st.form("field_type_form"):
        field = st.selectbox(
            "Field",
            df.columns.tolist(),
            key="type_field",
        )

        target_type = st.selectbox(
            "Convert to",
            ["Text", "Integer", "Decimal", "Currency", "Date", "Boolean"],
            key="type_target",
        )

        currency_code = None
        if target_type == "Currency":
            currency_code = st.text_input(
                "Currency code or symbol",
                value="USD",
                placeholder="For example USD, EUR, GBP, or NGN",
                help="Currency values are stored as numeric amounts; the chosen currency is recorded in the transformation history.",
                key="type_currency_code",
            )

        submitted = st.form_submit_button(
            "Apply field type",
            type="primary",
            width="stretch",
        )

    if submitted:
        result = df.copy(deep=True)

        try:
            if target_type == "Text":
                result[field] = result[field].astype("string")

            elif target_type == "Integer":
                result[field] = _parse_number_with_unit(result[field]).astype("Int64")

            elif target_type == "Decimal":
                result[field] = _parse_number_with_unit(result[field])

            elif target_type == "Currency":
                if not currency_code or not currency_code.strip():
                    st.error("Enter the currency code or symbol for this field.")
                    return

                raw_values = result[field].astype("string").str.strip()
                is_parenthesized_negative = raw_values.str.match(r"^\(.*\)$", na=False)
                amounts = raw_values.str.replace(r"[^0-9.+-]", "", regex=True)
                amounts = amounts.mask(is_parenthesized_negative, "-" + amounts)
                amounts = amounts.replace("", pd.NA)
                result[field] = pd.to_numeric(amounts, errors="raise")

            elif target_type == "Date":
                result[field] = pd.to_datetime(
                    result[field], errors="raise"
                )

            elif target_type == "Boolean":
                mapping = {
                    "true": True,
                    "false": False,
                    "1": True,
                    "0": False,
                    "yes": True,
                    "no": False,
                }

                result[field] = result[field].map(
                    lambda value: (
                        mapping.get(str(value).strip().lower())
                        if pd.notna(value) else None
                    )
                ).astype("boolean")

            if result.equals(df):
                st.info("The field already has this type.")
            else:
                if target_type == "Text":
                    type_code = f"df[{field!r}] = df[{field!r}].astype('string')"
                elif target_type in ("Integer", "Decimal"):
                    type_code = (
                        f"_text = df[{field!r}].astype('string').str.strip()\n"
                        "_number = _text.str.extract(r'^([+-]?(?:\\d[\\d,]*\\.?\\d*|\\.\\d+))\\s*[^\\d.+-]*$', expand=False)\n"
                        "_number = pd.to_numeric(_number.str.replace(',', '', regex=False), errors='raise')\n"
                        f"df[{field!r}] = _number.astype('Int64')"
                        if target_type == "Integer" else
                        f"_text = df[{field!r}].astype('string').str.strip()\n"
                        "_number = _text.str.extract(r'^([+-]?(?:\\d[\\d,]*\\.?\\d*|\\.\\d+))\\s*[^\\d.+-]*$', expand=False)\n"
                        f"df[{field!r}] = pd.to_numeric(_number.str.replace(',', '', regex=False), errors='raise')"
                    )
                elif target_type == "Currency":
                    type_code = (
                        f"_raw = df[{field!r}].astype('string').str.strip()\n"
                        "_negative = _raw.str.match(r'^\\(.*\\)$', na=False)\n"
                        "_amount = _raw.str.replace(r'[^0-9.+-]', '', regex=True)\n"
                        "_amount = _amount.mask(_negative, '-' + _amount).replace('', pd.NA)\n"
                        f"df[{field!r}] = pd.to_numeric(_amount, errors='raise')"
                    )
                elif target_type == "Date":
                    type_code = f"df[{field!r}] = pd.to_datetime(df[{field!r}], errors='raise')"
                else:
                    type_code = (
                        f"_mapping = {{'true': True, 'false': False, '1': True, '0': False, 'yes': True, 'no': False}}\n"
                        f"df[{field!r}] = df[{field!r}].map(lambda value: _mapping.get(str(value).strip().lower()) if pd.notna(value) else None).astype('boolean')"
                    )
                record_transformation(
                    result,
                    f"Convert {field} to {target_type}"
                    + (f" ({currency_code.strip()})" if target_type == "Currency" else ""),
                    python_code=type_code,
                )
                currency_suffix = f" ({currency_code.strip()})" if target_type == "Currency" else ""
                st.success(f"{field} converted to {target_type}{currency_suffix}.")
                st.rerun()

        except Exception as error:
            st.error(f"Conversion failed: {error}")


# =========================================================
# CLEAN: OUTLIERS
# =========================================================

def render_outliers(df):
    st.markdown(
        '<div class="prep-subheading">Treat Potential Outliers</div>',
        unsafe_allow_html=True,
    )

    numeric_columns = get_numeric_columns(df)

    if not numeric_columns:
        st.info("No numeric fields are available.")
        return

    with st.form("outlier_form"):
        field = st.selectbox(
            "Numeric field",
            numeric_columns,
            key="outlier_field",
        )

        treatment = st.selectbox(
            "Treatment",
            [
                "Cap values (winsorize)",
                "Remove rows outside IQR bounds",
            ],
            key="outlier_treatment",
        )

        sensitivity = st.slider(
            "IQR sensitivity",
            min_value=1.0,
            max_value=3.0,
            value=1.5,
            step=0.1,
            key="outlier_sensitivity",
        )

        submitted = st.form_submit_button(
            "Apply outlier treatment",
            type="primary",
            width="stretch",
        )

    series = pd.to_numeric(
        df[field], errors="coerce"
    ).dropna()

    if series.empty:
        st.info("No usable numeric values in this field.")
        return

    q1 = series.quantile(0.25)
    q3 = series.quantile(0.75)
    iqr = q3 - q1

    lower_bound = q1 - sensitivity * iqr
    upper_bound = q3 + sensitivity * iqr

    outlier_count = int(
        ((series < lower_bound) | (series > upper_bound)).sum()
    )

    st.caption(
        f"{outlier_count:,} potential outliers detected · "
        f"Lower: {lower_bound:,.2f} · Upper: {upper_bound:,.2f}"
    )

    if submitted:
        result = df.copy(deep=True)

        if treatment == "Cap values (winsorize)":
            result[field] = result[field].clip(
                lower=lower_bound,
                upper=upper_bound,
            )
        else:
            numeric_values = pd.to_numeric(
                result[field], errors="coerce"
            )

            keep_mask = (
                numeric_values.between(lower_bound, upper_bound)
                | numeric_values.isna()
            )

            result = result.loc[keep_mask].reset_index(drop=True)

        if result.equals(df):
            st.info("No changes were necessary.")
        else:
            record_transformation(
                result,
                f"{treatment} on {field}; IQR sensitivity {sensitivity}",
                python_code=(
                    f"_values = pd.to_numeric(df[{field!r}], errors='coerce').dropna()\n"
                    "_q1, _q3 = _values.quantile(.25), _values.quantile(.75)\n"
                    f"_lower, _upper = _q1 - {sensitivity!r} * (_q3 - _q1), _q3 + {sensitivity!r} * (_q3 - _q1)\n"
                    + (f"df[{field!r}] = df[{field!r}].clip(lower=_lower, upper=_upper)"
                       if treatment == "Cap values (winsorize)" else
                       f"_values = pd.to_numeric(df[{field!r}], errors='coerce')\n"
                       "df = df.loc[_values.between(_lower, _upper) | _values.isna()].reset_index(drop=True)")
                ),
            )
            st.success("Outlier treatment applied.")
            st.rerun()


# =========================================================
# CLEAN TAB
# =========================================================

def _clean_quality_metrics(data):
    rows = len(data)
    total_cells = rows * len(data.columns)
    missing = int(data.isna().sum().sum())
    duplicates = int(data.duplicated().sum())
    missing_percent = missing / total_cells * 100 if total_cells else 0
    duplicate_percent = duplicates / rows * 100 if rows else 0
    score = max(0, 100 - missing_percent * 0.7 - duplicate_percent * 0.3)
    return {
        "Rows": rows,
        "Missing values": missing,
        "Duplicate rows": duplicates,
        "Quality score": round(score, 2),
    }


def _build_quick_clean_preview(data, remove_duplicates, trim_whitespace, fill_missing, fill_strategy):
    result = data.copy(deep=True)
    if trim_whitespace:
        text_columns = result.select_dtypes(include=["object", "string"]).columns
        for column in text_columns:
            result[column] = result[column].map(
                lambda value: value.strip() if isinstance(value, str) else value
            )
    if fill_missing:
        for column in result.columns:
            series = result[column]
            if not series.isna().any():
                continue
            if fill_strategy == "Median" and pd.api.types.is_numeric_dtype(series):
                value = series.median()
            else:
                modes = series.mode(dropna=True)
                value = modes.iloc[0] if not modes.empty else None
            if value is not None and not pd.isna(value):
                result[column] = series.fillna(value)
    if remove_duplicates:
        result = result.drop_duplicates()
    return result.reset_index(drop=True)


_CLEAN_OPERATIONS = [
    "Remove", "Remove Other Columns", "Duplicate Column", "Remove Errors",
    "Change Type", "Transform", "Replace Values", "Replace Errors",
    "Split Column", "Fill", "Rename",
]
_TRANSFORM_OPERATIONS = [
    "lowercase", "UPPERCASE", "Capitalize Each Word", "Trim", "Clean",
    "Length", "JSON", "XML", "Extract",
]
_EXTRACT_OPERATIONS = [
    "By Delimiter", "By Number of Characters", "By Positions", "Length",
    "First Characters", "Last Characters", "Range", "Text Before Delimiter",
    "Text After Delimiter", "Text Between Delimiters",
]
_CLEAN_TYPES = [
    "Decimal Number", "Fixed decimal number", "Whole Number", "Percentage",
    "Date/Time", "Date", "Time", "Date/Time/Timezone", "Duration", "Text",
    "True/False", "Binary", "Using Locale ...",
]
_ERROR_TEXTS = ("#REF!", "#VALUE!", "#DIV/0!", "#N/A", "#NAME?", "#NUM!", "#NULL!")


def _is_error_value(value):
    return isinstance(value, str) and value.strip().upper() in _ERROR_TEXTS


def _apply_clean_type(series, target_type, locale_name="en-US", use_locale=False):
    if target_type == "Text":
        return series.astype("string")
    if target_type in ("Decimal Number", "Fixed decimal number", "Whole Number", "Percentage"):
        values = series.astype("string").str.strip()
        if target_type == "Percentage":
            has_percent = values.str.endswith("%", na=False)
            values = values.str.replace("%", "", regex=False)
            if use_locale:
                separators = {
                    "en-US": (",", "."), "en-GB": (",", "."),
                    "de-DE": (".", ","), "fr-FR": (" ", ","),
                    "es-ES": (".", ","), "it-IT": (".", ","),
                }
                thousands, decimal = separators[locale_name]
                if thousands:
                    values = values.str.replace(thousands, "", regex=False)
                if decimal != ".":
                    values = values.str.replace(decimal, ".", regex=False)
            numbers = pd.to_numeric(values, errors="raise")
            return numbers.where(~has_percent, numbers / 100)
        if use_locale:
            separators = {
                "en-US": (",", "."), "en-GB": (",", "."),
                "de-DE": (".", ","), "fr-FR": (" ", ","),
                "es-ES": (".", ","), "it-IT": (".", ","),
            }
            thousands, decimal = separators[locale_name]
            if thousands:
                values = values.str.replace(thousands, "", regex=False)
            if decimal != ".":
                values = values.str.replace(decimal, ".", regex=False)
        else:
            values = values.str.replace(",", "", regex=False)
        if target_type == "Fixed decimal number":
            from decimal import Decimal
            return values.map(lambda value: Decimal(str(value)) if pd.notna(value) else None)
        numbers = pd.to_numeric(values, errors="raise")
        if target_type == "Whole Number":
            return numbers.round().astype("Int64")
        return numbers
    if target_type in ("Date/Time", "Date", "Date/Time/Timezone"):
        dates = pd.to_datetime(
            series, errors="raise", utc=(target_type == "Date/Time/Timezone"),
            dayfirst=(use_locale and locale_name != "en-US" and target_type != "Date/Time/Timezone"),
        )
        if target_type == "Date":
            return dates.dt.date
        return dates
    if target_type == "Time":
        return pd.to_datetime(series, errors="raise").dt.time
    if target_type == "Duration":
        return pd.to_timedelta(series, errors="raise")
    if target_type == "True/False":
        mapping = {"true": True, "false": False, "1": True, "0": False, "yes": True, "no": False}
        converted = series.map(lambda value: mapping.get(str(value).strip().lower()) if pd.notna(value) else pd.NA)
        invalid = series.notna() & converted.isna()
        if invalid.any():
            raise ValueError("Values must be true/false, yes/no, or 1/0.")
        return converted.astype("boolean")
    if target_type == "Binary":
        return series.map(lambda value: str(value).encode("utf-8") if pd.notna(value) else None)
    raise ValueError(f"Unsupported type: {target_type}")


def _apply_text_transform(series, operation):
    text = series.astype("string")
    if operation == "lowercase":
        return text.str.lower()
    if operation == "UPPERCASE":
        return text.str.upper()
    if operation == "Capitalize Each Word":
        return text.str.title()
    if operation == "Trim":
        return text.str.strip()
    if operation == "Clean":
        return text.str.replace(r"[\x00-\x1f\x7f]", "", regex=True)
    if operation == "Length":
        return text.str.len().astype("Int64")
    if operation == "JSON":
        return series.map(lambda value: json.loads(value) if isinstance(value, str) and value.strip() else value)
    if operation == "XML":
        import xml.etree.ElementTree as ET
        return series.map(lambda value: ET.fromstring(value) if isinstance(value, str) and value.strip() else value)
    raise ValueError(f"Unsupported transform: {operation}")


def _apply_text_extract(series, method, params):
    text = series.astype("string")

    def extract(value):
        if pd.isna(value):
            return pd.NA
        if method == "By Delimiter":
            pieces = value.split(params["delimiter"])
            position = params["delimiter_position"]
            return pieces[position - 1] if position <= len(pieces) else ""
        if method == "By Number of Characters":
            count = params["character_count"]
            return value[:count] if params["character_side"] == "From start" else value[-count:] if count else ""
        if method == "By Positions":
            start = params["position_start"]
            return value[start:start + params["position_count"]]
        if method == "Length":
            return len(value)
        if method == "First Characters":
            return value[:params["character_count"]]
        if method == "Last Characters":
            count = params["character_count"]
            return value[-count:] if count else ""
        if method == "Range":
            start = params["range_start"] - 1
            return value[start:start + params["range_count"]]
        if method == "Text Before Delimiter":
            delimiter = params["delimiter"]
            return value.split(delimiter, 1)[0]
        if method == "Text After Delimiter":
            delimiter = params["delimiter"]
            return value.split(delimiter, 1)[1] if delimiter in value else ""
        if method == "Text Between Delimiters":
            start_delimiter = params["start_delimiter"]
            end_delimiter = params["end_delimiter"]
            start_at = value.find(start_delimiter)
            if start_at < 0:
                return ""
            start_at += len(start_delimiter)
            end_at = value.find(end_delimiter, start_at)
            return value[start_at:end_at] if end_at >= 0 else ""
        raise ValueError(f"Unsupported extract method: {method}")

    extracted = text.map(extract)
    return extracted.astype("Int64") if method == "Length" else extracted


def _perform_clean_operation(data, operation, params):
    result = data.copy(deep=True)
    column = params.get("column")
    if operation == "Remove":
        mode = params["remove_mode"]
        if mode == "Columns":
            return result.drop(columns=params["columns"])
        if mode == "Top Rows":
            return result.iloc[params["row_count"]:].reset_index(drop=True)
        if mode == "Bottom Rows":
            return result.iloc[:-params["row_count"] or None].reset_index(drop=True)
        if mode == "Blank Rows":
            return result.dropna(how="all").reset_index(drop=True)
        return result.drop_duplicates().reset_index(drop=True)
    if operation == "Remove Other Columns":
        return result[params["columns"]].copy()
    if operation == "Duplicate Column":
        new_name = params["new_name"].strip()
        if not new_name or new_name in result.columns:
            raise ValueError("Enter a new column name that is not already in use.")
        result[new_name] = result[column].copy()
        return result
    if operation in ("Remove Errors", "Replace Errors"):
        error_mask = result[column].map(_is_error_value)
        if operation == "Remove Errors":
            return result.loc[~error_mask].reset_index(drop=True)
        result.loc[error_mask, column] = params["replacement"]
        return result
    if operation == "Change Type":
        result[column] = _apply_clean_type(
            result[column], params["target_type"], params.get("locale", "en-US"),
            params.get("use_locale", False),
        )
        return result
    if operation == "Transform":
        if params.get("transform") == "Extract":
            result[column] = _apply_text_extract(
                result[column], params["extract_operation"], params,
            )
            return result
        result[column] = _apply_text_transform(result[column], params["transform"])
        return result
    if operation == "Replace Values":
        target = params["find_value"]
        replacement = params["replace_value"]
        result[column] = result[column].map(lambda value: replacement if pd.notna(value) and str(value) == target else value)
        return result
    if operation == "Split Column":
        delimiter = params["delimiter"]
        if not delimiter:
            raise ValueError("Enter a delimiter to split on.")
        parts = result[column].astype("string").str.split(delimiter, expand=True)
        names = [f"{column}.{index + 1}" for index in range(parts.shape[1])]
        conflicts = set(names) & (set(result.columns) - {column})
        if conflicts:
            raise ValueError(f"Split column names already exist: {', '.join(sorted(conflicts))}.")
        result = result.drop(columns=[column]).join(parts.set_axis(names, axis=1))
        return result
    if operation == "Fill":
        mode = params["fill_mode"]
        if mode == "Down":
            result[column] = result[column].ffill()
        elif mode == "Up":
            result[column] = result[column].bfill()
        else:
            result[column] = result[column].fillna(params["fill_value"])
        return result
    if operation == "Rename":
        new_name = params["new_name"].strip()
        if not new_name or (new_name in result.columns and new_name != column):
            raise ValueError("Enter a non-empty column name that is not already in use.")
        return result.rename(columns={column: new_name})
    raise ValueError(f"Unsupported operation: {operation}")


def _clean_operation_python_code(operation, params):
    """Return an equivalent pandas code block for the selected clean action."""
    column = params.get("column")
    quoted_column = repr(column)
    if operation == "Remove":
        mode = params["remove_mode"]
        if mode == "Columns":
            return f"df = df.drop(columns={params['columns']!r})"
        if mode == "Top Rows":
            return f"df = df.iloc[{params['row_count']}:].reset_index(drop=True)"
        if mode == "Bottom Rows":
            return f"df = df.iloc[:-{params['row_count']} or None].reset_index(drop=True)"
        if mode == "Blank Rows":
            return "df = df.dropna(how='all').reset_index(drop=True)"
    if operation == "Remove Other Columns":
        return f"df = df[{params['columns']!r}].copy()"
    if operation == "Duplicate Column":
        return f"df[{params['new_name'].strip()!r}] = df[{quoted_column}].copy()"
    if operation in ("Remove Errors", "Replace Errors"):
        errors = list(_ERROR_TEXTS)
        code = f"_error_mask = df[{quoted_column}].map(lambda value: isinstance(value, str) and value.strip().upper() in {errors!r})\n"
        if operation == "Remove Errors":
            return code + "df = df.loc[~_error_mask].reset_index(drop=True)"
        return code + f"df.loc[_error_mask, {quoted_column}] = {params['replacement']!r}"
    if operation == "Change Type":
        kind = params["target_type"]
        if kind == "Text":
            return f"df[{quoted_column}] = df[{quoted_column}].astype('string')"
        if kind in ("Decimal Number", "Fixed decimal number", "Whole Number", "Percentage"):
            locale = params.get("locale", "en-US")
            use_locale = params.get("use_locale", False)
            thousands, decimal = {"en-US": (",", "."), "en-GB": (",", "."), "de-DE": (".", ","), "fr-FR": (" ", ","), "es-ES": (".", ","), "it-IT": (".", ",")}.get(locale, (",", ".")) if use_locale else (",", ".")
            prep = f"_values = df[{quoted_column}].astype('string').str.strip()\n"
            if kind == "Percentage":
                prep += "_has_percent = _values.str.endswith('%', na=False)\n_values = _values.str.replace('%', '', regex=False)\n"
            if thousands:
                prep += f"_values = _values.str.replace({thousands!r}, '', regex=False)\n"
            if decimal != ".":
                prep += f"_values = _values.str.replace({decimal!r}, '.', regex=False)\n"
            if kind == "Fixed decimal number":
                prep += "from decimal import Decimal\ndf[" + quoted_column + "] = _values.map(lambda value: Decimal(str(value)) if pd.notna(value) else None)"
            else:
                prep += "_numbers = pd.to_numeric(_values, errors='raise')\n"
                if kind == "Percentage":
                    prep += "_numbers = _numbers.where(~_has_percent, _numbers / 100)\n"
                if kind == "Whole Number":
                    prep += "_numbers = _numbers.round().astype('Int64')\n"
                prep += f"df[{quoted_column}] = _numbers"
            return prep
        if kind in ("Date/Time", "Date", "Date/Time/Timezone"):
            return f"_dates = pd.to_datetime(df[{quoted_column}], errors='raise', utc={kind == 'Date/Time/Timezone'!r}, dayfirst={bool(params.get('use_locale') and params.get('locale') != 'en-US')!r})\n" + (f"df[{quoted_column}] = _dates.dt.date" if kind == "Date" else f"df[{quoted_column}] = _dates")
        if kind == "Time":
            return f"df[{quoted_column}] = pd.to_datetime(df[{quoted_column}], errors='raise').dt.time"
        if kind == "Duration":
            return f"df[{quoted_column}] = pd.to_timedelta(df[{quoted_column}], errors='raise')"
        if kind == "True/False":
            return f"_boolean_map = {{'true': True, 'false': False, '1': True, '0': False, 'yes': True, 'no': False}}\ndf[{quoted_column}] = df[{quoted_column}].map(lambda value: _boolean_map.get(str(value).strip().lower()) if pd.notna(value) else pd.NA).astype('boolean')"
        if kind == "Binary":
            return f"df[{quoted_column}] = df[{quoted_column}].map(lambda value: str(value).encode('utf-8') if pd.notna(value) else None)"
    if operation == "Transform":
        transform = params["transform"]
        if transform in ("lowercase", "UPPERCASE", "Capitalize Each Word", "Trim", "Length", "Clean"):
            method = {"lowercase": "lower", "UPPERCASE": "upper", "Capitalize Each Word": "title", "Trim": "strip", "Length": "len"}.get(transform)
            if method:
                return f"df[{quoted_column}] = df[{quoted_column}].astype('string').str.{method}()"
            return f"df[{quoted_column}] = df[{quoted_column}].astype('string').str.replace(r'[\\x00-\\x1f\\x7f]', '', regex=True)"
        if transform in ("JSON", "XML"):
            import_name = "json" if transform == "JSON" else "xml.etree.ElementTree as ET"
            parser = "json.loads" if transform == "JSON" else "ET.fromstring"
            return f"import {import_name}\ndf[{quoted_column}] = df[{quoted_column}].map(lambda value: {parser}(value) if isinstance(value, str) and value.strip() else value)"
        if transform == "Extract":
            method = params["extract_operation"]
            if method == "By Delimiter":
                expression = f".str.split({params['delimiter']!r}).str[{params['delimiter_position'] - 1}]"
            elif method == "By Number of Characters":
                count = params["character_count"]
                expression = f".str[:{count}]" if params["character_side"] == "From start" else f".str[-{count}:]" if count else ".str[:0]"
            elif method in ("First Characters", "Last Characters"):
                count = params["character_count"]
                expression = f".str[:{count}]" if method == "First Characters" else f".str[-{count}:]" if count else ".str[:0]"
            elif method == "By Positions":
                start, count = params["position_start"], params["position_count"]
                expression = f".str[{start}:{start + count}]"
            elif method == "Range":
                start, count = params["range_start"] - 1, params["range_count"]
                expression = f".str[{start}:{start + count}]"
            elif method == "Length":
                expression = ".str.len().astype('Int64')"
            elif method == "Text Before Delimiter":
                expression = f".str.split({params['delimiter']!r}, n=1).str[0]"
            elif method == "Text After Delimiter":
                expression = f".str.split({params['delimiter']!r}, n=1).str[1].fillna('')"
            else:
                start, end = params["start_delimiter"], params["end_delimiter"]
                return f"_text = df[{quoted_column}].astype('string')\ndf[{quoted_column}] = _text.map(lambda value: value[value.find({start!r}) + len({start!r}):value.find({end!r}, value.find({start!r}) + len({start!r}))] if pd.notna(value) and value.find({start!r}) >= 0 and value.find({end!r}, value.find({start!r}) + len({start!r})) >= 0 else '')"
            return f"df[{quoted_column}] = df[{quoted_column}].astype('string'){expression}"
    if operation == "Replace Values":
        return f"df[{quoted_column}] = df[{quoted_column}].map(lambda value: {params['replace_value']!r} if pd.notna(value) and str(value) == {params['find_value']!r} else value)"
    if operation == "Split Column":
        delimiter = params["delimiter"]
        return f"_parts = df[{quoted_column}].astype('string').str.split({delimiter!r}, expand=True)\n_names = [{column!r} + '.' + str(index + 1) for index in range(_parts.shape[1])]\ndf = df.drop(columns=[{column!r}]).join(_parts.set_axis(_names, axis=1))"
    if operation == "Fill":
        mode = params["fill_mode"]
        method = "ffill" if mode == "Down" else "bfill" if mode == "Up" else None
        return f"df[{quoted_column}] = df[{quoted_column}].{method}()" if method else f"df[{quoted_column}] = df[{quoted_column}].fillna({params['fill_value']!r})"
    if operation == "Rename":
        return f"df = df.rename(columns={{{quoted_column}: {params['new_name'].strip()!r}}})"
    raise ValueError(f"No Python export implementation for {operation}.")


def render_clean_operations(df):
    st.markdown("#### Column and row operations")
    operation = st.selectbox("Choose an operation", _CLEAN_OPERATIONS, key="clean_operation")
    transform = None
    extract_operation = None
    target_type = None
    if operation == "Transform":
        transform = st.selectbox("Transform", _TRANSFORM_OPERATIONS, key="clean_transform")
        if transform == "Extract":
            extract_operation = st.selectbox("Extract", _EXTRACT_OPERATIONS, key="clean_extract_operation")
    elif operation == "Change Type":
        target_type = st.selectbox("Change type to", _CLEAN_TYPES, key="clean_target_type")

    columns = df.columns.tolist()
    params = {}
    with st.form("clean_operation_form"):
        if operation == "Remove":
            params["remove_mode"] = st.selectbox("Remove", ["Columns", "Top Rows", "Bottom Rows", "Blank Rows"], key="clean_remove_mode")
            if params["remove_mode"] == "Columns":
                params["columns"] = st.multiselect("Columns to remove", columns, key="clean_remove_columns")
            elif params["remove_mode"] in ("Top Rows", "Bottom Rows"):
                params["row_count"] = st.number_input("Number of rows", min_value=1, max_value=max(1, len(df)), value=1, key="clean_remove_row_count")
        elif operation == "Remove Other Columns":
            params["columns"] = st.multiselect("Keep these columns", columns, key="clean_keep_columns")
        elif operation in ("Duplicate Column", "Change Type", "Transform", "Remove Errors", "Replace Errors", "Replace Values", "Split Column", "Fill", "Rename"):
            params["column"] = st.selectbox("Column", columns, key="clean_operation_column")
            if operation == "Duplicate Column":
                params["new_name"] = st.text_input("New column name", key="clean_duplicate_name")
            elif operation == "Rename":
                params["new_name"] = st.text_input("New column name", value=str(params["column"]), key="clean_rename_name")
            elif operation == "Change Type":
                params["target_type"] = target_type
                if target_type == "Using Locale ...":
                    params["use_locale"] = True
                    params["locale"] = st.selectbox("Locale", ["en-US", "en-GB", "de-DE", "fr-FR", "es-ES", "it-IT"], key="clean_type_locale")
                    params["target_type"] = st.selectbox(
                        "Data type",
                        ["Decimal Number", "Fixed decimal number", "Whole Number", "Percentage", "Date/Time", "Date"],
                        key="clean_type_locale_target",
                    )
            elif operation == "Transform":
                params["transform"] = transform
                if transform == "Extract":
                    params["extract_operation"] = extract_operation
                    if extract_operation == "By Delimiter":
                        params["delimiter"] = st.text_input("Delimiter", key="clean_extract_delimiter")
                        params["delimiter_position"] = st.number_input("Delimited section number", min_value=1, value=1, key="clean_extract_delimiter_position")
                    elif extract_operation == "By Number of Characters":
                        params["character_count"] = st.number_input("Number of characters", min_value=0, value=1, key="clean_extract_character_count")
                        params["character_side"] = st.selectbox("Take characters from", ["From start", "From end"], key="clean_extract_character_side")
                    elif extract_operation == "By Positions":
                        params["position_start"] = st.number_input("Start position (0-based)", min_value=0, value=0, key="clean_extract_position_start")
                        params["position_count"] = st.number_input("Number of characters", min_value=0, value=1, key="clean_extract_position_count")
                    elif extract_operation in ("First Characters", "Last Characters"):
                        params["character_count"] = st.number_input("Number of characters", min_value=0, value=1, key="clean_extract_character_count")
                    elif extract_operation == "Range":
                        params["range_start"] = st.number_input("Start position (1-based)", min_value=1, value=1, key="clean_extract_range_start")
                        params["range_count"] = st.number_input("Number of characters", min_value=0, value=1, key="clean_extract_range_count")
                    elif extract_operation in ("Text Before Delimiter", "Text After Delimiter"):
                        params["delimiter"] = st.text_input("Delimiter", key="clean_extract_delimiter")
                    elif extract_operation == "Text Between Delimiters":
                        params["start_delimiter"] = st.text_input("Start delimiter", key="clean_extract_start_delimiter")
                        params["end_delimiter"] = st.text_input("End delimiter", key="clean_extract_end_delimiter")
            elif operation == "Replace Values":
                params["find_value"] = st.text_input("Value to find", key="clean_find_value")
                params["replace_value"] = st.text_input("Replace with", key="clean_replace_value")
            elif operation == "Replace Errors":
                params["replacement"] = st.text_input("Replace errors with", key="clean_replace_errors")
            elif operation == "Split Column":
                params["delimiter"] = st.text_input("Delimiter", value=",", key="clean_split_delimiter")
            elif operation == "Fill":
                params["fill_mode"] = st.selectbox("Fill", ["Down", "Up", "With a value"], key="clean_fill_mode")
                if params["fill_mode"] == "With a value":
                    params["fill_value"] = st.text_input("Value", key="clean_fill_value")
        submitted = st.form_submit_button(operation, type="primary", width="stretch")

    if submitted:
        try:
            if operation == "Remove Other Columns" and not params["columns"]:
                raise ValueError("Choose at least one column to keep.")
            if operation == "Remove" and params["remove_mode"] == "Columns" and not params["columns"]:
                raise ValueError("Choose at least one column to remove.")
            if operation == "Remove" and params["remove_mode"] == "Columns" and len(params["columns"]) == len(columns):
                raise ValueError("At least one column must remain in the dataset.")
            if operation == "Transform" and transform == "Extract":
                required_delimiters = {
                    "By Delimiter": ("delimiter",),
                    "Text Before Delimiter": ("delimiter",),
                    "Text After Delimiter": ("delimiter",),
                    "Text Between Delimiters": ("start_delimiter", "end_delimiter"),
                }.get(extract_operation, ())
                if any(not params[name] for name in required_delimiters):
                    raise ValueError("Enter all required delimiter values.")
            result = _perform_clean_operation(df, operation, params)
            if result.equals(df):
                st.info("No changes were necessary.")
            else:
                detail = (
                    extract_operation if operation == "Transform" and transform == "Extract"
                    else transform if operation == "Transform"
                    else target_type if operation == "Change Type"
                    else operation
                )
                record_transformation(
                    result,
                    f"{detail} — {params.get('column', '')}".rstrip(" —"),
                    python_code=_clean_operation_python_code(operation, params),
                )
                st.success(f"{detail} applied.")
                st.rerun()
        except Exception as error:
            st.error(f"Could not apply {operation.lower()}: {error}")


def render_clean_tab(df):
    st.markdown("### Clean your dataset")
    st.caption("Clean and transform rows or columns while keeping the original upload untouched.")

    render_clean_operations(df)

    st.divider()

    st.markdown("#### Quick cleanup preview")
    remove_duplicates = st.checkbox("Remove duplicate rows", value=True, key="clean_preview_duplicates")
    trim_whitespace = st.checkbox("Trim leading and trailing text whitespace", value=True, key="clean_preview_whitespace")
    fill_missing = st.checkbox("Fill missing values", value=False, key="clean_preview_missing")
    fill_strategy = st.selectbox(
        "Missing-value strategy", ["Median", "Mode"],
        help="Median fills numeric columns. Mode fills columns with their most frequent value. Columns without a suitable value are left unchanged.",
        key="clean_preview_fill_strategy",
    )

    current_df = st.session_state.working_df.copy(deep=True)
    preview_df = _build_quick_clean_preview(
        current_df, remove_duplicates, trim_whitespace, fill_missing, fill_strategy
    )
    before_metrics = _clean_quality_metrics(current_df)
    after_metrics = _clean_quality_metrics(preview_df)
    impact_table = pd.DataFrame({
        "Metric": ["Rows", "Missing values", "Duplicate rows", "Quality score"],
        "Before": [f"{before_metrics['Rows']:,}", f"{before_metrics['Missing values']:,}", f"{before_metrics['Duplicate rows']:,}", f"{before_metrics['Quality score']:.2f}%"],
        "After": [f"{after_metrics['Rows']:,}", f"{after_metrics['Missing values']:,}", f"{after_metrics['Duplicate rows']:,}", f"{after_metrics['Quality score']:.2f}%"],
    })
    st.dataframe(impact_table, width="stretch", hide_index=True)
    apply_col, reset_col = st.columns(2)
    with apply_col:
        if st.button("Apply cleanup", type="primary", width="stretch", key="apply_quality_cleanup"):
            if preview_df.equals(current_df):
                st.info("No cleanup changes to apply.")
            else:
                quick_cleanup_code = []
                if trim_whitespace:
                    quick_cleanup_code.extend([
                        "for column in df.select_dtypes(include=['object', 'string']).columns:",
                        "    df[column] = df[column].map(lambda value: value.strip() if isinstance(value, str) else value)",
                    ])
                if fill_missing:
                    quick_cleanup_code.extend([
                        "for column in df.columns:",
                        "    series = df[column]",
                        "    if not series.isna().any(): continue",
                        "    if " + repr(fill_strategy) + " == 'Median' and pd.api.types.is_numeric_dtype(series):",
                        "        value = series.median()",
                        "    else:",
                        "        modes = series.mode(dropna=True)",
                        "        value = modes.iloc[0] if not modes.empty else None",
                        "    if value is not None and not pd.isna(value): df[column] = series.fillna(value)",
                    ])
                if remove_duplicates:
                    quick_cleanup_code.append("df = df.drop_duplicates()")
                quick_cleanup_code.append("df = df.reset_index(drop=True)")
                record_transformation(
                    preview_df, "Apply quick cleanup",
                    python_code="\n".join(quick_cleanup_code),
                )
                st.success("Cleanup applied to the working dataset.")
                st.rerun()
    with reset_col:
        if st.button("Reset to original upload", width="stretch", key="reset_quality_cleanup"):
            original_df = st.session_state.get("original_df")
            if original_df is None:
                st.warning("The original upload is unavailable. Upload the dataset again to reset.")
            elif original_df.equals(current_df):
                st.info("The working dataset already matches the original upload.")
            else:
                record_transformation(
                    original_df, "Reset dataset to original upload",
                    python_code="df = original_df.copy(deep=True)",
                )
                st.success("Restored the original uploaded dataset.")
                st.rerun()
    with st.expander("Preview the first 20 rows after cleanup"):
        st.dataframe(preview_df.head(20), width="stretch", hide_index=True)

    st.divider()
    st.markdown("#### Targeted cleaning tools")
    missing_col, duplicate_col = st.columns(
        2,
        gap="large",
    )

    with missing_col:
        render_missing_values(df)

    with duplicate_col:
        render_duplicates(df)

    st.markdown('<div class="prep-divider"></div>', unsafe_allow_html=True)

    render_outliers(df)


# =========================================================
# WRANGLE: FILTER ROWS
# =========================================================

def render_filter_rows(df):
    st.markdown("#### Filter rows")
    st.caption("Keep only records that match your selected condition.")

    with st.form("filter_rows_form"):
        field = st.selectbox(
            "Field",
            df.columns.tolist(),
            key="filter_field",
        )

        condition = st.selectbox(
            "Condition",
            [
                "Equals",
                "Does not equal",
                "Contains",
                "Does not contain",
                "Greater than",
                "Greater than or equal to",
                "Less than",
                "Less than or equal to",
                "Is missing",
                "Is not missing",
            ],
            key="filter_condition",
        )

        value = st.text_input(
            "Value",
            key="filter_value",
            disabled=condition in ["Is missing", "Is not missing"],
        )

        submitted = st.form_submit_button(
            "Keep matching rows",
            type="primary",
            width="stretch",
        )

    if submitted:
        series = df[field]

        try:
            if condition == "Is missing":
                mask = series.isna()

            elif condition == "Is not missing":
                mask = series.notna()

            elif condition in [
                "Greater than",
                "Greater than or equal to",
                "Less than",
                "Less than or equal to",
            ]:
                numeric_series = pd.to_numeric(
                    series, errors="coerce"
                )
                numeric_value = float(value)

                if condition == "Greater than":
                    mask = numeric_series > numeric_value
                elif condition == "Greater than or equal to":
                    mask = numeric_series >= numeric_value
                elif condition == "Less than":
                    mask = numeric_series < numeric_value
                else:
                    mask = numeric_series <= numeric_value

            elif condition == "Equals":
                mask = series.astype(str) == value

            elif condition == "Does not equal":
                mask = series.astype(str) != value

            elif condition == "Contains":
                mask = series.astype(str).str.contains(
                    value, case=False, na=False
                )

            else:
                mask = ~series.astype(str).str.contains(
                    value, case=False, na=False
                )

            result = df.loc[mask].reset_index(drop=True)

            if result.equals(df):
                st.info("The filter did not change the dataset.")
            elif result.empty:
                st.warning(
                    "No records match this condition. "
                    "Your working dataset was not changed."
                )
            else:
                removed = len(df) - len(result)

                record_transformation(
                    result,
                    f"Filter rows: {field} {condition.lower()} {value}",
                    python_code=(
                        f"_series = df[{field!r}]\n"
                        + ("_mask = _series.isna()" if condition == "Is missing" else
                           "_mask = _series.notna()" if condition == "Is not missing" else
                           f"_numeric = pd.to_numeric(_series, errors='coerce')\n_mask = _numeric {'>' if condition == 'Greater than' else '>=' if condition == 'Greater than or equal to' else '<' if condition == 'Less than' else '<='} {float(value)!r}" if condition in ("Greater than", "Greater than or equal to", "Less than", "Less than or equal to") else
                           f"_mask = _series.astype(str) {'==' if condition == 'Equals' else '!='} {value!r}" if condition in ("Equals", "Does not equal") else
                           f"_mask = _series.astype(str).str.contains({value!r}, case=False, na=False)" if condition == "Contains" else
                           f"_mask = ~_series.astype(str).str.contains({value!r}, case=False, na=False)")
                        + "\ndf = df.loc[_mask].reset_index(drop=True)"
                    ),
                )

                st.success(
                    f"Kept {len(result):,} records and excluded {removed:,}."
                )
                st.rerun()

        except Exception as error:
            st.error(f"Could not apply filter: {error}")


# =========================================================
# WRANGLE: CALCULATED FIELD
# =========================================================

def render_calculated_field(df):
    st.markdown("#### Calculated field")
    st.caption("Create a new field using two existing numeric fields.")

    numeric_columns = get_numeric_columns(df)

    if not numeric_columns:
        st.info("No numeric fields are available.")
        return

    with st.form("calculated_field_form"):
        new_name = st.text_input(
            "New field name",
            placeholder="e.g. Total Amount",
        )

        calculation = st.selectbox(
            "Calculation",
            ["Add", "Subtract", "Multiply", "Divide"],
        )

        first_field = st.selectbox(
            "First field",
            numeric_columns,
            key="calc_first",
        )

        second_field = st.selectbox(
            "Second field",
            numeric_columns,
            key="calc_second",
        )

        submitted = st.form_submit_button(
            "Create calculated field",
            type="primary",
            width="stretch",
        )

    if submitted:
        if not new_name.strip():
            st.warning("Enter a name for the new field.")
            return

        if new_name in df.columns:
            st.warning("A field with that name already exists.")
            return

        result = df.copy(deep=True)

        a = pd.to_numeric(result[first_field], errors="coerce")
        b = pd.to_numeric(result[second_field], errors="coerce")

        if calculation == "Add":
            result[new_name] = a + b
        elif calculation == "Subtract":
            result[new_name] = a - b
        elif calculation == "Multiply":
            result[new_name] = a * b
        else:
            result[new_name] = a.div(b.replace(0, pd.NA))

        record_transformation(
            result,
            f"Create {new_name}: {first_field} {calculation} {second_field}",
            python_code=(
                f"_a = pd.to_numeric(df[{first_field!r}], errors='coerce')\n"
                f"_b = pd.to_numeric(df[{second_field!r}], errors='coerce')\n"
                f"df[{new_name.strip()!r}] = "
                + ("_a + _b" if calculation == "Add" else "_a - _b" if calculation == "Subtract" else "_a * _b" if calculation == "Multiply" else "_a.div(_b.replace(0, pd.NA))")
            ),
        )

        st.success(f"Created {new_name}.")
        st.rerun()


# =========================================================
# WRANGLE: GROUP & SUMMARIZE
# =========================================================

def render_group_summarize(df):
    st.markdown("#### Group & summarize")

    numeric_columns = get_numeric_columns(df)

    if not numeric_columns:
        st.info("No numeric fields are available.")
        return

    with st.form("group_summarize_form"):
        group_fields = st.multiselect(
            "Group by fields",
            df.columns.tolist(),
        )

        value_field = st.selectbox(
            "Numeric field to summarize",
            numeric_columns,
        )

        aggregation = st.selectbox(
            "Summary calculation",
            ["Sum", "Mean", "Median", "Count", "Minimum", "Maximum"],
        )

        submitted = st.form_submit_button(
            "Create summary",
            type="primary",
            width="stretch",
        )

    if submitted:
        if not group_fields:
            st.warning("Select at least one grouping field.")
            return

        functions = {
            "Sum": "sum",
            "Mean": "mean",
            "Median": "median",
            "Count": "count",
            "Minimum": "min",
            "Maximum": "max",
        }

        result = (
            df.groupby(group_fields, dropna=False)[value_field]
            .agg(functions[aggregation])
            .reset_index()
        )

        result = result.rename(
            columns={value_field: f"{aggregation} of {value_field}"}
        )

        record_transformation(
            result,
            f"Group by {', '.join(group_fields)}; "
            f"{aggregation} of {value_field}",
            python_code=(
                f"_functions = {{'Sum': 'sum', 'Mean': 'mean', 'Median': 'median', 'Count': 'count', 'Minimum': 'min', 'Maximum': 'max'}}\n"
                f"df = df.groupby({group_fields!r}, dropna=False)[{value_field!r}].agg(_functions[{aggregation!r}]).reset_index()\n"
                f"df = df.rename(columns={{{value_field!r}: {f'{aggregation} of {value_field}'!r}}})"
            ),
        )

        st.success("Grouped summary created.")
        st.rerun()


# =========================================================
# WRANGLE: PIVOT
# =========================================================

def render_pivot(df):
    st.markdown("#### Pivot")
    numeric_columns = get_numeric_columns(df)

    if not numeric_columns:
        st.info("A numeric field is required for pivot values.")
        return

    if len(df.columns) < 2:
        st.info("At least two fields are required.")
        return

    with st.form("pivot_form"):
        index_field = st.selectbox(
            "Rows (index)",
            df.columns.tolist(),
        )

        columns_field = st.selectbox(
            "Columns",
            [c for c in df.columns if c != index_field],
        )

        values_field = st.selectbox(
            "Values",
            numeric_columns,
        )

        aggregation = st.selectbox(
            "Aggregation",
            ["Sum", "Mean", "Count"],
        )

        submitted = st.form_submit_button(
            "Create pivot table",
            type="primary",
            width="stretch",
        )

    if submitted:
        functions = {
            "Sum": "sum",
            "Mean": "mean",
            "Count": "count",
        }

        try:
            result = pd.pivot_table(
                df,
                index=index_field,
                columns=columns_field,
                values=values_field,
                aggfunc=functions[aggregation],
            ).reset_index()

            result.columns.name = None

            record_transformation(
                result,
                f"Pivot {values_field} by {index_field} and {columns_field}",
                python_code=(
                    f"_functions = {{'Sum': 'sum', 'Mean': 'mean', 'Count': 'count'}}\n"
                    f"df = pd.pivot_table(df, index={index_field!r}, columns={columns_field!r}, values={values_field!r}, aggfunc=_functions[{aggregation!r}]).reset_index()\n"
                    "df.columns.name = None"
                ),
            )

            st.success("Pivot table created.")
            st.rerun()

        except Exception as error:
            st.error(f"Could not create pivot table: {error}")


# =========================================================
# WRANGLE: RESHAPE
# =========================================================

def render_reshape(df):
    st.markdown("#### Reshape")
    st.caption("Convert a wide dataset into a long-format dataset.")

    with st.form("reshape_form"):
        identifier_fields = st.multiselect(
            "Identifier fields to keep",
            df.columns.tolist(),
        )

        submitted = st.form_submit_button(
            "Reshape dataset",
            type="primary",
            width="stretch",
        )

    if submitted:
        if not identifier_fields:
            st.warning("Select at least one identifier field.")
            return

        value_fields = [
            column for column in df.columns
            if column not in identifier_fields
        ]

        if not value_fields:
            st.warning("No fields remain to reshape.")
            return

        result = pd.melt(
            df,
            id_vars=identifier_fields,
            value_vars=value_fields,
            var_name="Variable",
            value_name="Value",
        )

        record_transformation(
            result,
            f"Reshape wide to long; retain {', '.join(identifier_fields)}",
            python_code=(
                f"_id_fields = {identifier_fields!r}\n"
                "_value_fields = [column for column in df.columns if column not in _id_fields]\n"
                "df = pd.melt(df, id_vars=_id_fields, value_vars=_value_fields, var_name='Variable', value_name='Value')"
            ),
        )

        st.success("Dataset reshaped.")
        st.rerun()


# =========================================================
# WRANGLE TAB: TASK BUTTONS
# =========================================================

def render_wrangle_tab(df):
    tasks = [
        "Filter rows",
        "Calculated field",
        "Group & summarize",
        "Pivot",
        "Reshape",
    ]

    if (
        st.session_state.wrangle_active_task not in tasks
    ):
        st.session_state.wrangle_active_task = "Filter rows"

    st.markdown(
        '<div class="prep-section-heading">Wrangling task</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="prep-task-caption">'
        'Choose an operation to transform your working dataset.'
        '</div>',
        unsafe_allow_html=True,
    )

    # Separate task buttons, visually distinct from the main tabs.
    task_columns = st.columns(5, gap="small")

    for index, task in enumerate(tasks):
        with task_columns[index]:
            active = st.session_state.wrangle_active_task == task

            if st.button(
                task,
                key=f"wrangle_task_button_{index}",
                type="primary" if active else "secondary",
                width="stretch",
            ):
                st.session_state.wrangle_active_task = task
                st.rerun()

    st.markdown(
        '<div class="prep-divider"></div>',
        unsafe_allow_html=True,
    )

    selected_task = st.session_state.wrangle_active_task

    if selected_task == "Filter rows":
        render_filter_rows(df)

    elif selected_task == "Calculated field":
        render_calculated_field(df)

    elif selected_task == "Group & summarize":
        render_group_summarize(df)

    elif selected_task == "Pivot":
        render_pivot(df)

    elif selected_task == "Reshape":
        render_reshape(df)


# =========================================================
# COMBINE: JOIN
# =========================================================

def read_uploaded_dataset(uploaded_file):
    if uploaded_file.name.lower().endswith(".csv"):
        return pd.read_csv(uploaded_file)

    return pd.read_excel(uploaded_file)


def render_join(df):
    st.markdown("#### Join tables")
    st.caption(
        "Combine two datasets using matching fields."
    )

    uploaded_file = st.file_uploader(
        "Upload the second dataset",
        type=["csv", "xlsx", "xls"],
        key="join_upload",
    )

    if uploaded_file is None:
        st.info("Upload another dataset to configure a join.")
        return

    try:
        second_df = read_uploaded_dataset(uploaded_file)
    except Exception as error:
        st.error(f"Could not read the second dataset: {error}")
        return

    st.caption(
        f"Second dataset: {len(second_df):,} rows × "
        f"{len(second_df.columns):,} fields"
    )

    with st.form("join_form"):
        left_key = st.selectbox(
            "Field in working dataset",
            df.columns.tolist(),
        )

        right_key = st.selectbox(
            "Matching field in second dataset",
            second_df.columns.tolist(),
            index=(
                second_df.columns.tolist().index(left_key)
                if left_key in second_df.columns else 0
            ),
        )

        join_type = st.selectbox(
            "Join type",
            ["Left", "Inner", "Right", "Outer"],
        )

        submitted = st.form_submit_button(
            "Join datasets",
            type="primary",
            width="stretch",
        )

    if submitted:
        try:
            result = pd.merge(
                df,
                second_df,
                left_on=left_key,
                right_on=right_key,
                how=join_type.lower(),
                suffixes=("", "_joined"),
            )

            record_transformation(
                result,
                f"{join_type} join with {uploaded_file.name} "
                f"using {left_key} = {right_key}",
                python_code=(
                    "import base64, io\n"
                    f"_joined_csv = {base64.b64encode(second_df.to_csv(index=False).encode('utf-8')).decode('ascii')!r}\n"
                    "_joined_df = pd.read_csv(io.BytesIO(base64.b64decode(_joined_csv)))\n"
                    f"df = pd.merge(df, _joined_df, left_on={left_key!r}, right_on={right_key!r}, how={join_type.lower()!r}, suffixes=('', '_joined'))"
                ),
            )

            st.success(
                f"Join completed: {len(result):,} rows × "
                f"{len(result.columns):,} fields."
            )
            st.rerun()

        except Exception as error:
            st.error(f"Could not join datasets: {error}")


# =========================================================
# COMBINE: UNION
# =========================================================

def render_union(df):
    st.markdown("#### Union tables")
    st.caption(
        "Append records from another dataset to your working dataset."
    )

    uploaded_file = st.file_uploader(
        "Upload the dataset to append",
        type=["csv", "xlsx", "xls"],
        key="union_upload",
    )

    if uploaded_file is None:
        st.info("Upload another dataset to append its rows.")
        return

    try:
        second_df = read_uploaded_dataset(uploaded_file)
    except Exception as error:
        st.error(f"Could not read the second dataset: {error}")
        return

    shared_fields = [
        column for column in df.columns
        if column in second_df.columns
    ]

    st.metric(
        "Matching fields",
        f"{len(shared_fields)} / {len(df.columns)}",
    )

    include_all_columns = st.checkbox(
        "Keep fields from both datasets",
        value=True,
        key="union_all_columns",
        help="Retain unmatched fields and fill missing cells where needed.",
    )

    if st.button(
        "Union datasets",
        type="primary",
        width="stretch",
        key="union_apply",
    ):
        if not shared_fields:
            st.warning("The datasets have no matching field names.")
            return

        if include_all_columns:
            result = pd.concat(
                [df, second_df],
                ignore_index=True,
                sort=False,
            )
        else:
            result = pd.concat(
                [
                    df[shared_fields],
                    second_df[shared_fields],
                ],
                ignore_index=True,
            )

        record_transformation(
            result,
            f"Union with {uploaded_file.name}",
            python_code=(
                "import base64, io\n"
                f"_append_csv = {base64.b64encode(second_df.to_csv(index=False).encode('utf-8')).decode('ascii')!r}\n"
                "_append_df = pd.read_csv(io.BytesIO(base64.b64decode(_append_csv)))\n"
                + ("df = pd.concat([df, _append_df], ignore_index=True, sort=False)"
                   if include_all_columns else
                   f"_shared_fields = {[column for column in df.columns if column in second_df.columns]!r}\n"
                   "df = pd.concat([df[_shared_fields], _append_df[_shared_fields]], ignore_index=True)")
            ),
        )

        st.success(
            f"Union completed: {len(result):,} rows × "
            f"{len(result.columns):,} fields."
        )
        st.rerun()


# =========================================================
# COMBINE DATASETS TAB
# =========================================================

def render_combine_tab(df):
    join_col, union_col = st.columns(2, gap="large")

    with join_col:
        render_join(df)

    with union_col:
        render_union(df)


# =========================================================
# MAIN PREPARE PAGE
# =========================================================

def render_prepare():

    if st.session_state.get("working_df") is None:
        st.info(
            "No dataset is loaded. Open Data Intake to upload "
            "a CSV or Excel file."
        )
        return

    if st.session_state.get("original_df") is None:
        st.warning(
            "The original upload is unavailable. "
            "Please upload your dataset again."
        )
        return

    initialize_prepare_state()
    prepare_styles()

    original_df = st.session_state.original_df
    working_df = st.session_state.working_df

    # -----------------------------------------------------
    # HERO
    # -----------------------------------------------------

    st.markdown(
        """
        <div class="prep-hero">
            <div class="prep-eyebrow">Data preparation studio</div>
            <div class="prep-title">Clean, reshape, and combine.</div>
            <div class="prep-description">
                Turn raw data into analysis-ready data.
                Clean inconsistencies, reshape fields, and combine
                datasets while keeping your original upload untouched.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # -----------------------------------------------------
    # SUMMARY
    # -----------------------------------------------------

    render_summary(original_df, working_df)

    st.markdown(
        '<div class="prep-divider"></div>',
        unsafe_allow_html=True,
    )

    # -----------------------------------------------------
    # MAIN WORKSPACE TABS
    # -----------------------------------------------------

    clean_tab, wrangle_tab, combine_tab = st.tabs(
        ["Clean", "Wrangle", "Combine datasets"],
        key="prepare_workspace_tabs",
    )

    with clean_tab:
        render_clean_tab(st.session_state.working_df)

    with wrangle_tab:
        render_wrangle_tab(st.session_state.working_df)

    with combine_tab:
        render_combine_tab(st.session_state.working_df)
