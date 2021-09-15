import streamlit as st
from multipage import MultiPage
import pages

# App layout settings
st.set_page_config(page_title='Apothemata',\
                    page_icon='chart_with_upwards_trend',\
                    layout='wide',\
                    initial_sidebar_state='auto')

# Create an instance of the app 
app = MultiPage()
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
# Dowload dataset
# if not correct ticker give message
# little life-data game
# learn css/html to put all css markdowns in context