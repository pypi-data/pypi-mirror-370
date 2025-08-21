# Dependency (const_types) enumeration mapping
from typing import Dict, List, Tuple, TypedDict, Union

from numpy import dtype, float64
from numpy.typing import NDArray

from fc_value import FCValue


DEPENDENCY_TYPES: Dict[int, str] = {
    0: "CONSTANT",
    1: "TABULAR_X",
    2: "TABULAR_Y",
    3: "TABULAR_Z",
    4: "TABULAR_TIME",
    5: "TABULAR_TEMPERATURE",
    6: "FORMULA",
    7: "TABULAR_FREQUENCY",
    8: "TABULAR_STRAIN",
    10: "TABULAR_ELEMENT_ID",
    11: "TABULAR_NODE_ID",
    12: "TABULAR_MODE_ID",
}

DEPENDENCY_TYPES_R: Dict[str, int] = {v: k for k, v in DEPENDENCY_TYPES.items()}


class FCDependencyColumn:
    type: str  # Форма задания зависимости - значение из DEPENDENCY_TYPES
    value: FCValue

    def __init__(self, type: str, value: FCValue):
        self.type = type
        self.value = value


class FCData:
    """
    Определяет зависимость свойства от внешних факторов (температура, координаты, etc.).
    """
    type: Union[int, str] # -1 - таблица, иное число - константа

    value: FCValue  # Данные для зависимости (e.g., массив ID узлов)
    table: List[FCDependencyColumn]

    def __init__(self, data: str, dep_type: Union[List[int], int, str], dep_data: Union[List[str], str]):

        if isinstance(dep_type, list) and isinstance(dep_data, list):
            self.value = FCValue(data, dtype(float64))
            self.type = -1
            self.table = [FCDependencyColumn(
                type = DEPENDENCY_TYPES[deps_type],
                value = FCValue(dep_data[j], dtype(float64))
            ) for j, deps_type in enumerate(dep_type)]

        elif (isinstance(dep_type, int) or isinstance(dep_type, str)) and isinstance(dep_data, str):
            self.value = FCValue(data, dtype(float64), 'formula' if dep_type == 6 else 'array')
            self.type = dep_type
            self.table = []
        else:
            raise ValueError("Invalid dependency data")

    def dump(self) -> Union[Tuple[str, List[int], List[str]], Tuple[str, Union[int, str], str]]:
        if self.type == -1:
            return self.value.dump(), [DEPENDENCY_TYPES_R[deps.type] for deps in self.table], [deps.value.dump() for deps in self.table]
        else:
            return self.value.dump(), self.type, ""

    def __len__(self):
        if not len(self.table):
            return 0
        return len(self.table[0].value)

