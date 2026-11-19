#13/11/2026

#imports
from MyProblem import MyProblem
from SearchInfra import aStar, bfs, MySearchNode
import numpy as np, sys

#start of problem-specific helper functions
BOARD_DIM = 3
#the states (board) will be represented a ilnear tuple with BOARD_DIM^2 elements
#it must be immutable and hashable, so that we cannot use numpy matrices as is
#but for convinience during interim calculations, we will convert the tuples to numpy matrices
TARGET_STATE_TPL = tuple(range(BOARD_DIM * BOARD_DIM))
#this dictionary specifies, given the coordinates of the 0's tile, what tile should move, given a certain action
#note that it can also go out of bounds - we check it later
#the coordinates are given as offsets (row, column) from the 0's current position
movers_offset_from_zero_dict = { 
            "Left": (0,1), 
            "Right": (0,-1), 
            "Up": (-1,0), 
            "Down": (1,0)
        }

#find the coordinates of the empty tile
def findZeroCoords(that_state_matrix):
    rows, cols = np.where(that_state_matrix == 0)
    return int(rows[0]), int(cols[0])

#the next function receives a state (as a tuple) and an action, and calculates the coordinates of the tile that is supposed to move given this action
def findMoverCoords(zero_coords : tuple, action_str : str) -> tuple:
    offsets_from_zero = movers_offset_from_zero_dict[action_str]
    return zero_coords[0] + offsets_from_zero[0], zero_coords[1] + offsets_from_zero[1]

#extracting a unique and hashable value from each numpy matrix
def tplFromMatrix(np_matrix):
    return tuple([int(num) for num in np_matrix.flat])

#the opposite direction
def matrixFromTpl(in_tpl):
    return np.array(in_tpl, dtype=np.uint8).reshape(BOARD_DIM, BOARD_DIM)

def whichNumHadMoved(state_tpl, action_str) -> int:
    state_matrix = matrixFromTpl(state_tpl)
    zeros_row, zeros_col = findZeroCoords(state_matrix)
    mover_row, mover_col = findMoverCoords((zeros_row, zeros_col), action_str)
    return int(state_matrix[mover_row, mover_col])

def printResults(alg_name, results_dict):
    print("Algorithm:", alg_name)
    if results_dict["sol-node"] is None:
        print("No solution")
    else:
        sol_node : MySearchNode = results_dict["sol-node"]
        sol_path_list : list = sol_node.showPath()
        sol_nums = []
        for step_tpl in sol_path_list[:-1]: #the last element is a state without action (the final state)
            sol_nums.append(whichNumHadMoved(*step_tpl))
        print("Path:", " ".join(map(str,sol_nums)))

        print("Length:", int(sol_node.total_cost))

    print("Expanded:", str(results_dict["expand-count"]))



#------------end of helpers---------------



#now we define a function that defines the MyProblem object for ur specific tiles problem.
#it includes many sub functions that are meant for MyProblem's constructor
def defineTilesProblem(that_init_state_tpl : tuple) -> MyProblem:
    def that_is_target_state_fn(curr_state_tpl) -> bool:
        return curr_state_tpl == TARGET_STATE_TPL

    that_actions_tpl = ("Left", "Right", "Up", "Down") # we need it as a tuple because it has to be ordered, for tie-breaking

    def that_transition_fn(state_tpl, action_str) -> tuple | None:
        #first we ought to check the legallity of the proposed move
        #a direction is legal, only if the empty tile is not bound by a wall in the opposite direction
        #this is equivalent to: the designated "mover" tile's coordinates - are within the bounds of the matrix
        that_matrix = matrixFromTpl(state_tpl)
        zero_coords = findZeroCoords(that_matrix)
        mover_tile_coords = findMoverCoords((zero_coords), action_str)
        for coord in mover_tile_coords:
            if (coord < 0) or (coord > BOARD_DIM - 1):
                return None
        
        #right here, we know the move is legal        
        that_matrix[zero_coords] = that_matrix[mover_tile_coords]
        that_matrix[mover_tile_coords] = 0
        return tplFromMatrix(that_matrix)

    def that_cost_fn(begin_state_tpl, action_str, end_state_tpl) -> float:
        return 1.0 # uniform action prices in this case

    #instantiate and return the Problem object
    return MyProblem(initial_state=that_init_state_tpl,
                     is_target_state_fn=that_is_target_state_fn, 
                     actions_tpl=that_actions_tpl, 
                     transition_fn=that_transition_fn, 
                     cost_fn=that_cost_fn
                     )

#----------------------end of problem's definition, moving to my heuristic func-------------------------

def calcDestCoordsByVal(tile_val) -> tuple:
    return (int(tile_val // BOARD_DIM), int(tile_val % BOARD_DIM))

def calcManhattanDists(state_as_matrix) -> int:
    sum_dists = 0
    for row in range(BOARD_DIM):
        for col in range(BOARD_DIM):
            tile_val = int(state_as_matrix[row, col])
            if tile_val == 0:
                continue
            dest_coords = calcDestCoordsByVal(tile_val)
            sum_dists += abs(dest_coords[0] - row) + abs(dest_coords[1] - col)
    return sum_dists

def calcCollisions(state_as_matrix) -> int:
    num_rows_with_collisions = 0
    for row in range(BOARD_DIM):
        collision_candids = []
        for col in range(BOARD_DIM):
            tile_val = int(state_as_matrix[row, col])
            if tile_val == 0:
                continue
            dest_coords = calcDestCoordsByVal(tile_val)
            if(dest_coords[0] == row):
                collision_candids.append({"curr_col" : col, "dest_col": dest_coords[1]})
        if len(collision_candids) > 1:
            #now we have to check that at least two of the candidates actually collide
            flag = False
            for candid in collision_candids:
                if flag: break
                for peer in collision_candids:
                    if flag: break
                    candid_curr, candid_dest = candid["curr_col"], candid["dest_col"]
                    peer_curr, peer_dest = peer["curr_col"], peer["dest_col"]
                    if (candid_curr < peer_curr and peer_dest < candid_dest):
                        num_rows_with_collisions += 1
                        flag = True #break both loops - we found a collisdion at this row

    return num_rows_with_collisions * 2

def myHeuristic(state_as_tpl) -> float:
    #my heuristic is an "enhanced" manhattan distance, that tries to predict simple horizontal (only!) collisions and take them into account
    #my method: manhattan + 2 * how many rows, contain at least one pair of tiles that have to "cross" each other to reach their destination
    # the logic is, that if a row has such a conflict, at least one of the tiles invoved will have to give way, and consequently, 
    # this tile will go, at least, once up and once down, to give way and then return to its home row.
    # that is +2 moves on top of manhattan distance
    # this proves admissibility.
    # in addition, because we count at most 1 collision in each row, we can infer that h(n) <= 1 + h(n'),
    # that is because each move reduces, at most, 2 from the heristic value for resolving a conflict,
    # (nothing if there are still conflicts on that same row)
    # and on top of that, it inceases the cost so far by 1, and increases the base manhattan distance of the tile
    # that gave way by 1. so that h(n') is smaller by, at most, 1 compared to h(n)
    # this proves consistency.
    #finally, is is always higher than manhattan's so it is more informed
    #we could also try and take into account column-collisions, but this complicates the proof so i decided to leave it out
    #(since i already found a more informed, consistant heuristic already)

    state_matrix = matrixFromTpl(state_as_tpl)
    manhattan_part = calcManhattanDists(state_matrix)
    collisions_part = calcCollisions(state_matrix)
    return float(manhattan_part + collisions_part)

#--------------------------main--------------------------------

def main():
    args_list = sys.argv[1:]
    if len(args_list) < BOARD_DIM * BOARD_DIM:
        print("usage: Tiles.py <a space delimited permutation of (0 to 8)>")
        args_list = "8 6 7 2 5 4 3 0 1".split(" ")
    as_tpl = tuple(map(int, args_list))
    problem = defineTilesProblem(as_tpl)

    printResults("BFS", bfs(problem))
    printResults("A*", aStar(problem, myHeuristic))

main()