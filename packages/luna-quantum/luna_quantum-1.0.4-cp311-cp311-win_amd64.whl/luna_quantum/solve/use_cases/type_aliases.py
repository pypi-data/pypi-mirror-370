Node = int | str

NestedDictGraph = dict[Node, dict[Node, dict[str, float]]]

NestedDictIntGraph = dict[int, dict[int, dict[str, float]]]

CalculusLiteral = tuple[int, bool]

Clause = tuple[CalculusLiteral, ...]
