import os
import subprocess

def is_unix():
    return os.name == "posix"

def run_command(command_args):
    subprocess.call(command_args, text=True)