"""
Formatting for text using common NLP techniques.

Available functions:
- `remove_stopwords(text)`: Remove stopwords from the input text using NLTK's stopwords.
- `remove_numbers(text)`: Remove numbers from the input text.
- `remove_whitespace(text)`: Remove excess whitespace from the input text.
- `normalize_whitespace(text)`: Normalize multiple whitespaces into a single whitespace in the input text.
- `seperate_symbols(text)`: Separate symbols and words with a space to ease tokenization.
- `remove_special_characters(text)`: Remove special characters from the input text.
- `standardize_text(text)`: Standardize the formatting of the input text.
- `tokenize_text(text)`: Tokenize the input text into individual words.
- `stem_words(words)`: Stem the input words using Porter stemming algorithm.
- `lemmatize_words(words)`: Lemmatize the input words using WordNet lemmatization.
- `pos_tag(text)`: Perform part-of-speech (POS) tagging on the input text.
- `remove_profanity_from_text(text)`: Remove profane words from the input text.
- `remove_sensitive_info_from_text(text)`: Remove sensitive information from the input text.
- `remove_hate_speech_from_text(text)`: Remove hate speech or offensive speech from the input text.
- `post_format_text(text)`: Post-format the text using regex.
"""

import string
import re
import nltk
from valx import remove_profanity, remove_sensitive_information, detect_hate_speech
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer, WordNetLemmatizer

def remove_stopwords(text):
    """
    Remove stopwords from the input text using NLTK's stopwords.

    Stopwords are frequently used words (e.g., 'the', 'and', 'is') that are often
    excluded from text processing to focus on more meaningful content.
    
    Parameters:
    - `text` (str): The input text from which stopwords should be removed.

    Returns:
    - `str`: The text without stopwords.
    """
    try:
        nltk.download('stopwords', quiet=True)
        stop_words = set(stopwords.words('english'))
        tokens = text.split()
        filtered_tokens = [token for token in tokens if token.lower() not in stop_words]
        filtered_text = ' '.join(filtered_tokens)
        return filtered_text
    except Exception as e:
        print(f"An error occurred during stopwords removal: {str(e)}")
        return text

def remove_numbers(text):
    """
    Remove numbers from the input text.

    Numerical digits are removed from the text to focus on the non-numeric content.
    
    Parameters:
    - `text` (str): The input text from which numbers should be removed.

    Returns:
    - `str`: The text without numbers.
    """
    try:
        text = re.sub(r'\d+', '', text)
        return text
    except Exception as e:
        print(f"An error occurred during number removal: {str(e)}")
        return text

def remove_whitespace(text):
    """
    Remove excess whitespace from the input text.

    Excess whitespace, including leading, trailing, and multiple consecutive spaces,
    is removed from the text to create a more standardized and readable format.
    
    Parameters:
    - `text` (str): The input text from which excess whitespace should be removed.

    Returns:
    - `str`: The text with the removed excess whitespace.
    """
    try:
        text = ' '.join(text.split())
        return text
    except Exception as e:
        print(f"An error occurred during whitespace removal: {str(e)}")
        return text

def normalize_whitespace(text):
    """
    Normalize multiple whitespaces into a single whitespace in the input text.

    Multiple consecutive whitespaces are replaced with a single whitespace to
    create a more consistent and readable text format.
    
    Parameters:
    - `text` (str): The input text from which whitespace should be normalized.

    Returns:
    - `str`: The text with normalized whitespace.
    """
    try:
        text = re.sub(r'\s+', ' ', text)
        return text
    except Exception as e:
        print(f"An error occurred during whitespace normalization: {str(e)}")
        return text

def separate_symbols(text):
    """
    Separate symbols and words with a space to ease tokenization.

    Symbols in the input text are separated from words with a space to facilitate
    easier tokenization and analysis of the text.
    
    Parameters:
    - `text` (str): The input text from which symbols needs to be seperated.

    Returns:
    - `str`: The text from which symbols have been seperated.
    """
    try:
        pattern = r"([\W])"
        separated_text = re.sub(pattern, r" \1 ", text)
        return separated_text
    except Exception as e:
        print(f"An error occurred during symbol separation: {str(e)}")
        return text

def remove_special_characters(text):
    """
    Remove special characters from the input text.

    Special characters, such as punctuation and user-defined symbols, are removed
    to create a text without these non-alphanumeric elements.
    
    Parameters:
    - `text` (str): The input text from which special characters should be removed.

    Returns:
    - `str`: The text with special characters removed.
    """
    try:
        text = text.translate(str.maketrans("", "", string.punctuation))
        special_characters = "@#$%^&*"
        text = ''.join(char for char in text if char not in special_characters)
        return text
    except Exception as e:
        print(f"An error occurred during special character removal: {str(e)}")
        return text

def standardize_text(text):
    """
    Standardize the formatting of the input text.

    The input text is converted to lowercase and leading/trailing whitespaces are removed
    to create a standardized representation for easier comparison and analysis.

    Parameters:
    - `text` (str): The input text which needs to be standardized.

    Returns:
    - `str`: The standardized text.
    """
    try:
        text = text.lower()
        text = text.strip()
        return text
    except Exception as e:
        print(f"An error occurred during text standardization: {str(e)}")
        return text

def tokenize_text(text):
    """
    Tokenize the input text into individual words.

    Tokenization is the process of breaking down a text into individual words, 
    facilitating further analysis, such as counting word frequencies or analyzing 
    language patterns.
    
    Parameters:
    - `text` (str): The input text to be tokenized.

    Returns:
    - `list`: A list of tokens (words) from the input text.
    """
    nltk.download('punkt', quiet=True)
    tokens = word_tokenize(text)
    return tokens

def stem_words(words):
    """
    Stem the input words using Porter stemming algorithm.

    Stemming reduces words to their base or root form, helping to consolidate 
    variations of words and simplify text analysis.

    Parameters:
    - `words` (list): A list of words to be stemmed.

    Returns:
    - `list`: A list of stemmed words.
    """
    stemmer = PorterStemmer()
    stemmed_words = [stemmer.stem(word) for word in words]
    return stemmed_words

def lemmatize_words(words):
    """
    Lemmatize the input words using WordNet lemmatization.

    Lemmatization reduces words to their base or dictionary form, helping to 
    normalize variations and simplify text analysis.
    
    Parameters:
    - `words` (list): A list of words to be lemmatized.

    Returns:
    - `list`: A list of lemmatized words.
    """
    nltk.download('wordnet', quiet=True)
    lemmatizer = WordNetLemmatizer()
    lemmatized_words = [lemmatizer.lemmatize(word) for word in words]
    return lemmatized_words

def pos_tag(text):
    """
    Perform part-of-speech (POS) tagging on the input text.

    Part-of-speech tagging assigns a grammatical category (tag) to each word 
    in a text, aiding in syntactic analysis and understanding sentence structure.
    
    Parameters:
    - `text` (str): The input text to be POS tagged.

    Returns:
    - `list`: A list of tuples containing (word, tag) pairs.
    """
    try:
        nltk.download('punkt', quiet=True)
        nltk.download('averaged_perceptron_tagger', quiet=True)
        tokens = nltk.word_tokenize(text)
        tagged_words = nltk.pos_tag(tokens)
        return tagged_words
    except Exception as e:
        print(f"An error occurred during POS tagging: {str(e)}")
        return []

def remove_profanity_from_text(text):
    """
    Remove profane words from the input text.

    This ensures that text is clean and does not contain inappropriate language.
    
    Parameters:
    - `text` (str): The input text to remove profanity from.

    Returns:
    - `text` (str): The cleaned output text.
    """
    nltk.download('punkt', quiet=True)
    sentences = nltk.sent_tokenize(text)
    cleaned_sentences = remove_profanity(sentences, language='All')
    cleaned_text = ' '.join(cleaned_sentences)

    return cleaned_text

def remove_sensitive_info_from_text(text):
    """
    Remove sensitive information from the input text.

    This can be useful for depersonalization of text data.
    
    Parameters:
    - `text` (str): The input text to remove sensitive information from.

    Returns:
    - `text` (str): The cleaned output text.
    """
    nltk.download('punkt', quiet=True)
    sentences = nltk.sent_tokenize(text)
    cleaned_sentences = remove_sensitive_information(sentences)
    cleaned_text = ' '.join(cleaned_sentences)

    return cleaned_text

def remove_hate_speech_from_text(text):
    """
    Remove hate speech or offensive speech from the input text.

    This function removes sentences, and not just a certain word, because it is context relevant.
    
    Parameters:
    - `text` (str): The input text to remove hate speech and offensive speech from.

    Returns:
    - `text` (str): The cleaned output text.
    """
    nltk.download('punkt', quiet=True)
    sentences = nltk.sent_tokenize(text)
    cleaned_sentences = []
    for sentence in sentences:
        outcome = detect_hate_speech(sentence)
        if outcome != ['Hate Speech'] and outcome != ['Offensive Speech'] and outcome == ['No Hate and Offensive Speech']:
            cleaned_sentences.append(sentence)
    cleaned_text = ' '.join(cleaned_sentences)

    return cleaned_text

def post_format_text(text):
    """
    Post-format the text using regex.

    This function post-formats the text by removing extra spaces and ensuring
    proper punctuation spacing.

    Parameters:
    - `text` (str): The input text to be post-formatted.

    Returns:
    - `str`: The post-formatted text.
    """
    # Remove extra spaces
    text = re.sub(r'\s+', ' ', text)
    # Ensure proper punctuation spacing
    text = re.sub(r'\s([.,!?;:])', r'\1', text)
    return text