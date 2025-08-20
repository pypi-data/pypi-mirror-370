from .install_command import handle_install_command
from .create_starter_project import create_starter_project
from .vcpkg import setup_vcpkg

# -----------------------------------------------------------------------------

def handle_init_command(project_name: str = "new-project"):
    create_starter_project(project_name)
    setup_vcpkg()

    handle_install_command()

# -----------------------------------------------------------------------------

