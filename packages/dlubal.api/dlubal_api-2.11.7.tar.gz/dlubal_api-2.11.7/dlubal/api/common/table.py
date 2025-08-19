import pandas

class Table:

    def __init__(self, data: pandas.DataFrame):
        self.data = data

    def __getitem__(self, key):
        if isinstance(key, str):
            return self.col(key)
        elif isinstance(key, int):
            return self.row(key)

    def col(self, key):
        column = self.data[key]
        if len(column) == 0:
            return None
        if len(column) == 1:
            return column.values[0]
        return column.values

    def row(self, idx):
        return self.data.iloc[idx]

    def values(self, *keys):
        results = [self.col(key) for key in keys]
        try:
            result_tuples = list(zip(*results))
            if len(result_tuples) == 0:
                return None
            if len(result_tuples) == 1:
                return result_tuples[0]
            else:
                return result_tuples
        except:
            return tuple(results)