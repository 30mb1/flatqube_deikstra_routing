from collections import namedtuple
from utils import ALL_TOKENS, VERTEXES, calculate_price, get_pair_output, initialize, symbol, DECIMALS
import logging


PathPoint = namedtuple('PathPoint', ['token_amount', 'price'])


def get_shortest_path(from_token_amount, from_token, to_token):
    if from_token not in ALL_TOKENS or to_token not in ALL_TOKENS:
        raise Exception('Fuck you')

    if from_token == to_token:
        raise Exception('Fuck you')

    logging.info(f'Searching for best path from {symbol(from_token)} to {symbol(to_token)}')
    # key - token, value - shortest path (best amount we can get)
    # initially, all paths length are 0
    highest_values = {token: PathPoint(0, 0) for token in ALL_TOKENS}
    highest_values[from_token] = PathPoint(from_token_amount, calculate_price(from_token, from_token_amount))
    # key - token, value - boolean, indicating if we were here
    was_here = {token: False for token in ALL_TOKENS}
    # we need this dict to reconstruct path after algorithm end
    # key - token, value - previous token in our path
    prev_token_in_path = {}

    # we made exactly N iterations
    for i in range(len(ALL_TOKENS)):
        # get all unvisited nodes
        unvisited_tokens = [token for token in was_here.keys() if was_here[token] == False]
        # select node with the shortest path (highest value in our case) between unvisited nodes
        highest_values_sorted = sorted(unvisited_tokens, key=lambda x: highest_values[x].price, reverse=True)

        cur_token = highest_values_sorted[0]
        logging.info(f'Iteration #{i} out of max {len(ALL_TOKENS)}, trying to get better pathes from token {symbol(cur_token)}')

        # we reached desired token! Yeeeeeaaah
        if cur_token == to_token:
            logging.info(f'We reached desired token!')
            break

        was_here[cur_token] = True
        for connected_token in VERTEXES[cur_token]:
            # dont check used nodes
            if was_here[connected_token] is True:
                continue
            # now we try to upgrade path to all nodes connected to current node.
            # we check if new path from current node to connected node is better than
            # path, that we already store for connected node
            new_value = get_pair_output(highest_values[cur_token].token_amount, cur_token, connected_token)

            if new_value > highest_values[connected_token].token_amount:
                old_best_val = highest_values[connected_token]
                new_best_val = PathPoint(new_value, calculate_price(connected_token, new_value))

                highest_values[connected_token] = new_best_val
                prev_token_in_path[connected_token] = cur_token

                logging.info(f'Path to token {symbol(connected_token)} was improved from {old_best_val.price}$ to {new_best_val.price}$')

    # now we just need to reconstruct the path
    cur_node = prev_token_in_path[to_token]
    path = [to_token]

    while cur_node != from_token:
        path.append(cur_node)
        cur_node = prev_token_in_path[cur_node]

    path.append(from_token)
    # reverse path, because we reconstructed it from the end
    path.reverse()
    print ([symbol(i) for i in path])
    print ([f'{highest_values[i].token_amount / 10**DECIMALS[i]}' for i in path])
    print ([f'{highest_values[i].price}$' for i in path])
    return path

initialize()
get_shortest_path(
    1_000_000_000_000, # 1000 evers to dusa
    '0:a49cd4e158a9a15555e624759e2e4e766d22600b7800d891e46f9291f044a93d',
    '0:b3ed4b9402881c7638566b410dda055344679b065dce19807497c62202ba9ce3'
)
