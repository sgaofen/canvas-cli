"""Fix the Fig 3 caption — the earlier edit left OMML math and stray " is circled." trailing text.
Rebuild the paragraph cleanly by deleting all runs after the bold "Figure 3." and replacing the body run.
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from docx import Document
from copy import deepcopy
from lxml import etree

DOCX = r"D:\Desktop\m3lc\week 5\Lab 5 Worksheet_FILLED.docx"

d = Document(DOCX)

W_NS = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M_NS = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
def qn(prefix, tag):
    if prefix == 'w':
        return f'{{{W_NS}}}{tag}'
    if prefix == 'm':
        return f'{{{M_NS}}}{tag}'

for i, p in enumerate(d.paragraphs):
    if not p.text.startswith("Figure 3."):
        continue
    if "As Fig. 2" not in p.text:
        continue
    print(f"Found Fig 3 caption at P{i}: {p.text!r}")
    pel = p._element

    # Strategy: keep only the first two w:r children (assuming first is bold "Figure 3." and second is body).
    # Delete all other w:r, m:oMath, m:oMathPara, and any other children.
    children = list(pel)
    keep = []
    drop = []
    bold_run_seen = False
    for c in children:
        tag = etree.QName(c).localname
        if tag == 'r':
            # Check if this run contains "Figure 3."
            text_elems = c.findall(qn('w', 't'))
            run_text = ''.join(t.text or '' for t in text_elems)
            if "Figure 3." in run_text and not bold_run_seen:
                keep.append(c)
                bold_run_seen = True
            else:
                drop.append(c)
        elif tag in ('oMath', 'oMathPara'):
            drop.append(c)
        elif tag == 'pPr':
            keep.append(c)  # paragraph properties
        else:
            # bookmarks, hyperlinks, etc. — drop to be safe
            drop.append(c)

    print(f"  Keeping: {[etree.QName(c).localname for c in keep]}")
    print(f"  Dropping: {[etree.QName(c).localname for c in drop]}")

    # Remove drops
    for c in drop:
        pel.remove(c)

    # Now construct a new w:r with the simplified body text, matching the bold run's formatting style minus bold
    # Easier: use the existing bold run as a template, clone it, strip bold, replace text.
    bold_run = None
    for c in pel:
        if etree.QName(c).localname == 'r':
            bold_run = c
            break

    if bold_run is None:
        print("  ERROR: no bold run remaining; cannot construct caption body.")
        continue

    body_run = deepcopy(bold_run)
    # Strip bold from rPr if present
    rPr = body_run.find(qn('w', 'rPr'))
    if rPr is not None:
        b = rPr.find(qn('w', 'b'))
        if b is not None:
            rPr.remove(b)
        bcs = rPr.find(qn('w', 'bCs'))
        if bcs is not None:
            rPr.remove(bcs)
    # Replace the text in body_run
    for t in body_run.findall(qn('w', 't')):
        body_run.remove(t)
    new_t = etree.SubElement(body_run, qn('w', 't'))
    new_t.text = " As Fig. 2 for an unknown NaCl solution (Part C); equivalence point at (33.0 mL, 0.262 V)."
    new_t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')

    # Append body run after the bold run
    bold_run.addnext(body_run)

    print(f"  Done. New text: {p.text!r}")
    break

d.save(DOCX)
print(f"\nSaved: {DOCX}")
