import shutil
import os

from .utils import run_command, is_unix

# -----------------------------------------------------------------------------

def vcpkg_executable_name():
    vcpkg_root = "vcpkg"

    vcpkg_executable = "vcpkg" if is_unix() else "vcpkg.exe"
    return os.path.join(vcpkg_root, vcpkg_executable)

# -----------------------------------------------------------------------------

def setup_vcpkg():
    clone_vcpkg()
    bootstrap_vcpkg()

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