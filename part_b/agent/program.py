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
    def __init__(self, state, parent=None, parent_action=None, color = None, opponent_color = None,):
        self.state = state
        self.parent = parent
        self.parent_action = parent_action
        self.children = []
        self.visits = 0
        self.wins = 0
        self.color = color
        self.opponent_color = opponent_color
        self.untried_actions = self.get_untried_actions()
        self.legal_actions = self.untried_actions.copy()

    def get_untried_actions(self):
        self._untried_actions = self.state.get_legal_actions()
        return self._untried_actions
    
    # def q(self):
    #     wins = self._results[1]
    #     loses = self._results[-1]
    #     return wins - loses
    # def n(self):
    #     return self.visits
    
    def expand(self):
        action = self.untried_actions.pop(random.randrange(len(self.untried_actions)))
        #print("before = ",self.state.board)
        next_state = self.state.perform_action(action)
        #print("after = ",next_state.board)
        #print("newturn ",next_state.turn)
        child_node = MCTSTreeNode(next_state, parent=self, parent_action=action,color=self.opponent_color,opponent_color=self.color)
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
        depth_limit = None
        if self.color == PlayerColor.RED:
            depth_limit = 3
        else:
            depth_limit = 4
        depth = 0
        while depth < depth_limit: #not current_rollout_state.is_game_over() and:
            depth += 1
            possible_moves = current_rollout_state.get_legal_actions()
            if len(possible_moves) == 0:
                return current_rollout_state.opponent_color
            #print(current_rollout_state.board)
            action = self.rollout_policy(possible_moves)
            #print("action ",action)
            current_rollout_state = current_rollout_state.perform_action(action)
        #print("player_turn ",self._player_turn)
        #print("opponent ", self._opponent)
        winning_color = current_rollout_state.get_winning_color()
        return winning_color
    
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
        if self.color == result:
            self.wins += 1
        if self.parent:
            self.parent.backpropagate(result)

    # def is_terminal_node(self):
    #     return self.state.is_game_over()
    
    def is_fully_expanded(self):
        return len(self._untried_actions) == 0

    def best_child(self, c_param=0.1):   
        choices_weights = [(c.wins / c.visits) + c_param * np.sqrt((np.log(self.visits) / c.visits)) for c in self.children]
        return self.children[np.argmax(choices_weights)]
    
    def best_action(self):
        simulation_no = 50
        for _ in range(simulation_no): 
            v = self._tree_policy()
            reward = v.rollout()
            v.backpropagate(reward)
        best_index = 0
        best_visits = self.children[0].visits
        for i in range(len(self.children)):
            if self.children[i].visits > best_visits:
                best_visits = self.children[i].visits
                best_index = i
        return self.children[best_index]


def minimax_alpha_beta(state, depth, alpha, beta, maximizing_player):
    legal_actions = state.get_legal_actions()
    if depth == 0 or len(legal_actions) == 0:
        return state.evaluate_state(PlayerColor.RED,PlayerColor.BLUE)

    if maximizing_player:
        max_eval = -math.inf
        for action in legal_actions:
            next_state = state.perform_action(action)
            eval = minimax_alpha_beta(next_state, depth - 1, alpha, beta, False)
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = math.inf
        for action in legal_actions:
            next_state = state.perform_action(action)
            eval = minimax_alpha_beta(next_state, depth - 1, alpha, beta, True)
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval

def minimax_alpha_beta_decision(state, depth):
    best_action = None
    best_value = -math.inf
    alpha = -math.inf
    beta = math.inf
    legal_actions = state.get_legal_actions()
    print(len(legal_actions))
    for action in legal_actions:
        next_state = state.perform_action(action)
        value = minimax_alpha_beta(next_state, depth - 1, alpha, beta, False)
        if value > best_value:
            best_value = value
            best_action = action
        alpha = max(alpha, value)
    return best_action

class Agent:
    """
    This class is the "entry point" for your agent, providing an interface to
    respond to various Tetress game events.
    """

    def __init__(self, color: PlayerColor, **referee: dict):
        """
        This constructor method runs when the referee instantiates the agent.
        Any setup and/or precomputation should be done here.
        """
        self.turn = 1
        self.color = color
        self.opponent_color = None
        if color == PlayerColor.RED.value:
            self.opponent_color = PlayerColor.BLUE
        else:
            self.opponent_color = PlayerColor.RED
        self.numerical_color = None
        if(self.color == PlayerColor.RED.value):
            self.numerical_color = 0
        else:
            self.numerical_color = 1
        self.board = {}
        # self.board = {Coord(3, 3): 0, 
        #             Coord(3, 4): 0, 
        #             Coord(4, 3): 0,
        #             Coord(4, 4): 0,
        #             Coord(2, 3): 1,
        #             Coord(2, 4): 1,
        #             Coord(2, 5): 1, 
        #             Coord(2, 6): 1}
        self.firstTurn = True
        match color:
            case PlayerColor.RED:
                print("Testing: I am playing as RED")
            case PlayerColor.BLUE:
                print("Testing: I am playing as BLUE")

    def action(self, **referee: dict) -> Action:
        """
        This method is called by the referee each time it is the agent's turn
        to take an action. It must always return an action object. 
        """

        # Below we have hardcoded two actions to be played depending on whether
        # the agent is playing as BLUE or RED. Obviously this won't work beyond
        # the initial moves of the game, so you should use some game playing
        # technique(s) to determine the best action to take.
        print(self.turn)
        self.turn += 2
        if self.firstTurn:
            self.firstTurn = False
            match self.color:
                case PlayerColor.RED:
                    print("Testing: RED is playing a PLACE action")
                    return PlaceAction(
                        Coord(3, 3), 
                        Coord(3, 4), 
                        Coord(4, 3), 
                        Coord(4, 4)
                    )
                case PlayerColor.BLUE:
                    print("Testing: BLUE is playing a PLACE action")
                    return PlaceAction(
                        Coord(2, 3), 
                        Coord(2, 4), 
                        Coord(2, 5), 
                        Coord(2, 6)
                    )
        initialBoardState = BoardState(self.board,color=self.color,opponent_color=self.opponent_color)
        action = None
        if self.turn>30:
            action = minimax_alpha_beta_decision(initialBoardState,2)
        else:
            root = MCTSTreeNode(state = initialBoardState, color=self.color, opponent_color=self.opponent_color)
            selected_node = root.best_action()
            action = selected_node.parent_action
        coord1 = Coord(action[0].r,action[0].c)
        coord2 = Coord(action[1].r,action[1].c)
        coord3 = Coord(action[2].r,action[2].c)
        coord4 = Coord(action[3].r,action[3].c)
        return PlaceAction(coord1,coord2,coord3,coord4)

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
        place_action: PlaceAction = action
        c1, c2, c3, c4 = place_action.coords
        # numeric_color = None
        # if color == PlayerColor.RED:
        #     numeric_color = 0
        # else:
        #     numeric_color = 1
        coordinates = [c1,c2,c3,c4]
        # min_r = min(c.r for c in coordinates)
        # max_r = max(c.r for c in coordinates)
        # min_c = min(c.c for c in coordinates)
        # max_c = max(c.c for c in coordinates)
        for coord in coordinates:
            self.board[coord] = color
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
