"""Memory architecture for reinforcement learning."""

from collections import namedtuple, defaultdict
from collections.abc import Hashable
from uuid import uuid4 as uuid

from networkx import MultiDiGraph

from .rl_environments import State, Action, Environment
from .data_structures import TreeMultiMap


def memory_architecture(cls):
    """Decorate an Environment to become a memory architecture.

    Arguments:
        cls (class): The Environment superclass.

    Returns:
        class: A subclass with a memory architecture.
    """
    # pylint: disable = too-many-statements
    assert issubclass(cls, Environment)

    # pylint: disable = invalid-name
    BufferProperties = namedtuple('BufferProperties', ['copyable', 'writable'])

    class MemoryArchitectureMetaEnvironment(cls):
        """A subclass to add a long-term memory to an Environment."""

        BUFFERS = {
            'perceptual': BufferProperties(
                copyable=True,
                writable=False,
            ),
            'query': BufferProperties(
                copyable=False,
                writable=True,
            ),
            'retrieval': BufferProperties(
                copyable=True,
                writable=False,
            ),
            'scratch': BufferProperties(
                copyable=True,
                writable=True,
            ),
        }

        def __init__(
                self,
                buf_ignore=None, internal_reward=-0.1, max_internal_actions=None,
                knowledge_store=None,
                *args, **kwargs,
        ): # noqa: D102
            """Initialize a memory architecture.

            Arguments:
                buf_ignore (Iterable[str]): Buffers that should not be created.
                internal_reward (float): Reward for internal actions. Defaults to -0.1.
                max_internal_actions (int): Max number of consecutive internal actions. Defaults to None.
                knowledge_store (KnowledgeStore): The memory model to use.
                *args: Arbitrary positional arguments.
                **kwargs: Arbitrary keyword arguments.
            """
            # pylint: disable = keyword-arg-before-vararg
            # parameters
            if buf_ignore is None:
                buf_ignore = set()
            self.buf_ignore = set(buf_ignore)
            self.internal_reward = internal_reward
            self.max_internal_actions = max_internal_actions
            # infrastructure
            if knowledge_store is None:
                knowledge_store = NaiveDictKB()
            self.knowledge_store = knowledge_store
            # variables
            self.buffers = {}
            self.internal_action_count = 0
            # initialization
            self._clear_buffers()
            super().__init__(*args, **kwargs)

        @property
        def slots(self):
            """Yield all values of all attributes in all buffers.

            Yields:
                Tuple[str, str, Any]: A tuple of buffer, attribute, and value.
            """
            for buf, attrs in sorted(self.buffers.items()):
                for attr, val in attrs.items():
                    yield buf, attr, val

        def to_dict(self):
            """Convert the state into a dictionary."""
            return {buf + '_' + attr: val for buf, attr, val in self.slots}

        def get_state(self): # noqa: D102
            # pylint: disable = missing-docstring
            return State(**self.to_dict())

        def get_observation(self): # noqa: D102
            # pylint: disable = missing-docstring
            return State(**self.to_dict())

        def reset(self): # noqa: D102
            # pylint: disable = missing-docstring
            super().reset()
            self._clear_buffers()

        def _clear_buffers(self):
            self.buffers = {}
            for buf, _ in self.BUFFERS.items():
                if buf in self.buf_ignore:
                    continue
                self.buffers[buf] = TreeMultiMap()

        def _clear_ltm_buffers(self):
            self.buffers['query'].clear()
            self.buffers['retrieval'].clear()

        def start_new_episode(self): # noqa: D102
            # pylint: disable = missing-docstring
            super().start_new_episode()
            self._clear_buffers()
            self._sync_input_buffers()
            self.internal_action_count = 0

        def get_actions(self): # noqa: D102
            # pylint: disable = missing-docstring
            actions = super().get_actions()
            if actions == []:
                return actions
            actions = set(actions)
            allow_internal_actions = (
                self.max_internal_actions is None
                or self.internal_action_count < self.max_internal_actions
            )
            if allow_internal_actions:
                actions.update(self._generate_copy_actions())
                actions.update(self._generate_delete_actions())
                actions.update(self._generate_retrieve_actions())
                actions.update(self._generate_cursor_actions())
            return sorted(actions)

        def _generate_copy_actions(self):
            actions = []
            for src_buf, src_props in self.BUFFERS.items():
                if src_buf in self.buf_ignore or not src_props.copyable:
                    continue
                for attr in self.buffers[src_buf]:
                    for dst_buf, dst_prop in self.BUFFERS.items():
                        copyable = (
                            src_buf != dst_buf
                            and dst_buf not in self.buf_ignore
                            and dst_prop.writable
                            and not (src_buf == 'perceptual' and dst_buf == 'scratch')
                            and self.buffers[src_buf][attr] != self.buffers[dst_buf].get(attr, None)
                        )
                        if not copyable:
                            continue
                        actions.append(Action(
                            'copy',
                            src_buf=src_buf,
                            src_attr=attr,
                            dst_buf=dst_buf,
                            dst_attr=attr,
                        ))
            return actions

        def _generate_delete_actions(self):
            actions = []
            for buf, prop in self.BUFFERS.items():
                if buf in self.buf_ignore or not prop.writable:
                    continue
                for attr in self.buffers[buf]:
                    actions.append(Action(
                        'delete',
                        buf=buf,
                        attr=attr,
                    ))
            return actions

        def _generate_retrieve_actions(self):
            actions = []
            for buf, buf_props in self.BUFFERS.items():
                if buf in self.buf_ignore or not buf_props.copyable:
                    continue
                for attr, value in self.buffers[buf].items():
                    if self.knowledge_store.retrievable(value):
                        actions.append(Action('retrieve', buf=buf, attr=attr))
            return actions

        def _generate_cursor_actions(self):
            actions = []
            if self.buffers['retrieval']:
                if self.knowledge_store.has_prev_result:
                    actions.append(Action('prev-result'))
                if self.knowledge_store.has_next_result:
                    actions.append(Action('next-result'))
            return actions

        def react(self, action): # noqa: D102
            # pylint: disable = missing-docstring
            # handle internal actions and update internal buffers
            assert action in self.get_actions(), f'{action} not in {self.get_actions()}'
            external_action = self._process_internal_actions(action)
            if external_action:
                reward = super().react(action)
                self.internal_action_count = 0
            else:
                reward = self.internal_reward
                self.internal_action_count += 1
            self._sync_input_buffers()
            return reward

        def _process_internal_actions(self, action):
            """Process internal actions, if appropriate.

            Arguments:
                action (Action): The action, which may or may not be internal.

            Returns:
                bool: Whether the action was external.
            """
            if action.name == 'copy':
                val = self.buffers[action.src_buf][action.src_attr]
                self.buffers[action.dst_buf][action.dst_attr] = val
                if action.dst_buf == 'query':
                    self._query_ltm()
            elif action.name == 'delete':
                del self.buffers[action.buf][action.attr]
                if action.buf == 'query':
                    self._query_ltm()
            elif action.name == 'retrieve':
                result = self.knowledge_store.retrieve(self.buffers[action.buf][action.attr])
                self.buffers['query'].clear()
                if result is None:
                    self.buffers['retrieval'].clear()
                else:
                    self.buffers['retrieval'] = result
            elif action.name == 'prev-result':
                self.buffers['retrieval'] = self.knowledge_store.prev_result()
            elif action.name == 'next-result':
                self.buffers['retrieval'] = self.knowledge_store.next_result()
            else:
                return True
            return False

        def _query_ltm(self):
            if not self.buffers['query']:
                self.buffers['retrieval'].clear()
                return
            result = self.knowledge_store.query(self.buffers['query'])
            if result is None:
                self.buffers['retrieval'].clear()
            else:
                self.buffers['retrieval'] = result

        def _sync_input_buffers(self):
            # update input buffers
            self.buffers['perceptual'] = super().get_observation()

        def add_to_ltm(self, **kwargs):
            """Add a memory element to long-term memory.

            Arguments:
                **kwargs: The key-value pairs of the memory element.
            """
            self.knowledge_store.store(**kwargs)

    return MemoryArchitectureMetaEnvironment


class KnowledgeStore:
    """Generic interface to a knowledge base."""

    def clear(self):
        """Remove all knowledge from the KB."""
        raise NotImplementedError()

    def store(self, time_stamp, mem_id=None, **kwargs):
        """Add knowledge to the KB.

        Arguments:
            mem_id (any): The ID of the element. Defaults to None.
            **kwargs: Attributes and values of the element to add.

        Returns:
            bool: True if the add was successful.
        """
        raise NotImplementedError()

    def retrieve(self, mem_id):
        """Retrieve the element with the given ID.

        Arguments:
            mem_id (any): The ID of the desired element.

        Returns:
            TreeMultiMap: The desired element, or None.
        """
        raise NotImplementedError()

    def query(self, attr_vals):
        """Search the KB for elements with the given attributes.

        Arguments:
            attr_vals (Mapping[str, Any]): Attributes and values of the desired element.

        Returns:
            TreeMultiMap: A search result, or None.
        """
        raise NotImplementedError()

    @property
    def has_prev_result(self):
        """Determine if a previous query result is available.

        Returns:
            bool: True if there is a previous result.
        """
        raise NotImplementedError()

    def prev_result(self):
        """Get the prev element that matches the most recent search.

        Returns:
            TreeMultiMap: A search result, or None.
        """
        raise NotImplementedError()

    @property
    def has_next_result(self):
        """Determine if a next query result is available.

        Returns:
            bool: True if there is a next result.
        """
        raise NotImplementedError()

    def next_result(self):
        """Get the next element that matches the most recent search.

        Returns:
            TreeMultiMap: A search result, or None.
        """
        raise NotImplementedError()

    @staticmethod
    def retrievable(mem_id):
        """Determine if an object is a retrievable memory ID.

        Arguments:
            mem_id (any): The object to check.

        Returns:
            bool: True if the object is a retrievable memory ID.
        """
        raise NotImplementedError()


class NaiveDictKB(KnowledgeStore):
    """A list-of-dictionary implementation of a knowledge store."""

    def __init__(self):
        """Initialize the NaiveDictKB."""
        self.knowledge = []
        self.query_index = None
        self.query_matches = []

    def clear(self): # noqa: D102
        self.knowledge = []
        self.query_index = None
        self.query_matches = []

    def store(self, mem_id=None, **kwargs): # noqa: D102
        self.knowledge.append(TreeMultiMap(**kwargs))
        return True

    def retrieve(self, mem_id): # noqa: D102
        raise NotImplementedError()

    def query(self, attr_vals): # noqa: D102
        candidates = []
        for candidate in self.knowledge:
            match = all(
                attr in candidate and candidate[attr] == val
                for attr, val in attr_vals.items()
            )
            if match:
                candidates.append(candidate)
        if candidates:
            # if the current retrieved item still matches the new query
            # leave it there but update the cached matches and index
            if self.query_index is not None:
                curr_retrieved = self.query_matches[self.query_index]
            else:
                curr_retrieved = None
            self.query_matches = sorted(candidates)
            # use the ValueError from list.index() to determine if the query still matches
            try:
                self.query_index = self.query_matches.index(curr_retrieved)
            except ValueError:
                self.query_index = 0
            return self.query_matches[self.query_index]
        self.query_index = None
        self.query_matches = []
        return None

    @property
    def has_prev_result(self): # noqa: D102
        return True

    def prev_result(self): # noqa: D102
        self.query_index = (self.query_index - 1) % len(self.query_matches)
        return self.query_matches[self.query_index]

    @property
    def has_next_result(self): # noqa: D102
        return True

    def next_result(self): # noqa: D102
        self.query_index = (self.query_index + 1) % len(self.query_matches)
        return self.query_matches[self.query_index]

    @staticmethod
    def retrievable(mem_id): # noqa: D102
        return False


class NetworkXKB(KnowledgeStore):
    """A NetworkX implementation of a knowledge store."""

    def __init__(self, activation_class=None):
        """Initialize the NetworkXKB."""
        # parameters
        if activation_class is None:
            activation_fn = (lambda graph, mem_id: None)
        self.activation_class = activation_class
        self.activation_fn = activation_class.activate
        # variables
        self.graph = MultiDiGraph()
        self.inverted_index = defaultdict(set)
        self.query_results = None
        self.result_index = None
        self.clear()

    def clear(self): # noqa: D102
        self.graph.clear()
        self.inverted_index.clear()
        self.query_results = None
        self.result_index = None

    def get_activation(self, mem_id, current_time):
        # returning activation number using time stamp list ????
        total_act = 0
        # print(mem_id)
        for (time_stamp, scale_factor) in self.graph.nodes[mem_id]['activation']:
            time_since = current_time - time_stamp
            if time_since == 0: # time_since approaches zero
                total_act = total_act + scale_factor * (0.000000000001**(self.activation_class.decay_rate))
            else:
                total_act = total_act + scale_factor * (time_since**(self.activation_class.decay_rate))
        #print(total_act)
        return total_act

    def store(self, time_stamp, backlinks, mem_id=None,  **kwargs): # noqa: D102
        if mem_id is None:
            mem_id = uuid()
        if mem_id not in self.graph: # create node and attributes if needed
            self.graph.add_node(mem_id, activation=[])
        for attribute, value in kwargs.items():
            if value not in self.graph:
                self.graph.add_node(value, activation=[])
            self.graph.add_edge(mem_id, value, attribute=attribute)
            if backlinks:
                self.graph.add_edge(value, mem_id, attribute='backlink_from_' + value + '_to_' + mem_id)
            # FIXME what does inverted_index mean
            self.inverted_index[attribute].add(mem_id)
        # activate node, spread
        self.activation_fn(self.graph, mem_id, time_stamp)
        return True

    def _activate_and_return(self, time_stamp, mem_id):
        self.activation_fn(self.graph, mem_id, time_stamp)
        result = TreeMultiMap()
        for _, value, data in self.graph.out_edges(mem_id, data=True):
            result.add(data['attribute'], value)
        return result

    def retrieve(self, time_stamp, mem_id): # noqa: D102
        if mem_id not in self.graph:
            return None
        return self._activate_and_return(time_stamp, mem_id)

    def query(self, time_stamp, attr_vals): # noqa: D102
        # first pass: get candidates with all the attributes
        candidates = set.intersection(*(
            self.inverted_index[attribute] for attribute in attr_vals.keys()
        ))
        # second pass: get candidates with the correct values
        candidates = set(
            candidate for candidate in candidates
            if all((
                (candidate, value) in self.graph.edges
                and self.graph.get_edge_data(candidate, value)[0]['attribute'] == attribute
            ) for attribute, value in attr_vals.items())
        )
        # quit early if there are no results
        if not candidates:
            self.query_results = None
            self.result_index = None
            return None
        # final pass: sort results by activation
        self.query_results = sorted(          # do we need to use our get activation function here? jk we did woo
            candidates,
            key=(lambda mem_id: self.get_activation(mem_id, time_stamp)),
            reverse=True,
        )
        self.result_index = 0
        return self._activate_and_return(time_stamp, self.query_results[self.result_index])

    @property
    def has_prev_result(self): # noqa: D102
        return (
            self.query_results is not None
            and self.result_index > 0
        )

    def prev_result(self, time_stamp): # noqa: D102
        self.result_index -= 1
        return self._activate_and_return(time_stamp, self.query_results[self.result_index])

    @property
    def has_next_result(self): # noqa: D102
        return (
            self.query_results is not None
            and self.result_index < len(self.query_results) - 1
        )

    def next_result(self, time_stamp): # noqa: D102
        self.result_index += 1
        return self._activate_and_return(time_stamp, self.query_results[self.result_index])

    @staticmethod
    def retrievable(mem_id): # noqa: D102
        return isinstance(mem_id, Hashable)


class SparqlKB(KnowledgeStore):
    """An adaptor for RL agents to use KnowledgeSources."""

    # FIXME arguably this should be abstracted and moved to KnowledgeStore
    Augment = namedtuple('Augment', 'old_attrs, transform')

    BAD_VALUES = set([
        '"NAN"^^<http://www.w3.org/2001/XMLSchema#double>',
        '"NAN"^^<http://www.w3.org/2001/XMLSchema#float>',
    ])

    def __init__(self, knowledge_source, augments=None):
        """Initialize a SparqlKB.

        Arguments:
            knowledge_source (KnowledgeSource): A SPARQL knowledge source.
            augments (Sequence[Augment]): Additional values to add to results.
        """
        # parameters
        self.source = knowledge_source
        if augments is None:
            augments = []
        self.augments = list(augments)
        # variables
        self.prev_query = None
        self.query_offset = 0
        # cache
        self.retrieve_cache = {}
        self.query_cache = {}

    def clear(self): # noqa: D102
        raise NotImplementedError()

    def store(self, mem_id=None, **kwargs): # noqa: D102
        raise NotImplementedError()



    def retrieve(self, mem_id): # noqa: D102
        valid_mem_id = (
            isinstance(mem_id, str)
            and mem_id.startswith('<http')
            and mem_id.endswith('>')
        )
        if not valid_mem_id:
            raise ValueError(
                f'mem_id should be a str of the form "<http:.*>", '
                f'but got: {mem_id}'
            )
        if mem_id not in self.retrieve_cache:
            result = self._true_retrieve(mem_id)
            for augment in self.augments:
                if all(attr in result for attr in augment.old_attrs):
                    new_prop_val = augment.transform(result)
                    if new_prop_val is not None:
                        new_prop, new_val = new_prop_val
                        result[new_prop] = new_val
            self.retrieve_cache[mem_id] = TreeMultiMap.from_dict(result)
        result = self.retrieve_cache[mem_id]
        self.prev_query = None
        self.query_offset = 0
        return result

    def _true_retrieve(self, mem_id):
        query = f'''
        SELECT DISTINCT ?attr ?value WHERE {{
            {mem_id} ?attr ?value .
        }}
        '''
        results = self.source.query_sparql(query)
        # FIXME HACK to avoid dealing with multi-valued attributes,
        # we only return the "largest" value for each attribute
        result = defaultdict(set)
        for binding in results:
            val = binding['value'].rdf_format
            if val in self.BAD_VALUES:
                continue
            result[binding['attr'].rdf_format].add(val)
        return {attr: max(vals) for attr, vals in result.items()}

    def query(self, attr_vals): # noqa: D102
        query_terms = tuple((k, v) for k, v in sorted(attr_vals.items()))
        if query_terms not in self.query_cache:
            mem_id = self._true_query(attr_vals)
            self.query_cache[query_terms] = mem_id
        mem_id = self.query_cache[query_terms]
        self.query_offset = 0
        if mem_id is None:
            self.prev_query = None
            return TreeMultiMap()
        else:
            self.prev_query = attr_vals
            return self.retrieve(mem_id)

    def _true_query(self, attr_vals, offset=0):
        condition = ' ; '.join(
            f'{attr} {val}' for attr, val in attr_vals.items()
        )
        query = f'''
        SELECT DISTINCT ?concept WHERE {{
            ?concept {condition} ;
                     <http://xmlns.com/foaf/0.1/name> ?__name__ .
        }} ORDER BY ?__name__ LIMIT 1 OFFSET {offset}
        '''
        results = self.source.query_sparql(query)
        try:
            return next(iter(results))['concept'].rdf_format
        except StopIteration:
            return None

    @property
    def has_prev_result(self): # noqa: D102
        return self.prev_query is not None and self.query_offset > 0

    def prev_result(self): # noqa: D102
        if not self.has_prev_result:
            return None
        self.query_offset -= 1
        return self._true_query(self.prev_query, offset=self.query_offset)

    @property
    def has_next_result(self): # noqa: D102
        return self.prev_query is not None

    def next_result(self): # noqa: D102
        if not self.has_next_result:
            return None
        self.query_offset += 1
        return self._true_query(self.prev_query, offset=self.query_offset)

    @staticmethod
    def retrievable(mem_id): # noqa: D102
        return isinstance(mem_id, str) and mem_id.startswith('<http')

class Activation_Class:
    # FIXME will need to account for backlinks/not get stuck in loops
    def __init__(self, decay_rate, scale_factor, max_steps, capped):
        self.decay_rate = decay_rate
        self.scale_factor = scale_factor
        self.max_steps = max_steps
        self.capped = capped

    def _activate(self, visited, graph, mem_id, time_stamp, scale_factor, max_steps):
        # appends time stamp and scale factor
        graph.nodes[mem_id]['activation'].append((time_stamp, scale_factor))
        result = list(graph.successors(mem_id))

        # FIXME activation is very diluted according to this if we allow backlinks
        if self.capped and len(result) > 0:
            sharing = 1/len(result)
        else:
            sharing = 1
        for i in range(len(result)):
            if result[i] != mem_id and result[i] not in visited:
                # print('successor of ' + mem_id + " is " + result[i])
                # is sharing * scale_factor / 2 valid? ruth and bryce say yes
                visited.add(result[i])
                self._activate(visited, graph, result[i], time_stamp, sharing * scale_factor / 2, max_steps - 1)

    #FIXME add visited set that is passed into each recursive call and updated as we go along(!)
    def activate(self, graph, mem_id, time_stamp, scale_factor=None, max_steps=None):
        if max_steps == 0:
            return
        if scale_factor is None:
            scale_factor = self.scale_factor
        if max_steps is None:
            max_steps = self.max_steps
        visited = {mem_id}
        self._activate(visited, graph, mem_id, time_stamp, scale_factor, max_steps)


