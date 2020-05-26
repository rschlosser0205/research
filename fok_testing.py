from research.rl_memory import NetworkXKB
from research.rl_memory import Activation_Class
def test_networkxkb():
    """Test the NetworkX KnowledgeStore."""


    act_class = Activation_Class(-0.5, 0.5, 4, False)

    store = NetworkXKB(act_class)

    store.store(0, 'node_cat', is_a='node_mammal', has='node_fur', name='cat')
    store.store(1, 'node_bear', is_a='node_mammal', has='node_fur', name='bear')
    store.store(2, 'node_whale', is_a='node_mammal', lives_in='node_water')
    store.store(3, 'node_whale', name='whale') # this activates whale
    #print(store.get_activation('node_whale', 3))
    store.store(4, 'node_fish', is_a='node_animal', lives_in='node_water')
    store.store(5, 'node_mammal', has='node_vertebra', is_a='node_animal')
    # retrieval
    result = store.retrieve(6, 'node_whale')
    print(sorted(result.items()))
    assert sorted(result.items()) == [('is_a', 'node_mammal'), ('lives_in', 'node_water'), ('name', 'whale')]
    # failed query
    result = store.query(7, {'has': 'node_vertebra', 'lives_in': 'node_water'})
    assert result is None
    # unique query
    result = store.query(8, {'has': 'node_vertebra'})

    assert sorted(result.items()) == [('has', 'node_vertebra'), ('is_a', 'node_animal')]
    # query traversal
    store.store(9, 'node_cat')
    # at this point, whale has been activated twice (from the store and the retrieve)
    # prints whale activation list
    print('mammal ' + str(store.get_activation('node_mammal', 11)))
    print('cat ' + str(store.get_activation('node_cat', 11)))
    # while cat has been activated once (from the store)
    # so a search for mammals will give, in order: whale, cat, bear
    result = store.query(11, {'is_a': 'node_mammal'})
    # print(result['name'])
    assert result['name'] == 'whale'
    assert store.has_next_result


    result = store.next_result(11)
    assert result['name'] == 'cat'
    assert store.has_next_result
    result = store.next_result(11)
    print('bear ' + str(store.get_activation('node_bear', 11)))

    assert result['name'] == 'bear'
    assert not store.has_next_result
    assert store.has_prev_result
    result = store.prev_result(11)
    assert store.has_prev_result
    result = store.prev_result(11)

    assert result['name'] == 'whale'
    assert not store.has_prev_result

    print('bear ' + str(store.get_activation('node_bear', 11)))
    print('cat ' + str(store.get_activation('node_cat', 12)))
    print('whale ' + str(store.get_activation('node_whale', 12)))


# this function moved to Model_Generation.py
def test_model(act_decay_rate, act_scale_factor, act_max_steps, act_capped, backlinks, representation):
    # play with the parameters of activation class (decay_rate, scale_factor, max_steps, capped)
    # things to include-- changes in directionality? BACKLINKS VS NONE
    act_class = Activation_Class(act_decay_rate, act_scale_factor, act_max_steps, act_capped)
    store = NetworkXKB(act_class)
    # FIXME add a function that takes in a store and the rep parameters. this function will create the graph
        # where does this function go? in here or in networkx?
        # this function will accomplish store.store(...) * 4 or whatever
    # FIXME add other representations
    # FIXME add queries and retrievals to get from A to B in all representations
    # FIXME add node id as outgoing edge/attribute

    # one level (?) representation
    store.store(0, 'A', goes_to='B')
    store.store(0, 'A', goes_to='D')
    store.store(0, 'C', goes_to='B')
    store.store(0, 'C', goes_to='D')
    # get from A to B
    store.query(1, {'goes_to': 'B'})


    # two-level representation
    store.store(0, 'AB', first='A', second='B')
    store.store(1, 'AD', first='A', second='D')
    store.store(1, 'CB', first='C', second='B')
    store.store(1, 'CD', first='C', second='D')


test_networkxkb()
#test_model(-0.5, 0.5, 4, False, False, 2)