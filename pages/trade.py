import praw
import streamlit as st
from collections import deque
from random import randint
import time
import pandas as pd
import regex as re
import nltk
nltk.download('vader_lexicon', quiet = True)
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import datetime
import pickle
import yfinance as yf
import plotly.express as px
import base64

from page import Page
from utils import markdown_css, click_button, wait_message

class trade(Page):
    def __init__(self, title: str) -> None:
        super().__init__(title)
        self.green = '#00ff32'
        self.red = '#ff0000'
        self.yellow = '#fff000'
        self.white = '#ffffff'
        self.text_size = 16

    def load_page(self):
        strategy = self.get_sidebar_input()
        if strategy == '🚀 Reddit Power':
            st.header(f'{strategy}')
            self.reddit_strategy()
        elif strategy == '💬 Tweet It!':
            st.header(f'{strategy}')
            st.caption('Under development, stay tuned!')
        elif strategy == '🇺🇸 I believe Fox News':
            st.header(f'{strategy}')
            pressed = click_button('Find strategy')
            if pressed:
                seconds = randint(5,10)
                wait_message('Searching for trading strategy...',seconds)
                txt = '🤪 No strategy found. We are sorry you are retarded.'
                markdown_css(txt,20,self.white,height=200,position='center')

    def get_sidebar_input(self) -> str:
        st.sidebar.header('Please provide input:')
        options = ['🚀 Reddit Power', '💬 Tweet It!', '🇺🇸 I believe Fox News', '']
        strategy = st.sidebar.selectbox('Select trading strategy',options, index = len(options)-1)
        return strategy

    def reddit_strategy(self):

        # Choosing risk appetite
        options =  ['🏦 I want to make a risk-averse long term investment.',
                    # '📈 I want to protect my savings from inflation.',
                    '🙌 I have diamond hands!',
                    '🚀 Lets go to the moon!',
                    '']
        risk_type = st.selectbox('What is your risk profile?', options, index = len(options)-1)

        if risk_type == '🏦 I want to make a risk-averse long term investment.':
            if click_button('Find strategy'):
                seconds = randint(5,10)
                txt = 'Searching for trading strategy...'
                wait_message(txt,seconds)
                txt = '😬 Risk-averse, really? Sorry you are using the wrong Web App.'
                markdown_css(txt,20,self.white,height=200,position='center')
        elif risk_type == '📈 I want to protect my savings from inflation.':
            if click_button('Find strategy'):
                seconds = randint(5,10)
                txt = 'Searching for trading strategy...'
                wait_message(txt,seconds)
                txt = '🙄 Strategy not available. Who cares about savings? Here we play big - win big!'
                markdown_css(txt,20,self.white,height=200,position='center')
        elif risk_type == '🙌 I have diamond hands!':
            self.diamond_hands()
        elif risk_type == '🚀 Lets go to the moon!':
            # txt = '💰🤑💰 Superb... Armstrong will be your surname!'
            # markdown_css(txt,self.text_size,self.white)
            st.caption('Under development, stay tuned!')

    def diamond_hands(self):
        txt = '💎 Great! Holding meme stonks is in your nature.'
        markdown_css(txt,self.text_size,self.white)

        # Building strategy
        st.write('')# empty line
        txt = 'Lets build your trading strategy'
        markdown_css(txt,25,f'{st.get_option("theme.primaryColor")}')
        
        # initialize current running session
        if 'current_session' not in st.session_state:
            st.session_state['current_session'] = ('start',None)
            txt = 'The workflow is simple and takes up to 9 minutes following these steps:'
            markdown_css(txt,self.text_size,f'{st.get_option("theme.primaryColor")}')
            self._steps_description(1,1,1,1,1)
            click_button('Start')

        # taking trading strategy parameters
        elif st.session_state['current_session'][0]=='start':
            self._steps_description(1,0,0,0,0)
            strategy_parameters = self.user_strategy_paramenters()
            if click_button('Set parameters'):
                st.session_state['current_session'] = ('input_for_strategy',strategy_parameters)
                st.experimental_rerun()

        # trading strategy parameters set
        elif st.session_state['current_session'][0]=='input_for_strategy':
            self._steps_description(1,0,0,0,0)
            strategy_parameters = st.session_state['current_session'][1]
            txt = 'Parameters set:'
            markdown_css(txt,self.text_size,self.white)
            txt = f'◦ Start date: {strategy_parameters[0]}'
            markdown_css(txt,self.text_size,self.white)
            txt = f'◦ End date: {strategy_parameters[1]}'
            markdown_css(txt,self.text_size,self.white)
            txt = f'◦ Stop loss: {strategy_parameters[2]}%'
            markdown_css(txt,self.text_size,self.white)
            txt = f'◦ Stop gain: {strategy_parameters[3]}%'
            markdown_css(txt,self.text_size,self.white)
            st.session_state['current_session'] = ('input_for_reddit',strategy_parameters)
            click_button('Next')

        # reddit input parameters
        elif st.session_state['current_session'][0]=='input_for_reddit':
            self._steps_description(0,1,0,0,0)
            strategy_parameters = st.session_state['current_session'][1]
            start_trade = strategy_parameters[0]
            input_for_reddit = self.reddit_user_input(start_trade)
            if click_button('Scrape Reddit posts'):
                st.session_state['current_session'] = ('scrape_posts',(input_for_reddit,strategy_parameters))
                st.experimental_rerun()

        # scrape posts
        elif st.session_state['current_session'][0]=='scrape_posts':
            self._steps_description(0,1,0,0,0)
            input_for_reddit,strategy_parameters = st.session_state['current_session'][1]
            comments = self.scrape_reddit_data(input_for_reddit)
            st.session_state['current_session'] = ('top10_comments',(comments,strategy_parameters))
            txt = f'Scraping reddit posts is done.'
            markdown_css(txt,self.text_size,self.white)

            click_button('Next')

        # top 10 comments by score
        elif st.session_state['current_session'][0]=='top10_comments':
            self._steps_description(0,0,1,0,0)
            comments,strategy_parameters = st.session_state['current_session'][1]
            txt = 'Top 10 comments with highest score:'
            markdown_css(txt,self.text_size,self.white)
            for i in range(10):
                c = comments[i]
                txt = f'{i+1}. '+ c.body
                txt = txt.replace("\n", "")
                markdown_css(txt,self.text_size,self.white,height=20)
            st.session_state['current_session'] = ('sentiment_analysis',(comments,strategy_parameters))
            click_button('Analyse posts and comments')

        # sentiment analysis
        elif st.session_state['current_session'][0] == 'sentiment_analysis':
            self._steps_description(0,0,1,0,0)
            comments,strategy_parameters = st.session_state['current_session'][1]
            analysed_comments = self.analyse_comments(comments)
            st.session_state['current_session'] = ('top10_comments_sentiment',(analysed_comments,strategy_parameters))
            txt = f'All posts and comments are analysed. Number of comments considered is {len(comments)}.'
            markdown_css(f'{txt}',self.text_size,self.white)
            click_button('Next')

        # top 10 comments with sentiment
        elif st.session_state['current_session'][0]=='top10_comments_sentiment':
            self._steps_description(0,0,1,0,0)
            analysed_comments,strategy_parameters = st.session_state['current_session'][1]
            st.session_state['current_session'] = ('trading',(analysed_comments,strategy_parameters))
            txt = 'Sentiment of top 10 comments with highest score (red is negative, green is positive, yellow is neutral):'
            markdown_css(txt,self.text_size,self.white)
            for i in range(10):
                com,sentiment = analysed_comments[i]
                if sentiment==1:
                    color = self.green
                elif sentiment==0:
                    color = self.yellow
                else:
                    color = self.red
                txt = f'{i+1}. '+ com.body
                txt = txt.replace("\n", "")
                markdown_css(txt,self.text_size,color,height=20)
            click_button('Start YOLO trading!')

        # yolo trading
        elif st.session_state['current_session'][0]=='trading':
            self._steps_description(0,0,0,1,0)
            analysed_comments,strategy_parameters = st.session_state['current_session'][1]
            df_buy_deals,df_sell_deals = self.YOLO_trade(analysed_comments,strategy_parameters) 
            st.session_state['current_session'] = ('display_trading_summary_baloon',(df_buy_deals,df_sell_deals))
            click_button('Trading summary')

        # summary with baloons
        elif st.session_state['current_session'][0] == 'display_trading_summary_baloon':
            st.balloons()
            self._steps_description(0,0,0,0,1)
            df_buy_deals,df_sell_deals = st.session_state['current_session'][1]
            self.trade_summary(df_buy_deals,df_sell_deals)
            st.session_state['current_session'] = ('display_trading_summary',st.session_state['current_session'][1])
            if click_button('Finished'):
                # add rate app
                del st.session_state['current_session']
                st.experimental_rerun()
            st.caption('Please click finished if you want to build another strategy.')

        # summary
        elif st.session_state['current_session'][0] == 'display_trading_summary':
            self._steps_description(0,0,0,0,1)
            buy,sell = st.session_state['current_session'][1]
            self.trade_summary(buy,sell)
            if click_button('Finished'):
                # add rate app
                del st.session_state['current_session']
                st.experimental_rerun()
            st.caption('Please click finished if you want to build another strategy.')

    def user_strategy_paramenters(self) -> tuple:
        # select start-end dates
        start_date = datetime.date.today() - datetime.timedelta(days=6)
        end_date = start_date + datetime.timedelta(days=5)
        start_trade = pd.to_datetime(st.text_input('Select start date for trading', f'{start_date}'))
        end_trade = pd.to_datetime(st.text_input('Select end date for trading', f'{end_date}'))
        # select stop loss/gain
        loss_options = [i for i in range(101)]
        gain_options = [i for i in range(101)]
        loss_txt = 'Select stop loss percentage (recommended below 10):'
        gain_txt = 'Select stop gain percentage (recommended below 10):'
        stop_loss = st.select_slider(loss_txt,loss_options,value = 5)
        stop_gain = st.select_slider(gain_txt,gain_options, value = 5)
        return start_trade,end_trade,stop_loss,stop_gain

    def reddit_user_input(self,start_trade:datetime) -> tuple:
        # select subreddit
        options = ['r/wallstreetbets', 'r/stocks', 'r/pennystocks', 'r/robinhood', 'r/GME', 'other']
        subreddit = st.selectbox('Select your favourite subreddit',options, index = 0)
        if subreddit == 'other':
            subreddit = st.text_input('Choose subreddit (e.g r/subRedditName, subRedditName)')
        subreddit = subreddit.strip() # remove trailing spaces
    
        # select start-end dates
        start_date = datetime.date.today() - datetime.timedelta(days=11)
        end_date = start_date + datetime.timedelta(days=4)
        start_reddit = pd.to_datetime(st.text_input('Select start date for reddit post', f'{start_date}'))
        txt = f'Select end date for reddit post (should be before start date of trading {start_trade.strftime("%Y-%m-%d")} to avoid forward looking bias.)'
        end_reddit = pd.to_datetime(st.text_input(txt, f'{end_date}'))
        
        # select number of submissions,comments, level
        num_subs,num_comments,max_level = '','',''
        num_subs = st.number_input('Select number of hottest posts\
                        the strategy will scrape through (recommended 10-100)', value = 20, step=1)
        if num_subs != '':
            num_subs = int(num_subs)
            num_comments = st.number_input("Select number of comments with most upvotes to consider (recommended 50-500)", value = 100, step=1)
        if num_comments != '':
            num_comments = int(num_comments)
            txt = 'Each reddit post has comments and replies to comments.\
                Replies can have their own replies and so on. This defines a tree of comments and replies.\
                We will use Breadth First Traversal to scrape all comments and replies. Define level of tree such that\
                level 0 considers only comments to the post, then\
                level 1 considers replies to comments, etc.'
            markdown_css(txt,12,self.white)
            max_level = st.number_input("Select maximum level of comments tree (recommended 1-10)", value = 5, step = 1)
        
        if max_level != '':
            max_level = int(max_level)
        if num_subs == '':
            st.write('Please choose number of hottest posts.')
            return '','','','',''
        elif num_comments == '':
            st.write('Please choose number of comments.')
            return '','','','',''
        elif max_level == '':
            st.write('Please choose level.')
            return '','','','',''
        return subreddit, start_reddit, end_reddit, num_subs, num_comments, max_level

    def scrape_reddit_data(self, user_input:tuple) -> 'list[praw.models.Comment]':
        subreddit, start, end, num_subs, num_comments, max_level = user_input
        # reddit object
        reddit = praw.Reddit(
                client_id=st.secrets["client_id"],
                client_secret=st.secrets["client_secret"],
                user_agent=st.secrets["user_agent"],
                username=st.secrets["username"],
                password=st.secrets["password"],
                )
        if subreddit[:2]=='r/':
            subreddit = subreddit[2:]
        r_subreddit = reddit.subreddit(subreddit)
        sub_placeholder = st.empty()
        com_placeholder = st.empty()
        bar = st.progress(0)
        i = 0
        comments = []
        submissions = []
        denom = num_subs+1
        for r_submission in r_subreddit.hot(limit=None):
            if not self._within_time_interval(r_submission,start,end):
                continue
            i += 1
            bar.progress(i/denom)
            if num_subs == 0:
                break
            submissions.append(r_submission)
            num_subs -= 1
            sub_placeholder.text(f'Scraping post: "{r_submission.title}"')

            # handle More Comments tabs
            r_submission.comments.replace_more(limit=0)

            # seed level for BFS
            seed = []
            for comment in r_submission.comments[:]:
                if not self._within_time_interval(comment,start,end):
                    continue
                seed.append((comment,0))
            if len(seed)==0:
                continue
            # sort comments in submission by score 
            seed.sort(key = lambda x: x[0].score, reverse = True) 

            # print top comment in reddit submission
            com_placeholder.text(f'Top comment in post: {seed[0][0].body}')

            # BFS to scrape through comments and replies
            queue = deque(seed[:num_comments]) # take only top comments
            level = 0
            while queue:
                comment,level = queue.popleft()
                if not self._within_time_interval(comment,start,end):
                    continue
                if level<=max_level:
                    comments.append(comment)
                    queue.extend([(com,level+1) for com in comment.replies])
            comments = comments[1:]

        # sort comments by score
        comments.sort(key = lambda x: x.score, reverse = True)
        bar.progress(1.00)
        sub_placeholder.empty()
        com_placeholder.empty()
        return comments

    def analyse_comments(self, comments: 'list[praw.models.Comment]') -> list:
        # dislpay sentiment
        self.placeholder = st.empty()
        bar = st.progress(0)
        i = 0
        analysed_comments = []
        for com in comments:
            sentiment = self._nltk_sentiment(com.body)
            analysed_comments.append((com,sentiment))
            if len(com.body)>88:
                combody = com.body[:88].replace('\n','')
                txt = f'Comment: {combody} ...'
            else:
                txt = f'Comment: {com.body}'
            if sentiment==1:
                color = self.green
            elif sentiment==0:
                color = self.yellow
            else:
                color = self.red
            self._markdown_css(txt,self.text_size,color,placeholder=True)
            i+=1
            bar.progress(i/len(comments))
        self.placeholder = st.empty()
        return analysed_comments

    def YOLO_trade(self, analysed_comments: 'list[tuple[praw.models.Comment,str]]', strategy_parameters:tuple) -> 'tuple[list]':
        # loading tickers between certain times
        @st.cache(show_spinner=False)
        def _load_tickers_data(ticker:str, start:str, end:str):
            ticker = yf.Ticker(ticker)
            data = ticker.history(start=start,end=end,interval='1h')
            return data

        buy,sell = [],[]
        start_trade,end_trade,stop_loss, stop_gain = strategy_parameters
        stop_loss, stop_gain =1,1
        end_date = end_trade.strftime('%Y-%m-%d')
        end = end_trade.strftime('%Y-%m-%d %H:%M:S')
        symbols = self._get_symbols()

        # open positions based on sentiment
        # dislpay trades
        txt = 'Opening trading positions'
        self._markdown_css(txt,self.text_size,self.white)
        self.placeholder = st.empty()
        bar = st.progress(0)
        i = 0
        for com,sentiment in analysed_comments:
            words = re.split("\s|(?<!\d)[,.](?!\d)", com.body)
            for w in words:
                if w in symbols:
                    if sentiment==1:
                        date = datetime.datetime.utcfromtimestamp(com.created_utc).strftime('%Y-%m-%d %H:%M:%S')
                        buy.append((w,date))
                        txt = f'Buy: {symbols[w]} ({w}) on {date}'
                        self._markdown_css(txt,self.text_size,self.green,placeholder=True)
                        time.sleep(0.1)
                    elif sentiment==-1:
                        date = datetime.datetime.utcfromtimestamp(com.created_utc).strftime('%Y-%m-%d %H:%M:%S')
                        sell.append((w,date))
                        txt = f'Sell: {symbols[w]} ({w}) on {date}'
                        self._markdown_css(txt,self.text_size,self.red,placeholder=True)
                        time.sleep(0.1)
            i+=1
            bar.progress(i/len(analysed_comments))
        buy.sort(key=lambda x:x[1])
        sell.sort(key=lambda x:x[1])

        # close positions based on stop loss/gain and end date of trading
        # dislpay trades
        denom = len(buy)+len(sell)
        txt = 'Closing trading positions'
        self._markdown_css(txt,self.text_size,self.white)
        self.placeholder = st.empty()
        bar = st.progress(0)
        i = 0
        denom = len(buy)+len(sell)
        symbols = self._get_symbols()
        buy_deals,sell_deals = [],[]
        for ticker,start in buy:
            start_date, _ = start.split(' ')
            data = _load_tickers_data(ticker, start_date, end_date)
            data = data[data.index>=start]
            open = self._find_opening_price(data,start)
            close_date,close =  self._find_closing_price(data,open,stop_loss,stop_gain,True,end)
            buy_deals.append((ticker,symbols[ticker],open,close,start,close_date))
            txt = f'Sell: {symbols[ticker]} ({ticker}) on {close_date}'
            self._markdown_css(txt,self.text_size,self.red,placeholder=True)
            i+=1
            bar.progress(i/denom)

        for ticker,start in sell:
            start_date, _ = start.split(' ')
            data = _load_tickers_data(ticker, start_date, end_date)
            data = data[data.index>=start]
            open = self._find_opening_price(data,start)
            close_date, close =  self._find_closing_price(data,open,stop_loss,stop_gain,False,end)
            sell_deals.append((ticker,symbols[ticker],open,close,start,close_date))
            txt = f'Buy: {symbols[ticker]} ({ticker}) on {close_date}'
            self._markdown_css(txt,self.text_size,self.green,placeholder=True)
            i+=1
            bar.progress(i/denom)

        df_buy_deals,df_sell_deals = pd.DataFrame(buy_deals),pd.DataFrame(sell_deals)
        df_buy_deals.columns = ['ticker','company','open','close','open_time','close_time']
        df_sell_deals.columns = ['ticker','company','open','close','open_time','close_time']
        df_buy_deals['profit'] = df_buy_deals['close']-df_buy_deals['open']
        df_sell_deals['profit'] = df_sell_deals['open']-df_sell_deals['close']
        df_buy_deals.sort_values(by=['ticker','open_time'],inplace = True)
        df_sell_deals.sort_values(by=['ticker','open_time'],inplace = True)
        df_buy_deals['volume'],df_sell_deals['volume'] = 1,1
        return df_buy_deals,df_sell_deals

    def trade_summary(self, df_buy_deals:pd.DataFrame, df_sell_deals:pd.DataFrame):
        df_buy_grouped = df_buy_deals.groupby('ticker')['profit'].sum().reset_index()
        df_sell_grouped = df_sell_deals.groupby('ticker')['profit'].sum().reset_index()
        df_grouped = pd.concat([df_buy_grouped,df_sell_grouped]).groupby('ticker')['profit'].sum().reset_index()
        
        # currency
        # df_buy_deals['currency'] = [self._get_currency(ticker) for ticker in df_buy_grouped['ticker']]
        # df_sell_deals['currency'] = [self._get_currency(ticker) for ticker in df_sell_grouped['ticker']]
        if st.checkbox('Summary',value=True):
            long,short = len(df_buy_deals),len(df_sell_deals)
            trades = long+short
            profit = sum(df_grouped['profit'])
            txt = f'Total number of trades is {trades}'
            markdown_css(txt,self.text_size,self.white)
            txt = f'Number of opened long positions is {long}'
            markdown_css(txt,self.text_size,self.white)
            txt = f'Number of opened short positions is {short}'
            markdown_css(txt,self.text_size,self.white)
            txt = f'Total money made: {profit} USD'
            markdown_css(txt,self.text_size,self.white)
            fig = px.bar(df_grouped, x='ticker', y='profit',\
                    color='profit',height=500,\
                    title='Long deals',color_continuous_scale='Bluered_r')
            st.plotly_chart(fig, use_container_width=True)

        # profit barplots by ticker
        if st.checkbox('Long deals profit'):
            profit = sum(df_buy_grouped['profit'])
            txt = f'Total money made: {profit} USD'
            markdown_css(txt,self.text_size,self.white)
            fig = px.bar(df_buy_grouped, x='ticker', y='profit',\
                color='profit',height=500,\
                title='Long deals',color_continuous_scale='Bluered_r')
            st.plotly_chart(fig, use_container_width=True)
        # profit barplots by ticker
        if st.checkbox('Short deals profit'):
            profit = sum(df_sell_grouped['profit'])
            txt = f'Total money made: {profit} USD'
            markdown_css(txt,self.text_size,self.white)
            fig = px.bar(df_sell_grouped, x='ticker', y='profit',\
                    color='profit',height=500,\
                    title='Long deals',color_continuous_scale='Bluered_r')
            st.plotly_chart(fig, use_container_width=True)

        # long/short volumes
        if st.checkbox('Long deals volumes'):
            df_buy_volumes = df_buy_deals.groupby('ticker')['volume'].sum().reset_index()
            fig = px.bar(df_buy_deals, x='ticker', y='volume',\
                    color='volume',height=500,\
                    title='Long deals')
            st.plotly_chart(fig, use_container_width=True)

        if st.checkbox('Short deals volumes'):
            df_sell_volumes = df_sell_deals.groupby('ticker')['volume'].sum().reset_index()
            fig = px.bar(df_sell_volumes, x='ticker', y='volume',\
                    color='volume',height=500,\
                    title='Long deals')
            st.plotly_chart(fig, use_container_width=True)

        # long/short deals data
        if st.checkbox('Show long deals data'):
            st.write(df_buy_deals)
            download=click_button('Download csv')
            if download:
                csv = df_buy_deals.to_csv(index=False)
                b64 = base64.b64encode(csv.encode()).decode()  # some strings
                linko= f'<a href="data:file/csv;base64,{b64}" download="long_deals.csv">Click to download </a>'
                st.markdown(linko, unsafe_allow_html=True)
        if st.checkbox('Show short deals data'):
            st.write(df_sell_deals)
            download=click_button('Download csv')
            if download:
                csv = df_sell_deals.to_csv(index=False)
                b64 = base64.b64encode(csv.encode()).decode()  # some strings
                linko= f'<a href="data:file/csv;base64,{b64}" download="short_deals.csv">Click to download </a>'
                st.markdown(linko, unsafe_allow_html=True)
            

        if st.checkbox('Show trades'):
            symbols = self._get_symbols()
            col1,col2 = st.columns(2)
            for i in range(len(df_buy_deals)):
                ticker = df_buy_deals.iloc[i]['ticker']
                date = df_buy_deals.iloc[i]['open_time']
                txt = f'Buy: {symbols[ticker]} ({ticker}) on {date}'
                markdown_css(txt,self.text_size,self.green,col=col1)
            for i in range(len(df_sell_deals)):
                ticker = df_buy_deals.iloc[i]['ticker']
                date = df_buy_deals.iloc[i]['open_time']
                txt = f'Sell: {symbols[ticker]} ({ticker}) on {date}'
                markdown_css(txt,self.text_size,self.red,col=col2)
    @st.cache
    def _get_currency(self, ticker:str) -> str:
        ticker = yf.Ticker(ticker)
        return ticker.info['currency']

    def _find_opening_price(self, data:pd.DataFrame, start:str):
        for i in range(len(data)):
            if data.index[i].strftime('%Y-%m-%d %H:%M:%S')>=start:
                return data.iloc[i]['Open']

    def _find_closing_price(self, data:pd.DataFrame ,open:float ,stop_loss:float ,stop_gain:float ,buy:bool,end:str):
        if buy:
            close_loss_level = open*(1-stop_loss/100) if stop_loss<101 else 0
            close_gain_level = open*(1+stop_gain/100)
        else:
            close_loss_level = open*(1+stop_loss/100) if stop_loss<101 else float('inf')
            close_gain_level = open*(1-stop_gain/100)
        for i in range(len(data)):
            if data.iloc[i]['Open']>=max(close_loss_level,close_gain_level):
                close_date = data.index[i].strftime('%Y-%m-%d %H:%M:%S')
                return  close_date, max(close_loss_level,close_gain_level)
            elif data.iloc[i]['Open']<=min(close_loss_level,close_gain_level):
                close_date = data.index[i].strftime('%Y-%m-%d %H:%M:%S')
                return close_date, min(close_loss_level,close_gain_level)
        return end, self._find_opening_price(data, end)

    def _get_symbols(self):
        with open('context/symbols_dict.pickle','rb') as f:
            symbols = pickle.load(f)
        return symbols

    def _nltk_sentiment(self, text: str):
        sia = SentimentIntensityAnalyzer()
        sub_entries_nltk = {'negative': 0, 'positive' : 0, 'neutral' : 0}
        vs = sia.polarity_scores(text)
        if not vs['neg'] > 0.05:
            if vs['pos'] - vs['neg'] > 0:
                sub_entries_nltk['positive'] = sub_entries_nltk['positive'] + 1
                return 1
            else:
                sub_entries_nltk['neutral'] = sub_entries_nltk['neutral'] + 1
                return 0

        elif not vs['pos'] > 0.05:
            if vs['pos'] - vs['neg'] <= 0:
                sub_entries_nltk['negative'] = sub_entries_nltk['negative'] + 1
                return -1
            else:
                sub_entries_nltk['neutral'] = sub_entries_nltk['neutral'] + 1
                return 0
        else:
            sub_entries_nltk['neutral'] = sub_entries_nltk['neutral'] + 1
            return 0

    def _within_time_interval(self, reddit_obj: praw.models, start:datetime, end: datetime):
        utc_time = datetime.datetime.utcfromtimestamp(reddit_obj.created_utc).strftime('%Y-%m-%d')
        datetime_time = pd.to_datetime(utc_time)
        if datetime_time < start or datetime_time > end:
            return False
        return True

    def _steps_description(self,is_run1:bool,is_run2:bool,is_run3:bool,\
                        is_run4:bool,is_run5:bool,runColor=st.get_option("theme.primaryColor"),\
                        nonrunColor='#631126'):

        txt = '1. Select parameters for trading strategy'
        color = f"{is_run1*runColor+(1-is_run1)*nonrunColor}"
        markdown_css(txt,self.text_size,color)
        
        txt = '2. Scrape through Reddit posts'
        color = f"{is_run2*runColor+(1-is_run2)*nonrunColor}"
        markdown_css(txt,self.text_size,color)

        txt = '3. Sentiment analysis on Reddit posts'
        color = f"{is_run3*runColor+(1-is_run3)*nonrunColor}"
        markdown_css(txt,self.text_size,color)

        txt = '4. YOLO trading'
        color = f"{is_run4*runColor+(1-is_run4)*nonrunColor}"
        markdown_css(txt,self.text_size,color)

        txt = '5. Generate summary of trading results'
        color = f"{is_run5*runColor+(1-is_run5)*nonrunColor}"
        markdown_css(txt,self.text_size,color)

    def _markdown_css(self,txt:str, font_size:int, color:str, height:int = 17, position:str = 'left',col:int = 1, placeholder: bool = False) -> None:
        css_txt = f'<p style="font-family:sans-serif;color:{color};font-size: {font_size}px;text-align:{position};line-height: {height}px;"> {txt} </p>'
        if not placeholder:
            if col==1:
                st.markdown(css_txt, unsafe_allow_html=True)
            else:
                col.markdown(css_txt, unsafe_allow_html=True)
        else:
            self.placeholder.markdown(css_txt, unsafe_allow_html=True)
        