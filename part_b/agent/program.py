# COMP30024 Artificial Intelligence, Semester 1 2024
# Project Part B: Game Playing Agent

from referee.game import PlayerColor, Action, PlaceAction, Coord, BOARD_N
import math
import numpy as np
from referee.game.actions import PlaceAction
from referee.game.coord import Coord
from .helper import BoardState, Shape, RED, BLUE

BRANCHING_LIMIT = 30
HIGH_DEPTH = 4
LOW_DEPTH = 2

def minimax_alpha_beta(state, depth, alpha, beta, maximizing_player, playerColor, opponentColor, best_actions):
    if best_actions.get(state):
        return best_actions.get(state)
    legal_actions = state.get_legal_actions(state.color)
    if len(legal_actions) > BRANCHING_LIMIT:
                depth -= 1
    if depth <= 0 or len(legal_actions) == 0:
        return state.evaluate_state(playerColor,opponentColor)

    if maximizing_player:
        max_eval = -math.inf
        for action in legal_actions:
            next_state = state.perform_action(action)
            eval = minimax_alpha_beta(next_state, depth - 1, alpha, beta, False, playerColor, opponentColor,best_actions)
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        best_actions[state] = action  # Store the best action for this state
        return max_eval
    else:
        min_eval = math.inf
        for action in legal_actions:
            next_state = state.perform_action(action)
            eval = minimax_alpha_beta(next_state, depth - 1, alpha, beta, True, playerColor, opponentColor,best_actions)
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval

def handle_first_move(color, boardState: BoardState):
    if color == RED:
        return PlaceAction(
                        Coord(0, 0), 
                        Coord(10, 0), 
                        Coord(0, 10), 
                        Coord(10, 10)
                    )
    else:
        best_len = 0
        action = None
        shapes = [shape.value for shape in Shape]
        red_blocks = boardState.findCoordinates(RED)
        neighbours = []
        for red in red_blocks:
            neighbour = boardState.get_neighbors(red)
            neighbours.extend(neighbour)
        for block in neighbours:
            for shape in shapes:
                possible_start_points = boardState.get_new_starting_points(shape,block)
                for start in possible_start_points:
                    placedAt = []
                    if boardState.can_place(start,shape,placedAt):
                        similarity = len(set(placedAt) & set(neighbours))
                        if similarity > best_len:
                            best_len = similarity
                            action = placedAt
        coord1 = Coord(action[0][0],action[0][1])
        coord2 = Coord(action[1][0],action[1][1])
        coord3 = Coord(action[2][0],action[2][1])
        coord4 = Coord(action[3][0],action[3][1])
        return PlaceAction(coord1,coord2,coord3,coord4)

def minimax_alpha_beta_decision(state, depth, actions, playerColor, opponentColor: int, best_actions):
    if best_actions.get(state):
        return best_actions.get(state)
    best_action = None
    best_value = -math.inf
    alpha = -math.inf
    beta = math.inf
    legal_actions = actions
    for action in legal_actions:
        next_state = state.perform_action(action)
        value = minimax_alpha_beta(next_state, depth - 1, alpha, beta, False, playerColor, opponentColor, best_actions)
        if value > best_value:
            best_value = value
            best_action = action
        alpha = max(alpha, value)
    best_actions[state] = best_action
    return best_action

def get_numeric_color(color: PlayerColor):
    if color == PlayerColor.RED:
        return RED
    else:
        return BLUE

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
        self.stored_states = {}
        self.turn = 1
        self.opponent_numerical_color = None
        self.numerical_color = None
        if(color == PlayerColor.RED):
            self.numerical_color = RED
            self.opponent_numerical_color = BLUE
        else:
            self.numerical_color = BLUE
            self.opponent_numerical_color = RED
        self.boardState = BoardState(np.zeros((BOARD_N, BOARD_N), dtype=int),
                                     color=self.numerical_color,
                                     opponent_color=self.opponent_numerical_color)
        

    def action(self, **referee: dict) -> Action:
        """
        This method is called by the referee each time it is the agent's turn
        to take an action. It must always return an action object. 
        """
        if self.turn == 1:
            self.turn += 2
            return handle_first_move(self.numerical_color,self.boardState)
        
        initialBoardState = self.boardState.clone()
        legal_actions = initialBoardState.get_legal_actions(self.numerical_color)
        if len(legal_actions) < BRANCHING_LIMIT:
            print("Using minimax")
            depth = HIGH_DEPTH
        else:
            depth = LOW_DEPTH
        action = minimax_alpha_beta_decision(initialBoardState,depth,
                                                 actions=legal_actions,
                                                 playerColor=self.numerical_color,
                                                 opponentColor=self.opponent_numerical_color,
                                                 best_actions=self.stored_states)
        coord1 = Coord(action[0][0],action[0][1])
        coord2 = Coord(action[1][0],action[1][1])
        coord3 = Coord(action[2][0],action[2][1])
        coord4 = Coord(action[3][0],action[3][1])
        self.turn += 2
        return PlaceAction(coord1,coord2,coord3,coord4)

            
    def update(self, color: PlayerColor, action: Action, **referee: dict):
        """
        This method is called by the referee after an agent has taken their
        turn. You should use it to update the agent's internal game state. 
        """
        # There is only one action type, PlaceAction
        place_action: PlaceAction = action
        c1, c2, c3, c4 = place_action.coords
        numeric_color = get_numeric_color(color)
        coordinates = [c1,c2,c3,c4]
        for coord in coordinates:
            self.boardState.board[coord.r,coord.c] = numeric_color
        self.boardState.update_board()
        print("Time Remaining: ",referee["time_remaining"])
        print("Space Remaining: ",referee["space_remaining"])
        print(f"Testing: {color} played PLACE action: {c1}, {c2}, {c3}, {c4}")
