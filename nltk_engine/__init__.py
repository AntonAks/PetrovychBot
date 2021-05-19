import nltk
import numpy as np
from nltk.stem.porter import PorterStemmer

nltk.download('punkt')


def get_levenshtein_distance(first_word: str, second_word: str) -> tuple:
    match = False
    first_word = first_word.lower()
    second_word = second_word.lower()

    n, m = len(first_word), len(second_word)

    if n > m:        # Make sure n <= m, to use O(min(n,m)) space
        first_word, second_word = second_word, first_word
        n, m = m, n
    current_row = range(n+1)

    for i in range(1, m+1):
        previous_row, current_row = current_row, [i]+[0]*n
        for j in range(1, n+1):
            add, delete, change = previous_row[j]+1, current_row[j-1]+1, previous_row[j-1]
            if first_word[j - 1] != second_word[i - 1]:
                change += 1
            current_row[j] = min(add, delete, change)
    if (current_row[n] / len(first_word)) <= 0.17:
        match = True
    return current_row[n],  current_row[n] / len(first_word), match


def tokenize(sentence):
    return nltk.word_tokenize(sentence)


def stem(word):
    stemmer = PorterStemmer()
    return stemmer.stem(word.lower())


def bag_of_words(tokenized_sentence, all_words):

    tokenized_sentence = [stem(w) for w in tokenized_sentence]
    bag = np.zeros(len(all_words), dtype=np.float32)
    for idx, w in enumerate(all_words):
        if w in tokenized_sentence:
            bag[idx] = 1.0

    return bag
