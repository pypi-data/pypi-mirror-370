from typing import Dict, Tuple, List
import json


class DAG:
    def __init__(self, pairs: Dict[str, List[str]]) -> None:
        self.pairs = pairs

    @classmethod
    def from_pairs(cls, *args: Tuple[str, str]) -> "DAG":
        pairs = dict()
        for node, next_node in args:
            if node not in pairs:
                pairs[node] = []
            if next_node not in pairs[node]:
                pairs[node].append(next_node)
            if next_node not in pairs:
                pairs[next_node] = []

        return cls(pairs)

    def __len__(self) -> int:
        return len(self.pairs)

    @property
    def nodes(self) -> List[str]:
        return list(self.pairs.keys())

    @property
    def orphans(self) -> List[str]:
        """
        return nodes without parents
        """
        orphans = []
        for node in self.pairs:
            if not any(
                    node in next_nodes
                    for next_nodes in self.pairs.values()):
                orphans.append(node)
        return orphans

    def __getitem__(self, node: str) -> List[str]:
        if node in self.pairs:
            result = [node, ]
            for next_node in self.pairs[node]:
                result += self[next_node]
            return result
        else:
            return []

    def __setitem__(self, node: str, next_node: str) -> None:
        if node not in self.pairs:
            self.pairs[node] = []
        if next_node not in self.pairs[node]:
            self.pairs[node].append(next_node)
        if next_node not in self.pairs:
            self.pairs[next_node] = []

    def to_string(self) -> str:
        return json.dumps(self.pairs, indent=2)

    @classmethod
    def from_string(cls, string: str) -> "DAG":
        pairs = json.loads(string)
        return cls(pairs)
