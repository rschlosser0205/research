from itertools import product

from research.rl_memory import ActivationClass, NetworkXKB








def determine_fok_function(method):
    if method == 'cue':
        return cue_fok
    elif method == 'target':
        return target_fok
    elif method == 'cue and target':
        return cue_and_target_fok
    elif method == 'incoming edges':
        return incoming_edges_fok
    elif method == 'outgoing edges':
        return outgoing_edges_fok
    elif method == 'total edges':
        return total_edges_fok
    elif method == 'act by edges':
        return act_by_edges_fok


def cue_fok(store, cue, target, query_time):
    return store.get_activation(cue, (query_time - 0.0001))

def target_fok(store, cue, target, query_time):
    return store.get_activation(target, (query_time - 0.0001))

def cue_and_target_fok(store, cue, target, query_time):
    return 0.5*(store.get_activation(target, (query_time - 0.0001)) + store.get_activation(cue, (query_time - 0.0001)))

def incoming_edges_fok(store, cue, target, query_time):
    return len(store.graph.in_edges(cue))

def outgoing_edges_fok(store, cue, target, query_time):
    return len(store.graph.out_edges(cue))

def total_edges_fok(store, cue, target, query_time):
    return len(store.graph.in_edges(cue)) + len(store.graph.out_edges(cue))

def act_by_edges_fok(store, cue, target, query_time):
    return (len(store.graph.in_edges(cue)) + len(store.graph.out_edges(cue))) * store.get_activation(cue, (query_time - 0.0001))

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




# this function is specific to the AB- task
def set_up_ab(store, backlinks, representation, paradigm, store_time):
    # paradigm is either 'ABAB', 'ABAD', 'ABCB', 'ABCD'
    create_edge(store, store_time, backlinks, representation, 'A', 'B')
    create_edge(store, store_time+1, backlinks, representation, paradigm[2], paradigm[3])


# should take the task, the different paradigms/questions, and the representation
def create_knowledge_list(task, rep, paradigm):
    knowledge_list = []
    if task == 'AB-':
        for i in range(0, 2, 2):
            # determine attributes
            if rep == 'direct':
                attributes = [('goes_to_' + paradigm[i+1].lower(), paradigm[i+1])]
                knowledge_list.append([paradigm[i], attributes])
            elif rep == 'pairs':
                # print(rep)
                attributes = [('first', paradigm[i]), ('second', paradigm[i+1])]
                knowledge_list.append([paradigm[i]+paradigm[i+1], attributes])
            elif rep == 'types':
                attributes = [('first', paradigm[i]), ('second', paradigm[i+1]), ('type', 'pairs')]
                knowledge_list.append([paradigm[i] + paradigm[i + 1], attributes])
    return knowledge_list
    # elif task == 'jeopardy':
        # use dbpedia? or some other thing to generate background knowledge???






def populate(store, link, store_time, task, rep, paradigm):
    knowledge_list = create_knowledge_list(task, rep, paradigm)
    for node in knowledge_list:
        mem_id = node[0]
        attributes = {}
        for (attr, val) in node[1]:
            attributes[attr] = val
        store.store(store_time, link, mem_id, **attributes)
        store_time+=1




# returns a dictionary of query terms and a string that specifies what to ask of the result.
def determine_query_parameters(question):
    if question == 'direct':
        return {'goes_to_b': 'B'}, 'node_id'
    elif question == 'pairs':
        return {'first': 'A'}, 'second'
    elif question == 'types':
        return {'first': 'A'}, 'second'
    elif question == 'jeopardy_q_grid':
        return {'also_called': 'plan_showing_streets', 'num_letters': '4'}, 'name'





def test_model():
    act_decay_rate = [-0.42, -0.41]
    act_scale_factor = [0.5]
    act_max_steps = [2]
    act_capped = [False, True]
    backlinks = [True, False]
    representation = ['pairs', 'types']
    fok_method = ['act by edges']
    paradigms = ['ABAB', 'ABAD', 'ABCB', 'ABCD']
    store_time = 0
    query_time = 2
    tasks = ['AB-']


    generator = product(
        act_decay_rate,
        act_scale_factor,
        act_max_steps,
        act_capped,
        backlinks,
        representation,
        fok_method,
        paradigms,
        tasks
    )
    for rate, scale, step, cap, link, rep, fok_method, paradigm, task in generator:
        print(', '.join([
            # 'decay rate = ' + str(rate),
            # 'scale factor = ' + str(scale),
            # 'max steps = ' + str(step),
            # 'capped = ' + str(cap),
            'backlinks = ' + str(link),
            'representation = ' + rep,
            'paradigm = ' + paradigm,
            'fok_method = ' + fok_method,
            'task = ' + task
        ]))

        store = NetworkXKB(ActivationClass(rate, scale, step, cap))
        populate(store, link, store_time, task, rep, paradigm)

        terms, result_attr = determine_query_parameters(rep)
        result = store.query(query_time, terms)[result_attr]
        print('query first returns: ' + result)

        fok_function = determine_fok_function(fok_method)
        # what does cue mean in a jeopardy scenario?
        #fok = fok_function(store, cue, result, query_time)
        #print('fok = ' + str(fok))




test_model()