import re 
from typing import List, Dict
from transformers import RobertaTokenizer
import torch

class TextProcessor():
    def __init__(self):
        self.url_pattern = re.compile(r'https?://\S+')
        self.hashtag_pattern = re.compile(r'#(\w+)')
        self.cashtag_pattern = re.compile(r'\$([A-Za-z][A-Za-z0-9_]*)\b')
        self.endline_char_pattern = re.compile(r'\n+')

    def _remove_url(self, text: str):
        return self.url_pattern.sub('', text)

    def _remove_hashtags(self, text: str):
        return self.hashtag_pattern.sub(r'\1', text)
    
    def _remove_cashtags(self, text: str):
        return self.cashtag_pattern.sub(r'\1', text)
    
    def _convert_to_lowercase(self, text: str):
        return text.lower()
    
    def _remove_endline_chars(self, text: str):
        return self.endline_char_pattern.sub(' ', text)

    def remove_urls_hashtags_endline_chars(self, text: str):
        """ Removes from the text URLs, Hashtags, Cashtags, and endline chars. Converts text to lowercase. """
        cleaned_text = self._remove_url(text)
        cleaned_text = self._remove_hashtags(cleaned_text)
        cleaned_text = self._remove_cashtags(cleaned_text)
        cleaned_text = self._convert_to_lowercase(cleaned_text)
        cleaned_text = self._remove_endline_chars(cleaned_text)
        return cleaned_text



class TweetProcessor(TextProcessor):
    def __init__(self, max_len: int = 128, tokenization_model: str = "ElKulako/cryptobert"):
        """
        Initialize the TweetProcessor with a specified tokenization model.

        Args:
            tokenization_model (str): The model name for tokenization.
            max_len (int): Maximum length of the tweet.
        """
        super().__init__()  
        self.tokenizer = RobertaTokenizer.from_pretrained(tokenization_model)
        self.max_len = max_len
    
    def _is_valid_length(self, tweet: str, min_words: int = 3) -> bool:
        """       
        Validate if the tweet's length is appropriate for classification.

        Args:
            tweet (str): The tweet text.
            max_len (int): Maximum allowed length of the tweet.
            min_words (int): Minimum required number of words in the tweet.

        Returns:
            bool: True if valid, False otherwise.
        """
        words = len(tweet.split())
        return len(tweet) < self.max_len and words >= min_words

    def _check_if_retweet(self, tweet: str) -> bool:
        """Check if the tweet is a retweet."""
        return not tweet.startswith("RT ")
    
    def _tokenize_single_tweet(self, text: str) -> Dict[str, torch.Tensor]:
        """Tokenize a single tweet and return the tokenized inputs."""
        inputs = self.tokenizer(text, max_length=self.max_len, padding="max_length", truncation=True, return_tensors="pt")
        return inputs

    def validate_tweet(self, tweet: str) -> bool:
        """Validate if the tweet is suitable for saving and sentiment classification."""
        if not self._check_if_retweet(tweet):
            return False
        
        if not self._is_valid_length(tweet):
            return False
        
        return True 

    def prepare_inputs_for_model(self, text: List[str]) -> List[Dict[str, torch.Tensor]]:
        """Tokenize a list of tweets and return a list of tokenized inputs."""
        inputs_list = []
        for tweet in text:
            inputs = self._tokenize_single_tweet(tweet)
            inputs_list.append(inputs)

        return inputs_list

class ArticleProcessor(TextProcessor):
    pass
