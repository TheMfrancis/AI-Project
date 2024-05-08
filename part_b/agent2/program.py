# COMP30024 Artificial Intelligence, Semester 1 2024
# Project Part B: Game Playing Agent

from referee.game import PlayerColor, Action, PlaceAction, Coord
import random
import math
import numpy as np
from collections import defaultdict
from typing import List
from referee.game.actions import PlaceAction
from referee.game.coord import Coord
from .helper import BoardState

class MCTSTreeNode:
    def __init__(self, state, parent=None, parent_action=None, player_turn = None, opponent = None):
        self.state = state
        self.parent = parent
        self.parent_action = parent_action
        self.children = []
        self.visits = 0
        self._results = defaultdict(int)
        self._results[1] = 0
        self._results[-1] = 0
        self._player_turn = player_turn
        self._opponent = opponent
        self._untried_actions = self.untried_actions()
        self.legal_actions = self._untried_actions.copy()

    def untried_actions(self):
        self._untried_actions = self.state.get_legal_actions()
        return self._untried_actions
    
    def q(self):
        wins = self._results[1]
        loses = self._results[-1]
        return wins - loses
    def n(self):
        return self.visits
    
    def expand(self):
        action = self._untried_actions.pop()
        #print("before = ",self.state.board)
        next_state = self.state.perform_action(action)
        #print("after = ",next_state.board)
        #print("newturn ",next_state.turn)
        child_node = MCTSTreeNode(next_state, parent=self, parent_action=action,player_turn=next_state.turn)
        #print("hereeeeee",child_node.state.turn)
        self.children.append(child_node)
        return child_node 
    
    def rollout_policy(self, possible_moves):
        #print(possible_moves)
        return possible_moves[np.random.randint(len(possible_moves))]

    def rollout(self):
        current_rollout_state = self.state.clone()
        #print(current_rollout_state.board)
        #print(current_rollout_state.board)
        depth = 0
        while depth < 5: #not current_rollout_state.is_game_over() and:
            depth += 1
            possible_moves = current_rollout_state.get_legal_actions()
            if len(possible_moves) == 0:
                return -1
            #print(current_rollout_state.board)
            action = self.rollout_policy(possible_moves)
            #print("action ",action)
            current_rollout_state = current_rollout_state.perform_action(action)
        #print("player_turn ",self._player_turn)
        #print("opponent ", self._opponent)
        return current_rollout_state.is_winning(1-self._player_turn)
    
#     def simulate_from_node(self, node, depth):
#         current_state = node.state.clone()
#         while not current_state.is_terminal() and depth < self.cutoff_depth:
#             action = random.choice(current_state.get_legal_actions())
#             current_state = current_state.perform_action(action)
#             depth += 1
#         return current_state.is_winning()
    def _tree_policy(self):

        current_node = self
        while len(current_node.legal_actions) != 0: #not current_node.is_terminal_node():
            
            if not current_node.is_fully_expanded():
                return current_node.expand()
            else:
                current_node = current_node.best_child()
        return current_node   
    
    def backpropagate(self, result):
        self.visits += 1.
        self._results[result] += 1.
        if self.parent:
            self.parent.backpropagate(result)

    def is_terminal_node(self):
        return self.state.is_game_over()
    
    def is_fully_expanded(self):
        return len(self._untried_actions) == 0

    def best_child(self, c_param=0.1):   
        choices_weights = [(c.q() / c.n()) + c_param * np.sqrt((2 * np.log(self.n()) / c.n())) for c in self.children]
        return self.children[np.argmax(choices_weights)]
    
    def best_action(self):
        simulation_no = 80
        for i in range(simulation_no): 
            v = self._tree_policy()
            reward = v.rollout()
            v.backpropagate(reward)
        return self.best_child()

    # def is_fully_expanded(self):
    #     return len(self.children) == len(self.state.get_legal_actions())

    # def select_child(self, exploration_factor=1.0):
    #     exploration_bonus = exploration_factor * math.sqrt(math.log(self.visits + 1) / (self.visits + 1e-6))
    #     best_child = max(self.children, key=lambda node: node.wins / (node.visits + 1e-6) + exploration_bonus)
    #     return best_child

    # def expand(self):
    #     legal_actions = self.state.get_legal_actions()
    #     action = random.choice(legal_actions)
    #     next_state = self.state.perform_action(action)
    #     new_node = MCTSTreeNode(next_state, parent=self)
    #     self.children.append(new_node)
    #     return new_node

    # def backpropagate(self, result):
    #     self.visits += 1
    #     self.wins += result
    #     if self.parent:
    #         self.parent.backpropagate(result)


# class MonteCarloTreeSearchAgent:
#     def __init__(self,exploration_factor,simulation_limit,cutoff_depth):
#         self.root = None
#         self.exploration_factor = exploration_factor
#         self.simulation_limit = simulation_limit
#         self.cutoff_depth = cutoff_depth  # Example cutoff depth

#     def action(self, initial_state, **referee: dict) -> PlaceAction:
#         if self.root is None:
#             self.root = MCTSTreeNode(initial_state)

#         for _ in range(self.simulation_limit):
#             node = self.select_node_to_expand()
#             result = self.simulate_from_node(node, depth=0)  # Pass depth=0 for initial depth
#             node.backpropagate(result)

#         best_action = self.select_best_action()
#         return best_action

#     def select_node_to_expand(self):
#         current_node = self.root
#         while not current_node.state.is_terminal() and current_node.is_fully_expanded():
#             current_node = current_node.select_child(self.exploration_factor)
#         return current_node

#     def simulate_from_node(self, node, depth):
#         current_state = node.state.clone()
#         while not current_state.is_terminal() and depth < self.cutoff_depth:
#             action = random.choice(current_state.get_legal_actions())
#             current_state = current_state.perform_action(action)
#             depth += 1
#         return current_state.is_winning()

#     def select_best_action(self):
#         best_child = max(self.root.children, key=lambda node: node.visits)
#         return best_child.state.last_action
class Agent:
    def __init__(self, color: PlayerColor, **referee: dict):
        self.turn = 1
        self._color = color
        self.numerical_color = None
        if(self._color == PlayerColor.RED):
            self.numerical_color = 0
        else:
            self.numerical_color = 1
        self.exploration_factor = 1
        self.simulation_limit = 100
        self.cutoff_depth = 2
        self.board = {Coord(3, 3): 0, 
                    Coord(3, 4): 0, 
                    Coord(4, 3): 0,
                    Coord(4, 4): 0,
                    Coord(2, 3): 1,
                    Coord(2, 4): 1,
                    Coord(2, 5): 1, 
                    Coord(2, 6): 1}
        self.firstTurn = True
        match color:
            case PlayerColor.RED:
                print("Testing: I am playing as RED")
            case PlayerColor.BLUE:
                print("Testing: I am playing as BLUE")


    def action(self, **referee: dict) -> Action:
        c1 = input("c1: ").split(",")
        c2 = input("c2: ").split(",")
        c3 = input("c3: ").split(",")
        c4 = input("c4: ").split(",")
        c1r = int(c1[0])
        c1c = int(c1[1])
        c2r = int(c2[0])
        c2c = int(c2[1])
        c3r = int(c3[0])
        c3c = int(c3[1])
        c4r = int(c4[0])
        c4c = int(c4[1])
        return PlaceAction(Coord(c1r,c1c),Coord(c2r,c2c),Coord(c3r,c3c),Coord(c4r,c4c))
    
    
    def update_board(self,coordinates):
        min_r = min(c.r for c in coordinates)
        max_r = max(c.r for c in coordinates)
        min_c = min(c.c for c in coordinates)
        max_c = max(c.c for c in coordinates)
        coords_to_remove = set()
        for r in range(min_r, max_r + 1):
            non_empty_coords = []
            for c in range(11):
                if self.board.get(Coord(r,c)) != None:
                    non_empty_coords.append(Coord(r,c))
                else:
                    break
            if len(non_empty_coords) == 11:
                for coord in non_empty_coords:
                    coords_to_remove.add(coord)

        for c in range(min_c, max_c + 1):
            non_empty_coords = []
            for r in range(11):
                if self.board.get(Coord(r,c)) != None:
                    non_empty_coords.append(Coord(r,c))
                else:
                    break
            if len(non_empty_coords) == 11:
                for coord in non_empty_coords:
                    coords_to_remove.add(coord)
        for coord in coords_to_remove:
            self.board.pop(coord)

            
    def update(self, color: PlayerColor, action: Action, **referee: dict):
        """
        This method is called by the referee after an agent has taken their
        turn. You should use it to update the agent's internal game state. 
        """

        # There is only one action type, PlaceAction
        self.turn += 1
        place_action: PlaceAction = action
        c1, c2, c3, c4 = place_action.coords
        numeric_color = None
        if color == PlayerColor.RED:
            numeric_color = 0
        else:
            numeric_color = 1
        coordinates = [c1,c2,c3,c4]
        # min_r = min(c.r for c in coordinates)
        # max_r = max(c.r for c in coordinates)
        # min_c = min(c.c for c in coordinates)
        # max_c = max(c.c for c in coordinates)
        for coord in coordinates:
            self.board[coord] = numeric_color
        self.update_board(coordinates)
        # for r in range(min_r, max_r + 1):
        #     non_empty_coords = []
        #     for c in range(11):
        #         if self.board.get(Coord(r,c)) != None:
        #             non_empty_coords.append(Coord(r,c))
        #         else:
        #             break
        #     if len(non_empty_coords) == 11:
        #         for coord in non_empty_coords:
        #             self.board.pop(coord)

        # for c in range(min_c, max_c + 1):
        #     non_empty_coords = []
        #     for r in range(11):
        #         if self.board.get(Coord(r,c)) != None:
        #             non_empty_coords.append(Coord(r,c))
        #         else:
        #             break
        #     if len(non_empty_coords) == 11:
        #         for coord in non_empty_coords:
        #             self.board.pop(coord)
        
        
        #print(c1,c2,c3,c4)
        #print("after == ",self.board)
        
        #print
        # Here we are just printing out the PlaceAction coordinates for
        # demonstration purposes. You should replace this with your own logic
        # to update your agent's internal game state representation.
        print(f"Testing: {color} played PLACE action: {c1}, {c2}, {c3}, {c4}")


