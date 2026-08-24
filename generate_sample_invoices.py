from pathlib import Path
import fitz

OUT = Path(__file__).parent / "sample_invoices"
OUT.mkdir(exist_ok=True)

INVOICES = {
    "alpha_materials.pdf": [
        "INVOICE",
        "Supplier: Riverside Concrete Supply Ltd",
        "Invoice Number: RCS-2026-104",
        "Invoice Date: 2026-08-10",
        "Description: Concrete and rebar materials for Project Alpha Riverside site",
        "Subtotal: EUR 10000.00",
        "VAT: EUR 1800.00",
        "Total: EUR 11800.00",
    ],
    "beta_equipment.pdf": [
        "INVOICE",
        "Supplier: Central Equipment Rental Ltd",
        "Invoice Number: CER-2026-208",
        "Invoice Date: 2026-08-12",
        "Description: Crane and equipment rental for Project Beta Central district",
        "Subtotal: EUR 6000.00",
        "VAT: EUR 1080.00",
        "Total: EUR 7080.00",
    ],
    "ambiguous_transport.pdf": [
        "INVOICE",
        "Supplier: Metro Logistics Services",
        "Invoice Number: MLS-2026-331",
        "Invoice Date: 2026-08-15",
        "Description: Freight and truck delivery for construction materials",
        "Subtotal: EUR 2500.00",
        "VAT: EUR 450.00",
        "Total: EUR 2950.00",
    ],
}

for filename, lines in INVOICES.items():
    doc = fitz.open()
    page = doc.new_page(width=595, height=842)
    y = 90
    for i, line in enumerate(lines):
        size = 20 if i == 0 else 12
        page.insert_text((72, y), line, fontsize=size)
        y += 42 if i == 0 else 28
    doc.save(OUT / filename)
    doc.close()
    print(f"Created {OUT / filename}")
