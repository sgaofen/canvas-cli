# Lessons from graded reports

*Living knowledge base. Read in full before starting any new assignment or analyzing a new report. The first three sections (Pre-submission checklist, Iron laws, Course mandates) are the daily-use distillation; the later sections are the case studies that ground them.*

**Reports graded (with rubric detail)**: 2 (Worksheet 1 sig-fig pattern, Worksheet 2 → 96/100)
**Reports graded (headline result only)**: 1 (Worksheet 4 → 100, verbal confirmation, no PDF received)
**Direct TA feedback received**: 4 (Brad's email 2026-04-14 re: Lab 2; Brad's Canvas announcement 2026-04-18 re: Lab 3; Brad's Canvas announcement 2026-04-26 re: Lab 4 results section; Brad's Canvas announcement 2026-05-18 re: Lab 6 introduction)
**Peer reviews performed**: 1 (teammate's Lab 4 worksheet, 2026-04-30 — found row-swap bug, missing-class-data Q2, sig fig error 0.03→0.02, chemistry-typo Na₂H₂PO₄→Na₂HPO₄)
**Self-reviews performed pre-submission**: 5 (Lab 2, Lab 3 v1 + v2, Lab 4 v1 + v2 + v3, Lab 5, Lab 6)
**Last updated**: 2026-05-21 (Lab 6 drafted, awaiting class data; Lab 5 grading pending)

**Running scoreline**:
- Worksheet 1: lost points only on sig figs (standalone uncertainties + average decimal-places)
- Worksheet 2: **96/100** — 4 pts lost on Q7 (left bracketed Unknown ID placeholder + signed % error)
- Worksheet 4: **100/100** — confirms that pre-submission pruning, results-section requirement, class-data disclosure, sig-fig discipline, and the no-rebuild-after-edit protocol all work as intended
- Worksheet 5: drafted 2026-05-16, single-trial Q7–Q14 due to class data not posted by deadline
- Worksheet 6: drafted 2026-05-21, single-trial Q3/Q6/Q12 (no class data posted at writing time), Part A V=28 spectrum excluded on physical grounds (anomalous A@500), Introduction section per Brad's 2026-05-18 Canvas announcement

---

## Pre-submission checklist (read top-to-bottom on every worksheet)

These are the rules that have either (a) lost points in graded work or (b) been explicitly stated by the TA. Order is by historical impact.

1. **Sig figs `x ± u`**: round `u` to 1 sig fig at the first non-zero digit; round `x` to the same decimal place. Universal per Brad 2026-04-14.
2. **Sig figs for standalone error/% error**: 1 sig fig at the first non-zero digit. `0.0248 → 0.02`, not `0.03`.
3. **Sig figs for averages**: decimal places match the least-precise raw measurement.
4. **% error is non-negative**: `% error = |x_exp − x_theory| / x_theory × 100%`. The sign of the deviation lives in a separate sentence; the reported % error is always positive.
5. **Units on every dimensional value and axis label**. Absorbance is dimensionless — never "AU".
6. **Don't round intermediates**: carry full precision through the calc chain; only round the final boxed value. *Displayed* intermediates must have enough precision to reproduce the boxed answer (lesson on near-equal % error, Lab 4 v3 Q6).
7. **No placeholder text in submitted answers** (`[TODO]`, `[fill in]`, `[forgot]`). If a value is genuinely unknown, write a plain-language sentence acknowledging it. Cost on Worksheet 2 Q7: −2 pts.
8. **Variable label matches the question**: Q7 asks for pKa → reported value labeled `pKa = …`, not `pH_eq = …`. Easy copy-paste error after Q6.
9. **Internal consistency: every table number = same number in downstream calcs = same number in Results section**. Cross-check before submit.
10. **Answer only what's asked (iron law — see below)**. Delete restated questions, prose-narrated formulas, "good-to-know" context, AI-voice connectives. Discussion answers ≤ 3 sentences typical.
11. **Pruning needs ≥ 2 passes — MANDATORY, not optional.** Lab 5 and Lab 6 both confirmed: first-draft answers carry residual "good-to-know" sentences that survive the first pass. After writing, re-read the question literally; delete every clause it didn't ask for; do this twice. Do not show the first draft. Lab 6 cost a full rebuild cycle because pruning was skipped — user flagged it as a permanent skill rule.
12. **Plain undergrad voice**: first person where natural ("I prepared…"), short-medium sentences, plain verbs, at most one em-dash per paragraph. No "Three practical consequences follow:" lists. Pushback flagged ×4.
13. **Figures**: descriptive caption in a separate paragraph below, ≤ 2 sentences, no fit equation / R² / residuals duplicated in caption (those live in the body). **No title baked into the image** (`plt.title()` removed). Legible font. Not a LoggerPro screenshot.
14. **Plot annotation labels** placed at low-y when legend is in upper-right, to avoid collision. Visually inspect every figure post-rebuild.
15. **Pandoc table column widths**: keep header text short. Move LaTeX subscripts / wavelength conditions to the caption, not into header cells. Scan every table for letter-wrapping after PDF rebuild.
16. **Logger Pro equivalence point** = `argmax(dE/dV)` discrete max (central difference), not parabolic-refined / interpolated / sigmoid-fit. Same method everywhere (data log, figure annotation, answer body, Results).
17. **Class-shared or partner data not in hand** → italic disclosure sentence + best-available calculation. Do NOT fabricate a CI from n=1 (the formula is undefined). Confirmed working in Lab 4 Q2 (full marks).
18. **Outlier exclusion on physical/chemical grounds**: when class-shared data fails an internal-consistency or stoichiometric recompute, exclude on physical grounds with one italic disclosure sentence. Don't lean on Q-test alone.
19. **Chemical-formula proofread**: phosphate H-count vs charge (Na₂HPO₄ has one H, not Na₂H₂PO₄). Whenever writing a polyatomic ion or its salt, verify.
20. **Writing exercise rotates each lab; check Canvas announcement before drafting**. Lab 2 abstract → Lab 3 methods → Lab 4 results → Lab 5 had **no announcement, so no writing exercise**. Don't stack — each lab replaces the prior, unless the worksheet itself adds something.

---

## Iron laws (multiple data points / explicit user pushback)

These have either been stated by Stephen verbatim or have re-occurred enough times that they are non-negotiable.

### IL-1. Answer only what the question literally asks. **Concise > thorough.**
For each clause in each answer, ask "did the question ask for this?" If no, delete — even if it's correct, even if it's well-written.

**MANDATORY pruning pass before any rebuild.** Pruning is not a polish step — it is a required pre-flight that gates docx generation. After drafting the markdown:
1. Re-read every answer literally against the question text. Delete clauses the question did not ask for.
2. Cut figure captions to ≤ 2 sentences each.
3. Cut Discussion answers to ≤ 3 sentences each.
4. Cut the Introduction (when present) to a single tight paragraph — Brad's announcement explicitly says "a concise paragraph", not three.
5. Then a second pass with the same checklist — first pass leaves residue.

Do not deliver a first draft. Treat the first draft as raw material that *must* be cut before showing it.

**Pruning targets, in priority order**:
1. Sentences that restate the question
2. Prose narration alongside formulas (formula + values + result is self-explanatory)
3. Procedural notes inside captions
4. Sub-part headers longer than `(a) <what>`
5. AI-voice connectives (Furthermore / Moreover / It is important to note / In conclusion / "That kind of cross-check is what makes...")
6. Chemically true but rubric-irrelevant background
7. Forward-looking promises ("once data arrives, the CI will be computed as...") — state the constraint once, don't re-explain the formula

Stephen pushback log: ×7 across Lab 3/4/5/6 drafting. *"q4b没有要求解释，我把你的解释删掉没有问题吧"*, *"太 ai 了 / 太高大上了"*, *"humanize 和简化"*, *"不要冗长回答"*, *"题目，公式，公式旁边无意义的解释，caption等等所有的所有"*, *"有没有按照之前的要求简化你的答案"* (Lab 5, twice), *"我让你给答案做瘦身你做了吗 ... 写的太冗长了，记得在skills中要写死，一定要瘦身"* (Lab 6, 2026-05-22 — escalated to a permanent rule).

### IL-2. Never rebuild a docx Stephen is editing.
Once he opens the docx in Word and starts making manual changes, do **not** rebuild from the markdown source — python-docx text extraction misses OMML math, formatting, fills. Procedure:
- Before any potentially-destructive operation, back up the current working docx to `_USER_BACKUP.docx`.
- Apply edits surgically via python-docx paragraph operations (locate-by-text, then delete/replace).
- Reserve markdown→pandoc rebuilds for the **first** docx generation only.

Stephen explicit flag: *"我改的你并没有保留啊"* (Lab 3 v2). Iron law since.

### IL-3. Pandoc + LaTeX pipeline, never python-docx + plain-text unicode for math.
Author the worksheet as markdown with `$...$` / `$$...$$` LaTeX; convert via `pypandoc.convert_file(..., extra_args=["--from=markdown+tex_math_dollars+tex_math_single_backslash", "--to=docx"])`. Pandoc renders OMML; Word displays real fractions, roots, subscripts. Unicode substitutes (√, Σ, ·, ±) visibly look worse and cost formatting points. User flag: *"你这个 worksheet 排版很差啊，公式我要 latex 格式"* (Lab 3 v1).

### IL-4. Display precision must reproduce the reported answer.
When the displayed expression rounds inputs (especially % error of near-equal values), the TA can re-compute from the displayed numbers and find a different answer. Compute with full precision underneath, then back-fill the displayed inputs with enough decimal places that re-computing them reproduces the final 1-sf answer.

Lab 4 v3 Q6: originally displayed `|8.300 - 8.298|/8.298 = 0.01%`, but re-computing gives 0.02%. Fixed by displaying `|8.300 - 8.299|/8.299` which gives 0.012% → 0.01% ✓.
Lab 5 Q5: originally displayed `|0.79954 - 0.7996|/0.7996 = 0.0073%`, re-compute gives 0.0075% → 0.008%. Fixed to 6 dp: `|0.799542 - 0.7996|/0.7996` → 0.0073% → 0.007% ✓.

### IL-5. Cited intermediate statistics must come from the script, not from memory or from a different draft.
If the answer quotes `s_yx = 2.85e-3, Σ(xi−x̄)² = 5.00` and the script used different numbers, the TA cannot reproduce. Worse: when re-using a calculation pattern from a previous draft (different inputs), the *numbers* can drift while the *formula* stays the same.

- Lab 3 self-review: `s_yx` and Σ(xi−x̄)² were hand-typed wrong; the final CI was still right but the derivation un-reproducible.
- Lab 5 Q12 self-review: log K_sp value `−8.224` was copied from an earlier sigmoid-fit analysis using `E_eq = 0.249 V`, but the displayed inputs were the discrete-max `E_eq = 0.262 V` which actually gives `−7.796`. Caught only on second pass. **Procedure**: when reusing a calc block across drafts, always re-run the script, never copy the result.

---

## Course-level requirements (TA-stated, apply to every worksheet)

These are explicit mandates from Brad. Violations cost points on every future worksheet.

### CM-1. Abstract / methods / results — writing exercise rotates per lab
- Lab 2: **abstract** (purpose, methodology/techniques, chemicals involved, major outcomes; no procedure)
- Lab 3: **methods section** (expert-chemist level summary, not a manual restatement)
- Lab 4: **results section** (state major outcomes — concentrations measured, pKa values, identifications — concise, 1 short paragraph)
- Lab 5: **no writing exercise** (verified absent from Canvas announcements 2026-04-25 → 2026-05-15)
- Lab 6: **introduction** (concise paragraph: motivation, key techniques and *why those specific ones*, significance — researcher-headspace voice, "what would you tell the scientific community about why it mattered"). Brad's 2026-05-18 Canvas: *"a concise paragraph detailing your motivation for doing the experiment, the most important techniques you'll be using, why you're using that particular technique (not 'because I was told to' — the techniques are chosen for a reason to study a particular analyte for a given week), and what the significance of the experiment is."*
- Source: Brad emails 2026-04-14, 2026-04-18, 2026-04-26, Canvas 2026-05-18. Always check Canvas before drafting; the worksheet template often omits the writing-exercise prompt.

### CM-2. Don't restate the lab manual as methods.
Methods section = generalized technique + conditions an expert can reproduce. Do not enumerate every pipette, flask, Logger Pro click, button push. Brad verbatim 2026-04-18: *"A methods section is not an opportunity for you to restate the lab manual step by step."*

### CM-3. Plots in real graphing software, not LoggerPro screenshots.
Excel, Google Sheets, matplotlib — anything that produces a labeled, captioned figure. LoggerPro screenshots lose points starting Week 3. Brad 2026-04-14 + 2026-04-18.

### CM-4. Figure captions in a separate paragraph, never built into the figure.
Brad verbatim 2026-04-18: *"You will lose credit if your figure has a title built into it - delete it and put it in a figure caption!"*

### CM-5. Excel calculations need at least one written explanation per calc type.
Showing cells/formulas alone is not enough. Brad 2026-04-14.

### CM-6. Regrade-request channel: email TA directly.
Gradescope regrade button is disabled. Only contact for actual grader errors, not ambiguous small deductions (lowest worksheet is dropped). Brad 2026-04-18.

---

## Confirmed pitfalls (lost or would-have-lost points in graded work)

### CP-1. Sig figs on `x ± u` (Worksheet 1, −4 pts; confirmed universal by Brad)
- Wrote `4.988 ± 0.030 mL`, should be `4.99 ± 0.03 mL`.
- Wrote `19.919 ± 0.285 mL`, should be `19.9 ± 0.3 mL`.
- Grader comment: *"Avg volume sig figs stop at the same digit as CI. CI sig figs stop at the first non-zero digit."*
- See checklist item #1.

### CP-2. Sig figs on standalone % error / absolute error (Worksheet 1, −4 pts)
- Wrote `0.24%`, should be `0.2%`.
- Wrote `0.068 mL`, should be `0.07 mL`.
- See checklist item #2.

### CP-3. Sig figs on averages — decimal places, not total sig figs (Worksheet 1, −2 pts)
- Wrote `19.987 mL` from data with 0.01 precision; should be `19.99 mL`.
- See checklist item #3.

### CP-4. Placeholder text left in submitted answer (Worksheet 2 Q7, −2 pts)
- Wrote `Unknown ID number: [Forgot to record]`. Grader comment: *"Missing ID number."*
- See checklist item #7.

### CP-5. % error reported with sign (Worksheet 2 Q7, −2 pts)
- Wrote `% error = (411 − 417.77)/417.77 × 100% = −2%`. Grader comment: *"Percent error should be positive."*
- See checklist item #4.

### CP-6. Verbose figure caption (Worksheet 2 Q3, grader note, no deduction yet)
- Caption was 3 sentences with mechanism commentary. Grader: *"Caption should be concise. No titles allowed."* This is now strictly enforced post-2026-04-18.

### CP-7. Abstract missed naming signature reagent by analytical role (Worksheet 2 Q1, grader note)
- Abstract opened *"This experiment applied visible absorption spectroscopy with ferrozine..."*. Grader still flagged: *"Mentions most chemicals but missing ferrozine."* Lesson: name the reagent **and** restate its analytical role in the major-outcomes sentence (e.g., "Quantitation of Fe(II) via ferrozine absorbance at 562 nm yielded...").

---

## Pitfalls anticipated and successfully avoided

These were identified during drafting and caught before submission. Worksheet 4 graded at 100/100 confirms most of them are real (would have cost points). Keep applying.

### AP-1. Restating the lab manual as methods (Lab 3+) → fixed pre-submission Lab 3 v2.
### AP-2. Over-answering — adding mechanism/context the question never asked for → IL-1 (iron law).
### AP-3. AI-voice prose in worksheet answers → IL-1 + checklist #12.
### AP-4. Doubled title from pandoc YAML `title:` + Markdown `# H1` → keep only one. Caught Lab 3 v2.
### AP-5. Plain-text unicode math → IL-3 (iron law).
### AP-6. Display precision mismatch on near-equal % error → IL-4 (iron law).
### AP-7. Rounding `0.0248 → 0.03` instead of `0.02` → checklist #2. Caught Lab 4 self-review + teammate review.
### AP-8. Internal consistency: table value swap → checklist #9. Caught in teammate's Lab 4 (row swap V_eq ↔ pH_eq, Trial 3).
### AP-9. Variable label correctness (pKa vs pH_eq) → checklist #8. Caught in teammate's Lab 4.
### AP-10. Phosphate H-count typo (Na₂H₂PO₄) → checklist #19. Caught in teammate's Lab 4.
### AP-11. Outlier exclusion on physical grounds (not Q-test alone) → checklist #18. Applied Lab 4 Q2 (Alicia/Kalia exclusion).
### AP-12. Class-pending data disclosure → checklist #17. Applied Lab 4 Q2; Lab 4 graded full = the disclosure works.
### AP-13. Logger Pro V_eq method consistency → checklist #16. Applied Lab 4 + Lab 5.
### AP-14. Results section vs answer-body number drift → checklist #9.
### AP-15. Plot annotation collision with legend → checklist #14. Caught Lab 4 self-review.
### AP-16. Pandoc table column auto-width letter-wrapping → checklist #15. Caught Lab 4 v1.
### AP-17. Cited intermediate stats not from script → IL-5.

---

## Strengths (consistently earn credit)

### S-1. Table & data presentation
Numbered captions above tables, clean formatting, units in column headers. **Confirmed in**: Worksheet 1 Q1, Q5 full credit.

### S-2. Sample calculations
Labeled intermediate steps with units throughout, proper equations. **Confirmed in**: Worksheet 1 Q2, Q6 full credit.

### S-3. Statistical methods (calculation side)
`stdev.s` correctly chosen over population; correct t-values for given n; pooled std dev + t_calc for two-mean comparison; clear "falls within 95% CI" framing. **Confirmed in**: Worksheet 1 Q3, Q8, Q11.

### S-4. Outlier handling with evidence-based justification
Show both fits in figure (excluded point as open/red marker); quote residual ratio + R² improvement + suspected cause in caption and body. **Confirmed in**: Lab 3 SA-3 exclusion (R² 0.94 → 0.99); applied again Lab 4 Q2.

### S-5. Math-heavy questions
Multi-step derivations / back-dilutions / error propagation all earned full credit. Pattern: LaTeX formula → substitute values with units → report with sig figs. **Confirmed in**: Worksheet 2 Q6 (12/12), Q9 (18/18), Q13 (4/4); Worksheet 4 full credit on all calc questions.

### S-6. Plain-prose first-person voice in Methods/Discussion
"I prepared / I dropped X because…". Short-medium sentences. Plain verbs. **Confirmed in**: Lab 3 v2, Lab 4. **Concrete signal**: humanizing v2 of Lab 3 shrank page count 14 → 13.

### S-7. Tight figure captions (≤ 2 sentences)
Caption = subject + (optional) one-phrase pointer; never repeats body numbers. **Confirmed in**: Lab 3 v2 (6 captions trimmed from 3–4 sentences to 1–2), Lab 5 (3 captions).

### S-8. Discussion / Instrumentation conceptual questions
Three short paragraphs: mechanism / why needed for this lab / how it enables the specific measurement. **Confirmed in**: Worksheet 2 Q10–Q12 full credit (4/4, 6/6, 6/6); Worksheet 4 full credit on all conceptual Q's.

### S-9. Partner-group / shared-solution data disclosure
When the partner-group number isn't available at writing time, use manual target + italic prose attribution. Same pattern as class-shared data disclosure. **Confirmed in**: Lab 3 partner data, Lab 4 class data.

### S-10. LaTeX math via pandoc OMML
**Confirmed in**: Lab 2 (Q4, Q6, Q9, Q10, Q13 equations); Lab 3 v2 (after fixing v1 unicode); Lab 4; Lab 5.

### S-11. Pre-submission self-review catching real bugs
Lab 4 self-review caught: column-header letter-wrapping, label-collision in Fig 3, rounding 0.0248 → 0.03 mistake, near-equal-% error display precision (0.01% vs 0.02%). Lab 5 self-review caught: Q12 K_sp copied wrong from sigmoid analysis, Q5 display precision insufficient. **Pattern**: write → review with the specific checklist → fix → submit.

### S-12. Administrative discipline
Honesty agreement on time, no plagiarism, no incomplete. **Confirmed in**: all submitted worksheets.

---

## Workflow rules (build pipeline)

- Author worksheet as `_worksheet.md` (markdown with `$...$` LaTeX).
- Convert via `_build.py` using pypandoc with `--from=markdown+tex_math_dollars+tex_math_single_backslash --to=docx`.
- Render PDF for visual check (docx2pdf on Windows; LibreOffice fallback).
- Place plot generation in `_make_plots.py`. No `plt.title()` inside plot generation. Equivalence-point labels at low-y to avoid legend collision.
- Backup `Lab N Worksheet_FILLED.docx` → `_USER_BACKUP.docx` before any operation that could overwrite user manual edits.
- Active folder: `active/lab-N-<slug>/`. After grading: copy headline info into `history/<date>_worksheet-N-<slug>.md` and delete the active folder.

---

## Open questions

*None currently — the "1 sig fig for errors universal?" question was resolved by Brad 2026-04-14. The Lab 3 mass% / % error literature-source question was waived by TA.*

### Watch list (not yet seen in production)
- Whether the partner-group disclosure pattern (S-9) survives a TA's grading without deduction — Lab 3 was the test case; awaiting graded result.
- Whether Lab 5's single-trial-with-disclosure approach (lacking class data) survives Brad's grading — the Lab 4 Q2 precedent suggests yes (Lab 4 = 100), but Lab 5 has 7 questions in this state vs. Lab 4's one.
