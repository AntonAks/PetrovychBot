import nltk

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
    if (current_row[n] / len(first_word)) <= 0.15:
        match = True
    return current_row[n],  current_row[n] / len(first_word), match


def lev_deist_for_lists(list1, list2):
    if abs(len(list1) - len(list2)) > 1:
        return False

    result = [l1 for l1 in list1 for l2 in list2 if get_levenshtein_distance(l1, l2)[2]]

    if abs(len(list1) - len(result)) < 1:
        return True


def find_answer(user_text, short_talk_dict):
    result = 'Unknown'
    ignore_words = ['?', '!', '.', ',']

    user_text_tokenized = nltk.word_tokenize(user_text)
    user_text_list = [x for x in user_text_tokenized if x not in ignore_words]

    keys = short_talk_dict.keys()
    for key in keys:
        for phrase in short_talk_dict[key]['phrase']:
            phrase_tokenized = nltk.word_tokenize(phrase)
            words = [word for word in phrase_tokenized if word not in ignore_words]

            if lev_deist_for_lists(user_text_list, words):
                result = key
                return result

    return result
