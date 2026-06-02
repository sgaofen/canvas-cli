"""Build Lab 5 worksheet DOCX + PDF via pandoc (lessons #18, #14b: first build only)."""
import pypandoc, subprocess, os
HERE = os.path.dirname(os.path.abspath(__file__))
md = os.path.join(HERE, "_worksheet.md")
docx = os.path.join(HERE, "Lab 5 Worksheet_FILLED.docx")
pdf = os.path.join(HERE, "Lab 5 Worksheet_FILLED.pdf")

pypandoc.convert_file(
    md, "docx",
    outputfile=docx,
    extra_args=[
        "--from=markdown+tex_math_dollars+tex_math_single_backslash",
        "--to=docx",
        "--standalone",
    ],
)
print(f"docx: {docx}")

# PDF via Word (LibreOffice fallback if not on Win)
import platform
if platform.system() == "Windows":
    try:
        from docx2pdf import convert as docx2pdf_convert
        docx2pdf_convert(docx, pdf)
        print(f"pdf:  {pdf}")
    except Exception as e:
        print(f"PDF gen via docx2pdf failed: {e}; trying pandoc PDF instead")
        pypandoc.convert_file(md, "pdf", outputfile=pdf,
            extra_args=["--from=markdown+tex_math_dollars", "--pdf-engine=xelatex"])
