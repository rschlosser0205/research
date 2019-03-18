import sys
import logging
from collections import namedtuple
from itertools import combinations, chain

from networkx import MultiDiGraph, DiGraph
from networkx.algorithms import shortest_path

from research.knowledge_base import SparqlEndpoint
from research.rl_memory import SparqlKB


from record_store import first_letter, date_to_decade

SparqlGraph = namedtuple('SparqlGraph', 'name, graph, props, start_vars, end_var, diff_vars, transform')
Action = namedtuple('Action', 'type, subject, property, object, result')

LOGGER = logging.getLogger(__name__)

KB_SOURCE = SparqlEndpoint('http://162.233.132.179:8890/sparql')
KB_ADAPTOR = SparqlKB(KB_SOURCE)

NAME_PROP = '<http://xmlns.com/foaf/0.1/name>'
RELEASE_DATE_PROP = '<http://wikidata.dbpedia.org/ontology/releaseDate>'
ALBUM_PROP = '<http://wikidata.dbpedia.org/ontology/album>'
ARTIST_PROP = '<http://wikidata.dbpedia.org/ontology/artist>'
HOMETOWN_PROP = 'http://wikidata.dbpedia.org/ontology/hometown'
COUNTRY_PROP = 'http://wikidata.dbpedia.org/ontology/country'


def release_date():
    graph = MultiDiGraph()
    graph.add_edge('track', 'album_uri', label=ALBUM_PROP)
    graph.add_edge('album_uri', 'album_name', label=NAME_PROP)
    graph.add_edge('album_uri', 'release_date', label=RELEASE_DATE_PROP)
    return SparqlGraph(
        'album_date',
        graph,
        [NAME_PROP],
        ['album_name'],
        'release_date',
        [],
        date_to_decade,
    )


def artist():
    graph = MultiDiGraph()
    graph.add_edge('track_uri', 'album_uri', label=ALBUM_PROP)
    graph.add_edge('album_uri', 'album_name', label=NAME_PROP)
    graph.add_edge('album_uri', 'artist_uri', label=ARTIST_PROP)
    graph.add_edge('artist_uri', 'artist_name', label=NAME_PROP)
    return SparqlGraph(
        'album_artist',
        graph,
        [NAME_PROP],
        ['album_name'],
        'artist_name',
        [],
        first_letter,
    )


def country():
    graph = MultiDiGraph()
    graph.add_edge('track_uri', 'album_uri', label=ALBUM_PROP)
    graph.add_edge('album_uri', 'album_name', label=NAME_PROP)
    graph.add_edge('album_uri', 'artist_uri', label=ARTIST_PROP)
    graph.add_edge('artist_uri', 'hometown_uri', label=HOMETOWN_PROP)
    graph.add_edge('hometown_uri', 'country_uri', label=COUNTRY_PROP)
    graph.add_edge('country_uri', 'country_name', label=NAME_PROP)
    return SparqlGraph(
        'album_country',
        graph,
        [NAME_PROP],
        ['album_name'],
        'country_name',
        [],
        first_letter,
    )


def other_album():
    graph = MultiDiGraph()
    graph.add_edge('track', 'album_uri', label=ALBUM_PROP)
    graph.add_edge('album_uri', 'album_name', label=NAME_PROP)
    graph.add_edge('album_uri', 'release_date', label=RELEASE_DATE_PROP)
    graph.add_edge('album_uri', 'artist_uri', label=ARTIST_PROP)
    graph.add_edge('other_track', 'other_album_uri', label=ALBUM_PROP)
    graph.add_edge('other_album_uri', 'other_album_name', label=NAME_PROP)
    graph.add_edge('other_album_uri', 'other_release_date', label=RELEASE_DATE_PROP)
    graph.add_edge('other_album_uri', 'artist_uri', label=ARTIST_PROP)
    graph.add_edge('artist_uri', 'artist_name', label=NAME_PROP)
    return SparqlGraph(
        'album_date_album',
        graph,
        [NAME_PROP, RELEASE_DATE_PROP],
        ['album_name', 'other_release_date'],
        'other_album_name',
        ['album_uri', 'other_album_uri'],
        first_letter,
    )


def networkx_to_sparql(sparql_graph):
    lines = []
    result_vars = ' '.join(
        f'?{var}' for var
        in sparql_graph.start_vars + [sparql_graph.end_var]
    )
    lines.append(f'SELECT DISTINCT {result_vars} WHERE {{')
    variables = set()
    names = set()
    for src, dst, _ in sparql_graph.graph.edges:
        variables.add(src)
        variables.add(dst)
        for _, edge_data in sparql_graph.graph.get_edge_data(src, dst).items():
            if edge_data["label"] == NAME_PROP:
                names.add(dst)
            lines.append(f'    ?{src} {edge_data["label"]} ?{dst} .')
    for var in sparql_graph.start_vars + [sparql_graph.end_var] + sparql_graph.diff_vars:
        if var not in variables:
            raise ValueError(f'?{var} is not a variable in the query')
    for name in names:
        lines.append(f'    FILTER ( lang(?{name}) = "en" )')
    for var1, var2 in combinations(sparql_graph.diff_vars, 2):
        lines.append(f'    FILTER ( ?{var1} != ?{var2} )')
    lines.append(f'}}')
    return '\n'.join(lines)


def get_edge_label(graph, src, dst):
    return graph.get_edge_data(src, dst)[0]['label']


def add_path_to_action_graph(path, graph, action_graph):
    i = 0
    while i < len(path) - 1:
        curr_node = path[i]
        next_node = path[i + 1]
        if i + 2 < len(path):
            next_next_node = path[i + 2]
        else:
            next_next_node = None
        should_query_child = (
            next_next_node is not None
            and graph.has_edge(curr_node, next_node)
            and graph.has_edge(next_next_node, next_node)
        )
        if next_node == path[-1]:
            # use child
            label = get_edge_label(graph, curr_node, next_node)
            action_graph.add_edge(
                curr_node, next_node,
                action=Action('use', curr_node, label, next_node, next_node),
                label=f'use child: {curr_node} -> {next_node}',
            )
            i += 1
        elif graph.has_edge(next_node, curr_node):
            # query self
            label = get_edge_label(graph, next_node, curr_node)
            action_graph.add_edge(
                curr_node, next_node,
                action=Action('query', '_environment', label, curr_node, next_node),
                label=f'query self: {next_node} -> {curr_node}',
            )
            i += 1
        elif should_query_child:
            # query child
            label = get_edge_label(graph, curr_node, next_node)
            action_graph.add_edge(
                curr_node, next_next_node,
                action=Action('query', curr_node, label, next_node, next_next_node),
                label=f'query child: {curr_node} -> {next_next_node}',
            )
            i += 2
        elif graph.has_edge(curr_node, next_node):
            # retrieve child
            label = get_edge_label(graph, curr_node, next_node)
            action_graph.add_edge(
                curr_node, next_node,
                action=Action('retrieve', curr_node, label, next_node, next_node),
                label=f'retrieve child: {curr_node} -> {next_node}',
            )
            i += 1
        else:
            ValueError(f'not sure what to do at {curr_node}')


def build_action_graph(sparql_graph):
    action_graph = DiGraph()
    graph = sparql_graph.graph
    for start_var in sparql_graph.start_vars:
        path = shortest_path(graph.to_undirected(), start_var, sparql_graph.end_var)
        add_path_to_action_graph(path, graph, action_graph)
    return action_graph


def sequentialize_actions(sparql_graph, action_graph):
    queue = list(chain(*(
        action_graph.successors(start_var)
        for start_var in sparql_graph.start_vars
    )))
    visited = set(sparql_graph.start_vars)
    actions = []
    while queue:
        curr_node = queue.pop(0)
        if curr_node in visited:
            continue
        while all(node in visited for node in action_graph.predecessors(curr_node)):
            visited.add(curr_node)
            actions.append([
                action_graph.get_edge_data(predecessor, curr_node)['action']
                for predecessor in action_graph.predecessors(curr_node)
            ])
            if curr_node == sparql_graph.end_var:
                break
            successors = list(action_graph.successors(curr_node))
            curr_node = successors[0]
            queue.extend(successors[1:])
        if curr_node != sparql_graph.end_var:
            queue.append(curr_node)
    return actions


def download_qa_pairs(sparql_graph):
    limit = 100
    offset = 0
    query_template = networkx_to_sparql(sparql_graph)
    query = query_template + f' LIMIT {limit} OFFSET {offset}'
    results = KB_SOURCE.query_sparql(query)
    while results:
        for result in results:
            question = {
                prop: result[start_var].rdf_format for prop, start_var
                in zip(sparql_graph.props, sparql_graph.start_vars)
            }
            answer = result[sparql_graph.end_var].rdf_format
            yield question, answer
        offset += limit
        query = query_template + f' LIMIT {limit} OFFSET {offset}'
        results = KB_SOURCE.query_sparql(query)


def check_query(cache, actions):
    query_terms = {}
    for action in actions:
        if action.property not in cache[action.subject]:
            return None
        query_terms[action.property] = cache[action.subject][action.property]
    LOGGER.debug(f'querying for {query_terms}')
    return KB_ADAPTOR.query(query_terms)


def check_retrieve(cache, actions):
    assert len(actions) == 1
    action = next(iter(actions))
    if action.property not in cache[action.subject]:
        return None
    LOGGER.debug(f'retrieving {cache[action.subject][action.property]}')
    return KB_ADAPTOR.retrieve(cache[action.subject][action.property])


def is_valid_qa_pair(question, answer, sparql_graph, actions):
    cache = {
        '_environment': question,
    }
    for step, step_actions in enumerate(actions, start=1):
        LOGGER.debug(f'Step {step}')
        LOGGER.debug('\n'.join(f'    {action}' for action in step_actions))
        assert len(set(action.type for action in step_actions)) == 1
        assert len(set(action.result for action in step_actions)) == 1
        for action in step_actions:
            if action.subject not in cache:
                raise ValueError('need {action.subject} but not found in cache')
        action = step_actions[0]
        result_var = action.result
        if action.type == 'query':
            result = check_query(cache, step_actions)
        elif action.type == 'retrieve':
            result = check_retrieve(cache, step_actions)
        elif action.type == 'use':
            LOGGER.debug(f'checking {cache[action.subject].get(action.property, None)} == {answer}')
            return cache[action.subject].get(action.property, None) == answer
        else:
            raise ValueError(step_actions)
        LOGGER.debug(f'result: {result}')
        if result is None:
            return False
        cache[result_var] = result
    raise ValueError('ran out of actions before use')


def download_data(sparql_graph):
    action_graph = build_action_graph(sparql_graph)
    actions = sequentialize_actions(sparql_graph, action_graph)
    with open('data/' + sparql_graph.name, 'w') as fd:
        fd.write('(\n')
    count = 0
    for question, answer in download_qa_pairs(sparql_graph):
        LOGGER.info(f'verifying {question} -> {answer}')
        if is_valid_qa_pair(question, answer, sparql_graph, actions):
            transformed_answer = sparql_graph.transform(answer)
            if transformed_answer:
                with open('data/' + sparql_graph.name, 'a') as fd:
                    fd.write('    ' + repr((question, transformed_answer)))
                    fd.write(',\n')
                count += 1
                if count % 100 == 0:
                    LOGGER.debug(f'processed {count} albums')
    with open('data/' + sparql_graph.name, 'a') as fd:
        fd.write(')\n')


def main():
    if sys.argv[1] == 'release-date':
        sparql_graph = release_date()
    elif sys.argv[1] == 'artist':
        sparql_graph = artist()
    elif sys.argv[1] == 'country':
        sparql_graph = country()
    elif sys.argv[1] == 'other-album':
        sparql_graph = other_album()
    download_data(sparql_graph)


if __name__ == '__main__':
    main()
