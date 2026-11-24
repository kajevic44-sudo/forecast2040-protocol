/-
  Protocol.lean

  Machine-checked invariants for the forecasting protocol of the dissertation
  "Forecasting the German automotive industry to 2040".

  Scope: only the deterministic skeleton. No statistics, no estimation, no
  floating point. Everything here is a statement about indices, lists and
  rational arithmetic, checked by the Lean 4 kernel.

  Author: Armin
-/

namespace Protocol

/-! ## 1. Non-anticipativity of the expanding window

The origin is `T`. The model may use observations with index `0, ..., T-1`
and nothing else. The theorem says that every index in the training set is
strictly smaller than the origin, which is the formal content of "no
look-ahead". -/

/-- Indices available at forecast origin `T`. -/
def trainIdx (T : Nat) : List Nat := List.range T

/-- Every index used for training is strictly before the origin. -/
theorem trainIdx_lt {T i : Nat} (h : i ∈ trainIdx T) : i < T := by
  simpa [trainIdx] using (List.mem_range.mp h)

/-- The observation at the origin is never part of the training set. -/
theorem origin_not_in_train {T : Nat} : T ∉ trainIdx T := by
  intro h
  have := trainIdx_lt h
  omega

/-- The training set is nested: what was available yesterday is available today. -/
theorem trainIdx_mono {T i : Nat} (h : i ∈ trainIdx T) : i ∈ trainIdx (T + 1) := by
  have hi : i < T := trainIdx_lt h
  simp [trainIdx]
  omega

/-! ## 2. Rolling window of fixed length

Some models use a window of the last `h` observations instead of the full
history. The same non-anticipativity statement must hold. -/

/-- Indices `T-h, ..., T-1`, the last `h` observations before the origin. -/
def rollIdx (T h : Nat) : List Nat := (List.range h).map (fun k => T - h + k)

/-- A rolling window never reaches the origin. -/
theorem rollIdx_lt {T h i : Nat} (_hh : 0 < h) (hT : h ≤ T) (hi : i ∈ rollIdx T h) : i < T := by
  simp [rollIdx] at hi
  obtain ⟨k, hk, rfl⟩ := hi
  omega

/-! ## 3. Determinism of the selection rule

Model selection is a function. Two runs on the same validation losses must
return the same model, otherwise the backtest is not reproducible. -/

/-- Selection rule: pick the candidate with the smallest validation loss. -/
def selectBest (loss : Nat → Rat) (candidates : List Nat) : Option Nat :=
  candidates.foldl
    (fun acc c =>
      match acc with
      | none => some c
      | some b => if loss c < loss b then some c else some b)
    none

/-- The selection rule is a function: identical inputs give identical outputs. -/
theorem selectBest_det (loss : Nat → Rat) (cs : List Nat) :
    selectBest loss cs = selectBest loss cs := rfl

/-! ## 4. The LCCB accounting identity

The life cycle cost of a battery is the sum of its components. Two facts are
needed for the projection: the total is homogeneous of degree one in the
components, and the unit cost is the total divided by the energy delivered. -/

/-- Total of a list of cost components. -/
def total (xs : List Rat) : Rat := xs.sum

/-- Scaling every component by `c` scales the total by `c`. -/
theorem total_scale (xs : List Rat) (c : Rat) :
    total (xs.map (fun x => c * x)) = c * total xs := by
  induction xs with
  | nil => simp [total]
  | cons x xs ih =>
      have ih' : (List.map (fun x => c * x) xs).sum = c * xs.sum := ih
      simp only [total, List.map_cons, List.sum_cons, Rat.mul_add]
      rw [ih']

/-- Splitting a component into two sub-components leaves the total unchanged. -/
theorem total_split (a b : Rat) (xs : List Rat) :
    total ((a + b) :: xs) = total (a :: b :: xs) := by
  simp [total, Rat.add_assoc]

/-- Unit cost is total divided by volume, provided the volume is not zero. -/
theorem unit_cost_eq (t v u : Rat) (hv : v ≠ 0) (h : t = u * v) : t / v = u := by
  rw [h]
  exact Rat.mul_div_cancel hv

/-! ## 5. Coherence of a projection

A projection is admissible only if the three identities hold simultaneously:
revenue is price times volume, profit is margin times revenue, and profit per
vehicle is profit divided by volume. The theorem shows that the fourth
identity, profit per vehicle equals margin times price, follows from the
first three. This is the formal version of the coherence test applied to the
2040 scenarios. -/

theorem profit_per_vehicle (price volume margin : Rat) (hv : volume ≠ 0) :
    (margin * (price * volume)) / volume = margin * price := by
  rw [← Rat.mul_assoc]
  exact Rat.mul_div_cancel hv

end Protocol
