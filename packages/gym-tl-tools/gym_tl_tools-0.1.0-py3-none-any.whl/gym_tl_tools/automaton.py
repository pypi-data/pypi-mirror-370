import re
from typing import Literal

import numpy as np
import spot
from pydantic import BaseModel
from spot import twa as Twa

from gym_tl_tools.parser import Parser


class Transition(BaseModel):
    """
    Represents a transition in a finite state automaton from a LTL formula.

    Attributes
    ----------
    next_state : int
        The next automaton state after the transition.
    condition : str
        The condition that triggers the transition represented as a Boolean expression.
        e.g. "psi_1 & psi_2" or "psi_1 | !psi_2".
    is_trapped_next : bool
        Indicates if the next state is a trap state (i.e., no further transitions are possible).
        Defaults to False.
    """

    condition: str
    next_state: int
    is_trapped_next: bool = False


class Predicate(BaseModel):
    """
    Represents a predicate in a TL formula.

    Attributes
    ----------
    name : str
        The name of the atomic predicate.
        e.g. "psi_goal_robot".
    formula : str
        The formula of the atomic predicate, which can be a Boolean expression.
        e.g. "d_robot_goal < 5".
    """

    name: str
    formula: str


class RobNextStatePair(BaseModel):
    """
    Represents a pair of robustness value and transition.

    Attributes
    ----------
    robustness : float
        The robustness value of the transition.
    next_state: int
        The next state of the automaton after the transition.
    """

    robustness: float
    next_state: int


class RobustnessCounter(BaseModel):
    robustness: float
    ind: int


class AutomatonStateCounter(BaseModel):
    state: int
    ind: int


class Edge:
    """
    Represents an edge in a finite state automaton from a LTL formula.
    Attributes
    ----------
    state : int
        The automaton state.
    transitions : list[Transition]
        The transitions from this state to other states.
    is_inf_zero_acc : bool
        Indicates if the edge has an Inf(0) acceptance condition.
    is_terminal_state : bool
        Indicates if the edge is a terminal state (i.e., no further transitions are possible).
    is_trap_state : bool
        Indicates if the edge is a trap state (i.e., all transitions lead to trap states).
    """

    def __init__(self, raw_state: str, atomic_pred_names: list[str]):
        """
        Parameters
        ----------
        raw_state : str
            The raw state string from the automaton in HOA format.
        atomic_pred_names : list[str]
            The names of the atomic predicates used in the transitions.
        """
        self.state: int = int(*re.findall("State: (\d).*\[", raw_state))
        self.transitions: list[Transition] = [
            Transition(
                condition=replace_atomic_pred_ids_to_names(
                    add_or_parentheses(re.findall("\[(.*)\]", transition)[0]),
                    atomic_pred_names,
                ),
                next_state=int(*re.findall("\[.*\] (\d)", transition)),
            )
            for transition in re.findall(
                "(\[.*\] \d+)\n", raw_state.replace("[", "\n[")
            )
        ]
        # Check if the edge has an Inf(0) acceptance condition
        self.is_inf_zero_acc = True if "{0}" in raw_state else False
        # Check if the edge is a terminal state. If so, elimite 't' transition
        # looping back to itself
        is_terminal_state: bool = True
        for i, transition in enumerate(self.transitions):
            if transition.next_state != self.state:
                is_terminal_state = False
            else:
                if transition.condition == "t":
                    self.transitions.pop(i)
                else:
                    pass
        self.is_terminal_state = is_terminal_state
        # A terminal state is a trap state if it doesn't have Inf(0) acceptance
        self.is_trap_state: bool = (
            True if not self.is_inf_zero_acc and self.is_terminal_state else False
        )


class Automaton:
    def __init__(
        self,
        tl_spec: str,
        atomic_predicates: list[Predicate],
        parser: Parser = Parser(),
    ) -> None:
        """
        Initialize the Automaton with a temporal logic specification and atomic predicates.
        Parameters
        ----------
        tl_spec : str
            The temporal logic specification in LTL format.
            e.g. "F(psi_1 & psi_2) | G(psi_3)".
        atomic_predicates : list[Predicate]
            A list of atomic predicates used in the temporal logic specification.
            Each predicate should be an instance of the Predicate class.
            e.g. [Predicate("psi_1", "d_robot_goal < 5"), Predicate("psi_2", "d_robot_goal < 10")].
        parser : Parser = gym_tl_tools.parser.Parser()
            An instance of the Parser class used to parse the temporal logic specification.
            Defaults to a new instance of Parser.
        """
        self.tl_spec: str = tl_spec
        self.atomic_predicates: list[Predicate] = atomic_predicates
        self.parser: Parser = parser

        aut: Twa = spot.translate(tl_spec, "Buchi", "state-based", "complete")
        aut_hoa: str = aut.to_str("hoa")
        self.num_states: int = int(aut.num_states())  # type: ignore
        self.start: int = int(*re.findall("Start: (\d+)\n", aut_hoa))

        num_used_aps: int = int(*re.findall('AP: (\d+) "', aut_hoa))
        used_aps: list[str] = (
            re.findall("AP: \d+ (.*)", aut_hoa)[0].replace('"', "").split()
        )
        if len(used_aps) != num_used_aps:
            raise ValueError(
                f"Number of used atomic predicates ({len(used_aps)}) does not match the number of atomic predicates in the automaton ({num_used_aps})."
            )
        else:
            self.used_aps: list[str] = used_aps

        self.acc_name: str = re.findall("acc-name: (.*)\n", aut_hoa)[0]
        self.acceptance: str = re.findall("Acceptance: (.*)\n", aut_hoa)[0]
        self.properties = re.findall("properties: (.*)\n", aut_hoa)

        aut_hoa_states = (
            aut_hoa.replace("\n", "")
            .replace("State", "\nState")
            .replace("--END--", "\n")
        )
        raw_states: list[str] = [
            raw_state + "\n" for raw_state in re.findall("(State:.*)\n", aut_hoa_states)
        ]

        untrapped_edges: list[Edge] = [
            Edge(raw_state, self.used_aps) for raw_state in raw_states
        ]

        # Check if a transition of an edge leads to a trap state and if all transitions
        # of an edge leads to a trap state (if so, this edge is also a trap state)
        trap_states: list[int] = [
            edge.state for edge in untrapped_edges if edge.is_trap_state
        ]
        goal_states: list[int] = []
        # for _ in range(len(untrapped_edges)):
        for i, edge in enumerate(untrapped_edges):
            if edge.is_trap_state:
                pass
            elif edge.is_inf_zero_acc and edge.is_terminal_state:
                # If the edge has Inf(0) acceptance and is a terminal state,
                # it is a goal state
                goal_states.append(edge.state)
            else:
                is_trapped_in_all_trans = True
                for j, transition in enumerate(edge.transitions):
                    if transition.next_state in trap_states:
                        if edge.is_inf_zero_acc:
                            edge.transitions.pop(j)
                            goal_states.append(edge.state)
                        else:
                            edge.transitions[j] = Transition(
                                condition=transition.condition,
                                next_state=transition.next_state,
                                is_trapped_next=True,
                            )
                    else:
                        is_trapped_in_all_trans = False

                if is_trapped_in_all_trans and edge.transitions:
                    untrapped_edges[i].is_trap_state = True
                    trap_states.append(edge.state)
                else:
                    pass

        self.goal_states: tuple[int, ...] = tuple(goal_states)
        self.trap_states: tuple[int, ...] = tuple(trap_states)
        self.edges: tuple[Edge, ...] = tuple(untrapped_edges)

    def reset(self, seed: int | None = None) -> None:
        """
        Reset the automaton to its initial state.
        """
        self.current_state: int = self.start
        self.status: Literal["intermediate", "goal", "trap"] = "intermediate"
        # Initialize Numpy RNG if a seed is provided
        self._np_rng: np.random.Generator = np.random.default_rng(seed)

    def step(
        self,
        var_value_dict: dict[str, float],
        terminal_state_reward: float = 5,
        state_trans_reward_scale: float = 100,
        dense_reward: bool = False,
        dense_reward_scale: float = 0.01,
    ) -> tuple[float, int]:
        """
        Step the automaton to the next state based on the current predicate values.
        This function updates the current state of the automaton based on the
        values of variables defining atomic predicates provided in `var_value_dict`.

        Parameters
        ----------
        var_value_dict : dict[str, float]
            A dictionary mapping the variable names used in the atomic predicate definitions
            to their current values.
            e.g. {"d_robot_goal": 3.0, "d_robot_obstacle": 1.0, "d_robot_goal": 0.5}.
        terminal_state_reward : float = 5


        Returns
        -------
        reward : float
            The reward for the current step.
        new_state : int
            The new automaton state.
        """

        if not hasattr(self, "current_state"):
            raise ValueError(
                " Error: The automaton has not been reset. Please call the reset() method before stepping."
            )

        ap_rob_dict: dict[str, float] = {
            atom_pred.name: self.parser.tl2rob(atom_pred.formula, var_value_dict)
            for atom_pred in self.atomic_predicates
        }

        reward, new_state = self.tl_reward(
            ap_rob_dict,
            self.current_state,
            terminal_state_reward=terminal_state_reward,
            state_trans_reward_scale=state_trans_reward_scale,
            dense_reward=dense_reward,
            dense_reward_scale=dense_reward_scale,
        )

        # Update the current state of the automaton
        self.current_state = new_state

        # Update the status of the automaton
        if new_state in self.goal_states:
            self.status = "goal"
        elif new_state in self.trap_states:
            self.status = "trap"
        else:
            self.status = "intermediate"

        return reward, new_state

    def tl_reward(
        self,
        ap_rob_dict: dict[str, float],
        curr_aut_state: int,
        terminal_state_reward: float = 5,
        state_trans_reward_scale: float = 100,
        dense_reward: bool = False,
        dense_reward_scale: float = 0.01,
    ) -> tuple[float, int]:
        """
        Calculate the reward of the step from a given automaton.

        Parameters
        ----------
        ap_rob_dict: dict[str, float]
            A dictionary mapping the names of atomic predicates to their robustness values.
        curr_aut_state: int
            The current state of the automaton.
        dense_reward: bool
            If True, the reward is calculated based on the maximum robustness of non-trap transitions.
        terminal_state_reward: float
            The reward given when the automaton reaches a terminal state.

        Returns
        -------
        reward : float
            The reward of the step based on the MDP and automaton states.
        next_aut_state : int
            The resultant automaton state after the step.
        """

        if curr_aut_state in self.goal_states:
            return (terminal_state_reward, curr_aut_state)
        elif curr_aut_state in self.trap_states:
            return (-terminal_state_reward, curr_aut_state)
        else:
            curr_edge = self.edges[curr_aut_state]
            transitions = curr_edge.transitions

            (
                pos_trap_rob_trans_pairs,
                pos_non_trap_rob_trans_pairs,
                zero_trap_rob_trans_pairs,
                zero_non_trap_rob_trans_pairs,
                non_trap_rob_trans_pairs,
            ) = self.transition_robustness(transitions, ap_rob_dict)

            trans_rob: float
            next_aut_state: int
            if len(pos_trap_rob_trans_pairs) == 1:
                # If there is only one positive transition robustness leading to a trap state
                trans_rob = pos_trap_rob_trans_pairs[0].robustness
                next_aut_state = pos_trap_rob_trans_pairs[0].next_state
            elif len(pos_non_trap_rob_trans_pairs) == 1:
                # If there is only one positive transition robustness leading to a non-trap state
                trans_rob = pos_non_trap_rob_trans_pairs[0].robustness
                next_aut_state = pos_non_trap_rob_trans_pairs[0].next_state
            elif zero_trap_rob_trans_pairs:
                # If there are no positive transition robustnesses, but there are zero transition robustnesses
                # leading to a trap state, select the first one
                trans_rob = zero_trap_rob_trans_pairs[0].robustness
                next_aut_state = zero_trap_rob_trans_pairs[0].next_state
            elif zero_non_trap_rob_trans_pairs:
                # If there are no positive transition robustnesses, but there are zero transition robustnesses
                # leading to a non-trap state, select the first one
                selected_index: int = int(
                    self._np_rng.integers(0, len(zero_non_trap_rob_trans_pairs))
                )
                trans_rob = zero_non_trap_rob_trans_pairs[selected_index].robustness
                next_aut_state = zero_non_trap_rob_trans_pairs[
                    selected_index
                ].next_state

            else:
                raise ValueError(
                    "Error: No singular positive or zero transition robustnesses found for the current automaton state.",
                    "Current automaton state:",
                    curr_aut_state,
                    "Positive trap transitions:",
                    pos_trap_rob_trans_pairs,
                    "Positive non-trap transitions:",
                    pos_non_trap_rob_trans_pairs,
                    "Zero trap transitions:",
                    zero_trap_rob_trans_pairs,
                    "Zero non-trap transitions:",
                    zero_non_trap_rob_trans_pairs,
                )

            # Calculate the reward
            reward: float
            # Weight for reward calculation
            # alpha: float = 0.7
            # beta: float = 0.5
            gamma: float = dense_reward_scale
            delta: float = state_trans_reward_scale

            if next_aut_state == curr_aut_state:
                # non_trap_robs.remove(trans_rob)
                # reward = -gamma * (
                #    beta * 1 / max(non_trap_robs) - (1 - beta) * 1 / max(trap_robs)
                # )

                # reward = gamma * (
                #    beta * 1 / max(non_trap_robs) - (1 - beta) * 1 / max(trap_robs)
                # )
                if dense_reward:
                    non_trap_robs: list[float] = [
                        pair.robustness for pair in non_trap_rob_trans_pairs
                    ]
                    # ] + [pair.robustness for pair in zero_non_trap_rob_trans_pairs]
                    non_trap_robs.remove(trans_rob)
                    reward = gamma * max(non_trap_robs)
                else:
                    reward = 0
            else:
                if next_aut_state not in self.trap_states:
                    reward = (
                        delta * trans_rob
                    )  # alpha * trans_rob - (1 - alpha) * max(trap_robs)
                elif next_aut_state in self.trap_states:
                    reward = (
                        -delta * trans_rob
                    )  # -(1 - alpha) * max(non_trap_robs) - alpha * trans_rob
                else:
                    raise ValueError(
                        "Error: the transition robustness doesn't exit in the robustness set."
                    )

            return reward, next_aut_state

    def transition_robustness(
        self,
        transitions: list[Transition],
        ap_rob_dict: dict[str, float],
    ) -> tuple[
        list[RobNextStatePair],
        list[RobNextStatePair],
        list[RobNextStatePair],
        list[RobNextStatePair],
        list[RobNextStatePair],
    ]:
        """
        Calculate the robustness of transitions in the automaton.
        This function computes the robustness values for each transition based on the
        conditions of the transitions and the robustness values of the atomic predicates.

        Parameters
        ----------
        transitions: list[Transition]
            A list of transitions in the automaton.
        ap_rob_dict: dict[str, float]
            A dictionary mapping the names of atomic predicates to their robustness values.

        Returns
        -------
        pos_trap_rob_trans_pairs : list[RobNextStatePair]
            A list of pairs of positive robustness values and transitions that lead to trap states.
        pos_non_trap_rob_trans_pairs : list[RobNextStatePair]
            A list of pairs of positive robustness values and transitions that do not lead to trap states.
        zero_trap_rob_trans_pairs : list[RobNextStatePair]
            A list of pairs of zero robustness values and transitions that lead to trap states.
        zero_non_trap_rob_trans_pairs : list[RobNextStatePair]
            A list of pairs of zero robustness values and transitions that do not lead to trap states.
        """

        robs: list[float] = []
        pos_trap_rob_trans_pairs: list[RobNextStatePair] = []
        pos_non_trap_rob_trans_pairs: list[RobNextStatePair] = []
        zero_trap_rob_trans_pairs: list[RobNextStatePair] = []
        zero_non_trap_rob_trans_pairs: list[RobNextStatePair] = []
        non_trap_rob_trans_pairs: list[RobNextStatePair] = []

        for trans in transitions:
            rob: float = self.parser.tl2rob(trans.condition, ap_rob_dict)
            robs.append(rob)
            match (rob, trans.is_trapped_next):
                case (0, True):
                    zero_trap_rob_trans_pairs.append(
                        RobNextStatePair(robustness=rob, next_state=trans.next_state)
                    )
                case (0, False):
                    zero_non_trap_rob_trans_pairs.append(
                        RobNextStatePair(robustness=rob, next_state=trans.next_state)
                    )
                    non_trap_rob_trans_pairs.append(
                        RobNextStatePair(robustness=rob, next_state=trans.next_state)
                    )

                case (rob, True) if rob > 0:
                    pos_trap_rob_trans_pairs.append(
                        RobNextStatePair(robustness=rob, next_state=trans.next_state)
                    )
                case (rob, False) if rob > 0:
                    pos_non_trap_rob_trans_pairs.append(
                        RobNextStatePair(robustness=rob, next_state=trans.next_state)
                    )
                    non_trap_rob_trans_pairs.append(
                        RobNextStatePair(robustness=rob, next_state=trans.next_state)
                    )
                case (rob, False) if rob < 0:
                    non_trap_rob_trans_pairs.append(
                        RobNextStatePair(robustness=rob, next_state=trans.next_state)
                    )
                case _:
                    pass
        return (
            pos_trap_rob_trans_pairs,
            pos_non_trap_rob_trans_pairs,
            zero_trap_rob_trans_pairs,
            zero_non_trap_rob_trans_pairs,
            non_trap_rob_trans_pairs,
        )

    @property
    def is_goaled(self) -> bool:
        """
        Check if the current state of the automaton is a goal state.
        Returns
        -------
        bool
            True if the current state is a goal state, False otherwise.
        """
        return self.status == "goal"

    @property
    def is_trapped(self) -> bool:
        """
        Check if the current state of the automaton is a trap state.
        Returns
        -------
        bool
            True if the current state is a trap state, False otherwise.
        """
        return self.status == "trap"

    @property
    def is_terminated(self) -> bool:
        """
        Check if the automaton is in a terminal state (goal or trap).
        Returns
        -------
        bool
            True if the automaton is in a terminal state, False otherwise.
        """
        return self.is_goaled or self.is_trapped


def add_or_parentheses(condition: str) -> str:
    or_locs: list[int] = [m.start() for m in re.finditer("\|", condition)]

    condition_list: list[str] = list(condition)

    new_condition: str = condition

    if or_locs:
        for loc in or_locs:
            if condition_list[loc - 1] == " " and condition_list[loc + 1] == " ":
                condition_list[loc - 1] = ")"
                condition_list[loc + 1] = "("
            else:
                pass
        new_condition = "(" + "".join(condition_list) + ")"
    else:
        pass

    return new_condition


def replace_atomic_pred_ids_to_names(condition: str, atom_prop_names: list[str]):
    spec: str = condition
    # Replace atomic props in numeric IDs to their actual names (ex. '0'->'psi_0')
    for i, atom_prop_name in enumerate(reversed(atom_prop_names)):
        target = str(len(atom_prop_names) - 1 - i)
        spec = spec.replace(target, atom_prop_name)

    return spec
