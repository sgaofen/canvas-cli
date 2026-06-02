"""Build the worksheet docx from _worksheet.md via pandoc, then render PDF."""
import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import pypandoc

src = '_worksheet.md'
out_docx = 'Lab 6 Worksheet_FILLED.docx'

pypandoc.convert_file(
    src,
    'docx',
    outputfile=out_docx,
    extra_args=[
        '--from=markdown+tex_math_dollars+tex_math_single_backslash',
    ],
)
print(f'Wrote {out_docx}')

# Render PDF for visual check
try:
    from docx2pdf import convert
    convert(out_docx, 'Lab 6 Worksheet_FILLED.pdf')
    print('Wrote Lab 6 Worksheet_FILLED.pdf')
except Exception as e:
    print(f'docx2pdf failed: {e}')
    # Try LibreOffice fallback
    import subprocess
    try:
        subprocess.run(['soffice', '--headless', '--convert-to', 'pdf', out_docx], check=True)
        print('Wrote PDF via LibreOffice')
    except Exception as e2:
        print(f'LibreOffice fallback failed: {e2}')
