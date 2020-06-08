from research.rl_memory import NetworkXKB
from research.rl_memory import ActivationClass

def jeopardy_test():
    act_class = ActivationClass(-0.5, 0.5, 4, False)
    store = NetworkXKB(act_class)
    terms = [{'also_called': 'plans_showing_streets'}, {'num_letters': '4'}]

    store.store(0, True, 'plans_showing_streets', type='object')
    store.store(0, True, 'node_map', also_called='plans_showing_streets', num_letters= '3', name='map')
    store.store(0, True, 'node_grid', also_called='plans_showing_streets', num_letters='4', name='grid')

    result = store.query(1, terms[0])


    for item in range(len(store.query_results)):
        if result[list(terms[1])[0]] == terms[1].get(list(terms[1])[0]):
            return result['name']
        else:
            result = store.next_result(1)

    return 'no result found'



print(jeopardy_test())