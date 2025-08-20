import os

# -----------------------------------------------------------------------------

def create_starter_project(project_name: str):
    create_cmake_lists(project_name)
    create_main_cpp()
    create_git_ignore()
    create_vcpkg_json(project_name)
    create_readme_file(project_name)


# -----------------------------------------------------------------------------

def create_cmake_lists(project_name: str):
    if not os.path.exists("CMakeLists.txt"):
        with open("CMakeLists.txt", "w") as f:
            f.write("cmake_minimum_required(VERSION 3.30)\n")
            f.write(f"project({project_name})\n")
            f.write("\n")
            f.write("set(SRC_FILES src/main.cpp)\n")
            f.write("add_executable(${PROJECT_NAME} ${SRC_FILES})\n")

# -----------------------------------------------------------------------------

def create_main_cpp():
    if not os.path.exists("src/main.cpp"):
        os.makedirs("src", exist_ok=True)
        with open("src/main.cpp", "w") as f:
            f.write("#include <iostream>\n\n")
            f.write("int main() {\n")
            f.write("    std::cout << \"Hello World!\" << std::endl;\n")
            f.write("    return 0;\n")
            f.write("}\n")

# -----------------------------------------------------------------------------

def create_git_ignore():
    if not os.path.exists(".gitignore"):
        with open(".gitignore", "w") as f:
            f.write("# build\n")
            f.write("build/\n\n")
            f.write("# vcpkg\n")
            f.write("vcpkg/\n")
            f.write("vcpkg_installed/\n\n")

# -----------------------------------------------------------------------------

def create_vcpkg_json(project_name: str):
    if not os.path.exists("vcpkg.json"):
        with open("vcpkg.json", "w") as f:
            f.write("{\n")
            f.write(f'  "name": "{project_name}",\n')
            f.write('  "version-string": "1.0.0",\n')
            f.write('  "dependencies": [\n')
            f.write('    "vcpkg-cmake",\n')
            f.write('    "vcpkg-cmake-config"\n')
            f.write('  ]\n')
            f.write("}\n")

# -----------------------------------------------------------------------------

def create_readme_file(project_name: str):
    if not os.path.exists("README.md"):
        with open("README.md", "w") as f:
            f.write(f"# {project_name}\n\n")
            f.write("This is a C++ project created by CppM.\n")
            f.write("## Build Instructions\n")
            f.write("Run `cppm build` to build the project.\n")
            f.write("## Usage\n")
            f.write("Run the executable in the `build` directory.\n")

# -----------------------------------------------------------------------------