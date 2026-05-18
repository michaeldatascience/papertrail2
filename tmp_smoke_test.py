import fitz
from pathlib import Path

out = Path('smoke_test.pdf')
doc = fitz.open()
page = doc.new_page(width=595, height=842)
text = '''Invoice
Invoice Number: INV-1001
Date: 2026-05-18
Customer: Jane Doe
Total: $123.45
'''
page.insert_text((72, 72), text, fontsize=14)
doc.save(out)
print(out)
