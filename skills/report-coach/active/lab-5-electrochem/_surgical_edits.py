"""Surgical edits to Lab 5 Worksheet_FILLED.docx (IL-2: no rebuild after user edits).
Applies:
  - Q1: delete trailing sentence "The line of best fit is itself the experimental Nernst equation."
  - Q9: delete the post-boxed explanation paragraph (~370x offset)
  - Q10: simplify Fig 3 caption (cross-reference Fig 2)
  - Discussion + Instrumentation: prepend Q15 / Q16 / Q17 / Q18 to the italic question text.
"""
import sys, shutil, os
sys.stdout.reconfigure(encoding='utf-8')
from docx import Document

DOCX = r"D:\Desktop\m3lc\week 5\Lab 5 Worksheet_FILLED.docx"
SHADOW = r"C:\Users\YY\.claude\skills\report-coach\active\lab-5-electrochem\Lab 5 Worksheet_FILLED.docx"

def delete_paragraph(paragraph):
    p = paragraph._element
    p.getparent().remove(p)
    paragraph._p = paragraph._element = None

def edit(path):
    d = Document(path)
    actions = []

    for i, p in enumerate(list(d.paragraphs)):
        t = p.text

        # --- Q1: trim "The line of best fit is itself the experimental Nernst equation." ---
        # The full paragraph text in P011 is roughly: "so slope ↔ ... and intercept ↔ ...
        # E°(Ag+/Ag) − 0.307. The line of best fit is itself the experimental Nernst equation."
        # The trailing English sentence after the OMML "− 0.307" is in a plain text run.
        if "The line of best fit is itself the experimental Nernst equation" in t:
            for r in p.runs:
                if "The line of best fit is itself" in r.text:
                    r.text = r.text.replace(
                        " The line of best fit is itself the experimental Nernst equation.",
                        "").replace(
                        "The line of best fit is itself the experimental Nernst equation.",
                        "")
                    actions.append(f"P{i}: Q1 trailing sentence removed")

        # --- Q9: delete the entire paragraph about junction potential offset ---
        if (t.strip().startswith("The ") and "offset is consistent with a junction potential" in t):
            actions.append(f"P{i}: Q9 explanation paragraph deleted -- '{t[:60]}…'")
            delete_paragraph(p)
            continue

        # --- Q10: simplify Figure 3 caption ---
        if t.startswith("Figure 3.") and "Potentiometric titration of 100.0 mL of an unknown" in t:
            # python-docx loses bold prefix in single-run access, but bold of "Figure 3." should
            # already be styled. We'll rewrite the whole paragraph text.
            new_text = "Figure 3. As Fig. 2 for an unknown NaCl solution (Part C); equivalence point at (33.0 mL, 0.262 V)."
            # Find the run with the main text and replace
            for r in p.runs:
                if "Potentiometric titration of 100.0 mL of an unknown" in r.text:
                    # Need to identify: "Figure 3." is in a bold run, the rest is body.
                    # Replace body run with the simpler text.
                    r.text = " As Fig. 2 for an unknown NaCl solution (Part C); equivalence point at (33.0 mL, 0.262 V)."
                    actions.append(f"P{i}: Q10 caption simplified")
                elif "Cell potential (blue, left axis)" in r.text:
                    r.text = ""  # remove the second sentence content
                elif "Several points in the steep region" in r.text:
                    pass  # this is a separate paragraph, leave for now

        # --- Add Q15 to Discussion question ---
        if t.strip().startswith("Why does the concentration of") and "before, during, and after" in t:
            for r in p.runs:
                if r.text.startswith("Why does the concentration of"):
                    r.text = "Q15. " + r.text
                    actions.append(f"P{i}: prepended Q15 to Discussion")
                    break
                elif r.text and not r.text.startswith("Q15"):
                    # If the runs are split, prepend Q15 to whichever run starts with "Why"
                    if "Why does the concentration" in r.text:
                        r.text = r.text.replace("Why does the concentration", "Q15. Why does the concentration")
                        actions.append(f"P{i}: prepended Q15 (mid-run)")
                        break

        # --- Add Q16/Q17/Q18 to Instrumentation questions ---
        if "what happens at the cathode" in t and "What happens at the anode" in t:
            for r in p.runs:
                if r.text and "what happens at the cathode" in r.text:
                    r.text = r.text.replace("In general,", "Q16. In general,")
                    actions.append(f"P{i}: prepended Q16")
                    break
        if "purpose of a reference electrode" in t:
            for r in p.runs:
                if r.text and "purpose of a reference electrode" in r.text:
                    r.text = "Q17. " + r.text
                    actions.append(f"P{i}: prepended Q17")
                    break
        if "Cu/CuSO" in t and "reference electrode? Write the reaction" in t:
            for r in p.runs:
                if r.text and "What is happening at the" in r.text:
                    r.text = "Q18. " + r.text
                    actions.append(f"P{i}: prepended Q18")
                    break

    d.save(path)
    return actions

print(f"Editing: {DOCX}")
acts = edit(DOCX)
for a in acts:
    print("  ", a)
print(f"\nMirroring to shadow: {SHADOW}")
shutil.copy(DOCX, SHADOW)
print("Done.")
