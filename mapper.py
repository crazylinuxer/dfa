from typing import List, Dict, Set, FrozenSet, Tuple


class State:
    def __init__(self, name, is_end=False, local_map: Dict[str, str] = None):
        """
        :param name: name of state
        :param local_map: dict in which keys are letters and values are state names to move automaton to
        """
        self.name = name
        self._is_end = is_end
        self._local_map: Dict[str, str] = local_map if local_map and all(local_map.keys()) else dict()

    @property
    def is_final(self):
        return self._is_end

    def add_jump(self, letter: str, state: str):
        if self._local_map.get(letter):
            raise RuntimeError("Letter '" + letter + "' already exists in " + self.name + " local map")
        self._local_map[letter] = state

    def get_transitions(self) -> Dict[str, str]:
        return self._local_map.copy()

    def next_state(self, letter: str) -> str:
        return self._local_map[letter]

    def is_present(self, letter: str) -> bool:
        return bool(self._local_map.get(letter))

    @property
    def used_alphabet(self) -> set:
        return set(self._local_map.keys())


class Map:
    def __init__(self, alphabet: Set[str], data: List[State] = None):
        self._alphabet = alphabet
        self._data: Dict[str, State] = {item.name: item for item in data} if data and alphabet else dict()
        self.check_integrity()

    def __getitem__(self, item: str) -> State:
        return self._data.get(item)

    @property
    def alphabet(self):
        return self._alphabet

    @property
    def data(self):
        return self._data.copy()

    def extend_data(self, new_data: List[State]):
        self.data.update({item.name: item for item in new_data})
        self.check_integrity()

    @property
    def initial_state(self) -> State:
        return self[min(self._data.keys())]

    def check_integrity(self) -> None:
        end = False
        for state in self._data:
            if self._data[state].name != state:
                raise KeyError("Keys in map don't match with state names")
            if self._data[state].used_alphabet != self._alphabet:
                raise KeyError("State " + self._data[state].name + " does not match an alphabet")
            for letter in self._alphabet:
                if self[self._data[state].next_state(letter)] is None:
                    raise KeyError("Error in state " + self._data[state].name + ": state " +
                                   self._data[state].next_state(letter) + " not found in the map")
            if self._data[state].is_final:
                end = True
        if not end:
            raise RuntimeError("Cannot define DFA without any final state")

    def _get_pairs_table(self, previous: Dict[str, Dict[str, bool]] = None) -> Dict[str, Dict[str, bool]]:
        if previous:
            changed = False
            for i in previous:
                for j in previous[i]:
                    if previous[i][j]:
                        continue
                    for letter in self.alphabet:
                        first = self[i].next_state(letter)
                        second = self[j].next_state(letter)
                        if first == second:
                            continue
                        try:
                            tmp = previous[first][second]
                        except KeyError:
                            tmp = previous[second][first]
                        if tmp:
                            changed = True
                            previous[i][j] = True
                            break
            if changed:
                return self._get_pairs_table(previous)
            return previous
        else:
            result = dict()
            states = list(self._data.keys())
            states.sort()
            for i in range(len(states)):
                result[states[i]] = dict((states[j], False) for j in range(i))
            del result[states[0]]
            for i in result:
                for j in result[i]:
                    result[i][j] = self[i].is_final ^ self[j].is_final
            return self._get_pairs_table(result)

    def _get_states_to_combine(self) -> List[Tuple]:
        raw_result: List[FrozenSet] = list()
        table = self._get_pairs_table()
        for i in table:
            for j in table[i]:
                if not table[i][j]:
                    raw_result.append(frozenset({i, j}))
        result: List[FrozenSet] = list()
        for pair in raw_result:
            added_to_existing = False
            for j in range(len(result)):
                if result[j].intersection(pair):
                    result[j] = result[j].union(pair)
                    added_to_existing = True
                    break
            if not added_to_existing:
                result.append(pair)
        return [tuple(data) for data in set(result)]

    def _replace_states(self, states_to_replace: Tuple[str], new_name: str) -> None:
        new_is_final = None
        transitions = dict()
        for state in states_to_replace:
            if new_is_final is None:
                new_is_final = self[state].is_final
            elif new_is_final != self[state].is_final:
                raise ValueError("Cannot replace final and non-final states at once")
            if not transitions:
                transitions = self[state].get_transitions()
                for letter in self.alphabet:
                    if self[state].next_state(letter) in states_to_replace:
                        transitions[letter] = new_name
        '''
            else:
                tmp_transitions = dict()
                for letter in self.alphabet:
                    next_state = self[state].next_state(letter)
                    if next_state in states_to_replace:
                        next_state = new_name
                    tmp_transitions[letter] = next_state
                if tmp_transitions != transitions:
                    raise ValueError("Cannot combine states with different transitions")
        '''  # this commented code checks some shit but idk if it works properly or not and is it needed
        for state_to_delete in states_to_replace:
            del self._data[state_to_delete]
        for state_to_replace in self._data:
            new_transitions = self._data[state_to_replace].get_transitions()
            is_end = self._data[state_to_replace].is_final
            for letter in new_transitions:
                if new_transitions[letter] in states_to_replace:
                    new_transitions[letter] = new_name
            self._data[state_to_replace] = State(state_to_replace, is_end, new_transitions)
        self._data[new_name] = State(new_name, new_is_final, transitions)
        self.check_integrity()

    def minimize(self) -> None:
        for state_tuple in self._get_states_to_combine():
            self._replace_states(state_tuple, '_'.join(sorted(state_tuple)))
