from dataclasses import dataclass
from typing import Any
import yaml


@dataclass
class YamlProblem:
    path: str
    problem: str

    def __str__(self) -> str:
        return f"{self.path}: {self.problem}"


def find_yaml_problems(
    data: Any, path: str = "", problems: list[YamlProblem] | None = None
) -> list[YamlProblem]:
    """
    Find any problems with the given data that would prevent it from being serialized to "standard"
    YAML, i.e. it's all dicts, lists, and primitives.

    Returns a list of YamlProblem instances, which will be empty if there are no problems.
    """
    if problems is None:
        problems = []
    if isinstance(data, (str, int, float, bool, type(None))):
        return problems
    elif isinstance(data, list):
        for i, item in enumerate(data):
            find_yaml_problems(item, f"{path}[{i}]", problems)
    elif isinstance(data, dict):
        for k, v in data.items():
            if not isinstance(k, str):
                problems.append(YamlProblem(path, f"Invalid dict key: {type(k).__name__}"))
                return problems
            find_yaml_problems(v, f"{path}.{k}", problems)
    else:
        problems.append(YamlProblem(path, f"Invalid type: {type(data).__name__}"))
    return problems


def ensure_yamlizable(data: Any, data_description: str) -> None:
    """
    Ensure that the given data is serializable to YAML without any non-standard tags. I.e. it's all
    dicts, lists, and primitives.

    Raises a TypeError with a very descriptive error message if the data is not serializable.
    """
    problems = find_yaml_problems(data)
    if problems:
        bad_yaml = yaml.dump(data)
        problems_str = " - " + "\n - ".join(str(p) for p in problems)
        raise TypeError(
            f"Failed to serialize {data_description} to safe YAML:\n\n{bad_yaml}\nProblems:\n{problems_str}"
        )
