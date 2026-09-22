"""Generate three demo matrices: a covariance, a graph Laplacian, a stiffness-like SPD."""
import numpy as np
from pathlib import Path

out = Path(__file__).parent
rng = np.random.default_rng(42)

# 1. covariance: X^T X / m, mildly ill-conditioned
X = rng.standard_normal((200, 24)) @ np.diag(np.logspace(0, -2, 24))
np.save(out / "covariance.npy", X.T @ X / 200)

# 2. graph Laplacian: ring + chords, PSD with one zero eigenvalue
n = 30
L = np.zeros((n, n))
edges = [(i, (i + 1) % n) for i in range(n)] + [(i, (i + 7) % n) for i in range(n)]
for i, j in edges:
    L[i, i] += 1; L[j, j] += 1; L[i, j] -= 1; L[j, i] -= 1
np.save(out / "laplacian.npy", L)

# 3. stiffness-like SPD: diagonally dominant
B = rng.standard_normal((16, 16))
S = B @ B.T + 16 * np.eye(16)
np.save(out / "stiffness.npy", S)

print("wrote", sorted(p.name for p in out.glob("*.npy")))
