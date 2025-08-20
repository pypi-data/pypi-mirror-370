from .utils import run_command, is_unix

# -----------------------------------------------------------------------------

def handle_install_command():
    
    if is_unix():
        path_to_vcpkg = "vcpkg/vcpkg"
    else:
        path_to_vcpkg = "vcpkg/vcpkg.exe"
    
    vcpkg_install = [path_to_vcpkg, "install"]

    run_command(vcpkg_install)

# -----------------------------------------------------------------------------