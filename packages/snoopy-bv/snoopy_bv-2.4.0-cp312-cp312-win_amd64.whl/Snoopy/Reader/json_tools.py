import json
import numpy as np

class NumpyEncoder(json.JSONEncoder):
    """Encoder so that numpy arrays can directly be written in JSON

    Example
    -------
    >>> a = {"table" : np.array([[1, 2, 3], [4, 5, 6.]])}
    >>> json_dump = json.dumps(a, cls=NumpyEncoder)
    {"table": [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]]}

    Note
    ----
    From https://stackoverflow.com/questions/26646362/numpy-array-is-not-json-serializable

    """

    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)



if __name__ == "__main__":

    a = {"table" : np.array([[1, 2, 3], [4, 5, 6.]])}
    print (a)

    json_dump = json.dumps(a, cls=NumpyEncoder)
    print(json_dump)
    b = json.loads( json_dump )
    print (b)
