from research.rl_memory import NetworkXKB
from research.rl_memory import ActivationClass

act_on = False

def jeopardy_test():
    act_class = ActivationClass(-0.5, 0.5, 4, False)
    store = NetworkXKB(act_class)
    terms = {'also_called': 'plan_showing_streets', 'num_letters': '4'}

    store.store(0, True, act_on, 'plan_showing_streets', type='object')
    store.store(0, True, act_on, 'node_map', also_called='plan_showing_streets', num_letters='3', name='map')
    store.store(0, True, act_on, 'node_street_network', also_called='plan_showing_streets', num_letters='14', name='street_network')
    store.store(0, True, act_on, 'node_bus_routes', also_called='plan_showing_streets', num_letters='9', name='bus_routes')
    store.store(0, True, act_on, 'node_freeway_system', also_called='plan_showing_streets', num_letters='13', name='freeway_system')
    store.store(0, True, act_on, 'node_grid', also_called='plan_showing_streets', num_letters='4', name='grid')

    # order matters during population

    result = store.query(1, terms)

    return result['name']



print(jeopardy_test())