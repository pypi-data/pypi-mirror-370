import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Embedding, TimeDistributed, Dense, Bidirectional
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.utils import to_categorical
import pickle
import re
import os
import requests # Added to fetch the Excel file
import io # Added to read binary data from a URL

# -----------------------------
# N-Gram Helper Functions
# -----------------------------
def generate_ngrams(word, n):
    """Generates n-grams for a given word."""
    return [word[i:i+n] for i in range(len(word)-n+1)]

def find_nearest_word_by_ngram(unknown_word, known_words, n=3):
    """Finds the nearest known word using n-gram overlap."""
    target_ngrams = set(generate_ngrams(unknown_word, n))
    max_overlap = 0
    best_match = None
    for w in known_words:
        w_ngrams = set(generate_ngrams(w, n))
        overlap = len(target_ngrams & w_ngrams)
        if overlap > max_overlap:
            max_overlap = overlap
            best_match = w
    return best_match

# -----------------------------
# Universal Suffix-Based Normalizer
# -----------------------------
def get_suffix_list(dictionary, min_len=2, max_len=4):
    """Extracts a sorted list of common suffixes from a dictionary."""
    suffix_set = set()
    for word in dictionary:
        for L in range(min_len, min(max_len, len(word)) + 1):
            suffix_set.add(word[-L:])
    return sorted(suffix_set, key=lambda x: -len(x))

def normalize_word(word, word_to_tag, known_suffixes):
    """Normalizes a word by removing common suffixes if the stem is a known word."""
    for suffix in known_suffixes:
        if word.endswith(suffix):
            candidate = word[:-len(suffix)]
            if candidate in word_to_tag:
                return candidate
    return word

# -----------------------------
# Main function for training and prediction
# -----------------------------
def run_pos_tagger(column_name, train=True):
    """
    Trains or loads a POS tagger model for a specific dialect column.

    Args:
        column_name (str): The name of the dialect column to use from the dataset.
        train (bool): If True, trains a new model. If False, loads an existing model.
    """
    print(f"✅ Preparing POS tagger for column: {column_name}")

    # File paths (Local file and GitHub URL)
    pos_data_url = "https://raw.githubusercontent.com/ShakirHaque/BRNLTK/refs/heads/main/PritomBanglaversion%202.2.xlsx%20-%20Sheet1.csv"
    training_data_url = "https://raw.githubusercontent.com/ShakirHaque/BRNLTK/refs/heads/main/Regional_sentence.csv"
    
    # File names for local model files
    model_file = f"lstm_pos_model_{column_name}.h5"
    word_tokenizer_file = f"word_tokenizer_{column_name}.pkl"
    tag_tokenizer_file = f"tag_tokenizer_{column_name}.pkl"
    
    try:
        # Load POS dictionary from URL using requests and io
        pos_response = requests.get(pos_data_url)
        pos_df = pd.read_csv(io.StringIO(pos_response.text)) # Assuming the Excel sheet was converted to CSV
        
        speech_words_raw = pos_df[column_name].astype(str).str.strip()
        general_words_raw = pos_df['General'].astype(str).str.strip()
        tags_raw = pos_df['Updated Human'].astype(str).str.strip()

        word_to_tag = dict()
        for s_word, g_word, tag in zip(speech_words_raw, general_words_raw, tags_raw):
            for w in {s_word, g_word}:
                if w:
                    word_to_tag[w] = tag

        known_suffixes = get_suffix_list(word_to_tag)

    except Exception as e:
        print(f"❌ Error loading data from URL: {e}")
        return None, None, None

    if train:
        print("🛠️ Training new model...")
        try:
            # Load and prepare training data from URL
            sent_df = pd.read_csv(training_data_url)
            sentences_raw = sent_df[column_name].dropna().tolist()
        except Exception as e:
            print(f"❌ Error loading training data from URL: {e}")
            return None, None, None

        X, y = [], []
        for sent in sentences_raw:
            words = sent.strip().split()
            tags = []
            for w in words:
                tag = word_to_tag.get(w)
                if tag:
                    tags.append(tag)
                else:
                    norm_w = normalize_word(w, word_to_tag, known_suffixes)
                    tag = word_to_tag.get(norm_w)
                    if tag:
                        tags.append(tag)
                    else:
                        tags.append('UNK')
            X.append(words)
            y.append(tags)

        # Tokenization
        word_tokenizer = Tokenizer(lower=False, filters='', oov_token='<UNK>')
        tag_tokenizer = Tokenizer(lower=False, filters='')
        word_tokenizer.fit_on_texts(X)
        tag_tokenizer.fit_on_texts(y)

        if '<UNK>' not in tag_tokenizer.word_index:
            tag_tokenizer.word_index['<UNK>'] = len(tag_tokenizer.word_index) + 1
            tag_tokenizer.index_word[tag_tokenizer.word_index['<UNK>']] = '<UNK>'

        X_seq = word_tokenizer.texts_to_sequences(X)
        y_seq = tag_tokenizer.texts_to_sequences(y)

        max_len = max(len(seq) for seq in X_seq)
        X_padded = pad_sequences(X_seq, maxlen=max_len, padding='post')
        y_padded = pad_sequences(y_seq, maxlen=max_len, padding='post')
        y_final = [to_categorical(seq, num_classes=len(tag_tokenizer.word_index)+1) for seq in y_padded]

        X_train = X_padded
        y_train = np.array(y_final)

        # Build and train the LSTM model
        model = Sequential()
        model.add(Embedding(input_dim=len(word_tokenizer.word_index) + 1, output_dim=64, input_length=max_len))
        model.add(Bidirectional(LSTM(units=64, return_sequences=True)))
        model.add(TimeDistributed(Dense(len(tag_tokenizer.word_index) + 1, activation="softmax")))
        model.compile(optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"])
        model.summary()
        model.fit(X_train, y_train, batch_size=32, epochs=10, validation_split=0.1)

        model.save(model_file)
        with open(word_tokenizer_file, "wb") as f:
            pickle.dump(word_tokenizer, f)
        with open(tag_tokenizer_file, "wb") as f:
            pickle.dump(tag_tokenizer, f)
        print("✅ Model trained and saved successfully.")
    
    def predict_pos_tags(new_sentence, return_confidence=False):
        """
        Predicts POS tags for a new sentence using the loaded model and fallback mechanisms.
        """
        try:
            model = load_model(model_file)
            with open(word_tokenizer_file, "rb") as f:
                word_tokenizer = pickle.load(f)
            with open(tag_tokenizer_file, "rb") as f:
                tag_tokenizer = pickle.load(f)
        except FileNotFoundError:
            print("❌ Required files not found. Please train the model first by setting 'train=True'.")
            return []

        reverse_tag_index = {v: k for k, v in tag_tokenizer.word_index.items()}
        orig_words = new_sentence.strip().split()
        norm_words_for_model = [normalize_word(w, word_to_tag, known_suffixes) for w in orig_words]
        seq = word_tokenizer.texts_to_sequences([norm_words_for_model])
        padded = pad_sequences(seq, maxlen=model.input_shape[1], padding='post')
        preds = model.predict(padded, verbose=0)

        predicted_tags_info = []

        for i, word in enumerate(orig_words):
            tag = None
            confidence = None

            # 1. Lookup in the full dictionary first
            tag = word_to_tag.get(word)
            if not tag:
                # 2. Try with suffix-based normalization
                norm_word = normalize_word(word, word_to_tag, known_suffixes)
                tag = word_to_tag.get(norm_word)
            
            # 3. Try N-gram-based similarity
            if not tag:
                nearest = find_nearest_word_by_ngram(word, list(word_to_tag.keys()))
                if nearest:
                    tag = word_to_tag.get(nearest)

            # 4. Fallback to model prediction
            if not tag:
                if i < len(preds[0]):
                    tag_id = np.argmax(preds[0][i])
                    confidence = float(preds[0][i][tag_id])
                    tag = reverse_tag_index.get(tag_id, 'N_NN')
                else:
                    tag = 'N_NN'
                    confidence = 0.0
            else:
                confidence = 1.0

            predicted_tags_info.append((word, tag, confidence) if return_confidence else (word, tag))

        return predicted_tags_info
    
    return predict_pos_tags, known_suffixes, word_to_tag