import os
from .utils import run_command

# -----------------------------------------------------------------------------

def find_cmake_app():
    cmake_app_name = "cmake"
    vcpkg_root = "vcpkg"

    for root, _, files in os.walk(vcpkg_root):
        if cmake_app_name in files:
            path_to_cmake = os.path.join(root, cmake_app_name)
            return os.path.abspath(path_to_cmake)
    
    return ""

# -----------------------------------------------------------------------------

def handle_build_command(build_folder, cmake_args):
    cmake = find_cmake_app()
    vcpkg_toolchain_path = "vcpkg/scripts/buildsystems/vcpkg.cmake"

    cmake_config =  [cmake, "-S", ".", "-B", build_folder]
    cmake_config.extend(cmake_args)
    cmake_config.extend([f"-DCMAKE_TOOLCHAIN_FILE={vcpkg_toolchain_path}"])
    
    run_command(cmake_config)

    cmake_build = [cmake, "--build", build_folder]
    run_command(cmake_build)

# -----------------------------------------------------------------------------