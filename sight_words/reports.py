"""Utils to generate reports"""
import math
from typing import Dict
from typing import Mapping
from collections import OrderedDict


from sight_words import data_rep, ml


def marks_by_grade(dataset: Dict[str, data_rep.SightWordDatum]) -> Mapping[str, int]:
    """retrieve marks by grade"""
    params_by_grade = ml.get_beta_params_by_grade(dataset)
    marks_by_grade_dict = OrderedDict()
    for grade, params in sorted(params_by_grade.items(), reverse=True):
        mark = math.ceil(
            100
            * params[ml.SUCCESS_KEY]
            / (params[ml.SUCCESS_KEY] + params[ml.FAILURE_KEY])
        )
        grade_str = "K" if grade == 0 else str(grade)
        marks_by_grade_dict[grade_str] = mark
    return marks_by_grade_dict


def marks_by_word(dataset: Dict[str, data_rep.SightWordDatum]) -> Mapping[str, int]:
    """Retrieves the marks by word, sorted from lowest to highest"""
    marks = {word: math.ceil(100 * datum.score) for word, datum in dataset.items()}
    return OrderedDict(sorted(marks.items(), key=lambda x: x[1]))
