import base64
from collections import deque
from io import BytesIO
import os
import time
from PIL import Image
import pandas as pd
import praw
import requests
import streamlit as st
import datetime
import pytesseract
pytesseract.pytesseract.tesseract_cmd ='context/tesseract'

import tweepy

from framework.page import Page
from framework.utils import markdown_css, click_button

class getAltData(Page):
    def __init__(self, title: str) -> None:
        super().__init__(title)
        self.white = '#ffffff'

    def load_page(self) -> None:
        self.show_title()
        data_source = self.get_input()
        options = ['🚀 Reddit', '🐦 Twitter']
        d = dict(zip([i for i in range(len(options))],options))
        if data_source == d[0]:
            options = ['Posts', 'Memes', '']
            reddit_data_type = st.selectbox('Select reddit data',options, index = 2)
            if reddit_data_type =='Posts':
                self.reddit_post_data()
            elif reddit_data_type=='Memes':
                self.reddit_meme_data()

        elif data_source == d[1]:
            self.twitter_data()

    def twitter_data(self):
        if 'twitter_data' not in st.session_state:
            input_for_twitter = self.twitter_input()
            if click_button('Load Tweets'):
                hashtag, num_tweets, start_twitter, end_twitter = input_for_twitter
                df = self.scrape_tweets(hashtag, num_tweets, start_twitter, end_twitter)
                st.session_state['twitter_data'] = df
                st.experimental_rerun()
        elif 'download' not in st.session_state:
            df = st.session_state['twitter_data']
            st.write(df)
            if click_button('Download csv'):
                csv = df.to_csv(index=False)
                b64 = base64.b64encode(csv.encode()).decode()  # some strings
                linko= f'<a href="data:file/csv;base64,{b64}" download="twitter_data.csv">Click to download </a>'
                st.markdown(linko, unsafe_allow_html=True)

            if click_button('Finished'):
                for key in st.session_state.keys():
                    del st.session_state[key]
                st.experimental_rerun()

    def reddit_post_data(self):
        if 'reddit_posts_data' not in st.session_state:
            input_for_reddit = self.reddit_user_input_posts()
            if click_button('Load Posts'):
                df_comments = self.scrape_reddit_data(input_for_reddit)
                st.session_state['reddit_posts_data'] = df_comments
                st.experimental_rerun()
        elif 'download' not in st.session_state:
            df_comments = st.session_state['reddit_posts_data']
            st.write(df_comments)
            if click_button('Download csv'):
                csv = df_comments.to_csv(index=False)
                b64 = base64.b64encode(csv.encode()).decode()  # some strings
                linko= f'<a href="data:file/csv;base64,{b64}" download="reddit_comments.csv">Click to download </a>'
                st.markdown(linko, unsafe_allow_html=True)
            
            if click_button('Finished'):
                for key in st.session_state.keys():
                    del st.session_state[key]
                st.experimental_rerun()

    def reddit_meme_data(self):
        if 'reddit_memes_data' not in st.session_state:
            input_for_reddit = self.reddit_user_input_memes()
            if click_button('Load Memes'):
                subreddit, num_memes, start_reddit, end_reddit = input_for_reddit
                df_memes = self.scrape_reddit_memes(subreddit, num_memes, start_reddit, end_reddit)
                st.session_state['reddit_memes_data'] = df_memes
                st.experimental_rerun()

        elif 'download' not in st.session_state:
            df_memes = st.session_state['reddit_memes_data']
            st.write(df_memes)
            if click_button('Download csv'):
                csv = df_memes.to_csv(index=False)
                b64 = base64.b64encode(csv.encode()).decode()  # some strings
                linko= f'<a href="data:file/csv;base64,{b64}" download="reddit_memes.csv">Click to download </a>'
                st.markdown(linko, unsafe_allow_html=True)
            
            if click_button('Finished'):
                for key in st.session_state.keys():
                    del st.session_state[key]
                st.experimental_rerun()

    def reddit_user_input_posts(self) -> tuple:
        # select subreddit
        options = ['r/wallstreetbets', 'r/stocks', 'r/pennystocks', 'r/robinhood', 'r/GME', 'other']
        subreddit = st.selectbox('Select your favourite subreddit',options, index = 0)
        if subreddit == 'other':
            subreddit = st.text_input('Choose subreddit (e.g r/subRedditName, subRedditName)')
        subreddit = subreddit.strip() # remove trailing spaces
    
        # select start-end dates
        start_date = datetime.date.today() - datetime.timedelta(days=30)
        end_date = start_date + datetime.timedelta(days=29)
        start_reddit = pd.to_datetime(st.text_input('Select start date for reddit post', f'{start_date}'))
        txt = f'Select end date for reddit post.'
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

    def reddit_user_input_memes(self) -> tuple:
        options = ['r/wallstreetbets', 'r/stocks', 'r/pennystocks', 'r/robinhood', 'r/GME', 'other']
        subreddit = st.selectbox('Select your favourite subreddit',options, index = 0)
        if subreddit == 'other':
            subreddit = st.text_input('Choose subreddit (e.g r/subRedditName, subRedditName)')
        subreddit = subreddit.strip() # remove trailing spaces
        if subreddit[:2]=='r/':
            subreddit = subreddit[2:]
        num_memes = st.number_input('Select number of memes you want to consider', value = 50)

        # select start-end dates
        start_date = datetime.date.today() - datetime.timedelta(days=30)
        end_date = start_date + datetime.timedelta(days=29)
        start_reddit = pd.to_datetime(st.text_input('Select start date for reddit post', f'{start_date}'))
        txt = f'Select end date for reddit post.'
        end_reddit = pd.to_datetime(st.text_input(txt, f'{end_date}'))

        return subreddit, num_memes, start_reddit, end_reddit

    def scrape_reddit_data(self, user_input:tuple) -> pd.DataFrame:
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

        comments_formatted =[]
        for com in comments:
            date = datetime.datetime.utcfromtimestamp(com.created_utc).strftime('%Y-%m-%d %H:%M:%S')
            if com.author:
                comments_formatted.append((date,com.author.name,com.body,com.score))
            else:
                comments_formatted.append((date,None,com.body,com.score))

        bar.progress(1.00)
        sub_placeholder.empty()
        com_placeholder.empty()
        df_comments = pd.DataFrame(comments_formatted)
        df_comments.columns = ['Date','Author','Text','Upvotes']
        return df_comments

    def scrape_reddit_memes(self, subreddit:str, num_memes:int, start_reddit:str, end_reddit:str)->list:
        # reddit object
        reddit = praw.Reddit(
                client_id=st.secrets["client_id"],
                client_secret=st.secrets["client_secret"],
                user_agent=st.secrets["user_agent"],
                username=st.secrets["username"],
                password=st.secrets["password"],
                )
        subreddit = reddit.subreddit(subreddit)
        allowed_image_extensions = ['.jpg', '.jpeg', '.png']
        passed = 0
        memes = []
        post_placeholder = st.empty()
        bar = st.progress(0)
        image_placeholder = st.empty()
        start = pd.to_datetime(start_reddit)
        end = pd.to_datetime(end_reddit)
        s = time.time()
        for post in subreddit.hot(limit=None):
            url = post.url
            _,ext = os.path.splitext(url)
            if ext in allowed_image_extensions and self._within_time_interval(post,start,end):
                response = requests.get(url)
                img = Image.open(BytesIO(response.content))
                self._set_background(url)
                meme_txt = pytesseract.image_to_string(img)
                title = post.title
                date = datetime.datetime.utcfromtimestamp(post.created_utc).strftime('%Y-%m-%d %H:%M:%S')
                memes.append((date,meme_txt,title,url))
                passed+=1
                post_placeholder.text(f'Loading meme at {url}')
                bar.progress(passed/num_memes)
                image_placeholder.image(f'{url}',use_column_width = 'auto')
                if passed>=num_memes:
                    break
        e = time.time()
        bar.progress(1.0)
        if passed<num_memes:
            txt = f'In this subreddit we found only {passed} memes/pictures for the selected scraping period.'
            self._markdown_css(txt,self.text_size,self.white)
        post_placeholder.text(f'Memes/pictures scraped and analysed in {round(e-s,4)} seconds. To continue please click "Next" on the bottom of the page.')
        df_memes = pd.DataFrame(memes)
        df_memes.columns = ['Date','Meme Text', 'Post Title', 'URL']
        return df_memes

    def get_input(self) -> str:
        st.subheader('Select Data Source')
        options = ['🚀 Reddit', '🐦 Twitter', '']
        data_source = st.selectbox('Select source',options, index = len(options)-1)
        return data_source
    
    def twitter_input(self) -> tuple:
        options = ['#GME','#trump','#StockMarket','#bitcoin','#crypto', 'other']
        hashtag = st.selectbox('Select popular hashtag',options, index = 0)
        if hashtag == 'other':
            hashtag = st.text_input('Choose hashtag (e.g #hashtag)')
        hashtag = hashtag.strip() # remove trailing spaces
        num_tweets = st.number_input('Select number of tweets you want to dowload', value = 100)

        # select start-end dates
        start_date = datetime.date.today() - datetime.timedelta(days=5)
        end_date = start_date + datetime.timedelta(days=1)
        txt = 'Select start date for first tweet'
        start_tweet = st.text_input(txt, f'{start_date}')
        txt = f'Select end date for last tweet post.'
        end_tweet = st.text_input(txt, f'{end_date}')
        start_tweet = ''.join(start_tweet.split('-'))+'0000'
        end_tweet = ''.join(end_tweet.split('-'))+'0000'
        return hashtag, num_tweets, start_tweet, end_tweet

    def scrape_tweets(self, hashtag, num_tweets, start_twitter, end_twitter):
        text, user_name, media, date, tags = [],[],[],[],[]
        auth = tweepy.OAuthHandler(st.secrets["consumer_key"],st.secrets['consumer_secret'])
        auth.set_access_token(st.secrets['access_token_key'], st.secrets['access_token_secret'])
        api = tweepy.API(auth,wait_on_rate_limit=True)

        tweet_placeholder = st.empty()
        bar = st.progress(0)
        passed = 0
        for status in tweepy.Cursor(api.search_full_archive,'prod', hashtag, 
                fromDate=start_twitter, toDate=end_twitter).items(num_tweets):
            dt = status.created_at.strftime('%Y-%m-%d %H:%M:%S')
            date.append(dt)
            if status.truncated:
                txt = status.extended_tweet['full_text']
                text.append(txt)
            else:
                txt = status.text
                text.append(txt)
            user_name.append(status.user.screen_name)
            ls_tags = [d['text'] for d in status.entities['hashtags']]
            tags.append(', '.join(ls_tags))
            if status.entities.get('media'):
                media.append(status.entities.get('media')[0]['media_url'])
            else:
                media.append('NA')
            passed += 1
            tweet_placeholder.text(f'Loading Tweet: {txt}')
            bar.progress(passed/num_tweets)

        df = pd.DataFrame()
        df['date'] = date
        df['hashtags'] = tags
        df['user_name'] = user_name
        df['text'] = text
        df['media'] = media
        return df
    

    def _within_time_interval(self, reddit_obj: praw.models, start:datetime, end: datetime):
        utc_time = datetime.datetime.utcfromtimestamp(reddit_obj.created_utc).strftime('%Y-%m-%d')
        datetime_time = pd.to_datetime(utc_time)
        if datetime_time < start or datetime_time > end:
            return False
        return True

    def _set_background(self, png_url:str, placeholder:bool = False):
        page_bg_img = f'<style>body {{background-image: url("{png_url}");background-size: 12px;}}</style>'
        
        self.placeholder = st.empty()
        if placeholder:
            self.placeholder.markdown(page_bg_img, unsafe_allow_html=True)
        else:
            st.markdown(page_bg_img, unsafe_allow_html=True)

    def download_image_button(url: str, format_type:str) -> None:
        '''
        Button for downloading an image.
        '''
        txt = 'Save file'
        button = click_button(txt,size=15)
        if button:
            st.download_button(
                label='Click to download',
                data=url,
                file_name=f'result.{format_type}',
                mime=f'image/{format_type}')