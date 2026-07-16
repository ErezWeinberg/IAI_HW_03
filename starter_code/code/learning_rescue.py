"""Student implementation file for HW3 Part C.

Only edit this file unless course staff explicitly instruct otherwise.
"""

from __future__ import annotations

import math
import random
from collections import defaultdict
from typing import Any, Callable

from rescue_env import RescueEnv
from rescue_types import Action, State

AlphaSchedule = Callable[[int], float]
EpsilonSchedule = Callable[[int], float]


def estimate_transition_reward_model(
    trajectories: list[dict[str, Any]],
    actions: tuple[Action, ...],
    smoothing: float,
) -> dict[str, Any]:
    """Estimate P_hat and R_hat from offline transitions.

    The input trajectories list contains dictionaries with:
        state, action, reward, next_state, done

    Use Laplace smoothing for transition probabilities over the next states
    observed for each (state, action) pair. For each observed
    (state, action, next_state), use the mean observed reward for that triple.

    Return exactly this dictionary schema:
        {
            "transitions": {
                (state, action): [(probability, next_state, mean_reward), ...],
                ...
            },
            "actions_by_state": {
                state: (action1, action2, ...),
                ...
            },
            "states": (state1, state2, ...),
            "actions": actions,
        }

    Store actions in the same order as the actions argument. Store transition
    lists in a deterministic order, for example sorted by repr(next_state).
    States or actions with no observations should not invent transitions.
    """
    all_states = set()
    state_actions_map = defaultdict(set)
    grouped = defaultdict(list)

    for traj in trajectories:
        s = traj["state"]
        a = traj["action"]
        ns = traj["next_state"]
        r = traj["reward"]

        all_states.add(s)
        all_states.add(ns)
        state_actions_map[s].add(a)
        grouped[(s, a)].append((ns, r))

    transitions = {}
    for (s, a), obs in grouped.items():
        ns_counts = defaultdict(int)
        ns_rewards = defaultdict(list)
        for ns, r in obs:
            ns_counts[ns] += 1
            ns_rewards[ns].append(r)

        total_count = len(obs)
        K = len(ns_counts)

        prob_list = []
        for ns in ns_counts:
            count = ns_counts[ns]
            prob = (count + smoothing) / (total_count + smoothing * K)
            mean_r = sum(ns_rewards[ns]) / len(ns_rewards[ns])
            prob_list.append((prob, ns, mean_r))

        prob_list.sort(key=lambda x: repr(x[1]))
        transitions[(s, a)] = prob_list

    states = tuple(sorted(all_states))

    actions_by_state = {}
    for s in states:
        if s in state_actions_map:
            obs_actions = state_actions_map[s]
            ordered = tuple(act for act in actions if act in obs_actions)
            actions_by_state[s] = ordered

    return {
        "transitions": transitions,
        "actions_by_state": actions_by_state,
        "states": states,
        "actions": actions,
    }


def plan_with_estimated_model(
    model: dict[str, Any],
    start_state: State,
    horizon: int,
) -> dict[int, dict[State, Action]]:
    """Run finite-horizon planning on the learned model.

    Use the model schema returned by estimate_transition_reward_model. A state
    with no actions in actions_by_state should be treated as terminal with
    value 0. Break exact action-value ties according to the action order stored
    in model["actions"].
    """
    V = {t: {} for t in range(horizon + 1)}
    policy = {t: {} for t in range(1, horizon + 1)}

    for s in model["states"]:
        if s[4] == 0:
            V[0][s] = 0.0

    for t in range(1, horizon + 1):
        for s in model["states"]:
            if s[4] != t:
                continue

            actions = model["actions_by_state"].get(s, ())
            if not actions:
                V[t][s] = 0.0
            else:
                best_action = None
                best_value = -float("inf")

                for action in actions:
                    val = 0.0
                    transitions_list = model["transitions"].get((s, action), [])
                    for prob, next_state, reward in transitions_list:
                        val += prob * (reward + V[t - 1].get(next_state, 0.0))

                    # Round to 8 decimal places for stable tie-breaking
                    val = round(val, 8)

                    if val > best_value:
                        best_value = val
                        best_action = action

                if best_action is not None:
                    V[t][s] = best_value
                    policy[t][s] = best_action
                else:
                    V[t][s] = 0.0

    return policy


def first_visit_mc(
    env: RescueEnv,
    policy: dict[int, dict[State, Action]] | dict[State, Action],
    n_episodes: int,
    gamma: float,
    seed: int,
) -> dict[State, float]:
    """Estimate V^pi from sampled episodes using first-visit Monte Carlo.

    Use random.Random(seed) to generate a fresh deterministic seed for each
    episode; do not pass the same seed to every rollout.
    """
    state_returns = defaultdict(list)
    rng = random.Random(seed)
    episode_seeds = [rng.randint(0, 2**31 - 1) for _ in range(n_episodes)]

    for ep_seed in episode_seeds:
        result = env.simulate(policy, seed=ep_seed)
        trajectory = result["trajectory"]

        G = 0.0
        first_visits = []
        for step in reversed(trajectory):
            state, action, reward, next_state, done = step
            G = reward + gamma * G
            first_visits.append((state, G))

        visited = set()
        for state, g in reversed(first_visits):
            if state not in visited:
                visited.add(state)
                state_returns[state].append(g)

    V = {}
    for state, returns in state_returns.items():
        V[state] = sum(returns) / len(returns)

    return V


def td_prediction(
    env: RescueEnv,
    policy: dict[int, dict[State, Action]] | dict[State, Action],
    n_episodes: int,
    alpha_schedule: AlphaSchedule,
    gamma: float,
    seed: int,
) -> dict[State, float]:
    """Estimate V^pi from online interaction using TD(0).

    Count TD updates from t=0 upward when calling alpha_schedule(t). Use a fresh
    deterministic episode seed derived from seed for each episode.
    """
    V = defaultdict(float)
    rng = random.Random(seed)
    episode_seeds = [rng.randint(0, 2**31 - 1) for _ in range(n_episodes)]

    def get_action(pol, st):
        if callable(pol):
            return pol(st)
        time_remaining = st[4]
        if time_remaining in pol:
            action = pol[time_remaining].get(st)
            if action is not None:
                return action
            return env.actions(st)[0]
        action = pol.get(st)
        if action is not None:
            return action
        return env.actions(st)[0]

    update_count = 0
    for ep_seed in episode_seeds:
        state = env.reset(seed=ep_seed)
        while not env.is_terminal(state):
            action = get_action(policy, state)
            next_state, reward, done, _ = env.step(action)

            alpha = alpha_schedule(update_count)
            next_val = 0.0 if env.is_terminal(next_state) else V[next_state]
            V[state] = V[state] + alpha * (reward + gamma * next_val - V[state])

            update_count += 1
            state = next_state

    return dict(V)


def q_learning_rescue(
    env: RescueEnv,
    n_episodes: int,
    alpha_schedule: AlphaSchedule,
    epsilon_schedule: EpsilonSchedule,
    gamma: float,
    seed: int,
) -> tuple[dict[tuple[State, Action], float], dict[State, Action]]:
    """Learn a tabular Q policy with epsilon-greedy exploration.

    Count Q updates from t=0 upward when calling alpha_schedule(t) and
    epsilon_schedule(t). During exploration, choose uniformly from all legal
    env.actions(state). Break greedy ties using env.actions(state) order.
    """
    Q = defaultdict(float)
    master_rng = random.Random(seed)
    episode_seeds = [master_rng.randint(0, 2**31 - 1) for _ in range(n_episodes)]

    update_count = 0
    for ep_seed in episode_seeds:
        ep_rng = random.Random(ep_seed)
        state = env.reset(seed=ep_seed)

        while not env.is_terminal(state):
            eps = epsilon_schedule(update_count)
            actions = env.actions(state)
            if not actions:
                break

            if ep_rng.random() < eps:
                action = ep_rng.choice(actions)
            else:
                action = actions[0]
                best_q = Q.get((state, action), 0.0)
                for act in actions[1:]:
                    q_val = Q.get((state, act), 0.0)
                    if q_val > best_q:
                        best_q = q_val
                        action = act

            next_state, reward, done, _ = env.step(action)

            alpha = alpha_schedule(update_count)

            if env.is_terminal(next_state):
                max_next_q = 0.0
            else:
                next_actions = env.actions(next_state)
                if next_actions:
                    max_next_q = max(Q.get((next_state, a), 0.0) for a in next_actions)
                else:
                    max_next_q = 0.0

            old_q = Q.get((state, action), 0.0)
            Q[(state, action)] = old_q + alpha * (reward + gamma * max_next_q - old_q)

            update_count += 1
            state = next_state

    policy = {}
    visited_states = set(s for s, a in Q.keys())
    for s in visited_states:
        actions = env.actions(s)
        if actions:
            best_act = actions[0]
            best_q = Q.get((s, best_act), 0.0)
            for act in actions[1:]:
                q_val = Q.get((s, act), 0.0)
                if q_val > best_q:
                    best_q = q_val
                    best_act = act
            policy[s] = best_act

    return dict(Q), policy


def boltzmann_action(
    Q: dict[tuple[State, Action], float],
    state: State,
    actions: tuple[Action, ...],
    temperature: float,
) -> Action:
    """Sample an action according to softmax(Q(state, action) / temperature).

    Use the Python random module for sampling. Subtract the largest scaled
    Q-value before exponentiating for numerical stability.
    """
    q_vals = [Q.get((state, a), 0.0) for a in actions]
    scaled = [q / temperature for q in q_vals]
    max_val = max(scaled)
    exp_vals = [math.exp(s - max_val) for s in scaled]
    sum_exp = sum(exp_vals)
    probs = [e / sum_exp for e in exp_vals]

    return random.choices(actions, weights=probs)[0]


def evaluate_rescue_agent(
    env: RescueEnv,
    policy: dict[int, dict[State, Action]] | dict[State, Action],
    n_episodes: int,
    seed: int,
) -> dict[str, Any]:
    """Return success rate, mean return, mean length, and failure breakdown.

    Use random.Random(seed) to generate a fresh deterministic seed for each
    evaluation episode. If a learned policy has no action for a reachable state,
    the provided environment uses its first legal action as a deterministic
    fallback.
    """
    rng = random.Random(seed)
    episode_seeds = [rng.randint(0, 2**31 - 1) for _ in range(n_episodes)]

    total_return = 0.0
    total_length = 0
    success_count = 0
    failure_breakdown = {"danger": 0, "battery": 0, "timeout": 0}

    for ep_seed in episode_seeds:
        result = env.simulate(policy, seed=ep_seed)
        total_return += result["return"]
        total_length += result["length"]
        reason = result["terminal_reason"]
        if reason == "success":
            success_count += 1
        elif reason in failure_breakdown:
            failure_breakdown[reason] += 1

    return {
        "success_rate": success_count / n_episodes,
        "mean_return": total_return / n_episodes,
        "mean_length": total_length / n_episodes,
        "failure_breakdown": failure_breakdown,
    }


def default_alpha_schedule(t: int) -> float:
    """Alpha schedule required by the assignment."""

    return 0.5 / (1 + (t // 1000))


def constant_epsilon(_: int) -> float:
    return 0.1


def decaying_epsilon(t: int) -> float:
    return max(0.02, 1 / ((t + 1) ** 0.5))
