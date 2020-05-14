from mapper import State, Map, List, Set


FILE_MSG = """#Will always start from first state by alphabet or q0 if present
#Alphabet must be described in "alphabet" order!
#Warning: author doesn't recommend you
#to enter state names manually using '_' symbol
#state\tisfin\ta\tb\tetc...\n
"""


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
            raise RuntimeError("Cannot parse input file" + (": error in line " + str(number)) if number else '')
        new_state = State(line[0], is_final)
        iterator = 2
        for letter in self.alphabet:
            new_state.add_jump(letter, line[iterator])
            iterator += 1
        return new_state


class Parser:
    def __init__(self, alphabet_filename: str, input_filename: str, output_filename: str = None):
        self.input_file = input_filename
        self.alphabet_file = alphabet_filename
        self.output_filename = output_filename if output_filename else input_filename

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
                    raise RuntimeError("Error while parsing alphabet: letter must be a single char")
                if len(letter) == 1:
                    parsed.add(letter)
        return parsed

    def write_to_file(self, map_to_write: Map) -> None:
        with open(self.output_filename, "w") as file:
            file.write(FILE_MSG)
            for state in map_to_write.data:
                file.write(state + '\t' + str(int(map_to_write[state].is_final)) + '\t')
                sorted_alphabet = list(map_to_write.alphabet)
                sorted_alphabet.sort()
                transitions_to_write = ''
                for letter in sorted_alphabet:
                    transitions_to_write += map_to_write[state].next_state(letter) + '\t'
                file.write(transitions_to_write.strip() + '\n')
