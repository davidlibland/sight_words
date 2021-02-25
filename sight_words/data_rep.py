"""Datastructures and (de)serialization"""
from typing import List
from typing import Dict
import dataclasses

import yaml

DATASET_YAML_TAG = u"!Dataset"
DATUM_YAML_TAG = u"!SightWordDatum"
EVENT_YAML_TAG = u"!Event"

EVENT_WINDOW = 10


@dataclasses.dataclass(frozen=True)
class Event:
    success: float
    failure: float

    @staticmethod
    def yaml_representer(dumper, data):
        return dumper.represent_mapping(EVENT_YAML_TAG, dataclasses.asdict(data))

    @staticmethod
    def yaml_constructor(loader, node):
        value = loader.construct_mapping(node)
        return Event(**value)


@dataclasses.dataclass(frozen=True)
class SightWordDatum:
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
        return dumper.represent_mapping(
            DATUM_YAML_TAG, {"grade": data.grade, "log": data.log}
        )

    @staticmethod
    def yaml_constructor(loader, node):
        value = loader.construct_mapping(node)
        return SightWordDatum(**value)

    @property
    def score(self):
        """The score"""
        return self.successes / (self.successes + self.failures)


@dataclasses.dataclass(frozen=True)
class DataSet:
    spelling_words: Dict[str, SightWordDatum]
    reading_words: Dict[str, SightWordDatum]
    text: str = "p_and_p"

    @staticmethod
    def yaml_representer(dumper, data):
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
        value = loader.construct_mapping(node)
        return DataSet(**value)


yaml.add_representer(Event, Event.yaml_representer)
yaml.add_constructor(EVENT_YAML_TAG, Event.yaml_constructor)

yaml.add_representer(SightWordDatum, SightWordDatum.yaml_representer)
yaml.add_constructor(DATUM_YAML_TAG, SightWordDatum.yaml_constructor)

yaml.add_representer(DataSet, DataSet.yaml_representer)
yaml.add_constructor(DATASET_YAML_TAG, DataSet.yaml_constructor)
