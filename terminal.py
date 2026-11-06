import importlib.util
import os
import shlex
import sys
from datetime import datetime
from pathlib import Path

class Command:
    def __init__(self, name, description, callback):
        self.name = name
        self.description = description
        self.callback = callback

    def __call__(self, shell, *args):
        return self.callback(shell, *args)

class Terminal:
    def __init__(self):
        self.commands = {}
        self.register("help", "Show available commands", self.help_command)
        self.register("echo", "Print a message", self.echo_command)
        self.register("date", "Show current date and time", self.date_command)
        self.register("clear", "Clear the terminal", self.clear_command)
        self.register("calc", "Evaluate a math expression", self.calc_command)
        self.register("pwd", "Print current working directory", self.pwd_command)
        self.register("ls", "List files in the current directory", self.ls_command)
        self.register("exit", "Exit the terminal", self.exit_command)
        self.register("quit", "Exit the terminal", self.exit_command)

    def register(self, name, description, callback):
        self.commands[name.lower()] = Command(name.lower(), description, callback)

    def unregister(self, name):
        self.commands.pop(name.lower(), None)

    def load_plugins(self, plugin_dir="plugins"):
        plugin_path = Path(plugin_dir)
        if not plugin_path.exists():
            return

        for file in sorted(plugin_path.glob("*.py")):
            if file.name.startswith("_"):
                continue
            module_name = f"plugin_{file.stem}"
            spec = importlib.util.spec_from_file_location(module_name, file)
            if spec is None or spec.loader is None:
                print(f"Could not load plugin: {file}")
                continue

            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            if hasattr(module, "register"):
                module.register(self)
            else:
                print(f"Plugin {file.name} does not define register(shell)")

    def help_command(self, shell, *args):
        if not args:
            print("Available commands:")
            for name in sorted(self.commands.keys()):
                cmd = self.commands[name]
                print(f"  {cmd.name:<12} - {cmd.description}")
            return

        target = args[0].lower()
        cmd = self.commands.get(target)
        if cmd is None:
            print(f"Unknown command: {target}")
            return
        print(f"{cmd.name} - {cmd.description}")

    def echo_command(self, shell, *args):
        print(" ".join(args))

    def date_command(self, shell, *args):
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    def clear_command(self, shell, *args):
        os.system("cls" if os.name == "nt" else "clear")

    def calc_command(self, shell, *args):
        if not args:
            print("Usage: calc <expression>")
            return

        expression = " ".join(args)
        allowed_names = {
            "abs": abs,
            "min": min,
            "max": max,
            "pow": pow,
            "round": round,
            "sum": sum
        }

        try:
            result = eval(expression, {"__builtins__": {}}, allowed_names)
            print(result)
        except Exception as e:
            print(f"Error: {e}")

    def pwd_command(self, shell, *args):
        print(os.getcwd())

    def ls_command(self, shell, *args):
        path = args[0] if args else "."
        try:
            for entry in sorted(os.listdir(path)):
                print(entry)
        except FileNotFoundError:
            print(f"No such directory: {path}")

    def exit_command(self, shell, *args):
        raise SystemExit

    def execute(self, line):
        if not line.strip():
            return

        try:
            tokens = shlex.split(line)
        except ValueError as e:
            print(f"Syntax error: {e}")
            return

        name = tokens[0].lower()
        cmd = self.commands.get(name)

        if cmd is None:
            print(f"Unknown command: {name}")
            print("Type 'help' to see available commands.")
            return

        try:
            cmd.callback(self, *tokens[1:])
        except SystemExit:
            raise
        except Exception as e:
            print(f"Command error: {e}")

    def run(self):
        print("Custom Python Terminal")
        print("Type 'help' to see commands. Type 'exit' to quit.")
        while True:
            try:
                line = input(">>> ")
            except EOFError:
                print("\nGoodbye.")
                break
            try:
                self.execute(line)
            except SystemExit:
                print("Goodbye.")
                break

if __name__ == "__main__":
    shell = Terminal()
    shell.load_plugins()
    shell.run()
