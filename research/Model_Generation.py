import math
from itertools import product
from collections import namedtuple

from research.rl_memory import ActivationClass, NetworkXKB
from statistics import mean

# doing_query = True
Task = namedtuple('Task', 'knowledge_list, retrieval_steps, question_concepts, activate_on_store')
Knowledge = namedtuple('Knowledge', 'node_id, attributes')
RetrievalStep = namedtuple('RetrievalStep', 'action, query_terms, constraints, result_attr')
volcano_knowledge_list = [Knowledge('indonesia', {
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
                    'colonized by': 'the netherlands',
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
        Knowledge('hill', {'type': 'landform', 'similar to': 'mountain', 'smaller than': 'mountain', 'name': 'Hill', 'covered_in': 'grass'}),
        Knowledge(
            'volcano', {
                'type': 'leak',
                'comes from': 'tectonic plates',
                'produces': 'heat',
                'expels': 'lava',
                'full of': 'magma',
                'name': 'Volcano',
                'similar to': 'mountain',
                'can be called': 'fire mountain',
                'example': 'krakatoa'
            },
        ),
        Knowledge('lava', {'type': 'molten rock', 'expelled from': 'volcano', 'gives off': 'heat', 'related to': 'fire', 'formerly': 'magma', 'name': 'Lava', 'associated with': 'volcano'}),
        Knowledge('magma', {'type': 'molten rock', 'inside': 'volcano', 'gives off': 'heat', 'related to': 'fire', 'name': 'Magma', 'associated with': 'volcano'}),
        Knowledge('krakatoa', {'type': 'volcano', 'located in': 'indonesia', 'last eruption': '2020', 'is a': 'mountain', 'name': 'Krakatoa', 'setting for': '21 balloons'}),
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
        Knowledge('the netherlands', {'type': 'nation', 'located in': 'europe', 'name': 'The Netherlands', 'official language': 'dutch'}),
        Knowledge('21 balloons', {'type': 'novel', 'written by': 'william pene du bois', 'title': 'The 21 Balloons', 'setting': 'krakatoa'}),
    ]
TASKS = {
    'j_grid': Task(
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
        question_concepts=['city', '4', 'plan_showing_streets'],
        activate_on_store=False
    ),

    'j_volcano_to_marapi': Task(
        knowledge_list=volcano_knowledge_list,
        retrieval_steps=[
            RetrievalStep('query', {'famous example': 'marapi'}, {}, 'name'),

        ],
        question_concepts=['indonesia', 'marapi', 'fire mountain', 'fire', 'mountain'],
        activate_on_store=False
    ),
    'j_volcano_fire': Task(
            knowledge_list=volcano_knowledge_list,
            retrieval_steps=[
                RetrievalStep('query', {'related to': 'fire'}, {}, 'associated with')
            ],
            question_concepts=['indonesia', 'marapi', 'fire mountain', 'fire', 'mountain'],
            activate_on_store=False
        ),
    'j_indonesia_mountain': Task(
            knowledge_list= volcano_knowledge_list,
            retrieval_steps=[
                RetrievalStep('query', {'located in': 'indonesia'}, {'is a': 'mountain'}, 'type') # returns volcano
            ],
            question_concepts=['indonesia', 'marapi', 'fire mountain', 'fire', 'mountain'],
            activate_on_store=False
        ),
    'j_volcano_mountain': Task(
            knowledge_list= volcano_knowledge_list,
            retrieval_steps=[
                # free associate on mountain (may return hill)
                RetrievalStep('query', {'similar to': 'mountain'}, {}, 'name'),
            ],
            question_concepts=['indonesia', 'marapi', 'fire mountain', 'fire', 'mountain'],
            activate_on_store=False
        ),
    'j_marapi_to_volcano': Task(
                knowledge_list= volcano_knowledge_list,
                retrieval_steps=[
                    RetrievalStep('query', {'name': 'Marapi'}, {}, 'is a'),
                ],
                question_concepts=['indonesia', 'marapi', 'fire mountain', 'fire', 'mountain'],
                activate_on_store=False
            ),
    'krakatoa_dutch': Task(
                knowledge_list= volcano_knowledge_list,
                retrieval_steps=[
                    RetrievalStep('query', {'type': 'volcano'}, {'last eruption': '2020', 'setting for': '21 balloons'}, 'node_id'), # krakatoa
                    RetrievalStep('retrieve', {}, {}, 'located in'), # indonesia
                    RetrievalStep('retrieve', {}, {}, 'colonized by'), # the netherlands
                    RetrievalStep('retrieve', {}, {}, 'official language') # dutch!
                ],
                question_concepts=['official language', 'europe', 'nation', 'volcano', 'islands', '2020', '21 balloons', 'william pene du bois'],
                activate_on_store=False
            ),
    'j_oval_office': Task(
            knowledge_list=[
            Knowledge('oval_office', {'is_a': 'room', 'located_in': 'the_white_house', 'first_word': 'oval', 'second_word': 'office', 'designed_by': 'nathan_c_wyeth', 'name': 'Oval Office'}),
            Knowledge('white_house', {'is_a': 'building', 'houses': 'president', 'has': 'room', 'famous_room': 'oval_office'}),
            Knowledge('oval', {'is_a': 'shape', 'num_sides': '0'}),
            Knowledge('square', {'is_a': 'shape', 'num_sides': '4'}),
            Knowledge('circle', {'is_a': 'shape', 'num_sides': '0'}),
            Knowledge('nathan_c_wyeth', {'is_a': 'architect', 'worked_on': 'the_white_house', 'born_in': 'illinois', 'year_born': '1870'}),
            Knowledge('william_taft', {'is_a': 'president', 'president_number': '27', 'assumed_office_in': '1909', 'ordered_construction_of': 'oval_office'}),
            Knowledge('1909', {'marks_opening_of': 'manhattan_bridge'}),
        ],
            retrieval_steps=[
                RetrievalStep('query', {'is_a': 'room'}, {'designed_by': 'nathan_c_wyeth', 'located_in': 'the_white_house'}, 'name'),
        ],
            question_concepts=['shape', 'room', 'nathan_c_wyeth', 'william_taft', '1909'],
            activate_on_store=False
        ),

    'j_nathan_birth_year': Task(
            knowledge_list=[
            Knowledge('oval_office', {'is_a': 'room', 'located_in': 'the_white_house', 'first_word': 'oval', 'second_word': 'office', 'designed_by': 'nathan_c_wyeth', 'name': 'Oval Office'}),
            Knowledge('white_house', {'is_a': 'building', 'houses': 'president', 'has': 'room', 'famous_room': 'oval_office'}),
            Knowledge('oval', {'is_a': 'shape', 'num_sides': '0'}),
            Knowledge('square', {'is_a': 'shape', 'num_sides': '4'}),
            Knowledge('circle', {'is_a': 'shape', 'num_sides': '0'}),
            Knowledge('nathan_c_wyeth', {'is_a': 'architect', 'worked_on': 'the_white_house', 'born_in': 'illinois', 'year_born': '1870'}),
            Knowledge('william_taft', {'is_a': 'president', 'president_number': '27', 'assumed_office_in': '1909', 'ordered_construction_of': 'oval_office'}),
            Knowledge('1909', {'marks_opening_of': 'manhattan_bridge'}),
        ],
            retrieval_steps=[
                RetrievalStep('query', {'is_a': 'room'}, {'located_in': 'the_white_house'}, 'node_id'),
                RetrievalStep('retrieve', {}, {}, 'designed_by'),
                RetrievalStep('retrieve', {}, {}, 'year_born')
        ],
            question_concepts=['year_born', 'architect', 'shape', 'room', 'the_white_house', '1909'],
            activate_on_store=False
        ),

    'michigan_football_q': Task(
            knowledge_list=[
            Knowledge('football', {'is_a': 'american_sport', 'best_d1_team': 'u_of_michigan'}),
            Knowledge('best_d1_team', {'means': 'most_wins'}),
            Knowledge('u_of_michigan', {'is_a': 'university', 'mascot_name': 'willy'}),
            Knowledge('willy', {'animal_type': 'wolverine', 'is_a': 'name'}),
        ],
            retrieval_steps=[
                RetrievalStep('query', {'is_a': 'american_sport'}, {}, 'best_d1_team'),
                RetrievalStep('retrieve', {}, {}, 'mascot_name'),
                RetrievalStep('retrieve', {}, {}, 'animal_type')
        ],
            question_concepts=['name', 'mascot', 'university', 'most_wins', 'american_sport'],
            activate_on_store=False
        ),

    'china_flag_q': Task(
            knowledge_list=[
            Knowledge('great_wall_of_china', {'is_a': 'wall', 'notable_info': 'largest_man_made_structure', 'located_in': 'china'}),
            Knowledge('china', {'is_a': 'country', 'located_in': 'asia', 'flag_is': 'chinese_flag'}),
            Knowledge('chinese_flag', {'is_a': 'flag', 'main_color': 'red', 'secondary_color': 'yellow', 'has_shape': 'star'}),
            Knowledge('red', {'is_a': 'color'}),
            Knowledge('yellow', {'is_a': 'color'})

        ],
            retrieval_steps=[
                RetrievalStep('query', {'notable_info': 'largest_man_made_structure'}, {}, 'located_in'),
                RetrievalStep('retrieve', {}, {}, 'flag_is'),
                RetrievalStep('retrieve', {}, {}, 'main_color'),
        ],
            question_concepts=['color', 'flag', 'country', 'largest_man_made_structure'],
            activate_on_store=False
        ),

    'khmer_cambodia_q': Task(
            knowledge_list=[
            Knowledge('khmer', {'is_a': 'language', 'notable_info': 'largest_alphabet', 'official_language_of': 'cambodia'}),
            Knowledge('cambodia', {'is_a': 'country', 'national_flower': 'rumduol'}),
            Knowledge('rumduol', {'smells': 'good', 'color': 'yellow'}),
        ],
            retrieval_steps=[
                RetrievalStep('query', {'notable_info': 'largest_alphabet'}, {}, 'official_language_of'),
                RetrievalStep('retrieve', {}, {}, 'national_flower'),
                RetrievalStep('retrieve', {}, {}, 'color'),
        ],
            question_concepts=['color', 'national_flower', 'country', 'language', 'largest_alphabet'],
            activate_on_store=False
        ),
    'olympics_washington': Task(
                knowledge_list=[
                Knowledge('2028 euro cup', {'is_a': 'major international sporting event', 'year': '2028'}),
                Knowledge('2028 olympics', {'is_a': 'major international sporting event', 'year': '2028',
                                            'host city': 'los angeles', 'is a': 'summer olympics'}),
                Knowledge('los angeles', {'is_a': 'city', 'in nation': 'usa', 'in state': 'california', 'mayor': 'eric garcetti'}),
                Knowledge('usa', {'is_a': 'nation', 'capital': 'washington dc'}),
            ],
                retrieval_steps=[
                    RetrievalStep('query', {'is_a': 'major international sporting event'}, {'year': '2028'}, 'node_id'),
                    RetrievalStep('retrieve', {}, {}, 'host city'), # los angeles
                    RetrievalStep('retrieve', {}, {}, 'in nation'),  # usa
                    RetrievalStep('retrieve', {}, {}, 'capital') #dc
            ],
                question_concepts=['capital', 'nation', 'major international sporting event', '2028'],
                activate_on_store=False
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
            question_concepts=['A'],
            activate_on_store=True
        )


create_paired_recall_tasks()


def determine_fok_function(method):
    if method == 'cue':
        return cue_fok
    elif method == 'target':
        return target_fok
    elif method == 'cue and target':
        return cue_and_target_fok
    elif method == 'straight_activation_fok':
        return straight_activation_fok
    elif method == 'outgoing edges cue':
        return outgoing_edges_cue_fok
    elif method == 'outgoing edges target':
        return outgoing_edges_target_fok
    elif method == 'cue_act_over_all':
        return cue_act_over_all
    elif method == 'act by edges cue':
        return act_by_edges_cue
    elif method == 'act_by_edges_target':
        return act_by_edges_target
    elif method == 'avg activation of everything':
        return avg_activation_of_everything
    elif method == 'results looked through':
        return results_looked_through_fok
    elif method == 'step num':
        return step_num_fok
    elif method == 'outgoing_edges_switch_fok':
        return outgoing_edges_switch_fok
    elif method == 'act_by_edges_switch_fok':
        return act_by_edges_switch_fok
    elif method == 'cue_out_edge_and_step_num_fok':
        return cue_out_edge_and_step_num_fok

# changes to return different node's activations depending on which pieces are available
def straight_activation_fok(store, terms, result, query_time, results_looked_through, step_num):
    if len(terms) > 0:
       return cue_fok(store, terms, result, query_time, results_looked_through, step_num)
    return target_fok(store, terms, result, query_time, results_looked_through, step_num)



# terms is {attribute : node}, like {first : A}
def cue_fok(store, terms, result, query_time, results_looked_through, step_num):
    # if the cue node is in the graph, proceed. (for the marapi cue this returns 0)
    avg_act = avg_activation_of_everything(store, terms, result, query_time, results_looked_through, step_num)
    if avg_act == 0:
        return 0
    return sum(
        math.log(store.get_activation(cue, query_time, True)/avg_act)
        for cue in terms.values() if store.graph.has_node(cue)
    )


def target_fok(store, terms, result, query_time, results_looked_through, step_num):
    if result is None:
        return 0
    avg_act = avg_activation_of_everything(store, terms, result, query_time, results_looked_through, step_num)
    if avg_act == 0 or store.get_activation(result, query_time, True) == 0:
        return 0
    return math.log(store.get_activation(result, query_time, True)/avg_act)


def cue_and_target_fok(store, terms, result, query_time, results_looked_through, step_num):
    return cue_fok(store, terms, result, query_time, results_looked_through, step_num) \
           + target_fok(store, terms, result, query_time, results_looked_through, step_num)

def cue_act_over_all(store, terms, result, query_time, results_looked_through, step_num):
    all_nodes = list(store.graph.nodes)
    total_act = sum(
        store.get_activation(node, query_time, True)
        for node in all_nodes
    )
    if total_act == 0:
        return 0
    return sum(
        store.get_activation(cue, query_time, True)
        / total_act
        for cue in terms.values()
    )

def outgoing_edges_cue_fok(store, terms, result, query_time, results_looked_through, step_num):
    avg_num_edges = store.graph.number_of_edges()/store.graph.number_of_nodes()
    return sum(math.log((len(store.graph.out_edges(cue))/avg_num_edges))
               for cue in terms.values() if len(store.graph.out_edges(cue)) != 0)

def outgoing_edges_target_fok(store, terms, result, query_time, results_looked_through, step_num):
    avg_num_edges = store.graph.number_of_edges()/store.graph.number_of_nodes()
    return math.log((len(store.graph.out_edges(result))/avg_num_edges))

def act_by_edges_cue(store, terms, result, query_time, results_looked_through, step_num):
    return sum(
        (
            (len(store.graph.out_edges(cue))* store.get_activation(cue, query_time, True)
        )
        for cue in terms.values() if store.graph.has_node(cue)
    ))

def act_by_edges_target(store, terms, result, query_time, results_looked_through, step_num):
    return len(store.graph.out_edges(result))* store.get_activation(result, query_time, True)

def avg_activation_of_everything(store, terms, result, query_time, results_looked_through, step_num):
    all_nodes = list(store.graph.nodes)
    return sum(
        store.get_activation(node, query_time, True)
        for node in all_nodes
    ) / len(all_nodes)

def results_looked_through_fok(store, terms, result, query_time, results_looked_through, step_num):
    if results_looked_through != 0:
        return 1/results_looked_through
    return 0

def step_num_fok(store, terms, result, query_time, results_looked_through, step_num):
    return step_num

def outgoing_edges_switch_fok(store, terms, result, query_time, results_looked_through, step_num):
    if len(terms) > 0:
        return outgoing_edges_cue_fok(store, terms, result, query_time, results_looked_through, step_num)
    else:
        return outgoing_edges_target_fok(store, terms, result, query_time, results_looked_through, step_num)

def act_by_edges_switch_fok(store, terms, result, query_time, results_looked_through, step_num):
    if len(terms) > 0:
        return act_by_edges_cue(store, terms, result, query_time, results_looked_through, step_num)
    else:
        return act_by_edges_target(store, terms, result, query_time, results_looked_through, step_num)

def cue_out_edge_and_step_num_fok(store, terms, result, query_time, results_looked_through, step_num):
    if len(terms) > 0:
        return outgoing_edges_cue_fok(store, terms, result, query_time, results_looked_through, step_num)
    else:
        return step_num_fok(store, terms, result, query_time, results_looked_through, step_num)





def contextualize_fok(historical_fok_list, pure_fok):
    # store pure fok in a list
    historical_fok_list.append(pure_fok)
    # then avg that list and multiply it w pure fok of the current node
    return (pure_fok * mean(historical_fok_list)), historical_fok_list


def populate(store, link, store_time, activate_on_store, knowledge_list):
    for knowledge in knowledge_list:
        store.store(store_time, link, activate_on_store, knowledge.node_id, **knowledge.attributes)
        store_time += 1
    return store_time


def test_model():
    act_decay_rate = [-0.25]
    act_scale_factor = [0.5]
    act_max_steps = [6]
    act_capped = [True]
    backlinks = [True, False]
    fok_method = [
        'act by edges cue', 'cue and target', 'cue', 'target', 'cue_act_over_all', 'act_by_edges_target',
                 'outgoing edges cue', 'outgoing edges target', 'avg activation of everything', 'results looked through', 'step num',
                'outgoing_edges_switch_fok', 'act_by_edges_switch_fok', 'cue_out_edge_and_step_num_fok',
            'straight_activation_fok'
    ]

    # task_names = list(TASKS.keys())
    task_names = [ 'j_grid', 'j_volcano_to_marapi', 'j_volcano_fire',
                'j_indonesia_mountain', 'j_volcano_mountain',
                   'j_marapi_to_volcano', 'j_oval_office', 'krakatoa_dutch', 'j_nathan_birth_year',
                   'michigan_football_q', 'china_flag_q', 'khmer_cambodia_q', 'olympics_washington'
                  ]
    task_names = ['olympics_washington', 'michigan_football_q']

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
        step_history_list = []
        task = TASKS[task_name]
        print(', '.join([
            'task = ' + str(task_name),
            'fok_method = ' + fok_method,
            # 'decay rate = ' + str(rate),
            # 'scale factor = ' + str(scale),
            # 'max steps = ' + str(step),
            'capped = ' + str(cap),
            'backlinks = ' + str(backlink),

        ]))
        store = NetworkXKB(ActivationClass(rate, scale, step, cap))
        time = 1 + populate(store, backlink, 0, task.activate_on_store, task.knowledge_list)
        for concept in task.question_concepts: #familiarizing self with question concepts
            store.retrieve(time, concept)
        fok_function = determine_fok_function(fok_method)
        prev_fok = []
        prev_result = None

        # loop through the retrieval steps
        for step_num, step in enumerate(task.retrieval_steps, start=1):
            on_step_level = True
            print(step)
            # take the retrieval step
            if step.action == 'query':
                result = store.query(time, False, step.query_terms)
            elif step.action == 'retrieve':
                result = store.retrieve(time, prev_result)
            else:
                print('invalid action: ' + step.action)
                return
            failed = result is None
            results_looked_through = 1
            time += 1

            while not failed:
                print(result['node_id'])
                # calculate fok
                pure_fok = fok_function(store, step.query_terms, result['node_id'], time, results_looked_through, step_num)
                print('step ' + str(step_num) + ' pure_fok = ' + str(pure_fok))


                if all(result.get(attr, None) == val for attr, val in step.constraints.items()):
                    # if the constraints are met, move on to the next step
                    if result.__contains__(step.result_attr):
                        prev_result = result[step.result_attr]
                        # and add this current pure fok to the history (?)
                        # (and this is the step level, I suppose, as this if is the gate to the next step)
                        informed_fok, prev_fok = contextualize_fok(prev_fok, pure_fok)
                        # print('informed/contextualized fok = ' + str(informed_fok))
                        break
                    else:
                        # curr result does not have the result_attr we were expecting. continue looping through results
                        results_looked_through += 1
                        # if there is a next result, move on to the next result
                        result = store.next_result(time)
                elif store.has_next_result:
                    results_looked_through += 1
                    # if there is a next result, move on to the next result
                    result = store.next_result(time)
                else:
                    # otherwise, we've hit a dead end
                    print('this is a dead end')
                    failed = True
                time += 1
            if failed:
                break
        print(prev_result)
        print()

test_model()
