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
                css_txt = f'<p style="font-family:sans-serif;color:white;font-size: 20px;text-align:center;line-height: 150px;"> {txt} </p>'
                st.markdown(css_txt, unsafe_allow_html=True)


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
            seconds = randint(2,10)
            self._wait_message(seconds)
            st.write('😬 Risk-averse, really? Sorry you are using the wrong Web App.')
        elif risk_type == 'I want to protect my savings from inflation.':
            seconds = randint(2,10)
            self._wait_message(seconds)
            st.write('🙄 Strategy not available. Who cares about savings? Here we play big - win big!')
        elif risk_type == 'I have diamond hands!':
            st.write('💎 Great! Holding meme stonks is in your nature.')
            options = ['r/wallstreetbets', 'r/stocks', 'r/pennystocks', 'r/robinhood', 'r/GME', 'other', '']
            subreddit = st.selectbox('Select your favourite subreddit',options, index = len(options)-1)
            if subreddit == 'other':
                subreddit = st.text_input('Choose subreddit (e.g r/subRedditName, subRedditName)')
            subreddit = subreddit.strip() # remove trailing spaces
            if subreddit == '':
                return

            user_input = self._reddit_user_input()
            pressed = self._click_button('Build Strategy')
            if pressed and 'r/' in subreddit[:2] and 'trading ' not in st.session_state:
                comments = self._load_reddit_data(subreddit[2:],user_input)
            elif pressed and 'trading ' not in st.session_state:
                comments = self._load_reddit_data(subreddit, user_input)
            if 'scrapping_submission' in st.session_state:
                trade = self._click_button('YOLO start trading!')
                st.session_state['trading'] = False
                if trade : 
                    self._YOLO_trade(st.session_state['scrapping_submission'])
                    del st.session_state['trading']
                    del st.session_state['scrapping_submission']

        elif risk_type == 'Lets go to the moon!':
            st.write('🤑 Superb... Armstrong will be your surname!')

    def _reddit_user_input(self) -> tuple:
        txt = '<p style="font-family:sans-serif; color:#F63366; font-size: 21px;"> Lets build your trading strategy</p>'
        st.markdown(txt, unsafe_allow_html=True)
        txt = '<p style="font-family:sans-serif; color: white; font-size: 14px;"> We will scrape through popular reddit posts and execute trades based on users sentiment.</p>'
        st.markdown(txt, unsafe_allow_html=True)

        start = pd.to_datetime(st.text_input('Select start date', '2021-09-01'))
        end = pd.to_datetime(st.text_input('Select end date', '2021-09-15'))

        num_subs,num_comments,max_level = '','',''

        num_subs = st.number_input('Select number of hottest submissions\
                        the strategy will scrape through (recommended 10-80)', value = 20, step=1)
        if num_subs != '':
            num_subs = int(num_subs)
            num_comments = st.number_input("Select number of comments with most upvotes to consider (recommended 10-150)", value = 50, step=1)
        if num_comments != '':
            num_comments = int(num_comments)
            txt = 'Each reddit submission has comments and replies to comments.\
                Replies can have their own replies and so on. This defines a tree of comments and replies.\
                We will use Breadth First Traversal to scrape all comments and replies. Define level of tree such that\
                level 0 considers only comments to the submission, then\
                level 1 considers replies to comments, etc.'

            css_txt = f'<p style="font-family:sans-serif; color:white ; font-size: 12px;"> {txt} </p>'
            st.markdown(css_txt, unsafe_allow_html=True)
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
        st.session_state['scrapping_submission'] = comments
        return comments

    def _YOLO_trade(self, comments: 'list[praw.models.Comment]'):
        buy = collections.defaultdict(int)
        sell = collections.defaultdict(int)
        with open('context/symbols_dict.pickle','rb') as f:
            symbols = pickle.load(f)
        # sentiment analysis for each comment
        for com in comments:
            words = re.split("\s|(?<!\d)[,.](?!\d)", com.body)
            for w in words:
                if w in symbols:
                    sentiment = self._nltk_sentiment(com.body)
                    if sentiment=='Positive':
                        buy[w]+=1
                        date = datetime.utcfromtimestamp(com.created_utc).strftime('%Y-%m-%d')
                        time.sleep(0.1)
                        st.write(f'Buy: {symbols[w]} ({w}) on {date}')
                    elif sentiment=='Negative':
                        sell[w]+=1
                        date = datetime.utcfromtimestamp(com.created_utc).strftime('%Y-%m-%d')
                        time.sleep(0.1)
                        st.write(f'Sell: {symbols[w]} ({w}) on {date}')
        
    
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
        st.markdown("""
            <style>
            div.stButton > button:first-child {
                background-color: #F63366;
                text-align:center;
            }
            </style>""", unsafe_allow_html=True)
        pressed = st.button(f'{txt}', on_click = on_click, args = args)
        return pressed


        # # save comments
        # st.write(len(comments))
        # st.write(len(submissions))
        # import pickle
        # with open('comments.pickle', 'wb') as f:
        #     pickle.dump(comments, f)
        # with open('submissions.pickle', 'wb') as f1:
        #     pickle.dump(submissions, f1)
    