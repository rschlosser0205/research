from itertools import product

from research.rl_memory import ActivationClass, NetworkXKB


def create_edge(store, time, backlinks, representation, src, dst):
    # src and dst would be either 'A', 'B', 'C', 'D'
    if representation == 'direct':
        store.store(time, backlinks, src, **{'goes_to_' + dst.lower(): dst, })
    elif representation == 'pairs':
        # two-level representation
        store.store(time, backlinks, src + dst, first=src, second=dst)
    elif representation == 'types':
        # three levels (type=pairs is a shared child of AB and CD)
        store.store(time, backlinks, src + dst, first=src, second=dst, type='pairs')

# comment out the two unused pairs!
def create_graph(store, backlinks, representation, paradigm):
    # paradigm is either 'ABAB', 'ABAD', 'ABCB', 'ABCD'
    create_edge(store, 0, backlinks, representation, 'A', 'B')
    create_edge(store, 1, backlinks, representation, paradigm[2], paradigm[3])

# FIXME refactor?
def query_test(representation, store):
    # get from A to B in each representation and then print out the result
    if representation == 'direct':
        # specifying the value at the end of an edge protects from duplicate edges being added to the result map.
        result = store.query(2, {'goes_to_b': 'B'})
        final = result['node_id']
    elif representation == 'pairs':
        result = store.query(2, {'first': 'A'}) # this should give AB or AD
        final = result['second']
    elif representation == 'types':
        result = store.query(2, {'first': 'A'})  # this should give AB or AD
        final = result['second']
    print('query first returns: ' + final)

def test_model():
    act_decay_rate = [-0.5, -0.25]
    act_scale_factor = [0.5, 0.25]
    act_max_steps = [2, 3]
    act_capped = [True, False]
    backlinks = [True, False]
    representation = ['direct', 'pairs', 'types']
    paradigm = ['ABAB', 'ABAD', 'ABCB', 'ABCD']

    generator = product(
        act_decay_rate,
        act_scale_factor,
        act_max_steps,
        act_capped,
        backlinks,
        representation,
        paradigm,
    )

    for rate, scale, step, cap, link, rep, paradigm in generator:
        print(', '.join([
            'decay rate = ' + str(rate),
            'scale factor = ' + str(scale),
            'max steps = ' + str(step),
            'capped = ' + str(cap),
            'backlinks = ' + str(link),
            'representation = ' + str(rep),
        ]))
        store = NetworkXKB(ActivationClass(rate, scale, step, cap))
        create_graph(store, link, rep, paradigm)
        query_test(rep, store)

test_model()