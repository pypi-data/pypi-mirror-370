import random

def choice_weighted(items, weights):
    return random.choices(items, weights=weights, k=1)[0]