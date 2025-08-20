import os
import shutil
from .install_command import handle_install_command
from .create_starter_project import create_starter_project
from .utils import run_command, is_unix

# -----------------------------------------------------------------------------

def handle_init_command(project_name: str = "new-project"):
    create_starter_project(project_name)
    clone_vcpkg()
    bootstrap_vcpkg()

    handle_install_command()

# -----------------------------------------------------------------------------

def clone_vcpkg():
    git_command = shutil.which("git")
    git_clone_command = [
        git_command, 
        "clone", 
        "https://github.com/Microsoft/vcpkg.git"
    ]
    run_command(git_clone_command)

# -----------------------------------------------------------------------------

def bootstrap_vcpkg():
    os.chdir("vcpkg")

    run_bootstrap_script = []
    
    if is_unix():
        unix_sh_command = shutil.which("sh")
        run_bootstrap_script = [unix_sh_command, "bootstrap-vcpkg.sh"]
    else: #windows
        run_bootstrap_script = ["bootstrap-vcpkg.bat"]
    
    run_command(run_bootstrap_script)

    os.chdir("..")

# -----------------------------------------------------------------------------
