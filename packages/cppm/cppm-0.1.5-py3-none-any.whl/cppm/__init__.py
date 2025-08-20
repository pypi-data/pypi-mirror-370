import argparse

from .add_command import handle_add_command
from .build_command import handle_build_command
from .init_command import handle_init_command
from .install_command import handle_install_command
from .new_command import handle_new_command

# -----------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        prog="cppm",
        description="Project manager for C++ projects"
    )

    subparsers = parser.add_subparsers(dest="command", required=True)
    
    parser_build = subparsers.add_parser("build")
    parser_build.add_argument("-o", "--build_output", default="build")
    parser_build.add_argument(
        "--cmake_args",
        nargs=argparse.REMAINDER,
        default=[],
        help="Parameter list to forward to cmake command. Must be the last parameter, if used!"
    )

    parser_init = subparsers.add_parser("init")
    parser_init.add_argument(
        "--project_name",
        type=str,
        default="new-project",
        help="Name of the new project to create"
    )

    parser_add = subparsers.add_parser("add")
    parser_add.add_argument(
        "vcpkg_packages",
        nargs=argparse.REMAINDER,
        default=[],
        help="Packages list to forward to vcpkg install. Must be the last parameter, if used!"
    )

    subparsers.add_parser("install")

    parser_new = subparsers.add_parser("new")
    parser_new.add_argument(
        "project_name",
        type=str,
        help="Name of the new project to create"
    )
    
    args = parser.parse_args()

    if args.command == "build":
        handle_build_command(args.build_output, args.cmake_args)
    elif args.command == "init":
        handle_init_command(args.project_name)
    elif args.command == "add":
        handle_add_command(args.vcpkg_packages)
    elif args.command == "install":
        handle_install_command()
    elif args.command == "new":
        handle_new_command(args.project_name)
    
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    main()

# -----------------------------------------------------------------------------

