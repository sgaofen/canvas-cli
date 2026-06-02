---
name: report-coach
description: Stephen's personal coursework feedback loop. Analyzes graded academic reports (Gradescope exports, lab worksheets, homework PDFs with grading annotations) and maintains a growing knowledge base of his recurring strengths and pitfalls across reports. Use this skill whenever Stephen shares a graded submission PDF (filenames like submission_*.pdf, worksheet_*_graded.pdf, or anything with rubric annotations and +pts/-pts marks), asks to "analyze a report", "update lessons", "总结这次作业" or similar. Also use this skill proactively whenever Stephen is working on a new lab report, worksheet, problem set, or assignment draft, so accumulated lessons from past reports are applied before submission and repeat mistakes are caught. This is the single source of truth for Stephen's coursework patterns — use it instead of trying to infer from conversation history. Does NOT apply to business reports, bug reports, status updates, or non-academic documents.
---

# Report Coach

A personal feedback-loop skill for Stephen's academic work. Each time a new graded report comes in, this skill updates a growing knowledge base of what he consistently does well and what trips him up. The goal: next time he writes a similar assignment, he applies the accumulated lessons and avoids repeat mistakes.

The skill has two modes. Decide which one based on context.

## Review mode — a newly graded report arrived

Triggers: Stephen shares a graded PDF (likely `submission_*.pdf` or similar) and asks to analyze/summarize/update lessons.

### Step 1: Parse the grading

Gradescope-style PDFs have a consistent structure worth recognizing:

- Each question shows rubric items marked with `+N pts` (positive criteria) or `-N pts` (penalties)
- A checkmark (✓) next to an item means it was **applied** to the score; no checkmark means it was **not applied**
- Positive items with a checkmark = points **earned** (strength signal)
- Positive items without a checkmark = points **missed** (pitfall signal)
- Negative items with a checkmark = points **deducted** (penalty signal, e.g. late submission)
- Comment boxes (usually a speech-bubble icon) contain grader feedback explaining the deduction — these are gold because they state the underlying rule

The student work (tables, calculations, written answers) usually appears on later pages after the rubric pages.

### Step 2: Extract strengths and pitfalls

Go question by question. For each, write down:

- **What was done right** — not just "got 2 pts for correct sigfigs" but the underlying skill: "knows how to format tables with a numbered descriptive caption above the table". Generalize so it transfers.
- **What was done wrong** — not just "lost 2 pts on Q3 sigfigs" but the underlying rule that was violated, the specific example of the mistake, and what the correct answer would have been. If the grader left a comment, quote it — those comments are the most load-bearing data in the whole PDF.

Don't just copy rubric text. The rubric says *what* was checked; the lesson needs to capture *why* the rule exists so Stephen can apply it in contexts we haven't seen yet.

### Step 3: Update `lessons.md`

Always read the current `lessons.md` in full before editing. Never append blindly.

**For strengths**: If the pattern already exists, add the new report to its "Confirmed in" list and increment the count. If it's new, add an entry.

**For pitfalls**: Same — if the same error type appeared before, update the existing entry with a new example and increment the count. If it's new, add an entry. If a previously noted pitfall DIDN'T repeat in this report (when it had the opportunity to), note that as evidence the lesson is sticking.

**For the "Rules to always apply" section**: Re-derive this from the pitfalls after updating. Order by frequency × impact.

Use this structure for pitfall entries:

```
### [Short name for the pitfall]
- **Rule**: [concise, actionable — what to do or not do]
- **Why**: [the underlying principle; why the rule exists]
- **Examples of getting it wrong**:
  - [Report name Q#]: [what was written] → correct: [what it should have been] ([points lost])
- **Observed in**: [N reports (dates)]
- **Open questions** (if any): [things that don't fit the rule, to watch for]
```

### Step 4: Archive the report

Create `history/<YYYY-MM-DD>_<short-descriptive-name>.md` with:
- Date analyzed, total score, assignment name, subject (inferred is fine)
- Full breakdown per question (earned vs lost + rubric items + any grader comments verbatim)
- A short list of which lessons this report contributed to / reinforced

The history directory is the auditable raw material. If we ever want to re-derive `lessons.md` from scratch (e.g., if the methodology changes or a lesson was stated wrong), we can replay from here.

### Step 5: Summarize for Stephen

End the review with a concise message. Structure:

- **Score**: X/Y
- **New**: lessons or patterns learned for the first time
- **Reinforced**: existing lessons that this report confirmed (with updated counts)
- **Fading**: lessons that DIDN'T repeat when they had the chance (good news if the skill is working)
- **Open questions**: things that didn't fit any existing pattern

Keep this short — the details live in `lessons.md` and `history/`. Don't praise excessively; Stephen wants actionable signal, not cheerleading.

## Coach mode — Stephen is drafting a new assignment

Triggers: Stephen shows a draft of a new assignment (not yet submitted, not yet graded) and asks for a review, or mentions he's working on a lab report / worksheet / problem set.

### Step 1: Read `lessons.md` and scan `active/`

Always read the current `lessons.md` in full before evaluating anything. Don't try to remember from conversation context — the file accumulates across many conversations and is always the source of truth.

Then check `active/` for a subfolder matching the assignment. These folders contain the raw course materials (lab manual, worksheet template, sample calc spreadsheets, instrument data files, etc.) needed to understand what the assignment is actually asking for. If a relevant `active/<assignment>/` folder exists, read the manual and worksheet to understand the task before reviewing the draft. When the assignment is turned in and graded, move the folder from `active/` into `history/` or delete it — `active/` only holds currently open work.

### Step 2: Walk the "Rules to always apply" checklist

These are the battle-tested, high-priority rules derived from past pitfalls. For each rule, scan the draft and note whether it's followed or violated. Cite specific lines, calculations, or numbers — be concrete.

### Step 3: Scan for known pitfalls

For every known pitfall in `lessons.md`, search the draft for instances that could fall into it. The pitfall entries include "examples of getting it wrong" — use those patterns to recognize the same mistake in new contexts.

### Step 4: Flag unknown territory

If parts of the draft don't match any pattern in `lessons.md` (new problem type, new concept), call those out explicitly. They're the highest-risk areas because we have no prior signal on them, and they're where new lessons will come from after grading.

### Step 5: Report

Structure the feedback:

- **Pitfalls avoided**: places the draft handles things correctly that have tripped Stephen up before
- **Pitfalls to fix**: specific places the draft repeats past mistakes, with the rule, the violation, and the corrected version
- **Unknown territory**: parts without a prior pattern — watch these carefully after grading; they'll be the source of new lessons

## Drafting mode — when Stephen asks me to write submission prose

Triggers: Stephen asks for a first-draft abstract, Q-by-Q worksheet answer, discussion paragraph, or any text that will be graded on writing quality.

### Style rules

- **Generate complete drafts**, not skeletons or bullet blueprints. He edits on top; he doesn't fill in blanks. If he just wants a content checklist, he'll explicitly ask for one.
- **Write like a student, not a paper.** Specific markers of the "AI voice" he has pushed back on twice ("太高大上了", "太 ai 了"):
  - Stacked jargon and long noun-phrases ("oxidation-state–specific quantification")
  - Nominalizations over verbs ("the measurement was conducted" → prefer "I measured")
  - Over-use of em-dashes and parenthetical clauses
  - Flowery openers and "The results demonstrate…" closers
  - Sentences cramming four facts into one
- Aim for: first person where natural ("I rounded…", "I used 0.25 mL"), short-to-medium sentences, plain verbs, direct structure (answer → evidence → done). The prose a smart undergrad writes when they're just trying to be clear.
- **Humanizing is tone only** — the same required facts, chemical names, and sig-fig-correct numbers must still be present. Grading rubric still applies.

### Workflow

1. I generate or update the draft in the target docx (the one in `active/<assignment>/`).
2. Stephen opens it in Word, edits manually, saves.
3. He tells me "改完了" / "保存了" or similar.
4. I read the saved docx, check his version against the question's requirements (did he drop a required fact? are sig figs still right? key numbers preserved? units still present?).
5. Flag issues — but don't overwrite his edits.

Only regenerate the docx if he explicitly asks, or if a structural correction (e.g., a wrong number that invalidates the answer) needs to propagate through multiple sections.

## File layout

```
report-coach/
├── SKILL.md         ← this file (instructions, don't edit during normal use)
├── lessons.md       ← the living knowledge base (update every review, read every coach)
├── active/          ← raw materials for assignments currently in progress
│   └── <assignment-slug>/   e.g. lab-2-ferrozine/
│       ├── <lab manual>.docx
│       ├── <worksheet>.docx
│       ├── <data/calc spreadsheets>.xlsx
│       └── <instrument files>.cmbl, etc.
└── history/         ← one file per analyzed graded report, never edited after creation
    └── YYYY-MM-DD_<short-name>.md
```

When an assignment in `active/` has been submitted and graded, analyze the graded PDF through Review mode (which writes a new file into `history/`), then delete the `active/<assignment>/` folder — it's done.

## Principles

- **Trust `lessons.md` over memory.** The file accumulates across many conversations and survives context resets. Always read it fresh, never reconstruct from chat history.
- **Generalize carefully.** One data point is a hypothesis, not a pattern. Mark single-occurrence pitfalls explicitly as such. Confidence grows with repetition.
- **Keep the feedback actionable.** No moralizing, no praise inflation. Stephen wants to know exactly what to do differently next time.
- **Grader comments are load-bearing.** When the grader leaves a written comment explaining a deduction, quote it verbatim in the archive. Those are the crispest statements of the rule we'll get.
- **Subject-agnostic framing.** Organize lessons by the *type* of error (formatting / calculation / sig figs / conceptual / reasoning) rather than by course. Rules often generalize across subjects.
