from itertools import product

from research.rl_memory import ActivationClass, NetworkXKB


# general method! but is it useful? returns activations right before the query
def calculate_fok(store, cue, target, method, query_time):
    if method == 'cue':
        return store.get_activation(cue, (query_time - 0.0001))
    elif method == 'target':
        # return the activation of what was returned by the query
        return store.get_activation(target, (query_time - 0.0001))

# this function is specific to the AB- Task
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

# This function is specific to the AB- task
def create_graph(store, backlinks, representation, paradigm):
    # paradigm is either 'ABAB', 'ABAD', 'ABCB', 'ABCD'
    create_edge(store, 0, backlinks, representation, 'A', 'B')
    create_edge(store, 1, backlinks, representation, paradigm[2], paradigm[3])

# this function is specific to the AB- task
def query_test(representation, store, fok_method):
    # get from A to B in each representation and then print out the result
    if representation == 'direct':
        # specifying the value at the end of an edge protects from duplicate edges being added to the result map.
        result = store.query(2, {'goes_to_b': 'B'})
        final = result['node_id']
        print('method = ' + fok_method + ' fok = ' + str(calculate_fok(store, 'B', final, fok_method, 2)))
    elif representation == 'pairs':
        result = store.query(2, {'first': 'A'}) # this should give AB or AD
        final = result['second']
        print('method = ' + fok_method + ' fok = ' + str(calculate_fok(store, 'A', final, fok_method, 2)))
    elif representation == 'types':
        result = store.query(2, {'first': 'A'})  # this should give AB or AD
        final = result['second']
        print('method = ' + fok_method + ' fok = ' + str(calculate_fok(store, 'A', final, fok_method, 2)))


    print('query first returns: ' + final)





def test_model(fok_method):
    act_decay_rate = [-0.42, -0.41]
    act_scale_factor = [0.5]
    act_max_steps = [2]
    act_capped = [False, True]
    backlinks = [True, False]
    representation = ['pairs', 'types', 'direct']
    paradigm = ['ABAD', 'ABAB', 'ABCB', 'ABCD']

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
            # 'scale factor = ' + str(scale),
            # 'max steps = ' + str(step),
            'capped = ' + str(cap),
            'backlinks = ' + str(link),
            'representation = ' + rep,
            'paradigm = ' + paradigm
        ]))
        store = NetworkXKB(ActivationClass(rate, scale, step, cap))
        create_graph(store, link, rep, paradigm)
        query_test(rep, store, fok_method)
        print('')



def testy (tasks, fok_method):
    for task in tasks:
        if task == 'AB-':
            for method in fok_method:
                test_model(method)




testy(['AB-'], ['cue', 'target'])