import copy
import json
from typing import Union, List, Tuple, Any, Optional, Dict, Set, Type, TypeVar
from collections.abc import MutableMapping
import dotdict_parser

T = TypeVar("T", bound='DotDict')

class DotDict(MutableMapping):
    def __init__(self, dictionary: Optional[Union[dict | list]] = None):
        if dictionary is None:
            dictionary = {}
        if not isinstance(dictionary, (dict, list)):
            raise TypeError(f"Expected dictionary or list as DotDict. Got {type(dictionary)}.")
        self._root = dictionary

    def _set_path_value(self, path, value):
        """
        Walks through `_root` (which should be a dict or list at the top level),
        creating intermediate dicts/lists as needed so that each element in `path`
        is valid. The final element of `path` will be set to `value`.
        """
        node = self._root

        for i in range(len(path) - 1):
            key = path[i]
            next_key = path[i + 1]

            if isinstance(key, str):
                # Ensure `node` is a dict if we are using a string key
                if not isinstance(node, dict):
                    raise TypeError(f"Cannot use string key on non-dict: {node}")
                # If key doesn't exist, create either a dict or list based on the next key
                if key not in node:
                    node[key] = [] if isinstance(next_key, int) else {}
                node = node[key]

            elif isinstance(key, int):
                # Ensure `node` is a list if we are using an integer key
                if not isinstance(node, list):
                    raise TypeError(f"Cannot use integer key on non-list: {node}")
                # Expand the list if needed
                while len(node) <= key:
                    node.append(None)
                # If there's nothing at node[key], create either a dict or list for the next step
                if node[key] is None:
                    node[key] = [] if isinstance(next_key, int) else {}
                node = node[key]

            else:
                raise TypeError(f"Keys must be str or int, got {type(key)}")

        # Convert DotDict to dict
        if isinstance(value, DotDict):
            value = value.to_dict()

        # Handle the last key in the path and set `value`
        last_key = path[-1]
        if isinstance(last_key, str):
            if not isinstance(node, dict):
                raise TypeError(f"Cannot assign string-key '{last_key}' to non-dict: {node}")
            node[last_key] = value
        elif isinstance(last_key, int):
            if not isinstance(node, list):
                raise TypeError(f"Cannot assign integer-key '{last_key}' to non-list: {node}")
            while len(node) <= last_key:
                node.append(None)
            node[last_key] = value
        else:
            raise TypeError(f"Keys must be str or int, got {type(last_key)}")

    def _set_reference(self, path, key):
        data = self._root
        print(path)
        for item_no, item in enumerate(path):
            print(item)
            if isinstance(item, int):
                if not isinstance(data, list):
                    data = []
                data[item] = []
            elif isinstance(item, str):
                if item not in data:
                    data[item] = {}
                data = data[item]
            else:
                raise KeyError(f"Only string keys are allowed. Got {item} of type {type(item)}.")
        return data

    def _has_reference(self, keys) -> bool:
        data = self._root
        last = len(keys) - 1
        for pos, key in enumerate(keys):

            if data is None:
                return False

            if isinstance(key, int):
                # Is int but dat is not list
                if not isinstance(data, list):
                    return False
                # Is last so check number of items
                if pos == last:
                    return len(data) > key
                else:
                    # Not last so check if key not out of range
                    if len(data) <= key:
                        return False

            elif key not in data:
                return False
            try:
                data = data[key]
            except TypeError:
                return False
        return True

    def _reference(self, keys):
        data = self._root
        for key in keys:
            data = data[key]
        return data

    @staticmethod
    def _path_key(keys):
        path = keys[:-1]
        key = keys[-1]
        return path, key

    def cast_to(self, cast_to: Type[T]) -> T:
        return cast_to(self._root)

    def get(self, key, *args):
        try:
            keys = dotdict_parser.parse_unified_path(key)
            return self._reference(keys)
        except (ValueError, KeyError) as e:
            if args:
                return args[0]
            raise KeyError(f"Could not get DotDict value for {key}. Default value: {args}. Details: {str(e)}")

    def copy(self):
        return DotDict(self._root.copy())

    def deep_copy(self):
        return DotDict(copy.deepcopy(self._root))

    def to_dict(self) -> dict:
        return self._root

    def to_json(self, default=None, cls=None):
        return json.dumps(self._root, default=default, cls=cls)

    @staticmethod
    def as_list(data: List[dict]) -> List['DotDict']:
        return list(map(DotDict, data))

    def get_or_none(self, key: str) -> Optional[Any]:
        return self.get(key, None)

    def empty(self, key) -> bool:
        result = self.get(key, None)

        if isinstance(result, (bool, int, float)):
            return False

        return result is None or not bool(result)

    def flat(self):
        return dotdict_parser.flatten(self._root)

    def map(self, right: Union['DotDict', dict]) -> 'Mapper':
        return Mapper(self, right)

    def __setattr__(self, key, value):
        if not key.startswith('_'):
            raise KeyError(f"Attribute `{key}` can not be set. DotDict can not be modified by setting attributes.")
        super().__setattr__(key, value)

    def __contains__(self, item):
        keys = dotdict_parser.parse_unified_path(item)
        return self._has_reference(keys)

    def __getitem__(self, item):
        if isinstance(item, int):
            return self._root[item]
        return self.get(item)

    def __setitem__(self, key, value):
        keys = dotdict_parser.parse_unified_path(key)
        self._set_path_value(keys, value)

    def __delitem__(self, key):
        if isinstance(key, int):
            del self._root[key]
        else:
            keys = dotdict_parser.parse_unified_path(key)
            path, key = self._path_key(keys)
            data = self._reference(path)
            del data[key]

    def __repr__(self):
        return f'{self.__class__}({self._root})'

    def __str__(self):
        return self._root.__str__()

    def __hash__(self):
        return self._root.__hash__()

    def __len__(self):
        return self._root.__len__()

    def __getstate__(self):
        return self._root

    def __setstate__(self, state):
        self._root = state

    def __iter__(self):
        # Return an iterator over the keys
        return self._root.__iter__()

    def __eq__(self, other):
        if isinstance(other, DotDict):
            return other.to_dict() == self.to_dict()
        elif isinstance(other, dict):
            return other == self.to_dict()
        else:
            return False

    def __lshift__(self, list_of_kv: Union[List[Tuple[str, str]], Dict[str,str]]) -> 'DotDict':
        list_of_kv = list_of_kv.items() if isinstance(list_of_kv, dict) else list_of_kv

        for key, value in list_of_kv:
            self[key] = value

        return self

    def __rshift__(self, list_of_kv: Union[List[Tuple[str, str]], Dict[str,str]]) -> 'DotDict':
        list_of_kv = list_of_kv.items() if isinstance(list_of_kv, dict) else list_of_kv

        dot = DotDict()
        for key, value in list_of_kv:
            if value not in self:
                continue
            dot[key] = self[value]
        return dot

    def __or__(self, property):
        return self.get_or_none(property)

def _data_convert(list_of_left_right):
    if isinstance(list_of_left_right, set):
        return [(item, item) for item in list_of_left_right]
    return list_of_left_right.items() if isinstance(list_of_left_right, dict) else list_of_left_right


class Mapper:

    def __init__(self, left: DotDict, right: Union[DotDict, dict]):
        self.left = left
        self.right: DotDict = DotDict(right) if isinstance(right, dict) else right

    def __lshift__(self, list_of_left_right: Union[List[Tuple[str, str]], Dict[str, str], Set[str]]) -> 'DotDict':
        list_of_left_right = _data_convert(list_of_left_right)
        for left, right in list_of_left_right:
            if right in self.right:
                self.left[left] = self.right[right]

        return self.left

    def __rshift__(self, list_of_left_right: Union[List[Tuple[str, str]], Dict[str, str], Set[str]]) -> 'DotDict':
        list_of_left_right = _data_convert(list_of_left_right)
        for left, right in list_of_left_right:
            if left in self.left:
                self.right[right] = self.left[left]
        return self.right
