from twitter_api import TwitterScraper
from src.mongodb.twitter_info_config import TwitterInfoConfig


async def scrape_tweets():
    scraper_config = TwitterInfoConfig()
    scraping_accounts = scraper_config.get_all_scraping_acc_data()
    followed_tt_accounts = scraper_config.get_all_followed_accounts()
    
    if scraping_accounts:
        scraper = TwitterScraper(scraping_accounts)
    else: 
        raise Exception("No Twitter scraping accounts found in the MongoDB database.")
    
    if followed_tt_accounts:
        await scraper.get_todays_tweets_from_accounts_bulk(followed_tt_accounts)
    else:
        raise Exception("No followed Twitter accounts found in the MongoDB database.")
    

def scrape_articles():
    pass 