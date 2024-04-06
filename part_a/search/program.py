# COMP30024 Artificial Intelligence, Semester 1 2024
# Project Part A: Single Player Tetress

from .core import PlayerColor, Coord, PlaceAction, BOARD_N, Direction
from .helper import Shape, BoardState, BLOCK_LEN
from .utils import render_board
from queue import PriorityQueue
from collections import defaultdict

def isGoal(board,goal):
    """
    Checks if the goal is met

    Args:
        board (dict): Dictionary representing the game board.
        goal: Coordinates representing the 'B' node on the board

    Returns:
        Boolean True if the goal is met on the board and False if it isnt
    """
    goal_coordinates_row = sum([1 for c in range(BOARD_N) if board.get(Coord(goal.r, c)) != None])
    goal_coordinates_column = sum([1 for r in range(BOARD_N) if board.get(Coord(r, goal.c)) != None])
    
    return goal_coordinates_column == BOARD_N or goal_coordinates_row == BOARD_N

def retracePath(boardState,start):
    res = []
    while boardState.board != start:
        res.append(boardState.redInserted)
        boardState = boardState.parent
    res.reverse()
    return res

def a_star_search(board,goal):
    """
    Uses A* Search algorithm to determine the best path of tetrimino shaped blocks to clear the 'B' node on board

    Args:
        board (dict): Dictionary representing the game board.
        goal: Coordinates representing the 'B' node on the board

    Returns:
        'current': A path in the form of a list of Coords
        None: If no valid paths are found
    """
    if isGoal(board,goal):
        return current
    initialRedCoord = findRedCoordinates(board)
    initialr,initialc = find_best_red(initialRedCoord,goal)
    initialBoard = BoardState(board,None,None,0,initialRedCoord,initialr,initialc)   
    open_set = PriorityQueue()
    visited = set()
    open_set.put((0, initialBoard))  # (f-score, node):
    shapes = [shape.value for shape in Shape]
    while open_set.empty() ==  False:
        _, current = open_set.get()
        board = current.board
        redCoordinates = current.redCoord
        for red in redCoordinates:
            neighbours = get_neighbors(red,board)
            for neighbor in neighbours:
                for shape in shapes:
                    possible_start_points = get_new_starting_points(shape,neighbor) #6-2
                    for start in possible_start_points:
                        if can_place(start,board,shape):
                            newBoard = board.copy()
                            newRedCoord = current.redCoord.copy()
                            cost = current.cost + BLOCK_LEN
                            newBoardState = BoardState(newBoard,current,None,cost,newRedCoord,current.bestRow,current.bestCol)
                            blocks = place_blocks_and_update_state(shape,start,goal,newBoardState)  
                            newBoardState.redInserted = blocks 
                            if isGoal(newBoard,goal):
                                return newBoardState                                                                              
                            if newBoardState not in visited:
                                heuristic_value = heuristic(newBoardState,goal)
                                f_score = cost + heuristic_value
                                open_set.put((f_score, newBoardState))
                                visited.add(newBoardState)
                            
    return None  # No path found


def place_blocks(shape,coord,board):
    """
    Function to place the tetrimino shaped blocks onto the board given a set of coordinates
    """
    res = []
    for r, c in shape:
        new_r = (coord.r + r)%BOARD_N
        new_c = (coord.c + c)%BOARD_N
        board[Coord(new_r, new_c)] = PlayerColor.RED
        res.append(Coord(new_r, new_c))
    return res

def check_and_handle_full_rows_or_columns(boardState,new_r,new_c,goal):
    board = boardState.board
    redCoords = boardState.redCoord
    fullr = sum([1 for c in range(BOARD_N) if board.get(Coord(new_r, c)) != None])
    fullc = sum([1 for r in range(BOARD_N) if board.get(Coord(r, new_c)) != None])
    if fullc == BOARD_N and new_c != goal.c:
        for row in range(BOARD_N):
            board.pop(Coord(row,new_c),None)
            if Coord(row,new_c) in redCoords:
                redCoords.remove(Coord(row,new_c))
        best_r,best_c = find_best_red(redCoords,goal)
        boardState.bestRow = best_r
        boardState.bestCol = best_c
    if fullr == BOARD_N and new_r != goal.r:
        for col in range(BOARD_N):
            board.pop(Coord(new_r,col),None)
            if Coord(new_r,col) in redCoords:
                redCoords.remove(Coord(new_r,col))
        best_r,best_c = find_best_red(redCoords,goal)
        boardState.bestRow = best_r
        boardState.bestCol = best_c

def place_blocks_and_update_state(shape,coord,goal,boardState):
    board = boardState.board
    redCoords = boardState.redCoord
    res = []
    for r, c in shape:
        new_r = (coord.r + r)%BOARD_N
        new_c = (coord.c + c)%BOARD_N
        r_dis = min(abs(new_r - goal.r),BOARD_N - abs(new_r - goal.r))
        c_dis = min(abs(new_c - goal.c),BOARD_N - abs(new_c - goal.c))
        if r_dis < boardState.bestRow:
            boardState.bestRow = r_dis
        if c_dis < boardState.bestCol:
            boardState.bestCol = c_dis
        board[Coord(new_r, new_c)] = PlayerColor.RED
        redCoords.append(Coord(new_r, new_c))
        check_and_handle_full_rows_or_columns(boardState,new_r,new_c,goal)
        res.append(Coord(new_r, new_c))
    return res


def heuristic(boardState, goal):
    """
    Function to find the shortest possible path to the goal coordinate
    """
    board = boardState.board
    row_spaces = sum([1 for r in range(BOARD_N) if board.get(Coord(r, goal.c)) == None])
    col_spaces = sum([1 for c in range(BOARD_N) if board.get(Coord(goal.r, c)) == None])
    #return min(row_spaces,col_spaces)
    total_r = boardState.bestRow + col_spaces
    total_c = boardState.bestCol + row_spaces
    return min(total_r, total_c)
    
def can_place(coord, board, shape):
    """
    Boolean function to determine if the shape can be fit into the given coordinate based on surrounding pieces
    """
    for r, c in shape:
        new_r = (coord.r + r)%BOARD_N
        new_c = (coord.c + c)%BOARD_N
        if board.get(Coord(new_r,new_c)) != None:
            return False
    return True

def get_new_starting_points(shape,neighbor):
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

def findRedCoordinates(board: dict[Coord, PlayerColor]) -> list:
    """
    Function to search the board and return a list of all red blocks found
    """
    red_blocks = [coord for coord, color in board.items() if color == PlayerColor.RED]
    return red_blocks

def find_best_red(red_coords, goal):
    """
    Function to determine the best starting red node to begin the heuristic calculation for the A* search
    """
    r_dis = min(abs(red_coords[0].r - goal.r),BOARD_N - abs(red_coords[0].r - goal.r))
    c_dis = min(abs(red_coords[0].c - goal.c),BOARD_N - abs(red_coords[0].c - goal.c)) 
    for i in range (1, len(red_coords)):
        new_r_dis = min(abs(red_coords[i].r - goal.r),BOARD_N - abs(red_coords[i].r - goal.r))
        new_c_dis = min(abs(red_coords[i].c - goal.c),BOARD_N - abs(red_coords[i].c - goal.c))
        if new_r_dis < r_dis:
            r_dis = new_r_dis
        if new_c_dis < c_dis:
            c_dis = new_c_dis
    return (r_dis, c_dis)

def get_neighbors(coord, board):
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
        if board.get(Coord(new_r, new_c)) != PlayerColor.BLUE and board.get(Coord(new_r, new_c)) != PlayerColor.RED:
            neighbors.append(Coord(new_r, new_c))  # Add the neighboring coordinate
    return neighbors

def search(
    board: dict[Coord, PlayerColor], 
    target: Coord
) -> list[PlaceAction] | None:
    """
    This is the entry point for your submission. You should modify this
    function to solve the search problem discussed in the Part A specification.
    See `core.py` for information on the types being used here.

    Parameters:
        `board`: a dictionary representing the initial board state, mapping
            coordinates to "player colours". The keys are `Coord` instances,
            and the values are `PlayerColor` instances.  
        `target`: the target BLUE coordinate to remove from the board.
    
    Returns:
        A list of "place actions" as PlaceAction instances, or `None` if no
        solution is possible.
    """

    # The render_board() function is handy for debugging. It will print out a
    # board state in a human-readable format. If your terminal supports ANSI
    # codes, set the `ansi` flag to True to print a colour-coded version!
    print(render_board(board, target, ansi=True))

    finalBoard = a_star_search(board,target)
    
    if not finalBoard:
        return None
    print(render_board(finalBoard.board, target, ansi=True))
    path = retracePath(finalBoard,board)
    ans = []
    for i in path:
        ans.append(PlaceAction(i[0],i[1],i[2],i[3]))
    return ans
