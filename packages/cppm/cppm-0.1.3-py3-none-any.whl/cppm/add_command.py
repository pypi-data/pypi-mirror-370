import os
from .utils import run_command

# -----------------------------------------------------------------------------

def handle_add_command(packages_to_add):
    if packages_to_add is None or len(packages_to_add) == 0:
        print("Error: No packages specified to add.")
        return

    if os.name == "posix":
        path_to_vcpkg = "vcpkg/vcpkg"
    else:
        path_to_vcpkg = "vcpkg/vcpkg.exe"
    vcpkg_add_port = [path_to_vcpkg, "add", "port"]
    vcpkg_add_port.extend(packages_to_add)

    run_command(vcpkg_add_port)

# -----------------------------------------------------------------------------