# Plan: rp2_cohomology

21/21 lemmas proved · 13 definitions · spent $50.25 of $200.00 · replans 2

## Goal

Compute the simplicial cohomology of the real projective plane RP^2 from an explicit finite triangulation, fully formally in Lean 4 + Mathlib.

Required final theorems (the last nodes of the plan), for the cochain complex C^0 -> C^1 -> C^2 of the triangulation:
  1. Over ℤ:  H^0 ≅ ℤ,  H^1 = 0,  H^2 ≅ ZMod 2.
  2. Over ZMod 2:  H^0 ≅ ZMod 2,  H^1 ≅ ZMod 2,  H^2 ≅ ZMod 2.
Each H^k must be defined as an honest quotient (kernel of the coboundary modulo the image of the previous coboundary) or an equivalent concrete description proven equal to it, and the isomorphisms must be stated as `Nonempty (H^k ≃+ ℤ)`, `Nonempty (H^k ≃+ ZMod 2)`, or `Subsingleton H^k` (for the zero group), as additive group isomorphisms.

## Design guidance given to the planner

Use the standard 6-vertex triangulation of RP^2 (the hemi-icosahedron): vertices Fin 6, 15 edges (every pair of vertices), 10 triangles. Represent k-cochains as functions `Fin m → R` (m = 6, 15, 10) and the coboundary maps as explicit integer matrices `Matrix (Fin 15) (Fin 6) ℤ` and `Matrix (Fin 10) (Fin 15) ℤ` given by `!![...]` literals or by explicit `fun i j => ...` with a finite case table, mapped into R via `Matrix.map` or `Int.cast`. Then δ¹ ∘ δ⁰ = 0 is a finite computation (`decide`, or `ext i j; fin_cases i <;> fin_cases j <;> rfl`/`simp`). Cohomology can be defined as `(LinearMap.ker δ¹) ⧸ (LinearMap.range δ⁰).comap (LinearMap.ker δ¹).subtype` or via Mathlib's `Module` quotients; alternatively define it as a quotient of AddSubgroups. Prefer statements that can be closed by decide / simp / omega / norm_num / linarith and explicit witnesses; avoid needing Smith normal form. For the ℤ/2-torsion in H^2 over ℤ, exhibit the 2-cochain that is not a coboundary and show 2 times it is one, and show every 2-cochain is congruent mod coboundaries to 0 or that one. State small computational facts (e.g. the value of δ on each basis vector, the rank/kernel facts) as separate lemmas so each is a few lines. Use `open Matrix` and `open BigOperators` where helpful. IMPORTANT DESIGN RULE (learned): instance/defeq checking on `ZMod 2` is very slow in Lean (ZMod is defined by recursion), and specializing quotient constructions directly at R = ℤ or R = ZMod 2 causes `failed to synthesize instance` / heartbeat timeouts. So: prove every structural lemma (isomorphisms of H^k, quotient descriptions) GENERICALLY over `(R : Type) [CommRing R]` taking the concrete facts (witness cochain, surjectivity/injectivity-mod-image facts) as hypotheses, and make the final ℤ / ZMod 2 theorems one-line specializations, exactly as H0_equiv_R -> H0_int / H0_zmod2 did. Concrete computational facts (that a specific cochain is a cocycle, that c • u ∈ range ↔ 2 ∣ c, etc.) may be stated at the specific ring, but should avoid quotient types entirely.

## Nodes in dependency order

| # | | id | kind | what it says | depends on | attempts | cost |
|---:|---|---|---|---|---|---:|---:|
| 1 | ✅ | `opens` | def | Open namespaces for matrices and big operators. |  |  |  |
| 2 | ✅ | `d0` | def | Coboundary matrix δ⁰. | `opens` |  |  |
| 3 | ✅ | `triList` | def | The 10 triangles. | `opens` |  |  |
| 4 | ✅ | `edgeIdx` | def | Edge index of a pair. | `opens` |  |  |
| 5 | ✅ | `d1` | def | Coboundary matrix δ¹. | `opens`, `triList`, `edgeIdx` |  |  |
| 6 | ✅ | `d0lin` | def | δ⁰ as a linear map. | `d0` |  |  |
| 7 | ✅ | `d1lin` | def | δ¹ as a linear map. | `d1` |  |  |
| 8 | ✅ | `d1d0_int` | lemma | d1mat * d0mat = 0 over ℤ. | `d0`, `d1` | 1 | $0.04 |
| 9 | ✅ | `d1_comp_d0` | lemma | δ¹ ∘ δ⁰ = 0. | `d0lin`, `d1lin`, `d1d0_int` | 1 | $0.34 |
| 10 | ✅ | `H0` | def | H^0 = ker δ⁰. | `d0lin` |  |  |
| 11 | ✅ | `H1` | def | H^1 = ker δ¹ / im δ⁰. | `d1lin`, `d0lin` |  |  |
| 12 | ✅ | `H1inst` | def | AddCommGroup on H1. | `H1` |  |  |
| 13 | ✅ | `H2` | def | H^2 = C^2 / im δ¹. | `d1lin` |  |  |
| 14 | ✅ | `H2inst` | def | AddCommGroup on H2. | `H2` |  |  |
| 15 | ✅ | `H0_eq_constants` | lemma | ker δ⁰ = constants. | `H0`, `d0`, `d0lin` | 1 | $0.43 |
| 16 | ✅ | `H0_equiv_R` | lemma | H^0 ≅ R. | `H0`, `H0_eq_constants` | 1 | $0.09 |
| 17 | ✅ | `H0_int` | lemma | Over ℤ: H^0 ≅ ℤ. | `H0_equiv_R`, `H0` | 8 | $1.18 |
| 18 | ✅ | `H0_zmod2` | lemma | Over ZMod 2: H^0 ≅ ZMod 2. | `H0_equiv_R`, `H0` | 1 | $0.02 |
| 19 | ✅ | `ker_d1_int_desc` | lemma | Over ℤ, ker δ¹ = im δ⁰. | `d0lin`, `d1lin`, `d0`, `d1` | 1 | $0.44 |
| 20 | ✅ | `H1_int_subsingleton` | lemma | Over ℤ, H^1 = 0. | `H1`, `H1inst`, `d1_comp_d0` | 2 | $0.25 |
| 21 | ✅ | `ker_d1_zmod2_desc` | lemma | Over ZMod 2, ker δ¹ / im δ⁰ is 1-dimensional with witness w. | `d0lin`, `d1lin`, `d0`, `d1` | 3 | $5.75 |
| 22 | ✅ | `H1_equiv_of_witness` | lemma | Generic: given a cocycle witness w spanning H^1 with no relations, H^1 R ≅ R. | `H1`, `H1inst`, `d0lin`, `d1lin`, `d1_comp_d0` | 2 | $0.80 |
| 23 | ✅ | `H1_zmod2` | lemma | Over ZMod 2, H^1 ≅ ZMod 2. | `H1`, `H1inst`, `H1_equiv_of_witness` | 1 | $18.29 |
| 24 | ✅ | `H2_int_witness` | lemma | Over ℤ, range δ¹ description with Z/2 torsion witness u. | `d1lin`, `d1` | 3 | $8.77 |
| 25 | ✅ | `phi2` | def | A linear functional φ : (Fin 10 → ZMod 2) → ZMod 2 given by the sum of all 10 coordinates (the total-degree / orientation functional), which vanishes exactly on the range of δ¹ over ZMod 2. This is the detector for H^2 over ZMod 2. | `opens` |  |  |
| 26 | ✅ | `phi2_apply` | lemma | φ2 evaluated on v equals the sum of all coordinates. | `phi2` | 1 | $0.23 |
| 27 | ✅ | `phi2_range_zero` | lemma | φ2 vanishes on the range of δ¹ over ZMod 2 (each triangle-boundary has an even number of edge contributions, but here φ2 counts triangles; the key is φ2 ∘ d1lin = 0). Proved by computing φ2 (d1lin _ x) = 0 for all x, i.e. showing the columns of d1mat each sum to an even number mod 2. | `phi2`, `phi2_apply`, `d1lin`, `d1` | 1 | $0.46 |
| 28 | ✅ | `phi2_mem_range` | lemma | Conversely, over ZMod 2 any v with φ2 v = 0 lies in the range of δ¹. Proven by exhibiting an explicit preimage: since range has codimension 1 detected by φ2, and rank of d1mat over ZMod 2 is 9. State as: φ2 v = 0 → v ∈ range. | `phi2`, `phi2_apply`, `d1lin`, `d1` | 1 | $1.07 |
| 29 | ✅ | `H2_zmod2_witness` | lemma | Over ZMod 2, range δ¹ description with witness u = e0 (first standard basis vector), using φ2 as the detector: u∉range since φ2 u = 1 ≠ 0; every v is in range or v-u in range since φ2 v ∈ {0,1}. | `d1lin`, `d1`, `phi2`, `phi2_apply`, `phi2_range_zero`, `phi2_mem_range` | 2 | $7.18 |
| 30 | ✅ | `two_elt_addequiv_zmod2` | lemma | Generic helper: an additive group A with a nonzero element g such that every element is 0 or g and 2•g = 0 is ≃+ ZMod 2. |  | 3 | $2.40 |
| 31 | ✅ | `H2_classes_of_witness` | lemma | Generic: from a witness u obtain a generator g = ⟦u⟧ of H2 R with g ≠ 0, 2•g = 0, and every element 0 or g. | `H2`, `H2inst`, `d1lin` | 1 | $0.53 |
| 32 | ✅ | `H2_equiv_of_witness` | lemma | Generic: from the witness u for H2 R, get H2 R ≃+ ZMod 2. | `H2`, `H2inst`, `H2_classes_of_witness`, `two_elt_addequiv_zmod2` | 1 | $0.24 |
| 33 | ✅ | `H2_int` | lemma | Over ℤ, H^2 ≅ ZMod 2. | `H2`, `H2inst`, `H2_int_witness`, `H2_equiv_of_witness` | 1 | $0.23 |
| 34 | ✅ | `H2_zmod2` | lemma | Over ZMod 2, H^2 ≅ ZMod 2. Specialization of H2_equiv_of_witness; the 2•u ∈ range hypothesis is trivial since (2:ZMod 2)•u = 0. | `H2`, `H2inst`, `H2_zmod2_witness`, `H2_equiv_of_witness` | 1 | $0.23 |

## Statements

### `opens` (def, proved)

Open namespaces for matrices and big operators.

```lean
open Matrix BigOperators
```

### `d0` (def, proved)

Coboundary matrix δ⁰.

```lean
def edgePair : Fin 15 → Fin 6 × Fin 6 := ![(0,1),(0,2),(0,3),(0,4),(0,5),(1,2),(1,3),(1,4),(1,5),(2,3),(2,4),(2,5),(3,4),(3,5),(4,5)]

def d0mat : Matrix (Fin 15) (Fin 6) ℤ := fun i j =>
  (if (edgePair i).2 = j then 1 else 0) - (if (edgePair i).1 = j then 1 else 0)
```

### `triList` (def, proved)

The 10 triangles.

```lean
def triList : Fin 10 → Fin 6 × Fin 6 × Fin 6 := ![(0,1,2),(0,1,3),(0,2,4),(0,3,5),(0,4,5),(1,2,5),(1,3,4),(1,4,5),(2,3,4),(2,3,5)]
```

### `edgeIdx` (def, proved)

Edge index of a pair.

```lean
def edgeIdx (a b : Fin 6) : Fin 15 :=
  ![![0,0,1,2,3,4],![0,0,5,6,7,8],![1,5,0,9,10,11],![2,6,9,0,12,13],![3,7,10,12,0,14],![4,8,11,13,14,0]] a b
```

### `d1` (def, proved)

Coboundary matrix δ¹.

```lean
def d1mat : Matrix (Fin 10) (Fin 15) ℤ := fun t e =>
  let v := triList t
  let i := v.1; let j := v.2.1; let k := v.2.2
  (if edgeIdx j k = e then 1 else 0) - (if edgeIdx i k = e then 1 else 0) + (if edgeIdx i j = e then 1 else 0)
```

### `d0lin` (def, proved)

δ⁰ as a linear map.

```lean
def d0lin (R : Type) [CommRing R] : (Fin 6 → R) →ₗ[R] (Fin 15 → R) :=
  Matrix.mulVecLin (d0mat.map (Int.cast : ℤ → R))
```

### `d1lin` (def, proved)

δ¹ as a linear map.

```lean
def d1lin (R : Type) [CommRing R] : (Fin 15 → R) →ₗ[R] (Fin 10 → R) :=
  Matrix.mulVecLin (d1mat.map (Int.cast : ℤ → R))
```

### `d1d0_int` (lemma, proved)

d1mat * d0mat = 0 over ℤ.

```lean
theorem d1d0_int : d1mat * d0mat = 0
```

### `d1_comp_d0` (lemma, proved)

δ¹ ∘ δ⁰ = 0.

```lean
theorem d1_comp_d0 (R : Type) [CommRing R] : (d1lin R).comp (d0lin R) = 0
```

### `H0` (def, proved)

H^0 = ker δ⁰.

```lean
def H0 (R : Type) [CommRing R] : Submodule R (Fin 6 → R) := LinearMap.ker (d0lin R)
```

### `H1` (def, proved)

H^1 = ker δ¹ / im δ⁰.

```lean
abbrev H1 (R : Type) [CommRing R] : Type :=
  (LinearMap.ker (d1lin R)) ⧸ (LinearMap.range (d0lin R)).comap (LinearMap.ker (d1lin R)).subtype
```

### `H1inst` (def, proved)

AddCommGroup on H1.

```lean
noncomputable instance H1inst (R : Type) [CommRing R] : AddCommGroup (H1 R) := inferInstance
```

### `H2` (def, proved)

H^2 = C^2 / im δ¹.

```lean
abbrev H2 (R : Type) [CommRing R] : Type :=
  (Fin 10 → R) ⧸ (LinearMap.range (d1lin R))
```

### `H2inst` (def, proved)

AddCommGroup on H2.

```lean
noncomputable instance H2inst (R : Type) [CommRing R] : AddCommGroup (H2 R) := inferInstance
```

### `H0_eq_constants` (lemma, proved)

ker δ⁰ = constants.

```lean
theorem H0_mem_iff (R : Type) [CommRing R] (f : Fin 6 → R) :
    f ∈ H0 R ↔ ∀ i, f i = f 0
```

### `H0_equiv_R` (lemma, proved)

H^0 ≅ R.

```lean
theorem H0_equiv_R (R : Type) [CommRing R] : Nonempty (H0 R ≃+ R)
```

### `H0_int` (lemma, proved)

Over ℤ: H^0 ≅ ℤ.

```lean
theorem H0_int : Nonempty (H0 ℤ ≃+ ℤ)
```

### `H0_zmod2` (lemma, proved)

Over ZMod 2: H^0 ≅ ZMod 2.

```lean
theorem H0_zmod2 : Nonempty (H0 (ZMod 2) ≃+ ZMod 2)
```

### `ker_d1_int_desc` (lemma, proved)

Over ℤ, ker δ¹ = im δ⁰.

```lean
theorem ker_d1_eq_range_d0_int (z : Fin 15 → ℤ) :
    z ∈ LinearMap.ker (d1lin ℤ) ↔ z ∈ LinearMap.range (d0lin ℤ)
```

### `H1_int_subsingleton` (lemma, proved)

Over ℤ, H^1 = 0.

```lean
theorem H1_int : Subsingleton (H1 ℤ)
```

### `ker_d1_zmod2_desc` (lemma, proved)

Over ZMod 2, ker δ¹ / im δ⁰ is 1-dimensional with witness w.

```lean
theorem H1_zmod2_witness : ∃ w : Fin 15 → ZMod 2,
    w ∈ LinearMap.ker (d1lin (ZMod 2)) ∧
    (∀ z ∈ LinearMap.ker (d1lin (ZMod 2)), ∃ c : ZMod 2,
      z - c • w ∈ LinearMap.range (d0lin (ZMod 2))) ∧
    (∀ c : ZMod 2, c • w ∈ LinearMap.range (d0lin (ZMod 2)) → c = 0)
```

### `H1_equiv_of_witness` (lemma, proved)

Generic: given a cocycle witness w spanning H^1 with no relations, H^1 R ≅ R.

```lean
theorem H1_equiv_of_witness (R : Type) [CommRing R] (w : Fin 15 → R)
    (hw : w ∈ LinearMap.ker (d1lin R))
    (hsurj : ∀ z ∈ LinearMap.ker (d1lin R), ∃ c : R, z - c • w ∈ LinearMap.range (d0lin R))
    (hinj : ∀ c : R, c • w ∈ LinearMap.range (d0lin R) → c = 0) :
    Nonempty (H1 R ≃+ R)
```

### `H1_zmod2` (lemma, proved)

Over ZMod 2, H^1 ≅ ZMod 2.

```lean
theorem H1_zmod2 : Nonempty (H1 (ZMod 2) ≃+ ZMod 2)
```

### `H2_int_witness` (lemma, proved)

Over ℤ, range δ¹ description with Z/2 torsion witness u.

```lean
theorem H2_int_witness : ∃ u : Fin 10 → ℤ,
    (2 : ℤ) • u ∈ LinearMap.range (d1lin ℤ) ∧
    u ∉ LinearMap.range (d1lin ℤ) ∧
    (∀ v : Fin 10 → ℤ, v ∈ LinearMap.range (d1lin ℤ) ∨
      v - u ∈ LinearMap.range (d1lin ℤ))
```

### `phi2` (def, proved)

A linear functional φ : (Fin 10 → ZMod 2) → ZMod 2 given by the sum of all 10 coordinates (the total-degree / orientation functional), which vanishes exactly on the range of δ¹ over ZMod 2. This is the detector for H^2 over ZMod 2.

```lean
def phi2 : (Fin 10 → ZMod 2) →ₗ[ZMod 2] ZMod 2 := ∑ i : Fin 10, LinearMap.proj i
```

### `phi2_apply` (lemma, proved)

φ2 evaluated on v equals the sum of all coordinates.

```lean
theorem phi2_apply (v : Fin 10 → ZMod 2) : phi2 v = ∑ i : Fin 10, v i
```

### `phi2_range_zero` (lemma, proved)

φ2 vanishes on the range of δ¹ over ZMod 2 (each triangle-boundary has an even number of edge contributions, but here φ2 counts triangles; the key is φ2 ∘ d1lin = 0). Proved by computing φ2 (d1lin _ x) = 0 for all x, i.e. showing the columns of d1mat each sum to an even number mod 2.

```lean
theorem phi2_range_zero (v : Fin 10 → ZMod 2) (hv : v ∈ LinearMap.range (d1lin (ZMod 2))) : phi2 v = 0
```

### `phi2_mem_range` (lemma, proved)

Conversely, over ZMod 2 any v with φ2 v = 0 lies in the range of δ¹. Proven by exhibiting an explicit preimage: since range has codimension 1 detected by φ2, and rank of d1mat over ZMod 2 is 9. State as: φ2 v = 0 → v ∈ range.

```lean
theorem phi2_mem_range (v : Fin 10 → ZMod 2) (hv : phi2 v = 0) : v ∈ LinearMap.range (d1lin (ZMod 2))
```

### `H2_zmod2_witness` (lemma, proved)

Over ZMod 2, range δ¹ description with witness u = e0 (first standard basis vector), using φ2 as the detector: u∉range since φ2 u = 1 ≠ 0; every v is in range or v-u in range since φ2 v ∈ {0,1}.

```lean
theorem H2_zmod2_witness : ∃ u : Fin 10 → ZMod 2,
    u ∉ LinearMap.range (d1lin (ZMod 2)) ∧
    (∀ v : Fin 10 → ZMod 2, v ∈ LinearMap.range (d1lin (ZMod 2)) ∨
      v - u ∈ LinearMap.range (d1lin (ZMod 2)))
```

### `two_elt_addequiv_zmod2` (lemma, proved)

Generic helper: an additive group A with a nonzero element g such that every element is 0 or g and 2•g = 0 is ≃+ ZMod 2.

```lean
theorem two_elt_addequiv_zmod2 (A : Type) [AddCommGroup A] (g : A)
    (hg : g ≠ 0) (h2 : (2 : ℤ) • g = 0) (hcov : ∀ x : A, x = 0 ∨ x = g) :
    Nonempty (A ≃+ ZMod 2)
```

### `H2_classes_of_witness` (lemma, proved)

Generic: from a witness u obtain a generator g = ⟦u⟧ of H2 R with g ≠ 0, 2•g = 0, and every element 0 or g.

```lean
theorem H2_classes_of_witness (R : Type) [CommRing R] (u : Fin 10 → R)
    (h2 : (2 : R) • u ∈ LinearMap.range (d1lin R))
    (hu : u ∉ LinearMap.range (d1lin R))
    (hcov : ∀ v : Fin 10 → R, v ∈ LinearMap.range (d1lin R) ∨ v - u ∈ LinearMap.range (d1lin R)) :
    ∃ g : H2 R, g ≠ 0 ∧ (2 : ℤ) • g = 0 ∧ (∀ x : H2 R, x = 0 ∨ x = g)
```

### `H2_equiv_of_witness` (lemma, proved)

Generic: from the witness u for H2 R, get H2 R ≃+ ZMod 2.

```lean
theorem H2_equiv_of_witness (R : Type) [CommRing R] (u : Fin 10 → R)
    (h2 : (2 : R) • u ∈ LinearMap.range (d1lin R))
    (hu : u ∉ LinearMap.range (d1lin R))
    (hcov : ∀ v : Fin 10 → R, v ∈ LinearMap.range (d1lin R) ∨ v - u ∈ LinearMap.range (d1lin R)) :
    Nonempty (H2 R ≃+ ZMod 2)
```

### `H2_int` (lemma, proved)

Over ℤ, H^2 ≅ ZMod 2.

```lean
theorem H2_int : Nonempty (H2 ℤ ≃+ ZMod 2)
```

### `H2_zmod2` (lemma, proved)

Over ZMod 2, H^2 ≅ ZMod 2. Specialization of H2_equiv_of_witness; the 2•u ∈ range hypothesis is trivial since (2:ZMod 2)•u = 0.

```lean
theorem H2_zmod2 : Nonempty (H2 (ZMod 2) ≃+ ZMod 2)
```

## Most expensive lemmas

| lemma | cost |
|---|---:|
| `H1_zmod2` | $18.29 |
| `H2_int_witness` | $8.77 |
| `H2_zmod2_witness` | $7.18 |
| `ker_d1_zmod2_desc` | $5.75 |
| `two_elt_addequiv_zmod2` | $2.40 |
