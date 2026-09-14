from numbers_parser import Document

doc = Document("../ChartOfAccount.numbers")
sheets = doc.sheets
for sheet in sheets:
    tables = sheet.tables
    for table in tables:
        print(f"Sheet: {sheet.name}, Table: {table.name}")
        for i, row in enumerate(table.rows()):
            print([cell.value for cell in row])
            if i > 20:  # Print first 20 rows
                break
