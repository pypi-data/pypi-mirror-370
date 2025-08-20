import json

from enum import Enum


class KClassifier(Enum):
    BINARY = "binary"
    SVM = "svm"
    RANDOM_FOREST = "random_forest"
    LOGISTIC_REGRESSION = "logistic_regression"

    @classmethod
    def _get_class_options(cls) -> dict[str, str]:
        options = {
            e.name.replace("_", " ").title(): e.value for e in cls if isinstance(e.name, str) and e.name.isupper()
        }
        return options

    @classmethod
    def serialized(cls) -> str:
        options = KClassifier._get_class_options()
        return f"{KClassifier.__name__}:{json.dumps(options)}"

    def __str__(self) -> str:
        return self.serialized()
