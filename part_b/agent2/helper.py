from enum import Enum
from .core import PlayerColor, Coord, BOARD_N, PlaceAction  

red_color = PlayerColor.RED
blue_color = PlayerColor.BLUE

class BoardState:
    def __init__(self, board: dict[Coord, int], parent = None, last_action = None, turn = None):
        self.board = board
        self.parent = parent
        self.last_action = last_action
        self.turn = turn

 
    def can_place(self, coord, board, shape, placedAt):
        """
        Boolean function to determine if the shape can be fit into the given coordinate based on surrounding pieces
        """
        for r, c in shape:
            new_r = (coord.r + r)%BOARD_N
            new_c = (coord.c + c)%BOARD_N
            placedAt.append(Coord(new_r,new_c))
            if Coord(new_r,new_c) in board.keys():
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
            new_r = (neighbor.r + i[0])%BOARD_N
            new_c = (neighbor.c + i[1])%BOARD_N
            ans.append(Coord(new_r,new_c))
        return ans

    def get_legal_actions(self):
        actions = []
        shapes = [shape.value for shape in Shape]
        blocks = self.findCoordinates(self.board,self.turn)
        #print("blocks =",blocks)
        for block in blocks:
            neighbors = self.get_neighbors(block,self.board)
            #print(neighbors)
            for neighbor in neighbors:
                for shape in shapes:
                    possible_start_points = self.get_new_starting_points(shape,neighbor)
                    for start in possible_start_points:
                        placedAt = []
                        if self.can_place(start,self.board,shape,placedAt): 
                            actions.append(placedAt)  
        # if len(actions) == 0:
        #     print(self.board)
        return actions
    
    def update_board(self,coordinates):
        min_r = min(c.r for c in coordinates)
        max_r = max(c.r for c in coordinates)
        min_c = min(c.c for c in coordinates)
        max_c = max(c.c for c in coordinates)
        coords_to_remove = set()
        for r in range(min_r, max_r + 1):
            non_empty_coords = []
            for c in range(BOARD_N):
                if self.board.get(Coord(r,c)) != None:
                    non_empty_coords.append(Coord(r,c))
                else:
                    break
            if len(non_empty_coords) == BOARD_N:
                for coord in non_empty_coords:
                    coords_to_remove.add(coord)

        for c in range(min_c, max_c + 1):
            non_empty_coords = []
            for r in range(BOARD_N):
                if self.board.get(Coord(r,c)) != None:
                    non_empty_coords.append(Coord(r,c))
                else:
                    break
            if len(non_empty_coords) == BOARD_N:
                for coord in non_empty_coords:
                    coords_to_remove.add(coord)
        for coord in coords_to_remove:
            self.board.pop(coord)

    def perform_action(self,coordinates):
        newBoard = self.board.copy()
        newTurn = None
        for coord in coordinates: 
            assert(type(coord) != int) 
            newBoard[coord] = self.turn
        #print("selfturn ",self.turn)
        if self.turn == 0:
            newTurn = 1
        else:
            newTurn = 0
        newBoardState = BoardState(newBoard,self,coordinates,newTurn)
        newBoardState.update_board(coordinates)
        return newBoardState

    def get_neighbors(self, coord, board):
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
            new_r = (coord.r + dr)%BOARD_N
            new_c = (coord.c + dc)%BOARD_N
            # Check if the new coordinate is not obstructed by a blue block
            if board.get(Coord(new_r, new_c)) != 1 and board.get(Coord(new_r, new_c)) != 0:
                neighbors.append(Coord(new_r, new_c))  # Add the neighboring coordinate
        return neighbors
    
    def clone(self):
        newBoard = self.board.copy()
        newLastAction = None
        return BoardState(newBoard,None,newLastAction,turn=self.turn)
    
    def is_terminal(self):

        return 

    def findCoordinates(self, board: dict[Coord, int],playerColor) -> list:
        """
        Function to search the board and return a list of all red blocks found
        """
        red_blocks = [coord for coord, color in board.items() if color == playerColor]
        return red_blocks

    def is_winning(self, your_color):
        opponent_blocks = self.findCoordinates(self.board,1 - your_color)
        your_blocks = self.findCoordinates(self.board,your_color)
        if len(your_blocks) > len(opponent_blocks):
            return 1
        elif len(your_blocks) < len(opponent_blocks):
            return -1
        return 0

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