19/11/2026

Hi, following is an overview of my solution for maman 01 - implement AI search algorithms, BFS, A* and the 8-Tiles Problem.

## 1. Usage

```text
Tiles.py <a space separated permutation of 0 to 8>
```

## 2. Overview

This program defines modular classes and functions that simulate formal problems, search algorithms, and allow plugging different actual instances of the problem with different algorithms and view [...]

## 3. Code structure

### a. The `Problem` class

The `Problem` class is an abstract representation of a problem via attributes such as possible actions, transition model, cost function, and an initial state.

Each problem has a format for representing states, with a unique key for each state.

### b. The `Node` class

The `Node` class is modular infrastructure for a search algorithm. It tracks the paths in an ongoing solution, so that we can:

- Backtrack
- Assess the cost
- Compare alternative further steps during the search

The state of the node is stored as a tuple because it acts as the key to identify a unique state of the problem.

### c. Search algorithms

The search algorithms are BFS and A*.

- **BFS** is implemented with `deque` (a FIFO queue) as the frontier and a Python `set` as the reached set.
- **A*** is implemented with `heapq` as the frontier and a Python dictionary as the reached set.

> A* can handle both consistent and inconsistent heuristics, provided that they are admissible.

There is an issue with removing elements from `heapq` that hurts performance. It is resolved with a mechanism that checks whether a better-cost node has already been found before trying to expand any node.

**Optimality:** Both algorithms return an optimal solution:

- BFS is inherently optimal.
- A* is optimal when paired with an admissible heuristic.

### d. 8-Tile helper functions and `Problem` instantiation

Problem-specific helper functions and `Problem` object instantiation are added by:

- Adding analytical functions that locate the empty tile
- Determining the moving tiles for each action
- Printing a summary of an algorithm
- Passing the transition function, cost function, and other components to the `Problem` constructor

A state is a one-dimensional tuple of nine integers:

```python
(0, 7, 8, 2, 1, 5, 6, 4, 3)
```

The transition model allows performing an action such as `"Left"` if the coordinates of the tile to the right of the current zero tile are within the board bounds.

```python
movers_offset_from_zero_dict = {
    "Left": (0, 1),
    "Right": (0, -1),
    "Up": (1, 0),
    "Down": (-1, 0)
}
```

This dictionary specifies, for each action, the offset from the zero tile of the tile that will move as a consequence of the action.

### e. Custom heuristic function

The custom heuristic is an "enhanced" Manhattan distance that tries to predict simple horizontal collisions and take them into account.

The heuristic is calculated as:

```text
Manhattan distance + 2 × number of rows containing at least one pair of tiles that have to cross each other to reach their destinations
```

If a row has such a conflict, at least one extra move is required to resolve it.

Because at most one collision is counted in each row, we can infer that:

```text
h(n) <= 1 + h(n')
```

This is because each move reduces, at most, `2` from the heuristic value for resolving a conflict.

Finally, the heuristic is always higher than Manhattan distance and is therefore more informed.

Column collisions could also be taken into account, but this complicates the proof, so they were left out.

### f. Main function

The main function reads arguments from the command line and then runs and prints the results of BFS and A* with the custom heuristic on the corresponding 8-Tile instance.

## 4. Example runs with the custom heuristic

Running A* with the custom heuristic on:

```text
0 7 8 2 1 5 6 4 3
```

produces the board:

```text
0 7 8
2 1 5
6 4 3
```

To calculate the heuristic, we look for rows containing tiles that are at their destination row but have colliding paths.

- **Row 0:** None of `7` or `8` is at their final row.
- **Row 1:** Only `5` is at its final row.
- **Row 2:** Only `6` is at its final row.

For this state, the heuristic value is exactly Manhattan distance. It does not improve upon Manhattan distance.

Here is another example where the heuristic gives a higher value than Manhattan distance:

```text
2 1 5
6 4 3
0 7 8
```

- **Row 0:** `1` and `2` are both at their destination row and in reverse order: `+2`
- **Row 1:** `6` and `4` are both at their destination row and in reverse order: `+2`
- **Row 2:** `7` and `8` are in their destination row but not reversed: `+0`

**Conclusion:** The heuristic values this state as:

```text
Manhattan distance + 4
```
