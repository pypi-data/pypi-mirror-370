# Arrow table dict conversion

A Python package for converting dictionaries to Apache Arrow tables, and vice versa.

## Installation

```bash
pip install arrow-table-dict-conversion
```

## Usage

From dict to table:

```python
from arrow_table_dict_conversion import dict_to_pa_table

data = {
    "col1": [1, 2, 3],
    "col2": ["a", "b", "c"]
}

table = dict_to_pa_table(data)
print(table)
```

From table to dict:

```python
from arrow_table_dict_conversion import unpack_pa_table_dict

# Create an example Arrow table
data = {
    "col1": [1, 2, 3],
    "col2": ["a", "b", "c"]
}
table = pa.table(data)
# Convert Arrow table back to dict
result_dict = unpack_pa_table_dict(table)
print(result_dict)
```

## Requirements

- Python 3.7+
- pyarrow
