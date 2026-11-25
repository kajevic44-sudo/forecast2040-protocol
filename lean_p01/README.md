# ProtocolCausal: a checked Lean 4 module for non-anticipativity

Author: Armin Kajevic

This directory contains a small Lean 4 module that formalises the
non-anticipativity property of a forecasting protocol with a MASE style scale
and a lexicographic selection rule. The module compiles with Lean core only, it
does not use Mathlib, and it contains no `sorry` and no `admit`.

## Files

- `ProtocolCausal.lean`: the whole development, definitions and theorems.
- `CheckAxioms.lean`: a scratch file that prints the axioms of every theorem.
- `lakefile.toml`, `lean-toolchain`: the Lake project, pinned to Lean 4.36.0.
- `build_log.txt`: the successful build output, the Lean version and the axiom check.

## Definitions

A series is a finite list of rational numbers, `abbrev Series : Type := List Rat`.
Rationals are used because `Rat` is part of Lean core, while `Real` would require
Mathlib. A protocol run is finite, so exact rational arithmetic is the natural
setting.

- `«prefix» m xs := xs.take m`. Lean 4 reserves the token `prefix` for notation
  declarations, so the definition is written with escaped identifiers. The name is
  `prefix`, and it is applied as `«prefix» m xs`.
- `mean xs` is the arithmetic mean of a finite list of rationals. It returns `0`
  for the empty list, which is the zero guard.
- `forecast m xs := mean («prefix» m xs)`, the mean of the first `m` observations.
- `absDiff xs` is the list of absolute first differences of `xs`.
- `scale m xs := mean (absDiff («prefix» m xs))`, the mean absolute first difference
  of the first `m` observations. It is `0` when the prefix has fewer than two
  observations, which is the zero guard for the scale.
- `lexLe a b` is the lexicographic order on keys of type `Nat × Nat`, defined as
  `a.1 < b.1 ∨ (a.1 = b.1 ∧ a.2 ≤ b.2)`. Lean core has no `LE (Nat × Nat)`
  instance, so the order is defined explicitly.
- `argminStep k acc` keeps the smaller of the new key `k` and the incumbent `acc`,
  with ties going to the new key, which is the earlier key of the candidate list.
- `argmin xs` folds `argminStep` over the candidate list and returns `none` for the
  empty list.

The hypothesis used by the causality theorems is written with `xs.get? i`. Lean
4.36 core names the partial lookup function `List.getElem?` and provides the
notation `xs[i]?`, so the module defines `List.get?` as a thin wrapper around
`List.getElem?` in order to keep the conventional name and dot notation.

## Theorems

Prefix agreement:

- `prefix_congr`: if two series agree at every index below `m`, that is
  `∀ i, i < m → xs.get? i = ys.get? i`, then `«prefix» m xs = «prefix» m ys`.

Non-anticipativity of the two functionals:

- `forecast_causal`: under the same hypothesis, `forecast m xs = forecast m ys`.
- `scale_causal`: under the same hypothesis, `scale m xs = scale m ys`.
- `forecast_scale_causal`: under the same hypothesis,
  `(forecast m xs, scale m xs) = (forecast m ys, scale m ys)`.

The same fact in the form used by the protocol, where future data are appended:

- `forecast_append`: if `m ≤ xs.length`, then
  `forecast m (xs ++ ys) = forecast m xs`.
- `scale_append`: if `m ≤ xs.length`, then `scale m (xs ++ ys) = scale m xs`.

Order lemmas for keys:

- `lexLe_refl`: `lexLe a a`.
- `lexLe_trans`: `lexLe a b` and `lexLe b c` imply `lexLe a c`.
- `lexLe_antisymm`: `lexLe a b` and `lexLe b a` imply `a = b`.
- `lexLe_total`: `lexLe a b` or `lexLe b a`.

Selection:

- `argmin_mem`: if `argmin xs = some k`, then `k` is a member of `xs`.
- `argmin_le`: if `argmin xs = some k`, then `lexLe k j` for every `j` in `xs`.
- `argmin_unique`: if the keys in `xs` are pairwise distinct (`xs.Nodup`) and
  `argmin xs = some k`, then every `j` in `xs` with `lexLe j k` equals `k`.

Supporting lemmas used by the selection proofs are `argminStep_eq_new_or_acc`,
`argminStep_spec`, `argmin_cons_ne_none` and `argmin_eq_none`. They state that a
selection step returns either the new key or the incumbent key, that the returned
key is below both of them, that a nonempty list always selects a key, and that
`argmin` returns `none` only on the empty list.

## Why this matters for the protocol

At origin `m` the protocol may use observations with indices `0` to `m - 1` only.
The forecast and the scale are compositions of `mean`, `absDiff` and
`«prefix» m`, and `prefix_congr` shows that `«prefix» m xs` is determined by the
values of `xs` at indices below `m`. Therefore any two series that coincide up to
`m` produce the same forecast and the same scale, no matter how much they differ
after `m`. The theorems `forecast_append` and `scale_append` express the same
statement in the operational form: appending future observations to a series
leaves both numbers unchanged. This is exactly the non-anticipativity property,
namely that the evaluation at origin `m` cannot depend on data that are not yet
available at `m`.

The selection theorems show that the candidate selection is well defined. The
selected key is a member of the candidate list (`argmin_mem`), it is minimal in
the lexicographic order (`argmin_le`), and when the keys are distinct every
candidate below it must equal it (`argmin_unique`), so the selected key is the
unique minimum.

## Design choices and simplifications

- Rationals instead of reals, as explained above. This keeps the development
  inside Lean core and makes every computation exact.
- `mean` has an explicit zero guard for the empty list, and `absDiff` returns the
  empty list for a prefix with fewer than two observations, so `scale` is `0` for
  prefixes of length `0` or `1`.
- The lexicographic order is a definition, `lexLe`, rather than a type class
  instance. The statements therefore read `lexLe k j` where the protocol text
  reads `k ≤ j` in the lexicographic order.
- `argmin_unique` keeps the hypothesis `xs.Nodup`, because distinct candidate keys
  are part of the protocol assumption. The conclusion follows from antisymmetry
  of `lexLe` alone, so the hypothesis is not needed by the proof. The statement
  was kept as specified and the redundancy is recorded here.
- No definition had to be simplified or weakened to make a proof pass. The
  definitions used in the statements are the ones listed above, and all proofs
  are complete.

## How to reproduce

```
cd /home/ubuntu/battery_phd/thesis/lean
lake build
```

The build exits with code `0` and prints `Build completed successfully`. To check
the axioms of the theorems, run

```
lake env lean CheckAxioms.lean
```

Every theorem depends only on the standard Lean axioms, `propext`,
`Classical.choice` and `Quot.sound`, and `lexLe_refl` and `lexLe_total` depend on
none of them. No theorem depends on `sorryAx`. The build produces no warnings.

Lean version used: 4.36.0, toolchain `leanprover/lean4:v4.36.0`, Lake 5.0.0.
