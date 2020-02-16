from mapper import State, List, Set


class SmartRange:
    def __init__(self, start: int = 0):
        self.i = start
        self._count = 0

    def __call__(self, count: int):
        self._count = count
        while self.i < self._count:
            yield self.i
            self.i += 1

    def dec(self):
        self.i -= 1
        self._count -= 1


class StateGenerator:
    def __init__(self, alphabet: Set[str]):
        self.alphabet = list(alphabet)
        self.alphabet.sort()

    def __call__(self, line: List[str], number: int = None) -> State:
        if line[1] == '1':
            is_final = True
        elif line[1] == '0':
            is_final = False
        else:
            raise ValueError("Cannot parse input file" + (": error in line " + str(number)) if number else '')
        if line[2] == '1':
            is_error = True
        elif line[2] == '0':
            is_error = False
        else:
            raise ValueError("Cannot parse input file" + (": error in line " + str(number)) if number else '')
        new_state = State(line[0], is_error, is_final)
        iterator = 3
        for letter in self.alphabet:
            new_state.local_map[letter] = line[iterator]
            iterator += 1
        return new_state


class Parser:
    def __init__(self, alphabet_filename: str, input_filename: str):
        self.input_file = input_filename
        self.alphabet_file = alphabet_filename

    def parse_input(self) -> List[State]:
        get_state = StateGenerator(self.parse_alphabet())
        result = list()
        with open(self.input_file) as file:
            for line in file.readlines():
                line = line.strip()
                if not line or line[0] == '#':
                    continue
                line = line.replace(",", ' ').split()
                line_counter = SmartRange()
                for i in line_counter(len(line)):
                    if line[i] == '':
                        del line[i]
                        line_counter.dec()
                result.append(get_state(line))
        return result

    def parse_alphabet(self) -> Set[str]:
        parsed = set()
        with open(self.alphabet_file) as file:
            result = file.read().strip().replace(',', ' ').replace('.', ' ').strip().split()
            for letter in result:
                if len(letter) > 1:
                    raise ValueError("Error while parsing alphabet: letter must be a single char")
                if len(letter) == 1:
                    parsed.add(letter)
        return parsed
