19/11/2026

Hi, following is an overview of my solution for maman 01.

## Usage

```text
Tiles.py <a space separated permutation of 0 to 8>
```

This program defines modular classes and functions that simulate formal problems, search algorithms, and allow plugging different actual instances of the problem with different algorithms and view the run’s statistics

## The code is made of the following parts

### a. the Problem class

The Problem class: an abstract representation of a problem, via attributes such as possible actions, transition model, cost function, and an initial state. Each problem has a format for representing states, that has to be hashable, because it acts as the key to identify a unique state of the problem.

### b. the Node class

The Node class: this is a modular infra. for a search algorithm – it tracks the paths in an ongoing solution, so that we can backtrack, assess the cost, and compare alternative further steps during n ongoing search and after one has finished. The class contains the “expand” method as well as “create root” given an instance of a Problem object.

### c. the search algorithms

The search algorithms: BFS and A*. BFS is implemented with deque (FIFO queue) as the frontier, and a python set as the reached set. A* is implemented with heapq as the frontier and a python dictionary {state-as-hashable : best-path-node-object} as the reached set.

Note that A* can handle both consistent and inconsistent heuristics (they have to be admissible).

There is an isuue with removing elements from heapq that hurts performance. It is resolved with a mechanism that checks whether a better cost node has already been found before trying to expand any node.

**optimality:** both algorithms return an optimal solution: BFS is inherently optimal, and A* is optimal when paired with an admissible heuristic (which it has, see part e.)

### d. problem-specific (8-tile) helper functions and Problem object instantiation

We add analytical functions that locate the empty tile, the moving tiles per each action, print summary of an algorithm’s run and so on. A state is a 1-D tuple of 9 integers.

The transition model allows performing action “Left”, if the coordinates of the tile to the right of the current 0-tile, are within the board’s bounds. this is implemented with:

```python
movers_offset_from_zero_dict = {
    "Left": (0,1),
    "Right": (0,-1),
    "Up": (1,0),
    "Down": (-1,0)
}
```

This dictionary specifies, for each action, in which offset from the 0-tile, is the tile that is going to move as a consequence of the action. only if such coordinates (the 0 tile offsetted by the offset) exist within the boards bounds, is this action considered legal. finally, we pass the transition function, cost function, etc. to the constructor of the Problem object.

### e. the custom heuristic function

The custom heuristic function: my heuristic is an "enhanced" manhattan distance, that tries to predict simple horizontal (only!) collisions and take them into account.

my method is: Manhattan + 2 * (how many rows, contain at least one pair of tiles that have to "cross" each other to reach their destination). My idea is, that if a row has such a conflict, at least one of the tiles involved will have to give way, and consequently go, at least, once up and once down, to give way and then return to its home row. That is +2 moves on top of Manhattan distance. This proves admissibility.

In addition, because we count at most 1 collision in each row, we can infer that h(n) <= 1 + h(n'). That is because each move reduces, at most, 2 from the heuristic value for resolving a conflict (nothing if there are still conflicts on that same row), and on top of that, it increases the cost so far (g(n)) by 1 and increases the base Manhattan distance of the tile that gave way by 1. so that h(n') is smaller by, at most, 1 compared to h(n). This proves consistency.

Finally, is always higher than Manhattan’s so it is more informed. We could also try and take into account column-collisions, but this complicates the proof, so I decided to leave it out (since i already found a more informed, consistent heuristic already).

### f. A main function

A main function that reads arguments from the command line, and the runs and prints the results of BFS and A* (the latter with my custom heuristic), on the corresponding 8-tile instance.

## Running A* with my custom heuristic on the input

```text
0 7 8
2 1 5
6 4 3
```

to calculate, we look for rows with tiles that are at their destination row, but have colliding paths.

- row 0: none of 7,8 is at its final row
- row 1: only 5 is at its final row
- row 2 : only 6 is at its final row.

right here, the heuristic value for this state is exactly manhatten’s. it does not improve upon manhatten.

i will now show another example, where my heuristic gives a higher value than manhatten’s alone:

```text
2 1 5
6 4 3
0 7 8
```

- row 0: 1 and 2 are both at their destination row, and they are in reverse order +2
- row 1:6 and 4 are both at their destination row in reverse order +2
- row 2: 7 and 8 are in their destination row but not reversed +0.

in conclusion, my heuristic will value this state as (Manhattan distance + 4)
