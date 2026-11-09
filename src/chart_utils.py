import matplotlib.pyplot as plt
import streamlit as st

def render_chart():
    """
    Checks if the AI generated a matplotlib plot and renders it on Streamlit.
    """
    fig = plt.gcf()
    if fig.get_axes():  # If there is an active plot with drawing axes
        st.pyplot(fig)
        plt.clf()       # Clear the canvas for the next question