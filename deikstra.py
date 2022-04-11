from collections import namedtuple
from utils import ALL_TOKENS, VERTEXES, calculate_price, get_pair_output, initialize, symbol, DECIMALS
from heap import BinaryHeap
import logging


PathPoint = namedtuple('PathPoint', ['token', 'price'])


def get_shortest_path(from_token_amount, from_token, to_token):
    if from_token not in ALL_TOKENS or to_token not in ALL_TOKENS:
        raise Exception('Fuck you')

    if from_token == to_token:
        raise Exception('Fuck you')

    logging.info(f'Searching for best path from {symbol(from_token)} to {symbol(to_token)}')
    # key - token, value - shortest path (best amount we can get)
    # initially, all paths length are 0
    best_value_for_token = {token: 0 for token in ALL_TOKENS}
    best_value_for_token[from_token] = from_token_amount
    # key - token, value - boolean, indicating if we were here
    was_here = {token: False for token in ALL_TOKENS}
    # we need this dict to reconstruct path after algorithm end
    # key - token, value - previous token in our path
    prev_token_in_path = {}

    # we store such elements in heap, so that with pop() we always get PathPoint with best price
    first_path_point = PathPoint(from_token, calculate_price(from_token, from_token_amount))
    # for comparison key we use negative price, because heap is sorted in ascending order
    path_heap = BinaryHeap([first_path_point], key=lambda x: -x.price)

    # we made exactly N iterations
    for i in range(len(ALL_TOKENS)):
        # get unvisited node with shortest path (best price)
        cur_point = path_heap.pop()

        cur_token = cur_point.token
        # get token amount that we have in this node
        cur_amount = best_value_for_token[cur_token]
        logging.info(f'Iteration #{i} out of max {len(ALL_TOKENS)}, trying to get better pathes from token {symbol(cur_token)}')

        # we reached desired token! Yeeeeeaaah
        if cur_token == to_token:
            logging.info(f'We reached desired token!')
            break

        # mark this node as visited
        was_here[cur_token] = True
        for connected_token in VERTEXES[cur_token]:
            # dont check used nodes
            if was_here[connected_token] is True:
                continue
            # now we try to upgrade path to all nodes connected to current node.
            # we check if new path from current node to connected node is better than
            # path, that we already store for connected node
            new_best_value = get_pair_output(cur_amount, cur_token, connected_token)
            new_price = calculate_price(connected_token, new_best_value)

            if new_best_value > best_value_for_token[connected_token]:
                old_best_val = best_value_for_token[connected_token]
                old_price = calculate_price(connected_token, old_best_val)

                new_path_point = PathPoint(connected_token, new_price)
                path_heap.push(new_path_point)

                best_value_for_token[connected_token] = new_best_value
                prev_token_in_path[connected_token] = cur_token

                logging.info(f'Path to token {symbol(connected_token)} was improved from {old_price}$ to {new_price}$')

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
    print ([f'{best_value_for_token[i] / 10**DECIMALS[i]}' for i in path])
    print ([f'{calculate_price(i, best_value_for_token[i])}$' for i in path])
    return path

initialize()
