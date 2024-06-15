import data_processing.text_processing as text_processing
from mongodb.scraped_data_fetcher import get_todays_scraped_data, ScrapedDataFetcher
from mongodb.mongo_connector import MongoDatabase

article_processor = text_processing.ArticleProcessor()
mongo_connector = MongoDatabase()

def process_tweets(tweets):
    tweet_processor = text_processing.TweetProcessor()
    
    tweets_to_save = []
    for tweet in tweets:
        tweet_content = tweet['content']
        preprocessed_content = tweet_processor.remove_urls_hashtags_endline_chars(tweet_content)
        if tweet_processor.validate_tweet(tweet_content):
            tweet['content'] = preprocessed_content 
            del tweet['_id']
            del tweet['type']
            tweets_to_save.append(tweet)
    mongo_connector.insert_many("tweets", tweets_to_save)
    return tweets_to_save


def process_articles(articles):
    article_content = article['content']
    for article in articles:
        pass
    return 0 

def return_proceessed_tweets_and_articles():
    data = {}
    scraped_data = get_todays_scraped_data()

    if 'tweets' in scraped_data and len(scraped_data['tweets']) > 0 :
        valid_tweets = process_tweets(scraped_data['tweets'])
        data['tweets'] = valid_tweets


    if 'articles' in scraped_data and len(scraped_data['articles']) > 0:
        valid_articles = process_articles(scraped_data['articles'])
        data['articles'] = valid_articles
    return data