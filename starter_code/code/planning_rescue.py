"""Student implementation file for HW3 Part B.

Only edit this file unless course staff explicitly instruct otherwise.
"""

from __future__ import annotations

import random
from collections import defaultdict
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
    val = 0.0
    for prob, next_state, reward in env.transitions(state, action):
        val += prob * (reward + V_next.get(next_state, 0.0))
    return round(val, 8)


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
    V = {t: {} for t in range(horizon + 1)}
    policy = {t: {} for t in range(1, horizon + 1)}

    states_by_t = defaultdict(list)
    for s in env.reachable_states(horizon):
        states_by_t[s[4]].append(s)

    for s in states_by_t[0]:
        V[0][s] = 0.0

    for t in range(1, horizon + 1):
        for s in states_by_t[t]:
            if env.is_terminal(s):
                V[t][s] = 0.0
            else:
                best_action = None
                best_value = -float("inf")
                for action in env.actions(s):
                    val = action_value(env, V[t - 1], s, action)
                    if val > best_value:
                        best_value = val
                        best_action = action
                V[t][s] = best_value
                policy[t][s] = best_action

    return V, policy


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
    rng = random.Random(seed)
    episode_seeds = [rng.randint(0, 2**31 - 1) for _ in range(n_episodes)]

    total_return = 0.0
    total_length = 0
    success_count = 0
    failure_breakdown = {"danger": 0, "battery": 0, "timeout": 0}
    returns = []

    for ep_seed in episode_seeds:
        result = env.simulate(policy, seed=ep_seed)
        ret = result["return"]
        returns.append(ret)
        total_return += ret
        total_length += result["length"]
        reason = result["terminal_reason"]
        if reason == "success":
            success_count += 1
        elif reason in failure_breakdown:
            failure_breakdown[reason] += 1

    return {
        "mean_return": total_return / n_episodes,
        "success_rate": success_count / n_episodes,
        "mean_length": total_length / n_episodes,
        "failure_breakdown": failure_breakdown,
        "returns": returns,
    }


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
    results = []
    for state in states_to_show:
        actions_by_time = {}
        for t in sorted(policy.keys()):
            if state in policy[t]:
                actions_by_time[t] = policy[t][state]
        if actions_by_time:
            results.append({
                "state": state,
                "actions_by_time": actions_by_time
            })
    return results
