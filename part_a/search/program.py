# COMP30024 Artificial Intelligence, Semester 1 2024
# Project Part A: Single Player Tetress

from .core import PlayerColor, Coord, PlaceAction, BOARD_N, Direction
from .helper import Shape, BoardState
from .utils import render_board
from queue import PriorityQueue
from collections import defaultdict

def isGoal(board,goal):
    '''
    Checks if the goal is met

    Args:
        board (dict): Dictionary representing the game board.
        goal: Coordinates representing the 'B' node on the board

    Returns:
        Boolean True if the goal is met on the board and False if it isnt
    '''
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

def update_board(board,goal):
    '''
    Update the board dictionary by removing keys corresponding to full rows or columns.

    Args:
        board (dict): Dictionary representing the game board.
        goal: Coordinates representing the 'B' node on the board

    Returns:
        The function modifies the input board dictionary directly and does not return an argument
    '''
    # Count the number of blocks in each row and column
    row_counts = defaultdict(int)
    col_counts = defaultdict(int)
    for coord, color in board.items():
        if color is not None:
            row_counts[coord.r] += 1
            col_counts[coord.c] += 1
    
    row_counts[goal.r] = None
    col_counts[goal.c] = None
    
    # Identify full rows and columns
    full_rows = [r for r, count in row_counts.items() if count == BOARD_N]
    full_cols = [c for c, count in col_counts.items() if count == BOARD_N]
    
    # Remove keys corresponding to full rows
    for row in full_rows:
        for col in range(BOARD_N):
            del board[Coord(row, col)]
    
    # Remove keys corresponding to full columns
    for col in full_cols:
        for row in range(BOARD_N):
            del board[Coord(row, col)]


def a_star_search(board,goal):
    '''
    Uses A* Search algorithm to determine the best path of tetrimino shaped blocks to clear the 'B' node on board

    Args:
        board (dict): Dictionary representing the game board.
        goal: Coordinates representing the 'B' node on the board

    Returns:
        'current': A path in the form of a list of Coords
        None: If no valid paths are found
    '''
    initialRedCoord = findRedCoordinates(board)
    initialBoard = BoardState(board,initialRedCoord)
    open_set = PriorityQueue()
    visited = set()
    open_set.put((0, initialBoard))  # (f-score, node):
    shapes = [shape.value for shape in Shape]
    i = 5
    while open_set.empty() == False:
        i -= 1
        _, current = open_set.get()
        board = current.board
        if isGoal(board,goal):
            return current
        for red in current.red_coordinates:
            neighbours = get_neighbors(red,board)
            for neighbor in neighbours:
                for shape in shapes:
                    possible_start_points = get_new_starting_points(shape,neighbor)
                    for start in possible_start_points:
                        if can_place(start,board,shape):
                            newBoard = board.copy()
                            blocks = place_blocks(shape,start,newBoard)
                            update_board(newBoard,goal)
                            cost = current.cost + 4
                            heuristic_value = heuristic(newBoard,goal) # Calculate the heuristic value
                            f_score = cost + heuristic_value
                            newRedCoord = findRedCoordinates(newBoard)
                            newBoardState = BoardState(newBoard,newRedCoord,current,blocks,cost)
                            if newBoardState not in visited:
                                open_set.put((f_score, newBoardState))
                                visited.add(newBoardState)
                            #print(render_board(newBoard, goal, ansi=True))
    return None  # No path found

def place_blocks(shape,coord,board):
    '''
    Function to place the tetrimino shaped blocks onto the board given a set of coordinates
    '''
    res = []
    for r, c in shape:
        new_r = (coord.r + r)%BOARD_N
        new_c = (coord.c + c)%BOARD_N
        board[Coord(new_r, new_c)] = PlayerColor.RED
        res.append(Coord(new_r, new_c))
    return res


def heuristic(board, goal):
    '''
    Function to find the shortest possible path to the goal coordinate
    '''
    row_spaces = sum([1 for r in range(BOARD_N) if board.get(Coord(r, goal.c)) == None])
    col_spaces = sum([1 for c in range(BOARD_N) if board.get(Coord(goal.r, c)) == None])
    return min(row_spaces, col_spaces)

    
    
def can_place(coord, board, shape):
    '''
    Boolean function to determine if the shape can be fit into the given coordinate based on surrounding pieces
    '''
    for r, c in shape:
        new_r = (coord.r + r)%BOARD_N
        new_c = (coord.c + c)%BOARD_N
        if Coord(new_r,new_c) in board.keys():
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
    '''
    Function to search the board and return a list of all red blocks found
    '''
    red_blocks = [coord for coord, color in board.items() if color == PlayerColor.RED]
    return red_blocks

def find_best_red(red_coords, goal):
    '''
    Function to determine the best starting red node to begin the heuristic calculation for the A* search
    '''
    best_row_coord = red_coords[0]
    best_col_coord = red_coords[0]
    r_dis = abs(best_row_coord.r - goal.r)
    c_dis = abs(best_col_coord.c - goal.c) 
    for red_coord in range (1, len(red_coords)):
        new_r_dis = abs(red_coord.r - goal.r)
        new_c_dis = abs(red_coord.c - goal.c)
        if new_r_dis < r_dis:
            best_row_coord = red_coord
            r_dis = new_r_dis
        if new_c_dis < c_dis:
            best_col_coord = red_coord
            c_dis = new_c_dis
    return (best_row_coord, best_col_coord)

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

#def contains_goal_row_or_column(came_from, goal, board):
#    """
#    Check if the given path contains all the coordinates of the goal's row or column.
#    """
#    goal_coordinates_row = {Coord(goal.r, c) for c in range(11) if board.get(Coord(goal.r, c)) 
#                            != PlayerColor.BLUE and board.get(Coord(goal.r, c)) != PlayerColor.RED}
#    goal_coordinates_column = {Coord(r, goal.c) for r in range(11) if board.get(Coord(r, goal.c)) 
#                               != PlayerColor.BLUE and board.get(Coord(r, goal.c)) != PlayerColor.RED}
#    # # Check if all goal coordinates are present in the path
#    if all(coord in came_from.keys() for coord in goal_coordinates_row):
#        return ("ROW",True)
#    elif all(coord in came_from.keys() for coord in goal_coordinates_column):
#        return ("COL",True)
#    else:
#        return (2,False)

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

    # Do some impressive AI stuff here to find the solution...
    # ...
    # ... (your solution goes here!)
    finalBoard = a_star_search(board,target)
    #print(render_board(finalBoard.board, target, ansi=True))
    
    if not finalBoard:
        return None
    print(render_board(finalBoard.board, target, ansi=True))
    path = retracePath(finalBoard,board)
    ans = []
    for i in path:
        ans.append(PlaceAction(i[0],i[1],i[2],i[3]))
    return ans
    # if shortest_path:
    #     print("Shortest path from start to goal:", shortest_path)
    # else:
    #     print("No path exists from start to goal.")
    # for i in shortest_path:
    #     board[i] = PlayerColor.RED
    # print(render_board(board, target, ansi=True))
    # Here we're returning "hardcoded" actions as an example of the expected
    # output format. Of course, you should instead return the result of your
    # search algorithm. Remember: if no solution is possible for a given input,
    # return `None` instead of a list.
    #return [
    #    PlaceAction(Coord(2, 5), Coord(2, 6), Coord(3, 6), Coord(3, 7)),
    #    PlaceAction(Coord(1, 8), Coord(2, 8), Coord(3, 8), Coord(4, 8)),
    #    PlaceAction(Coord(5, 8), Coord(6, 8), Coord(7, 8), Coord(8, 8)),
    #]