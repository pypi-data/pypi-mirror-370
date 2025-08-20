import argparse
import shutil
import os

os.environ['PYTHONDONTWRITEBYTECODE'] = '1'

def init():
    """Initialize the project."""
    templates = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')
    files_to_copy = ['md_config.yml']
    for filename in files_to_copy:
        src_path = os.path.join(templates, filename)
        if not os.path.exists(filename):
            shutil.copy(src_path, filename)

def main():
    parser = argparse.ArgumentParser(description="McDis RCON CLI")
    subparsers = parser.add_subparsers(dest='command')

    # Subcommand `init`
    init_parser = subparsers.add_parser('init', help='Initialize the project')
    init_parser.set_defaults(func=init)

    # Subcommand `run`
    from ..main import run
    mcdis_parser = subparsers.add_parser('run', help='Run the main function')
    mcdis_parser.set_defaults(func=run)

    # Subcommand `run`
    from ..main import update_po
    mcdis_parser = subparsers.add_parser('po', help='Update the .po file')
    mcdis_parser.set_defaults(func = update_po)

    # Parse args and call the appropriate function
    args = parser.parse_args()
    if args.command:
        args.func()
    else:
        parser.print_help()
