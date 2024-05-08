import random
import math
from typing import List
from referee.game.actions import PlaceAction
from referee.game.coord import Coord

class MCTSTreeNode:
    def __init__(self, state: GameState, parent=None):
        self.state = state
        self.parent = parent
        self.children = []
        self.visits = 0
        self.wins = 0

    def is_fully_expanded(self):
        return len(self.children) == len(self.state.get_legal_actions())

    def select_child(self, exploration_factor=1.0):
        exploration_bonus = exploration_factor * math.sqrt(math.log(self.visits + 1) / (self.visits + 1e-6))
        best_child = max(self.children, key=lambda node: node.wins / (node.visits + 1e-6) + exploration_bonus)
        return best_child

    def expand(self):
        legal_actions = self.state.get_legal_actions()
        action = random.choice(legal_actions)
        next_state = self.state.perform_action(action)
        new_node = MCTSTreeNode(next_state, parent=self)
        self.children.append(new_node)
        return new_node

    def backpropagate(self, result):
        self.visits += 1
        self.wins += result
        if self.parent:
            self.parent.backpropagate(result)


class MonteCarloTreeSearchAgent:
    def __init__(self):
        self.root = None
        self.exploration_factor = 1.0
        self.simulation_limit = 1000

    def action(self, **referee: dict) -> Action:
        if self.root is None:
            self.root = MCTSTreeNode(initial_state)

        for _ in range(self.simulation_limit):
            node = self.select_node_to_expand()
            result = self.simulate_from_node(node)
            node.backpropagate(result)

        best_action = self.select_best_action()
        return best_action

    def select_node_to_expand(self):
        current_node = self.root
        while not current_node.state.is_terminal() and current_node.is_fully_expanded():
            current_node = current_node.select_child(self.exploration_factor)
        return current_node

    def simulate_from_node(self, node):
        current_state = node.state.clone()
        while not current_state.is_terminal():
            action = random.choice(current_state.get_legal_actions())
            current_state = current_state.perform_action(action)
        return current_state.get_result()

    def select_best_action(self):
        best_child = max(self.root.children, key=lambda node: node.visits)
        return best_child.state.last_action
