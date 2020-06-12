from itertools import product

from research.rl_memory import ActivationClass, NetworkXKB

act_on = False

jeopardy_grid_list = [
            ['plan_showing_streets', [('type', 'object')]],
            ['node_map', [('also_called', 'plan_showing_streets'), ('num_letters', '3'), ('name', 'map')]],
            ['node_street_network', [('also_called', 'plan_showing_streets'), ('num_letters', '14'), ('name', 'street_network')]],
            ['node_bus_routes', [('also_called', 'plan_showing_streets'), ('num_letters', '9'), ('name','bus_routes')]],
            ['node_freeway_system', [('also_called', 'plan_showing_streets'), ('num_letters', '13'), ('name','freeway_system')]],
            ['node_grid', [('also_called','plan_showing_streets'), ('num_letters', '4'), ('name', 'grid')]],
            ['node_road', [('also_called', 'street'), ('num_letters', '4'), ('name', 'road')]],
            ['node_pedestrian', [('also_called', 'walker'), ('num_letters', '10'), ('name', 'pedestrian')]],
            ['node_lane', [('part_of_a', 'road'), ('num_letters', '4'), ('name', 'lane')]],
]
jeopardy_grid_terms = {'also_called': 'plan_showing_streets', 'num_letters': '4'}, 'name'

jeopardy_marapi_list = [
        ['indonesia', [('type', 'country'), ('capital', 'jakarta'), ('official language', 'indonesian'),
                        ('currency', 'indonesian rupiah'), ('driving side', 'left'), ('located in', 'southeast asia'),
                        ('made up of', 'islands'), ('ocean to the west', 'indian ocean'), ('ocean to the east', 'pacific ocean'),
                       ('topography', 'mountains'), ('climate', 'tropical'), ('name', 'Indonesia'), ('colonized by', 'Netherlands')]],
        ['indian ocean', [('type', 'ocean'), ('name', 'Indian Ocean')]],
        ['pacific ocean', [('type', 'ocean'), ('contributes to formation of', 'volcanoes'), ('notable', 'largest ocean'),
                            ('name', 'Pacific Ocean')]],
        ['mountains', [('type', 'landform'), ('comes from', 'volcanoes'), ('name', 'Mountain')]],
        ['volcanoes', [('type', 'leak'), ('comes from', 'tectonic plates'), ('produces', 'heat'), ('expels', 'ash'),
                       ('full of', 'lava'), ('name', 'Volcano'), ('result in', 'mountains'), ('can be called', 'fire mountain')]],
        ['fire', [('type', 'chemical reaction'), ('produces', 'heat'), ('results in', 'ash')]]

]
jeopardy_marapi_terms = {'synonym': 'fire mountain', 'famous example': 'marapi'}

jeopardy_oval_office_list = [
            ['oval_office', [('is_a', 'room'), ('located_in', 'the_white_house'), ('first_word', 'oval'),
             ('second_word', 'office'), ('designed_by', 'nathan_c_wyeth')]],
            ['white_house', [('is_a', 'building'), ('houses', 'president'), ('has', 'room'), ('famous_room', 'oval_office')]],
            ['oval', [('is_a', 'shape'), ('num_sides', '0')]],
            ['square', [('is_a', 'shape'), ('num_sides', '4')]],
            ['circle', [('is_a', 'shape'), ('num_sides', '0')]],
            ['nathan_c_wyeth', [('is_a', 'architect'), ('worked_on', 'the_white_house'), ('born_in', 'illinois')]],
            ['william_taft', [('is_a', 'president'), ('president_number', '27'), ('assumed_office_in', '1909'), ('odered_construction_of', 'oval_office')]],
            ['1909', [('marks_opening_of', 'manhattan_bridge')]],
]

jeopardy_oval_office_terms = {'is_a': 'room', 'designed_by': 'nathan_c_wyeth', 'located_in': 'the_white_house'}


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

# terms is {attribute : node}, like {first : A}
def cue_fok(store, terms, result, query_time):
    fok = 0
    for cue in terms.values():
        fok += store.get_activation(cue, (query_time - 0.0001))
    return fok

def target_fok(store, terms, result, query_time):
    return store.get_activation(result, (query_time - 0.0001))

def cue_and_target_fok(store, terms, result, query_time):
    fok = 0
    for cue in terms.values():
        fok += store.get_activation(cue, (query_time - 0.0001))
    return fok + store.get_activation(result, (query_time - 0.0001))

def incoming_edges_fok(store, terms, result, query_time):
    fok = 0
    for cue in terms.values():
        fok += len(store.graph.in_edges(cue))
    return fok

def outgoing_edges_fok(store, terms, result, query_time):
    fok = 0
    for cue in terms.values():
        fok += len(store.graph.out_edges(cue))
    return fok

def total_edges_fok(store, terms, result, query_time):
    fok = 0
    for cue in terms.values():
        fok += len(store.graph.in_edges(cue)) + len(store.graph.out_edges(cue))
    return fok

def act_by_edges_fok(store, terms, result, query_time):
    fok = 0
    for cue in terms.values():
        fok += (len(store.graph.in_edges(cue)) + len(store.graph.out_edges(cue))) * store.get_activation(cue, (query_time - 0.0001))
    return fok

# this function is specific to the AB- Task
def create_edge(store, time, backlinks, representation, src, dst):
    # src and dst would be either 'A', 'B', 'C', 'D'
    if representation == 'direct':
        store.store(time, backlinks, True, src, **{'goes_to_' + dst.lower(): dst, })
    elif representation == 'pairs':
        # two-level representation
        store.store(time, backlinks, True, src + dst, first=src, second=dst)
    elif representation == 'types':
        # three levels (type=pairs is a shared child of AB and CD)
        store.store(time, backlinks, True, src + dst, first=src, second=dst, type='pairs')




# should take the task, the different paradigms, and the representation
def create_knowledge_list(task, rep=None, paradigm=None):
    knowledge_list = []
    if task == 'AB-':
        for i in range(0, 4, 2):
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
    elif task == 'jeopardy_q_grid':
        # this background knowledge is specific to the grid question
        knowledge_list = jeopardy_grid_list

    return knowledge_list





def populate(store, link, store_time, act_on, task, rep=None, paradigm=None):
    knowledge_list = create_knowledge_list(task, rep, paradigm)
    for node in knowledge_list:
        mem_id = node[0]
        attributes = {}
        for (attr, val) in node[1]:
            attributes[attr] = val
        store.store(store_time, link, act_on, mem_id, **attributes)
        store_time+=1
    return store_time



# returns a dictionary of query terms and a string that specifies what to ask of the result.
def determine_query_parameters(question):
    if question == 'direct':
        return {'goes_to_b': 'B'}, 'node_id'
    elif question == 'pairs':
        return {'first': 'A'}, 'second'
    elif question == 'types':
        return {'first': 'A'}, 'second'
    elif question == 'jeopardy_q_grid':
        return jeopardy_grid_terms





# I'm sorry. I'm so so sorry
def test_model():
    act_decay_rate = [-0.42, -0.41]
    act_scale_factor = [0.5]
    act_max_steps = [2]
    act_capped = [False, True]
    backlinks = [True, False]
    fok_method = ['act by edges']
    store_time = 0
    tasks = ['AB-', 'jeopardy_q_grid']
    representation = ['direct', 'pairs', 'types']
    paradigm = ['ABAB', 'ABAD', 'ABCB', 'ABCD']

    generator = product(
        act_decay_rate,
        act_scale_factor,
        act_max_steps,
        act_capped,
        backlinks,
        fok_method,
        tasks
    )

    ab_combos = product(representation, paradigm)

    for rate, scale, step, cap, link, fok_method, task in generator:
        print(', '.join([
            # 'decay rate = ' + str(rate),
            'scale factor = ' + str(scale),
            # 'max steps = ' + str(step),
            # 'capped = ' + str(cap),
            'backlinks = ' + str(link),
            'fok_method = ' + fok_method,
            'task = ' + task
        ]))
        store = NetworkXKB(ActivationClass(rate, scale, step, cap))
        if task == 'AB-':
            for rep, para in ab_combos:
                store = NetworkXKB(ActivationClass(rate, scale, step, cap))
                query_time = 1 + populate(store, link, store_time, act_on, task, rep, para)

                terms, result_attr = determine_query_parameters(rep)
                result = store.query(query_time, terms)[result_attr]
                print('query first returns: ' + result)

                fok_function = determine_fok_function(fok_method)
                # what does cue mean in a jeopardy scenario? -- use both/all
                fok = fok_function(store, terms, result, query_time)
                print('fok = ' + str(fok))

        else:
            store = NetworkXKB(ActivationClass(rate, scale, step, cap))
            query_time = 1 + populate(store, link, store_time, act_on, task)

            # use task bc jeopardy question
            terms, result_attr = determine_query_parameters(task)
            result = store.query(query_time, terms)[result_attr]
            print('query first returns: ' + result)

            fok_function = determine_fok_function(fok_method)
            fok = fok_function(store, terms, result, query_time)
            print('fok = ' + str(fok))




test_model()