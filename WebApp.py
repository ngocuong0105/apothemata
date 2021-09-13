import streamlit as st
import pandas as pd
from PIL import Image

# Add a title and image
st.write("""
# Welcome to the money machine app
"""
)
# Open and display an image
image = Image.open('./context/ml_pic.webp')
st.image(image, use_column_width = True)

# Create a sidebar header
st.sidebar.header('Please provide input:')

# Create a function to get users input
def get_input():
    start_date = st.sidebar.text_input('Start Date', '2020-01-01')
    end_date = st.sidebar.text_input('End Date', '2021-08-12')
    return start_date,end_date

df = pd.read_csv('./context/sample.csv')
start_date, end_date = get_input()

# Display
st.header('Data Statistics')
st.write(df.describe())





