from typing import List, Dict, Set


class State:
    def __init__(self, name, is_err=False, is_end=False, local_map: Dict[str, str] = None):
        """
        :param name: name of state
        :param local_map: dict in which keys are letters and values are state names to move automaton to
        """
        self.name = name
        self._is_err = is_err
        self._is_end = is_end
        self.local_map: Dict[str, str] = local_map if local_map and all(local_map.keys()) else dict()

    @property
    def is_error(self):
        return self._is_err

    @property
    def is_final(self):
        return self._is_end


class Map:
    def __init__(self, alphabet: Set[str], data: List[State] = None):
        self._alphabet = alphabet
        self._data = {item.name: item for item in data} if data and alphabet else dict()
        self.check_integrity()

    @property
    def alphabet(self):
        return self._alphabet

    @property
    def data(self):
        return self._data.copy()

    def extend_data(self, new_data: List[State]):
        self.data.update({item.name: item for item in new_data})
        self.check_integrity()

    def __getitem__(self, item: str):
        return self._data.get(item)

    @property
    def initial_state(self):
        return self["q0"] if self["q0"] else self[min(self._data.keys())]

    def check_integrity(self) -> None:
        end = False
        for state in self._data:
            if self._data[state].name != state:
                raise KeyError("Keys in map don't match with state names")
            if set(self._data[state].local_map.keys()) != self._alphabet:
                raise KeyError("State " + self._data[state].name + " does not match an alphabet")
            for next_state in self._data[state].local_map.values():
                if self[next_state] is None:
                    raise KeyError("Error in state " + self._data[state].name + ": state " + next_state + " not found in map")
            if self._data[state].is_final:
                end = True
        if not end:
            raise ValueError("Cannot define finite automaton without any final state")
