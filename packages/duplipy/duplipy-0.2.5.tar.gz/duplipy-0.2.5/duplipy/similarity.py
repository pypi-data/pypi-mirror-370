"""
Text similarity testing.

Available functions:
- `edit_distance_score(text1, text2)`: Calculate the edit distance score between two texts.
- `bleu_score(reference, candidate)`: Calculate the BLEU score between a reference sentence and a candidate sentence.
- `jaccard_similarity_score(text1, text2)`: Calculate Jaccard similarity between two texts.
- `sorensen_dice_coefficient(text1, text2)`: Calculate the Sorensen-Dice coefficient between two texts.
- `cosine_similarity_score(text1, text2)`: Calculate the cosine similarity between two texts.
- `mean_squared_error(image1, image2)`: Calculate the mean squared error (MSE) between two images.
- `psnr(image1, image2)`: Calculate the peak signal-to-noise ratio (PSNR) between two images.
"""
import collections
import math
import numpy as np
from PIL import Image
import nltk
from nltk.metrics import distance
from nltk.translate.bleu_score import sentence_bleu

def edit_distance_score(text1, text2):
    """
    Calculate the edit distance score between two texts.

    The edit distance, also known as Levenshtein distance, is a measure of the
    minimum number of single-character edits (insertions, deletions, or
    substitutions) required to transform one text into another.

    Parameters:
    - `text1` (str): The first text.
    - `text2` (str): The second text.

    Returns:
    - `int`: The edit distance score between the two texts. A lower score
      indicates greater similarity, with 0 meaning the texts are identical.
    """
    try:
        # Calculate the edit distance
        edit_dist = distance.edit_distance(text1, text2)
        return edit_dist
    except Exception as e:
        print(f"An error occurred during edit distance calculation: {str(e)}")
        return 0
    
def bleu_score(reference, candidate):
    """
    Calculate the BLEU (Bilingual Evaluation Understudy) score between a reference sentence and a candidate sentence.

    BLEU is a metric commonly used for evaluating the quality of machine-translated text. It measures the precision of the
    candidate sentence's n-grams (contiguous sequences of n items) against the reference sentence.

    Parameters:
    - `reference` (str): The reference sentence.
    - `candidate` (str): The candidate sentence.

    Returns:
    - `float`: The BLEU score. The score ranges from 0 (no similarity) to 1 (perfect match).
    """
    try:
        nltk.download('punkt', quiet=True)
        # Tokenize the reference and candidate sentences
        reference_tokens = nltk.word_tokenize(reference)
        candidate_tokens = nltk.word_tokenize(candidate)

        # Calculate the BLEU score
        bleu = sentence_bleu([reference_tokens], candidate_tokens)
        return bleu
    except Exception as e:
        print(f"An error occurred during BLEU score calculation: {str(e)}")
        return 0.0
    
# DupliPy 0.2.0

def jaccard_similarity_score(text1, text2):
    """
    Calculate Jaccard similarity between two texts.

    Jaccard similarity is a measure of similarity between two sets. In the context
    of text comparison, it calculates the similarity between the sets of words
    in two texts.

    Parameters:
    - `text1` (str): The first text for comparison.
    - `text2` (str): The second text for comparison.

    Returns:
    - `float`: Jaccard similarity score between the two texts. The score ranges
      from 0 (no similarity) to 1 (complete similarity).
    """
    set1 = set(text1.split())
    set2 = set(text2.split())
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    similarity_score = intersection / union if union != 0 else 0
    return similarity_score

def sorensen_dice_coefficient(text1, text2):
    """
    Calculate the Sorensen-Dice coefficient between two texts.

    The Sorensen-Dice coefficient is a statistic used for comparing the
    similarity of two samples.

    Parameters:
    - `text1` (str): The first text for comparison.
    - `text2` (str): The second text for comparison.

    Returns:
    - `float`: The Sorensen-Dice coefficient between the two texts.
    """
    set1 = set(text1.split())
    set2 = set(text2.split())
    intersection = len(set1.intersection(set2))
    return 2 * intersection / (len(set1) + len(set2))

def cosine_similarity_score(text1, text2):
    """
    Calculate the cosine similarity between two texts.

    Cosine similarity is a measure of similarity between two non-zero vectors
    of an inner product space that measures the cosine of the angle between them.

    Parameters:
    - `text1` (str): The first text for comparison.
    - `text2` (str): The second text for comparison.

    Returns:
    - `float`: The cosine similarity score between the two texts.
    """
    nltk.download('punkt', quiet=True)
    vec1 = collections.Counter(nltk.word_tokenize(text1))
    vec2 = collections.Counter(nltk.word_tokenize(text2))

    intersection = set(vec1.keys()) & set(vec2.keys())
    numerator = sum([vec1[x] * vec2[x] for x in intersection])

    sum1 = sum([vec1[x]**2 for x in vec1.keys()])
    sum2 = sum([vec2[x]**2 for x in vec2.keys()])
    denominator = math.sqrt(sum1) * math.sqrt(sum2)

    if not denominator:
        return 0.0
    return float(numerator) / denominator

def mean_squared_error(image1, image2):
    """
    Calculate the mean squared error (MSE) between two images.

    MSE is a measure of the average squared difference between the estimated
    values and the actual value.

    Parameters:
    - `image1` (PIL.Image.Image): The first image for comparison.
    - `image2` (PIL.Image.Image): The second image for comparison.

    Returns:
    - `float`: The mean squared error between the two images.
    """
    image1 = np.array(image1)
    image2 = np.array(image2)
    err = np.sum((image1.astype("float") - image2.astype("float")) ** 2)
    err /= float(image1.shape[0] * image1.shape[1])
    return err

def psnr(image1, image2):
    """
    Calculate the peak signal-to-noise ratio (PSNR) between two images.

    PSNR is the ratio between the maximum possible power of a signal and the
    power of corrupting noise that affects the fidelity of its representation.

    Parameters:
    - `image1` (PIL.Image.Image): The first image for comparison.
    - `image2` (PIL.Image.Image): The second image for comparison.

    Returns:
    - `float`: The peak signal-to-noise ratio between the two images.
    """
    mse = mean_squared_error(image1, image2)
    if mse == 0:
        return 100
    max_pixel = 255.0
    psnr = 20 * math.log10(max_pixel / math.sqrt(mse))
    return psnr