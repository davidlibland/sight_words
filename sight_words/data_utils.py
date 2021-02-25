"""Utils for working with data files"""
import collections
import dataclasses
import random
import re
from typing import Dict
from typing import List
import pathlib

import nltk
import pkg_resources

import yaml

import sight_words.data_rep as data_rep

PRIOR_FAILURES = 0.5
PRIOR_SUCCESSES = 0.5


def load_sight_words():
    """Loads the sight words from the raw data"""
    full_path_str = pkg_resources.resource_filename(
        "sight_words", "data/sight_words.yml"
    )
    full_path = pathlib.Path(full_path_str)
    with full_path.open("r") as f:
        data = yaml.load(f, Loader=yaml.SafeLoader)
    return data


def build_new_dataset(
    max_grade: int, past_grade_success_incr: int = 1
) -> Dict[str, data_rep.SightWordDatum]:
    """Builds a new dataset of sight words"""
    sight_words = load_sight_words()
    data_set = {}
    for grade, words in sight_words.items():
        if grade > max_grade:
            # Skip grades above the max-grade
            continue
        for word in words:
            success = past_grade_success_incr * (max_grade - grade) + PRIOR_SUCCESSES
            datum = data_rep.SightWordDatum(
                grade=grade,
                log=[data_rep.Event(success=success, failure=PRIOR_FAILURES)],
            )
            data_set[word] = datum
    return data_set


def save_dataset(file_path: pathlib.Path, dataset: data_rep.DataSet):
    """Save the dataset"""
    with file_path.open("w") as f:
        yaml.dump(dataset, f)


def load_dataset(file_path: pathlib.Path) -> data_rep.DataSet:
    """Save the dataset"""
    with file_path.open("r") as f:
        dataset = yaml.load(f, Loader=yaml.FullLoader)
    return dataset


def update_dataset(
    dataset: data_rep.DataSet,
    successes=0,
    failures=0,
    spelling_word=None,
    reading_word=None,
) -> data_rep.DataSet:
    """Updates a dataset with new succeses/failures"""
    data_to_update = []
    if spelling_word:
        data_to_update.append((spelling_word, "spelling_words"))
    if reading_word:
        data_to_update.append((reading_word, "reading_words"))
    for word, attr in data_to_update:
        if word not in getattr(dataset, attr):
            raise ValueError(f"Word {word} not in the dataset.")
        new_words = getattr(dataset, attr).copy()
        old_data = getattr(dataset, attr)[word]
        log = old_data.log + [data_rep.Event(success=successes, failure=failures)]
        new_data = dataclasses.replace(old_data, log=log)
        new_words[word] = new_data
        return dataclasses.replace(dataset, **{attr: new_words})


def build_new_sentence_file(input_file, output_name, max_length=100):
    """Process a text file into a list of sentences."""
    with open(input_file) as f:
        text = re.sub(" +", " ", f.read().replace("\n", " "))
    nltk.download("punkt")
    sentences = nltk.sent_tokenize(text.encode("ascii", "ignore").decode())
    sentences = [
        s
        for s in sentences
        if s and len(s) < max_length and s[0] == s[0].upper() and " " in s
    ]

    # Now save the sentences
    output_file = pkg_resources.resource_filename(
        "sight_words", f"data/{output_name}.yml"
    )
    with open(output_file, "w") as f:
        yaml.dump(sentences, f)

    # Now save the index
    lookup_dict = _get_lookup_dict(sentences)
    output_file = pkg_resources.resource_filename(
        "sight_words", f"data/{output_name}_index.yml"
    )
    with open(output_file, "w") as f:
        yaml.dump(lookup_dict, f)


def _get_lookup_dict(sentences: List[str]) -> Dict[str, List[int]]:
    lookup_dict = collections.defaultdict(list)
    for i, sentence in enumerate(sentences):
        words = re.sub(r"[^\w\s]", "", sentence).split()
        words = {w.lower() for w in words}
        for word in words:
            lookup_dict[word].append(i)
    return {w: l for w, l in lookup_dict.items()}


@dataclasses.dataclass()
class SentenceIndex:
    sentences: List[str]
    index: Dict[str, int]

    def get_sentence(self, word) -> str:
        """Returns a sentence using that word"""
        ixs = self.index.get(word.lower(), [])
        if ixs:
            ix = random.choice(ixs)
            return self.sentences[ix]
        return ""


def get_indexed_sentences(name):
    """Loads the sight words from the raw data"""
    sentences_path = pkg_resources.resource_filename("sight_words", f"data/{name}.yml")
    full_path = pathlib.Path(sentences_path)
    with full_path.open("r") as f:
        sentences = yaml.load(f, Loader=yaml.SafeLoader)
    index_path = pkg_resources.resource_filename(
        "sight_words", f"data/{name}_index.yml"
    )
    full_path = pathlib.Path(index_path)
    with full_path.open("r") as f:
        index = yaml.load(f, Loader=yaml.SafeLoader)
    return SentenceIndex(sentences=sentences, index=index)
