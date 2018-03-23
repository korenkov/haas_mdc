import random
import string


def get_random_color():
    return random.choice([
        'red',
        'green',
        'blue',
        'yellow',
        'black'
    ])


def get_random_chars(k=12):
    choices = list(string.ascii_letters) + list(string.digits)
    return ''.join(random.choices(choices, k=k))