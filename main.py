from mapper import Map, State
from parser import Parser


def green(inp: str) -> str:
    """Returns string in green color to print"""
    return "\033[92m" + inp + "\033[0m"


def red(inp: str) -> str:
    """Returns string in red color to print"""
    return "\033[91m" + inp + "\033[0m"


def yellow(inp: str) -> str:
    """Returns string in yellow color to print"""
    return "\033[93m" + inp + "\033[0m"


def underline(inp: str) -> str:
    """Returns underlined string to print"""
    return "\033[4m" + inp + "\033[0m"


def blue(inp: str) -> str:
    """Returns string in blue color to print"""
    return "\033[94m" + inp + "\033[0m"


class Runner:
    def __init__(self):
        parser = Parser("./data/alphabet.txt", "./data/input.txt")
        self.map = Map(parser.parse_alphabet(), parser.parse_input())

    def __call__(self, string_to_check: str, explain: bool = False) -> bool:
        current_state: State = self.map.initial_state
        if explain:
            func = yellow
            if current_state.is_final:
                func = green
            elif current_state.is_error:
                func = red
            print("Beginning with state " + func(current_state.name))
        for symbol in string_to_check:
            if symbol not in self.map.alphabet:
                if explain:
                    print("Symbol " + underline(red(symbol)) + " not found in the alphabet")
                return False
            if not current_state.is_present(symbol):
                raise RuntimeError("Internal automaton error: cannot determine how to change state with symbol " + symbol)
            if explain:
                print("Detected symbol " + underline(blue(symbol)))
                func = yellow
                if self.map[current_state.next_state(symbol)].is_final:
                    func = green
                elif self.map[current_state.next_state(symbol)].is_error:
                    func = red
                print("Changing state to " + func(current_state.next_state(symbol)))
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
    try:
        runner = Runner()
    except Exception as exc:
        print(red("Error!"))
        print(red(exc.args[0]))
        exit()
    print(green("Done"))

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
                print("    Accept " + green("✔️") + '\n')
            else:
                print("    Reject " + red("❌") + '\n')
    except (EOFError, KeyboardInterrupt):
        print()
        exit()
    except Exception as exc:
        print(red(exc.args[0]))
        exit()
