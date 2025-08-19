# TableX

TableX is a simple and powerful Python library to seamlessly convert
between **CSV**, **Excel**, and **JSON** formats.\
It also provides utilities like **pretty-printing JSON**,
**flattening/unflattening JSON**, and more.

------------------------------------------------------------------------

## Features

-   📑 Convert between **CSV ↔ JSON ↔ Excel**
-   🎯 Easy-to-use, minimal code required
-   ⚡ Lightweight & fast
-   🛠️ Utility functions for JSON pretty printing and flattening

------------------------------------------------------------------------

## Installation

``` bash
pip install tablex
```

------------------------------------------------------------------------

## Example Usage

``` python
from tablex import TableX

# ---------------- CSV <-> JSON ----------------

# Convert CSV → JSON
records = TableX.csv_to_json(
    csv_file="students.csv",
    json_file="students.json",
    pretty=True,
    indent=2
)

# Convert JSON → CSV
TableX.json_to_csv(
    json_file="students.json",
    csv_file="students_converted.csv"
)


# ---------------- Excel <-> JSON ----------------

# Convert Excel → JSON
records = TableX.excel_to_json(
    excel_file="results.xlsx",
    json_file="results.json",
    sheet_name="result sheet",
    pretty=True,
    indent=4
)

# Convert JSON → Excel
TableX.json_to_excel(
    json_file="results.json",
    excel_file="results_converted.xlsx"
)


# ---------------- CSV <-> Excel ----------------

# Convert CSV → Excel
TableX.csv_to_excel(
    csv_file="students.csv",
    excel_file="students.xlsx"
)

# Convert Excel → CSV
TableX.excel_to_csv(
    excel_file="results.xlsx",
    csv_file="results_converted.csv",
    sheet_name="result sheet"
)


# ---------------- Utility functions ----------------

# Pretty-print JSON file to console
TableX.pretty_print_json("students.json")

# Flatten JSON into a single dictionary (dot notation)
flat = TableX.flatten_json("students.json")
print(flat)
# Example: {"user.name": "Alice", "user.age": 25, "user.skills.0": "Python"}

# Unflatten dictionary back into JSON
unflat = TableX.unflatten_json(flat)
print(unflat)
# Example: {"user": {"name": "Alice", "age": 25, "skills": ["Python"]}}
```

------------------------------------------------------------------------

## License

MIT License © 2025
