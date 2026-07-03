"""Student implementation file for HW3 Part B.

Only edit this file unless course staff explicitly instruct otherwise.
"""

from __future__ import annotations

from typing import Any

from rescue_env import RescueEnv
from rescue_types import Action, State


def action_value(env: RescueEnv, V_next: dict[State, float], state: State, action: Action) -> float:
    """Return the one-step finite-horizon backup for one action.

    Formula:
        sum_{s'} P(s' | s,a) * (R(s,a,s') + V_next[s'])

    Missing states in V_next must be treated as having value 0.0. This is
    useful for terminal states and for tiny public tests.
    """

    raise NotImplementedError


def finite_horizon_dp(env: RescueEnv, horizon: int) -> tuple[dict[int, dict[State, float]], dict[int, dict[State, Action]]]:
    """Return V[t][s] and a time-dependent policy pi[t][s].

    The state already includes time_remaining. Use env.reachable_states(horizon)
    once, then group reachable states by s[4]. V[t] should contain states whose
    embedded time_remaining is t.

    V[0][s] should be 0 for every reachable state with no time remaining.
    For t >= 1, use the finite-horizon Bellman recursion over env.actions(s).
    Terminal states should have value 0 and should not appear in the policy.

    If two actions have exactly the same value, choose the action that appears
    earlier in env.actions(s). This makes public and hidden tests deterministic.

    The returned policy should contain entries for t=1,...,horizon.
    """

    raise NotImplementedError


def rollout_time_dependent_policy(
    env: RescueEnv,
    policy: dict[int, dict[State, Action]],
    n_episodes: int,
    seed: int,
) -> dict[str, Any]:
    """Simulate a time-dependent policy and return summary statistics.

    Use random.Random(seed) to generate a fresh deterministic seed for each
    episode; do not pass the same seed to every rollout.

    Expected return keys:
        mean_return, success_rate, mean_length, failure_breakdown, returns
    """

    raise NotImplementedError


def compare_policy_slices(
    env: RescueEnv,
    policy: dict[int, dict[State, Action]],
    states_to_show: list[State],
) -> list[dict[str, Any]]:
    """Return a compact table of policy changes for selected states.

    Include only policy entries that exist for the supplied states. Each row can
    be a dictionary such as:
        {"state": state, "actions_by_time": {t: action, ...}}
    """

    raise NotImplementedError
