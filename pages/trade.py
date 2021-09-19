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
            st.caption('Under developement, stay tuned!')
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
        options =  ['I want to make a risk-averse long term investment.',
                    'I want to protect my savings from inflation.',
                    'I have diamond hands!',
                    'Lets go to the moon!',
                    '']
        risk_type = st.selectbox('What is your risk appetite?', options, index = len(options)-1)

        if risk_type == 'I want to make a risk-averse long term investment.':
            if click_button('Find strategy'):
                seconds = randint(5,10)
                txt = 'Searching for trading strategy...'
                wait_message(txt,seconds)
                txt = '😬 Risk-averse, really? Sorry you are using the wrong Web App.'
                markdown_css(txt,20,self.white,height=200,position='center')
        elif risk_type == 'I want to protect my savings from inflation.':
            if click_button('Find strategy'):
                seconds = randint(5,10)
                txt = 'Searching for trading strategy...'
                wait_message(txt,seconds)
                txt = '🙄 Strategy not available. Who cares about savings? Here we play big - win big!'
                markdown_css(txt,20,self.white,height=200,position='center')
        elif risk_type == 'I have diamond hands!':
            self.diamond_hands()
        elif risk_type == 'Lets go to the moon!':
            # txt = '💰🤑💰 Superb... Armstrong will be your surname!'
            # markdown_css(txt,self.text_size,self.white)
            st.caption('Under developement, stay tuned!')

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
                txt = 'The workflow is simple and takes up to 5 minutes following these steps:'
                markdown_css(txt,self.text_size,f'{st.get_option("theme.primaryColor")}')
                self._steps_description(1,1,1,1,1)
                click_button('Start')

            elif st.session_state['current_session'][0]=='start':
                self._steps_description(1,0,0,0,0)
                user_input = self._reddit_user_input()
                if click_button('Scrape Reddit posts'):
                    st.session_state['current_session'] = ('load_data',user_input)
                    st.experimental_rerun()
            elif st.session_state['current_session'][0]=='load_data':
                self._steps_description(1,0,0,0,0)
                user_input = st.session_state['current_session'][1]
                comments = self._load_reddit_data(user_input)
                st.session_state['current_session'] = ('building_strategy',comments)
                st.session_state['current_session'] = ('input_for_strategy',comments)
                txt = 'Scraping reddit posts is done.'
                markdown_css(txt,self.text_size,self.white)
                click_button('Next')
            elif st.session_state['current_session'][0]=='input_for_strategy':
                self._steps_description(0,1,0,0,0)
                comments = st.session_state['current_session'][1]
                strategy_parameters = self._user_strategy_paramenters()
                if click_button('Set parameters'):
                    st.session_state['current_session'] = ('before_building_strategy',(comments,strategy_parameters))
                    st.experimental_rerun()
            elif st.session_state['current_session'][0]=='before_building_strategy':
                self._steps_description(0,1,0,0,0)
                strategy_parameters = st.session_state['current_session'][1][1]
                txt = 'Parameters set:'
                markdown_css(txt,self.text_size,self.white)
                if strategy_parameters[0]!=101:
                    txt = f'① Stop loss is {strategy_parameters[0]}%'
                else:
                    txt = f'① Stop loss is disabled'
                markdown_css(txt,self.text_size,self.white)
                txt = f'② Stop gain is {strategy_parameters[1]}%'
                markdown_css(txt,self.text_size,self.white)
                st.session_state['current_session'] = ('sentiment_analysis',st.session_state['current_session'][1])
                click_button('Next')
            elif st.session_state['current_session'][0]=='sentiment_analysis':
                self._steps_description(0,0,1,0,0)
                comments,parameters = st.session_state['current_session'][1]
                txt = 'Top 10 comments with highest score:'
                markdown_css(txt,self.text_size,self.white)
                for i in range(10):
                    c = comments[i]
                    txt = f'{i+1}. '+ c.body
                    txt = txt.replace("\n", "")
                    markdown_css(txt,self.text_size,self.white,height=20)
                st.session_state['current_session'] = ('sentiment_analysis1',st.session_state['current_session'][1])
                click_button('Analyse posts and comments')
            elif st.session_state['current_session'][0] == 'sentiment_analysis1':
                self._steps_description(0,0,1,0,0)
                comments,parameters = st.session_state['current_session'][1]
                analysed_comments = self._analyse_comments(comments,parameters)
                st.session_state['current_session'] = ('before_trading',analysed_comments)
                txt = 'All posts and comments are analysed.'
                markdown_css(f'{txt}',self.text_size,self.white)
                click_button('Next')
            elif st.session_state['current_session'][0]=='before_trading':
                self._steps_description(0,0,1,0,0)
                analysed_comments = st.session_state['current_session'][1]
                st.session_state['current_session'] = ('trading',analysed_comments)
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
            elif st.session_state['current_session'][0]=='trading':
                self._steps_description(0,0,0,1,0)
                analysed_comments = st.session_state['current_session'][1]
                buy,sell = self._YOLO_trade(analysed_comments) 
                st.session_state['current_session'] = ('display_trading_summary_baloon',(buy,sell))
                click_button('Trading summary')
            elif st.session_state['current_session'][0] == 'display_trading_summary_baloon':
                st.balloons()
                self._steps_description(0,0,0,0,1)
                buy,sell = st.session_state['current_session'][1]
                self._trade_summary(buy,sell)
                st.session_state['current_session'] = ('display_trading_summary',st.session_state['current_session'][1])
                if click_button('Finished'):
                    # add rate app
                    del st.session_state['current_session']
                    st.experimental_rerun()
                st.caption('Please click finished if you want to build another strategy.')
            elif st.session_state['current_session'][0] == 'display_trading_summary':
                self._steps_description(0,0,0,0,1)
                buy,sell = st.session_state['current_session'][1]
                self._trade_summary(buy,sell)
                if click_button('Finished'):
                    # add rate app
                    del st.session_state['current_session']
                    st.experimental_rerun()
                st.caption('Please click finished if you want to build another strategy.')

    def _reddit_user_input(self) -> tuple:
        # select subreddit
        options = ['r/wallstreetbets', 'r/stocks', 'r/pennystocks', 'r/robinhood', 'r/GME', 'other']
        subreddit = st.selectbox('Select your favourite subreddit',options, index = 0)
        if subreddit == 'other':
            subreddit = st.text_input('Choose subreddit (e.g r/subRedditName)')
        subreddit = subreddit.strip() # remove trailing spaces
    
        # select start-end dates
        yesterday = datetime.date.today() - datetime.timedelta(days=1)
        end_date = yesterday.strftime('%Y-%m-%d')
        start_date = yesterday - datetime.timedelta(days=8)
        start = pd.to_datetime(st.text_input('Select start date', f'{start_date}'))
        end = pd.to_datetime(st.text_input('Select end date', f'{end_date}'))
        
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
        return subreddit, start, end, num_subs, num_comments, max_level

    def _load_reddit_data(self, user_input:tuple) -> 'list[praw.models.Comment]':
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
        sub_placeholder.empty()
        com_placeholder.empty()
        return comments

    def _user_strategy_paramenters(self):
        loss_options = [i for i in range(102)]
        gain_options = [i for i in range(101)]
        loss_txt = 'Select stop loss percentage, where 101 disables stop loss (recommended 101 - you have diamond hands, right?)'
        gain_txt = 'Select stop gain percentage'
        stop_loss = st.select_slider(loss_txt,loss_options,value = 101)
        stop_gain = st.select_slider(gain_txt,gain_options, value = 10)
        return stop_loss,stop_gain

    def _analyse_comments(self, comments: 'list[praw.models.Comment]', parameters:tuple):
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

    def _YOLO_trade(self, analysed_comments: 'list[tuple[praw.models.Comment,str]]') -> 'tuple[list]':
        buy,sell = [],[]
        with open('context/symbols_dict.pickle','rb') as f:
            symbols = pickle.load(f)
        
        # dislpay trades
        self.placeholder = st.empty()
        bar = st.progress(0)
        i = 0
        # sentiment analysis for each comment
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
        self.placeholder = st.empty()
        buy.sort(key=lambda x:x[1])
        sell.sort(key=lambda x:x[1])
        return buy,sell

    def _trade_summary(self, buy, sell):
        with open('context/symbols_dict.pickle','rb') as f:
            symbols = pickle.load(f)
        trades = len(buy)+len(sell)
        txt = f'Total number of trades: {trades}'
        markdown_css(txt,self.text_size,self.white)
        if st.checkbox('Show trades'):
            col1,col2 = st.columns(2)
            for w,date in buy:
                txt = f'Buy: {symbols[w]} ({w}) on {date}'
                markdown_css(txt,self.text_size,self.green,col=col1)
            for w,date in sell:
                txt = f'Sell: {symbols[w]} ({w}) on {date}'
                markdown_css(txt,self.text_size,self.red,col=col2)
            
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

        txt = '1. Scrape through Reddit posts'
        color = f"{is_run1*runColor+(1-is_run1)*nonrunColor}"
        markdown_css(txt,self.text_size,color)
        
        txt = '2. Select parameters for trading strategy'
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
        