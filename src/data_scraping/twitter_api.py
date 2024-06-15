import tracemalloc
tracemalloc.start()
from twscrape import API
import asyncio 
from typing import List
import datetime  
from mongodb import mongo_connector
from mongodb.twitter_info_config import TwitterAccount
from utils.date_utils import TIMEZONE


class TwitterScraper():
    """Class representing Twitter Scraper inheriting from twscrape API object"""
    def __init__(self, user_list: List[TwitterAccount], collection_name='scraped_data'):
        self.user_list = user_list
        self.collection_name = collection_name
        self.api = API()
        self.db_connector = mongo_connector.MongoDatabase()


    async def initialize(self):
        """Initializes all scraping accounts."""
        await self._prepare_all_accounts()


    async def _prepare_all_accounts(self):
        for user in self.user_list: 
            await self.api.pool.add_account(user.tt_name, user.tt_password, user.email, user.email_password)
        await self.api.pool.login_all()


    async def get_user_id(self, login) -> int:
        """ Get user's ID by the login """
        user = await API.user_by_login(login)
        return user.id 
    

    async def get_todays_users_posts(self, user_id, limit=5) -> List[dict]:
        """ Returns user's twitter posts from the current day. """
        user_tweets = []
        today = datetime.datetime.now(TIMEZONE).date()

        async for tweet in API.user_tweets(self.api, uid=user_id, limit=limit):
            tweet_date_desired_timezone = tweet.date.astimezone(TIMEZONE).date()
            if tweet_date_desired_timezone == today:
                tweet_data = {
                    "type": "tweet",
                    "tweet_id": tweet.id,
                    "tweet_creator_id": user_id,
                    "tweet_creator_username": tweet.user.username, 
                    "created": tweet.date, 
                    "content": tweet.rawContent
                }
                user_tweets.append(tweet_data)

        return user_tweets 


    async def get_todays_tweets_from_accounts_bulk(self, accounts: List[int]):
        """ Retrieves all today's tweets from all accounts provided in the 'followed_account_ids' and saves them into MongoDB """
        all_tweets = []
        tasks = [self.get_todays_users_posts(user_id) for user_id in accounts]
        all_tweets_lists = await asyncio.gather(*tasks)
        all_tweets = [tweet for tweets_list in all_tweets_lists for tweet in tweets_list]
        self.db_connector.insert_many(self.collection_name, all_tweets)
