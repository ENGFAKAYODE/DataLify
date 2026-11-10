"""Shared visual system for the Datalify Streamlit workspace."""

import streamlit as st


def load_styles() -> None:
    st.markdown(
        """
        <style>
        :root {
            --primary-color: #356AE6 !important;
            --st-primary-color: #356AE6 !important;
            --dl-ink: #17243B;
            --dl-muted: #64748B;
            --dl-blue: #356AE6;
            --dl-blue-dark: #2454C6;
            --dl-mint: #20B99A;
            --dl-line: #E3EAF4;
            --dl-surface: #FFFFFF;
            --dl-canvas: #F5F7FB;
            --dl-shadow: 0 8px 28px rgba(20, 41, 78, 0.055);
        }

        .stApp {
            --primary-color: #356AE6 !important;
            --st-primary-color: #356AE6 !important;
            background:
                radial-gradient(ellipse at 90% 0%, rgba(83, 126, 232, .075), transparent 32rem),
                var(--dl-canvas);
            color: var(--dl-ink);
            font-family: Inter, "Segoe UI", sans-serif;
        }
        [data-testid="stHeader"] { background: rgba(245, 247, 251, .84); }
        .block-container {
            max-width: 1500px;
            padding: 2rem clamp(1.25rem, 3vw, 3.25rem) 3rem;
        }
        h1, h2, h3, h4 { color: var(--dl-ink); letter-spacing: -.035em; }
        h1 { font-size: clamp(1.8rem, 3vw, 2.45rem) !important; font-weight: 760 !important; }
        h2 { font-size: 1.55rem !important; font-weight: 720 !important; }
        h3 { font-size: 1.12rem !important; font-weight: 700 !important; }
        p, li { color: #42516A; line-height: 1.65; }
        [data-testid="stCaptionContainer"] { color: var(--dl-muted); }

        /* Calm, persistent product navigation */
        [data-testid="stSidebar"] {
            background: linear-gradient(178deg, #14223C 0%, #1A2D4B 64%, #1A3450 100%);
            border-right: 1px solid rgba(220, 234, 255, .10);
        }
        [data-testid="stSidebar"],
        [data-testid="stSidebar"] > div,
        [data-testid="stSidebar"] > div > div,
        [data-testid="stSidebar"] [data-testid="stSidebarContent"],
        [data-testid="stSidebar"] [data-testid="stSidebarUserContent"] {
            overflow-y: hidden !important;
            overflow-x: hidden !important;
            scrollbar-width: none !important;
        }
        [data-testid="stSidebar"] [data-testid="stSidebarContent"] { padding: .12rem .9rem .55rem; }
        [data-testid="stSidebar"] [data-testid="stSidebarContent"]::-webkit-scrollbar { display: none !important; }
        [data-testid="stSidebar"] > div::-webkit-scrollbar,
        [data-testid="stSidebar"] > div > div::-webkit-scrollbar,
        [data-testid="stSidebar"] [data-testid="stSidebarContent"] *::-webkit-scrollbar { display: none !important; }
        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3,
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] label { color: #F1F5FC !important; }
        [data-testid="stSidebar"] [data-testid="stCaptionContainer"] { color: #AFC0D8 !important; }
        [data-testid="stSidebar"] [data-testid="stButton"] { margin: .08rem 0; }
        [data-testid="stSidebar"] [data-testid="stButton"] button {
            min-height: 2.42rem;
            padding: .36rem .78rem !important;
            border: 1px solid transparent !important;
            border-radius: 11px !important;
            background: transparent !important;
            color: #D3DEEF !important;
            box-shadow: none !important;
            justify-content: flex-start !important;
            transition: background .16s ease, border-color .16s ease, transform .16s ease;
        }
        [data-testid="stSidebar"] [data-testid="stButton"] button > div {
            display: flex !important; width: 100% !important; justify-content: flex-start !important;
            align-items: center !important; gap: .55rem;
        }
        [data-testid="stSidebar"] [data-testid="stButton"] button p,
        [data-testid="stSidebar"] [data-testid="stButton"] button span {
            color: inherit !important; font-weight: 570; text-align: left !important;
        }
        [data-testid="stSidebar"] [data-testid="stButton"] button p {
            flex: 1 1 auto; margin: 0 !important; text-align: left !important;
        }
        [data-testid="stSidebar"] [data-testid="stButton"] button:hover {
            background: rgba(255, 255, 255, .075) !important;
            border-color: rgba(255, 255, 255, .08) !important;
            transform: translateX(2px);
        }
        [data-testid="stSidebar"] [data-testid="stButton"] button[kind="primary"],
        [data-testid="stSidebar"] [data-testid="stButton"] [data-testid="stBaseButton-primary"] {
            background: linear-gradient(105deg, #315FC5, #264A98) !important;
            border-color: #6289E3 !important;
            color: #FFFFFF !important;
        }
        [data-testid="stSidebar"] [data-testid="stButton"] [data-testid="stBaseButton-primary"] *,
        [data-testid="stSidebar"] [data-testid="stButton"] button[kind="primary"] * { color: #FFFFFF !important; }
        .brand-mark {
            display: inline-flex; align-items: center; gap: .68rem;
            margin: .1rem 0 .25rem; color: #fff; font-size: 1.22rem;
            font-weight: 780; letter-spacing: -.035em;
        }
        .brand-glyph {
            display: inline-grid; place-items: center; width: 2rem; height: 2rem;
            border-radius: 10px; color: white; font-size: 1rem;
            background: linear-gradient(145deg, #5C8BFF, #20B99A);
            box-shadow: 0 5px 15px rgba(27, 102, 192, .35);
        }
        .brand-tagline { margin: .05rem 0 .9rem; color: #AFC0D8; font-size: .76rem; line-height: 1.5; }
        .sidebar-dataset {
            margin-top: 2rem; padding: .82rem; border-radius: 13px;
            border: 1px solid rgba(207, 225, 255, .13);
            background: rgba(255, 255, 255, .055);
        }
        .sidebar-dataset-label { margin-bottom: .35rem; color: #91A6C5; font-size: .65rem; font-weight: 750; letter-spacing: .12em; }
        .sidebar-dataset-name { overflow-wrap: anywhere; color: #F5F8FF; font-size: .83rem; font-weight: 650; }
        [data-testid="stSidebar"] .brand-mark { margin-top: -.12rem; }
        [data-testid="stSidebar"] [data-testid="stImage"] {
            margin: -.7rem 0 .25rem !important; transform: translateY(-5px);
        }
        [data-testid="stSidebar"] [data-testid="stImage"] img {
            display: block; width: 80% !important; max-width: 80% !important;
            margin: 0 auto !important;
        }

        .workspace-dataset-header {
            display: flex; align-items: center; gap: .85rem; margin: 0 0 1.65rem;
            padding: .82rem 1rem; border: 1px solid var(--dl-line); border-radius: 15px;
            background: rgba(255,255,255,.88); box-shadow: 0 4px 16px rgba(20,41,78,.035);
        }
        .workspace-dataset-mark {
            display: grid; flex: 0 0 2.45rem; place-items: center; width: 2.45rem; height: 2.45rem;
            border-radius: 11px; color: #2454C6; font-size: .9rem; font-weight: 800;
            background: linear-gradient(145deg, #E4ECFF, #E5F7F2);
        }
        .workspace-dataset-copy { min-width: 0; }
        .workspace-dataset-label { margin-bottom: .08rem; color: #7A899F; font-size: .62rem; font-weight: 770; letter-spacing: .12em; }
        .workspace-dataset-name { overflow-wrap: anywhere; color: #17243B; font-size: .98rem; font-weight: 780; letter-spacing: -.02em; }
        .workspace-dataset-details { margin-left: auto; color: #6A7890; font-size: .78rem; font-weight: 560; text-align: right; }

        /* Metrics and consistent card surfaces */
        [data-testid="stMetric"] {
            min-height: 112px; padding: 1.05rem 1.12rem;
            border: 1px solid var(--dl-line); border-radius: 16px;
            background: var(--dl-surface); box-shadow: var(--dl-shadow);
        }
        [data-testid="stMetricLabel"] { color: #687790; font-size: .78rem; font-weight: 650; }
        [data-testid="stMetricValue"] { color: var(--dl-ink); font-size: 1.7rem; font-weight: 760; letter-spacing: -.04em; }
        [data-testid="stMetricDelta"] { font-size: .76rem; }
        .quality-kpi {
            position: relative; min-height: 142px; height: 100%; overflow: hidden;
            padding: 1rem 1.05rem .9rem; border: 1px solid #DCE5F2; border-radius: 16px;
            background: #FFFFFF;
            box-shadow: 0 7px 20px rgba(24, 48, 87, .055);
        }
        .quality-kpi::before { content: none !important; }
        .quality-kpi-label { color: #53627A; font-size: .84rem; font-weight: 740; letter-spacing: .025em; }
        .quality-kpi-value { margin-top: .35rem; color: #17243B; font-size: clamp(1.32rem, 2vw, 1.8rem); font-weight: 780; letter-spacing: -.045em; line-height: 1.2; }
        .quality-kpi-detail { margin-top: .34rem; color: #748198; font-size: .73rem; font-weight: 560; line-height: 1.35; }
        .quality-kpi-health { background: #F3FBF9; }
        .quality-kpi-health .quality-kpi-value { color: #147E70; }
        .quality-health-track { height: 5px; margin-top: .72rem; overflow: hidden; border-radius: 99px; background: #DDECE9; }
        .quality-health-track span { display: block; height: 100%; border-radius: inherit; background: #20B99A; }
        [data-testid="stDataFrame"] {
            overflow: hidden; border: 1px solid var(--dl-line); border-radius: 13px;
            background: white; box-shadow: 0 3px 12px rgba(20, 41, 78, .035);
        }
        [data-testid="stPlotlyChart"] > div {
            border: 1px solid rgba(227, 234, 244, .8); border-radius: 15px;
            background: #fff; box-shadow: 0 4px 16px rgba(20, 41, 78, .035);
        }
        [data-testid="stExpander"] {
            overflow: hidden; border: 1px solid var(--dl-line); border-radius: 13px;
            background: rgba(255,255,255,.82);
        }
        [data-testid="stForm"] {
            padding: 1.15rem; border: 1px solid var(--dl-line); border-radius: 15px;
            background: #fff; box-shadow: var(--dl-shadow);
        }
        [data-testid="stAlert"] { border-radius: 12px; }
        hr { margin: 1.5rem 0; border-color: var(--dl-line); }

        /* Comfortable controls and a strong keyboard focus ring */
        [data-testid="stTextInput"] input,
        [data-testid="stTextArea"] textarea,
        [data-testid="stNumberInput"] input,
        [data-testid="stSelectbox"] [data-baseweb="select"] > div,
        [data-testid="stMultiSelect"] [data-baseweb="select"] > div {
            border-radius: 10px;
        }
        [data-testid="stFileUploader"] section {
            padding: 1.2rem; border: 1px dashed #AFC2E0; border-radius: 14px;
            background: #FBFCFF;
        }
        div.stButton > button,
        div[data-testid="stDownloadButton"] > button,
        div[data-testid="stFormSubmitButton"] > button {
            min-height: 2.72rem; padding: .55rem 1rem;
            border-radius: 10px; font-weight: 650;
            transition: transform .16s ease, box-shadow .16s ease, border-color .16s ease;
        }
        div.stButton > button:hover,
        div[data-testid="stDownloadButton"] > button:hover,
        div[data-testid="stFormSubmitButton"] > button:hover {
            transform: translateY(-1px); box-shadow: 0 5px 15px rgba(40, 78, 150, .12);
        }
        div.stButton > button[kind="primary"],
        div[data-testid="stFormSubmitButton"] > button[kind="primary"],
        div.stButton [data-testid="stBaseButton-primary"],
        div[data-testid="stFormSubmitButton"] [data-testid="stBaseButton-primary"],
        div[data-testid="stDownloadButton"] [data-testid="stBaseButton-primary"] {
            border-color: #2454C6 !important; background: #2454C6 !important;
            color: #FFFFFF !important;
        }
        div.stButton > button[kind="primary"] *,
        div[data-testid="stFormSubmitButton"] > button[kind="primary"] *,
        div.stButton [data-testid="stBaseButton-primary"] *,
        div[data-testid="stFormSubmitButton"] [data-testid="stBaseButton-primary"] *,
        div[data-testid="stDownloadButton"] [data-testid="stBaseButton-primary"] * { color: #FFFFFF !important; }
        button[data-testid="stBaseButton-primary"] svg,
        button[kind="primary"] svg { fill: #FFFFFF !important; color: #FFFFFF !important; }
        div.stButton > button[kind="primary"]:hover,
        div[data-testid="stFormSubmitButton"] > button[kind="primary"]:hover {
            border-color: #1D45A8 !important; background: #1D45A8 !important;
            color: #FFFFFF !important;
        }
        div.stButton [data-testid="stBaseButton-primary"]:hover,
        div[data-testid="stFormSubmitButton"] [data-testid="stBaseButton-primary"]:hover {
            border-color: #1D45A8 !important; background: #1D45A8 !important; color: #FFFFFF !important;
        }
        button:focus-visible, input:focus-visible, textarea:focus-visible,
        [tabindex="0"]:focus-visible {
            outline: 3px solid #2454C6 !important; outline-offset: 2px !important;
        }

        /* Tabs read as a workspace switcher */
        [data-testid="stTabs"] [data-baseweb="tab-list"],
        [data-testid="stTabs"] [role="tablist"] {
            display: flex !important; gap: .4rem; padding: .38rem; border: 1px solid #DCE5F2;
            border-radius: 14px; background: #EDF2F9;
            justify-content: flex-start !important; align-items: center;
        }
        [data-testid="stTabs"] [data-baseweb="tab"],
        [data-testid="stTabs"] button[role="tab"] {
            display: flex !important; flex: 0 0 auto !important; justify-content: flex-start !important;
            height: 2.58rem; padding: 0 1.05rem !important; border: 1px solid transparent !important;
            border-radius: 10px !important; background: transparent !important;
            color: #53627A !important; font-weight: 680; text-align: left !important;
            border-bottom: 0 !important;
        }
        [data-testid="stTabs"] [data-baseweb="tab"]::after,
        [data-testid="stTabs"] button[role="tab"]::after { display: none !important; }
        [data-testid="stTabs"] [data-baseweb="tab"] p,
        [data-testid="stTabs"] button[role="tab"] p { width: 100%; color: inherit !important; text-align: left !important; }
        [data-testid="stTabs"] [data-baseweb="tab"][aria-selected="true"],
        [data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
            color: #FFFFFF !important; background: #2857BE !important; border-color: #2857BE !important;
            box-shadow: 0 4px 10px rgba(38, 83, 181, .2);
        }
        [data-testid="stTabs"] [aria-selected="true"] p,
        [data-testid="stTabs"] [aria-selected="true"] span { color: #FFFFFF !important; }
        [data-testid="stTabs"] [data-baseweb="tab"]:hover:not([aria-selected="true"]),
        [data-testid="stTabs"] button[role="tab"]:hover:not([aria-selected="true"]) { background: #FFFFFF !important; border-color: #DCE5F2 !important; }

        /* Final tab layout: equal-width, padded tabs with left-aligned labels. */
        [data-testid="stTabs"] [data-baseweb="tab-list"],
        [data-testid="stTabs"] [role="tablist"] {
            display: flex !important; width: 100% !important; gap: .65rem !important;
            justify-content: stretch !important; align-items: stretch !important;
            padding: .62rem !important; border: 1px solid #D6E1F0 !important;
            border-radius: 17px !important;
            background: linear-gradient(110deg, #EAF0FA 0%, #F2F6FC 56%, #E8F4F1 100%) !important;
            box-shadow: inset 0 1px 0 rgba(255,255,255,.9), 0 8px 22px rgba(31,57,99,.06) !important;
        }
        [data-testid="stTabs"] [data-baseweb="tab"],
        [data-testid="stTabs"] button[role="tab"] {
            display: flex !important; flex: 1 1 0% !important; width: auto !important; min-width: 0 !important;
            height: 3.2rem !important; padding: 0 1.1rem !important;
            justify-content: flex-start !important; align-items: center !important;
            border: 1px solid #D6E1F0 !important; border-radius: 12px !important;
            background: rgba(255,255,255,.92) !important; color: #34445F !important;
            font-size: .95rem !important; font-weight: 720 !important; text-align: left !important;
            box-shadow: 0 2px 5px rgba(28,48,80,.035) !important;
        }
        [data-testid="stTabs"] [data-baseweb="tab"] > div,
        [data-testid="stTabs"] button[role="tab"] > div {
            display: flex !important; width: 100% !important; justify-content: flex-start !important;
            align-items: center !important; text-align: left !important;
        }
        [data-testid="stTabs"] [data-baseweb="tab"] p,
        [data-testid="stTabs"] button[role="tab"] p,
        [data-testid="stTabs"] [data-baseweb="tab"] span,
        [data-testid="stTabs"] button[role="tab"] span {
            width: 100% !important; margin: 0 !important; color: inherit !important;
            font-size: .95rem !important; font-weight: 720 !important; text-align: left !important;
            white-space: nowrap !important;
        }
        [data-testid="stTabs"] [data-baseweb="tab"][aria-selected="true"],
        [data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
            border-color: #2857BE !important;
            background: linear-gradient(115deg, #2857BE 0%, #3978D7 100%) !important;
            color: #FFFFFF !important; box-shadow: 0 6px 15px rgba(40,87,190,.24) !important;
        }
        [data-testid="stTabs"] [data-baseweb="tab"]:hover:not([aria-selected="true"]),
        [data-testid="stTabs"] button[role="tab"]:hover:not([aria-selected="true"]) {
            border-color: #9BB5E5 !important; background: #FFFFFF !important; color: #234DA5 !important;
        }

        /* Streamlit 1.65 renders tabs as React Aria role=tab elements,
           not Baseweb tabs or necessarily button elements. */
        [data-testid="stTabs"] [role="tablist"] {
            display: flex !important; width: 100% !important; gap: .65rem !important;
            justify-content: stretch !important; align-items: stretch !important;
            padding: .62rem !important; border: 1px solid #D6E1F0 !important;
            border-radius: 17px !important;
            background: linear-gradient(110deg, #EAF0FA 0%, #F2F6FC 56%, #E8F4F1 100%) !important;
            box-shadow: inset 0 1px 0 rgba(255,255,255,.9), 0 8px 22px rgba(31,57,99,.06) !important;
        }
        [data-testid="stTabs"] [role="tab"] {
            display: flex !important; flex: 1 1 0% !important; width: auto !important; min-width: 0 !important;
            height: 3.2rem !important; padding: 0 1.1rem !important;
            justify-content: flex-start !important; align-items: center !important;
            border: 1px solid #D6E1F0 !important; border-radius: 12px !important;
            background: rgba(255,255,255,.92) !important; color: #34445F !important;
            font-size: .95rem !important; font-weight: 720 !important; text-align: left !important;
            box-shadow: 0 2px 5px rgba(28,48,80,.035) !important;
        }
        [data-testid="stTabs"] [role="tab"] > div {
            display: flex !important; width: 100% !important; justify-content: flex-start !important;
            align-items: center !important; text-align: left !important;
        }
        [data-testid="stTabs"] [role="tab"] p,
        [data-testid="stTabs"] [role="tab"] span {
            width: 100% !important; margin: 0 !important; color: inherit !important;
            font-size: .95rem !important; font-weight: 720 !important; text-align: left !important;
            white-space: nowrap !important;
        }
        [data-testid="stTabs"] [role="tab"][aria-selected="true"] {
            border-color: #2857BE !important;
            background: linear-gradient(115deg, #2857BE 0%, #3978D7 100%) !important;
            color: #FFFFFF !important; box-shadow: 0 6px 15px rgba(40,87,190,.24) !important;
        }
        [data-testid="stTabs"] [role="tab"]:hover:not([aria-selected="true"]) {
            border-color: #9BB5E5 !important; background: #FFFFFF !important; color: #234DA5 !important;
        }
        /* Compact the sub-tabs after applying the readable visual treatment. */
        [data-testid="stTabs"] [role="tablist"],
        .st-key-quality_lab_tabs [data-testid="stTabs"] [role="tablist"],
        .st-key-prepare_workspace_tabs [data-testid="stTabs"] [role="tablist"],
        .st-key-data_preview_tabs [data-testid="stTabs"] [role="tablist"] {
            display: flex !important; grid-template-columns: none !important;
            width: 100% !important; gap: .18rem !important; padding: .32rem !important;
            justify-content: flex-start !important;
        }
        [data-testid="stTabs"] [role="tab"],
        .st-key-quality_lab_tabs [data-testid="stTabs"] [role="tab"],
        .st-key-prepare_workspace_tabs [data-testid="stTabs"] [role="tab"],
        .st-key-data_preview_tabs [data-testid="stTabs"] [role="tab"] {
            flex: 0 0 auto !important; width: auto !important; min-width: 0 !important;
            height: 1.8rem !important; min-height: 1.8rem !important;
            padding: 0 .65rem !important; border-radius: 8px !important;
            font-size: .8rem !important;
        }
        [data-testid="stTabs"] [role="tab"] p,
        [data-testid="stTabs"] [role="tab"] span {
            font-size: .8rem !important; font-weight: 680 !important;
        }
        /* Keep labels legible on every primary blue action, including icons and nested spans. */
        button[kind="primary"],
        button[data-testid="stBaseButton-primary"],
        [data-testid="stBaseButton-primary"] {
            color: #FFFFFF !important;
        }
        button[kind="primary"] *,
        button[data-testid="stBaseButton-primary"] *,
        [data-testid="stBaseButton-primary"] * {
            color: #FFFFFF !important; fill: #FFFFFF !important;
        }
        /* Make section headings easy to scan consistently on every page. */
        [data-testid="stMarkdownContainer"] h3 {
            margin: 1.25rem 0 .72rem !important; padding: .42rem .72rem;
            border: 1px solid #D9E3F0; border-left: 4px solid #356AE6;
            border-radius: 8px; background: #FFFFFF; color: #1C3155 !important;
            font-size: 1.17rem !important; font-weight: 760 !important;
            letter-spacing: -.018em !important;
        }
        [data-testid="stMarkdownContainer"] h4 {
            margin: 1.05rem 0 .55rem !important; padding-bottom: .35rem;
            border-bottom: 1px solid #D9E3F0; color: #2857A7 !important;
            font-size: 1rem !important; font-weight: 740 !important;
        }
        /* Plain, consistent cards across all five Quality Lab metrics. */
        .quality-kpi, .quality-kpi-health {
            background: #FFFFFF !important; background-image: none !important;
        }
        .quality-kpi-health .quality-kpi-value { color: #17243B !important; }
        .quality-health-track span { background: #20B99A !important; }
        /* Keep navigation and the active dataset visible in shorter windows. */
        [data-testid="stSidebar"] [data-testid="stButton"] { margin: .025rem 0 !important; }
        [data-testid="stSidebar"] [data-testid="stButton"] button {
            min-height: 1.92rem !important; padding: .2rem .68rem !important;
        }
        [data-testid="stSidebar"] [data-testid="stImage"] { margin: -.2rem 0 0 !important; }
        [data-testid="stSidebar"] [data-testid="stImage"] img {
            max-height: 3.8rem; object-fit: contain; object-position: left center;
        }
        .sidebar-dataset { margin-top: .4rem !important; padding: .62rem !important; }
        [data-testid="stTabs"] [role="tablist"] { gap: .14rem !important; }
        [data-testid="stTabs"] [role="tab"] {
            height: 1.82rem !important; min-height: 1.82rem !important;
            padding: 0 .58rem !important;
        }
        /* The requested +15% size applies to Quality Lab and Prepare tabs. */
        .st-key-quality_lab_tabs [role="tab"],
        .st-key-prepare_workspace_tabs [role="tab"] {
            height: 2.07rem !important; min-height: 2.07rem !important;
            padding: 0 .75rem !important; font-size: .92rem !important;
        }
        .st-key-quality_lab_tabs [role="tab"] p,
        .st-key-quality_lab_tabs [role="tab"] span,
        .st-key-prepare_workspace_tabs [role="tab"] p,
        .st-key-prepare_workspace_tabs [role="tab"] span {
            font-size: .92rem !important;
        }
        .st-key-quality_lab_tabs { margin-top: .8rem !important; }

        /* Spacious, readable sub-tab navigation across the main workspaces */
        .st-key-quality_lab_tabs [data-testid="stTabs"] [role="tablist"],
        .st-key-quality_lab_tabs [data-testid="stTabs"] [data-baseweb="tab-list"],
        .st-key-prepare_workspace_tabs [data-testid="stTabs"] [role="tablist"],
        .st-key-prepare_workspace_tabs [data-testid="stTabs"] [data-baseweb="tab-list"],
        .st-key-data_preview_tabs [data-testid="stTabs"] [role="tablist"],
        .st-key-data_preview_tabs [data-testid="stTabs"] [data-baseweb="tab-list"] {
            display: grid !important;
            gap: .55rem; padding: .55rem; border: 1px solid #D8E3F2; border-radius: 17px;
            background: linear-gradient(115deg, #E9F0FB, #F2F6FC 58%, #E8F5F2);
            box-shadow: inset 0 1px 0 rgba(255,255,255,.9), 0 8px 22px rgba(31,57,99,.06);
        }
        .st-key-quality_lab_tabs [data-testid="stTabs"] [role="tablist"],
        .st-key-quality_lab_tabs [data-testid="stTabs"] [data-baseweb="tab-list"] {
            grid-template-columns: repeat(5, minmax(0, 1fr));
        }
        .st-key-prepare_workspace_tabs [data-testid="stTabs"] [role="tablist"],
        .st-key-prepare_workspace_tabs [data-testid="stTabs"] [data-baseweb="tab-list"] {
            grid-template-columns: repeat(3, minmax(0, 1fr));
        }
        .st-key-data_preview_tabs [data-testid="stTabs"] [role="tablist"],
        .st-key-data_preview_tabs [data-testid="stTabs"] [data-baseweb="tab-list"] {
            grid-template-columns: repeat(2, minmax(0, 1fr));
        }
        .st-key-quality_lab_tabs [data-testid="stTabs"] button[role="tab"],
        .st-key-quality_lab_tabs [data-testid="stTabs"] [data-baseweb="tab"],
        .st-key-prepare_workspace_tabs [data-testid="stTabs"] button[role="tab"],
        .st-key-prepare_workspace_tabs [data-testid="stTabs"] [data-baseweb="tab"],
        .st-key-data_preview_tabs [data-testid="stTabs"] button[role="tab"],
        .st-key-data_preview_tabs [data-testid="stTabs"] [data-baseweb="tab"] {
            width: 100% !important; min-width: 0; height: 3rem; padding: 0 .9rem !important;
            border: 1px solid #DCE5F2 !important; border-radius: 12px !important;
            background: rgba(255,255,255,.82) !important; color: #33445F !important;
            font-size: .94rem; font-weight: 720; text-align: left !important;
            transition: color .18s ease, background .18s ease, box-shadow .18s ease, transform .18s ease;
        }
        .st-key-quality_lab_tabs [data-testid="stTabs"] button[role="tab"] p,
        .st-key-quality_lab_tabs [data-testid="stTabs"] [data-baseweb="tab"] p,
        .st-key-prepare_workspace_tabs [data-testid="stTabs"] button[role="tab"] p,
        .st-key-prepare_workspace_tabs [data-testid="stTabs"] [data-baseweb="tab"] p,
        .st-key-data_preview_tabs [data-testid="stTabs"] button[role="tab"] p,
        .st-key-data_preview_tabs [data-testid="stTabs"] [data-baseweb="tab"] p {
            overflow: visible; white-space: nowrap; color: inherit !important;
            font-size: .94rem; font-weight: 720; text-align: left !important;
        }
        .st-key-quality_lab_tabs [data-testid="stTabs"] button[role="tab"][aria-selected="true"],
        .st-key-quality_lab_tabs [data-testid="stTabs"] [data-baseweb="tab"][aria-selected="true"],
        .st-key-prepare_workspace_tabs [data-testid="stTabs"] button[role="tab"][aria-selected="true"],
        .st-key-prepare_workspace_tabs [data-testid="stTabs"] [data-baseweb="tab"][aria-selected="true"],
        .st-key-data_preview_tabs [data-testid="stTabs"] button[role="tab"][aria-selected="true"],
        .st-key-data_preview_tabs [data-testid="stTabs"] [data-baseweb="tab"][aria-selected="true"] {
            border-color: #2857BE !important;
            background: linear-gradient(120deg, #2857BE 0%, #3978D7 100%) !important;
            color: #FFFFFF !important; box-shadow: 0 6px 15px rgba(40,87,190,.25);
            transform: translateY(-1px);
        }
        .st-key-quality_lab_tabs [data-testid="stTabs"] button[role="tab"]:hover:not([aria-selected="true"]),
        .st-key-quality_lab_tabs [data-testid="stTabs"] [data-baseweb="tab"]:hover:not([aria-selected="true"]),
        .st-key-prepare_workspace_tabs [data-testid="stTabs"] button[role="tab"]:hover:not([aria-selected="true"]),
        .st-key-prepare_workspace_tabs [data-testid="stTabs"] [data-baseweb="tab"]:hover:not([aria-selected="true"]),
        .st-key-data_preview_tabs [data-testid="stTabs"] button[role="tab"]:hover:not([aria-selected="true"]),
        .st-key-data_preview_tabs [data-testid="stTabs"] [data-baseweb="tab"]:hover:not([aria-selected="true"]) {
            border-color: #9BB5E5 !important; background: #FFFFFF !important; color: #234DA5 !important;
        }

        @media (max-height: 800px) {
            [data-testid="stSidebar"] [data-testid="stButton"] { margin: 0 !important; }
            [data-testid="stSidebar"] [data-testid="stButton"] button { min-height: 2.22rem; }
            .sidebar-dataset { margin-top: 1.1rem; padding: .68rem; }
            .brand-tagline { margin-bottom: .55rem; }
        }

        /* Overview page components */
        .overview-hero {
            position: relative; overflow: hidden; margin: .15rem 0 1.3rem;
            padding: clamp(1.35rem, 3vw, 2.2rem); border-radius: 22px;
            color: #fff; background: linear-gradient(115deg, #17315B 0%, #2D5BC2 66%, #3978CE 100%);
            box-shadow: 0 14px 35px rgba(34, 72, 145, .18);
        }
        .overview-hero:after {
            content: ""; position: absolute; width: 20rem; height: 20rem; right: -5rem; top: -12rem;
            border: 1px solid rgba(255,255,255,.14); border-radius: 50%;
            box-shadow: 0 0 0 2.5rem rgba(255,255,255,.035), 0 0 0 5rem rgba(255,255,255,.025);
        }
        .overview-eyebrow { position: relative; z-index: 1; margin-bottom: .55rem; color: #C9D9FF; font-size: .7rem; font-weight: 780; letter-spacing: .15em; text-transform: uppercase; }
        .overview-title { position: relative; z-index: 1; margin: 0 0 .45rem; color: #fff; font-size: clamp(1.7rem, 3vw, 2.4rem); font-weight: 780; letter-spacing: -.045em; }
        .overview-copy { position: relative; z-index: 1; max-width: 720px; margin: 0; color: #E2EBFF; font-size: .95rem; }
        .section-kicker { margin: .25rem 0 .7rem; color: #77869C; font-size: .68rem; font-weight: 760; letter-spacing: .13em; text-transform: uppercase; }
        .insight-card {
            height: 100%; padding: 1rem 1.05rem; border: 1px solid var(--dl-line);
            border-radius: 14px; background: #fff; box-shadow: 0 4px 15px rgba(20,41,78,.035);
        }
        .insight-card-label { margin-bottom: .45rem; color: #75839A; font-size: .67rem; font-weight: 760; letter-spacing: .1em; text-transform: uppercase; }
        .insight-card-value { margin-bottom: .25rem; color: var(--dl-ink); font-size: 1.12rem; font-weight: 730; letter-spacing: -.025em; }
        .insight-card-copy { color: #64748B; font-size: .81rem; line-height: 1.5; }
        .readiness-track { height: .48rem; margin: .7rem 0 .4rem; overflow: hidden; border-radius: 999px; background: #E7EDF6; }
        .readiness-fill { height: 100%; border-radius: inherit; background: linear-gradient(90deg, #20B99A, #4C9FE6); }
        .pulse-card {
            min-height: 132px; height: 100%; padding: 1rem 1.05rem;
            border: 1px solid var(--dl-line); border-radius: 15px;
            background: #fff; box-shadow: 0 5px 18px rgba(20,41,78,.045);
        }
        .pulse-label { margin-bottom: .6rem; color: #78879D; font-size: .8rem; font-weight: 770; letter-spacing: .08em; text-transform: uppercase; }
        .pulse-value { overflow-wrap: anywhere; margin-bottom: .34rem; color: #1C3156; font-size: 1.1rem; font-weight: 740; letter-spacing: -.025em; }
        .pulse-detail { color: #596982; font-size: .86rem; line-height: 1.5; }

        @media (max-width: 768px) {
            .block-container { padding: 1.1rem 1rem 2rem; }
            [data-testid="stMetric"] { min-height: auto; padding: .85rem; }
            [data-testid="stMetricValue"] { font-size: 1.35rem; }
            [data-testid="stTabs"] [data-baseweb="tab-list"] { overflow-x: auto; }
            .st-key-quality_lab_tabs [data-testid="stTabs"] [role="tablist"],
            .st-key-quality_lab_tabs [data-testid="stTabs"] [data-baseweb="tab-list"] {
                display: flex !important; overflow-x: auto; justify-content: flex-start !important;
            }
            .st-key-prepare_workspace_tabs [data-testid="stTabs"] [role="tablist"],
            .st-key-prepare_workspace_tabs [data-testid="stTabs"] [data-baseweb="tab-list"],
            .st-key-data_preview_tabs [data-testid="stTabs"] [role="tablist"],
            .st-key-data_preview_tabs [data-testid="stTabs"] [data-baseweb="tab-list"] {
                display: flex !important; overflow-x: auto; justify-content: flex-start !important;
            }
            [data-testid="stTabs"] [role="tablist"] { overflow-x: auto !important; }
            [data-testid="stTabs"] [role="tab"] { flex: 0 0 auto !important; width: auto !important; }
            .st-key-quality_lab_tabs [data-testid="stTabs"] button[role="tab"],
            .st-key-quality_lab_tabs [data-testid="stTabs"] [data-baseweb="tab"],
            .st-key-prepare_workspace_tabs [data-testid="stTabs"] button[role="tab"],
            .st-key-prepare_workspace_tabs [data-testid="stTabs"] [data-baseweb="tab"],
            .st-key-data_preview_tabs [data-testid="stTabs"] button[role="tab"],
            .st-key-data_preview_tabs [data-testid="stTabs"] [data-baseweb="tab"] {
                width: 10.5rem !important; flex: 0 0 10.5rem !important;
            }
            .workspace-dataset-header { align-items: flex-start; flex-wrap: wrap; }
            .workspace-dataset-details { width: 100%; margin-left: 3.3rem; text-align: left; }
        }
        @media (prefers-reduced-motion: reduce) {
            *, *::before, *::after { scroll-behavior: auto !important; transition-duration: .01ms !important; }
        }
        /* Compact, consistently spaced sub-tabs across the workspace. */
        [data-testid="stTabs"] [role="tablist"] { gap: .28rem !important; }
        .st-key-quality_lab_tabs [role="tab"],
        .st-key-prepare_workspace_tabs [role="tab"],
        .st-key-data_preview_tabs [role="tab"] {
            height: 2.1rem !important; min-height: 2.1rem !important;
            padding: 0 .72rem !important;
        }
        /* Final compact sizing takes precedence over earlier workspace tab rules. */
        [data-testid="stTabs"] [role="tablist"] { gap: .12rem !important; padding: .24rem !important; }
        [data-testid="stTabs"] [role="tab"] {
            height: 1.78rem !important; min-height: 1.78rem !important;
            padding: 0 .52rem !important;
        }
        .st-key-quality_lab_tabs [role="tab"],
        .st-key-prepare_workspace_tabs [role="tab"],
        .st-key-data_preview_tabs [role="tab"] {
            height: 1.86rem !important; min-height: 1.86rem !important;
            padding: 0 .6rem !important;
        }
        /* Keep tab corners consistent across default, active, and hover states. */
        [data-testid="stTabs"] [role="tab"],
        [data-testid="stTabs"] [data-baseweb="tab"] {
            border-radius: 3.4px !important;
        }
        /* Prepare form submit controls stay readable on their blue primary fill. */
        [data-testid="stFormSubmitButton"] button[kind="primary"],
        [data-testid="stFormSubmitButton"] button[data-testid="stBaseButton-primary"],
        [data-testid="stFormSubmitButton"] [data-testid="stBaseButton-primary"] {
            color: #FFFFFF !important;
        }
        [data-testid="stFormSubmitButton"] button[kind="primary"] *,
        [data-testid="stFormSubmitButton"] button[data-testid="stBaseButton-primary"] *,
        [data-testid="stFormSubmitButton"] [data-testid="stBaseButton-primary"] * {
            color: #FFFFFF !important; fill: #FFFFFF !important;
        }
        /* Force readable labels and icons on Streamlit primary buttons across pages. */
        body .stApp button[kind*="primary"],
        body .stApp button[data-testid*="BaseButton-primary"],
        body .stApp [data-testid*="BaseButton-primary"] {
            color: #FFFFFF !important;
            -webkit-text-fill-color: #FFFFFF !important;
        }
        body .stApp button[kind*="primary"] *,
        body .stApp button[data-testid*="BaseButton-primary"] *,
        body .stApp [data-testid*="BaseButton-primary"] * {
            color: #FFFFFF !important;
            -webkit-text-fill-color: #FFFFFF !important;
            fill: #FFFFFF !important;
        }
        /* Keep primary actions blue even when Streamlit's deployed theme defaults to red. */
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
        /* Streamlit's red tab underline is unnecessary with our filled selected tabs. */
        body .stApp [data-testid="stTabs"] [data-baseweb="tab-highlight"],
        body .stApp [data-testid="stTabs"] [data-baseweb="tab-border"],
        body .stApp [data-testid="stTabs"] [role="tablist"]::before,
        body .stApp [data-testid="stTabs"] [role="tablist"]::after,
        body .stApp [data-testid="stTabs"] [role="tab"]::before,
        body .stApp [data-testid="stTabs"] [role="tab"]::after {
            display: none !important;
        }
        body .stApp [data-testid="stTabs"] [role="tab"][aria-selected="true"] {
            border-bottom: 0 !important;
        }
        /* Streamlit 1.5x renders tab labels with React Aria's stTab test id. */
        body .stApp [data-testid="stTabs"] [data-testid="stTab"] {
            --indicator-color: transparent !important;
            border-bottom-color: transparent !important;
            box-shadow: none !important;
        }
        body .stApp [data-testid="stTabs"] [data-testid="stTab"]::before,
        body .stApp [data-testid="stTabs"] [data-testid="stTab"]::after,
        body .stApp [data-testid="stTabs"] [data-testid="stTab"] [data-testid*="indicator"],
        body .stApp [data-testid="stTabs"] [data-testid="stTab"] [data-testid*="Indicator"] {
            display: none !important;
            background: transparent !important;
            border-color: transparent !important;
        }
        body .stApp [data-testid="stTabs"] [data-testid="stTab"][aria-selected="true"] {
            border-bottom: 0 !important;
            box-shadow: none !important;
        }
        /* Reinforce the theme color on filter widgets with their own rendered marks. */
        body .stApp [data-testid="stSlider"] [role="slider"],
        body .stApp [data-testid="stSlider"] [data-testid*="Thumb"] {
            background-color: #356AE6 !important;
            border-color: #356AE6 !important;
        }
        body .stApp [data-testid="stSlider"] [data-testid*="TrackFill"],
        body .stApp [data-testid="stSlider"] [data-testid*="trackFill"] {
            background-color: #356AE6 !important;
            border-color: #356AE6 !important;
        }
        body .stApp [data-testid="stMultiSelect"] [data-baseweb="tag"],
        body .stApp [data-testid="stMultiSelect"] [data-testid*="Tag"] {
            background-color: #356AE6 !important;
        }
        body .stApp [data-testid="stMultiSelect"] [role="option"][aria-selected="true"] {
            color: #234DA5 !important;
            background-color: #EAF0FF !important;
        }
        body .stApp [data-testid="stCheckbox"] [role="checkbox"][aria-checked="true"],
        body .stApp [data-testid="stCheckbox"] input:checked + div,
        body .stApp [data-testid="stCheckbox"] input:checked,
        body .stApp [data-testid="stCheckbox"] [role="checkbox"][data-state="checked"] {
            color: #356AE6 !important;
            background-color: #356AE6 !important;
            border-color: #356AE6 !important;
        }
        body .stApp [data-testid="stCheckbox"] input,
        body .stApp [data-testid="stSlider"] input {
            accent-color: #356AE6 !important;
        }
        body .stApp [data-testid="stCheckbox"] [data-baseweb="checkbox"] > div,
        body .stApp [data-testid="stCheckbox"] [role="checkbox"][aria-checked="true"] > div {
            background-color: #356AE6 !important;
            border-color: #356AE6 !important;
        }
        body .stApp [data-testid="stCheckbox"] svg {
            fill: #FFFFFF !important;
        }
        @media (max-height: 800px) {
            [data-testid="stSidebar"] [data-testid="stButton"] button {
                min-height: 1.78rem !important; padding-top: .14rem !important; padding-bottom: .14rem !important;
            }
            [data-testid="stSidebar"] [data-testid="stImage"] img { max-height: 3.2rem; }
            .sidebar-dataset { margin-top: .28rem !important; padding: .5rem !important; }
            .sidebar-dataset-label { margin-bottom: .2rem; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
