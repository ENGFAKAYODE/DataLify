import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()


def get_config(key, default=None):
    """Retrieve configuration from environment variables or Streamlit Secrets."""

    value = os.getenv(key)

    if value:
        return value

    try:
        return st.secrets.get(key, default)
    except Exception:
        return default


OPENROUTER_API_KEY = get_config("OPENROUTER_API_KEY")

OPENROUTER_MODEL = get_config(
    "OPENROUTER_MODEL",
    "deepseek/deepseek-v4.1-flash-1017"
)