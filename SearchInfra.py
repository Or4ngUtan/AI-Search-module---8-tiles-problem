#13/11/2026

#imports
from collections.abc import Callable, Hashable
from dataclasses import dataclass
from collections import deque # for the fifo queue of bfs
from itertools import count
import heapq

from MyProblem import MyProblem


#this class defines a node-structure that is utilized by searching algorithms to document and track paths
@dataclass
class MySearchNode[T]:
    this_problem : MyProblem[T]
    parent : MySearchNode[T] | None
    from_action : str | None
    this_state : T
    is_target : bool
    total_cost : float

    def expandNode(self) -> list[MySearchNode[T]]:
        children_nodes = list()
        prblm = self.this_problem
        for action_name in prblm.actions_tpl:
            new_state = prblm.transition_fn(self.this_state, action_name)
            if(new_state is not None):
                new_is_target = prblm.is_target_state_fn(new_state)
                cost_delta = prblm.cost_fn(self.this_state, action_name, new_state)
                child_node = MySearchNode(
                                            this_problem=prblm,
                                            parent=self,
                                            from_action=action_name,
                                            this_state=new_state,
                                            is_target=new_is_target,
                                            total_cost=self.total_cost + cost_delta
                )
                children_nodes.append(child_node)
        return children_nodes

    #a static (non-instance) function that creates a root for a given problem
    @staticmethod
    def createRoot(this_problem : MyProblem[T]) -> MySearchNode[T]:
        return MySearchNode(
            this_problem=this_problem, 
            parent=None,
            from_action=None, 
            this_state=this_problem.initial_state, 
            is_target=this_problem.is_target_state_fn(this_problem.initial_state), 
            total_cost=0
        )

    #the following will show the path, including all states and actions that were chosen, ordered from beginning to end
    def showPath(self) -> list[tuple[T,str | None]]:
        ret_list = list()
        curr_node = self
        action_after = None
        #we will return tuples of (state, action that was taken *after* it)
        while curr_node is not None:
            ret_list.append((curr_node.this_state, action_after))
            action_after = curr_node.from_action
            curr_node = curr_node.parent

        ret_list.reverse()
        return ret_list

#now we define the main algorithms. bfs does not have a parameter of a heuristic function
#BFS is implemented with deque (FIFO queue) as the frontier, and a python set as the reached set
def bfs(problem : MyProblem) -> dict:
    root : MySearchNode = MySearchNode.createRoot(problem)
    if root.is_target:
        return {"sol-node" : root, "expand-count" : 0}

    frontier = deque([root])
    reached = {root.this_state} #a set, not a dict - BFS does not care what is the cost of the path that lead to a state
    #^ it simply has to know whether this state was ever "touched" or not
    expanded_count = 0
    while len(frontier) > 0:
        curr_node : MySearchNode = frontier.popleft()
        children_nodes = curr_node.expandNode()
        expanded_count += 1

        child : MySearchNode
        for child in children_nodes:
            if child.is_target:
                return {"sol-node" : child, "expand-count" : expanded_count}
            else:
                new_state = child.this_state
                if new_state not in reached:
                    reached.add(new_state)
                    frontier.append(child)
    return {"sol-node" : None, "expand-count" : expanded_count}

#A* is implemented with heapq as the frontier and a python dictionary {state-as-hashable : best-path-node-object} as the reached set
def aStar(problem : MyProblem, heur_fn : Callable[[Hashable], float]) -> dict:
    root : MySearchNode = MySearchNode.createRoot(problem)
    frontier = [] # a min heap [((priority, tie-breaker), value)]
    calc_heap_priority_fn  = lambda node: node.total_cost + heur_fn(node.this_state) # f(n) = g(n) + h(n)
    tie_breaker = count() #heapq throws an error if there are two items with same priority, so we must differentiate
    push_to_frontier_fn = lambda node: heapq.heappush(frontier, ((calc_heap_priority_fn(node), next(tie_breaker)), node))
    pop_from_frontier_fn = lambda: (heapq.heappop(frontier))[1]

    push_to_frontier_fn(root)
    reached = {root.this_state : root} #A* may handle both consistent and inconsistent heuristics
    #thus, the "reached" set must not only contain the state, but also the shortest path so far that lead to it.
    #thus we will use a dictionary {state : node}, and compare each time to update to the best path
    #we later implement a re-exploration of nodes that has been found to improve upon already discovered states
    expanded_count = 0
    while len(frontier) > 0:
        curr_node : MySearchNode =  pop_from_frontier_fn()
        #(**) heapq is complicated to remove nodes from, so we check that the cost is not greater than the one in 'reached'
        if curr_node.total_cost > reached[curr_node.this_state].total_cost:
            continue
        #in A*, we test for being a target state *before* expanding
        if curr_node.is_target:
            return {"sol-node" : curr_node, "expand-count" : expanded_count}

        children_nodes = curr_node.expandNode()
        expanded_count += 1 #as per the instructions: count anyway, even if leads to an already explored state

        child : MySearchNode
        for child in children_nodes:
            new_state = child.this_state
            #important:  we must compare the cost of this new path to the previous one, and re-explore if we found a better one
            if (new_state not in reached) or (reached[new_state].total_cost > child.total_cost):
                reached[new_state] = child
                #we could try and remove all previous nodes with the same state from heap, but heapq makes it complicated.
                #instead, we will add a check, before expanding, to see that the cost is not greater than the one in 'reached', see (**)
                push_to_frontier_fn(child)
    
    return {"sol-node" : None, "expand-count" : expanded_count}