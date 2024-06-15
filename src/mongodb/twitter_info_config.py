from mongodb.mongo_connector import MongoDatabase
from mongodb.mongo_models import TwitterAccount, TwitterScrapedAccount
from typing import List


class TwitterInfoConfig:
    def __init__(self, scraping_acc_collection_name: str = 'tt_scraping_accounts', followed_collection_name: str = 'tt_followed_acc'):
        self.connector = MongoDatabase()
        self.scraping_acc_collection_name = scraping_acc_collection_name
        self.followed_collection_name = followed_collection_name

    def get_all_scraping_acc_data(self) -> List[TwitterAccount]:
        self.connector.initialize()
        cursor = self.connector.find(self.scraping_acc_collection_name, {})
        twitter_accounts = []
        for acc in cursor:
            tt_acc = TwitterAccount(
                tt_name=acc['twitter_name'], 
                tt_password=acc['twitter_pwd'], 
                email=acc['email'],
                email_password=acc['email_pwd']
            )
            twitter_accounts.append(tt_acc)
        return twitter_accounts

    def get_all_followed_accounts(self) -> List[TwitterScrapedAccount]:
        self.connector.initialize()
        cursor = self.connector.find(self.followed_collection_name, {})
        scraped_accounts = []
        for acc in cursor:
            scraped_acc = TwitterScrapedAccount(
                id=acc['id'], 
                url=acc['url'], 
                name=acc['name']
            )
            scraped_accounts.append(scraped_acc)
        return scraped_accounts
    
    def get_followed_accounts_ids(self, scraped_accounts: List[TwitterScrapedAccount]) -> List[int]:
        return [acc.id for acc in scraped_accounts]
    
    