# Datalify

Datalify is a local Streamlit workspace for importing, profiling, preparing,
visualizing, analyzing, and exporting tabular data.

## Run from Windows Terminal

From this project folder, create the environment and install dependencies once:

```powershell
py -m venv venv
.\venv\Scripts\python.exe -m pip install -r requirements.txt
```

Then start Datalify on port 8504:

```powershell
.\run_datalify.bat
```

Open <http://localhost:8504>. You can also start it directly with
`.\venv\Scripts\python.exe -m streamlit run app.py --server.port 8504`.
The `.streamlit/config.toml` file sets 8504 as Streamlit's default port too.

AI Analyst is optional. To enable it, set `OPENROUTER_API_KEY` in the project
root `.env` file and optionally set `OPENROUTER_MODEL`. Keep `.env` private.

Prepare and AI Brief each include a separate **Agentic mode**. The pipeline
profiles the schema, detects CSV encoding and delimiter, flattens row-preserving
JSON objects, standardizes high-confidence types and labels, removes exact and
identifiable version duplicates, drops unusable columns, resolves missing
values where a safe rule is available, flags domain anomalies, and validates
the output. Both modes apply
changes to the undoable working copy and export a replayable recipe and audit
summary. AI Brief also investigates the cleaned dataset and generates an
evidence-led executive brief without asking for an audience or decision. The
original upload stays unchanged. The data profile and a small sample are sent
to the configured OpenRouter model; review the privacy notice in the app before
using sensitive data.
