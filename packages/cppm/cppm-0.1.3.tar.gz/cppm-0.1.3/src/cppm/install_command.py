import os
from .utils import run_command

# -----------------------------------------------------------------------------

def handle_install_command():
    
    if os.name == "posix":
        path_to_vcpkg = "vcpkg/vcpkg"
    else:
        path_to_vcpkg = "vcpkg/vcpkg.exe"
    vcpkg_install = [path_to_vcpkg, "install"]

    run_command(vcpkg_install)

# -----------------------------------------------------------------------------