from research.rl_memory import NetworkXKB

def test_networkxkb():
    """Test the NetworkX KnowledgeStore."""

    def activation_fn(graph, mem_id):
        graph.nodes[mem_id]['activation'] += 1

    store = NetworkXKB(activation_fn=activation_fn)
    store.store('cat', is_a='mammal', has='fur', name='cat')
    store.store('bear', is_a='mammal', has='fur', name='bear')
    store.store('whale', is_a='mammal', lives_in='water')
    store.store('whale', name='whale') # this activates whale
    store.store('fish', is_a='animal', lives_in='water')
    store.store('mammal', has='vertebra', is_a='animal')
    # retrieval
    result = store.retrieve('whale')
    assert sorted(result.items()) == [('is_a', 'mammal'), ('lives_in', 'water'), ('name', 'whale')]
    # failed query
    result = store.query({'has': 'vertebra', 'lives_in': 'water'})
    assert result is None
    # unique query
    result = store.query({'has': 'vertebra'})
    assert sorted(result.items()) == [('has', 'vertebra'), ('is_a', 'animal')]
    # query traversal
    store.store('cat')
    # at this point, whale has been activated twice (from the store and the retrieve)
    # while cat has been activated once (from the store)
    # so a search for mammals will give, in order: whale, cat, bear
    result = store.query({'is_a': 'mammal'})
    assert result['name'] == 'whale'
    assert store.has_next_result
    result = store.next_result()
    assert result['name'] == 'cat'
    assert store.has_next_result
    result = store.next_result()
    assert result['name'] == 'bear'
    assert not store.has_next_result
    assert store.has_prev_result
    result = store.prev_result()
    assert store.has_prev_result
    result = store.prev_result()
    assert result['name'] == 'whale'
    assert not store.has_prev_result


test_networkxkb()