# -*- coding: utf-8 -*-
"""
main.py
This is the main entry point for the loguru_wrapper Python application.
"""
import importlib.util
import argparse
from dotenv import load_dotenv

from locshapython.extension.commands.command_manager import CommandManager
from locshapython.extension.registry import Registry

# Import project modules
from loguru_wrapper import __version_number__
# from src.loguru_wrapper.extension.my_module import MyClass

def register_module_spec() -> None:
    """
    Register the module spec.

    Package name must be dynamically read from current package to find path for
    installed package.
    """
    name = __package__
    if not name:
        raise ValueError('Package name not found')
    spec = importlib.util.find_spec(name)
    if not spec:
        raise ValueError('Package not found')

    Registry.set_module_spec(spec)

    if str(spec.name).find('loguru_wrapper') < 0:
        raise ValueError(f'Package name is not "loguru_wrapper", name: {spec.name}')

def register_command_manager() -> None:
    """
    Register the command manager.
    """
    Registry.set_command_manager(CommandManager())

def get_parser() -> argparse.ArgumentParser:
    """
    Create and return the argument parser for the application.
    """
    parser = argparse.ArgumentParser(description='My application')
    # subparsers = parser.add_subparsers(dest='<name>', help='', required=True)
    # parser.add_argument('command', help='what it does?')
    # parser.add_argument('name', help='Application name')
    parser.add_argument('-v', '--version', action='version', version=f'%(prog)s v{__version_number__}', help='version')
    parser.add_argument('--info', action='store_true', help='information')

    return parser

def get_args() -> argparse.Namespace:
    """
    Parse and return the command line arguments.
    """
    return get_parser().parse_args()

def main():
    """
    Run the application with $ python main.py <args>
    """
    load_dotenv()
    register_module_spec()
    register_command_manager()

    args = get_args()

    # my_application.App.run(args)

if __name__ == '__main__':
    main()