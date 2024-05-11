from enum import Enum
from .core import BOARD_N 
import numpy as np


RED = 1
BLUE = 2
DRAW = 3
FILLED_THRESHOLD = 5

class BoardState:
    def __init__(self, board, parent = None, last_action = None, color = None, opponent_color = None):
        self.board = board
        self.parent = parent
        self.last_action = last_action
        self.color = color
        self.opponent_color = opponent_color

 
    def can_place(self, coord, shape, placedAt):
        """
        Boolean function to determine if the shape can be fit into the given coordinate based on surrounding pieces
        """
        for r, c in shape:
            new_r = (coord[0] + r)%BOARD_N
            new_c = (coord[1] + c)%BOARD_N
            placedAt.append((new_r,new_c))
            if self.board[new_r,new_c] != 0:
                return False
        return True
    
    def get_new_starting_points(self,shape,neighbor):
        res = [shape[0]]
        ans = []
        for i in range(1,4):
            diff = tuple(x - y for x, y in zip(shape[i], shape[0]))
            newStart = tuple(x - y for x, y in zip(shape[0], diff))
            res.append(newStart)
        for i in res:
            new_r = (neighbor[0] + i[0])%BOARD_N
            new_c = (neighbor[1] + i[1])%BOARD_N
            ans.append((new_r,new_c))
        return ans

    def get_legal_actions(self,color):
        actions = []
        shapes = [shape.value for shape in Shape]
        blocks = self.findCoordinates(color)
        for block in blocks:
            neighbors = self.get_neighbors(block)
            for neighbor in neighbors:
                for shape in shapes:
                    possible_start_points = self.get_new_starting_points(shape,neighbor)
                    for start in possible_start_points:
                        placedAt = []
                        if self.can_place(start,shape,placedAt):
                            actions.append(tuple(placedAt)) 
        unique_actions = list(set(actions))
        return unique_actions
    
    def update_board(self):
        # Create a boolean mask for non-zero entries
        non_zero_mask = self.board != 0
        # Sum along the rows and columns
        row_non_zero_sums = np.sum(non_zero_mask, axis=1)
        col_non_zero_sums = np.sum(non_zero_mask, axis=0)
        # Find indices where the sum of non-zero entries equals 11
        row_indices = np.where(row_non_zero_sums == 11)[0]
        col_indices = np.where(col_non_zero_sums == 11)[0]
        # Set rows and columns to 0
        self.board[row_indices, :] = 0
        self.board[:, col_indices] = 0

    def perform_action(self,coordinates):
        newBoard = self.board.copy()
        newTurn = None
        for coord in coordinates: 
            newBoard[coord] = self.color
        if self.color == RED:
            newTurn = BLUE
        else:
            newTurn = RED
        newBoardState = BoardState(newBoard,self,coordinates,newTurn)
        newBoardState.update_board()
        return newBoardState

    def get_neighbors(self, coord):
        """
        Get the neighboring coordinates of a given coordinate,
        considering obstacles on the board.
        """
        UP = (-1,0)
        DOWN = (1,0)
        RIGHT = (0,1)
        LEFT = (0,-1)
        neighbors = []
        for dr, dc in [DOWN, UP, RIGHT, LEFT]:
            new_r = (coord[0] + dr)%BOARD_N
            new_c = (coord[1] + dc)%BOARD_N
            # Check if the new coordinate is not obstructed by a blue block
            if self.board[new_r,new_c] != RED and self.board[new_r,new_c] != BLUE:
                neighbors.append((new_r, new_c))  # Add the neighboring coordinate
        return neighbors
    
    def clone(self):
        newBoard = self.board.copy()
        return BoardState(newBoard,None,None,color=self.color,
                          opponent_color=self.opponent_color)
    
    def count_rows_or_columns_with_blocks(self, color, threshold):
        # Count rows with more than `threshold` blocks of the specified color
        row_counts = np.sum(self.board == color, axis=1)
        filled_row = np.sum(row_counts > threshold)
        # Count columns with more than `threshold` blocks of the specified color
        column_counts = np.sum(self.board == color, axis=0)
        filled_col = np.sum(column_counts > threshold)
        return filled_row + filled_col

    def findCoordinates(self, playerColor) -> list:
        """
        Function to search the board and return a list of all red blocks found
        """
        indices = np.where(self.board == playerColor)
        coordinates = list(zip(indices[0], indices[1]))
        return coordinates

    def evaluate_state(self,player_color,opponent_color):
        player = self.findCoordinates(player_color)
        opponent = self.findCoordinates(opponent_color)
        block_diff = len(player) - len(opponent)
        red_col = self.count_rows_or_columns_with_blocks(RED,FILLED_THRESHOLD)
        blue_col = self.count_rows_or_columns_with_blocks(BLUE,FILLED_THRESHOLD)
        return block_diff + blue_col - red_col


    


class Shape(Enum):
    '''
    An `Enum` class for all the different shape of tetrimino blocks
    '''
    I1 = [(0,0), (1,0), (2,0), (3,0)]
    I2 = [(0,0), (0,1), (0,2), (0,3)]

    O = [(0,0), (0,1), (1,0), (1,1)]

    T1 = [(0,0), (0,1), (0,2), (1,1)]
    T2 = [(0,0), (1,-1), (1,0), (2,0)]
    T3 = [(0,0), (0,1), (-1,1), (0,2)]
    T4 = [(0,0), (1,0), (2,0), (1,1)]

    J1 = [(0,0), (1,0), (2,0), (2,-1)]
    J2 = [(0,0), (1,0), (1,1), (1,2)]
    J3 = [(0,0), (0,1), (1,0), (2,0)]
    J4 = [(0,0), (0,1), (0,2), (1,2)]

    L1 = [(0,0),(1,0),(2,0),(2,1)]
    L2 = [(0,0),(0,1),(0,2),(1,0)]
    L3 = [(0,0),(0,1),(1,1),(2,1)]
    L4 = [(0,0),(0,1),(0,2),(-1,2)]

    Z1 = [(0,0),(0,1),(1,1),(1,2)]
    Z2 = [(0,0),(1,-1),(1,0),(2,-1)]

    S1 = [(0,0),(0,1),(1,-1),(1,0)]
    S2 = [(0,0),(1,0),(1,1),(2,1)]
