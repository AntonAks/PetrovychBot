from random import choice
from engine import get_levenshtein_distance

short_talks = {
    "How are you": {
        "phrase": ['как дела?',
                   'как жизнь?',
                   'как здоровье?',
                   'как оно?'],
        "answer": ["Живее всех живых!",
                   "Не дождешься",
                   "Грех жаловаться",
                   "Годится",
                   "Много не мало"],
    },
    "Hello": {
        "phrase": ['привет.',
                   'Петрович?',
                   'ты тут?',
                   'ты здесь?',
                   'салют'],
        "answer": ['Чем могу быть полезен? /help',
                   'Здорова!',
                   'Есть чо..?',
                   'На позиции!'],
    }
}


def short_talk_answer(message):
    keys = short_talks.keys()
    for key in keys:
        for phrase in short_talks[key]['phrase']:
            if get_levenshtein_distance(phrase, message)[2] or \
                    get_levenshtein_distance('Петрович ' + phrase, message)[2]:
                return choice(short_talks[key]['answer'])

