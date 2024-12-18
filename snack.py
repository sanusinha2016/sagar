import streamlit as st
import time

# Define a function to simulate a notification or "Snackbar"
def show_snackbar():
    st.toast("This is a Snackbar notification!", icon="ℹ️")

# Title of the app
st.title("Streamlit Snackbar Example")

# Button to show the Snackbar notification
if st.button("Show Snackbar"):
    show_snackbar()
    time.sleep(1)  # Simulate delay to show the toast for a brief moment

# Optional: Display some content
st.write("This is a simple demonstration of a Snackbar-like notification in Streamlit.")
