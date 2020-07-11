import math
from itertools import product
from collections import namedtuple

from research.rl_memory import ActivationClass, NetworkXKB
from statistics import mean

from bokeh.io import show
from bokeh.layouts import gridplot
from bokeh.plotting import figure

import plotly.graph_objects as go

task_list = []
fok_method_list = []
result_list = []
fok_list = []
hist_fok_list = []
step_list = []


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
                'type': 'landform',
                'comes from': 'tectonic plates',
                'produces': 'heat',
                'expels': 'lava',
                'full of': 'magma',
                'name': 'Volcano',
                'similar to': 'mountain',
                'can be called': 'fire mountain',
            },
        ),
        Knowledge('lava', {'type': 'molten rock', 'expelled from': 'volcano', 'gives off': 'heat', 'related to': 'fire', 'formerly': 'magma', 'name': 'Lava', 'associated with': 'volcano'}),
        Knowledge('magma', {'type': 'molten rock', 'inside': 'volcano', 'gives off': 'heat', 'related to': 'fire', 'name': 'Magma', 'associated with': 'volcano'}),
        Knowledge('fire', {'consumes': 'grass', 'type': 'chemical reaction', 'related to': 'heat', 'results in': 'ash', 'name': 'Fire'}),
        Knowledge('jakarta', {'type': 'city', 'capital of': 'indonesia', 'located in': 'indonesia', 'population': '9.6 million', 'name': 'Jakarta'}),
        Knowledge('yamin', {'type': 'mountain', 'located in': 'indonesia', 'height': '4540 m', 'name': 'Yamin'}),
        Knowledge('pangrango', {'type': 'volcano', 'located in': 'indonesia', 'status': 'dormant', 'name': 'Pangrango', 'is a': 'mountain'}),
        Knowledge('tujuh', {'type': 'volcano', 'located in': 'indonesia', 'is a': 'mountain', 'name': 'Tujuh'}),
        Knowledge('kelimutu', {'type': 'volcano', 'located in': 'indonesia', 'name': 'Kelimutu', 'last eruption': '1968', 'is a': 'mountain'}),
        Knowledge('krakatoa', {'type': 'volcano', 'located in': 'indonesia', 'last eruption': '2020', 'is a': 'mountain', 'name': 'Krakatoa', 'setting for': '21 balloons'}),
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
            RetrievalStep('query', {'famous example': 'marapi'}, {}, 'name'), # returns null (so try again!)
            RetrievalStep('query', {'located in': 'indonesia'}, {'is a': 'mountain'}, 'type') # returns volcano
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
                    RetrievalStep('query', {'name': 'Marapi'}, {}, 'is a'), # returns null, so try something different
                    RetrievalStep('query', {'located in': 'indonesia'}, {'is a': 'mountain'}, 'type') # returns volcano
                ],
                question_concepts=['indonesia', 'marapi', 'fire mountain', 'fire', 'mountain'],
                activate_on_store=False
            ),
    'j_volcano_strategy_switch': Task(
            knowledge_list= volcano_knowledge_list,
            retrieval_steps=[
                # free associate on fire
                RetrievalStep('query', {'related to': 'fire'}, {}, 'name'),
                # free associate on mountain (should not return hill bc lava was just queried activated)
                RetrievalStep('query', {'similar to': 'mountain'}, {}, 'name'),
            ],
            question_concepts=['indonesia', 'marapi', 'fire mountain', 'fire', 'mountain'],
            activate_on_store=False
        ),

    'krakatoa_dutch': Task(
                knowledge_list= volcano_knowledge_list,
                retrieval_steps=[
                    RetrievalStep('query', {'type': 'volcano'}, {'last eruption': '2020', 'setting for': '21 balloons'}, 'located in'), # krakatoa --> indonesia
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
                RetrievalStep('query', {'is_a': 'room'}, {'located_in': 'the_white_house'}, 'designed_by'),
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
                    RetrievalStep('query', {'is_a': 'major international sporting event'}, {'year': '2028'}, 'host city'), # los angeles
                    RetrievalStep('retrieve', {}, {}, 'in nation'),  # usa
                    RetrievalStep('retrieve', {}, {}, 'capital') #dc
            ],
                question_concepts=['capital', 'nation', 'major international sporting event', '2028'],
                activate_on_store=False
            ),
    'lanyard': Task(
                    knowledge_list=[
                    Knowledge('occidental', {'is_a': 'college', 'mascot': 'oswald', 'city': 'los angeles', 'state': 'california',
                                             'president': 'harry elam'}),
                    Knowledge('college', {'is_a': 'academic institution', 'gives': 'degree', 'has': 'dorm',
                                          'enrolls': 'students', 'employs': 'professors'}),
                    Knowledge('harvard', {'is_a': 'college', 'known for': 'prestige'}),
                    Knowledge('liberal arts school', {'is_a': 'college'}),
                    Knowledge('dorm', {'is_a': 'building', 'has': 'rooms', 'requires': 'key'}),
                    Knowledge('key', {'used for': 'doors'}),
                    Knowledge('keychain', {'holds': 'key'}),
                    Knowledge('lanyard', {'holds': 'key', 'used by': 'students'}),
                    Knowledge('los angeles', {'is_a': 'city', 'in nation': 'usa', 'in state': 'california', 'mayor': 'eric garcetti'}),
                    Knowledge('usa', {'is_a': 'nation', 'capital': 'washington dc'}),
                    Knowledge('sailing', {'requires': 'ships', 'gives': 'degree'}),
                    ],
                    retrieval_steps=[
                        RetrievalStep('query', {'related to':'college'}, {'holds': 'key'}, 'node_id'), # high fok bc college, but fails
                        RetrievalStep('query', {'holds': 'key'}, {'origin': 'sailing'}, 'node_id'), # fails, too narrow
                        RetrievalStep('query', {'holds': 'key'}, {}, 'node_id') # returns....lanyard, bc spreading from college
                ],
                    question_concepts=['college', 'dorm', 'key', 'sailing'],
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
    if method == 'straight_activation_fok':
        return relative_activation_fok
    elif method == 'act_over_all_fok':
        return act_over_all_fok
    elif method == 'results_looked_through':
        return results_looked_through_fok
    elif method == 'step_num':
        return step_num_fok
    elif method == 'outgoing_edges_fok':
        return outgoing_edges_fok
    elif method == 'act_over_edges_fok_1':
        return act_over_edges_fok_1
    elif method == 'act_over_edges_fok_2':
        return act_over_edges_fok_2
    elif method == 'num_results_fok':
        return num_results_fok
    elif method == 'competition_fok_1':
        return competition_fok_1
    elif method == 'competition_fok_2':
        return competition_fok_2


# helper functions to support more complicated fok methods
def avg_activation_of_everything(store, query_time):
    all_nodes = list(store.graph.nodes)
    return sum(
        store.get_activation(node, query_time, True)
        for node in all_nodes
    ) / len(all_nodes)

def outgoing_edges_of_cue(store, terms, result, query_time, results_looked_through, step_num):
    avg_num_edges = store.graph.number_of_edges()/store.graph.number_of_nodes()
    return sum(math.log((len(store.graph.out_edges(cue))/avg_num_edges))
               for cue in terms.values() if len(store.graph.out_edges(cue)) != 0)

def outgoing_edges_of_target(store, terms, result, query_time, results_looked_through, step_num):
    avg_num_edges = store.graph.number_of_edges()/store.graph.number_of_nodes()
    return math.log((len(store.graph.out_edges(result))/avg_num_edges))

def cue_activation(store, terms, query_time):
    # if the cue node is in the graph, proceed. (for the marapi cue this returns 0)
    avg_act = avg_activation_of_everything(store, query_time)
    if avg_act == 0:
        return 0
    return sum(
        math.log(store.get_activation(cue, query_time, True)/avg_act) for cue in terms.values()
    )

def target_activation(store, result, query_time):
    if result is None:
        return 0
    avg_act = avg_activation_of_everything(store, query_time)
    if avg_act == 0 or store.get_activation(result, query_time, True) == 0:
        return 0
    return math.log(store.get_activation(result, query_time, True)/avg_act)




# actual fok methods

def relative_activation_fok(store, terms, result, query_time, results_looked_through, step_num):
    if len(terms) > 0:
       return cue_activation(store, terms, query_time)
    return target_activation(store, result, query_time)

# returns the current node's activation as a share of total activation of all nodes in the network
def act_over_all_fok(store, terms, result, query_time, results_looked_through, step_num):  #FIXME
    all_nodes = list(store.graph.nodes)
    total_act = sum(
        store.get_activation(node, query_time, True) for node in all_nodes
    )
    if total_act == 0:
        return 0
    return relative_activation_fok(store, terms, result, query_time, results_looked_through, step_num)


def results_looked_through_fok(store, terms, result, query_time, results_looked_through, step_num):
    if results_looked_through != 0:
        return 1/results_looked_through
    return 0

def step_num_fok(store, terms, result, query_time, results_looked_through, step_num):
    return step_num

def outgoing_edges_fok(store, terms, result, query_time, results_looked_through, step_num):
    if len(terms) > 0:
        return outgoing_edges_of_cue(store, terms, result, query_time, results_looked_through, step_num)
    else:
        return outgoing_edges_of_target(store, terms, result, query_time, results_looked_through, step_num)

# logs first
def act_over_edges_fok_1(store, terms, result, query_time, results_looked_through, step_num):
    relative_edges = outgoing_edges_fok(store, terms, result, query_time, results_looked_through, step_num)
    if relative_edges == 0:
        return 0
    return (relative_activation_fok(store, terms, result, query_time, results_looked_through, step_num)
            / relative_edges)

#
def act_over_edges_fok_2(store, terms, result, query_time, results_looked_through, step_num):
    if len(terms) > 0:
        curr_activation = sum(store.get_activation(cue, query_time, True) for cue in terms.values())
        curr_edges = sum(len(store.graph.out_edges(cue)) for cue in terms.values())
    else:
        curr_activation = store.get_activation(result, query_time, True)
        curr_edges = len(store.graph.out_edges(result))
    avg_num_edges = store.graph.number_of_edges() / store.graph.number_of_nodes()
    if avg_activation_of_everything(store, query_time) == 0:
        return 0
    activation_ratio = curr_activation/avg_activation_of_everything(store, query_time)
    if curr_edges == 0 or avg_num_edges == 0:
        return 0
    edges_ratio = curr_edges/avg_num_edges
    return math.log(
        activation_ratio/edges_ratio
    )

# returns 1/ the relative edges measurement defined above
def competition_fok_1(store, terms, result, query_time, results_looked_through, step_num):
    edges = outgoing_edges_fok(store, terms, result, query_time, results_looked_through, step_num)
    if edges == 0:
        return 0
    return 1/edges

# returns 1/ the raw number of edges
def competition_fok_2(store, terms, result, query_time, results_looked_through, step_num):
    if len(terms) > 0:
        edges = (sum((len(store.graph.out_edges(cue)))
                   for cue in terms.values()))
    else:
        edges = (len(store.graph.out_edges(result)))
    if edges == 0:
        return 0
    else:
        return 1/edges

def num_results_fok(store, terms, result, query_time, results_looked_through, step_num):
    return len(store.query_results)
    # FIXME is the same the whole time

def create_historic_fok(fok_function):
    foks = []
    def real_fok(store, terms, result, query_time, results_looked_through, step_num):
        foks.append(fok_function(store, terms, result, query_time, results_looked_through, step_num))
        if len(foks) < 2:  # baseline is 0
            return mean(foks)
        else:
            return foks[len(foks)-1] - foks[len(foks)-2]  # delta of the last two foks to determine decrease/ increase


    return real_fok


#
# def contextualize_fok(historical_fok_list, pure_fok):
#     # store pure fok in a list
#     historical_fok_list.append(pure_fok)
#     # then avg that list and multiply it w pure fok of the current node
#     return (pure_fok * mean(historical_fok_list)), historical_fok_list


def populate(store, link, store_time, activate_on_store, knowledge_list):
    for knowledge in knowledge_list:
        store.store(store_time, link, activate_on_store, knowledge.node_id, **knowledge.attributes)
        store_time += 1
    return store_time

# visuals

def create_table(headers, column_values):
    fig = go.Figure(data=[go.Table(header=dict(values=headers),
                                   cells=dict(values=column_values))
                          ])
    fig.show()

def create_and_display_graph(steps, foks, hist_foks, fok_method, task_names):
    color_list = ['#f52500', '#f59700', '#c9b500', '#5ca602', '#05e8a8', '#00c5db', '#0038d1', '#9457ff', '#cc28fa',
                  '#e305a4']

    graph_list = []

    for name in TASKS.keys():
        index = task_names.index(name)
        graph = figure(title=name, x_axis_label='Step Num',
                       y_axis_label='FOK')
        method_name = fok_method[index]
        color_index = 0
        x_list = []
        y_list = []
        hist_list = []
        while True:
            while steps[index] != '':
                assert foks[index] != ''
                x_list.append(steps[index])
                y_list.append(foks[index])
                hist_list.append(hist_foks[index])
                index += 1
            if index == len(steps) -1:    # end of the list
                break
            index += 1  # skipping over blank line in method
            graph.circle(x_list, y_list, line_width=4, color=color_list[color_index])
            graph.line(x_list, y_list, line_width=2, color=color_list[color_index])

            graph.circle(x_list, hist_list, line_width=3, color=color_list[color_index])
            graph.line(x_list, hist_list, line_width=2, color=color_list[color_index], line_dash='dotted')

            if task_names[index] == name:  # next plot of different fok method
                x_list = []
                y_list = []
                hist_list = []
                color_index += 1
                assert color_index <= len(color_list)
                method_name = fok_method[index]
            else:
                break  # next graph
        graph_list.append(graph)

    grid = gridplot([graph_list], plot_width=490, plot_height=500)
    show(grid)




def test_model():
    global task_list, fok_method_list, step_list, fok_list, hist_fok_list, result_list
    act_decay_rate = [-0.25]
    act_scale_factor = [0.5]
    act_max_steps = [6]
    act_capped = [True]
    backlinks = [True]
    fok_methods = [
        'straight_activation_fok', 'act_over_all_fok', 'results_looked_through', 'step_num',
        'outgoing_edges_fok', 'act_over_edges_fok_1', 'act_over_edges_fok_2', 'num_results_fok', 'competition_fok_1',
        'competition_fok_2'
    ]
    # 'cue_and_target', 'straight_activation_fok', 'act_over_avg_fok', 'results_looked_through', 'step_num', 'outgoing_edges_fok', 'act_over_edges_fok'
    task_names = list(TASKS.keys())
    # task_names = [ 'j_grid', 'j_volcano_to_marapi', 'j_volcano_fire',
    #             'j_indonesia_mountain', 'j_volcano_mountain', 'j_volcano_strategy_switch',
    #                'j_marapi_to_volcano', 'j_oval_office', 'krakatoa_dutch', 'j_nathan_birth_year',
    #                'michigan_football_q', 'china_flag_q', 'khmer_cambodia_q', 'olympics_washington'
    #               ]

    # task_names = ['ABAB_direct', 'ABCB_direct', 'ABCD_direct', 'ABAD_direct',
    #               'ABAB_pairs', 'ABCB_pairs', 'ABCD_pairs', 'ABAD_pairs',
    #                 'ABAB_types', 'ABCB_types', 'ABCD_types', 'ABAD_types',]


    generator = product(
        task_names,
        act_decay_rate,
        act_scale_factor,
        act_max_steps,
        act_capped,
        backlinks,
        fok_methods,


    )

    for task_name, rate, scale, step, cap, backlink, fok_method, in generator:
        query_list = []   # creating/ resetting query and retrieval lists
        retrieval_dict = {}
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
        fok_method_list.append(fok_method)  # FOK METHOD TO TABLE
        task_list.append(str(task_name))  # TASK TO TABLE

        store = NetworkXKB(ActivationClass(rate, scale, step, cap))
        time = 1 + populate(store, backlink, 0, task.activate_on_store, task.knowledge_list)
        for concept in task.question_concepts: # familiarizing self with question concepts
            store.retrieve(time, concept)
        fok_function = determine_fok_function(fok_method)
        historic_fok = create_historic_fok(fok_function)
        prev_result = None

        # loop through the retrieval steps
        for step_num, step in enumerate(task.retrieval_steps, start=1):
            # print(step)
            # take the retrieval step
            if step.action == 'query':
                if step in query_list:  # if this entire query retrieval step has been done before in this task, don't try again
                    print('youve already done this, try another query')
                result = store.query(time, False, step.query_terms)
                query_list.append(step)  # append the whole retrieval step
            elif step.action == 'retrieve':
                if prev_result in retrieval_dict and step.result_attr == retrieval_dict[prev_result]:
                    print('youve already done this, try another retrieval')
                result = store.retrieve(time, prev_result)
                retrieval_dict.update({prev_result: step.result_attr})  # append the previous result and the result attribute (ex. indonesia: colonized by)

            else:
                print('invalid action: ' + step.action)
                return
            failed = result is None
            results_looked_through = 1
            time += 1

            while not failed:
                # print(str(result['node_id']) + ' '+ str(store.get_activation(result['node_id'], time, False)))

                fok_method_list.append('')
                task_list.append('')
                result_list.append(result['node_id'])  # RESULT TO TABLE




                # calculate fok
                pure_fok = fok_function(store, step.query_terms, result['node_id'], time, results_looked_through, step_num)
                hist_fok = historic_fok(store, step.query_terms, result['node_id'], time, results_looked_through, step_num)
                print('step ' + str(step_num) + ' pure_fok = ' + str(pure_fok) + ', historic fok = ' + str(hist_fok))
                print(result['node_id'])
                hist_fok_list.append(hist_fok)
                fok_list.append(pure_fok)  # FOK TO TABLE
                step_list.append(str(step_num))  # STEP TO TABLE





                if all(result.get(attr, None) == val for attr, val in step.constraints.items()):
                    # if the constraints are met, move on to the next step
                    if result.__contains__(step.result_attr):
                        prev_result = result[step.result_attr]
                        # and add this current pure fok to the history (?)
                        # (and this is the step level, I suppose, as this if is the gate to the next step)
                        # informed_fok, prev_fok = contextualize_fok(prev_fok, pure_fok)
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
        result_list.append(prev_result)
        fok_list.append('')
        hist_fok_list.append('')
        step_list.append('')
        print()

    create_and_display_graph(step_list, fok_list, hist_fok_list, fok_method_list, task_list)


test_model()
# create_table(['task', 'fok method', 'step num', 'fok', 'result'], [task_list, fok_method_list, step_list, fok_list, result_list])
#create_and_display_graph()
#sehrjkejrgh



