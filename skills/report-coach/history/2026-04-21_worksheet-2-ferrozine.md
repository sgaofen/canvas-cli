# Worksheet 2 — Lab 2 Ferrozine (graded 2026-04-21)

**Assignment**: Lab 2 Worksheet — Determination of Aqueous [Fe(II)] & [Fe(III)] with Ferrozine
**Subject**: CHEM M3LC (Analytical Chemistry Lab)
**Submission**: `submission_406797540.pdf` (Gradescope export, 15 pages)
**Score**: **96 / 100**
**Grader**: TA (signed as "Brad" in prior email; individual Q grading may be different TA)

---

## Per-question breakdown

| Q# in rubric | Q# in worksheet | Earned / Max | Status | Notes |
|---|---|---:|---|---|
| 1 | Abstract | 10/10 | ✅ full | Grader note: "Mentions most chemicals but missing ferrozine" — lenient, no deduction |
| 2 | Q1 (abs overlay) | 6/6 | ✅ full | −2 for logger-pro graphs NOT applied (matplotlib plots used). Note: "No titles allowed" |
| 3 | Q2 (λmax determination) | 6/6 | ✅ full | Reasonable value, explained derivation |
| 4 | Q3 (Beer's Law) | 6/6 | ✅ full | Grader note: "Caption should be concise. No titles allowed" |
| 5 | Q4 (slope+intercept CI) | 4/4 | ✅ full | Reported `m = 30 ± 10 mM⁻¹`, `b = 0.1 ± 0.3` — correct sig-fig format, correct units |
| 6 | Q5 (Part C unknown plot) | 6/6 | ✅ full | matplotlib plot, no logger-pro deduction |
| 7 | Q6 (FeII conc + molar mass) | 12/12 | ✅ full | 6 sub-items, all credited. Expected initial mol = 0.0001864; Stephen's work matched |
| **8** | **Q7 (unknown ID + % error)** | **2/6** | ❌ **−4** | **See "Lost points" below** |
| 9 | Q8 (Part D spectra) | 6/6 | ✅ full | matplotlib plot, good caption |
| 10 | Q9 (Fe(III) calc, 5 sub-parts) | 18/18 | ✅ full | All sub-parts including error propagation |
| 11 | Q10 (transmittance ↔ absorbance) | 4/4 | ✅ full | Mentioned log relationship and linear-in-c property |
| 12 | Q11 (role of ferrozine) | 6/6 | ✅ full | Covered binding, necessity in B, usefulness in D |
| 13 | Q12 (why reducing agent) | 6/6 | ✅ full | Explained subtraction approach |
| 14 | Q13 (photon energy) | 4/4 | ✅ full | Showed E = hν, calculated answer |

**Total: 96 / 100**

---

## Lost points — Q7 (Unknown ID + percent error), 2/6

### Deduction 1: Missing ID number (−2 pts)
**Grader rubric:** `+2 pts 2 pt for ID number` — **NOT earned (no checkmark)**
**Grader comment:** "Missing ID number. Percent error should be positive"
**What Stephen wrote:**
> Unknown ID number: *[Forgot to record]*

**What was expected:** The TA-assigned unknown number from the bench. If genuinely forgotten, a prose acknowledgment that the number was not recorded (and identification rests on molar-mass match alone) would have been more likely to earn partial credit than a bracketed placeholder.

### Deduction 2: Percent error reported with negative sign (−2 pts)
**Grader rubric:** `+2 pts 2 pt for percent error calculation` — **NOT earned (no checkmark)**
**Grader comment:** "Percent error should be positive" (same comment box as above)
**What Stephen wrote:**
> % error = (M_exp − M_theory) / M_theory × 100% = (411 − 417.77) / 417.77 × 100% = **−2%**

**What was expected:**
> % error = |M_exp − M_theory| / M_theory × 100% = |411 − 417.77| / 417.77 × 100% = **2%**
or equivalently: `% error ≈ 1.6%` (using −1.62% as the signed relative deviation, but **report only the absolute value** as percent error).

---

## Advisory comments (no deduction)

### Abstract — Q1
**Grader comment:** "Mentions most chemicals but missing ferrozine"
**Assessment:** Stephen's abstract *did* literally mention ferrozine in its opening sentence. The grader's note suggests the reference should be more explicit — probably repeated in the major-outcomes sentence ("Quantitation of Fe(II) via ferrozine absorbance at 562 nm yielded..."). No points deducted; lenient grading. Lesson: name the signature reagent at least **twice** — in purpose and in outcomes.

### Figure captions — Q3 (Beer's Law)
**Grader comment:** "Caption should be concise. No titles allowed"
**Assessment:** Stephen's Fig. 2 caption was 3 sentences and included a reference to the Linear Calibration Spreadsheet. Grader wanted 1–2 sentences (what's shown + what to notice). No deduction on Lab 2 because the no-titles rule predated the strict 2026-04-18 enforcement. For Lab 3+ this will be a hard deduction.

### Figures with on-plot titles
Stephen's Lab 2 PDFs (`fig_q5_partC_unknown.png`, `fig_q8_partD.png`) had titles baked in ("Part C: Absorbance spectra of unknown Fe²⁺ salt solutions", "Part D: Absorbance spectra of Fe³⁺ stock solution..."). Not penalized on Lab 2, will be penalized on Lab 3+ per Brad's 2026-04-18 announcement.

---

## Strengths confirmed by this report

1. **Math-heavy Qs consistently at full credit** — Q6 (12/12), Q9 (18/18), Q13 (4/4). Pattern: LaTeX formula → substitute → unit → sig-fig-rounded final.
2. **Sig-fig rule now internalized** — Q4 (slope/intercept ± CI) earned 4/4 with correct format `m = 30 ± 10 mM⁻¹`, matching the rule set from the 2026-04-14 email.
3. **Units on every dimensional value** — explicitly credited in Q4 rubric line ("1pt for correct units").
4. **Discussion/conceptual answers** — Q10, Q11, Q12, Q13 all full credit. Short paragraphs covering mechanism + lab context + specific measurement.
5. **Real graphing software used** — all four figures matplotlib PNGs, not LoggerPro screenshots. The `−2 pts improper formatting due to logger pro graph` rubric option appeared on multiple Qs but was never applied.
6. **Back-dilution chains** — Q6a 2 pts "correctly backcalculating their dilutions" fully earned; Q9 error propagation across dilution factor fully earned.

## Lessons added to `lessons.md` from this report

- **Pitfall: Placeholder text left in a submitted answer** (−2 pts)
- **Pitfall: Percent error reported with a sign** (−2 pts)
- **Advisory: Figure captions too verbose / titles inside figures** (0 pts this time, will cost Lab 3+)
- **Advisory: Abstract mentioned signature reagent but not strongly enough** (0 pts this time)
- **Strength: Calculation depth on math-heavy questions** (confirmed pattern)
- **Strength: Discussion-question content**  (confirmed pattern)
- Running scoreline added to header

## Lessons NOT repeated from Worksheet 1 (fading — good sign)

- Worksheet 1 lost all its points on sig-fig issues (standalone uncertainty not rounded to 1 sig fig; averages not matching decimal places of raw data). Worksheet 2: **zero sig-fig deductions**. The rule set from the 2026-04-14 email is being applied correctly — Q4 (slope/intercept ± CI), Q6c ([Fe²⁺] ± CI), Q9e ([Fe³⁺] ± CI) all applied the "error to 1 sig fig; value to matching decimal place" rule without error.
