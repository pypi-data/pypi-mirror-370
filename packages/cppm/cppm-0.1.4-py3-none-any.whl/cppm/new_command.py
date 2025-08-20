import os
from .init_command import handle_init_command

# -----------------------------------------------------------------------------

def handle_new_command(project_name: str):
    os.makedirs(project_name, exist_ok=True)
    os.chdir(project_name)   
    handle_init_command(project_name)

# -----------------------------------------------------------------------------