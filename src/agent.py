import os
import pandas as pd
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_experimental.agents import create_pandas_dataframe_agent

load_dotenv()


def create_analyst_agent(df: pd.DataFrame):
    api_key = os.getenv("OPENROUTER_API_KEY")
    model = os.getenv(
        "OPENROUTER_MODEL",
        "deepseek/deepseek-v4.1-flash-1017"
    )

    if not api_key:
        raise ValueError("Missing OPENROUTER_API_KEY in .env file.")

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