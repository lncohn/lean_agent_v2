# Project: rp2_cohomology

**Status:** COMPLETE and verified  ·  lemmas proved 21/21  ·  spent $50.25 of $200.00  ·  replans 2  ·  0.0 min this session

## Goal

Compute the simplicial cohomology of the real projective plane RP^2 from an explicit finite triangulation, fully formally in Lean 4 + Mathlib.

Required final theorems (the last nodes of the plan), for the cochain complex C^0 -> C^1 -> C^2 of the triangulation:
  1. Over ℤ:  H^0 ≅ ℤ,  H^1 = 0,  H^2 ≅ ZMod 2.
  2. Over ZMod 2:  H^0 ≅ ZMod 2,  H^1 ≅ ZMod 2,  H^2 ≅ ZMod 2.
Each H^k must be defined as an honest quotient (kernel of the coboundary modulo the image of the previous coboundary) or an equivalent concrete description proven equal to it, and the isomorphisms must be stated as `Nonempty (H^k ≃+ ℤ)`, `Nonempty (H^k ≃+ ZMod 2)`, or `Subsingleton H^k` (for the zero group), as additive group isomorphisms.

## Plan and outcome

| node | kind | status | attempts | run |
|---|---|---|---:|---|
| `opens` | def | proved | 0 |  |
| `d0` | def | proved | 0 |  |
| `triList` | def | proved | 0 |  |
| `edgeIdx` | def | proved | 0 |  |
| `d1` | def | proved | 0 |  |
| `d0lin` | def | proved | 0 |  |
| `d1lin` | def | proved | 0 |  |
| `d1d0_int` | lemma | proved | 1 | [d1d0_int_2026-09-19_12-47-23](d1d0_int_2026-09-19_12-47-23/trace.md) |
| `d1_comp_d0` | lemma | proved | 1 | [d1_comp_d0_2026-09-19_12-48-11](d1_comp_d0_2026-09-19_12-48-11/trace.md) |
| `H0` | def | proved | 0 |  |
| `H1` | def | proved | 0 |  |
| `H1inst` | def | proved | 0 |  |
| `H2` | def | proved | 0 |  |
| `H2inst` | def | proved | 0 |  |
| `H0_eq_constants` | lemma | proved | 1 | [H0_eq_constants_2026-09-19_12-50-35](H0_eq_constants_2026-09-19_12-50-35/trace.md) |
| `H0_equiv_R` | lemma | proved | 1 | [H0_equiv_R_2026-09-19_12-53-15](H0_equiv_R_2026-09-19_12-53-15/trace.md) |
| `H0_int` | lemma | proved | 8 | [H0_int_2026-09-19_12-59-48](H0_int_2026-09-19_12-59-48/trace.md) |
| `H0_zmod2` | lemma | proved | 1 | [H0_zmod2_2026-09-19_13-00-51](H0_zmod2_2026-09-19_13-00-51/trace.md) |
| `ker_d1_int_desc` | lemma | proved | 1 | [ker_d1_int_desc_2026-09-19_13-01-14](ker_d1_int_desc_2026-09-19_13-01-14/trace.md) |
| `H1_int_subsingleton` | lemma | proved | 2 | [H1_int_subsingleton_2026-09-19_13-31-18](H1_int_subsingleton_2026-09-19_13-31-18/trace.md) |
| `ker_d1_zmod2_desc` | lemma | proved | 3 | [ker_d1_zmod2_desc_2026-09-19_13-17-23](ker_d1_zmod2_desc_2026-09-19_13-17-23/trace.md) |
| `H1_equiv_of_witness` | lemma | proved | 2 | [H1_equiv_of_witness_2026-09-19_14-39-20](H1_equiv_of_witness_2026-09-19_14-39-20/trace.md) |
| `H1_zmod2` | lemma | proved | 1 | [H1_zmod2_2026-09-19_14-43-33](H1_zmod2_2026-09-19_14-43-33/trace.md) |
| `H2_int_witness` | lemma | proved | 3 | [H2_int_witness_2026-09-19_15-01-02](H2_int_witness_2026-09-19_15-01-02/trace.md) |
| `phi2` | def | proved | 0 |  |
| `phi2_apply` | lemma | proved | 1 | [phi2_apply_2026-09-19_15-32-51](phi2_apply_2026-09-19_15-32-51/trace.md) |
| `phi2_range_zero` | lemma | proved | 1 | [phi2_range_zero_2026-09-19_15-33-51](phi2_range_zero_2026-09-19_15-33-51/trace.md) |
| `phi2_mem_range` | lemma | proved | 1 | [phi2_mem_range_2026-09-19_15-35-33](phi2_mem_range_2026-09-19_15-35-33/trace.md) |
| `H2_zmod2_witness` | lemma | proved | 2 | [H2_zmod2_witness_2026-09-19_15-39-55](H2_zmod2_witness_2026-09-19_15-39-55/trace.md) |
| `two_elt_addequiv_zmod2` | lemma | proved | 3 | [two_elt_addequiv_zmod2_2026-09-19_15-41-44](two_elt_addequiv_zmod2_2026-09-19_15-41-44/trace.md) |
| `H2_classes_of_witness` | lemma | proved | 1 | [H2_classes_of_witness_2026-09-19_15-47-42](H2_classes_of_witness_2026-09-19_15-47-42/trace.md) |
| `H2_equiv_of_witness` | lemma | proved | 1 | [H2_equiv_of_witness_2026-09-19_15-49-17](H2_equiv_of_witness_2026-09-19_15-49-17/trace.md) |
| `H2_int` | lemma | proved | 1 | [H2_int_2026-09-19_15-50-09](H2_int_2026-09-19_15-50-09/trace.md) |
| `H2_zmod2` | lemma | proved | 1 | [H2_zmod2_2026-09-19_15-51-00](H2_zmod2_2026-09-19_15-51-00/trace.md) |

## Final verification (`#print axioms` on every lemma)

```text
nt/lean_env/LeanEnv/Project_final.lean:508:8: warning: This simp argument is unused:
  Matrix.head_cons

Hint: Omit it from the simp argument list.
  [apply] simp only [Matrix.mulVec, dotProduct, d1mat, triList, edgeIdx, Matrix.map_apply, Fin.sum_univ_succ,
    Fin.sum_univ_zero, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.cons_val, Fin.isValue, Pi.sub_apply]

Note: This linter can be disabled with `set_option linter.unusedSimpArgs false`
/Users/lee_cohn/Desktop/lean_agent/lean_env/LeanEnv/Project_final.lean:508:26: warning: This simp argument is unused:
  Matrix.cons_val

Hint: Omit it from the simp argument list.
  [apply] simp only [Matrix.mulVec, dotProduct, d1mat, triList, edgeIdx, Matrix.map_apply, Fin.sum_univ_succ,
    Fin.sum_univ_zero, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons, Fin.isValue, Pi.sub_apply]

Note: This linter can be disabled with `set_option linter.unusedSimpArgs false`
/Users/lee_cohn/Desktop/lean_agent/lean_env/LeanEnv/Project_final.lean:554:52: warning: Used `tac1 <;> tac2` where `(tac1; tac2)` would suffice

Note: This linter can be disabled with `set_option linter.unnecessarySeqFocus false`
/Users/lee_cohn/Desktop/lean_agent/lean_env/LeanEnv/Project_final.lean:601:16: warning: This simp argument is unused:
  h110

Hint: Omit it from the simp argument list.
  [apply] simp_all

Note: This linter can be disabled with `set_option linter.unusedSimpArgs false`
'd1d0_int' depends on axioms: [propext, Classical.choice, Quot.sound]
'd1_comp_d0' depends on axioms: [propext, Classical.choice, Quot.sound]
'H0_mem_iff' depends on axioms: [propext, Classical.choice, Quot.sound]
'H0_equiv_R' depends on axioms: [propext, Classical.choice, Quot.sound]
'H0_int' depends on axioms: [propext, Classical.choice, Quot.sound]
'H0_zmod2' depends on axioms: [propext, Classical.choice, Quot.sound]
'ker_d1_eq_range_d0_int' depends on axioms: [propext, Classical.choice, Quot.sound]
'H1_int' depends on axioms: [propext, Classical.choice, Quot.sound]
'H1_zmod2_witness' depends on axioms: [propext, Classical.choice, Quot.sound]
'H1_equiv_of_witness' depends on axioms: [propext, Classical.choice, Quot.sound]
'H1_zmod2' depends on axioms: [propext, Classical.choice, Quot.sound]
'H2_int_witness' depends on axioms: [propext, Classical.choice, Quot.sound]
'phi2_apply' depends on axioms: [propext, Classical.choice, Quot.sound]
'phi2_range_zero' depends on axioms: [propext, Classical.choice, Quot.sound]
'phi2_mem_range' depends on axioms: [propext, Classical.choice, Quot.sound]
'H2_zmod2_witness' depends on axioms: [propext, Classical.choice, Quot.sound]
'two_elt_addequiv_zmod2' depends on axioms: [propext, Classical.choice, Quot.sound]
'H2_classes_of_witness' depends on axioms: [propext, Classical.choice, Quot.sound]
'H2_equiv_of_witness' depends on axioms: [propext, Classical.choice, Quot.sound]
'H2_int' depends on axioms: [propext, Classical.choice, Quot.sound]
'H2_zmod2' depends on axioms: [propext, Classical.choice, Quot.sound]
```

## Library (`library.lean`)

```lean
import Mathlib

open Matrix BigOperators

def edgePair : Fin 15 → Fin 6 × Fin 6 := ![(0,1),(0,2),(0,3),(0,4),(0,5),(1,2),(1,3),(1,4),(1,5),(2,3),(2,4),(2,5),(3,4),(3,5),(4,5)]

def d0mat : Matrix (Fin 15) (Fin 6) ℤ := fun i j =>
  (if (edgePair i).2 = j then 1 else 0) - (if (edgePair i).1 = j then 1 else 0)

def triList : Fin 10 → Fin 6 × Fin 6 × Fin 6 := ![(0,1,2),(0,1,3),(0,2,4),(0,3,5),(0,4,5),(1,2,5),(1,3,4),(1,4,5),(2,3,4),(2,3,5)]

def edgeIdx (a b : Fin 6) : Fin 15 :=
  ![![0,0,1,2,3,4],![0,0,5,6,7,8],![1,5,0,9,10,11],![2,6,9,0,12,13],![3,7,10,12,0,14],![4,8,11,13,14,0]] a b

def d1mat : Matrix (Fin 10) (Fin 15) ℤ := fun t e =>
  let v := triList t
  let i := v.1; let j := v.2.1; let k := v.2.2
  (if edgeIdx j k = e then 1 else 0) - (if edgeIdx i k = e then 1 else 0) + (if edgeIdx i j = e then 1 else 0)

def d0lin (R : Type) [CommRing R] : (Fin 6 → R) →ₗ[R] (Fin 15 → R) :=
  Matrix.mulVecLin (d0mat.map (Int.cast : ℤ → R))

def d1lin (R : Type) [CommRing R] : (Fin 15 → R) →ₗ[R] (Fin 10 → R) :=
  Matrix.mulVecLin (d1mat.map (Int.cast : ℤ → R))

theorem d1d0_int : d1mat * d0mat = 0 := by
  ext i j
  simp only [Matrix.mul_apply, Matrix.zero_apply]
  fin_cases i <;> fin_cases j <;> decide

theorem d1_comp_d0 (R : Type) [CommRing R] : (d1lin R).comp (d0lin R) = 0 := by
  unfold d1lin d0lin
  rw [← Matrix.mulVecLin_mul]
  have : d1mat.map (Int.cast : ℤ → R) * d0mat.map (Int.cast : ℤ → R) = 0 := by
    have e : (Int.cast : ℤ → R) = ⇑(Int.castRingHom R) := rfl
    rw [e, ← Matrix.map_mul, d1d0_int]
    ext i j
    simp
  rw [this]
  simp

def H0 (R : Type) [CommRing R] : Submodule R (Fin 6 → R) := LinearMap.ker (d0lin R)

abbrev H1 (R : Type) [CommRing R] : Type :=
  (LinearMap.ker (d1lin R)) ⧸ (LinearMap.range (d0lin R)).comap (LinearMap.ker (d1lin R)).subtype

noncomputable instance H1inst (R : Type) [CommRing R] : AddCommGroup (H1 R) := inferInstance

abbrev H2 (R : Type) [CommRing R] : Type :=
  (Fin 10 → R) ⧸ (LinearMap.range (d1lin R))

noncomputable instance H2inst (R : Type) [CommRing R] : AddCommGroup (H2 R) := inferInstance

theorem H0_mem_iff (R : Type) [CommRing R] (f : Fin 6 → R) :
    f ∈ H0 R ↔ ∀ i, f i = f 0 := by
  unfold H0 d0lin
  rw [LinearMap.mem_ker, Matrix.mulVecLin_apply, funext_iff]
  constructor
  · intro h i
    fin_cases i
    · rfl
    · show f 1 = f 0
      have := h 0; simp only [Matrix.mulVec, dotProduct, d0mat, edgePair, Matrix.map_apply, Fin.sum_univ_succ, Fin.sum_univ_zero, Pi.zero_apply] at this; push_cast at this; linear_combination this
    · show f 2 = f 0
      have := h 1; simp only [Matrix.mulVec, dotProduct, d0mat, edgePair, Matrix.map_apply, Fin.sum_univ_succ, Fin.sum_univ_zero, Pi.zero_apply] at this; push_cast at this; linear_combination this
    · show f 3 = f 0
      have := h 2; simp only [Matrix.mulVec, dotProduct, d0mat, edgePair, Matrix.map_apply, Fin.sum_univ_succ, Fin.sum_univ_zero, Pi.zero_apply] at this; push_cast at this; linear_combination this
    · show f 4 = f 0
      have := h 3; simp only [Matrix.mulVec, dotProduct, d0mat, edgePair, Matrix.map_apply, Fin.sum_univ_succ, Fin.sum_univ_zero, Pi.zero_apply] at this; push_cast at this; linear_combination this
    · show f 5 = f 0
      have := h 4; simp only [Matrix.mulVec, dotProduct, d0mat, edgePair, Matrix.map_apply, Fin.sum_univ_succ, Fin.sum_univ_zero, Pi.zero_apply] at this; push_cast at this; linear_combination this
  · intro h x
    fin_cases x <;>
    · simp only [Matrix.mulVec, dotProduct, d0mat, edgePair, Matrix.map_apply]
      simp [Fin.sum_univ_succ, h]

theorem H0_equiv_R (R : Type) [CommRing R] : Nonempty (H0 R ≃+ R) := by
  refine ⟨{
    toFun := fun f => f.1 0
    invFun := fun r => ⟨fun _ => r, by rw [H0_mem_iff]; intro i; rfl⟩
    left_inv := ?_
    right_inv := ?_
    map_add' := ?_
  }⟩
  · intro f
    ext i
    show (f.1 0 : R) = f.1 i
    rw [(H0_mem_iff R f.1).mp f.2 i]
  · intro r; rfl
  · intro f g; rfl

theorem H0_int : Nonempty (H0 ℤ ≃+ ℤ) := by
  exact H0_equiv_R ℤ

theorem H0_zmod2 : Nonempty (H0 (ZMod 2) ≃+ ZMod 2) := by
  exact H0_equiv_R (ZMod 2)

theorem ker_d1_eq_range_d0_int (z : Fin 15 → ℤ) :
    z ∈ LinearMap.ker (d1lin ℤ) ↔ z ∈ LinearMap.range (d0lin ℤ) := by
  constructor
  · intro hz
    rw [LinearMap.mem_ker] at hz
    unfold d1lin at hz
    rw [Matrix.mulVecLin_apply, funext_iff] at hz
    have simp_eq : ∀ t : Fin 10, (d1mat.map (Int.cast : ℤ → ℤ)).mulVec z t = 0 := hz
    have e0 := simp_eq 0
    have e1 := simp_eq 1
    have e2 := simp_eq 2
    have e3 := simp_eq 3
    have e4 := simp_eq 4
    have e5 := simp_eq 5
    have e6 := simp_eq 6
    have e7 := simp_eq 7
    have e8 := simp_eq 8
    have e9 := simp_eq 9
    simp only [Matrix.mulVec, dotProduct, d1mat, triList, edgeIdx, Matrix.map_apply, Fin.sum_univ_succ, Fin.sum_univ_zero, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons, Matrix.cons_val, Fin.isValue] at e0 e1 e2 e3 e4 e5 e6 e7 e8 e9
    norm_num at e0 e1 e2 e3 e4 e5 e6 e7 e8 e9
    refine ⟨![0, z 0, z 1, z 2, z 3, z 4], ?_⟩
    unfold d0lin
    rw [Matrix.mulVecLin_apply]
    funext ed
    simp only [Matrix.mulVec, dotProduct, d0mat, edgePair, Matrix.map_apply, Fin.sum_univ_succ, Fin.sum_univ_zero]
    fin_cases ed <;>
      simp only [Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons, Matrix.cons_val_fin_one, Fin.isValue, Matrix.cons_val, Pi.zero_apply] <;>
      norm_num <;>
      linarith
  · rintro ⟨f, rfl⟩
    rw [LinearMap.mem_ker]
    have h2 : (d1lin ℤ) ((d0lin ℤ) f) = ((d1lin ℤ).comp (d0lin ℤ)) f := rfl
    rw [h2, d1_comp_d0 ℤ]
    rfl

theorem H1_int : Subsingleton (H1 ℤ) := by
  unfold H1
  rw [Submodule.Quotient.subsingleton_iff]
  rw [Submodule.eq_top_iff']
  rintro ⟨z, hz⟩
  rw [Submodule.mem_comap]
  exact (ker_d1_eq_range_d0_int z).mp hz

theorem H1_zmod2_witness : ∃ w : Fin 15 → ZMod 2,
    w ∈ LinearMap.ker (d1lin (ZMod 2)) ∧
    (∀ z ∈ LinearMap.ker (d1lin (ZMod 2)), ∃ c : ZMod 2,
      z - c • w ∈ LinearMap.range (d0lin (ZMod 2))) ∧
    (∀ c : ZMod 2, c • w ∈ LinearMap.range (d0lin (ZMod 2)) → c = 0) := by
  refine ⟨![0,0,0,0,0,0,0,1,1,1,0,1,1,0,0], ?_, ?_, ?_⟩
  · rw [LinearMap.mem_ker]
    unfold d1lin
    rw [Matrix.mulVecLin_apply]
    funext t
    fin_cases t <;>
      simp only [Matrix.mulVec, dotProduct, d1mat, triList, edgeIdx, Matrix.map_apply,
        Fin.sum_univ_succ, Fin.sum_univ_zero, Matrix.cons_val_zero, Matrix.head_cons,
        Matrix.cons_val, Fin.isValue] <;>
      decide
  · intro z hz
    rw [LinearMap.mem_ker] at hz
    unfold d1lin at hz
    rw [Matrix.mulVecLin_apply, funext_iff] at hz
    have E : ∀ t, (d1mat.map (Int.cast : ℤ → ZMod 2)).mulVec z t = 0 := hz
    have e0 := E 0; have e1 := E 1; have e2 := E 2; have e3 := E 3; have e4 := E 4
    have e5 := E 5; have e6 := E 6; have e7 := E 7; have e8 := E 8; have e9 := E 9
    simp only [Matrix.mulVec, dotProduct, d1mat, triList, edgeIdx, Matrix.map_apply,
      Fin.sum_univ_succ, Fin.sum_univ_zero, Matrix.cons_val_zero, Matrix.cons_val_one,
      Matrix.head_cons, Matrix.cons_val, Fin.isValue] at e0 e1 e2 e3 e4 e5 e6 e7 e8 e9
    norm_num at e0 e1 e2 e3 e4 e5 e6 e7 e8 e9
    refine ⟨z 7 + z 0 + z 3, ?_⟩
    rw [LinearMap.mem_range]
    refine ⟨![0, z 0, z 1, z 2, z 3, z 4], ?_⟩
    unfold d0lin
    rw [Matrix.mulVecLin_apply]
    funext ed
    simp only [Matrix.mulVec, dotProduct, d0mat, edgePair, Matrix.map_apply, Fin.sum_univ_succ,
      Fin.sum_univ_zero, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons,
      Matrix.cons_val, Fin.isValue, Pi.sub_apply, Pi.smul_apply, smul_eq_mul]
    fin_cases ed <;> push_cast
    · linear_combination (norm := (ring_nf; try simp [CharTwo.two_eq_zero]; try ring_nf)) (0 : ZMod 2)
    · linear_combination (norm := (ring_nf; try simp [CharTwo.two_eq_zero]; try ring_nf)) (0 : ZMod 2)
    · linear_combination (norm := (ring_nf; try simp [CharTwo.two_eq_zero]; try ring_nf)) (0 : ZMod 2)
    · linear_combination (norm := (ring_nf; try simp [CharTwo.two_eq_zero]; try ring_nf)) (0 : ZMod 2)
    · linear_combination (norm := (ring_nf; try simp [CharTwo.two_eq_zero]; try ring_nf)) (0 : ZMod 2)
    · linear_combination (norm := (ring_nf; try simp [CharTwo.two_eq_zero]; try ring_nf)) e0
    · linear_combination (norm := (ring_nf; try simp [CharTwo.two_eq_zero]; try ring_nf)) e1
    · linear_combination (norm := (ring_nf; try simp [CharTwo.two_eq_zero]; try ring_nf)) (0 : ZMod 2)
    · linear_combination (norm := (ring_nf; try simp [CharTwo.two_eq_zero]; try ring_nf)) e7 + e4
    · linear_combination (norm := (ring_nf; try simp [CharTwo.two_eq_zero]; try ring_nf)) e8 + e6 + e2 + e1
    · linear_combination (norm := (ring_nf; try simp [CharTwo.two_eq_zero]; try ring_nf)) e2
    · linear_combination (norm := (ring_nf; try simp [CharTwo.two_eq_zero]; try ring_nf)) e5 + e7 + e4 + e0
    · linear_combination (norm := (ring_nf; try simp [CharTwo.two_eq_zero]; try ring_nf)) e6 + e1
    · linear_combination (norm := (ring_nf; try simp [CharTwo.two_eq_zero]; try ring_nf)) e3
    · linear_combination (norm := (ring_nf; try simp [CharTwo.two_eq_zero]; try ring_nf)) e4
  · intro c hc
    rw [LinearMap.mem_range] at hc
    obtain ⟨g, hg⟩ := hc
    unfold d0lin at hg
    rw [Matrix.mulVecLin_apply, funext_iff] at hg
    have h0 := hg 0; have h3 := hg 3; have h7 := hg 7
    simp only [Matrix.mulVec, dotProduct, d0mat, edgePair, Matrix.map_apply, Fin.sum_univ_succ,
      Fin.sum_univ_zero, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons,
      Matrix.cons_val, Fin.isValue, Pi.smul_apply, smul_eq_mul] at h0 h3 h7
    norm_num at h0 h3 h7
    linear_combination (norm := (ring_nf; try simp [CharTwo.two_eq_zero]; try ring_nf)) h7 + h3 + h0

set_option maxHeartbeats 1000000 in

theorem H1_equiv_of_witness (R : Type) [CommRing R] (w : Fin 15 → R)
    (hw : w ∈ LinearMap.ker (d1lin R))
    (hsurj : ∀ z ∈ LinearMap.ker (d1lin R), ∃ c : R, z - c • w ∈ LinearMap.range (d0lin R))
    (hinj : ∀ c : R, c • w ∈ LinearMap.range (d0lin R) → c = 0) :
    Nonempty (H1 R ≃+ R) := by
  set K := LinearMap.ker (d1lin R) with hK
  set P := (LinearMap.range (d0lin R)).comap K.subtype with hP
  set x : K := ⟨w, hw⟩ with hx
  let g : R →ₗ[R] (H1 R) := (P.mkQ).comp (LinearMap.toSpanSingleton R K x)
  have hgc : ∀ c : R, g c = P.mkQ (c • x) := fun c => rfl
  have hsub : ∀ c : R, (K.subtype) (c • x) = c • w := by
    intro c
    rw [map_smul, Submodule.subtype_apply, hx]
  have hbij : Function.Bijective g := by
    constructor
    · rw [← LinearMap.ker_eq_bot, LinearMap.ker_eq_bot']
      intro c hc
      rw [hgc, Submodule.mkQ_apply, Submodule.Quotient.mk_eq_zero, hP,
        Submodule.mem_comap, hsub] at hc
      exact hinj c hc
    · intro y
      obtain ⟨z, rfl⟩ := Submodule.Quotient.mk_surjective P y
      obtain ⟨c, hc⟩ := hsurj z.1 z.2
      refine ⟨c, ?_⟩
      rw [hgc, Submodule.mkQ_apply, Submodule.Quotient.eq, hP,
        Submodule.mem_comap, map_sub, hsub, Submodule.subtype_apply]
      have := neg_mem hc
      simpa [neg_sub] using this
  exact ⟨(AddEquiv.ofBijective g hbij).symm⟩

theorem H1_zmod2 : Nonempty (H1 (ZMod 2) ≃+ ZMod 2) := by
  obtain ⟨w, hw, hsurj, hinj⟩ := H1_zmod2_witness
  exact H1_equiv_of_witness (ZMod 2) w hw hsurj hinj

set_option maxHeartbeats 1000000 in
set_option maxRecDepth 4000 in

theorem H2_int_witness : ∃ u : Fin 10 → ℤ,
    (2 : ℤ) • u ∈ LinearMap.range (d1lin ℤ) ∧
    u ∉ LinearMap.range (d1lin ℤ) ∧
    (∀ v : Fin 10 → ℤ, v ∈ LinearMap.range (d1lin ℤ) ∨
      v - u ∈ LinearMap.range (d1lin ℤ)) := by
  have preim : ∀ (z : Fin 15 → ℤ) (target : Fin 10 → ℤ),
      d1mat.mulVec z = target → target ∈ LinearMap.range (d1lin ℤ) := by
    intro z target hz
    refine ⟨z, ?_⟩
    unfold d1lin
    rw [Matrix.mulVecLin_apply]
    have e : (d1mat.map (Int.cast : ℤ → ℤ)) = d1mat := by ext i j; simp
    rw [e]; exact hz
  refine ⟨![1,0,0,0,0,0,0,0,0,0], ?_, ?_, ?_⟩
  · apply preim ![1,-1,0,0,0,0,-1,0,0,0,1,0,1,0,0]
    funext t
    fin_cases t <;>
      simp only [Matrix.mulVec, dotProduct, d1mat, triList, edgeIdx, Matrix.map_apply,
        Fin.sum_univ_succ, Fin.sum_univ_zero, Matrix.cons_val_zero, Matrix.cons_val_one,
        Matrix.head_cons, Matrix.cons_val, Fin.isValue, Pi.smul_apply, smul_eq_mul] <;>
      decide
  · intro hmem
    obtain ⟨z, hz⟩ := hmem
    unfold d1lin at hz
    rw [Matrix.mulVecLin_apply] at hz
    have e : (d1mat.map (Int.cast : ℤ → ℤ)) = d1mat := by ext i j; simp
    rw [e] at hz
    have hsum : (∑ t : Fin 10, (d1mat *ᵥ z) t) = 1 := by
      rw [hz]; decide
    have hlhs : (∑ t : Fin 10, (d1mat *ᵥ z) t)
        = ∑ e : Fin 15, (∑ t : Fin 10, d1mat t e) * z e := by
      simp only [Matrix.mulVec, dotProduct]
      rw [Finset.sum_comm]
      congr 1; ext e; rw [Finset.sum_mul]
    have hpar : ∀ e : Fin 15, Even (∑ t : Fin 10, d1mat t e) := by decide
    have hEven : Even (∑ e : Fin 15, (∑ t : Fin 10, d1mat t e) * z e) := by
      apply Finset.even_sum
      intro e _
      exact (hpar e).mul_right _
    rw [← hlhs, hsum] at hEven
    exact (Int.not_even_iff_odd.2 odd_one) hEven
  · intro v
    set u : Fin 10 → ℤ := ![1,0,0,0,0,0,0,0,0,0] with hu
    have h2u : (2 : ℤ) • u ∈ LinearMap.range (d1lin ℤ) := by
      rw [hu]
      apply preim ![1,-1,0,0,0,0,-1,0,0,0,1,0,1,0,0]
      funext t
      fin_cases t <;>
        simp only [Matrix.mulVec, dotProduct, d1mat, triList, edgeIdx, Matrix.map_apply,
          Fin.sum_univ_succ, Fin.sum_univ_zero, Matrix.cons_val_zero, Matrix.cons_val_one,
          Matrix.head_cons, Matrix.cons_val, Fin.isValue, Pi.smul_apply, smul_eq_mul] <;>
        decide
    have hd0 : ((![1,0,0,0,0,0,0,0,0,0] : Fin 10 → ℤ) - u) ∈ LinearMap.range (d1lin ℤ) := by
      rw [hu]
      apply preim ![0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
      funext j; fin_cases j <;>
      simp only [Matrix.mulVec, dotProduct, d1mat, triList, edgeIdx, Matrix.map_apply,
        Fin.sum_univ_succ, Fin.sum_univ_zero, Matrix.cons_val_zero, Matrix.cons_val_one,
        Matrix.head_cons, Matrix.cons_val, Fin.isValue, Pi.sub_apply] <;> decide
    have hd1 : ((![0,1,0,0,0,0,0,0,0,0] : Fin 10 → ℤ) - u) ∈ LinearMap.range (d1lin ℤ) := by
      rw [hu]
      apply preim ![0,1,0,0,0,0,1,0,0,0,-1,0,-1,0,0]
      funext j; fin_cases j <;>
      simp only [Matrix.mulVec, dotProduct, d1mat, triList, edgeIdx, Matrix.map_apply,
        Fin.sum_univ_succ, Fin.sum_univ_zero, Matrix.cons_val_zero, Matrix.cons_val_one,
        Matrix.head_cons, Matrix.cons_val, Fin.isValue, Pi.sub_apply] <;> decide
    have hd2 : ((![0,0,1,0,0,0,0,0,0,0] : Fin 10 → ℤ) - u) ∈ LinearMap.range (d1lin ℤ) := by
      rw [hu]
      apply preim ![0,1,0,0,0,0,0,0,0,0,0,0,0,0,0]
      funext j; fin_cases j <;>
      simp only [Matrix.mulVec, dotProduct, d1mat, triList, edgeIdx, Matrix.map_apply,
        Fin.sum_univ_succ, Fin.sum_univ_zero, Matrix.cons_val_zero, Matrix.cons_val_one,
        Matrix.head_cons, Matrix.cons_val, Fin.isValue, Pi.sub_apply] <;> decide
    have hd3 : ((![0,0,0,1,0,0,0,0,0,0] : Fin 10 → ℤ) - u) ∈ LinearMap.range (d1lin ℤ) := by
      rw [hu]
      apply preim ![0,1,1,0,0,0,1,0,0,0,-1,0,-1,0,0]
      funext j; fin_cases j <;>
      simp only [Matrix.mulVec, dotProduct, d1mat, triList, edgeIdx, Matrix.map_apply,
        Fin.sum_univ_succ, Fin.sum_univ_zero, Matrix.cons_val_zero, Matrix.cons_val_one,
        Matrix.head_cons, Matrix.cons_val, Fin.isValue, Pi.sub_apply] <;> decide
    have hd4 : ((![0,0,0,0,1,0,0,0,0,0] : Fin 10 → ℤ) - u) ∈ LinearMap.range (d1lin ℤ) := by
      rw [hu]
      apply preim ![0,1,0,1,0,0,0,0,0,0,0,0,0,0,0]
      funext j; fin_cases j <;>
      simp only [Matrix.mulVec, dotProduct, d1mat, triList, edgeIdx, Matrix.map_apply,
        Fin.sum_univ_succ, Fin.sum_univ_zero, Matrix.cons_val_zero, Matrix.cons_val_one,
        Matrix.head_cons, Matrix.cons_val, Fin.isValue, Pi.sub_apply] <;> decide
    have hd5 : ((![0,0,0,0,0,1,0,0,0,0] : Fin 10 → ℤ) - u) ∈ LinearMap.range (d1lin ℤ) := by
      rw [hu]
      apply preim ![-1,1,0,0,0,1,1,0,0,0,-1,0,-1,0,0]
      funext j; fin_cases j <;>
      simp only [Matrix.mulVec, dotProduct, d1mat, triList, edgeIdx, Matrix.map_apply,
        Fin.sum_univ_succ, Fin.sum_univ_zero, Matrix.cons_val_zero, Matrix.cons_val_one,
        Matrix.head_cons, Matrix.cons_val, Fin.isValue, Pi.sub_apply] <;> decide
    have hd6 : ((![0,0,0,0,0,0,1,0,0,0] : Fin 10 → ℤ) - u) ∈ LinearMap.range (d1lin ℤ) := by
      rw [hu]
      apply preim ![-1,0,0,0,0,0,1,0,0,0,0,0,0,0,0]
      funext j; fin_cases j <;>
      simp only [Matrix.mulVec, dotProduct, d1mat, triList, edgeIdx, Matrix.map_apply,
        Fin.sum_univ_succ, Fin.sum_univ_zero, Matrix.cons_val_zero, Matrix.cons_val_one,
        Matrix.head_cons, Matrix.cons_val, Fin.isValue, Pi.sub_apply] <;> decide
    have hd7 : ((![0,0,0,0,0,0,0,1,0,0] : Fin 10 → ℤ) - u) ∈ LinearMap.range (d1lin ℤ) := by
      rw [hu]
      apply preim ![-1,0,0,0,0,0,1,1,0,0,0,0,0,0,0]
      funext j; fin_cases j <;>
      simp only [Matrix.mulVec, dotProduct, d1mat, triList, edgeIdx, Matrix.map_apply,
        Fin.sum_univ_succ, Fin.sum_univ_zero, Matrix.cons_val_zero, Matrix.cons_val_one,
        Matrix.head_cons, Matrix.cons_val, Fin.isValue, Pi.sub_apply] <;> decide
    have hd8 : ((![0,0,0,0,0,0,0,0,1,0] : Fin 10 → ℤ) - u) ∈ LinearMap.range (d1lin ℤ) := by
      rw [hu]
      apply preim ![0,1,0,0,0,0,0,0,0,0,-1,0,0,0,0]
      funext j; fin_cases j <;>
      simp only [Matrix.mulVec, dotProduct, d1mat, triList, edgeIdx, Matrix.map_apply,
        Fin.sum_univ_succ, Fin.sum_univ_zero, Matrix.cons_val_zero, Matrix.cons_val_one,
        Matrix.head_cons, Matrix.cons_val, Fin.isValue, Pi.sub_apply] <;> decide
    have hd9 : ((![0,0,0,0,0,0,0,0,0,1] : Fin 10 → ℤ) - u) ∈ LinearMap.range (d1lin ℤ) := by
      rw [hu]
      apply preim ![-1,0,0,0,0,0,1,0,0,1,0,0,-1,0,0]
      funext j; fin_cases j <;>
      simp only [Matrix.mulVec, dotProduct, d1mat, triList, edgeIdx, Matrix.map_apply,
        Fin.sum_univ_succ, Fin.sum_univ_zero, Matrix.cons_val_zero, Matrix.cons_val_one,
        Matrix.head_cons, Matrix.cons_val, Fin.isValue, Pi.sub_apply] <;> decide
    have general : ∀ (q c : ℤ),
        (v 0 + v 1 + v 2 + v 3 + v 4 + v 5 + v 6 + v 7 + v 8 + v 9) = 2 * q + c →
        v - c • u ∈ LinearMap.range (d1lin ℤ) := by
      intro q c hsq
      have hcomb :
          q • ((2:ℤ) • u) +
          (v 0 • ((![1,0,0,0,0,0,0,0,0,0] : Fin 10 → ℤ) - u) +
          (v 1 • ((![0,1,0,0,0,0,0,0,0,0] : Fin 10 → ℤ) - u) +
          (v 2 • ((![0,0,1,0,0,0,0,0,0,0] : Fin 10 → ℤ) - u) +
          (v 3 • ((![0,0,0,1,0,0,0,0,0,0] : Fin 10 → ℤ) - u) +
          (v 4 • ((![0,0,0,0,1,0,0,0,0,0] : Fin 10 → ℤ) - u) +
          (v 5 • ((![0,0,0,0,0,1,0,0,0,0] : Fin 10 → ℤ) - u) +
          (v 6 • ((![0,0,0,0,0,0,1,0,0,0] : Fin 10 → ℤ) - u) +
          (v 7 • ((![0,0,0,0,0,0,0,1,0,0] : Fin 10 → ℤ) - u) +
          (v 8 • ((![0,0,0,0,0,0,0,0,1,0] : Fin 10 → ℤ) - u) +
          v 9 • ((![0,0,0,0,0,0,0,0,0,1] : Fin 10 → ℤ) - u))))))))))
          ∈ LinearMap.range (d1lin ℤ) := by
        apply add_mem (Submodule.smul_mem _ _ h2u)
        apply add_mem (Submodule.smul_mem _ _ hd0)
        apply add_mem (Submodule.smul_mem _ _ hd1)
        apply add_mem (Submodule.smul_mem _ _ hd2)
        apply add_mem (Submodule.smul_mem _ _ hd3)
        apply add_mem (Submodule.smul_mem _ _ hd4)
        apply add_mem (Submodule.smul_mem _ _ hd5)
        apply add_mem (Submodule.smul_mem _ _ hd6)
        apply add_mem (Submodule.smul_mem _ _ hd7)
        apply add_mem (Submodule.smul_mem _ _ hd8)
        exact Submodule.smul_mem _ _ hd9
      have hveq :
          (q • ((2:ℤ) • u) +
          (v 0 • ((![1,0,0,0,0,0,0,0,0,0] : Fin 10 → ℤ) - u) +
          (v 1 • ((![0,1,0,0,0,0,0,0,0,0] : Fin 10 → ℤ) - u) +
          (v 2 • ((![0,0,1,0,0,0,0,0,0,0] : Fin 10 → ℤ) - u) +
          (v 3 • ((![0,0,0,1,0,0,0,0,0,0] : Fin 10 → ℤ) - u) +
          (v 4 • ((![0,0,0,0,1,0,0,0,0,0] : Fin 10 → ℤ) - u) +
          (v 5 • ((![0,0,0,0,0,1,0,0,0,0] : Fin 10 → ℤ) - u) +
          (v 6 • ((![0,0,0,0,0,0,1,0,0,0] : Fin 10 → ℤ) - u) +
          (v 7 • ((![0,0,0,0,0,0,0,1,0,0] : Fin 10 → ℤ) - u) +
          (v 8 • ((![0,0,0,0,0,0,0,0,1,0] : Fin 10 → ℤ) - u) +
          v 9 • ((![0,0,0,0,0,0,0,0,0,1] : Fin 10 → ℤ) - u))))))))))) = v - c • u := by
        rw [hu]
        funext j
        fin_cases j <;>
          (simp only [Pi.add_apply, Pi.smul_apply, Pi.sub_apply, smul_eq_mul]
           norm_num [Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons,
             Matrix.cons_val_fin_one, Matrix.cons_val]
           try linarith [hsq])
      rwa [hveq] at hcomb
    rcases Int.even_or_odd (v 0 + v 1 + v 2 + v 3 + v 4 + v 5 + v 6 + v 7 + v 8 + v 9) with ⟨k, hk⟩ | ⟨k, hk⟩
    · left
      have := general k 0 (by omega)
      simpa using this
    · right
      have := general k 1 (by omega)
      simpa using this

def phi2 : (Fin 10 → ZMod 2) →ₗ[ZMod 2] ZMod 2 := ∑ i : Fin 10, LinearMap.proj i

theorem phi2_apply (v : Fin 10 → ZMod 2) : phi2 v = ∑ i : Fin 10, v i := by
  unfold phi2
  rw [LinearMap.sum_apply]
  rfl

theorem phi2_range_zero (v : Fin 10 → ZMod 2) (hv : v ∈ LinearMap.range (d1lin (ZMod 2))) : phi2 v = 0 := by
  rw [phi2_apply]
  obtain ⟨z, hz⟩ := hv
  unfold d1lin at hz
  rw [Matrix.mulVecLin_apply] at hz
  rw [← hz]
  simp only [Matrix.mulVec, dotProduct]
  rw [Finset.sum_comm]
  have key : ∀ e : Fin 15, (∑ t : Fin 10, (d1mat.map (Int.cast : ℤ → ZMod 2)) t e * z e) = 0 := by
    intro e
    rw [← Finset.sum_mul]
    have hcol : (∑ t : Fin 10, (d1mat.map (Int.cast : ℤ → ZMod 2)) t e) = 0 := by
      fin_cases e <;> decide
    rw [hcol, zero_mul]
  rw [Finset.sum_congr rfl (fun e _ => key e)]
  simp

set_option maxHeartbeats 1000000 in

theorem phi2_mem_range (v : Fin 10 → ZMod 2) (hv : phi2 v = 0) : v ∈ LinearMap.range (d1lin (ZMod 2)) := by
  have preim : ∀ (z : Fin 15 → ZMod 2) (target : Fin 10 → ZMod 2),
      (d1mat.map (Int.cast : ℤ → ZMod 2)).mulVec z = target → target ∈ LinearMap.range (d1lin (ZMod 2)) := by
    intro z target hz
    refine ⟨z, ?_⟩
    unfold d1lin
    rw [Matrix.mulVecLin_apply]
    exact hz
  have hd1 : ((![0,1,0,0,0,0,0,0,0,0] : Fin 10 → ZMod 2) - ![1,0,0,0,0,0,0,0,0,0]) ∈ LinearMap.range (d1lin (ZMod 2)) := by
    apply preim ![0,1,0,0,0,0,1,0,0,0,-1,0,-1,0,0]
    funext j; fin_cases j <;>
      simp only [Matrix.mulVec, dotProduct, d1mat, triList, edgeIdx, Matrix.map_apply,
        Fin.sum_univ_succ, Fin.sum_univ_zero, Matrix.cons_val_zero, Matrix.cons_val_one,
        Matrix.head_cons, Matrix.cons_val, Fin.isValue, Pi.sub_apply] <;> decide
  have hd2 : ((![0,0,1,0,0,0,0,0,0,0] : Fin 10 → ZMod 2) - ![1,0,0,0,0,0,0,0,0,0]) ∈ LinearMap.range (d1lin (ZMod 2)) := by
    apply preim ![0,1,0,0,0,0,0,0,0,0,0,0,0,0,0]
    funext j; fin_cases j <;>
      simp only [Matrix.mulVec, dotProduct, d1mat, triList, edgeIdx, Matrix.map_apply,
        Fin.sum_univ_succ, Fin.sum_univ_zero, Matrix.cons_val_zero, Matrix.cons_val_one,
        Matrix.head_cons, Matrix.cons_val, Fin.isValue, Pi.sub_apply] <;> decide
  have hd3 : ((![0,0,0,1,0,0,0,0,0,0] : Fin 10 → ZMod 2) - ![1,0,0,0,0,0,0,0,0,0]) ∈ LinearMap.range (d1lin (ZMod 2)) := by
    apply preim ![0,1,1,0,0,0,1,0,0,0,-1,0,-1,0,0]
    funext j; fin_cases j <;>
      simp only [Matrix.mulVec, dotProduct, d1mat, triList, edgeIdx, Matrix.map_apply,
        Fin.sum_univ_succ, Fin.sum_univ_zero, Matrix.cons_val_zero, Matrix.cons_val_one,
        Matrix.head_cons, Matrix.cons_val, Fin.isValue, Pi.sub_apply] <;> decide
  have hd4 : ((![0,0,0,0,1,0,0,0,0,0] : Fin 10 → ZMod 2) - ![1,0,0,0,0,0,0,0,0,0]) ∈ LinearMap.range (d1lin (ZMod 2)) := by
    apply preim ![0,1,0,1,0,0,0,0,0,0,0,0,0,0,0]
    funext j; fin_cases j <;>
      simp only [Matrix.mulVec, dotProduct, d1mat, triList, edgeIdx, Matrix.map_apply,
        Fin.sum_univ_succ, Fin.sum_univ_zero, Matrix.cons_val_zero, Matrix.cons_val_one,
        Matrix.head_cons, Matrix.cons_val, Fin.isValue, Pi.sub_apply] <;> decide
  have hd5 : ((![0,0,0,0,0,1,0,0,0,0] : Fin 10 → ZMod 2) - ![1,0,0,0,0,0,0,0,0,0]) ∈ LinearMap.range (d1lin (ZMod 2)) := by
    apply preim ![-1,1,0,0,0,1,1,0,0,0,-1,0,-1,0,0]
    funext j; fin_cases j <;>
      simp only [Matrix.mulVec, dotProduct, d1mat, triList, edgeIdx, Matrix.map_apply,
        Fin.sum_univ_succ, Fin.sum_univ_zero, Matrix.cons_val_zero, Matrix.cons_val_one,
        Matrix.head_cons, Matrix.cons_val, Fin.isValue, Pi.sub_apply] <;> decide
  have hd6 : ((![0,0,0,0,0,0,1,0,0,0] : Fin 10 → ZMod 2) - ![1,0,0,0,0,0,0,0,0,0]) ∈ LinearMap.range (d1lin (ZMod 2)) := by
    apply preim ![-1,0,0,0,0,0,1,0,0,0,0,0,0,0,0]
    funext j; fin_cases j <;>
      simp only [Matrix.mulVec, dotProduct, d1mat, triList, edgeIdx, Matrix.map_apply,
        Fin.sum_univ_succ, Fin.sum_univ_zero, Matrix.cons_val_zero, Matrix.cons_val_one,
        Matrix.head_cons, Matrix.cons_val, Fin.isValue, Pi.sub_apply] <;> decide
  have hd7 : ((![0,0,0,0,0,0,0,1,0,0] : Fin 10 → ZMod 2) - ![1,0,0,0,0,0,0,0,0,0]) ∈ LinearMap.range (d1lin (ZMod 2)) := by
    apply preim ![-1,0,0,0,0,0,1,1,0,0,0,0,0,0,0]
    funext j; fin_cases j <;>
      simp only [Matrix.mulVec, dotProduct, d1mat, triList, edgeIdx, Matrix.map_apply,
        Fin.sum_univ_succ, Fin.sum_univ_zero, Matrix.cons_val_zero, Matrix.cons_val_one,
        Matrix.head_cons, Matrix.cons_val, Fin.isValue, Pi.sub_apply] <;> decide
  have hd8 : ((![0,0,0,0,0,0,0,0,1,0] : Fin 10 → ZMod 2) - ![1,0,0,0,0,0,0,0,0,0]) ∈ LinearMap.range (d1lin (ZMod 2)) := by
    apply preim ![0,1,0,0,0,0,0,0,0,0,-1,0,0,0,0]
    funext j; fin_cases j <;>
      simp only [Matrix.mulVec, dotProduct, d1mat, triList, edgeIdx, Matrix.map_apply,
        Fin.sum_univ_succ, Fin.sum_univ_zero, Matrix.cons_val_zero, Matrix.cons_val_one,
        Matrix.head_cons, Matrix.cons_val, Fin.isValue, Pi.sub_apply] <;> decide
  have hd9 : ((![0,0,0,0,0,0,0,0,0,1] : Fin 10 → ZMod 2) - ![1,0,0,0,0,0,0,0,0,0]) ∈ LinearMap.range (d1lin (ZMod 2)) := by
    apply preim ![-1,0,0,0,0,0,1,0,0,1,0,0,-1,0,0]
    funext j; fin_cases j <;>
      simp only [Matrix.mulVec, dotProduct, d1mat, triList, edgeIdx, Matrix.map_apply,
        Fin.sum_univ_succ, Fin.sum_univ_zero, Matrix.cons_val_zero, Matrix.cons_val_one,
        Matrix.head_cons, Matrix.cons_val, Fin.isValue, Pi.sub_apply] <;> decide
  have hcomb :
      (v 1 • ((![0,1,0,0,0,0,0,0,0,0] : Fin 10 → ZMod 2) - ![1,0,0,0,0,0,0,0,0,0]) +
       v 2 • ((![0,0,1,0,0,0,0,0,0,0] : Fin 10 → ZMod 2) - ![1,0,0,0,0,0,0,0,0,0]) +
       v 3 • ((![0,0,0,1,0,0,0,0,0,0] : Fin 10 → ZMod 2) - ![1,0,0,0,0,0,0,0,0,0]) +
       v 4 • ((![0,0,0,0,1,0,0,0,0,0] : Fin 10 → ZMod 2) - ![1,0,0,0,0,0,0,0,0,0]) +
       v 5 • ((![0,0,0,0,0,1,0,0,0,0] : Fin 10 → ZMod 2) - ![1,0,0,0,0,0,0,0,0,0]) +
       v 6 • ((![0,0,0,0,0,0,1,0,0,0] : Fin 10 → ZMod 2) - ![1,0,0,0,0,0,0,0,0,0]) +
       v 7 • ((![0,0,0,0,0,0,0,1,0,0] : Fin 10 → ZMod 2) - ![1,0,0,0,0,0,0,0,0,0]) +
       v 8 • ((![0,0,0,0,0,0,0,0,1,0] : Fin 10 → ZMod 2) - ![1,0,0,0,0,0,0,0,0,0]) +
       v 9 • ((![0,0,0,0,0,0,0,0,0,1] : Fin 10 → ZMod 2) - ![1,0,0,0,0,0,0,0,0,0]))
      ∈ LinearMap.range (d1lin (ZMod 2)) := by
    apply add_mem
    apply add_mem
    apply add_mem
    apply add_mem
    apply add_mem
    apply add_mem
    apply add_mem
    apply add_mem
    · exact Submodule.smul_mem _ (v 1) hd1
    · exact Submodule.smul_mem _ (v 2) hd2
    · exact Submodule.smul_mem _ (v 3) hd3
    · exact Submodule.smul_mem _ (v 4) hd4
    · exact Submodule.smul_mem _ (v 5) hd5
    · exact Submodule.smul_mem _ (v 6) hd6
    · exact Submodule.smul_mem _ (v 7) hd7
    · exact Submodule.smul_mem _ (v 8) hd8
    · exact Submodule.smul_mem _ (v 9) hd9
  have hv' : v 0 + (v 1 + (v 2 + (v 3 + (v 4 + (v 5 + (v 6 + (v 7 + (v 8 + v 9)))))))) = 0 := by
    rw [phi2_apply] at hv
    simpa [Fin.sum_univ_succ] using hv
  have hveq :
      (v 1 • ((![0,1,0,0,0,0,0,0,0,0] : Fin 10 → ZMod 2) - ![1,0,0,0,0,0,0,0,0,0]) +
       v 2 • ((![0,0,1,0,0,0,0,0,0,0] : Fin 10 → ZMod 2) - ![1,0,0,0,0,0,0,0,0,0]) +
       v 3 • ((![0,0,0,1,0,0,0,0,0,0] : Fin 10 → ZMod 2) - ![1,0,0,0,0,0,0,0,0,0]) +
       v 4 • ((![0,0,0,0,1,0,0,0,0,0] : Fin 10 → ZMod 2) - ![1,0,0,0,0,0,0,0,0,0]) +
       v 5 • ((![0,0,0,0,0,1,0,0,0,0] : Fin 10 → ZMod 2) - ![1,0,0,0,0,0,0,0,0,0]) +
       v 6 • ((![0,0,0,0,0,0,1,0,0,0] : Fin 10 → ZMod 2) - ![1,0,0,0,0,0,0,0,0,0]) +
       v 7 • ((![0,0,0,0,0,0,0,1,0,0] : Fin 10 → ZMod 2) - ![1,0,0,0,0,0,0,0,0,0]) +
       v 8 • ((![0,0,0,0,0,0,0,0,1,0] : Fin 10 → ZMod 2) - ![1,0,0,0,0,0,0,0,0,0]) +
       v 9 • ((![0,0,0,0,0,0,0,0,0,1] : Fin 10 → ZMod 2) - ![1,0,0,0,0,0,0,0,0,0])) = v := by
    funext j
    fin_cases j <;>
      (simp only [Pi.add_apply, Pi.smul_apply, Pi.sub_apply, smul_eq_mul]
       norm_num [Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons,
         Matrix.cons_val_fin_one, Matrix.cons_val]) <;>
      linear_combination (norm := (ring_nf; try simp [CharTwo.two_eq_zero]; try ring_nf)) hv'
  rwa [hveq] at hcomb

theorem H2_zmod2_witness : ∃ u : Fin 10 → ZMod 2,
    u ∉ LinearMap.range (d1lin (ZMod 2)) ∧
    (∀ v : Fin 10 → ZMod 2, v ∈ LinearMap.range (d1lin (ZMod 2)) ∨
      v - u ∈ LinearMap.range (d1lin (ZMod 2))) := by
  refine ⟨![1,0,0,0,0,0,0,0,0,0], ?_, ?_⟩
  · intro h
    have := phi2_range_zero _ h
    rw [phi2_apply] at this
    simp [Fin.sum_univ_succ] at this
  · intro v
    have hu : phi2 (![1,0,0,0,0,0,0,0,0,0] : Fin 10 → ZMod 2) = 1 := by
      rw [phi2_apply]; simp [Fin.sum_univ_succ]
    have hx : ∀ y : ZMod 2, y = 0 ∨ y = 1 := by decide
    rcases hx (phi2 v) with h0 | h1
    · left; exact phi2_mem_range v h0
    · right
      apply phi2_mem_range
      rw [map_sub, hu, h1]; exact sub_self 1

theorem two_elt_addequiv_zmod2 (A : Type) [AddCommGroup A] (g : A)
    (hg : g ≠ 0) (h2 : (2 : ℤ) • g = 0) (hcov : ∀ x : A, x = 0 ∨ x = g) :
    Nonempty (A ≃+ ZMod 2) := by
  classical
  have hgg : g + g = 0 := by
    have : (2 : ℤ) • g = g + g := by rw [two_smul]
    rw [this] at h2; exact h2
  have hg0 : (0 : A) ≠ g := fun h => hg h.symm
  have h10 : (1 : ZMod 2) ≠ 0 := by decide
  have h110 : (1 : ZMod 2) + 1 = 0 := by decide
  have hzc : ∀ c : ZMod 2, c = 0 ∨ c = 1 := by decide
  refine ⟨{
    toFun := fun x => if x = g then 1 else 0
    invFun := fun c => if c = 0 then 0 else g
    left_inv := ?_
    right_inv := ?_
    map_add' := ?_
  }⟩
  · intro x
    rcases hcov x with h | h <;> subst h <;> simp_all
  · intro c
    rcases hzc c with h | h <;> subst h <;> simp_all
  · intro x y
    rcases hcov x with hx | hx <;> rcases hcov y with hy | hy <;> subst hx <;> subst hy <;>
      simp_all [h110]

theorem H2_classes_of_witness (R : Type) [CommRing R] (u : Fin 10 → R)
    (h2 : (2 : R) • u ∈ LinearMap.range (d1lin R))
    (hu : u ∉ LinearMap.range (d1lin R))
    (hcov : ∀ v : Fin 10 → R, v ∈ LinearMap.range (d1lin R) ∨ v - u ∈ LinearMap.range (d1lin R)) :
    ∃ g : H2 R, g ≠ 0 ∧ (2 : ℤ) • g = 0 ∧ (∀ x : H2 R, x = 0 ∨ x = g) := by
  refine ⟨Submodule.Quotient.mk u, ?_, ?_, ?_⟩
  · rw [Ne, Submodule.Quotient.mk_eq_zero]; exact hu
  · have h2u : (2:ℤ) • u = (2:R) • u := by
      funext i; simp only [Pi.smul_apply, zsmul_eq_mul, smul_eq_mul]; push_cast; ring
    rw [show ((2:ℤ) • (Submodule.Quotient.mk u : H2 R)) = Submodule.Quotient.mk ((2:ℤ) • u) from ?_]
    · rw [h2u, Submodule.Quotient.mk_eq_zero]; exact h2
    · rw [← Submodule.Quotient.mk_smul]
  · intro x
    obtain ⟨v, rfl⟩ := Submodule.Quotient.mk_surjective _ x
    rcases hcov v with h | h
    · left; rw [Submodule.Quotient.mk_eq_zero]; exact h
    · right; rw [Submodule.Quotient.eq]; exact h

theorem H2_equiv_of_witness (R : Type) [CommRing R] (u : Fin 10 → R)
    (h2 : (2 : R) • u ∈ LinearMap.range (d1lin R))
    (hu : u ∉ LinearMap.range (d1lin R))
    (hcov : ∀ v : Fin 10 → R, v ∈ LinearMap.range (d1lin R) ∨ v - u ∈ LinearMap.range (d1lin R)) :
    Nonempty (H2 R ≃+ ZMod 2) := by
  obtain ⟨g, hg, h2g, hcov'⟩ := H2_classes_of_witness R u h2 hu hcov
  exact two_elt_addequiv_zmod2 (H2 R) g hg h2g hcov'

theorem H2_int : Nonempty (H2 ℤ ≃+ ZMod 2) := by
  obtain ⟨u, h2, hu, hcov⟩ := H2_int_witness
  exact H2_equiv_of_witness ℤ u h2 hu hcov

theorem H2_zmod2 : Nonempty (H2 (ZMod 2) ≃+ ZMod 2) := by
  obtain ⟨u, hu, hcov⟩ := H2_zmod2_witness
  apply H2_equiv_of_witness (ZMod 2) u ?_ hu hcov
  have : (2 : ZMod 2) = 0 := by decide
  rw [this, zero_smul]
  exact Submodule.zero_mem _
```
