from enum import Enum
from .core import PlayerColor, Coord

class BoardState:
    def __init__(self, board: dict[Coord, PlayerColor], red_coordinates: list[Coord], parent = None, redInserted = None,cost = 0):
        self.board = board
        self.red_coordinates = red_coordinates
        self.parent = parent
        self.redInserted = redInserted
        self.cost = cost


    def to_tuple(self) -> tuple[dict[Coord, PlayerColor], list[Coord]]:
        return self.board, self.red_coordinates

    @classmethod
    def from_tuple(cls, state_tuple: tuple[dict[Coord, PlayerColor], list[Coord]]):
        return cls(*state_tuple)
    def __lt__(self, other):
        return len(self.red_coordinates) < len(other.red_coordinates)
    

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