from research.rl_memory import NetworkXKB
def test_networkxkb():
    """Test the NetworkX KnowledgeStore."""

    def activation_fn(graph, mem_id):
            # append to existing activation list
            graph.nodes[mem_id]['activation'].append(1)

    def activation_fn_time(graph, mem_id, time_stamp):
        #appends time stamp
        graph.nodes[mem_id]['activation'].append(time_stamp)







    store = NetworkXKB(activation_fn=activation_fn_time)
    store.store(0, 'cat', is_a='mammal', has='fur', name='cat')
    store.store(1, 'bear', is_a='mammal', has='fur', name='bear')
    store.store(2, 'whale', is_a='mammal', lives_in='water')
    store.store(3, 'whale', name='whale') # this activates whale
    store.store(4, 'fish', is_a='animal', lives_in='water')
    store.store(5, 'mammal', has='vertebra', is_a='animal')
    # retrieval
    result = store.retrieve(6, 'whale')
    assert sorted(result.items()) == [('is_a', 'mammal'), ('lives_in', 'water'), ('name', 'whale')]
    # failed query
    result = store.query(7, {'has': 'vertebra', 'lives_in': 'water'})
    assert result is None
    # unique query
    result = store.query(8, {'has': 'vertebra'})

    assert sorted(result.items()) == [('has', 'vertebra'), ('is_a', 'animal')]
    # query traversal
    store.store(9, 'cat')
    # at this point, whale has been activated twice (from the store and the retrieve)
    # prints whale activation list
    print(store.get_activation('cat', 11))
    # while cat has been activated once (from the store)
    # so a search for mammals will give, in order: whale, cat, bear
    result = store.query(11, {'is_a': 'mammal'})
    print(result['name'])
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