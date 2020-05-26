from research.rl_memory import Activation_Class, NetworkXKB


class Model_generation:
    def __init__(self, act_decay_rate, act_scale_factor, act_max_steps, act_capped, backlinks, representation):
        self.act_decay_rate = act_decay_rate
        self.act_scale_factor = act_scale_factor
        self.act_max_steps = act_max_steps
        self.act_capped = act_capped
        self.backlinks = backlinks
        self.representation = representation



    # comment out the two unused pairs!
    def create_graph(self, store, backlinks, representation):
        if representation == 1:
            # one level (?) representation
            store.store(0, backlinks, 'A', goes_to='B')
            store.store(1, backlinks, 'A', goes_to='D')
            store.store(1, backlinks, 'C', goes_to='B')
            store.store(1, backlinks, 'C', goes_to='D')

        elif representation == 2:
            # two-level representation
            store.store(0, backlinks, 'AB', first='A', second='B')
            store.store(1, backlinks, 'AD', first='A', second='D')
            store.store(1, backlinks, 'CB', first='C', second='B')
            store.store(1, backlinks, 'CD', first='C', second='D')
        elif representation == 3:
            # three levels (type=pairs is a shared child of AB and CD)
            store.store(0, backlinks, 'AB', first='A', second='B', type='pairs')
            store.store(1, backlinks, 'AD', first='A', second='D', type='pairs')
            store.store(1, backlinks, 'CB', first='C', second='B', type='pairs')
            store.store(1, backlinks, 'CD', first='C', second='D', type='pairs')

    # FIXME refactor?
    def query_test(self, representation, store):
        # get from A to B in each representation and then print out the result
        if representation == 1:
            result = store.query(2, {'goes_to': 'B'})
        elif representation == 2:
            result = store.query(2, {'first': 'A'}) # this should give AB or AC
            # FIXME how to get 'second' term?
        elif representation == 3:
            result = store.query(2, {'first': 'A'})  # this should give AB or AC
            # FIXME how to get 'second' term?
        # FIXME make this work so u can print ids
        print(result)

    def test_model(self):
        # play with the parameters of activation class (decay_rate, scale_factor, max_steps, capped)
        # things to include-- BACKLINKS VS NONE
        # loops

        for rate in self.act_decay_rate:
            for scale in self.act_scale_factor:
                for step in self.act_max_steps:
                    for cap in self.act_capped:
                        for link in self.backlinks:
                            for rep in self.representation:
                                print('decay rate = ' + str(rate) + ' scale factor = ' + str(scale) + ' max steps = ' +  str(step) + ' backlinks = ' + str(link) + ' representation = ' + str(rep))
                                store = NetworkXKB(Activation_Class(rate, scale, step, cap))
                                self.create_graph(store, link, rep)






        # FIXME add queries and retrievals to get from A to B in all representations
        # FIXME add node id as outgoing edge/attribute




test = Model_generation([-0.5, -0.25], [0.5, 0.25], [2, 3], [True, False], [True, False], [1, 2, 3])
test.test_model()