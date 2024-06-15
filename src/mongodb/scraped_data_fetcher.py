from mongodb.mongo_connector import MongoDatabase
from datetime import datetime
from utils.date_utils import get_start_and_end_of_day
from typing import List, Union
import os 


class ScrapedDataFetcher:
    def __init__(self, collection_name: str = 'scraped_data'):
        """ 
        A class representing data fetcher for MongoDB database which fetches raw scraped data.

        Attributes:
            collection_name (str): String name for the MongoDB collection containing scraped data
        
        """
        self.collection_name = collection_name or os.environ.get("MONGODB_SCRAPED_DATA_COLLECTION")
        self.connector = MongoDatabase()


    def get_scraped_tweets(self, created_from: datetime, created_to: datetime) -> Union[List[dict], None]:
        query = { 
            "type": "tweet", 
            "created": {
                "$gte": created_from, 
                "$lt": created_to
            }
        }
        self.connector.initialize()
        cursor = self.connector.find(self.collection_name, query)
        tweets = []
        for tweet in cursor:
            tweets.append(tweet)
        return tweets


    def get_scraped_articles(self, created_from: datetime, created_to: datetime) -> Union[List[dict], None]:
        query = {
            "type": "article",
            "created": {
                "$gte": created_from,
                "$lt": created_to
            }
        }
        self.connector.initialize()
        cursor  = self.connector.find(self.collection_name, query)
        articles = []
        for article in cursor:
            articles.append(article)
        return articles
    

def get_todays_scraped_data(collection_name: str =  "scraped_data", articles: bool = True, tweets: bool = True):
    """ Returns scraped data saved in mongodb database. 
    
        Args:
            collection_name (str): The name of MongoDB collection where scraped data is stored.
            articles (bool): Flag indicating if scraped articles should be returned. Defaults to True.
            tweets (bool): Flag indicating if scraped tweets should be returned. Defaults to True.
    
    """
    start_of_today, end_of_today = get_start_and_end_of_day("Etc/GMT-2")
    scraped_data_fetcher = ScrapedDataFetcher(collection_name=collection_name)
    data = {}
    if articles:
        articles = scraped_data_fetcher.get_scraped_articles(start_of_today, end_of_today)
        data['articles'] = articles
    if tweets:
        tweets = scraped_data_fetcher.get_scraped_tweets(start_of_today, end_of_today)
        data['tweets'] = tweets
    return data