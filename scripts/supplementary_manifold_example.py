# -*- coding: utf-8 -*-
"""
Minimal working example of the HoloAuditor manifold-construction and audit pipeline
(toy scale: 10 entities / 3 types / embedding dim 3; production scale: 1,851 / 31+ / 64).

Pipeline (matches Methods):
  (1) build the clinical ontology graph W over 3 entity types (symptom/syndrome/herb)
  (2) normalised Laplacian L = D^{-1/2} W D^{-1/2} variant used for embedding is
      L_sym = I - D^{-1/2} W D^{-1/2}; take the d smallest non-trivial eigenvectors
  (3) spectral embedding Z (n x d), rows L2-normalised
  (4) audit-time scoring of a query: symptom vector -> Gaussian-kernel topological
      proximity per candidate syndrome (Eq. 2) -> fusion with co-occurrence (alpha=0.6)
Seeded; runs anywhere numpy exists.
"""
import numpy as np

rng = np.random.default_rng(7)

# ------------------------------------------------------------------
# (0) Toy ontology: 10 entities, 3 types.
#     0-2  symptoms  (S1 S2 S3)
#     3-6  syndromes (SY1 SY2 SY3 SY4)
#     7-9  herbs     (H1 H2 H3)
# ------------------------------------------------------------------
names = ["S1", "S2", "S3", "SY1", "SY2", "SY3", "SY4", "H1", "H2", "H3"]
types = ["sym"] * 3 + ["syn"] * 4 + ["herb"] * 3
n = len(names)

# weighted edges: symptom-syndrome (clinical mapping) and syndrome-herb (formula logic)
edges = [(0, 3, 0.9), (0, 4, 0.4), (1, 3, 0.5), (1, 5, 0.8), (2, 5, 0.7),
         (2, 6, 0.3), (3, 7, 0.9), (4, 7, 0.6), (5, 8, 0.8), (6, 9, 0.5),
         (3, 4, 0.2), (5, 6, 0.3)]

W = np.zeros((n, n))
for i, j, w in edges:
    W[i, j] = W[j, i] = w

# ------------------------------------------------------------------
# (1)-(2) Laplacian and spectral embedding
# ------------------------------------------------------------------
deg = W.sum(axis=1)
Dm = np.diag(deg)
L = Dm - W                                   # unnormalised Laplacian
dinv = np.where(deg > 0, 1.0 / np.sqrt(np.maximum(deg, 1e-12)), 0.0)
Lsym = np.eye(n) - (dinv[:, None] * W * dinv[None, :])   # symmetric normalised

d = 3                                        # production uses 64
vals, vecs = np.linalg.eigh(Lsym)
Z = vecs[:, 1:d + 1]                         # skip the trivial eigenvector
Z /= np.linalg.norm(Z, axis=1, keepdims=True)  # rows to the unit sphere
print("embedding Z (10 x %d), rows L2-normalised:" % d)
print(np.round(Z, 3))

# ------------------------------------------------------------------
# (3)-(4) audit-time scoring of one query
# ------------------------------------------------------------------
# query = patient with symptoms S1 + S2 (weights 1.0); query embedding = mean of
# the symptom rows (production: synonym-expanded weighted average, same idea).
q_idx = [0, 1]
z_in = Z[q_idx].mean(axis=0)
z_in /= np.linalg.norm(z_in)

alpha, sigma = 0.6, 1.0
cooc = {"SY1": 0.30, "SY2": 0.10, "SY3": 0.05, "SY4": 0.00}   # normalised co-occurrence

print("\naudit-time scoring of the query (alpha=%.2f, sigma=%.1f):" % (alpha, sigma))
print("%-6s %8s %8s %8s" % ("syn", "topo", "cooc", "score"))
scores = {}
for si in range(3, 7):
    syn = names[si]
    topo = float(np.exp(-np.linalg.norm(z_in - Z[si]) ** 2 / sigma ** 2))
    c = cooc.get(syn, 0.0)
    s = alpha * c + (1 - alpha) * topo
    scores[syn] = s
    print("%-6s %8.3f %8.3f %8.3f" % (syn, topo, c, s))

ranked = sorted(scores, key=scores.get, reverse=True)
print("\nre-ranked candidates:", ranked)
print("top-1 =", ranked[0], "| audit decision computed deterministically")
