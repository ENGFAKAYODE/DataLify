import os
import pandas as pd
import streamlit as st

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_experimental.agents import create_pandas_dataframe_agent


# Load local environment variables when available.
load_dotenv()


def get_config(key, default=None):
    """
    Retrieve configuration from:
    1. Environment variables (.env locally or host environment variables).
    2. Streamlit Secrets (Streamlit Community Cloud).
    """

    value = os.getenv(key)

    if value:
        return value

    try:
        return st.secrets.get(key, default)
    except Exception:
        return default


def create_analyst_agent(df: pd.DataFrame):

    api_key = get_config("OPENROUTER_API_KEY")

    model = get_config(
        "OPENROUTER_MODEL",
        "deepseek/deepseek-v4.1-flash-1017"
    )

    if not api_key:
        raise ValueError(
            "Missing OPENROUTER_API_KEY. "
            "Configure it in your .env file or hosting environment secrets."
        )

    llm = ChatOpenAI(
        model=model,
        temperature=0,
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1"
    )

    agent = create_pandas_dataframe_agent(
        llm=llm,
        df=df,
        agent_type="tool-calling",
        verbose=True,
        allow_dangerous_code=True,
        handle_parsing_errors=True
    )

    return agent