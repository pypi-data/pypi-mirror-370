"""
For text analysis.

Available methods:
- `analyze_sentiment(text)`: Analyze the sentiment of the input text using NLTK's SentimentIntensityAnalyzer.
- `named_entity_recognition(text)`: Perform named entity recognition (NER) on the input text.
"""
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer

def analyze_sentiment(text):
    """
    Analyze the sentiment of the input text using NLTK's SentimentIntensityAnalyzer.

    Sentiment analysis assesses the emotional tone of a text, providing a sentiment
    score ranging from -1 (negative) to 1 (positive).
    
    Parameters:
    - `text` (str): The input text to be analyzed.

    Returns:
    - `float`: The sentiment score ranging from -1 (negative) to 1 (positive).
    """
    try:
        nltk.download('vader_lexicon', quiet=True)
        sid = SentimentIntensityAnalyzer()
        sentiment_scores = sid.polarity_scores(text)
        sentiment_score = sentiment_scores['compound']
        return sentiment_score
    except Exception as e:
        print(f"An error occurred during sentiment analysis: {str(e)}")
        return 0.0

def named_entity_recognition(text):
    """
    Perform named entity recognition (NER) on the input text.

    NER is the task of identifying and categorizing key information (entities)
    in text.

    Parameters:
    - `text` (str): The input text to be analyzed.

    Returns:
    - `list`: A list of named entities found in the text.
    """
    try:
        nltk.download('punkt', quiet=True)
        nltk.download('averaged_perceptron_tagger', quiet=True)
        nltk.download('maxent_ne_chunker', quiet=True)
        nltk.download('maxent_ne_chunker_tab', quiet=True)
        nltk.download('words', quiet=True)
        tokens = nltk.word_tokenize(text)
        tagged = nltk.pos_tag(tokens)
        entities = nltk.chunk.ne_chunk(tagged)
        return entities
    except Exception as e:
        print(f"An error occurred during NER: {str(e)}")
        return []