from itertools import product
from collections import namedtuple
from research.rl_memory import ActivationClass, NetworkXKB

Task = namedtuple('Task', 'knowledge_list, retrieval_steps, activate_on_store')
Knowledge = namedtuple('Knowledge', 'node_id, attributes')
RetrievalStep = namedtuple('RetrievalStep', 'action, query_terms, constraints, result_attr')
volcano_knowledge_list = Knowledge('indonesia', {
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
            }),
Knowledge('indian ocean', {'type': 'ocean', 'name': 'Indian Ocean'}),
Knowledge(
    'pacific ocean', {
        'type': 'ocean',
        'contributes to formation of': 'volcanoes',
        'notable': 'largest ocean',
        'name': 'Pacific Ocean',
    },
),
Knowledge('mountain', {'type': 'landform', 'comes from': 'volcano', 'name': 'Mountain'}),
Knowledge('hill', {'type': 'landform', 'similar to': 'mountain', 'smaller than': 'mountain', 'name': 'Hill', 'covered_in': 'grass'})
Knowledge(
    'volcano', {
        'type': 'leak',
        'comes from': 'tectonic plates',
        'produces': 'heat',
        'expels': 'ash',
        'full of': 'lava',
        'name': 'Volcano',
        'similar to': 'mountain',
        'can be called': 'fire mountain',
        'famous example from antiquity': 'mt vesuvius',
        'famous example from modernity': 'krakatoa',
        'related to': 'fire',
    },
),
Knowledge('lava', {'type': 'molten rock', 'located in': 'volcano', 'gives off': 'heat', 'related to': 'fire', 'inside': 'mountain', 'name': 'Lava'},),
Knowledge('krakatoa', {'type': 'volcano', 'located in': 'indonesia', 'last eruption': '2020', 'is a': 'mountain', 'name': 'Krakatoa'}),
Knowledge('fire', {'consumes': 'grass', 'type': 'chemical reaction', 'related to': 'heat', 'results in': 'ash', 'name': 'Fire'}),
Knowledge('jakarta', {'type': 'city', 'capital of': 'indonesia', 'located in': 'indonesia', 'population': '9.6 million', 'name': 'Jakarta'}),
Knowledge('yamin', {'type': 'mountain', 'located in': 'indonesia', 'height': '4540 m', 'name': 'Yamin'}),
Knowledge('pangrango', {'type': 'volcano', 'located in': 'indonesia', 'status': 'dormant', 'name': 'Pangrango', 'is a': 'mountain'}),
Knowledge('tujuh', {'type': 'volcano', 'located in': 'indonesia', 'is a': 'mountain', 'name': 'Tujuh'}),
Knowledge('kelimutu', {'type': 'volcano', 'located in': 'indonesia', 'name': 'Kelimutu', 'last eruption': '1968', 'is a': 'mountain'}),
Knowledge('kapalatmada', {'type': 'mountain', 'located in': 'indonesia', 'name': 'Kapalatmada', 'height': '2428m'}),
Knowledge('sentani', {'type': 'lake', 'located in': 'indonesia', 'name': 'Lake Sentani'}),
Knowledge('toba', {'type': 'lake', 'located in': 'indonesia', 'name': 'Lake Toba'}),
Knowledge('danau batur', {'type': 'lake', 'located in': 'indonesia', 'name': 'Danau Batur', 'formed by': 'volcano'}),
Knowledge('linow', {'type': 'lake', 'located in': 'indonesia', 'name': 'Lake Linow', 'formed by': 'volcano'}),
Knowledge('citarum', {'type': 'river', 'located in': 'indonesia', 'name': 'Citarum', 'flows to': 'java sea'}),
Knowledge('mahakam', {'type': 'river', 'located in': 'indonesia', 'name': 'Mahakam', 'flows to': 'makassar strait'}),
Knowledge('java', {'type': 'island', 'located in': 'indonesia', 'name': 'Java'}),
Knowledge('sumatra', {'type': 'island', 'located in': 'indonesia', 'name': 'Sumatra'}),

TASKS = {
    'jeopardy_grid': Task(
        knowledge_list=[
            Knowledge('plan_showing_streets', {'type': 'object'}),
            Knowledge('node_map', {'also_called': 'plan_showing_streets', 'num_letters': '3', 'name': 'map'}),
            Knowledge('node_street_network', {'also_called': 'plan_showing_streets', 'num_letters': '14', 'name': 'street_network'}),
            Knowledge('node_bus_routes', {'also_called': 'plan_showing_streets', 'num_letters': '9', 'name': 'bus_routes'}),
            Knowledge('node_freeway_system', {'also_called': 'plan_showing_streets', 'num_letters': '13', 'name': 'freeway_system'}),
            Knowledge('node_grid', {'also_called': 'plan_showing_streets', 'num_letters': '4', 'name': 'grid'}),
            Knowledge('node_road', {'also_called': 'street', 'num_letters': '4', 'name': 'road'}),
            Knowledge('node_pedestrian', {'also_called': 'walker', 'num_letters': '10', 'name': 'pedestrian'}),
            Knowledge('node_lane', {'part_of_a': 'road', 'num_letters': '4', 'name': 'lane'}),
        ],
        retrieval_steps=[
            RetrievalStep('query', {'also_called': 'plan_showing_streets'}, {'num_letters': '4'}, 'name'),
        ],
        activate_on_store=False,
    ),
    'jeopardy_volcano_to_marapi': Task(
        knowledge_list= volcano_knowledge_list,
        retrieval_steps=[
            RetrievalStep('query', {'famous example': 'marapi'}, {}, 'name'),

        ],
        activate_on_store=False,
    ),
    'jeopardy_volcano_fire': Task(
            knowledge_list= volcano_knowledge_list,
            retrieval_steps=[
                RetrievalStep('query', {'related to': 'fire'}, {'inside': 'mountain'}, 'node_id'), # gives lava
                RetrievalStep('retrieve', {}, {}, 'located in'), # returns volcano
            ],
            activate_on_store=False,
        ),
    'jeopardy_volcano_indonesia_mountain': Task(
            knowledge_list= volcano_knowledge_list,
            retrieval_steps=[
                RetrievalStep('query', {'located in': 'indonesia'}, {'is a': 'mountain'}, 'node_id'),
                RetrievalStep('retrieve', {}, {}, 'type'), # returns volcano
            ],
            activate_on_store=False,
        ),
    'jeopardy_volcano_mountain': Task(
            knowledge_list= volcano_knowledge_list,
            retrieval_steps=[
                # free associate on mountain
                RetrievalStep('query', {'similar to': 'mountain'}, {'related to': 'fire'}, 'name'),
                # free associate on fire
            ],
            activate_on_store=False,
        ),
    # 'jeopardy_marapi_to_volcano': Task(
    #             knowledge_list= volcano_knowledge_list,
    #             retrieval_steps=[
    #                 RetrievalStep('query', {'famous example': 'marapi'}, {}, 'name'),
    #
    #             ],
    #             activate_on_store=False,
    #         ),
    'jeopardy_oval_office': Task(
            knowledge_list=[
            Knowledge('oval_office', {'is_a': 'room', 'located_in': 'the_white_house', 'first_word': 'oval', 'second_word': 'office', 'designed_by': 'nathan_c_wyeth', 'name': 'Oval Office'}),
            Knowledge('white_house', {'is_a': 'building', 'houses': 'president', 'has': 'room', 'famous_room': 'oval_office'}),
            Knowledge('oval', {'is_a': 'shape', 'num_sides': '0'}),
            Knowledge('square', {'is_a': 'shape', 'num_sides': '4'}),
            Knowledge('circle', {'is_a': 'shape', 'num_sides': '0'}),
            Knowledge('nathan_c_wyeth', {'is_a': 'architect', 'worked_on': 'the_white_house', 'born_in': 'illinois'}),
            Knowledge('william_taft', {'is_a': 'president', 'president_number': '27', 'assumed_office_in': '1909', 'ordered_construction_of': 'oval_office'}),
            Knowledge('1909', {'marks_opening_of': 'manhattan_bridge'}),
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
                knowledge_list.append(Knowledge(paradigm[i], attributes))
            elif representation == 'pairs':
                # print(representation)
                attributes = {'first': paradigm[i], 'second': paradigm[i + 1]}
                knowledge_list.append(Knowledge(paradigm[i] + paradigm[i + 1], attributes))
            elif representation == 'types':
                attributes = {'first': paradigm[i], 'second': paradigm[i + 1], 'type': 'pairs'}
                knowledge_list.append(Knowledge(paradigm[i] + paradigm[i + 1], attributes))

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
    elif method == 'avg activation of everything':
        return avg_activation_of_everything
    elif method == 'results looked through':
        return results_looked_through_fok
    elif method == 'step num':
        return step_num_fok



# terms is {attribute : node}, like {first : A}
def cue_fok(store, terms, result, query_time, results_looked_through, step_num):
    # if the cue node is in the graph, proceed. (for the marapi cue this returns 0)
    return sum(
        store.get_activation(cue, (query_time - 0.0001))
        for cue in terms.values() if store.graph.has_node(cue)
    )


def target_fok(store, terms, result, query_time, results_looked_through, step_num):
    if result is None:
        return 0
    return store.get_activation(result, (query_time - 0.0001))


def cue_and_target_fok(store, terms, result, query_time, results_looked_through, step_num):
    if result is None:
        return 0
    total = sum(store.get_activation(cue, (query_time - 0.0001)) for cue in terms.values())
    return total + store.get_activation(result, (query_time - 0.0001))


def incoming_edges_fok(store, terms, result, query_time, results_looked_through, step_num):
    return sum(len(store.graph.in_edges(cue)) for cue in terms.values())


def outgoing_edges_fok(store, terms, result, query_time, results_looked_through, step_num):
    return sum(len(store.graph.out_edges(cue)) for cue in terms.values())


def total_edges_fok(store, terms, result, query_time, results_looked_through, step_num):
    return sum(
        len(store.graph.in_edges(cue)) + len(store.graph.out_edges(cue))
        for cue in terms.values()
    )


def act_by_edges_fok(store, terms, result, query_time, results_looked_through, step_num):
    return sum(
        (
            (len(store.graph.in_edges(cue)) + len(store.graph.out_edges(cue)))
            * store.get_activation(cue, (query_time - 0.0001))
        )
        for cue in terms.values() if store.graph.has_node(cue)
    )


def avg_activation_of_everything(store, terms, result, query_time, results_looked_through, step_num):
    all_nodes = list(store.graph.nodes)
    return sum(
        store.get_activation(node, (query_time - 0.0001))
        for node in all_nodes
    ) / len(all_nodes)

def results_looked_through_fok(store, terms, result, query_time, results_looked_through, step_num):
    if results_looked_through != 0:
        return 1/results_looked_through
    return 0

def step_num_fok(store, terms, result, query_time, results_looked_through, step_num):
    if step_num != 0:
        return 1/step_num
    return 0



def populate(store, link, store_time, activate_on_store, knowledge_list):
    for knowledge in knowledge_list:
        store.store(store_time, link, activate_on_store, knowledge.node_id, **knowledge.attributes)
        store_time += 1
    return store_time


def test_model():
    links_so_far = 0
    queries_so_far = 0
    act_decay_rate = [-0.42, -0.41]
    act_scale_factor = [0.5, 0.6]
    act_max_steps = [1, 2, 3]
    act_capped = [False, True]
    backlinks = [False, True]
    fok_method = [
        'incoming edges', 'act by edges', 'total edges', 'cue and target', 'cue', 'target',
        'outgoing edges', 'avg activation of everything', 'results looked through', 'step num'
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

        prev_result = None

        # loop through the retrieval steps
        for step_num, step in enumerate(task.retrieval_steps, start=1):

            # take the retrieval step
            if step.action == 'query':
                result = store.query(time, step.query_terms)
            elif step.action == 'retrieve':
                result = store.retrieve(time, prev_result)
            else:
                print('invalid action: ' + step.action)
                return

            failed = result is None
            results_looked_through = 1

            while not failed:
                # calculate fok
                fok = fok_function(store, step.query_terms, result['node_id'], time, results_looked_through, step_num)
                print('step ' + str(step_num) + ' fok = ' + str(fok))
                if all(result[attr] == val for attr, val in step.constraints.items()):
                    # if the constraints are met, move on to the next step
                    prev_result = result[step.result_attr]
                    break
                elif store.has_next_result:
                    results_looked_through += 1
                    # if there is a next result, move on to the next result
                    result = store.next_result(time)
                else:
                    # otherwise, we've hit a dead end
                    print('this is a dead end')
                    failed = True

            if failed:
                break


test_model()
