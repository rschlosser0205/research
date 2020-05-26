class Model_generation:
    def __init__(self, act_decay_rate, act_scale_factor, act_max_steps, act_capped, backlinks, representation):
        self.act_decay_rate = act_decay_rate
        self.act_scale_factor = act_scale_factor
        self.act_max_steps = act_max_steps
        self.act_capped = act_capped
        self.backlinks = backlinks
        self.representation = representation