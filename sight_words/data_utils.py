"""Utils for working with data files"""
import dataclasses
from typing import Dict
import pathlib
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
            datum = data_rep.SightWordDatum(
                grade=grade,
                successes=past_grade_success_incr * (max_grade - grade)
                + PRIOR_SUCCESSES,
                failures=PRIOR_FAILURES,
            )
            data_set[word] = datum
    return data_set


def save_dataset(file_path: pathlib.Path, dataset: Dict[str, data_rep.SightWordDatum]):
    """Save the dataset"""
    with file_path.open("w") as f:
        yaml.dump(dataset, f)


def load_dataset(file_path: pathlib.Path) -> Dict[str, data_rep.SightWordDatum]:
    """Save the dataset"""
    with file_path.open("r") as f:
        dataset = yaml.load(f, Loader=yaml.FullLoader)
    return dataset


def update_dataset(
    dataset: Dict[str, data_rep.SightWordDatum], word, successes=0, failures=0
) -> Dict[str, data_rep.SightWordDatum]:
    """Updates a dataset with new succeses/failures"""
    if word not in dataset:
        raise ValueError(f"Word {word} not in the dataset.")
    new_dataset = dataset.copy()
    old_data = dataset[word]
    new_data = dataclasses.replace(
        old_data,
        successes=old_data.successes + successes,
        failures=old_data.failures + failures,
    )
    new_dataset[word] = new_data
    return new_dataset
