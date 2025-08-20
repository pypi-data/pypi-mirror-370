import subprocess

def run_command(command_args):
    subprocess.call(command_args, text=True)