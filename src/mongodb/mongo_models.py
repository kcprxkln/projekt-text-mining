from dataclasses import dataclass
from datetime import datetime

@dataclass
class TwitterAccount():
    """Class representing Twitter Account used for data scraping."""
    tt_name: str
    tt_password: str
    email: str
    email_password: str

@dataclass
class TwitterScrapedAccount():
    """Class representing Twitter account that is being scraped."""
    id: int 
    url: str
    name: str

@dataclass
class DailySentimentObj:
    """Class representing object of overall sentiment in specific day."""
    day: datetime 
    positive_tweets: int
    neutral_tweets: int
    negative_tweets: int
    sentiment_score: float

