#!/usr/bin/env python3

import sys
from datetime import datetime, date
from pathlib import Path

DIRECTORY = Path(__file__).resolve().parent
sys.path.insert(0, str(DIRECTORY))

# pylint: disable = wrong-import-position
from permspace import PermutationSpace

from research.knowledge_base import SparqlEndpoint
from research.pspace_run import parallel_main
from research.rl_core import train_and_evaluate
from research.rl_agents import epsilon_greedy, LinearQLearner
from research.rl_memory import memory_architecture, SparqlKB

from record_store import RecordStore, feature_extractor
from record_store import DATE_DECADE


def testing():
    agent = epsilon_greedy(LinearQLearner)(
        # Linear Q Learner
        learning_rate=0.1,
        discount_rate=0.9,
        feature_extractor=feature_extractor,
        # Epsilon Greedy
        exploration_rate=0.05,
        # Random Mixin
        random_seed=8675309,
    )
    env = memory_architecture(RecordStore)(
        # record store
        data_file='data/album_decade',
        num_albums=1000,
        # memory architecture
        max_internal_actions=5,
        knowledge_store=SparqlKB(
            SparqlEndpoint('http://162.233.132.179:8890/sparql'),
            augments=[DATE_DECADE],
        ),
        # Random Mixin
        random_seed=8675309,
    )
    for trial in range(1000):
        env.start_new_episode()
        step = 0
        total = 0
        while not env.end_of_episode():
            observation = env.get_observation()
            actions = env.get_actions()
            action = agent.act(observation, actions)
            reward = env.react(action)
            agent.observe_reward(observation, reward, actions=env.get_actions())
            step += 1
            total += reward
            if total < -100:
                break
        print(trial, total)
    env.start_new_episode()
    visited = set()
    for step in range(10):
        print(step)
        observation = env.get_observation()
        print(observation)
        if observation in visited:
            print('\n')
            print('Looped; quitting.\n')
            break
        elif env.end_of_episode():
            break
        print(feature_extractor(observation))
        actions = env.get_actions()
        for action in sorted(actions):
            print(action)
            print('    ', agent.get_value(env.get_observation(), action))
        action = agent.get_best_stored_action(env.get_observation(), actions=actions)
        print(action)
        env.react(action)
        print()


def get_results_dir(params):
    return Path(DIRECTORY, 'results', params.results_folder)


def run_main_experiment(params, agent):
    results_dir = get_results_dir(params)
    for transfer_num in range(params.num_transfers + 1):
        first_episode = transfer_num * params.num_episodes
        env = memory_architecture(RecordStore)(
            # record store
            data_file=params.data_file,
            num_albums=params.num_albums,
            # memory architecture
            max_internal_actions=params.max_internal_actions,
            knowledge_store=SparqlKB(
                SparqlEndpoint('http://162.233.132.179:8890/sparql'),
                augments=[DATE_DECADE],
            ),
            buf_ignore=['scratch'],
            # Random Mixin
            random_seed=(first_episode + params.random_seed),
        )
        trial_results = train_and_evaluate(
            env,
            agent,
            num_episodes=params.num_episodes,
            eval_frequency=params.eval_frequency,
            min_return=params.min_return,
        )
        episodes = range(
            first_episode,
            first_episode + params.num_episodes + params.eval_frequency // 2,
            params.eval_frequency,
        )
        data_file = results_dir.joinpath(params.uniqstr_ + '.csv')
        try:
            for episode, mean_return in zip(episodes, trial_results):
                with data_file.open('a') as fd:
                    fd.write(f'{datetime.now().isoformat("_")} {episode} {mean_return}\n')
        except ValueError as err:
            print('ERROR')
            print(err)
            with data_file.open('a') as fd:
                fd.write(str(err))
                fd.write('\n')
            break


def save_weights(params, agent):
    results_dir = get_results_dir(params)
    if not params.save_weights:
        return
    weights_file = results_dir.joinpath(filename + '.weights')
    with weights_file.open('w') as fd:
        for action, weights in agent.weights.items():
            fd.write(str(action))
            fd.write('\n')
            for feature, weight in weights.items():
                fd.write(f'    {feature} {weight}')
                fd.write('\n')


def run_experiment(params):
    agent = epsilon_greedy(LinearQLearner)(
        # Linear Q Learner
        learning_rate=0.1,
        discount_rate=0.9,
        feature_extractor=feature_extractor,
        # Epsilon Greedy
        exploration_rate=0.05,
        # Random Mixin
        random_seed=params.random_seed,
    )
    results_dir = get_results_dir(params)
    results_dir.mkdir(parents=True, exist_ok=True)
    run_main_experiment(params, agent)


PSPACE = PermutationSpace(
    ['random_seed', 'num_transfers', 'num_albums', 'max_internal_actions'],
    random_seed=[
        0.35746869278354254, 0.7368915891545381, 0.03439267552305503, 0.21913569678035283, 0.0664623502695384,
        0.53305059438797, 0.7405341747379695, 0.29303361447547216, 0.014835598224628765, 0.5731489218909421,
        0.7636381976146833, 0.35714236561930957, 0.5160608307412042, 0.7820994131649518, 0.31390169902962717,
        0.5400876377274924, 0.6525757873962879, 0.19218707681741432, 0.8670148169024791, 0.1790981637428084,
        0.9134217950356655, 0.040659298111523356, 0.06483438648885109, 0.43867544728173746, 0.4648996620113045,
        0.12592474382215701, 0.75692510690223, 0.09073875189436231, 0.3888019332434871, 0.023769648152276224,
        0.875555147892463, 0.8366393362290254, 0.5286188504870308, 0.34338492322440306, 0.661316883315625,
        0.729196739896136, 0.2112397121528542, 0.22586909337188776, 0.9702411834858093, 0.7004826619335851,
        0.39823445434135263, 0.7599284542986776, 0.5200829278658589, 0.9263527832114413, 0.16836668813041167,
        0.37993543222011084, 0.05646030607329311, 0.8380140269416136, 0.06850735156933208, 0.8509431330734283,
        0.7412794617644994, 0.2581948390155667, 0.730942481453577, 0.22603438819536303, 0.03423539666033948,
        0.302059151008751, 0.355906014056683, 0.08587605919951402, 0.5117755667491667, 0.8872689255632645,
        0.2912805392817581, 0.4129551853107706, 0.48796957175363065, 0.4007943172230767, 0.8605908670991194,
        0.24670183964853332, 0.16422009968131168, 0.7822393190331338, 0.9934975000705282, 0.06825588105012037,
        0.21311293630928718, 0.9234705997701798, 0.8326358654854799, 0.9071456994646435, 0.16481506944276747,
        0.8094178195801208, 0.5599773672976621, 0.411978414613525, 0.8196096292357119, 0.7986699933718194,
        0.8028611631686207, 0.4945949995685762, 0.22196103928134492, 0.645337288567758, 0.6435668607690285,
        0.5490678941921603, 0.7304438695693786, 0.2603483323175092, 0.7318268751726856, 0.12479832683538916,
    ],
    num_episodes=10000,
    eval_frequency=100,
    num_albums=range(100, 1050, 100),
    max_internal_actions=range(1, 6),
    data_file='data/album_decade',
    results_folder=date.today().isoformat(),
    num_transfers=[1],
    min_return=-100,
    save_weights=False,
)
PSPACE.add_filter(lambda num_albums, max_internal_actions:
    num_albums == 100 or max_internal_actions == 1
)


def main():
    curr_file = Path(__file__).resolve()
    parallel_main(str(curr_file), f'{curr_file.stem}.PSPACE', f'{curr_file.stem}.run_experiment')


if __name__ == '__main__':
    main()
