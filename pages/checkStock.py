import plotly.graph_objects as go
import streamlit as st
import pandas as pd 
import base64
from fuzzywuzzy import process
import time
import json
from alpha_vantage.timeseries import TimeSeries
import yfinance as yf
import pickle
import datetime

from framework.page import Page
from framework.utils import click_button
class checkStock(Page):
    def __init__(self, title: str) -> None:
        super().__init__(title)
        self.sources = {'Yahoo Finance':'yahoo', 'Alpha Vantage (free license)':'alpha_vantage'}
        self.ava_key = st.secrets['alpha_vantage_key']

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
        self.show_info(ticker)
        self.show_trading_hours()


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
            symb, name = self._search_keyword_cached(keyword)
            ticker_results[symb] = name
        return ticker_results

    @st.cache(show_spinner=False, suppress_st_warning=True)
    def _search_keyword_cached(self, keyword:str):

        # quick search exact match
        with open('context/symbols_dict.pickle','rb') as f:
            symbols = pickle.load(f)
        if keyword in symbols:
            return keyword, symbols[keyword]
            
        # more sophisticated search not necessarily exact match
        json_file = open('context/s&p_symbols.json',)
        popular_stocks = json.load(json_file)
        ticker_info, score = process.extractOne(keyword, popular_stocks)
        if score<=50:
            json_file = open('context/symbols.json',)
            stockList = json.load(json_file)
            ticker_info = process.extractOne(keyword, stockList)[0]
        
        return ticker_info['symbol'], ticker_info['name']

    @st.cache(show_spinner=False, suppress_st_warning=True)
    def load_data_yahoo(self, ticker:str):
        data = yf.download(ticker)
        data.columns = [f'{ticker}'+'-'+col.lower() for col in data.columns]
        data = data.reset_index()
        data = data.rename(columns = {'Date':'date'})
        data = data.sort_values(by = 'date', ascending = False)
        return data

    @st.cache(show_spinner=False, suppress_st_warning=True)
    def load_data_alpha_vantage(self, ticker:str, outputsize:str = 'full'):
        ts = TimeSeries(key=self.ava_key, output_format='pandas')
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
        source = st.sidebar.selectbox('Select data source', ['Yahoo Finance', 'Alpha Vantage (free license)'], key = 'data_source')
        yesterday = datetime.date.today() - datetime.timedelta(days=1)
        s = (yesterday - datetime.timedelta(days=365)).strftime('%Y-%m-%d')
        e = yesterday.strftime('%Y-%m-%d')
        start_date = st.sidebar.text_input('Start Date', f'{s}')
        end_date = st.sidebar.text_input('End Date', f'{e}')
        
        keywords = [keyword for keyword in st.sidebar.text_input(\
                                            'Search Ticker (comma separated keywords)',\
                                            'GME, tesla').split(',') 
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
            'Select Ticker (e.g. AAPL, GME, TSLA)',
            list(ticker_results.keys()),
            key = 'ticker'
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
        fig.update_layout(title=f'{", ".join(value_cols)}')
        for forecast_col in value_cols:
            fig.add_scatter(
                x=data[time_col],
                y=data[forecast_col], 
                name=f'{ticker}-{forecast_col}'
            )

        if value_cols!=[]:
            st.subheader(f'Company name: {company_name}')
            st.write(f'Sector: {yf.Ticker(ticker).info["sector"]}')
            # st.write(f'Plotted: {", ".join(value_cols)}')
            st.plotly_chart(fig, use_container_width=True)

    # Display dataframe
    def show_data(self, data:pd.DataFrame, ticker:str):
        if st.checkbox('Data',value=True):
            st.subheader(f'{ticker}')
            if len(data)<50:
                st.table(data)
            else:
                st.dataframe(data)
            download=click_button('Download csv')
            if download:
                csv = data.to_csv(index=False)
                b64 = base64.b64encode(csv.encode()).decode()  # some strings
                linko= f'<a href="data:file/csv;base64,{b64}" download="{ticker}.csv">Click to download </a>'
                st.markdown(linko, unsafe_allow_html=True)

    # Display statistics
    def show_stats(self, data:pd.DataFrame, ticker:str):
        if st.checkbox('Statistics'):
            st.subheader(f'{ticker} Statistics')
            st.write(data.describe())

    # Display trading hours
    def show_trading_hours(self):
        if st.checkbox('Market hours'):
            with open('./context/market_hours.txt','r') as f:
                s = f.read()
            st.write(s)

    # Display ticker info
    def show_info(self, ticker:str):
        ticker = yf.Ticker(ticker)
        pd.set_option('display.float_format', lambda x: '%.0f' % x)
        if st.checkbox('Company info'):
            st.write(ticker.info['longBusinessSummary'])
        if st.checkbox('Yearly balance sheet'):
            st.write(ticker.balance_sheet)
        if st.checkbox('Quarterly balance sheet'):
            st.write(ticker.quarterly_balance_sheet)
        if st.checkbox('Yearly earnings'):
            st.write(ticker.earnings)
        if st.checkbox('Quarterly earnings'):
            st.write(ticker.quarterly_earnings)

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