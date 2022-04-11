import requests
import logging
from collections import defaultdict
from multiprocessing.pool import ThreadPool
import json
logging.getLogger().setLevel(logging.INFO)

# -------------------------------------- UTILS ----------------------------------------
def get_token_price(token_addr):
    res = requests.post(f'https://ton-swap-indexer.broxus.com/v1/currencies/{token_addr}')
    return float(res.json()['price'])


# key - pair tuple, value - balances tuple
# pairs are sorted by address body value,
PAIRS_SUPPLY = {}
# key - token, value - list of tokens this token has connections to
VERTEXES = defaultdict(lambda: [])
# list of all tokens we have in DEX
ALL_TOKENS = []
# $ prices of all tokens we have in DEX
PRICES = {}
# address to symbol
SYMBOLS = {}
# address to decimals
DECIMALS = {}


def initialize_meta():
    global SYMBOLS
    global DECIMALS

    with open('manifest.json', 'r') as f:
        meta = json.load(f)
        for token in meta['tokens']:
            SYMBOLS[token['address']] = token['symbol']
            DECIMALS[token['address']] = int(token['decimals'])

def initialize_pairs_data():
    global ALL_TOKENS
    global PAIRS_SUPPLY

    with open('pairs.txt', 'r') as f:
        lines = [line.split(',') for line in f.readlines()]

    for left_token, right_token, left_bal, right_bal in lines:
        ALL_TOKENS.append(left_token)
        ALL_TOKENS.append(right_token)
        # save vertexes
        VERTEXES[left_token].append(right_token)
        VERTEXES[right_token].append(left_token)
        # smaller token first
        left_bal, right_bal = int(left_bal), int(right_bal)
        if int(left_token[2:], 16) < int(right_token[2:], 16):
            PAIRS_SUPPLY[(left_token, right_token)] = (left_bal, right_bal)
        else:
            PAIRS_SUPPLY[(right_token, left_token)] = (right_bal, left_bal)

    # remove duplicates
    ALL_TOKENS = list(set(ALL_TOKENS))


def initialize_prices_data():
    global PRICES

    with open('prices.json', 'r') as f:
        PRICES = json.load(f)


def sort_tokens(from_token, to_token):
    if int(from_token[2:], 16) < int(to_token[2:], 16):
        return (from_token, to_token)
    return (to_token, from_token)

# return to_token output amount for pair (from_token, to_token) with from_token input amount
def get_pair_output(from_token_amount, from_token, to_token):
    # sort tokens to get correct supply balances
    sorted_tokens = sort_tokens(from_token, to_token)

    if sorted_tokens == (from_token, to_token):
        (from_bal, to_bal) = PAIRS_SUPPLY[(from_token, to_token)]
    else:
        (to_bal, from_bal) = PAIRS_SUPPLY[(to_token, from_token)]

    if from_bal == 0 or to_bal == 0:
        return 0

    # uniswap real math
    from_fee = int(from_token_amount * 3) / 1000
    new_from_bal = from_bal + from_token_amount
    new_to_bal = int(from_bal * to_bal) / int(new_from_bal - int(from_fee))
    expected_to_amount = to_bal - int(new_to_bal)

    return expected_to_amount


def calculate_price(token, token_amount):
    # cant calculate price correct for tokens with undefined decimals (
    decimals = 10
    if token in DECIMALS:
        decimals = 10**DECIMALS[token]
    return (token_amount / decimals) * PRICES[token]


def symbol(token_addr):
    if token_addr in SYMBOLS:
        return SYMBOLS[token_addr]
    return token_addr


def initialize():
    initialize_pairs_data()
    initialize_prices_data()
    initialize_meta()
