import os

from .utils import run_command, is_unix
from .vcpkg import setup_vcpkg, vcpkg_executable_name

# -----------------------------------------------------------------------------

def handle_install_command():
    if not os.path.exists("vcpkg"):
        setup_vcpkg()

    vcpkg = vcpkg_executable_name()
    vcpkg_install = [vcpkg, "install"]

    run_command(vcpkg_install)

# -----------------------------------------------------------------------------