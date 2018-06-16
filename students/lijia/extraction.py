import sys
import time
import datetime
from collections import Counter, defaultdict
from os.path import dirname, realpath, join as join_path
from os import listdir
from os.path import isfile
from collections import namedtuple
import spacy
import numpy as np

from nltk.corpus import wordnet as wn
from nltk.wsd import lesk
from PyDictionary import PyDictionary
from research.knowledge_base import KnowledgeFile, URI

from ifai import *

# make sure research library code is available
ROOT_DIRECTORY = dirname(dirname(dirname(realpath(__file__))))
sys.path.insert(0, ROOT_DIRECTORY)
STORY_DIRECTORY = join_path(ROOT_DIRECTORY, 'data/fanfic_stories')
OUTPUT_DIR = join_path(ROOT_DIRECTORY, 'data/output')
NP_DIR = join_path(OUTPUT_DIR, "np")
VO_DIR = join_path(OUTPUT_DIR, "vo")
UMBEL_KB_PATH = join_path(ROOT_DIRECTORY, 'data/kbs/umbel-concepts-typology.rdfsqlite')

UMBEL = KnowledgeFile(UMBEL_KB_PATH)
DICTIONARY = PyDictionary()

# load nlp model
model = 'en_core_web_sm'
nlp = spacy.load(model)


def get_filename_from_folder(dir):
    "read a folder  that yield filename to read from inividual file"
    for filename in listdir(dir):
        if not filename.startswith("."):
            yield filename


def get_sentence_from_folder(dir, filename):
    """separate document to yield tokenized individual sentences"""
    for line in open(join_path(dir, filename), encoding='utf-8'):
        s_ls = line.replace("\"","").split(". ")
        for s in s_ls:
            yield nlp(s)


def is_stop_verb(token):
    return True if token.pos_ == "VERB" and token.is_stop else False


def is_subject_noun(token):
    return True if (token.pos_ == "NOUN" or token.pos_ == "PRON") and token.dep_ == "nsubj" else False


def is_good_obj(token):
    return True if token.dep_ == "dobj" and token.lemma_ != "…"  \
                   and token.tag_ != "WP" else False


def is_good_verb(token):
    return True if token.head.pos_ == "VERB" and not is_stop_verb(token.head) \
                   and not token.text.startswith('\'') else False


def replace_wsd(doc, token):
    return lesk(doc.text.split(), str(token))


def check_tool_pattern(doc):
    """extract tool from a few prescript patterns"""
    for token in doc:
        # use NP to V
        if token.lemma_ == "use":
            # extract object
            obj = [child.lemma_ for child in token.head.children if child.dep_ == "dobj"]
            if obj:
                if umbel_is_manipulable_noun(obj[0]) or wn_is_manipulable_noun(obj[0]):
                    for child in token.children:
                        # find "to" that compliment "use"
                        if child.dep_ == "xcomp" and [grandchild for grandchild in child.children if grandchild.text == "to"]:
                            return [token.lemma_, obj, "to", child.lemma_]

        # V NP with NP
        elif token.text == "with" and token.head.pos_ == "VERB":
            obj = [child.lemma_ for child in token.head.children if child.dep_ == "dobj"]
            for child in token.children:
                # find the preposition object and check manipulability
                if child.dep_ == "pobj" and (umbel_is_manipulable_noun(child.lemma_) or wn_is_manipulable_noun(child.lemma_)):
                    # it does not really matter weather object exist or not, the tool is the 'pobj'
                    if obj:
                        return [token.head.lemma_, obj[0], "with", child.lemma_]
                    else:
                        return [token.head.lemma_, "with", child.lemma_]


def extract_vo(doc):
    vo_ls = []
    for token in doc:
        if token.pos_ == "VERB" and is_good_verb(token):
            for child in token.children:
                if child.dep_ == "dobj" and is_good_obj(child):
                    vo_ls.append("%s\t%s\n" % (token.lemma_, child.lemma_))
    return vo_ls


def extract_sentence_phrase(doc):
    """extract phrases that are SVO or SV

        Argument:
        doc: processed sentences
    """

    # iterate through each word of the sentence
    results = []
    tools = []
    for token in doc:
        # token.tag_ != "WP" and
        if token.pos_ == "NOUN" and token.lemma_ != "-PRON-" and not token.ent_type_ == "PERSON" and \
                (wn_is_manipulable_noun(token.lemma_) or umbel_is_manipulable_noun(token.lemma_)):
            tools.append(token.lemma_)

        if is_subject_noun(token) and is_good_verb(token.head):
            # extract tool
            # extract np
            sentence_results = []

            # if the token is likely a person's name, replace it
            if token.ent_type_ == "PERSON":
                s = "-PRON-"
            else:
                s = token.lemma_
            v = token.head.lemma_

            for child in token.head.children:
                # direct objects
                if child.dep_ == "dobj":
                    sentence_results.append([s, v, child.lemma_])
                # indirect (proposition) objects
                elif child.dep_ == "prep":
                    for pobj in child.children:
                        sentence_results.append([s, v + " " + child.lemma_, str(pobj.lemma_)])

            # if the verb has neither direct nor indirect objects
            if not sentence_results:
                sentence_results.append([s, v])
            results.extend(sentence_results)

    return results, tools


def extract_sentence_np(doc):
    """extract the [adj + noun] from the given doc sentence"""
    results = []
    for token in doc:
        # attributive adjective
        if token.dep_ == "amod" and token.pos_ == "ADJ":

            # Example: "Two cute girls no more than eight years old stood in the centre of their friends"
            # should result in "funny" and "eight years old"
            # if the children is amod and adj and does not have any children
            # not a good idea b/c "the eight year old girl is cute and very funny."
            # if not [child for child in token.children if child.dep_ != "advmod"]:

            if token.head.pos_ == "NOUN":
                a = replace_wsd(doc, token)
                results.append("%s\t%s\n" % (token.lemma_, token.head.lemma_))

            for child in token.children:
                if child.dep_ == "conj":
                    results.append("%s\t%s\n" % (child.lemma_, token.head.lemma_))

        # predicative adjective
        elif token.dep_ == "acomp" \
                and not [child for child in token.children]:
            # to fight against counter example: "Olivia was sure of it." --> sure olivia

            for child in token.head.children:
                if child.dep_ == "nsubj":
                    results.append("%s\t%s\n" % (token.lemma_, child.lemma_))
    return results


def extract_pobj(doc):
    """extract prep + object from the given doc sentence"""
    results = []
    for token in doc:
        if token.dep_ == "prep":
            for child in token.children:
                if child.dep_ == "pobj":
                    results.append([token.lemma_, child.lemma_])
    return results


def calculate_stats(dir):
    """output a file with frequency of extraction from previously stored files"""
    def write_out():
        with open(join_path(OUTPUT_DIR, dir[-2:] + "_stat.txt"), 'w', encoding='utf-8') as f:
            for k in d:
                c = d[k]
                f.write("%s (%s)\n" % (k, sum(c.values())))
                for x in d[k]:
                    f.write("---%s (%s)\n" % (x, c[x]))

    file_gen = get_filename_from_folder(dir)
    d = defaultdict(Counter)
    for file in file_gen:
        lines = [line.rstrip('\n').replace('\t', ' ') for line in open(join_path(dir, file), 'r', encoding='utf-8')]
        # add to defaultdict with x as key and a counter as value
        # the counter counts y's appearance
        for line in lines:
            x = line.split(' ')[0]
            y = line.split(' ')[1]
            if d[x]:
                d[x].update([y])
            else:
                d[x] = Counter([y])
    write_out()
    return


def pipe():
    for file in get_filename_from_folder(STORY_DIRECTORY):
        print(file)
        file_name_vo = join_path(VO_DIR, file[:-4] + "_vo.txt")
        file_name_np = join_path(NP_DIR, file[:-4] + "_np.txt")
        # start extraction if the file does not exist yet
        if not (isfile(file_name_vo) and isfile(file_name_np)):
            with open(file_name_vo, 'w', encoding='utf-8') as vo_file, open(file_name_np, 'w', encoding='utf-8') as np_file:
                for s in get_sentence_from_folder(STORY_DIRECTORY, file):
                    # write verb + obj result
                    for vo in extract_vo(s):
                        if vo is not None:
                            vo_file.write(vo)
                    # write adj + noun result
                    for np in extract_sentence_np(s):
                        if np is not None:
                            np_file.write(np)
    calculate_stats(NP_DIR)
    calculate_stats(VO_DIR)


def test_svo(nlp):
    """adding test cases for extracting svo/sv"""
    TestCase = namedtuple('TestCase', ['sentence', 'phrase'])
    test_cases = [
        TestCase(
            "Ashley snorted earning another chorus of 'yeah's'.",
            ["Ashley", "snort"],
        ),
        TestCase(
            "We're not poor! The slightly taller blonde haired girl known as Olivia replied, her lips pursing in anger at the insult the other girl had thrown at not only her, but her Mom to.",
            ['lip', 'purse in', 'anger'],
        ),
        TestCase(
            "Ashley snorted earning another chorus of 'yeah's'.",
            ['ashley', 'snort'],
        ),
        TestCase(
            "They had been arguing since the start of recess, and what had initially started as a small altercation over a burst ball, had quickly degenerated into a full blow argument.",
            [],
        ),
        TestCase(
            "Rachel Berry thought that she would be upset for a long time after Jesse had broken up with her, breaking his heart.",
            [['-PRON-', 'think'], ['-PRON-', 'break with', '-PRON-']]
        ),
        TestCase(
            "She wasn't sure how long she could keep the visage up with them around; she needed practice with her peers first.",
            [] # todo: fill this up
        )
    ]
    for test_case in test_cases:
        message = [
            "Parsing sentence: " + test_case.sentence,
            "    but failed to see expected result: " + str(test_case.phrase),
        ]
        assert test_case.phrase in extract_sentence_phrase(nlp(test_case.sentence)), "\n".join(message)


def test_np(nlp):
    """test cases for extracting [adj + NOUN]"""
    TestCase = namedtuple('TestCase', ['sentence', 'phrase'])
    test_cases = [
        TestCase(
            "Olivia guessed that even Ashley's parents weren't that rich, they didn't live near the park or have a house that backed onto the forest and that house, well It was the biggest house in Lima, Olivia was sure of it.",
            ['big', 'house'],
        ),
    ]
    for test_case in test_cases:
        message = [
            "Parsing sentence: " + test_case.sentence,
            "    but failed to see expected result: " + str(test_case.phrase),
        ]
        assert test_case.phrase in extract_sentence_phrase(nlp(test_case.sentence)), "\n".join(message)


def main():
    start = time.time()
    pipe()
    end = time.time()
    print("total time cost %s" % datetime.timedelta(seconds= (end - start)))


if __name__ == '__main__':
    main()