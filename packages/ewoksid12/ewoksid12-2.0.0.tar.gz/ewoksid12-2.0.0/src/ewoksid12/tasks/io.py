from typing import Dict, Sequence, Union
import numpy


def save_as_ascii(filename: str, data_dict: Dict[str, Sequence[Union[float, int]]]):
    dtype = [(key, type(values[0])) for key, values in data_dict.items()]
    data = list(zip(*data_dict.values()))
    structured_data = numpy.array(data, dtype=dtype)
    header = "  ".join(data_dict.keys())
    numpy.savetxt(
        filename, structured_data, fmt="%s", delimiter=" ", header=header, comments=""
    )
