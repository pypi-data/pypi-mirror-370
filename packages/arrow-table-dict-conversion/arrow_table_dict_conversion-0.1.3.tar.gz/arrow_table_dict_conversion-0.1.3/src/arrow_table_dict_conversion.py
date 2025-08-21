"""
Utility functions to convert dictionary data to PyArrow Table format and unpack it.
"""
import pyarrow as pa

def dict_to_pa_table(data:dict) -> pa.Table:
    """A util function to convert any dictionary data to pyArrow Table data, each column with a length of 1 which contains the data.

    Args:
        data (dict): Dictionary data to be converted
    Returns:
        pa.Table: PyArrow Table object for Flight transport.
        
    """
    names = []
    pa_arrays = []
    for k, v in data.items():
        names.append(k)
        value = v
        # Convert back to basic types
        if isinstance(v, pa.RecordBatch) or isinstance(v, pa.Table):
            value = v.to_pydict()
        elif isinstance(v, pa.Array):
            value = v.to_pylist()
        elif isinstance(v, pa.Scalar):
            value = v.as_py()
        pa_arrays.append(pa.array([value]))
    result = pa.Table.from_arrays(pa_arrays, names=names)
    return result

def unpack_pa_table_dict(data:pa.Table) -> dict:
    """Unpack a PyArrow Table data to a dictionary with each column containing a single value.
    Args:
        data (pa.Table): PyArrow Table data to be unpacked
    Returns:
        dict: Dictionary with each key corresponding to a column name and value being the first element of that column.
    """
    # get data from memory
    input_params:dict = pa.Table.to_pydict(data)
    # Unpack data
    for k, v in input_params.items():
        input_params[k] = v[0]
    return input_params
