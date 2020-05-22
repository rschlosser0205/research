from research.rl_memory import NetworkXKB
from research.rl_memory import Activation_Class
def test_networkxkb():
    """Test the NetworkX KnowledgeStore."""
    #i am making a change
    #
    # def activation_fn(graph, mem_id):
    #         # append to existing activation list
    #         graph.nodes[mem_id]['activation'].append(1)
    #
    # def activation_fn_time(graph, mem_id, time_stamp):
    #     recursive_activation(graph, mem_id, time_stamp, 1, 4)
    #
    # def recursive_activation(graph, mem_id, time_stamp, scale_factor, max_steps):
    #     result = list(graph.successors(mem_id))
    #     # appends time stamp and scale factor
    #     if max_steps is 0 or len(result) is 0:
    #         return
    #
    #     graph.nodes[mem_id]['activation'].append((time_stamp, scale_factor))
    #
    #     for successor in result:
    #         if successor != mem_id:
    #             print('successor of ' + mem_id + " is " + successor)
    #             recursive_activation(graph, successor, time_stamp, scale_factor / 2, max_steps - 1)

    act_class = Activation_Class(-0.5, 0.5, 4)

    store = NetworkXKB(act_class)

    store.store(0, 'node_cat', is_a='node_mammal', has='node_fur', name='cat')
    #FIXME add node to beginning of things that are not names!
    store.store(1, 'node_bear', is_a='node_mammal', has='node_fur', name='bear')
    store.store(2, 'node_whale', is_a='node_mammal', lives_in='node_water')
    store.store(3, 'node_whale', name='whale') # this activates whale
    print(store.get_activation('node_whale', 3))
    store.store(4, 'node_fish', is_a='node_animal', lives_in='node_water')
    store.store(5, 'node_mammal', has='node_vertebra', is_a='node_animal')
    # retrieval
    result = store.retrieve(6, 'node_whale')
    assert sorted(result.items()) == [('is_a', 'node_mammal'), ('lives_in', 'node_water'), ('name', 'whale')]
    # failed query
    result = store.query(7, {'has': 'node_vertebra', 'lives_in': 'node_water'})
    assert result is None
    # unique query
    result = store.query(8, {'has': 'node_vertebra'})

    assert sorted(result.items()) == [('has', 'node_vertebra'), ('is_a', 'node_animal')]
    # query traversal
    store.store(9, 'cat')
    # at this point, whale has been activated twice (from the store and the retrieve)
    # prints whale activation list
    print(store.get_activation('node_whale', 11))
    # while cat has been activated once (from the store)
    # so a search for mammals will give, in order: whale, cat, bear
    result = store.query(11, {'is_a': 'node_mammal'})
    assert result['name'] == 'whale'
    assert store.has_next_result

    result = store.next_result(11)
    assert result['name'] == 'cat'
    assert store.has_next_result
    result = store.next_result(11)

    assert result['name'] == 'bear'
    assert not store.has_next_result
    assert store.has_prev_result
    result = store.prev_result(11)
    assert store.has_prev_result
    result = store.prev_result(11)

    assert result['name'] == 'whale'
    assert not store.has_prev_result


test_networkxkb()