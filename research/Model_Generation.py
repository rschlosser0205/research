from itertools import product
from collections import namedtuple
from research.rl_memory import ActivationClass, NetworkXKB

Task = namedtuple('Task', 'knowledge_list, retrieval_steps, activate_on_store')
RetrievalStep = namedtuple('RetrievalStep', 'action, query_terms, constraints, result_attr')

TASKS = {
    'jeopardy_grid': Task(
        knowledge_list=[
            ['plan_showing_streets', {'type': 'object'}],
            ['node_map', {'also_called': 'plan_showing_streets', 'num_letters': '3', 'name': 'map'}],
            ['node_street_network', {'also_called': 'plan_showing_streets', 'num_letters': '14', 'name': 'street_network'}],
            ['node_bus_routes', {'also_called': 'plan_showing_streets', 'num_letters': '9', 'name': 'bus_routes'}],
            ['node_freeway_system', {'also_called': 'plan_showing_streets', 'num_letters': '13', 'name': 'freeway_system'}],
            ['node_grid', {'also_called': 'plan_showing_streets', 'num_letters': '4', 'name': 'grid'}],
            ['node_road', {'also_called': 'street', 'num_letters': '4', 'name': 'road'}],
            ['node_pedestrian', {'also_called': 'walker', 'num_letters': '10', 'name': 'pedestrian'}],
            ['node_lane', {'part_of_a': 'road', 'num_letters': '4', 'name': 'lane'}],
        ],
        retrieval_steps=[
            RetrievalStep('query', {'also_called': 'plan_showing_streets'}, {'num_letters': '4'}, 'name'),
        ],
        activate_on_store=False,
    ),
    'jeopardy_marapi': Task(
        knowledge_list=[
            ['indonesia', {
                    'type': 'country',
                    'capital': 'jakarta',
                    'official language': 'indonesian',
                    'currency': 'indonesian rupiah',
                    'driving side': 'left',
                    'located in': 'southeast asia',
                    'made up of': 'islands',
                    'ocean to the west': 'indian ocean',
                    'ocean to the east': 'pacific ocean',
                    'topography': 'mountains',
                    'climate': 'tropical',
                    'name': 'Indonesia',
                    'colonized by': 'Netherlands',
            }],
            ['indian ocean', {'type': 'ocean', 'name': 'Indian Ocean'}],
            [
                'pacific ocean', {
                    'type': 'ocean',
                    'contributes to formation of': 'volcanoes',
                    'notable': 'largest ocean',
                    'name': 'Pacific Ocean',
                },
            ],
            ['mountain', {'type': 'landform', 'comes from': 'volcano', 'name': 'Mountain'}],
            [
                'volcano', {
                    'type': 'leak',
                    'comes from': 'tectonic plates',
                    'produces': 'heat',
                    'expels': 'ash',
                    'full of': 'lava',
                    'name': 'Volcano',
                    'is a': 'mountain',
                    'can be called': 'fire mountain',
                    'famous example from antiquity': 'mt vesuvius',
                    'famous example from modernity': 'krakatoa',
                    'related to': 'fire',
                },
            ],
            ['lava', {'type': 'molten rock', 'located in': 'volcano', 'gives off': 'heat', 'related to': 'fire', 'inside': 'mountain', 'name': 'Lava'},],
            ['krakatoa', {'type': 'volcano', 'located in': 'indonesia', 'last eruption': '2020', 'is a': 'mountain', 'name': 'Krakatoa'}],
            ['fire', {'type': 'chemical reaction', 'related to': 'heat', 'results in': 'ash', 'name': 'Fire'}],
            ['jakarta', {'type': 'city', 'capital of': 'indonesia', 'located in': 'indonesia', 'population': '9.6 million', 'name': 'Jakarta'}],
            ['yamin', {'type': 'mountain', 'located in': 'indonesia', 'height': '4540 m', 'name': 'Yamin'}],
            ['pangrango', {'type': 'volcano', 'located in': 'indonesia', 'status': 'dormant', 'name': 'Pangrango', 'is a': 'mountain'}],
            ['tujuh', {'type': 'volcano', 'located in': 'indonesia', 'is a': 'mountain', 'name': 'Tujuh'}],
            ['kelimutu', {'type': 'volcano', 'located in': 'indonesia', 'name': 'Kelimutu', 'last eruption': '1968', 'is a': 'mountain'}],
            ['kapalatmada', {'type': 'mountain', 'located in': 'indonesia', 'name': 'Kapalatmada', 'height': '2428m'}],
            ['sentani', {'type': 'lake', 'located in': 'indonesia', 'name': 'Lake Sentani'}],
            ['toba', {'type': 'lake', 'located in': 'indonesia', 'name': 'Lake Toba'}],
            ['danau batur', {'type': 'lake', 'located in': 'indonesia', 'name': 'Danau Batur', 'formed by': 'volcano'}],
            ['linow', {'type': 'lake', 'located in': 'indonesia', 'name': 'Lake Linow', 'formed by': 'volcano'}],
            ['citarum', {'type': 'river', 'located in': 'indonesia', 'name': 'Citarum', 'flows to': 'java sea'}],
            ['mahakam', {'type': 'river', 'located in': 'indonesia', 'name': 'Mahakam', 'flows to': 'makassar strait'}],
            ['java', {'type': 'island', 'located in': 'indonesia', 'name': 'Java'}],
            ['sumatra', {'type': 'island', 'located in': 'indonesia', 'name': 'Sumatra'}],
        ],
        retrieval_steps=[
            RetrievalStep('query', {'famous example': 'marapi'}, {}, 'name'),
            RetrievalStep('query', {'located in': 'indonesia'}, {'is a': 'mountain'}, 'name'),
            # free associate on mountain
            RetrievalStep('query', {'is a': 'mountain'}, {'related to': 'fire'}, 'name'),
            # free associate on fire
            RetrievalStep('query', {'related to': 'fire'}, {'inside': 'mountain'}, 'located in'),
        ],
        activate_on_store=False,
    ),
    'jeopardy_oval_office': Task(
        knowledge_list=[
            ['oval_office', {'is_a': 'room', 'located_in': 'the_white_house', 'first_word': 'oval', 'second_word': 'office', 'designed_by': 'nathan_c_wyeth', 'name': 'Oval Office'}],
            ['white_house', {'is_a': 'building', 'houses': 'president', 'has': 'room', 'famous_room': 'oval_office'}],
            ['oval', {'is_a': 'shape', 'num_sides': '0'}],
            ['square', {'is_a': 'shape', 'num_sides': '4'}],
            ['circle', {'is_a': 'shape', 'num_sides': '0'}],
            ['nathan_c_wyeth', {'is_a': 'architect', 'worked_on': 'the_white_house', 'born_in': 'illinois'}],
            ['william_taft', {'is_a': 'president', 'president_number': '27', 'assumed_office_in': '1909', 'ordered_construction_of': 'oval_office'}],
            ['1909', {'marks_opening_of': 'manhattan_bridge'}],
        ],
        retrieval_steps=[
            RetrievalStep('query', {'is_a': 'room'}, {'designed_by': 'nathan_c_wyeth', 'located_in': 'the_white_house'}, 'name'),
        ],
        activate_on_store=False,
    ),
}


def create_paired_recall_tasks():
    generator = product(
        ['ABAB', 'ABAD', 'ABCB', 'ABCD'],
        ['direct', 'pairs', 'types'],
    )
    for paradigm, representation in generator:
        variable_name = paradigm + '_' + representation

        knowledge_list = []
        for i in range(0, 4, 2):
            # determine attributes
            if representation == 'direct':
                attributes = {'goes_to_' + paradigm[i + 1].lower(): paradigm[i + 1]}
                knowledge_list.append([paradigm[i], attributes])
            elif representation == 'pairs':
                # print(representation)
                attributes = {'first': paradigm[i], 'second': paradigm[i + 1]}
                knowledge_list.append([paradigm[i] + paradigm[i + 1], attributes])
            elif representation == 'types':
                attributes = {'first': paradigm[i], 'second': paradigm[i + 1], 'type': 'pairs'}
                knowledge_list.append([paradigm[i] + paradigm[i + 1], attributes])

        if representation == 'direct':
            retrieval_steps = [
                RetrievalStep('query', {'goes_to_b': 'B'}, {}, 'node_id'),
            ]
        elif representation == 'pairs':
            retrieval_steps = [
                RetrievalStep('query', {'first': 'A'}, {}, 'second'),
            ]
        elif representation == 'types':
            retrieval_steps = [
                RetrievalStep('query', {'first': 'A'}, {}, 'second'),
            ]

        globals()['TASKS'][variable_name] = Task(
            knowledge_list=knowledge_list,
            retrieval_steps=retrieval_steps,
            activate_on_store=True,
        )


create_paired_recall_tasks()


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
    elif method == 'avg_activation_of_everything':
        return avg_activation_of_everything


# terms is {attribute : node}, like {first : A}
def cue_fok(store, terms, result, query_time):
    # if the cue node is in the graph, proceed. (for the marapi cue this returns 0)
    return sum(
        store.get_activation(cue, (query_time - 0.0001))
        for cue in terms.values() if store.graph.has_node(cue)
    )


def target_fok(store, terms, result, query_time):
    if result is None:
        return 0
    return store.get_activation(result, (query_time - 0.0001))


def cue_and_target_fok(store, terms, result, query_time):
    if result is None:
        return 0
    total = sum(store.get_activation(cue, (query_time - 0.0001)) for cue in terms.values())
    return total + store.get_activation(result, (query_time - 0.0001))


def incoming_edges_fok(store, terms, result, query_time):
    return sum(len(store.graph.in_edges(cue)) for cue in terms.values())


def outgoing_edges_fok(store, terms, result, query_time):
    return sum(len(store.graph.out_edges(cue)) for cue in terms.values())


def total_edges_fok(store, terms, result, query_time):
    return sum(
        len(store.graph.in_edges(cue)) + len(store.graph.out_edges(cue))
        for cue in terms.values()
    )


def act_by_edges_fok(store, terms, result, query_time):
    return sum(
        (
            (len(store.graph.in_edges(cue)) + len(store.graph.out_edges(cue)))
            * store.get_activation(cue, (query_time - 0.0001))
        )
        for cue in terms.values() if store.graph.has_node(cue)
    )


def avg_activation_of_everything(store, terms, result, query_time):
    all_nodes = list(store.graph.nodes)
    return sum(
        store.get_activation(node, (query_time - 0.0001))
        for node in all_nodes
    ) / len(all_nodes)


def populate(store, link, store_time, activate_on_store, knowledge_list):
    for node in knowledge_list:
        mem_id = node[0]
        attributes = {}
        for (attr, val) in node[1]:
            attributes[attr] = val
        store.store(store_time, link, activate_on_store, mem_id, **attributes)
        store_time += 1
    return store_time


def test_model():
    act_decay_rate = [-0.42, -0.41]
    act_scale_factor = [0.5, 0.6]
    act_max_steps = [1, 2, 3]
    act_capped = [False, True]
    backlinks = [False, True]
    fok_method = [
        'incoming edges', 'act by edges', 'total edges', 'cue and target', 'cue', 'target',
        'outgoing edges', 'avg_activation_of_everything'
    ]
    #'act by edges', 'total edges', 'cue and target', 'cue', 'target', , 'outgoing edges', avg_activation_of_everything
    store_time = 0
    task_names = list(TASKS.keys())

    generator = product(
        act_decay_rate,
        act_scale_factor,
        act_max_steps,
        act_capped,
        backlinks,
        fok_method,
        task_names,
    )

    for rate, scale, step, cap, backlink, fok_method, task_name in generator:
        task = TASKS[task_name]
        print(', '.join([
            # 'decay rate = ' + str(rate),
            'scale factor = ' + str(scale),
            'max steps = ' + str(step),
            'capped = ' + str(cap),
            'backlinks = ' + str(backlink),
            'fok_method = ' + fok_method,
            'task = ' + str(task)
        ]))
        store = NetworkXKB(ActivationClass(rate, scale, step, cap))
        time = 1 + populate(store, backlink, store_time, task.activate_on_store, task.knowledge_list)
        fok_function = determine_fok_function(fok_method)

        # loop through retrieval step options
        for step in task.retrieval_steps:
            result = store.query(query_time, step.query_terms)

            while result is not None:
                # calculate fok
                fok = fok_function(store, step.query_terms, result, query_time)
                print('fok = ' + str(fok))
                # if the result doesn't fit the constraints, move on
                if not all(result[attr] == val for attr, val in step.constraints.items()):
                    result = store.next_result()
                    continue
                if result is not None:
                    print(result[step.result_attr])
                    break


test_model()
