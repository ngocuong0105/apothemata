import praw
from prawcore.sessions import session
import streamlit as st
from collections import deque
from random import randint
import time
import pandas as pd
import regex as re
import collections
import nltk
nltk.download('vader_lexicon', quiet = True)
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from datetime import datetime
import pickle

from page import Page

class trade(Page):
    def __init__(self, title: str) -> None:
        super().__init__(title)
        self.keycount = 0
        
    def load_page(self):
        strategy = self.get_sidebar_input()
        if strategy == '🚀 Reddit Power':
            st.header(f'{strategy}')
            self.reddit_strategy()
        elif strategy == '💬 Tweet It!':
            st.header(f'{strategy}')
            
        elif strategy == '🇺🇸 I believe Fox News':
            st.header(f'{strategy}')
            pressed = self._click_button('Find strategy')
            if pressed:
                seconds = randint(5,10)
                self._wait_message(seconds)
                txt = '🤪 No strategy found. We are sorry you are retarded.'
                self._markdown_css(txt,20,'white',height=200)

    def get_sidebar_input(self) -> str:
        st.sidebar.header('Please provide input:')
        options = ['🚀 Reddit Power', '💬 Tweet It!', '🇺🇸 I believe Fox News', '']
        strategy = st.sidebar.selectbox('Select trading strategy',options, index = len(options)-1)
        return strategy
    
    def _wait_message(self,seconds):
        placeholder = st.empty()
        placeholder.text('Searching for trading strategy...')
        bar = st.progress(0)
        for i in range(seconds):
            # Update the progress bar with each iteration.
            bar.progress((i+1)/seconds)
            time.sleep(1)
        bar.empty()
        placeholder.empty()

    def reddit_strategy(self):
        options =  ['I want to make a risk-averse long term investment.',
                    'I want to protect my savings from inflation.',
                    'I have diamond hands!',
                    'Lets go to the moon!',
                    '']
        
        risk_type = st.selectbox('What is your risk appetite?', options, index = len(options)-1)

        if risk_type == 'I want to make a risk-averse long term investment.':
            seconds = randint(5,10)
            self._wait_message(seconds)
            txt = '😬 Risk-averse, really? Sorry you are using the wrong Web App.'
            self._markdown_css(txt,20,'white',height=200)
        elif risk_type == 'I want to protect my savings from inflation.':
            seconds = randint(5,10)
            self._wait_message(seconds)
            txt = '🙄 Strategy not available. Who cares about savings? Here we play big - win big!'
            self._markdown_css(txt,20,'white',height=200)
        elif risk_type == 'I have diamond hands!':
            txt = '💎 Great! Holding meme stonks is in your nature.'
            self._markdown_css(txt,14,'white',height=17,position='left')
            options = ['r/wallstreetbets', 'r/stocks', 'r/pennystocks', 'r/robinhood', 'r/GME', 'other', '']
            subreddit = st.selectbox('Select your favourite subreddit',options, index = len(options)-1)
            if subreddit == 'other':
                subreddit = st.text_input('Choose subreddit (e.g r/subRedditName, subRedditName)')
            subreddit = subreddit.strip() # remove trailing spaces
            if subreddit == '':
                return

            user_input = self._reddit_user_input()
            pressed = self._click_button('Build Strategy')
            # init current running session
            if 'current_session' not in st.session_state:
                st.session_state['current_session'] = ('building_strategy',None) # name,data
            if st.session_state['current_session'][0]=='building_strategy':
                if pressed and 'r/' in subreddit[:2]:
                    comments = self._load_reddit_data(subreddit[2:],user_input)
                    st.session_state['current_session'] = ('trading',comments)
                    self._click_button('YOLO start trading!')
                elif pressed:
                    comments = self._load_reddit_data(subreddit, user_input)
                    st.session_state['current_session'] = ('trading',comments)
                    self._click_button('YOLO start trading!')
            elif st.session_state['current_session'][0]=='trading':
                buy,sell = self._YOLO_trade(st.session_state['current_session'][1]) # takes data from prev session
                st.session_state['current_session'] = ('display_trading_summary',(buy,sell))
                self._click_button('Generate trading summary.')
            elif st.session_state['current_session'][0] == 'display_trading_summary':
                buy,sell = st.session_state['current_session'][1]
                self._trade_summary(buy,sell)

        elif risk_type == 'Lets go to the moon!':
            st.write('💰🤑💰 Superb... Armstrong will be your surname!')

    def _reddit_user_input(self) -> tuple:
        txt = 'Lets build your trading strategy'
        self._markdown_css(txt,25,'#F63366')

        txt = 'We will scrape through popular reddit posts and execute trades based on users sentiment'
        self._markdown_css(txt,14,'white', height=17, position='left')

        start = pd.to_datetime(st.text_input('Select start date', '2021-09-01'))
        end = pd.to_datetime(st.text_input('Select end date', '2021-09-15'))

        num_subs,num_comments,max_level = '','',''

        num_subs = st.number_input('Select number of hottest submissions\
                        the strategy will scrape through (recommended 10-100)', value = 20, step=1)
        if num_subs != '':
            num_subs = int(num_subs)
            num_comments = st.number_input("Select number of comments with most upvotes to consider (recommended 50-500)", value = 50, step=1)
        if num_comments != '':
            num_comments = int(num_comments)
            txt = 'Each reddit submission has comments and replies to comments.\
                Replies can have their own replies and so on. This defines a tree of comments and replies.\
                We will use Breadth First Traversal to scrape all comments and replies. Define level of tree such that\
                level 0 considers only comments to the submission, then\
                level 1 considers replies to comments, etc.'
            self._markdown_css(txt,14,'white',height=17,position='left')
            max_level = st.number_input("Select maximum level of comments tree (recommended 1-10)", value = 5, step = 1)
        
        if max_level != '':
            max_level = int(max_level)
        if num_subs == '':
            st.write('Please choose number of hottest submissions.')
            return '','','','',''
        elif num_comments == '':
            st.write('Please choose number of comments.')
            return '','','','',''
        elif max_level == '':
            st.write('Please choose level.')
            return '','','','',''
        return start, end, num_subs, num_comments, max_level

    def _load_reddit_data(self, subreddit:str, user_input:tuple) -> 'list[praw.models.Comment]':
        start, end, num_subs, num_comments, max_level = user_input
        # reddit object
        reddit = praw.Reddit(
                client_id=st.secrets["client_id"],
                client_secret=st.secrets["client_secret"],
                user_agent=st.secrets["user_agent"],
                username=st.secrets["username"],
                password=st.secrets["password"],
                )

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
            sub_placeholder.text(f'Scraping submission: "{r_submission.title}"')

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
            com_placeholder.text(f'Top comment in submission: {seed[0][0].body}')

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
        sub_placeholder.empty()
        com_placeholder.empty()
        st.write('Scraping submissions is done!')
        return comments

    def _YOLO_trade(self, comments: 'list[praw.models.Comment]') -> 'tuple[dict]':
        buy = collections.defaultdict(int)
        sell = collections.defaultdict(int)
        with open('context/symbols_dict.pickle','rb') as f:
            symbols = pickle.load(f)
        
        # dislpay trades
        self.placeholder = st.empty()
        bar = st.progress(0)
        i = 0
        # sentiment analysis for each comment
        for com in comments:
            words = re.split("\s|(?<!\d)[,.](?!\d)", com.body)
            for w in words:
                if w in symbols:
                    sentiment = self._nltk_sentiment(com.body)
                    if sentiment=='Positive':
                        date = datetime.utcfromtimestamp(com.created_utc).strftime('%Y-%m-%d %H:%M:%S')
                        buy[(w,date)]+=1
                        txt = f'Buy: {symbols[w]} ({w}) on {date}'
                        self._markdown_css(txt,font_size=14,color='green',height=17,position='left',placeholder=True)
                        time.sleep(0.1)
                    elif sentiment=='Negative':
                        date = datetime.utcfromtimestamp(com.created_utc).strftime('%Y-%m-%d %H:%M:%S')
                        sell[(w,date)]+=1
                        txt = f'Sell: {symbols[w]} ({w}) on {date}'
                        self._markdown_css(txt,font_size=14,color='red',height=17,position='left',placeholder=True)
                        time.sleep(0.1)
            i+=1
            bar.progress(i/len(comments))
        return buy,sell

    def _trade_summary(self, buy, sell):
        with open('context/symbols_dict.pickle','rb') as f:
            symbols = pickle.load(f)
        trades = len(buy)+len(sell)
        if st.checkbox('Show trades'):
            col1,col2 = st.columns(2)
            for w,date in buy:
                txt = f'Buy: {symbols[w]} ({w}) on {date}'
                self._markdown_css(txt,font_size=14,height=17,color='green',position='left',col=col1)
            for w,date in sell:
                txt = f'Sell: {symbols[w]} ({w}) on {date}'
                self._markdown_css(txt,font_size=14,height=17,color='red',position='right',col=col2)

    def _nltk_sentiment(self, text: str):
        sia = SentimentIntensityAnalyzer()
        sub_entries_nltk = {'negative': 0, 'positive' : 0, 'neutral' : 0}
        vs = sia.polarity_scores(text)
        if not vs['neg'] > 0.05:
            if vs['pos'] - vs['neg'] > 0:
                sub_entries_nltk['positive'] = sub_entries_nltk['positive'] + 1
                return 'Positive'
            else:
                sub_entries_nltk['neutral'] = sub_entries_nltk['neutral'] + 1
                return 'Neutral'

        elif not vs['pos'] > 0.05:
            if vs['pos'] - vs['neg'] <= 0:
                sub_entries_nltk['negative'] = sub_entries_nltk['negative'] + 1
                return 'Negative'
            else:
                sub_entries_nltk['neutral'] = sub_entries_nltk['neutral'] + 1
                return 'Neutral'
        else:
            sub_entries_nltk['neutral'] = sub_entries_nltk['neutral'] + 1
            return 'Neutral'

    def _within_time_interval(self, reddit_obj: praw.models, start:datetime, end: datetime):
        utc_time = datetime.utcfromtimestamp(reddit_obj.created_utc).strftime('%Y-%m-%d')
        datetime_time = pd.to_datetime(utc_time)
        if datetime_time < start or datetime_time > end:
            return False
        return True

    def _click_button(self, txt:str, on_click = None, args = None):
        back_color = st.get_option('theme.primaryColor')
        placeholder = st.empty()
        placeholder.markdown(f"<style>div.stButton > button:first-child {{background-color:{back_color};color:white;font-size:16px;text-align:center;}} </style>", unsafe_allow_html=True)
        pressed = st.button(f'{txt}', on_click = on_click, args = args)
        if pressed:
            back_color = st.get_option('theme.textColor')
            placeholder.markdown(f"<style>div.stButton > button:first-child {{background-color:{back_color};color:white;font-size:16px;text-align:center;}} </style>", unsafe_allow_html=True)
        return pressed

    def _markdown_css(self,txt:str, font_size:int, color:str, height:int = 100, position:str = 'center',col:int = 1, placeholder: bool = False) -> None:
        css_txt = f'<p style="font-family:sans-serif;color:{color};font-size: {font_size}px;text-align:{position};line-height: {height}px;"> {txt} </p>'
        if not placeholder:
            if col==1:
                st.markdown(css_txt, unsafe_allow_html=True)
            else:
                col.markdown(css_txt, unsafe_allow_html=True)
        else:
            self.placeholder.markdown(css_txt, unsafe_allow_html=True)
        