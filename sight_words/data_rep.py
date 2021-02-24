"""Datastructures and (de)serialization"""

import dataclasses

import yaml

YAML_TAG = u"!SightWordDatum"


@dataclasses.dataclass(frozen=True)
class SightWordDatum:
    grade: int
    successes: float
    failures: float

    @staticmethod
    def yaml_representer(dumper, data):
        return dumper.represent_mapping(YAML_TAG, dataclasses.asdict(data))

    @staticmethod
    def yaml_constructor(loader, node):
        value = loader.construct_mapping(node)
        return SightWordDatum(**value)


yaml.add_representer(SightWordDatum, SightWordDatum.yaml_representer)
yaml.add_constructor(YAML_TAG, SightWordDatum.yaml_constructor)
