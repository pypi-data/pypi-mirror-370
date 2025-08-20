import pandas as pd
from difflib import get_close_matches
import os
import requests
import io

# -----------------------------
# N-Gram Helper Functions
# -----------------------------
def ngram_similarity(word1, word2, n=2):
    """Calculate n-gram similarity between two words"""
    def get_ngrams(word):
        return {word[i:i+n] for i in range(len(word)-n+1)}
    
    set1, set2 = get_ngrams(word1), get_ngrams(word2)
    
    if not set1 or not set2:
        return 0
    
    return len(set1 & set2) / len(set1 | set2)

# -----------------------------
# Translator function
# -----------------------------
def translate(sentence, from_area, to_area, threshold=0.5):
    """
    Translates a sentence from one Bengali dialect to another based on n-gram similarity.

    Args:
        sentence (str): The input sentence to translate.
        from_area (str): The source dialect column name (e.g., 'General').
        to_area (str): The target dialect column name (e.g., 'Chittagong_bangla_speech').
        threshold (float): The minimum n-gram similarity score for a word to be considered a match.

    Returns:
        str: The translated sentence.
    """
    # Use the correct raw GitHub URL. Note the missing closing parenthesis in your original URL.
    excel_url = "https://raw.githubusercontent.com/ShakirHaque/BRNLTK/refs/heads/main/PritomBanglaversion%202.2.xlsx%20-%20Sheet1.csv"
    
    try:
        # Load data from the URL using requests and io
        response = requests.get(excel_url)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        
        # Read the content into a pandas DataFrame.
        # Note: Your URL seems to point to a CSV, not an Excel file.
        # So I am using pd.read_csv. If it is an Excel file, you would use pd.read_excel(io.BytesIO(response.content)).
        df = pd.read_csv(io.StringIO(response.text))
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching the file from URL: {e}")
        return sentence
    except Exception as e:
        print(f"❌ An error occurred while loading the data: {e}")
        return sentence

    words = sentence.strip().split()
    translated_words = []

    for word in words:
        matched_row = None
        best_score = 0

        # Loop over dataset rows for best match
        for _, row in df.iterrows():
            source_word = str(row.get(from_area, '')).strip()
            # Handle potential KeyError if column_name does not exist
            if not source_word:
                continue
                
            sim = ngram_similarity(word, source_word)

            if sim > best_score and sim >= threshold:
                best_score = sim
                matched_row = row

        # If match found, translate to target area
        if matched_row is not None and to_area in matched_row:
            translated_words.append(str(matched_row[to_area]))
        else:
            translated_words.append(word)  # no change if no match

    return " ".join(translated_words)