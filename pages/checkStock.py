import plotly.graph_objects as go
import streamlit as st
import pandas as pd 
import requests
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
    
    def _filter_loaded_data(self, data:pd.DataFrame, start:str, end:str):
        if len(data) == 0:
            st.write('No data loaded')
            return data
        data = data[(data['date']>=start)&(data['date']<=end)]
        return data

    def _wait_message(self):
        st.write('Please wait 1 minute access to data.')
        # Add a placeholder
        latest_iteration = st.empty()
        bar = st.progress(0)
        for i in range(60):
            # Update the progress bar with each iteration.
            latest_iteration.text(f'{i+1} seconds')
            bar.progress((i+1)/60)
            time.sleep(1)

    @st.cache(show_spinner=False, suppress_st_warning=True)
    def _search_ticker(self, keywords: list[str]):
        json_file = open('context/symbols.json',)
        stockList = json.load(json_file)
        ticker_results = {}
        for keyword in keywords:
            # search ticker symbol
            ticker_info = process.extractOne(keyword, stockList)[0]
            ticker_results[ticker_info['symbol']] = ticker_info['name']

        return ticker_results

    def get_sidebar_input(self):
        # User input
        st.sidebar.header('Please provide input:')
        source = st.sidebar.selectbox('Select data source', ['Yahoo Finance', 'Alpha Vantage (free license)'])
        start_date = st.sidebar.text_input('Start Date', '2020-01-01')
        end_date = st.sidebar.text_input('End Date', '2021-08-12')
        
        keywords = [keyword for keyword in st.sidebar.text_input(\
                                            'Search Symbol (comma separated keywords)',\
                                            'google, alphabet').split(',') 
                                            if keyword !='']

        ticker_results = self._search_ticker(keywords)

        # Select Ticker
        ticker = st.sidebar.selectbox(
            'Select Ticker (e.g. AAPL, GOOGL, SPY, TSLA)',
            list(ticker_results.keys())
            )
        company_name = ticker_results[ticker]
        return start_date, end_date, ticker, company_name, self.sources[source]
   
    def load_page(self):
        self.show_title()
        start, end, ticker, company_name, source = self.get_sidebar_input()
        # Get stock data
        time_col = 'date'

        data = eval('self.load_data_' + f'{source}'+ '("'+ticker+'")')
        data = self._filter_loaded_data(data, start, end)

        if len(data)==0:
            if ticker == []:
                st.write('Please select ticker')
            else:
                st.markdown('Cannot find ticker')
            return
        # User selects columns to plot
        numerics = ['int16', 'int32', 'int64', 'float16', 'float32', 'float64']
        plotted_cols =list(data.select_dtypes(include=numerics).columns)
        value_cols = st.sidebar.multiselect(
            'Which prices are you interested in?',
            plotted_cols
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
            st.subheader(f'{company_name}:')
            st.subheader(f'{", ".join(value_cols)}')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.subheader(f'Closing price for {company_name}')
            fig.add_scatter(
                x=data[time_col],
                y=data[f'{ticker}-close'], 
                name=f'{ticker}-close'
            )
            st.plotly_chart(fig, use_container_width=True)

        # Display table
        if st.checkbox('Show data'):
            st.subheader(f'{ticker}')
            if len(data)<50:
                st.table(data)
            else:
                st.dataframe(data)

        # Display
        if st.checkbox('Show statistics'):
            st.subheader(f'{ticker} Statistics')
            st.write(data.describe())


'''
    @st.cache(show_spinner=False, suppress_st_warning=True)
    def _search_ticker(self, keywords: list[str]):
        
        # search ticker symbol
        ticker_results = []
        for keyword in keywords:
            # remove leading and trailing spaces
            keyword = keyword.strip()
            if keyword == 'google':
                keyword = 'googl'
            url = f'https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords={keyword}&apikey={self.ava_key}'
            r = requests.get(url)
            dict_json = r.json()
            
            # check if run out of 5 calls per minute/500 calls per day
            if 'Note' in dict_json:
                self._wait_message()
                url = f'https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords={keyword}&apikey={self.ava_key}'
                r = requests.get(url)
                dict_json = r.json()
            if 'Information' in dict_json:
                st.write('You ran out of data fetches for today (500+).\
                     Please use Yahoo Finance as data source.')
                return []
            st.write(dict_json)
            ls = list(pd.DataFrame(dict_json['bestMatches']).get('1. symbol',[]))
            if len(ls)>0:
                ticker_results.extend(ls)
            else:
                st.sidebar.write(f'Could not find tickers for "{keyword}"')
        return ticker_results
'''


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