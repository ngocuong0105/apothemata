import streamlit as st
import framework.page as page
class MultiPage: 
    '''
    Framework for combining multiple streamlit applications.
    Note streamlit does not support multipage setup in tyhe real sense 
    and here we implement 'artifitial' Multipage setup. That is why
    you will notice that the url would not change when you click on different 'pages'.
    '''
    def __init__(self) -> None:
        '''
        Constructor is a dictionary object where:
        key = title of page
        value = page object
        '''
        self.pages = {} 
    
    def add_page(self, page:page.Page) -> None: 
        '''
        Add page in framework. Similar to a 'setter'
        '''
        self.pages[page.title] = page
        
    def run(self):
        '''
        Run page with this method. Note that page title are added in navigation bar.
        Navigation bar is currently not supported in streamlit yet (as of version 1.0),
        therefore we use a sidebar radio as a workaround.
        '''
        # Dropdown to select the page to run
        st.sidebar.title('Navigation')
        selected_title = st.sidebar.radio("Go to", list(self.pages.keys()))
        
        # run the app function
        self.pages[selected_title].load_page()