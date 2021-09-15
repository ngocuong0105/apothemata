import plotly.graph_objects as go
import streamlit as st
import pandas as pd 
import requests
from functools import lru_cache
from fuzzywuzzy import process
import time
import json
from alpha_vantage.timeseries import TimeSeries
import yfinance as yf

from page import Page

class checkStock(Page):
    def __init__(self, title: str, alpha_vantage_key:str = '9VA69FN762V63TW7') -> None:
        super().__init__(title)
        self.sources = {'Yahoo Finance':'yahoo', 'Alpha Vantage (free license)':'alpha_vantage'}
        self.ava_key = alpha_vantage_key
        
    def _filter_loaded_data(self, data:pd.DataFrame, start:str, end:str):
        if len(data) == 0:
            st.write('No data loaded')
            return data
        data = data[(data['date']>=start)&(data['date']<=end)]
        return data

    def _wait_message(self):
        st.write('Please wait 1 minute to access data.')
        # Add a placeholder
        latest_iteration = st.empty()
        bar = st.progress(0)
        for i in range(60):
            # Update the progress bar with each iteration.
            latest_iteration.text(f'{i+1} seconds')
            bar.progress((i+1)/60)
            time.sleep(1)

    @st.cache(show_spinner=False, suppress_st_warning=True)
    def _search_ticker(self, keywords: 'list[str]'): 
        ticker_results = {}
        for keyword in keywords:
            # search ticker symbol
            ticker_info = self._search_keyword_cached(keyword)
            ticker_results[ticker_info['symbol']] = ticker_info['name']
        return ticker_results

    @st.cache(show_spinner=False, suppress_st_warning=True)
    def _search_keyword_cached(self, keyword:str):

        json_file = open('context/s&p_symbols.json',)
        popular_stocks = json.load(json_file)
        ticker_info, score = process.extractOne(keyword, popular_stocks)
        if score<=50:
            json_file = open('context/symbols.json',)
            stockList = json.load(json_file)
            ticker_info = process.extractOne(keyword, stockList)[0]

        return ticker_info

    @st.cache(show_spinner=False, suppress_st_warning=True)
    def load_data_yahoo(self, ticker:str):
        data = yf.download(ticker)
        data.columns = [f'{ticker}'+'-'+col.lower() for col in data.columns]
        data = data.reset_index()
        data = data.rename(columns = {'Date':'date'})
        return data

    @st.cache(show_spinner=False, suppress_st_warning=True)
    def load_data_alpha_vantage(self, ticker:str, outputsize:str = 'full'):
        ts = TimeSeries(key=self.ava_key, output_format='pandas')
        # intraday_data, _ = ts.get_intraday(ticker, outputsize='full', interval='1m')
        try:
            data, _ = ts.get_daily(ticker, outputsize=outputsize)
            data.columns = [f'{ticker}' + '-' + col[3:] for col in data.columns]
            data = data.reset_index()
        except:
            self._wait_message()
            try:
                data, _ = ts.get_daily(ticker, outputsize=outputsize)
                data.columns = [f'{ticker}' + '-' + col[3:] for col in data.columns]
                data = data.reset_index()
            except:
                st.write('You ran out of data fetches for today (500+).\
                     Please use Yahoo Finance as data source.')
                data = pd.DataFrame()
        return data

    # Sidebar
    def get_sidebar_input(self):
        # User input
        st.sidebar.header('Please provide input:')
        source = st.sidebar.selectbox('Select data source', ['Yahoo Finance', 'Alpha Vantage (free license)'])
        start_date = st.sidebar.text_input('Start Date', '2020-01-01')
        end_date = st.sidebar.text_input('End Date', '2021-08-12')
        
        keywords = [keyword for keyword in st.sidebar.text_input(\
                                            'Search Ticker (comma separated keywords)',\
                                            'google, tesla').split(',') 
                                            if keyword !='']
        if keywords == []:
            st.write('Please search ticker')
            return None, None, None, None, None
        
        start = time.time()
        ticker_results = self._search_ticker(keywords)
        end = time.time()
        st.markdown(f' <font color= #7979ff> Found ticker(s) in {round(end-start,4)} seconds </font>', unsafe_allow_html=True)
            
        # Select Ticker
        ticker = st.sidebar.selectbox(
            'Select Ticker (e.g. AAPL, GOOGL, SPY, TSLA)',
            list(ticker_results.keys())
            )
        company_name = ticker_results[ticker]
        return start_date, end_date, ticker, company_name, self.sources[source]

    def plot(self,data: pd.DataFrame, time_col: str, ticker:str, company_name:str):
        # User selects columns to plot
        numerics = ['int16', 'int32', 'int64', 'float16', 'float32', 'float64']
        plotted_cols =list(data.select_dtypes(include=numerics).columns)
        value_cols = st.sidebar.multiselect(
            'Which prices are you interested in?',
            plotted_cols,
            plotted_cols[0]
        )
        # PLOT
        fig = go.Figure(
            layout=DEFAULT_LAYOUT
        )
        for forecast_col in value_cols:
            fig.add_scatter(
                x=data[time_col],
                y=data[forecast_col], 
                name=f'{ticker}-{forecast_col}'
            )

        if value_cols!=[]:
            st.subheader(f'Company name: {company_name}')
            st.write(f'Plotted: {", ".join(value_cols)}')
            st.plotly_chart(fig, use_container_width=True)

    # Display dataframe
    def show_data(self, data:pd.DataFrame, ticker:str):
        if st.checkbox('Show data'):
            st.subheader(f'{ticker}')
            if len(data)<50:
                st.table(data)
            else:
                st.dataframe(data)

    # Display statistics
    def show_stats(self, data:pd.DataFrame, ticker:str):
        if st.checkbox('Show statistics'):
            st.subheader(f'{ticker} Statistics')
            st.write(data.describe())

    # Load page
    def load_page(self):
        self.show_title()
        start, end, ticker, company_name, source = self.get_sidebar_input()
        time_col = 'date'
        if ticker==None:
            return
        
        # Get stock data
        data = eval('self.load_data_' + f'{source}'+ '("'+ticker+'")')
        data = self._filter_loaded_data(data, start, end)

        if len(data)==0:
            if ticker == []:
                st.write('Please select ticker')
            else:
                st.markdown('Cannot find ticker')
            return

        self.plot(data, time_col, ticker, company_name)
        self.show_data(data, ticker)
        self.show_stats(data, ticker)

DEFAULT_LAYOUT = dict(
    xaxis=dict(
        type='date',
        rangeselector=dict(
            buttons=list([
                dict(count=7,
                    label='1w',
                    step='day',
                    stepmode='backward'),
                dict(count=1,
                    label='1m',
                    step='month',
                    stepmode='backward'),
                dict(count=3,
                    label='3m',
                    step='month',
                    stepmode='backward'),
                dict(count=6,
                    label='6m',
                    step='month',
                    stepmode='backward'),
                dict(count=1,
                    label='1y',
                    step='year',
                    stepmode='backward'),
                dict(step='all')
            ]),
            bgcolor = '#7792E3',
            font=dict(
                color = 'white',
                size = 13
            ),
        ),
        rangeslider=dict(
            visible=True
        ),
    ),
    height = 550
)