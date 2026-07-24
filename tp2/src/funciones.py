from dataclasses import dataclass
from typing import List


@dataclass
class Item:
    id: int
    volume: float = 0.0
    weight: float = 0.0
    value: float = 0.0

    def ratio(self, dimension: str) -> float:
        capacity = getattr(self, dimension, 0)
        return self.value / capacity if capacity else 0.0

    def __repr__(self) -> str:
        return f"Item(id={self.id}, volume={self.volume}, weight={self.weight}, value={self.value})"


@dataclass
class KnapsackSolution:
    items: List[Item]
    total_volume: float
    total_weight: float
    total_value: float

    def item_ids(self) -> List[int]:
        return [item.id for item in self.items]

    def item_labels(self) -> str:
        return ", ".join(str(item.id) for item in self.items) or "ninguno"

    def __repr__(self) -> str:
        return (
            f"KnapsackSolution(items={self.item_ids()}, total_volume={self.total_volume}, "
            f"total_weight={self.total_weight}, total_value={self.total_value})"
        )


class KnapsackProblem:
    def __init__(self, items: List[Item], capacity: float, capacity_dimension: str = "volume"):
        self.items = items
        self.capacity = capacity
        self.capacity_dimension = capacity_dimension

    def capacity_for(self, item: Item) -> float:
        return getattr(item, self.capacity_dimension, 0.0)

    def evaluate(self, selected_items: List[Item]) -> KnapsackSolution:
        total_volume = sum(item.volume for item in selected_items)
        total_weight = sum(item.weight for item in selected_items)
        total_value = sum(item.value for item in selected_items)
        return KnapsackSolution(selected_items, total_volume, total_weight, total_value)

    def is_feasible(self, solution: KnapsackSolution) -> bool:
        current_capacity = getattr(solution, f"total_{self.capacity_dimension}")
        return current_capacity <= self.capacity

    def all_solutions(self) -> List[KnapsackSolution]:
        solutions: List[KnapsackSolution] = []
        n = len(self.items)
        for mask in range(1 << n):
            selected = [self.items[i] for i in range(n) if (mask >> i) & 1]
            solutions.append(self.evaluate(selected))
        return sorted(solutions, key=lambda s: s.total_value, reverse=True)

    def best_exhaustive_solution(self) -> KnapsackSolution:
        feasible_solutions = [sol for sol in self.all_solutions() if self.is_feasible(sol)]
        return feasible_solutions[0] if feasible_solutions else KnapsackSolution([], 0.0, 0.0, 0.0)

    def greedy_solution(self) -> KnapsackSolution:
        sorted_items = sorted(self.items, key=lambda item: item.ratio(self.capacity_dimension), reverse=True)
        chosen: List[Item] = []
        used_capacity = 0.0
        for item in sorted_items:
            item_capacity = self.capacity_for(item)
            if used_capacity + item_capacity <= self.capacity:
                chosen.append(item)
                used_capacity += item_capacity
        return self.evaluate(chosen)


def build_items_from_table(table: List[List[float]], start_id: int = 1) -> List[Item]:
    return [Item(id=i + start_id, volume=row[0], value=row[1]) for i, row in enumerate(table)]


def build_weight_items(weights: List[float], values: List[float], start_id: int = 1) -> List[Item]:
    return [Item(id=i + start_id, weight=weights[i], value=values[i]) for i in range(len(weights))]
