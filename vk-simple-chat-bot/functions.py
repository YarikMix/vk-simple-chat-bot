from pathlib import Path

import random


def get_random_file(path):
    return random.choice(tuple((path).iterdir()))