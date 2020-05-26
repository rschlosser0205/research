from research.rl_memory import Activation_Class, NetworkXKB


class Model_generation:
    def __init__(self, act_decay_rate, act_scale_factor, act_max_steps, act_capped, backlinks, representation):
        self.act_decay_rate = act_decay_rate
        self.act_scale_factor = act_scale_factor
        self.act_max_steps = act_max_steps
        self.act_capped = act_capped
        self.backlinks = backlinks
        self.representation = representation

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