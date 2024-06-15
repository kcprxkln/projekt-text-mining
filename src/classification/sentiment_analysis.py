from typing import List, Union, Dict
from classification.models import TweetSentimentClassifier, ArticleSentimentClassifier


def run_classification(data: List[str], type: str) -> Union[List[Dict], None]:
    if type != "tweet" and type != "arcticle":
        raise ValueError("Argument `type` must be `tweet` or `article`.")
    
    if type == "tweet":
        classifier = TweetSentimentClassifier()
    if type == "article":
        classifier = ArticleSentimentClassifier()

    classifications = classifier.classify_sentiment(data)
    return classifications


def calc_final_sentiment(tweets_sentiment: Union[List[Dict], None] = None, articles_sentiment: Union[List[Dict], None] = None) -> float:
    """
    Calculate the final sentiment based on the sentiment of tweets and articles.

    Args:
        tweets_sentiment (Union[List[Dict], None]): List of dictionaries containing sentiment labels for tweets.
        articles_sentiment (Union[List[Dict], None]): List of dictionaries containing sentiment labels for articles.
 
    Returns:
        tuple: A tuple containing:
            - float: The final sentiment score, with 1.0 indicating 100% positive sentiment and 0.0 indicating 0% positive sentiment.
            - int: The count of positive (Bullish) sentiments.
            - int: The count of neutral sentiments.
            - int: The count of negative (Bearish) sentiments.
    """

    # Handle None inputs by converting them to empty lists
    if tweets_sentiment is None:
        tweets_sentiment = []

    if articles_sentiment is None:
        articles_sentiment = []

    classifications = tweets_sentiment + articles_sentiment

    positive_counter = 0
    negative_counter = 0
    neutral_counter = 0

    for classification in classifications:
        label = classification['label']
        print("LABEL-----", label)
        if label == 'Bullish':
            positive_counter += 1 
        if label == 'Bearish':
            negative_counter += 1
        if label == 'Neutral':
            neutral_counter += 1

    total = positive_counter + negative_counter
    
    if total == 0:
        return 0.0
    
    sentiment = positive_counter / total
    
    return sentiment, positive_counter, neutral_counter, negative_counter 