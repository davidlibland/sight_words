"""Datastructures and (de)serialization"""
from typing import List
from typing import Dict
from typing import TYPE_CHECKING
import dataclasses

import yaml


if TYPE_CHECKING:
    # pydantic doesn't play well with type checkers.
    from dataclasses import dataclass
else:
    from pydantic.dataclasses import dataclass

DATASET_YAML_TAG = u"!Dataset"
DATUM_YAML_TAG = u"!SightWordDatum"
EVENT_YAML_TAG = u"!Event"

EVENT_WINDOW = 10


@dataclass(frozen=True)  # pylint: disable=used-before-assignment
class Event:
    """A practice event for a given word."""
    success: float
    failure: float

    @staticmethod
    def yaml_representer(dumper, data):
        """Represent an Event as yaml"""
        return dumper.represent_mapping(EVENT_YAML_TAG, dataclasses.asdict(data))

    @staticmethod
    def yaml_constructor(loader, node):
        """Construct an Event from yaml"""
        value = loader.construct_mapping(node, deep=True)
        return Event(**value)


@dataclass(frozen=True)  # pylint: disable=used-before-assignment
class SightWordDatum:
    """The data associated to a sight word: the grade, and practice events"""
    grade: int
    log: List[Event]

    @property
    def successes(self) -> float:
        """The number of successes in the last `EVENT_WINDOW` events"""
        return sum(event.success for event in self.log[-EVENT_WINDOW:])

    @property
    def failures(self) -> float:
        """The number of successes in the last `EVENT_WINDOW` events"""
        return sum(event.failure for event in self.log[-EVENT_WINDOW:])

    @staticmethod
    def yaml_representer(dumper, data):
        """Represent a SightWordDatum as yaml"""
        return dumper.represent_mapping(
            DATUM_YAML_TAG, {"grade": data.grade, "log": data.log}
        )

    @staticmethod
    def yaml_constructor(loader, node):
        """Construct a SightWordDatum from yaml"""
        value = loader.construct_mapping(node, deep=True)
        return SightWordDatum(**value)

    @property
    def score(self):
        """The score"""
        return self.successes / (self.successes + self.failures)


@dataclass(frozen=True)  # pylint: disable=used-before-assignment
class DataSet:
    """A dataset representing a child's performance on a list of words"""
    spelling_words: Dict[str, SightWordDatum]
    reading_words: Dict[str, SightWordDatum]
    text: List[str] = dataclasses.field(default_factory=lambda: ["p_and_p"])

    @staticmethod
    def yaml_representer(dumper, data):
        """Represent a dataset as yaml"""
        return dumper.represent_mapping(
            DATASET_YAML_TAG,
            {
                "spelling_words": data.spelling_words,
                "reading_words": data.reading_words,
                "text": data.text,
            },
        )

    @staticmethod
    def yaml_constructor(loader, node):
        """Construct a DataSet from yaml"""
        value = loader.construct_mapping(node, deep=True)
        return DataSet(**value)


yaml.add_representer(Event, Event.yaml_representer)
yaml.add_constructor(EVENT_YAML_TAG, Event.yaml_constructor)

yaml.add_representer(SightWordDatum, SightWordDatum.yaml_representer)
yaml.add_constructor(DATUM_YAML_TAG, SightWordDatum.yaml_constructor)

yaml.add_representer(DataSet, DataSet.yaml_representer)
yaml.add_constructor(DATASET_YAML_TAG, DataSet.yaml_constructor)
