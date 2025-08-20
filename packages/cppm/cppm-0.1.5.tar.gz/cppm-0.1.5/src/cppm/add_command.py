from .utils import run_command
from .vcpkg import vcpkg_executable_name

# -----------------------------------------------------------------------------

def handle_add_command(packages_to_add):
    if packages_to_add is None or len(packages_to_add) == 0:
        print("Error: No packages specified to add.")
        return

    vcpkg = vcpkg_executable_name()

    vcpkg_add_port = [vcpkg, "add", "port"]
    vcpkg_add_port.extend(packages_to_add)

    run_command(vcpkg_add_port)

# -----------------------------------------------------------------------------