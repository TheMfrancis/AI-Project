# COMP30024 Artificial Intelligence, Semester 1 2024
# Project Part A: Single Player Tetress

from .core import PlayerColor, Coord, PlaceAction, Shape
from .utils import render_board
from queue import PriorityQueue

def a_star_search(board, start, goal):
    open_set = PriorityQueue()
    open_set.put((0, start))  # (f-score, node)
    came_from = {start: None}  # Store the entire path from start to current node
    g_score = {start: 0}

    while not open_set.empty():
        _, current = open_set.get()

        # Check if filling the row or column of the goal
        rowOrCol,isGoal = contains_goal_row_or_column(came_from,goal,board)
        if isGoal and rowOrCol == "ROW":
            #print(came_from)
            path = find_path_to_fill_row(came_from,start,goal.r)
            return path
        elif isGoal and rowOrCol == "COL":
            path = fill_column_path(came_from, start, goal.c)
            return path
        
        for neighbor in get_neighbors(current, board):
            tentative_g_score = g_score[current] + 1
            if tentative_g_score < g_score.get(neighbor, float('inf')):
                came_from[neighbor] = current  # Update the path
                g_score[neighbor] = tentative_g_score
                f_score = tentative_g_score + heuristic(board, neighbor, goal)
                open_set.put((f_score, neighbor))

    return None  # No path found

def find_path_to_fill_row(came_from, start, goal_row):
    # # Initialize an empty list to store the path
    path = []
    row = [i for i in list(came_from.keys()) if i.r == goal_row]
    print(row)
    for j in row:
        while j != start:
        # Append the current coordinate to the path
            if j not in path:
                path.append(j)
            j = came_from[j]
        # Move to the previous coordinate using the came_from dictionary
    return path

def fill_column_path (came_from, start, goal_column):
    path = []
    column = [i for i in list(came_from.keys()) if i.c == goal_column]
    for i in column:
        while i != start:
            if i not in path:
                path.append(i)
            i = came_from[i]
    return path

def heuristic(board, current, goal):
    # Calculate Manhattan distance to the goal
    manhattan_dist = abs(current.r - goal.r) + abs(current.c - goal.c)

    # Determine if it's easier to fill the row or column of the goal block
    row_spaces = sum(1 for coord, color in board.items() if coord.r == goal.r and color == None)
    col_spaces = sum(1 for coord, color in board.items() if coord.c == goal.c and color == None)

    # Adjust heuristic based on the easier option
    if row_spaces <= col_spaces:
        return manhattan_dist + row_spaces
    else:
        return manhattan_dist + col_spaces

def get_neighbors(coord, board):
    """
    Get the neighboring coordinates of a given coordinate,
    considering obstacles on the board.
    """
    neighbors = []
    for dr, dc in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
        new_r, new_c = coord.r + dr, coord.c + dc
        # Offsets the corrdinates out of bounds to simulate the edge warping effect
        if new_r == -1:
            new_r = 10
        elif new_r == 11:
            new_r = 0
        if new_c == -1:
            new_c = 10
        elif new_c == 11:
            new_c = 0

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
    red_coords = findRedCoordinates(board)
    shortest_path = None
    for i in red_coords:
        path = a_star_search(board, i, target)
        if path == None:
            continue
        if shortest_path == None:
            shortest_path = path
        elif len(path) < len(shortest_path):
            shortest_path = path

    if shortest_path:
        print("Shortest path from start to goal:", shortest_path)
    else:
        print("No path exists from start to goal.")

    # Here we're returning "hardcoded" actions as an example of the expected
    # output format. Of course, you should instead return the result of your
    # search algorithm. Remember: if no solution is possible for a given input,
    # return `None` instead of a list.
    return [
        PlaceAction(Coord(2, 5), Coord(2, 6), Coord(3, 6), Coord(3, 7)),
        PlaceAction(Coord(1, 8), Coord(2, 8), Coord(3, 8), Coord(4, 8)),
        PlaceAction(Coord(5, 8), Coord(6, 8), Coord(7, 8), Coord(8, 8)),
    ]
