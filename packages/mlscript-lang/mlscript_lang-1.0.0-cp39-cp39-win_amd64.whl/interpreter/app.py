import sys
from .core import Interpreter, ReturnSignal

def run_from_file(filepath):
    interp = Interpreter()
    try:
        with open(filepath, 'r') as f:
            code = f.read()
            interp.run(code)
    except FileNotFoundError:
        print(f"Error: File not found at '{filepath}'")
    except Exception as e:
        print(f"An error occurred while executing the file: {e}")

def start_repl():
    interp = Interpreter()
    print("mlscript v1.0.0 -- interactive REPL")
    print("Type 'quit' or 'exit' to leave.")

    buffer = ""
    prompt = "mlscript> "

    while True:
        try:
            line = input(prompt)

            if line.strip().lower() in ("quit", "exit"):
                break

            buffer += line

            if (buffer.count('{') > buffer.count('}') or
                buffer.count('(') > buffer.count(')') or
                buffer.count('[') > buffer.count(']')):
                prompt = "...       "
                buffer += "\n"
                continue
            
            if not buffer.strip():
                buffer = ""
                prompt = "mlscript> "
                continue
            
            interp.run(buffer)

            buffer = ""
            prompt = "mlscript> "

        except ReturnSignal:
             print("SyntaxError: 'return' can only be used inside a function.")
             buffer = ""
             prompt = "mlscript> "
        except Exception as e:
            print(f"Error: {e}")
            buffer = ""
            prompt = "mlscript> "

def main():
    if len(sys.argv) > 1:
        run_from_file(sys.argv[1])
    else:
        start_repl()

if __name__ == "__main__":
    main()