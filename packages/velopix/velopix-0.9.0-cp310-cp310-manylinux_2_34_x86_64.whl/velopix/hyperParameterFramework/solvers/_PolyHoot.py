from __future__ import annotations
from typing import List, Tuple, Optional
from dataclasses import dataclass
import numpy as np
from .._velopixTypes import pMap, pMapType, boundType
from .._optimizers import BaseOptimizer

@dataclass
class _HooNode:
    # Classic Node Properties
    bounds: np.ndarray
    depth: int
    parent_node: _HooNode | None  = None
    child_node_left: _HooNode | None = None 
    child_node_right: _HooNode | None = None 

    # Bandit specific node properties 
    number_of_visits: int = 0 
    mean_node_reward: float = 0.0
    upper_confidence: float = float("inf") 
    optimistic_subtree_value: float = float("inf")

    bound_action: np.ndarray | None = None

    def isLeafNode(self) -> bool:
        return self.child_node_left is None and self.child_node_right is None
    
    def midpointAction(self) -> np.ndarray:
        # Returns the midpoint of the Node 
        return (self.bounds[:, 0] + self.bounds[:, 1]) / 2
    
    def expandNode(self) -> Tuple[_HooNode, _HooNode]: 
        dimensions = self.bounds[:, 1] - self.bounds[:, 0]
        split_dimension = int(np.argmax(dimensions))
        midpoint = 0.5 * (self.bounds[split_dimension, 0] + self.bounds[split_dimension, 1])

        left_bounds = self.bounds.copy()
        right_bounds = self.bounds.copy()
        left_bounds[split_dimension, 1] = midpoint
        right_bounds[split_dimension, 0] = midpoint

        left_node = _HooNode(bounds=left_bounds, depth=self.depth + 1, parent_node=self)
        right_node = _HooNode(bounds=right_bounds, depth=self.depth + 1, parent_node=self)
        self.child_node_left, self.child_node_right = left_node, right_node
        return left_node, right_node
    
class HOOAgent:
    def __init__(self,
                 action_bounds: np.ndarray,
                 max_depth: int,
                 exploration_alpha: float,
                 polynomial_xi: float,
                 exploration_eta: float,
                 smoothness_scale: float,
                 smoothness_decay: float) -> None:
        self.root = _HooNode(bounds=np.array(action_bounds, dtype=float), depth=0)
        self.max_depth = max_depth

        self.exploration_alpha = float(exploration_alpha)
        self.polynomial_xi = float(polynomial_xi)
        self.exploration_eta = float(exploration_eta)

        self.smoothness_scale = float(smoothness_scale)
        self.smoothness_decay = float(smoothness_decay)

        self.plays: int = 0 
        self._last_path: List[_HooNode] = []

    def selectAction(self) -> Tuple[np.ndarray, list[_HooNode]]:
        current_node = self.root
        path = [current_node]

        while not current_node.isLeafNode():
            left_node: _HooNode = current_node.child_node_left # type: ignore # Suppress partialy known warning, since we know currentNode != leafNode we know it will have children
            right_node: _HooNode = current_node.child_node_right  # type: ignore 
            b_left = left_node.optimistic_subtree_value
            b_right = right_node.optimistic_subtree_value
            current_node = left_node if b_left >= b_right else right_node
            path.append(current_node)

        if current_node.depth < self.max_depth:
            if current_node.bound_action is None:
                current_node.bound_action = current_node.midpointAction()
            current_node.expandNode()
            action = current_node.bound_action
        else:
            if current_node.bound_action is None:
                current_node.bound_action = current_node.midpointAction()
            action = current_node.bound_action

        self._last_path = path
        return action.copy(), path         
    
    def updateBanditPolicy(self, observed_reward: float, path: Optional[List[_HooNode]] = None) -> None:
        if path is None:
            path = self._last_path
        
        self.plays += 1
        time_factor = self.plays ** (self.exploration_alpha / self.polynomial_xi) # Expo time decay

        # Update HOO Node params
        for node in path:
            node.number_of_visits += 1
            node.mean_node_reward += (observed_reward - node.mean_node_reward) / node.number_of_visits

            node.upper_confidence = node.mean_node_reward + (time_factor / (node.number_of_visits ** (self.exploration_eta - 1.0))) + self.smoothness_scale * (self.smoothness_decay ** node.depth)

        for node in reversed(path):
            if node.isLeafNode():
                node.optimistic_subtree_value = node.upper_confidence
            else:
                # I know this is not proper variable naming, but not sure what would be proper in this case 
                L = node.child_node_left.optimistic_subtree_value if node.child_node_left is not None else float("inf")
                R = node.child_node_right.optimistic_subtree_value if node.child_node_right is not None else float("inf")
                node.optimistic_subtree_value = min(node.upper_confidence, max(L, R))

    def greedyAction(self) -> np.ndarray:
        node: _HooNode = self.root
        while not node.isLeafNode():
            b_left = node.child_node_left.optimistic_subtree_value if node.child_node_left is not None else -float("inf")
            b_right = node.child_node_right.optimistic_subtree_value if node.child_node_right is not None else -float("inf")
            node = node.child_node_left if b_left >= b_right else node.child_node_right # type: ignore # we know that the node has child nodes since isLeafNode() check
        if node.bound_action is None:
            node.bound_action = node.midpointAction()
        return node.bound_action.copy()
    
class PolyHoot(BaseOptimizer):
    def __init__(
        self,
        *,
        objective: str = "min",
        auto_eval: dict[str, bool | list[float]] = {"autoEval": False, "nested": True, "weights": []},
        max_iterations: int = 100,
        hoo_max_depth: int = 8,
        exploration_alpha: float = 3.5,
        polynomial_xi: float = 16.0,
        exploration_eta: float = 0.75,
        smoothness_scale: float = 1.0,
        smoothness_decay: float = 0.5,
    ):
        super().__init__(objective=objective, auto_eval=auto_eval)
        self.max_iterations = int(max_iterations)
        self.current_iteration = 0

        self.hoo_max_depth = int(hoo_max_depth)
        self.exploration_alpha = float(exploration_alpha)
        self.polynomial_xi = float(polynomial_xi)
        self.exploration_eta = float(exploration_eta)
        self.smoothness_scale = float(smoothness_scale)
        self.smoothness_decay = float(smoothness_decay)

        self._numeric_keys: list[str] = []
        self._boolean_keys: list[str] = []
        self._action_bounds: np.ndarray | None = None
        self._agent: HOOAgent | None = None

        self._last_pmap: pMap | None = None

    def init(self) -> pMap:
        if not hasattr(self, "_algorithm"):
            raise RuntimeError("PolyHootPlanner.init() called before BaseOptimizer.start().")

        bounds_dict: boundType = self._algorithm.get_bounds()
        cfg_schema: pMapType = self._algorithm.get_config()

        self._numeric_keys = [k for k, (typ, _) in cfg_schema.items() if typ in (int, float)]
        self._boolean_keys = [k for k, (typ, _) in cfg_schema.items() if typ is bool]

        if len(self._numeric_keys) == 0:
            raise ValueError("PolyHootPlanner requires at least one numeric parameter to optimize.")

        action_bounds = []
        for key in self._numeric_keys:
            low, high = bounds_dict[key]  # type: ignore[assignment]
            action_bounds.append([float(low), float(high)]) # type: ignore[assignement]
        self._action_bounds = np.array(action_bounds, dtype=float)
        
        self._agent = HOOAgent(
            action_bounds=self._action_bounds,
            max_depth=self.hoo_max_depth,
            exploration_alpha=self.exploration_alpha,
            polynomial_xi=self.polynomial_xi,
            exploration_eta=self.exploration_eta,
            smoothness_scale=self.smoothness_scale,
            smoothness_decay=self.smoothness_decay,
        )

        # First suggestion
        pmap = self._vector_to_pmap(self._agent.selectAction()[0], bounds_dict, cfg_schema)
        self._last_pmap = pmap
        self.current_iteration = 1
        return pmap

    def next(self) -> pMap:
        self.current_iteration += 1
        if self._agent is None or self._action_bounds is None:
            raise RuntimeError("PolyHootPlanner.next() called before init().")

        if hasattr(self, "score_history") and len(self.score_history) > 0:  # type: ignore[attr-defined]
            last_score = self.score_history[-1]  # type: ignore[index]
            reward = -float(last_score) if self.objective == "min" else float(last_score)
            self._agent.updateBanditPolicy(reward)

        action, _path = self._agent.selectAction()
        bounds_dict: boundType = self._algorithm.get_bounds()
        cfg_schema: pMapType = self._algorithm.get_config()
        pmap = self._vector_to_pmap(action, bounds_dict, cfg_schema)
        self._last_pmap = pmap
        return pmap

    def is_finished(self) -> bool:
        return self.current_iteration >= self.max_iterations

    def _vector_to_pmap(
        self,
        action_vector: np.ndarray,
        bounds_dict: boundType,
        cfg_schema: pMapType,
    ) -> pMap:
        pmap: pMap = {}

        for i, key in enumerate(self._numeric_keys):
            low, high = bounds_dict[key]  # type: ignore[assignment]
            val = float(np.clip(action_vector[i], float(low), float(high))) # type: ignore[assignement]
            typ, _ = cfg_schema[key]
            if typ is int:
                pmap[key] = int(round(val))
            else:
                pmap[key] = float(val)

        for key in self._boolean_keys:
            default_bool: bool = False
            if key in bounds_dict and isinstance(bounds_dict[key], bool):
                default_bool = bool(bounds_dict[key])  # type: ignore[index]
            pmap[key] = default_bool

        return pmap