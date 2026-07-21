import matplotlib.pyplot as plt
from pathlib import Path

out_dir = Path(__file__).resolve().parent / "math_imgs"
out_dir.mkdir(exist_ok=True)

math_formulas = {
    "bellman_eq": r"$V_t(s) = \max_{a \in A(s)} \sum_{s'} P(s' \mid s, a) \left[ R(s, a, s') + V_{t-1}(s') \right], \quad V_0(s) = 0$",
    "policy_eq": r"$\pi_t^*(s) = \arg\max_{a \in A(s)} \sum_{s'} P(s' \mid s, a) \left[ R(s, a, s') + V_{t-1}(s') \right]$",
    "risky_utility": r"$\mathbb{E}[U(\text{RISKY})] = 0.7 \cdot (20 - 2) + 0.3 \cdot (-20 - 2) = 12.6 - 6.6 = 6.0$",
    "safe_utility": r"$\mathbb{E}[U(\text{SAFE}, t=4)] = 1.0 \cdot (20 - 4) = 16.0 > 6.0$",
    "laplace_eq": r"$\hat{P}(s' \mid s, a) = \frac{N(s, a, s') + \lambda}{N(s, a) + \lambda K}$",
    "td0_update": r"$V(s) \leftarrow V(s) + \alpha \left[ r + \gamma V(s') - V(s) \right]$",
    "td0_calc": r"$V_{\text{new}}(s) = 4 + 0.25 \cdot (-2 + 0.9 \cdot 7 - 4) = 4.075$",
    "q_update": r"$Q(s, a) \leftarrow Q(s, a) + \alpha \left[ r + \gamma \max_{a'} Q(s', a') - Q(s, a) \right]$",
    "q_calc": r"$Q_{\text{new}}(s, a) = 1 + 0.2 \cdot (5 + 0.8 \cdot 3 - 1) = 2.28$",
    "eps_prob": r"$P(a \text{ non-greedy}) = \frac{\epsilon}{|A(s)|} = \frac{0.1}{5} = 0.02$",
    "mc_eq": r"$V_{\text{MC}}(s_0) = \frac{1}{N_{\text{ep}}} \sum_{i=1}^{N_{\text{ep}}} G_i = \frac{6 + 2 + 4}{3} = 4.0$",
    "knn_dist": r"$d(x, q) = \sqrt{(x_1 - q_1)^2 + (x_2 - q_2)^2}$",
    "minmax_norm": r"$x_{\text{norm}} = \frac{x - x_{\min}}{x_{\max} - x_{\min}}$",
    "boltzmann_eq": r"$P(a \mid s) = \frac{\exp\left(Q(s,a)/T\right)}{\sum_{b \in A(s)} \exp\left(Q(s,b)/T\right)}$"
}

for name, formula in math_formulas.items():
    fig = plt.figure(figsize=(7, 0.8))
    plt.text(0.5, 0.5, formula, fontsize=14, ha="center", va="center", color="#182B49")
    plt.axis("off")
    plt.tight_layout()
    img_path = out_dir / f"{name}.png"
    plt.savefig(img_path, dpi=300, bbox_inches="tight", transparent=True)
    plt.close(fig)

print(f"Pre-rendered {len(math_formulas)} math formulas into {out_dir}")
