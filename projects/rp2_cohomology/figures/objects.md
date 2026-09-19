### The objects, concretely

![the triangulation](figures/triangulation.png)

**Vertices** are `Fin 6` = {0,…,5}. **Edges** are all 15 pairs, indexed by `edgePair : Fin 15 → Fin 6 × Fin 6`:

| e | e0 | e1 | e2 | e3 | e4 | e5 | e6 | e7 | e8 | e9 | e10 | e11 | e12 | e13 | e14 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| pair | 01 | 02 | 03 | 04 | 05 | 12 | 13 | 14 | 15 | 23 | 24 | 25 | 34 | 35 | 45 |

**Triangles** are the 10 triples in `triList : Fin 10 → Fin 6 × Fin 6 × Fin 6` (vertices listed increasing):

| t | t0 | t1 | t2 | t3 | t4 | t5 | t6 | t7 | t8 | t9 |
|---|---|---|---|---|---|---|---|---|---|---|
| triple | 012 | 013 | 024 | 035 | 045 | 125 | 134 | 145 | 234 | 235 |

Every edge lies in exactly two triangles (each column of δ¹ below has exactly two non-zero entries), every vertex
has degree 5, and 6 − 15 + 10 = 1 = χ(RP²). In the picture the five triangles containing vertex 0 form the central
pentagon; the other five are the "ears", and the outer boundary is glued to itself antipodally, which is why each
outer vertex label repeats a label from the pentagon.

**Cochains** with coefficients in a commutative ring R are functions `Fin 6 → R`, `Fin 15 → R`, `Fin 10 → R`
(a value on every vertex / edge / triangle). **Coboundary maps** are two explicit integer matrices, applied to a
cochain by `Matrix.mulVecLin` after casting entries into R (`d0lin R`, `d1lin R`).

`d0mat : Matrix (Fin 15) (Fin 6) ℤ` — row e = (a,b) has +1 at the head b and −1 at the tail a, so
(δ⁰f)(e) = f(b) − f(a):

| | v0 | v1 | v2 | v3 | v4 | v5 |
|---|---|---|---|---|---|---|
| **e0 (01)** | -1 | +1 | · | · | · | · |
| **e1 (02)** | -1 | · | +1 | · | · | · |
| **e2 (03)** | -1 | · | · | +1 | · | · |
| **e3 (04)** | -1 | · | · | · | +1 | · |
| **e4 (05)** | -1 | · | · | · | · | +1 |
| **e5 (12)** | · | -1 | +1 | · | · | · |
| **e6 (13)** | · | -1 | · | +1 | · | · |
| **e7 (14)** | · | -1 | · | · | +1 | · |
| **e8 (15)** | · | -1 | · | · | · | +1 |
| **e9 (23)** | · | · | -1 | +1 | · | · |
| **e10 (24)** | · | · | -1 | · | +1 | · |
| **e11 (25)** | · | · | -1 | · | · | +1 |
| **e12 (34)** | · | · | · | -1 | +1 | · |
| **e13 (35)** | · | · | · | -1 | · | +1 |
| **e14 (45)** | · | · | · | · | -1 | +1 |

`d1mat : Matrix (Fin 10) (Fin 15) ℤ` — row t = (i,j,k) is the signed boundary +[j,k] − [i,k] + [i,j], so
(δ¹g)(t) = g(jk) − g(ik) + g(ij):

| | e0 | e1 | e2 | e3 | e4 | e5 | e6 | e7 | e8 | e9 | e10 | e11 | e12 | e13 | e14 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **t0 (012)** | +1 | -1 | · | · | · | +1 | · | · | · | · | · | · | · | · | · |
| **t1 (013)** | +1 | · | -1 | · | · | · | +1 | · | · | · | · | · | · | · | · |
| **t2 (024)** | · | +1 | · | -1 | · | · | · | · | · | · | +1 | · | · | · | · |
| **t3 (035)** | · | · | +1 | · | -1 | · | · | · | · | · | · | · | · | +1 | · |
| **t4 (045)** | · | · | · | +1 | -1 | · | · | · | · | · | · | · | · | · | +1 |
| **t5 (125)** | · | · | · | · | · | +1 | · | · | -1 | · | · | +1 | · | · | · |
| **t6 (134)** | · | · | · | · | · | · | +1 | -1 | · | · | · | · | +1 | · | · |
| **t7 (145)** | · | · | · | · | · | · | · | +1 | -1 | · | · | · | · | · | +1 |
| **t8 (234)** | · | · | · | · | · | · | · | · | · | +1 | -1 | · | +1 | · | · |
| **t9 (235)** | · | · | · | · | · | · | · | · | · | +1 | · | -1 | · | +1 | · |

Two facts that drive the whole computation are visible in these tables:

- **δ¹ ∘ δ⁰ = 0** (`d1d0_int`, `d1_comp_d0`): each row of `d1mat` times `d0mat` cancels edge by edge.
- **Non-orientability.** Every column of `d1mat` has exactly two non-zero entries (each edge in two triangles),
  but their signs do not cancel: the column sums are [2, 0, 0, 0, -2, 2, 2, 0, -2, 2, 0, 0, 2, 2, 2]. On an orientable surface one could flip triangle
  orientations to make every column sum to 0; on RP² one cannot. That obstruction is exactly the torsion
  H² ≅ ℤ/2 over ℤ, detected in the proofs by the parity functional `phi2` (sum of all ten triangle coordinates)
  and by the witness cochain whose double is a coboundary while it is not.
