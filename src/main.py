import asyncio
import data_scraping.twitter_api as tt_api
import mongodb.twitter_info_config  as twitter_info_config
import mongodb.mongo_connector as mongo_connector
from mongodb.mongo_models import DailySentimentObj
from data_processing.process_scraped_data import return_proceessed_tweets_and_articles
from classification.sentiment_analysis import run_classification, calc_final_sentiment
from datetime import datetime


#  TODO: encapsulate in some class, and move to other file 
def add_classifications_into_db(processed_data):
    classifications = {}
    
    if 'tweets' in processed_data and processed_data['tweets']:
        tweet_contents = [tweet['content'] for tweet in processed_data['tweets']]
        tweet_sentiment_classification = run_classification(tweet_contents, type="tweet")

        for tweet, sentiment in zip(processed_data['tweets'], tweet_sentiment_classification):
            tweet['sentiment'] = sentiment['label']
            mongo_connector.MongoDatabase.upsert("tweets", {'id': tweet['tweet_id']}, tweet)
        
        classifications['tweets'] = tweet_sentiment_classification

    if 'articles' in processed_data and processed_data['articles']:
        article_contents = [article['content'] for article in processed_data['articles']]
        article_sentiment_classification = run_classification(article_contents, type="article")
        
        for article, sentiment in zip(processed_data['articles'], article_sentiment_classification):
            article['sentiment'] = sentiment['label']
            mongo_connector.MongoDatabase.upsert("articles", {'id': article['id']}, article)

        classifications['articles'] = article_sentiment_classification

    return classifications



async def main():
    mongodb_con = mongo_connector.MongoDatabase()
    mongodb_con.initialize()

    tt_scraper_info = twitter_info_config.TwitterInfoConfig()
    scraping_accounts = tt_scraper_info.get_all_scraping_acc_data()
    followed_tt_accounts = tt_scraper_info.get_all_followed_accounts()
    followed_accs_ids = tt_scraper_info.get_followed_accounts_ids(followed_tt_accounts)


    print("======== SCRAPING ACCOUNTS ========")
    print(scraping_accounts)
    print("======== FOLLOWED TWITTER ACCOUNTS ========")
    print(followed_tt_accounts)

    tt_scraper = tt_api.TwitterScraper(scraping_accounts)
    await tt_scraper.initialize()
    await tt_scraper.get_todays_tweets_from_accounts_bulk(followed_accs_ids)
    
    processed_data = return_proceessed_tweets_and_articles()
    print("========PROCESSED DATA========")
    print(processed_data)

    classifications = add_classifications_into_db(processed_data=processed_data)
    print("========CLASSIFICATIONS========")
    print(classifications)

    final_sent, positive_sum, neutral_sum, negative_sum = calc_final_sentiment(classifications['tweets'])
    print("FINAL SENTIMENT:", final_sent)

    current_datetime = datetime.now()
    date = current_datetime.date()

    daily_sent_obj = DailySentimentObj(
        day=date, 
        positive_tweets=positive_sum,
        neutral_tweets=neutral_sum, 
        negative_tweets=negative_sum, 
        sentiment_score=final_sent
    )

    mongodb_con.insert_one("daily_sentiment", daily_sent_obj.__dict__)


if __name__ == "__main__":
    asyncio.run(main())