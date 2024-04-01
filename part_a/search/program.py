# COMP30024 Artificial Intelligence, Semester 1 2024
# Project Part A: Single Player Tetress

from .core import PlayerColor, Coord, PlaceAction, Shape, BoardState
from .utils import render_board
from queue import PriorityQueue

def isGoal(board,goal):
    goal_coordinates_row = sum([1 for c in range(11) if board.get(Coord(goal.r, c)) != None])
    goal_coordinates_column = sum([1 for r in range(11) if board.get(Coord(r, goal.c)) != None])
    return goal_coordinates_column == 11 or goal_coordinates_row == 11
     

def a_star_search(board,goal):
    initialRedCoord = findRedCoordinates(board)
    initialBoard = BoardState(board,initialRedCoord)
    open_set = PriorityQueue()
    visited = set()
    open_set.put((0, initialBoard))  # (f-score, node):
    shapes = [shape.value for shape in Shape]
    i = 1
    while open_set:
        _, current = open_set.get()
        board = current.board
        if isGoal(board,goal):
            return board
        for red in current.red_coordinates:
            neighbours = get_neighbors(red,board)
            for neighbor in neighbours:
                for shape in shapes:
                    possible_start_points = get_new_starting_points(shape,neighbor)
                    for start in possible_start_points:
                        if can_place(start,board,shape):
                            newBoard = board.copy()
                            place_blocks(shape,start,newBoard)
                            cost = len(current.red_coordinates) + 4
                            heuristic_value = heuristic(newBoard,goal) # Calculate the heuristic value
                            f_score = cost + heuristic_value
                            newRedCoord = findRedCoordinates(newBoard)
                            newBoardState = BoardState(newBoard,newRedCoord)
                            if newBoardState not in visited:
                                open_set.put((f_score, newBoardState))
                                visited.add(newBoardState)
                            #print(render_board(newBoard, goal, ansi=True))
    return None  # No path found

def place_blocks(shape,coord,board):
    for r, c in shape:
        new_r = (coord.r + r)%11
        new_c = (coord.c + c)%11
        board[Coord(new_r, new_c)] = PlayerColor.RED


def heuristic(board, goal):
    goal_row = goal.r
    goal_column = goal.c
    row_spaces = sum([1 for r in range(11) if board.get(Coord(r, goal.c)) == None])
    col_spaces = sum([1 for c in range(11) if board.get(Coord(goal.r, c)) == None])
    return min(row_spaces, col_spaces)

    
    
def can_place(coord, board, shape):
    for r, c in shape:
        new_r = (coord.r + r)%11
        new_c = (coord.c + c)%11
        # if new_r < 0:
        #     new_r = 11 + new_r
        # elif new_r > 10:
        #     new_r = 11 - new_r
        # if new_c < 0:
        #     new_c = 11 + new_c
        # elif new_c > 10:
        #     new_c = 11 - new_c
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
        new_r = (neighbor.r + i[0])%11
        new_c = (neighbor.c + i[1])%11
        ans.append(Coord(new_r,new_c))
    return ans


def get_neighbors(coord, board):
    """
    Get the neighboring coordinates of a given coordinate,
    considering obstacles on the board.
    """
    neighbors = []
    for dr, dc in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
        new_r = (coord.r + dr)%11
        new_c = (coord.c + dc)%11
        # Check if the new coordinate is not obstructed by a blue block
        if board.get(Coord(new_r, new_c)) != PlayerColor.BLUE and board.get(Coord(new_r, new_c)) != PlayerColor.RED:
            neighbors.append(Coord(new_r, new_c))  # Add the neighboring coordinate
    return neighbors

def contains_goal_row_or_column(came_from, goal, board):
    """
    Check if the given path contains all the coordinates of the goal's row or column.
    """
    goal_coordinates_row = {Coord(goal.r, c) for c in range(11) if board.get(Coord(goal.r, c)) != PlayerColor.BLUE and board.get(Coord(goal.r, c)) != PlayerColor.RED}
    goal_coordinates_column = {Coord(r, goal.c) for r in range(11) if board.get(Coord(r, goal.c)) != PlayerColor.BLUE and board.get(Coord(r, goal.c)) != PlayerColor.RED}
    # # Check if all goal coordinates are present in the path
    if all(coord in came_from.keys() for coord in goal_coordinates_row):
        return ("ROW",True)
    elif all(coord in came_from.keys() for coord in goal_coordinates_column):
        return ("COL",True)
    else:
        return (2,False)
    
def findRedCoordinates(board: dict[Coord, PlayerColor]) -> list:
    red_blocks = [coord for coord, color in board.items() if color == PlayerColor.RED]
    return red_blocks


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
    # for i in red_coords:
    #     path = a_star_search(board, i, target)
    #     if path == None:
    #         continue
    #     if shortest_path == None:
    #         shortest_path = path
    #     elif len(path) < len(shortest_path):
    #         shortest_path = path
    shortest_path = a_star_search(board,target)
    print(render_board(shortest_path, target, ansi=True))
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
    return [
        PlaceAction(Coord(2, 5), Coord(2, 6), Coord(3, 6), Coord(3, 7)),
        PlaceAction(Coord(1, 8), Coord(2, 8), Coord(3, 8), Coord(4, 8)),
        PlaceAction(Coord(5, 8), Coord(6, 8), Coord(7, 8), Coord(8, 8)),
    ]
