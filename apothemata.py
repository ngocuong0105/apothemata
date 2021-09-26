import streamlit as st
from framework.multipage import MultiPage
import pages

# App layout settings
about_info = 'Investing real money using this app is highly discouraged.'
menu_items = {'About': about_info}

st.set_page_config(page_title='Apothemata',\
                    page_icon='🅰️',\
                    layout='wide',\
                    initial_sidebar_state='auto',\
                    menu_items=menu_items)
# Create an instance of the app 
app = MultiPage()
home = pages.home(title = 'Home')
checkStock = pages.checkStock(title = 'Check your stocks')
trade = pages.trade(title = 'Yolo trade')

# Add all your application here
app.add_page(home)
app.add_page(checkStock)
app.add_page(trade)

# The main app
app.run()
