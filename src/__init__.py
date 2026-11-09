import matplotlib.pyplot as plt
import streamlit as st

def render_chart():
    """Checks if a plot was created and displays it."""
    fig = plt.gcf()
    if fig.get_axes():
        st.pyplot(fig)
        plt.clf()