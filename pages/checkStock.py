import plotly.graph_objects as go
import yfinance as yf
import streamlit as st

from page import Page

class checkStock(Page):
    def __init__(self, title: str) -> None:
        super().__init__(title)

    @staticmethod
    def load(title):
        st.title(title)
        @st.cache
        def load_data(start,end,ticker):
            df_stock = yf.download(ticker, 
                                start=start, 
                                end=end, 
                                progress=False)

            df_stock = df_stock.reset_index() 
            return df_stock

        # Add a title and image
        st.title('Check your stocks')

        # User input

        def get_input():
            start_date = st.sidebar.text_input('Start Date', '2020-01-01')
            end_date = st.sidebar.text_input('End Date', '2021-08-12')
            ticker = st.sidebar.text_input('Ticker Symbol (e.g. AAPL, GOOGL, SPY, TSLA)', 'AMZN')
            return start_date, end_date, ticker
        st.sidebar.header('Please provide input:')

        start, end, ticker = get_input()

        # Get stock data
        time_col = 'Date'
        df_stock = load_data(start,end,ticker)

        # User selects columns to plot
        numerics = ['int16', 'int32', 'int64', 'float16', 'float32', 'float64']
        plotted_cols =list(df_stock.select_dtypes(include=numerics).columns)
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
                x=df_stock[time_col],
                y=df_stock[forecast_col], 
                name=f'{ticker}-{forecast_col}'
            )

        # Plot
        if value_cols!=[]:
            st.subheader(f'{ticker}: {", ".join(value_cols)}')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.subheader(f'{ticker} Closing price')
            fig1 = go.Figure(
            layout=DEFAULT_LAYOUT
            )   
            fig1.add_scatter(
                x=df_stock[time_col],
                y=df_stock['Close'], 
                name=f'{ticker}-Close'
            )

            st.plotly_chart(fig1, use_container_width=True)

        # Display table
        if st.checkbox('Show data'):
            st.subheader(f'{ticker}')
            if len(df_stock)<50:
                st.table(df_stock)
            else:
                st.dataframe(df_stock)

        # Display
        if st.checkbox('Show statistics'):
            st.subheader(f'{ticker} Statistics')
            st.write(df_stock.describe())

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