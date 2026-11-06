from datetime import datetime
import time

def register(shell):
    def tz_command(shell, *args):
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S %Z"))
    shell.register("tz", "Print current time", tz_command)
