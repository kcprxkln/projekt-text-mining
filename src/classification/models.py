from abc import ABC, abstractmethod
from transformers import TextClassificationPipeline, AutoModelForSequenceClassification, AutoModelForSeq2SeqLM, AutoTokenizer, pipeline, BertTokenizer, RobertaTokenizer, BatchEncoding
from typing import Union, List
from multiprocessing import Pool
import torch
import torch.nn.functional as F


class ArticleSummarizer:
    def __init__(self):
        self.model_name = "facebook/bart-large-cnn"
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)
        self.pipeline = pipeline("summarization", model=self.model, tokenizer=self.tokenizer, truncation=True)

    def summarize(self, input: Union[str, List[str]], max_length=150, min_length=40) -> Union[str, List[str]]:
        if isinstance(input, str):
            model_response = self.pipeline(input, max_length=max_length, min_length=min_length, do_sample=False)
            summarized_article = model_response['summary_text']
            return summarized_article
        
        elif isinstance(input, list):
            model_response = self.pipeline(input, max_length=max_length, min_length=min_length, do_sample=False)
            summarized_articles = []
            for article_data in model_response:
                summarized_articles.append(article_data['summary_text'])
            return summarized_articles


class SentimentClassifier(ABC):
    
    @abstractmethod
    def classify_sentiment(self):
        pass

    @abstractmethod
    def calc_overall_sentiment(self):
        pass


class TweetSentimentClassifier(SentimentClassifier):
    def __init__(self):
        self.model_name = "ElKulako/cryptobert" # https://huggingface.co/ElKulako/cryptobert
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name, use_fast=True)
        self.model = AutoModelForSequenceClassification.from_pretrained(self.model_name, num_labels=3)
        self.pipe = TextClassificationPipeline(model=self.model, tokenizer=self.tokenizer, max_length=128, truncation=True, padding='max_length')

    def evaluate(self, eval_dataset):
        pass 

    def _classify_chunk(self, chunk):
        
        if isinstance(chunk[0], BatchEncoding):

            if not all('input_ids' in item and 'attention_mask' in item for item in chunk):
                raise ValueError("Each dictionary in chunk must have 'input_ids' and 'attention_mask' keys.")
            
            input_ids_list = [item['input_ids'].squeeze(0) for item in chunk]
            attention_mask_list = [item['attention_mask'].squeeze(0) for item in chunk]

            input_ids_tensor = torch.stack(input_ids_list)
            attention_mask_tensor = torch.stack(attention_mask_list)
            
            inputs = {
                'input_ids': input_ids_tensor,
                'attention_mask': attention_mask_tensor
            }
            
            outputs = self.model(**inputs)
            
            logits = outputs.logits
            probabilities = F.softmax(logits, dim=-1)
            predictions = logits.argmax(dim=-1)
            confidence_scores = probabilities.max(dim=-1).values

            classifications = []

            labels = {
                0:"Bearish", 
                1:"Neutral", 
                2:"Bullish"
            }

            for i, pred in enumerate(predictions.tolist()):
                
                classification = {
                    "label": labels[pred], 
                    "score": confidence_scores[i].item()
                }

                classifications.append(classification)
        
            return classifications

        elif isinstance(chunk[0], str):
            classifications = self.pipe(chunk) 
            return classifications 

        else:
            raise TypeError("Can't classify chunk of data. It needs to be a list of dictionaries with prepared model inputs or list of tweets in string format.")
        

    def classify_sentiment(self, tweets: Union[List[str], List[dict]], num_processes: int = 1):
        if num_processes < 1:
            raise ValueError("Value for argument 'num_processes' must be at least 1.")
        
        if not isinstance(tweets, (list, dict)):
            raise TypeError("Argument 'tweets' must be a list of strings or list of dictionaries.")
        
        tweets_per_process = len(tweets) // num_processes

        tweet_chunks = [tweets[i:i + tweets_per_process] for i in range(0, len(tweets), tweets_per_process)]

        with Pool(num_processes) as pool:
            classifications = pool.map(self._classify_chunk, tweet_chunks)

        classifications = [item for sublist in classifications for item in sublist]

        return classifications        
    

    def calc_overall_sentiment(self, classifications: List[dict]) -> float:
        """ Returns float value of the Bullish tweets compared to the Bearish tweets.
            Tweets with neutral sentiment are being ignored in the calculations
            0 - 0% tweets have positive sentiment
            1 - 100% tweets have positive sentiment
        """
        bullish_evals = []
        bearish_evals = []

        for eval in classifications:
            if eval['label'] == 'Bullish':
                bullish_evals.append(eval)
            elif eval['label'] == 'Bearish':
                bearish_evals.append(eval)

        nr_of_bullish_tweets = len(bullish_evals)
        nr_of_bearish_tweets = len(bearish_evals)

        if nr_of_bearish_tweets == 0 and nr_of_bearish_tweets == 0:
            raise ValueError("Cannot calculate sentiment percentage: No bullish or bearish tweets found.")
        else:
            sentiment = round(nr_of_bullish_tweets / (nr_of_bullish_tweets+nr_of_bearish_tweets), 2)
            return sentiment 
    

class ArticleSentimentClassifier:
    def __init__(self):
        self.model_name = "ProsusAI/finbert" # https://huggingface.co/ProsusAI/finbert
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name, use_fast=True)
        self.model = AutoModelForSequenceClassification.from_pretrained(self.model_name, num_labels=3)
        self.pipe = TextClassificationPipeline(model=self.model, tokenizer=self.tokenizer, max_length=128, truncation=True)

    def classify_sentiment(self, articles: List[str]):
        input_data = [{"text": article} for article in articles]
        classifications = self.pipe(input_data)
        return classifications