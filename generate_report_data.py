import json
import sys
from pathlib import Path

# Add code directory to path
code_dir = Path(__file__).resolve().parent / "starter_code" / "code"
sys.path.insert(0, str(code_dir))

from rescue_env import load_default_env, load_jsonl_transitions, RescueEnv
from planning_rescue import (
    finite_horizon_dp,
    rollout_time_dependent_policy,
    compare_policy_slices,
    action_value
)
from learning_rescue import (
    estimate_transition_reward_model,
    plan_with_estimated_model,
    first_visit_mc,
    td_prediction,
    q_learning_rescue,
    boltzmann_action,
    evaluate_rescue_agent,
    default_alpha_schedule,
    constant_epsilon,
    decaying_epsilon
)
from rescue_types import ACTIONS

def run_all_experiments():
    env = load_default_env(root=Path(__file__).resolve().parent / "starter_code")
    seed = 236501

    results = {}

    # --- PART B ---
    print("Running Part B Experiments...")
    part_b_horizons = [12, 20, 30]
    part_b_data = {}

    policies_b = {}
    V_b = {}

    for H in part_b_horizons:
        V, policy = finite_horizon_dp(env, horizon=H)
        policies_b[H] = policy
        V_b[H] = V

        start_state = env.initial_state(horizon=H)
        V_start = V[H].get(start_state, 0.0)
        reachable = env.reachable_states(horizon=H)
        reachable_count = len(reachable)

        eval_res = rollout_time_dependent_policy(env, policy, n_episodes=100, seed=seed)

        part_b_data[H] = {
            "horizon": H,
            "V_start": V_start,
            "reachable_states_count": reachable_count,
            "mean_return": eval_res["mean_return"],
            "success_rate": eval_res["success_rate"],
            "mean_length": eval_res["mean_length"],
            "failure_breakdown": eval_res["failure_breakdown"]
        }

    results["part_b_horizons"] = part_b_data

    # Part B Q3: Policy slices comparisons
    h20_policy = policies_b[20]
    tracked_slices = []
    for s in env.reachable_states(20):
        r, c, carrying, bat, t = s
        if (r, c) == (0, 0) and not carrying:
            tracked_slices.append(s)

    results["part_b_policy_slices"] = compare_policy_slices(env, h20_policy, tracked_slices[:10])

    # Part B Q4: Doubled/Quadrupled Hazard Penalty (-200 instead of -50)
    print("Running Part B Q4 (Hazard Penalty Experiment)...")
    env_hazard_high = load_default_env(root=Path(__file__).resolve().parent / "starter_code")
    env_hazard_high.danger_reward = -200.0 # 4x penalty
    V_high, policy_high = finite_horizon_dp(env_hazard_high, horizon=20)
    eval_high = rollout_time_dependent_policy(env_hazard_high, policy_high, n_episodes=100, seed=seed)
    eval_high_on_norm = rollout_time_dependent_policy(env, policy_high, n_episodes=100, seed=seed)

    results["part_b_q4_hazard_experiment"] = {
        "danger_reward": env_hazard_high.danger_reward,
        "V_start_high": V_high[20].get(env_hazard_high.initial_state(20), 0.0),
        "eval_on_high_env": eval_high,
        "eval_on_normal_env": eval_high_on_norm
    }


    # --- PART C ---
    print("Running Part C Experiments...")
    data_dir = Path(__file__).resolve().parent / "starter_code" / "data"
    sparse_train = load_jsonl_transitions(data_dir / "offline_rollouts_sparse_train.jsonl")
    good_train = load_jsonl_transitions(data_dir / "offline_rollouts_good_train.jsonl")

    # C1: Model learning on Sparse & Good data with lambda smoothing
    smoothings = [0.0, 0.1, 1.0]
    c_model_results = {"sparse": {}, "good": {}}

    for lam in smoothings:
        # Sparse
        m_sparse = estimate_transition_reward_model(sparse_train, ACTIONS, smoothing=lam)
        p_sparse = plan_with_estimated_model(m_sparse, env.initial_state(20), horizon=20)
        e_sparse = evaluate_rescue_agent(env, p_sparse, n_episodes=100, seed=seed)
        c_model_results["sparse"][str(lam)] = {
            "smoothing": lam,
            "num_transitions": len(m_sparse["transitions"]),
            "eval": e_sparse
        }

        # Good
        m_good = estimate_transition_reward_model(good_train, ACTIONS, smoothing=lam)
        p_good = plan_with_estimated_model(m_good, env.initial_state(20), horizon=20)
        e_good = evaluate_rescue_agent(env, p_good, n_episodes=100, seed=seed)
        c_model_results["good"][str(lam)] = {
            "smoothing": lam,
            "num_transitions": len(m_good["transitions"]),
            "eval": e_good
        }

    results["part_c_model_estimation"] = c_model_results

    # C3 & C4: MC vs TD(0) for fixed policy (Part B H=20 policy)
    print("Running MC and TD(0) prediction...")
    fixed_policy_h20 = policies_b[20]
    V_true_h20 = V_b[20]

    V_mc = first_visit_mc(env, fixed_policy_h20, n_episodes=400, gamma=1.0, seed=seed)
    V_td = td_prediction(env, fixed_policy_h20, n_episodes=400, alpha_schedule=default_alpha_schedule, gamma=1.0, seed=seed)

    sample_states_cmp = [
        (0, 0, False, 6, 20),
        (0, 0, False, 5, 19),
        (0, 0, False, 4, 18),
        (0, 0, False, 3, 17),
        (0, 0, False, 2, 16)
    ]
    mc_td_comparison = []
    for s in sample_states_cmp:
        t = s[4]
        true_val = V_true_h20[t].get(s, 0.0) if t in V_true_h20 else 0.0
        mc_val = V_mc.get(s, 0.0)
        td_val = V_td.get(s, 0.0)
        mc_td_comparison.append({
            "state": list(s),
            "true_dp": true_val,
            "mc_val": mc_val,
            "td_val": td_val,
            "diff_mc": abs(true_val - mc_val),
            "diff_td": abs(true_val - td_val)
        })

    results["part_c_mc_td_comparison"] = mc_td_comparison

    # C5: Q-learning (Constant vs Decaying Epsilon)
    print("Running Q-learning experiments...")
    Q_const, p_const = q_learning_rescue(
        env, n_episodes=1000, alpha_schedule=default_alpha_schedule,
        epsilon_schedule=constant_epsilon, gamma=1.0, seed=seed
    )
    e_const = evaluate_rescue_agent(env, p_const, n_episodes=150, seed=seed)

    Q_decay, p_decay = q_learning_rescue(
        env, n_episodes=1000, alpha_schedule=default_alpha_schedule,
        epsilon_schedule=decaying_epsilon, gamma=1.0, seed=seed
    )
    e_decay = evaluate_rescue_agent(env, p_decay, n_episodes=150, seed=seed)

    results["part_c_q_learning"] = {
        "constant_epsilon": {
            "visited_q_entries": len(Q_const),
            "eval": e_const
        },
        "decaying_epsilon": {
            "visited_q_entries": len(Q_decay),
            "eval": e_decay
        }
    }

    # C6: Boltzmann Exploration
    print("Running Boltzmann exploration experiments...")
    def q_learning_boltzmann(env, n_episodes, temp, seed):
        import random
        from collections import defaultdict
        Q = defaultdict(float)
        master_rng = random.Random(seed)
        episode_seeds = [master_rng.randint(0, 2**31 - 1) for _ in range(n_episodes)]

        update_count = 0
        for ep_seed in episode_seeds:
            env.reset(seed=ep_seed)
            state = env.initial_state(20)
            while not env.is_terminal(state):
                actions = env.actions(state)
                if not actions:
                    break
                action = boltzmann_action(Q, state, actions, temperature=temp)
                next_state, reward, done, _ = env.step(action)
                alpha = default_alpha_schedule(update_count)
                next_actions = env.actions(next_state)
                max_next_q = max([Q.get((next_state, a), 0.0) for a in next_actions]) if (not env.is_terminal(next_state) and next_actions) else 0.0
                old_q = Q.get((state, action), 0.0)
                Q[(state, action)] = old_q + alpha * (reward + 1.0 * max_next_q - old_q)
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
        return Q, policy

    Q_b10, p_b10 = q_learning_boltzmann(env, 1000, temp=1.0, seed=seed)
    e_b10 = evaluate_rescue_agent(env, p_b10, n_episodes=150, seed=seed)

    Q_b02, p_b02 = q_learning_boltzmann(env, 1000, temp=0.2, seed=seed)
    e_b02 = evaluate_rescue_agent(env, p_b02, n_episodes=150, seed=seed)

    results["part_c_boltzmann"] = {
        "temp_1_0": {"visited_q": len(Q_b10), "eval": e_b10},
        "temp_0_2": {"visited_q": len(Q_b02), "eval": e_b02}
    }

    results["decision_agent_comparison"] = {
        "oracle_planner": part_b_data[20],
        "estimated_model_planner_good": c_model_results["good"]["0.1"]["eval"],
        "estimated_model_planner_sparse": c_model_results["sparse"]["0.1"]["eval"],
        "q_learning_constant": e_const,
        "q_learning_decaying": e_decay,
        "boltzmann_temp_1_0": e_b10,
        "boltzmann_temp_0_2": e_b02
    }

    output_path = Path(__file__).resolve().parent / "report_data.json"
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"Successfully generated all report data and saved to {output_path}")

if __name__ == "__main__":
    run_all_experiments()
