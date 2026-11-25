/-
  ProtocolCausal.lean

  A self-contained Lean 4 module for the non-anticipativity property of a
  forecasting protocol. A series is a finite list of rational numbers. The
  forecast and the MASE style scale at origin m are defined as explicit
  functions of the prefix of length m, and the main theorems show that they
  are invariant under changes of the data after m.

  Only Lean core is used. There is no dependency on Mathlib.

  Author: Armin Kajevic
-/

set_option autoImplicit false

/-! ## A compatibility name for partial lookup

Lean 4.36 core calls the partial lookup function `List.getElem?` and provides the
notation `xs[i]?`. The protocol statements are phrased with `xs.get? i`, so the
module provides this thin wrapper. -/

namespace List

/-- Partial lookup of the `i`-th element of a list, `none` when the index is out of
range. This is a wrapper around `List.getElem?` that keeps the name `get?`. -/
def get? {α : Type} (xs : List α) (i : Nat) : Option α := xs[i]?

end List

/-! ## Series, prefixes and the two functionals -/

namespace ProtocolCausal

/-- A series is a finite list of rational numbers. -/
abbrev Series : Type := List Rat

/-- The prefix of length `m`, that is, the first `m` observations of `xs`.

Lean 4 reserves the token `prefix` for notation declarations, so the name is
written with escaped identifiers. The name itself is `prefix`. -/
def «prefix» (m : Nat) (xs : Series) : Series := xs.take m

/-- Arithmetic mean of a finite list of rationals. The mean of the empty list is `0`. -/
def mean (xs : Series) : Rat :=
  match xs with
  | [] => 0
  | _ => xs.sum / (xs.length : Rat)

/-- The forecast at origin `m`: the mean of the first `m` observations. -/
def forecast (m : Nat) (xs : Series) : Rat := mean («prefix» m xs)

/-- The list of absolute first differences of a series. -/
def absDiff : Series → Series
  | [] => []
  | [_] => []
  | x :: y :: rest => (y - x).abs :: absDiff (y :: rest)

/-- The MASE style scale at origin `m`: the mean absolute first difference of the
first `m` observations. It is `0` when the prefix has fewer than two observations. -/
def scale (m : Nat) (xs : Series) : Rat := mean (absDiff («prefix» m xs))

/-! ## Agreement of prefixes

The hypothesis used throughout is that two series agree on every index below the
origin `m`. The first lemma shows that this hypothesis forces the two prefixes of
length `m` to be equal; the theorems about `forecast` and `scale` are corollaries. -/

theorem prefix_congr {m : Nat} {xs ys : Series}
    (h : ∀ i, i < m → xs.get? i = ys.get? i) : «prefix» m xs = «prefix» m ys := by
  unfold «prefix»
  apply List.ext_getElem?
  intro j
  rw [List.getElem?_take, List.getElem?_take]
  by_cases hj : j < m
  · rw [ite_eq_left hj, ite_eq_left hj]
    exact h j hj
  · rw [ite_eq_right hj, ite_eq_right hj]

/-- The forecast at origin `m` is invariant under changes of the data at indices `m` and later. -/
theorem forecast_causal {m : Nat} {xs ys : Series}
    (h : ∀ i, i < m → xs.get? i = ys.get? i) : forecast m xs = forecast m ys := by
  unfold forecast
  rw [prefix_congr h]

/-- The MASE style scale at origin `m` is invariant under changes of the data at
indices `m` and later. -/
theorem scale_causal {m : Nat} {xs ys : Series}
    (h : ∀ i, i < m → xs.get? i = ys.get? i) : scale m xs = scale m ys := by
  unfold scale
  rw [prefix_congr h]

/-- The pair formed by the forecast and the scale at origin `m` is invariant under
changes of the data at indices `m` and later. -/
theorem forecast_scale_causal {m : Nat} {xs ys : Series}
    (h : ∀ i, i < m → xs.get? i = ys.get? i) :
    (forecast m xs, scale m xs) = (forecast m ys, scale m ys) := by
  rw [forecast_causal h, scale_causal h]

/-- Appending future observations does not change the forecast, provided the origin
lies inside the original series. -/
theorem forecast_append {m : Nat} {xs ys : Series} (h : m ≤ xs.length) :
    forecast m (xs ++ ys) = forecast m xs := by
  unfold forecast «prefix»
  rw [List.take_append_of_le_length h]

/-- Appending future observations does not change the scale, provided the origin
lies inside the original series. -/
theorem scale_append {m : Nat} {xs ys : Series} (h : m ≤ xs.length) :
    scale m (xs ++ ys) = scale m xs := by
  unfold scale «prefix»
  rw [List.take_append_of_le_length h]

/-! ## Lexicographic order on keys -/

/-- Lexicographic order on keys. The first component is compared first and the
second component is compared only when the first components are equal. -/
def lexLe (a b : Nat × Nat) : Prop := a.1 < b.1 ∨ (a.1 = b.1 ∧ a.2 ≤ b.2)

instance instDecidableLexLe (a b : Nat × Nat) : Decidable (lexLe a b) := by
  unfold lexLe
  infer_instance

theorem lexLe_refl (a : Nat × Nat) : lexLe a a :=
  Or.inr ⟨rfl, Nat.le_refl a.2⟩

theorem lexLe_trans {a b c : Nat × Nat} (hab : lexLe a b) (hbc : lexLe b c) :
    lexLe a c := by
  rcases hab with h | ⟨h1, h2⟩
  · rcases hbc with h' | ⟨h1', _⟩
    · exact Or.inl (Nat.lt_trans h h')
    · exact Or.inl (Nat.lt_of_lt_of_eq h h1')
  · rcases hbc with h' | ⟨h1', h2'⟩
    · exact Or.inl (by omega)
    · exact Or.inr ⟨h1.trans h1', Nat.le_trans h2 h2'⟩

theorem lexLe_antisymm {a b : Nat × Nat} (hab : lexLe a b) (hba : lexLe b a) :
    a = b := by
  rcases hab with h | ⟨h1, h2⟩
  · rcases hba with h' | ⟨h1', _⟩
    · exact absurd h (Nat.lt_asymm h')
    · omega
  · rcases hba with h' | ⟨h1', h2'⟩
    · omega
    · exact Prod.ext h1 (Nat.le_antisymm h2 h2')

theorem lexLe_total (a b : Nat × Nat) : lexLe a b ∨ lexLe b a := by
  rcases Nat.lt_trichotomy a.1 b.1 with h | h | h
  · exact Or.inl (Or.inl h)
  · rcases Nat.le_total a.2 b.2 with h2 | h2
    · exact Or.inl (Or.inr ⟨h, h2⟩)
    · exact Or.inr (Or.inr ⟨h.symm, h2⟩)
  · exact Or.inr (Or.inl h)

/-! ## Selection over candidate keys -/

/-- One selection step. The incumbent `acc` is compared with the new key `k`, and the
smaller key is kept. Ties go to the new key, so the earlier key wins. -/
def argminStep (k : Nat × Nat) : Option (Nat × Nat) → Option (Nat × Nat)
  | none => some k
  | some j => if lexLe k j then some k else some j

/-- The selected key of a candidate list: the first key that is minimal for the
lexicographic order. The empty list selects nothing. -/
def argmin : List (Nat × Nat) → Option (Nat × Nat)
  | [] => none
  | k :: ks => argminStep k (argmin ks)

/-- A selection step returns either the new key or the key held by the incumbent. -/
theorem argminStep_eq_new_or_acc {k r : Nat × Nat} {acc : Option (Nat × Nat)}
    (h : argminStep k acc = some r) : r = k ∨ ∃ j, acc = some j ∧ r = j := by
  cases acc with
  | none => exact Or.inl (Option.some.inj h).symm
  | some j0 =>
    simp only [argminStep] at h
    by_cases hle : lexLe k j0
    · simp only [hle, ite_true] at h
      exact Or.inl (Option.some.inj h).symm
    · simp only [hle, ite_false] at h
      exact Or.inr ⟨j0, rfl, (Option.some.inj h).symm⟩

/-- A selection step returns a key that is below the new key and below every key
held by the incumbent. -/
theorem argminStep_spec {k r : Nat × Nat} {acc : Option (Nat × Nat)}
    (h : argminStep k acc = some r) :
    lexLe r k ∧ ∀ j, acc = some j → lexLe r j := by
  cases acc with
  | none =>
    have hr : r = k := (Option.some.inj h).symm
    rw [hr]
    exact ⟨lexLe_refl k, fun j hj => by simp at hj⟩
  | some j0 =>
    simp only [argminStep] at h
    by_cases hle : lexLe k j0
    · simp only [hle, ite_true] at h
      have hr : r = k := (Option.some.inj h).symm
      rw [hr]
      exact ⟨lexLe_refl k, fun j hj => by
        have hjj : j = j0 := by simpa using hj.symm
        rw [hjj]
        exact hle⟩
    · simp only [hle, ite_false] at h
      have hr : r = j0 := (Option.some.inj h).symm
      rw [hr]
      exact ⟨(lexLe_total k j0).resolve_left hle, fun j hj => by
        have hjj : j = j0 := by simpa using hj.symm
        rw [hjj]
        exact lexLe_refl j0⟩

/-- A nonempty candidate list always selects a key. -/
theorem argmin_cons_ne_none (a : Nat × Nat) (as : List (Nat × Nat)) :
    argmin (a :: as) ≠ none := by
  intro h
  cases hacc : argmin as with
  | none => simp [argmin, hacc, argminStep] at h
  | some j0 =>
    by_cases hle : lexLe a j0 <;> simp [argmin, hacc, argminStep, hle] at h

/-- The selection function returns `none` only on the empty list. -/
theorem argmin_eq_none {xs : List (Nat × Nat)} (h : argmin xs = none) : xs = [] := by
  cases xs with
  | nil => rfl
  | cons a as => exact absurd h (argmin_cons_ne_none a as)

/-- The selected key is a member of the candidate list. -/
theorem argmin_mem {xs : List (Nat × Nat)} {k : Nat × Nat} (h : argmin xs = some k) :
    k ∈ xs := by
  induction xs with
  | nil => simp [argmin] at h
  | cons a as ih =>
    rcases argminStep_eq_new_or_acc (k := a) (acc := argmin as) h with hk | ⟨j, hj, hk⟩
    · subst hk
      exact List.mem_cons_self
    · subst hk
      exact List.mem_cons_of_mem a (ih hj)

/-- The selected key is below every key in the candidate list, in the lexicographic
order. -/
theorem argmin_le {xs : List (Nat × Nat)} {k : Nat × Nat} (h : argmin xs = some k) :
    ∀ j, j ∈ xs → lexLe k j := by
  induction xs generalizing k with
  | nil => simp [argmin] at h
  | cons a as ih =>
    intro j hj
    rcases List.mem_cons.mp hj with hja | hja
    · subst hja
      exact (argminStep_spec h).1
    · cases hacc : argmin as with
      | none =>
        have has : as = [] := argmin_eq_none hacc
        subst has
        simp at hja
      | some j0 =>
        exact lexLe_trans ((argminStep_spec h).2 j0 hacc) (ih hacc j hja)

/-- If the candidate keys are pairwise distinct and the selection function returns
`k`, then every candidate `j` with `j` below `k` equals `k`. -/
theorem argmin_unique {xs : List (Nat × Nat)} {k : Nat × Nat}
    (_hnd : xs.Nodup) (h : argmin xs = some k) :
    ∀ j, j ∈ xs → lexLe j k → j = k := by
  intro j hj hjk
  exact lexLe_antisymm hjk (argmin_le h j hj)

end ProtocolCausal
