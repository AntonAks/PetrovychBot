from random import choice
from engine import get_levenshtein_distance
import settings

short_talks = settings.SHORT_TALKS


def short_talk_answer(message) -> tuple:
    keys = short_talks.keys()
    for key in keys:
        for phrase in short_talks[key]['phrase']:
            if get_levenshtein_distance(phrase, message)[2] or \
                    get_levenshtein_distance('Петрович ' + phrase, message)[2] or \
                    get_levenshtein_distance(phrase + ' Петрович', message)[2]:
                answer = choice(short_talks[key]['answer']), True
                return answer

    if 'петрович' in message.lower():
        answer = choice(short_talks['Unknown']['answer']), False
        return answer
