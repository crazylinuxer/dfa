from mapper import Map, State
from parser import Parser


class Runner:
    def __init__(self):
        parser = Parser("./data/alphabet.txt", "./data/input.txt")
        self.map = Map(parser.parse_alphabet(), parser.parse_input())

    def __call__(self, string_to_check: str, explain: bool = False) -> bool:
        current_state: State = self.map.initial_state
        if explain:
            print("Beginning with state " + current_state.name)
        for symbol in string_to_check:
            if symbol not in self.map.alphabet:
                if explain:
                    print("Symbol " + symbol + " not found in the alphabet")
                return False
            if not current_state.is_present(symbol):
                raise ValueError("Internal automaton error: cannot determine how to change state with symbol " + symbol)
            if explain:
                print("Detected symbol " + symbol)
                print("Changing state to " + current_state.next_state(symbol))
            current_state = self.map[current_state.next_state(symbol)]
            if current_state.is_error:
                if explain:
                    print("Detected error state")
                return False
        if current_state.is_final:
            if explain:
                print("Ended with final state")
            return True
        else:
            if explain:
                print("Ended with non-final state")
            return False


if __name__ == "__main__":
    print("Building state map... ", end='', flush=True)
    runner = Runner()
    print("\033[92m" + "Done" + "\033[0m")  # just 'Done' in green color

    print("Would you like to see explanation of each automaton step? [Y/n]")
    try:
        response = input()
        if response in ['', 'y', 'Y', 'д', 'Д']:
            exp = True
        else:
            exp = False
        while True:
            value = input("Enter the string to check: ")
            if runner(value, exp):
                print("Accept")
            else:
                print("Reject")
    except (EOFError, KeyboardInterrupt):
        print()
        exit()
