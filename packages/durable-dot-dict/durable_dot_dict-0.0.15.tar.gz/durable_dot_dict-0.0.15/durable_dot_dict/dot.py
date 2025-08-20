from typing import MutableMapping, Union, List


class DotList(list):
    def __getitem__(self, index):
        value = super().__getitem__(index)
        if isinstance(value, dict):
            return Dot(value)
        return value

    def flatten(self) -> List[dict]:
        return [item.flat() for item in self]

    def merge(self) -> dict:
        list = self.flatten()
        result = {}
        for item in list:
            result.update(item)
        return result


class Dot(dict):

    def __getattr__(self, item) -> Union['Dot', DotList]:
        value = self[item]
        if isinstance(value, dict):
            return Dot(value)
        elif isinstance(value, list):
            return DotList(value)
        return value