#13/11/2026

#imports
from collections.abc import Callable, Hashable
from dataclasses import dataclass

#the following class represents the properties of problem, without yet specifying how it would be solved
#it provides the states, transition model, and a cost function
@dataclass
class MyProblem[T : Hashable]: #T is the type of a representation of a single state
    initial_state : T
    is_target_state_fn : Callable[[T], bool] # could also do: targets_set : set[T]
    actions_tpl: tuple[str,...] #like ("Left", "Right",...). I could also make it a dictionary, and attach each string a Callable[[T],T], that is the essence of the action on a state
    # the following is the transition model, that is a function that applies an action on the current state (if legal),
    # and outputs the resulting state
    transition_fn: Callable[[T, str], T | None]
    cost_fn: Callable[[T, str, T], float] # params are (origin state, action's key, target state), and it returns a float that represents the cost for that specific transition.
    # we assume that the inputted parameters represent a legal transition (we have to pre-check for it)