from typing import Union, Tuple
import pandas as pd
import numpy as np
import time
from functools import cache
pd.options.mode.chained_assignment = None  # default='warn'

freq_df = pd.read_csv('frequency.csv').rename(columns={'count': 'frequency'})
with open('allowed.txt', 'rt') as f:
    words = f.read().splitlines()
with open('answers.txt', 'rt') as f:
    answers = f.read().splitlines()

words = list({*words, *answers})
words.sort()
words_df = pd.DataFrame(words, columns=['word'])
letters = list('abcdefghijklmnopqrstuvwxyz')
letter_freq = {l: 0 for l in letters}
for word in answers:
    for letter in word:
        letter_freq[letter] += 1

# good = letters left in the alphabet
# known = letters in the answer
# mask = 'aba__' for 'abase' =='abaft'


@cache
def score(word):
    return sum(letter_freq[letter] for letter in set(word))


@cache
def get_mask(word, answer):
    return ''.join([w if w == a else '_' for w, a in zip(word, answer)])


def evaluate(word: str, answer: str, good, known) -> Tuple[list, list, list]:
    for w in word:
        if w not in answer:
            if w in good:
                good.remove(w)
        else:
            known.append(w)
    return good, list(set(known)), get_mask(word, answer)


@cache
def is_mask(word, mask):
    return all(
        [
            (m == '_' or w == m)
            for w, m in zip(word, mask)
        ]
    )


def fits(word, good, known, mask):
    ws = set(word)
    return ws.issubset(set(good)) and set(known).issubset(ws) and is_mask(word, mask)


def guess(words_df, guessed, good, known, mask, dumb_player=False):
    key = f'{word}_fits'
    words_df[key] = words_df['word'].apply(lambda w: fits(w, good, known, mask))
    guesses = words_df[words_df[key] == True]
    if 'frequency' not in guesses.columns:
        guesses = guesses.merge(freq_df, on='word', how='left')
    if dumb_player:
        return guesses, guesses[(guesses['frequency'] == guesses['frequency'].max()) & (~guesses.word.isin(guessed))].word.iloc[0]
    else:
        if 'score' not in guesses.columns:
            guesses['score'] = guesses['word'].apply(lambda w: score(w))
        tmp = guesses[(guesses.score == guesses.score.max()) & (~guesses.word.isin(guessed))]
        if len(tmp) == 0:
            raise Exception('No words found')
        return guesses, tmp[tmp.score == tmp.score.max()].word.iloc[0]


def solve(word, answer, dumb_player=False):
    if len(word) != 5:
        return 1000
    guessed = []
    good, known, mask = evaluate(word, answer, letters.copy(), [])
    kw = words_df.copy()

    i = 1
    while True:
        try:
            kw, g = guess(kw[(~kw.word.isin(guessed))], guessed, good, known, mask, dumb_player)
        except Exception as e:
            print(word, answer, dumb_player)
            raise e
        if g in guessed:
            raise Exception('Duplicate word found, on {}, {}, {}'.format(word, answer, dumb_player))
        guessed.append(g)
        good, known, mask = evaluate(guessed[-1], answer, good, known)
        if guessed[-1] == answer:
            return len(guessed)
        i += 1
        if i >= 5:
            return 5


if __name__ == '__main__':
    t = time.time()
    print(np.mean([solve('rubin', w, True) for w in answers]))
    print(time.time() - t)
