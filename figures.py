#!/usr/bin/env python
"""Draw the RP² triangulation and tabulate the exact coboundary matrices, straight from the Lean definitions.
  python figures.py            # writes projects/rp2_cohomology/figures/{triangulation.png,objects.md} and splices objects.md into EXPLANATION.md
"""
import ast, math, re
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from lean_agent.config import Config
from lean_agent.checker import LeanChecker

PROJ = Path("projects/rp2_cohomology")
FIG = PROJ / "figures"; FIG.mkdir(exist_ok=True)

# ---- 1. ground truth from Lean -------------------------------------------------------------
lib = (PROJ / "library.lean").read_text()
defs = lib.split("def d0lin")[0].replace("import Mathlib", "", 1)
out = LeanChecker(Config()).probe(defs + """
#eval (List.ofFn fun i : Fin 15 => ((edgePair i).1.val, (edgePair i).2.val))
#eval (List.ofFn fun t : Fin 10 => let v := triList t; (v.1.val, v.2.1.val, v.2.2.val))
#eval (List.ofFn fun i : Fin 15 => List.ofFn fun j : Fin 6 => d0mat i j)
#eval (List.ofFn fun t : Fin 10 => List.ofFn fun e : Fin 15 => d1mat t e)
""")
blocks = [ast.literal_eval(b) for b in re.findall(r"^\[.*?\]$", out.replace("\n  ", " "), re.M | re.S)]
edges, tris, d0, d1 = blocks[0], blocks[1], blocks[2], blocks[3]
assert len(edges) == 15 and len(tris) == 10 and len(d0) == 15 and len(d1) == 10
eidx = {tuple(sorted(e)): k for k, e in enumerate(edges)}

# ---- 2. layout: star of vertex 0 as a pentagon, the other five triangles as outer ears --------
star = [t for t in tris if 0 in t]; outer = [t for t in tris if 0 not in t]
link_edges = [tuple(sorted(v for v in t if v != 0)) for t in star]
adj = {}
for a, b in link_edges:
    adj.setdefault(a, []).append(b); adj.setdefault(b, []).append(a)
cyc = [link_edges[0][0]]
while len(cyc) < 5:
    nxt = [v for v in adj[cyc[-1]] if v not in cyc]; cyc.append(nxt[0])
pos = {0: (0.0, 0.0)}
R1, R2 = 1.0, 2.05
for k, v in enumerate(cyc):
    a = math.radians(90 + 72 * k); pos[v] = (R1 * math.cos(a), R1 * math.sin(a))
ears = []  # (pentagon edge (a,b), apex label, apex position)
for k in range(5):
    a, b = cyc[k], cyc[(k + 1) % 5]
    apex = next(v for t in outer for v in t if set((a, b)) < set(t) and v not in (a, b))
    ang = math.radians(90 + 72 * k + 36); ears.append(((a, b), apex, (R2 * math.cos(ang), R2 * math.sin(ang))))

fig, ax = plt.subplots(figsize=(8.5, 8.5)); ax.set_aspect("equal"); ax.axis("off")
def seg(p, q, **kw): ax.plot([p[0], q[0]], [p[1], q[1]], **kw)
def mid(p, q, f=0.5): return (p[0] + f * (q[0] - p[0]), p[1] + f * (q[1] - p[1]))
def elabel(p, q, a, b, f=0.5, dx=0, dy=0):
    m = mid(p, q, f); ax.text(m[0] + dx, m[1] + dy, f"e{eidx[tuple(sorted((a, b)))]}", fontsize=9, color="#7a3e00",
                              ha="center", va="center", bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.9))
# faces: star (filled) and ears (filled lighter)
for t in star:
    pts = [pos[v] for v in t]; ax.fill(*zip(*pts), color="#dbe9f6", zorder=0)
for (a, b), apex, ap in ears:
    ax.fill(*zip(*[pos[a], pos[b], ap]), color="#f3e6f7", zorder=0)
# edges
for v in cyc: seg(pos[0], pos[v], color="k", lw=1.6); elabel(pos[0], pos[v], 0, v, 0.45, dx=0.08)
for k in range(5):
    a, b = cyc[k], cyc[(k + 1) % 5]; seg(pos[a], pos[b], color="k", lw=1.6); elabel(pos[a], pos[b], a, b)
for (a, b), apex, ap in ears:
    for v in (a, b):
        seg(pos[v], ap, color="k", lw=1.6, ls="--"); elabel(pos[v], ap, v, apex)
# triangle indices at centroids
def centroid(pts): return (sum(p[0] for p in pts) / 3, sum(p[1] for p in pts) / 3)
for t in tris:
    if 0 in t: c = centroid([pos[v] for v in t])
    else:
        (a, b), apex, ap = next(e for e in ears if set(e[0]) < set(t)); c = centroid([pos[a], pos[b], ap])
    ax.text(*c, f"t{tris.index(t)}\n({t[0]},{t[1]},{t[2]})", fontsize=8.5, ha="center", va="center", color="#333")
# vertices
for v, p in pos.items():
    ax.scatter(*p, s=520, color="#1f4e79", zorder=5); ax.text(*p, str(v), color="white", fontsize=12, ha="center", va="center", zorder=6, weight="bold")
for (a, b), apex, ap in ears:
    ax.scatter(*ap, s=520, facecolor="white", edgecolor="#1f4e79", lw=2, zorder=5); ax.text(*ap, str(apex), color="#1f4e79", fontsize=12, ha="center", va="center", zorder=6, weight="bold")
ax.set_title("The 6-vertex triangulation of RP² used in the Lean development\n"
             "filled vertices: the 6 vertices · hollow vertices: second copies of the same vertex (the outer boundary is glued antipodally)\n"
             "e_k = edge index in `edgePair`, t_k = triangle index in `triList`, dashed edges appear twice on the boundary", fontsize=9.5)
fig.tight_layout(); fig.savefig(FIG / "triangulation.png", dpi=170); print("wrote", FIG / "triangulation.png")

# ---- 3. objects.md: tables straight from the data ----------------------------------------
def mat_table(M, rows, cols):
    head = "| | " + " | ".join(cols) + " |\n|" + "---|" * (len(cols) + 1) + "\n"
    body = "\n".join("| **" + r + "** | " + " | ".join(("·" if x == 0 else f"{x:+d}") for x in row) + " |" for r, row in zip(rows, M))
    return head + body
colsum = [sum(d1[t][e] for t in range(10)) for e in range(15)]
nz = [sum(1 for t in range(10) if d1[t][e] != 0) for e in range(15)]
md = f"""### The objects, concretely

![the triangulation](figures/triangulation.png)

**Vertices** are `Fin 6` = {{0,…,5}}. **Edges** are all 15 pairs, indexed by `edgePair : Fin 15 → Fin 6 × Fin 6`:

| e | {' | '.join(f'e{k}' for k in range(15))} |
|---|{'---|' * 15}
| pair | {' | '.join(f'{a}{b}' for a, b in edges)} |

**Triangles** are the 10 triples in `triList : Fin 10 → Fin 6 × Fin 6 × Fin 6` (vertices listed increasing):

| t | {' | '.join(f't{k}' for k in range(10))} |
|---|{'---|' * 10}
| triple | {' | '.join(f'{a}{b}{c}' for a, b, c in tris)} |

Every edge lies in exactly two triangles (each column of δ¹ below has exactly two non-zero entries), every vertex
has degree 5, and 6 − 15 + 10 = 1 = χ(RP²). In the picture the five triangles containing vertex 0 form the central
pentagon; the other five are the "ears", and the outer boundary is glued to itself antipodally, which is why each
outer vertex label repeats a label from the pentagon.

**Cochains** with coefficients in a commutative ring R are functions `Fin 6 → R`, `Fin 15 → R`, `Fin 10 → R`
(a value on every vertex / edge / triangle). **Coboundary maps** are two explicit integer matrices, applied to a
cochain by `Matrix.mulVecLin` after casting entries into R (`d0lin R`, `d1lin R`).

`d0mat : Matrix (Fin 15) (Fin 6) ℤ` — row e = (a,b) has +1 at the head b and −1 at the tail a, so
(δ⁰f)(e) = f(b) − f(a):

{mat_table(d0, [f'e{k} ({a}{b})' for k, (a, b) in enumerate(edges)], [f'v{j}' for j in range(6)])}

`d1mat : Matrix (Fin 10) (Fin 15) ℤ` — row t = (i,j,k) is the signed boundary +[j,k] − [i,k] + [i,j], so
(δ¹g)(t) = g(jk) − g(ik) + g(ij):

{mat_table(d1, [f't{k} ({a}{b}{c})' for k, (a, b, c) in enumerate(tris)], [f'e{k}' for k in range(15)])}

Two facts that drive the whole computation are visible in these tables:

- **δ¹ ∘ δ⁰ = 0** (`d1d0_int`, `d1_comp_d0`): each row of `d1mat` times `d0mat` cancels edge by edge.
- **Non-orientability.** Every column of `d1mat` has exactly two non-zero entries (each edge in two triangles),
  but their signs do not cancel: the column sums are {colsum}. On an orientable surface one could flip triangle
  orientations to make every column sum to 0; on RP² one cannot. That obstruction is exactly the torsion
  H² ≅ ℤ/2 over ℤ, detected in the proofs by the parity functional `phi2` (sum of all ten triangle coordinates)
  and by the witness cochain whose double is a coboundary while it is not.
"""
(FIG / "objects.md").write_text(md); print("wrote", FIG / "objects.md")

# ---- 4. splice into EXPLANATION.md (replace the one-paragraph "The objects." if present) ----
ex = PROJ / "EXPLANATION.md"; text = ex.read_text()
if "### The objects, concretely" in text:
    text = re.sub(r"### The objects, concretely.*?(?=\n## )", md.rstrip() + "\n", text, flags=re.S)
else:
    text = re.sub(r"\*\*The objects\.\*\*.*?\n\n", "", text, count=1, flags=re.S)  # drop the short paragraph
    text = text.replace("\n## 2. How the development is organised", "\n" + md.rstrip() + "\n\n## 2. How the development is organised", 1)
ex.write_text(text); print("spliced into", ex)
