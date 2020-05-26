from research.rl_memory import Activation_Class, NetworkXKB


class Model_generation:
    def __init__(self, act_decay_rate, act_scale_factor, act_max_steps, act_capped, backlinks, representation):
        self.act_decay_rate = act_decay_rate
        self.act_scale_factor = act_scale_factor
        self.act_max_steps = act_max_steps
        self.act_capped = act_capped
        self.backlinks = backlinks
        self.representation = representation
        act_class = Activation_Class(act_decay_rate, act_scale_factor, act_max_steps, act_capped)
        store = NetworkXKB(act_class)



    # FIXME add a function that takes in a store and the rep parameters. this function will create the graph
    # where does this function go? in here
    # this function will accomplish store.store(...) * 4 or whatever
    def create_graph(self, store):
        if self.representation == 1:
            # one level (?) representation
            store.store(0, 'A', goes_to='B')
            store.store(0, 'A', goes_to='D')
            store.store(0, 'C', goes_to='B')
            store.store(0, 'C', goes_to='D')
        elif self.representation == 2:
            # two-level representation
            store.store(0, 'AB', first='A', second='B')
            store.store(1, 'AD', first='A', second='D')
            store.store(1, 'CB', first='C', second='B')
            store.store(1, 'CD', first='C', second='D')
        elif self.representation == 3:
            # three levels (type=pairs is a shared child of AB and CD)
            # FIXME add other representations

    def test_model(self):
        # play with the parameters of activation class (decay_rate, scale_factor, max_steps, capped)
        # things to include-- changes in directionality? BACKLINKS VS NONE

        for rate in self.act_decay_rate:
            for scale in self.act_scale_factor:
                for step in self.act_max_steps:
                    for cap in self.act_capped:
                        for link in self.backlinks:
                            for rep in self.representation:
                                store = NetworkXKB(Activation_Class(self.act_decay_rate, self.act_scale_factor, self.act_max_steps, self.act_capped))
                                self.create_graph(store)



        # FIXME add queries and retrievals to get from A to B in all representations
        # FIXME add node id as outgoing edge/attribute


        # get from A to B in rep 1
        store.query(1, {'goes_to': 'B'})

test = Model_generation()