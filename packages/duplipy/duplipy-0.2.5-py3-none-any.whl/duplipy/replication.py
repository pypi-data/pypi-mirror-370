"""
Text replication for NLP.

Available functions:
- `replace_word_with_synonym(word)`: Replace the given word with a synonym.
- `augment_text_with_synonyms(text, augmentation_factor, probability, progress=True)`: Augment the input text by replacing words with synonyms.
- `load_text_file(filepath)`: Load the contents of a text file.
- `augment_file_with_synonyms(file_path, augmentation_factor, probability, progress=True)`: Augment a text file by replacing words with synonyms.
- `insert_random_word(text, word)`: Insert a random word into the input text.
- `delete_random_word(text)`: Delete a random word from the input text.
- `random_word_deletion(text, num_deletions=1)`: Deletes a user-specified number of random words from the text.
- `swap_random_words(text)`: Swaps two random words in the text.
- `insert_synonym(text, word)`: Insert a synonym of the given word into the input text.
- `paraphrase(text)`: Paraphrase the input text.
- `flip_horizontal(image)`: Flip the input image horizontally.
- `flip_vertical(image)`: Flip the input image vertically.
- `rotate(image, angle)`: Rotate the input image by a specified angle.
- `random_rotation(image, max_angle)`: Randomly rotate the input image by an angle within the specified range.
- `resize(image, size)`: Resize the input image to the specified size.
- `crop(image, box)`: Crop the input image to the specified rectangular region.
- `random_crop(image, size)`: Randomly crop a region from the input image.
- `shuffle_words(text)`: Randomly shuffle the order of words in each sentence.
- `random_flip(image, horizontal, vertical)`: Randomly flip the input image horizontally and/or vertically.
- `random_color_jitter(image, brightness, contrast, saturation, hue)`: Randomly adjust the brightness, contrast, saturation, and hue of the input image.
- `noise_overlay(image, noise_factor, noise_type, grain_factor)`: Overlay noise on the input image.
"""

import random
import time
import nltk
from nltk.corpus import wordnet
from PIL import Image
import tqdm
from PIL import ImageEnhance

def replace_word_with_synonym(word):
    """
    Replace the given word with a synonym.

    Synonyms are alternative words with similar meanings, and replacing words
    with synonyms can be used for text augmentation or variation.
    
    Params:
    - `word` (str): The input word to replace with a synonym.

    Returns:
    - `str`: The synonym for the word.
    """
    try:
        nltk.download("wordnet", quiet=True)
        synonyms = []
        for syn in wordnet.synsets(word):
            for lemma in syn.lemmas():
                synonyms.append(lemma.name())
        
        if synonyms:
            synonym = random.choice(synonyms)
            return synonym
        
        return word
    except Exception as e:
        print(f"An error occurred during word replacement: {str(e)}")
        return word

def augment_text_with_synonyms(text, augmentation_factor, probability, progress=True):
    """
    Augment the input text by replacing words with synonyms.

    Parameters:
    - `text` (str): The input text to be augmented.
    - `augmentation_factor` (int): The number of times to augment the text.
    - `probability` (float): The probability of replacing a random word with a synonym.
    - `progress` (bool): Whether or not to return current progress during augmentation.

    Returns:
    - `list`: A list of augmented text.
    """
    augmented_text = []
    try:
        if probability is None:
            raise ValueError("Probability value cannot be of NoneType. Choose a float from 0 to 1")

        tokens = text.split()

        with tqdm.tqdm(total=augmentation_factor * len(tokens), desc="Augmenting Text", disable=not progress) as pbar:
            for _ in range(augmentation_factor):
                augmented_tokens = []

                for token in tokens:
                    if random.random() < probability:
                        replaced_token = replace_word_with_synonym(token)
                        augmented_tokens.append(replaced_token)
                    else:
                        augmented_tokens.append(token)
                    pbar.update(1)

                augmented_text.append(' '.join(augmented_tokens))

    except Exception as e:
        print(f"An error occurred during text augmentation: {str(e)}")
        return []

    return augmented_text

def load_text_file(file_path):
    """
    Load the contents of a text file.

    Parameters:
    - `file_path` (str): The path to the target input data.

    Returns:
    - `str`: The read text from the file.
    """
    try:
        with open(file_path, 'r') as file:
            text = file.read()
        return text
    except Exception as e:
        print(f"An error occurred during text file loading: {str(e)}")
        return ""

def augment_file_with_synonyms(file_path, augmentation_factor, probability, progress=True):
    """
    Augment a text file by replacing words with synonyms.

    Parameters:
    - `file_path` (str): The path to the target input data.
    - `augmentation_factor` (int): The number of times to augment the data.
    - `probability` (float): The probability of replacing a random word with its synonym.
    - `progress` (bool): Whether or not to print the current progress during augmentation.

    Returns:
    - `list`: A list of augmented text.
    """
    try:
        text = load_text_file(file_path)
        augmented_text = augment_text_with_synonyms(text, augmentation_factor, probability, progress)
        return augmented_text
    except Exception as e:
        print(f"An error occurred during text file augmentation: {str(e)}")
        return []


def insert_random_word(text, word):
    """
    Insert a random word into the input text.

    This function randomly inserts a specified word into the input text, creating
    variations for text augmentation or diversification.

    Parameters:
    - `text` (str): The input text for word insertion.
    - `word` (str): The word to be inserted into the text.

    Returns:
    - `str`: The text with the randomly inserted word.
    """
    try:
        nltk.download("punkt", quiet=True)
        words = nltk.word_tokenize(text)
        words.insert(random.randint(0, len(words)), word)
        modified_text = " ".join(words)
        return modified_text
    except Exception as e:
        print(f"An error occurred during word insertion: {str(e)}")
        return text


def random_word_deletion(text, num_deletions=1):
    """
    Delete a random word from the input text.

    This function randomly deletes a word from the input text, creating variations
    for text augmentation or diversity.
    
    Parameters:
    - `text` (str): The input text for word deletion.
    - `num_deletions` (int): The number of words to delete.

    Returns:
    - `str`: The text with a randomly deleted word.
    """
    try:
        nltk.download("punkt", quiet=True)
        words = nltk.word_tokenize(text)
        for _ in range(num_deletions):
            if len(words) > 1:
                words.pop(random.randint(0, len(words) - 1))
        modified_text = " ".join(words)
        return modified_text
    except Exception as e:
        print(f"An error occurred during word deletion: {str(e)}")
        return text

def delete_random_word(text):
    """
    Delete a random word from the input text.

    This function randomly deletes a word from the input text, creating variations
    for text augmentation or diversity.

    Parameters:
    - `text` (str): The input text for word deletion.

    Returns:
    - `str`: The text with a randomly deleted word.
    """
    return random_word_deletion(text, num_deletions=1)

def swap_random_words(text):
    """
    Swaps two random words in the text.

    This function randomly swaps two words in the input text, creating variations
    for text augmentation or diversity.

    Parameters:
    - `text` (str): The input text for word swapping.

    Returns:
    - `str`: The text with two words swapped.
    """
    try:
        nltk.download("punkt", quiet=True)
        words = nltk.word_tokenize(text)
        if len(words) > 1:
            idx1, idx2 = random.sample(range(len(words)), 2)
            words[idx1], words[idx2] = words[idx2], words[idx1]
        modified_text = " ".join(words)
        return modified_text
    except Exception as e:
        print(f"An error occurred during word swapping: {str(e)}")
        return text

def insert_synonym(text, word):
    """
    Insert a synonym of the given word into the input text.

    This function replaces the specified word in the input text with a synonym,
    introducing variations for text augmentation or diversity.
    
    Parameters:
    - `text` (str): The input text for synonym insertion.
    - `word` (str): The word for which a synonym will be inserted.

    Returns:
    - `str`: The text with a synonym of the word inserted.
    """
    try:
        synonym = replace_word_with_synonym(word)
        modified_text = text.replace(word, synonym)
        return modified_text
    except Exception as e:
        print(f"An error occurred during synonym insertion: {str(e)}")
        return text


def paraphrase(text):
    """
    Paraphrase the input text.

    This function leverages part-of-speech tagging to identify verbs (VB), nouns (NN),
    and adjectives (JJ) in the input text, replacing them with synonyms for paraphrasing.
    
    Parameters:
    - `text` (str): The input text to be paraphrased.

    Returns:
    - `str`: The paraphrased text.
    """
    try:
        nltk.download("punkt", quiet=True)
        nltk.download("averaged_perceptron_tagger", quiet=True)
        tokens = nltk.word_tokenize(text)
        tagged_tokens = nltk.pos_tag(tokens)
        paraphrased_tokens = [replace_word_with_synonym(token) if tag.startswith(("VB", "NN", "JJ")) else token for token, tag in tagged_tokens]
        paraphrased_text = " ".join(paraphrased_tokens)
        return paraphrased_text
    except Exception as e:
        print(f"An error occurred during paraphrasing: {str(e)}")
        return text

def flip_horizontal(image):
    """
    Flip the input image horizontally.

    Parameters:
    - `image` (PIL.Image.Image): The input image to be flipped.

    Returns:
    - `PIL.Image.Image`: The horizontally flipped image.
    """
    return image.transpose(Image.FLIP_LEFT_RIGHT)

def flip_vertical(image):
    """
    Flip the input image vertically.

    Parameters:
    - `image` (PIL.Image.Image): The input image to be flipped.

    Returns:
    - `PIL.Image.Image`: The vertically flipped image.
    """
    return image.transpose(Image.FLIP_TOP_BOTTOM)

def rotate(image, angle):
    """
    Rotate the input image by a specified angle.

    Parameters:
    - `image` (PIL.Image.Image): The input image to be rotated.
    - `angle` (float): The angle of rotation in degrees.

    Returns:
    - `PIL.Image.Image`: The rotated image.
    """
    rotated_image = image.rotate(angle, resample=Image.BICUBIC, expand=True)
    return crop(rotated_image, (0, 0, *image.size))

def random_rotation(image, max_angle=30):
    """
    Randomly rotate the input image by an angle within the specified range.

    Parameters:
    - `image` (PIL.Image.Image): The input image to be randomly rotated.
    - `max_angle` (float, optional): The maximum absolute angle of rotation in degrees. Default is 30.

    Returns:
    - `PIL.Image.Image`: The randomly rotated image.
    """
    angle = random.uniform(-max_angle, max_angle)
    return rotate(image, angle)

def resize(image, size):
    """
    Resize the input image to the specified size.

    Parameters:
    - `image` (PIL.Image.Image): The input image to be resized.
    - `size` (tuple): The new size in the format (width, height).

    Returns:
    - `PIL.Image.Image`: The resized image.
    """
    return image.resize(size, Image.BICUBIC)

def crop(image, box):
    """
    Crop the input image to the specified rectangular region.

    Parameters:
    - `image` (PIL.Image.Image): The input image to be cropped.
    - `box` (tuple): A tuple (left, upper, right, lower) specifying the region to crop.

    Returns:
    - `PIL.Image.Image`: The cropped image.
    """
    return image.crop(box)

def random_crop(image, size):
    """
    Randomly crop a region from the input image.

    Parameters:
    - `image` (PIL.Image.Image): The input image from which to extract the random crop.
    - `size` (tuple): The size of the output crop in the format (width, height).

    Returns:
    - `PIL.Image.Image`: The randomly cropped image region.
    """
    width, height = image.size
    left = random.randint(0, width - size[0])
    upper = random.randint(0, height - size[1])
    right = left + size[0]
    lower = upper + size[1]
    return crop(image, (left, upper, right, lower))

# DupliPy 0.2.0

def shuffle_words(text):
    """
    Randomly shuffle the order of words in each sentence.

    This function takes a list of sentences and randomly shuffles the order of words
    in each sentence, creating variations for text augmentation or diversity.
    
    Parameters:
    - `text` (list of str): List of sentences where each sentence's words needs to be shuffled.

    Returns:
    - `list of str`: List of sentences with randomly shuffled words.
    """
    # Shuffle the order of words in each sentence
    shuffled_text = []
    with tqdm(total=len(text), desc="Shuffling Words") as pbar:
        for sentence in text:
            words = sentence.split()
            shuffled_words = random.sample(words, len(words))
            shuffled_sentence = ' '.join(shuffled_words)
            shuffled_text.append(shuffled_sentence)
            pbar.update(1)
    return shuffled_text

def random_flip(image, horizontal=True, vertical=True):
    """
    Randomly flip the input image horizontally and/or vertically.

    Parameters:
    - `image` (PIL.Image.Image): The input image to be flipped.
    - `horizontal` (bool): Whether to flip the image horizontally.
    - `vertical` (bool): Whether to flip the image vertically.

    Returns:
    - `PIL.Image.Image`: The randomly flipped image.
    """
    if horizontal and vertical:
        flip = random.choice([Image.FLIP_LEFT_RIGHT, Image.FLIP_TOP_BOTTOM, Image.ROTATE_180])
    elif horizontal:
        flip = Image.FLIP_LEFT_RIGHT
    elif vertical:
        flip = Image.FLIP_TOP_BOTTOM
    else:
        return image

    return image.transpose(flip)

def random_color_jitter(image, brightness=0.2, contrast=0.2, saturation=0.2, hue=0.1):
    """
    Randomly adjust the brightness, contrast, saturation, and hue of the input image.

    Parameters:
    - `image` (PIL.Image.Image): The input image to be color-jittered.
    - `brightness` (float): The maximum factor to adjust brightness.
    - `contrast` (float): The maximum factor to adjust contrast.
    - `saturation` (float): The maximum factor to adjust saturation.
    - `hue` (float): The maximum factor to adjust hue.

    Returns:
    - `PIL.Image.Image`: The color-jittered image.
    """
    image = ImageEnhance.Brightness(image).enhance(1 + random.uniform(-brightness, brightness))
    image = ImageEnhance.Contrast(image).enhance(1 + random.uniform(-contrast, contrast))
    image = ImageEnhance.Color(image).enhance(1 + random.uniform(-saturation, saturation))

    h, s, v = image.convert("HSV").split()
    hue_factor = int(255 * random.uniform(-hue, hue))
    h = h.point(lambda i: (i + hue_factor) % 256)
    image = Image.merge("HSV", (h, s, v)).convert("RGB")

    return image

def noise_overlay(image, noise_factor=0.1, noise_type="gaussian", grain_factor=0.0):
    """
    Overlay noise on the input image.

    Parameters:
        - `image` (PIL.Image.Image): The input image to overlay noise on.
        - `noise_factor` (float): The factor to control the intensity of the noise (0.0 to 1.0).
        - `noise_type` (str): The type of noise to overlay ("gaussian", "salt_and_pepper"). Defaults to "gaussian".
        - `grain_factor` (float): The factor to control the graininess of the noise (0.0 to 1.0). Defaults to 0.0.

    Returns:
        - `PIL.Image.Image`: The image with overlaid noise.
    """
    noise = Image.new("RGB", image.size)

    if noise_type == "gaussian":
        # Generate random Gaussian noise with mean 128 and standard deviation proportional to noise_factor
        for x in range(noise.width):
            for y in range(noise.height):
                noise_value = int(128 + random.gauss(0, noise_factor * 255))
                noise.putpixel((x, y), (noise_value, noise_value, noise_value))
    elif noise_type == "salt_and_pepper":
        # Generate salt and pepper noise with probability proportional to noise_factor
        for x in range(noise.width):
            for y in range(noise.height):
                if random.random() < noise_factor:
                    noise_value = 0 if random.random() < 0.5 else 255
                    noise.putpixel((x, y), (noise_value, noise_value, noise_value))
    else:
        raise ValueError(f"Invalid noise type: {noise_type}")

    # Add grain effect by scaling random noise and blending with original image
    grain_noise = Image.new("RGB", image.size)
    for x in range(grain_noise.width):
        for y in range(grain_noise.height):
            noise_value = int(random.uniform(-grain_factor * 255, grain_factor * 255))
            grain_noise.putpixel((x, y), (noise_value, noise_value, noise_value))

    blended_noise = Image.blend(noise, grain_noise, grain_factor)

    return Image.blend(image, blended_noise, noise_factor)