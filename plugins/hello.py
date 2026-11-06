def register(shell):
    def hello_command(shell, *args):
        name = " ".join(args) if args else "world"
        print(f"Hello, {name}!")

    shell.register("hello", "Say hello to someone", hello_command)
