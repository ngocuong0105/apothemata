import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image

import time
from multipage import MultiPage
import pages

# App layout settings
st.set_page_config(page_title='IUH Corp.',\
                    page_icon='chart_with_upwards_trend',\
                    layout='wide',\
                    initial_sidebar_state='auto')


# Create an instance of the app 
app = MultiPage()

# Title of the main page
# display = Image.open('context/ml_pic.webp')
# display = np.array(display)

# col1, col2 = st.columns(2)
# col1.image(display, width = 400)
# col2.title("Stock Prices Application")


home = pages.home(title = 'Home')
checkStock = pages.checkStock(title = 'Check your stocks')

# Add all your application here
app.add_page("Home", home)
app.add_page('Stocks', checkStock)

# The main app
app.run()

# Features:
# Highest moving stock
# Source code link to git
# Popular stocks