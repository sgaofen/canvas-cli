# Worksheet 4 — Acids, Bases, Titrations, Buffers

**Date analyzed**: 2026-05-16
**Score**: **100 / 100** (perfect score, verbal confirmation from Stephen; graded PDF not received)
**Subject**: CHEM M3LC — General Chemistry Laboratory, Spring 2026 (UC Irvine, Ardo)
**Writing exercise**: Results section (per Brad's Canvas announcement 2026-04-26)
**Class-shared data status at submission**: NaOH standardization data partially missing for ≥ 5 trials → applied class-pending disclosure

## Headline result

Full marks. Without rubric detail, can't do per-question breakdown, but the verbal-100 confirms that the **pre-submission self-review pass caught every real point-losing issue** before it shipped.

## Lessons reinforced (now graded-validated)

These were anticipated pitfalls (🆕 in the previous lessons.md) that Lab 4 100/100 confirms worked:

| Lesson | What we did |
|---|---|
| Iron law: answer only what's asked | Trimmed Q3 prose narration; sub-part headers shortened to `(a) <what>`; Q15/Q16 cut to 1–2 sentences. |
| Iron law: pandoc + LaTeX | All math via `$...$` → OMML; no unicode substitutes. |
| Iron law: never rebuild user-edited docx | Surgical python-docx edits after first build; `_USER_BACKUP.docx` saved before any rebuild. |
| Iron law: display precision must reproduce | Q6 near-equal % error: fixed `\|8.300−8.298\|/8.298` to `\|8.300−8.299\|/8.299` so re-compute gives the reported 0.01%. |
| Iron law: cited intermediates from script | All statistical intermediates printed from the analysis script and pasted verbatim. |
| Checklist sig figs `x ± u` | `pKa = 4.66 ± 0.02` not `± 0.03` (the actual computed CI was 0.0248, rounds DOWN). |
| Checklist no placeholders | Unknown ID was included; no `[fill in]` survived to submission. |
| Checklist % error positive | All % errors written with `\|·\|`. |
| Checklist variable label | `pKa = …` in Q7, not `pH_eq = …` (peer caught this in teammate's draft). |
| Checklist internal consistency | Table 1 Trial 3 V_eq and pH_eq verified against .cmbl files; Results section numbers match Q6/Q7 exactly. |
| Checklist chemical formula | NaH₂PO₄ / Na₂HPO₄ verified; no Na₂H₂PO₄ typo (teammate had this). |
| Checklist Logger Pro V_eq method | `argmax(dpH/dV)` discrete max used everywhere; no mix with parabolic refinement. |
| Class-pending disclosure (Q2) | Italic sentence + single-trial calc + no fabricated CI from n=1. **This is the strongest signal: the disclosure pattern is grader-accepted.** |
| Outlier exclusion on physical grounds | Alicia/Kalia trial excluded with one-sentence chemistry justification (pH_eq 6.20 vs theoretical ~9; reported [NaOH] inconsistent with stoichiometric recompute). |
| Plain undergrad voice | Methods + Discussion in first person; no AI-voice connectives. |
| Tight captions | All Lab 4 captions trimmed to 1–2 sentences, no titles baked in. |
| Plot annotation labels | Label collision (Fig 3 λ₂ vs legend) fixed in self-review by moving labels to low-y. |
| Pandoc column widths | "Flask" column letter-wrapping in v1 Table 2 fixed by moving LaTeX subscripts to caption. |
| Results section | One short paragraph, ≤ 5 sentences, every number traceable to Q6/Q7/Q12. |

## Cross-reference to lessons.md

- Iron laws IL-1 through IL-5: **all five** had at least one failure mode caught in Lab 4 self-review or peer review.
- Pre-submission checklist items #1–20: applied in full. Items most load-bearing for Lab 4: #1 (sig figs), #2 (rounding 0.0248 → 0.02), #6 (display precision), #8 (variable label), #9 (internal consistency), #17 (class-pending disclosure), #18 (physical-grounds outlier exclusion), #19 (phosphate formula).

## Open follow-up

- No graded PDF means no per-question rubric trace. If the PDF arrives later, this entry should be replaced with a full Review-mode analysis (specific +N/−N marks per question).
- The strongest unobserved-but-anticipated pitfall left to test: whether multi-question class-pending disclosure (Lab 5's Q7–Q14) survives grading at the same standard as Lab 4's single Q2 case. Watch this when Lab 5 grades come in.
