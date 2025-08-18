"""
Define and run command-line applications.
"""
from __future__ import annotations

import inspect
import sys
from argparse import ArgumentParser, RawTextHelpFormatter, _SubParsersAction
from contextlib import AbstractContextManager, ExitStack
from importlib import import_module
from pkgutil import iter_modules
from textwrap import dedent
from types import ModuleType
from typing import Any, Callable, Iterable, Sequence

from zut import SimpleError, get_logger


def add_commands(subparsers: _SubParsersAction[ArgumentParser], package: ModuleType|str):
    """
    Add all sub modules of the given package as commands.
    """
    if isinstance(package, str):
        package = import_module(package)
    elif not isinstance(package, ModuleType):
        raise TypeError(f"Invalid argument 'package': not a module")

    package_path = getattr(package, '__path__', None)
    if not package_path:
        raise TypeError(f"Invalid argument 'package': not a package")

    for module_info in iter_modules(package_path):
        if module_info.name.startswith('_'):
            continue # skip

        add_command(subparsers, f'{package.__name__}.{module_info.name}')

    
def add_command(subparsers: _SubParsersAction[ArgumentParser], handle: Callable|ModuleType|str, *, name: str|None = None, doc: str|None = None, help: str|None = None, add_arguments: Callable[[ArgumentParser]]|None = None, self: Any|None = None, parents: ArgumentParser|Sequence[ArgumentParser]|None = None, **defaults):
    """
    Add the given function or module as a command.
    """
    if isinstance(handle, str):
        handle = import_module(handle)

    if isinstance(handle, ModuleType):
        module = handle        
        command_class = getattr(module, 'Command', None)
        if command_class:
            handle = command_class # will be treated later
        else:    
            handle = getattr(module, 'handle', None) # type: ignore
            if not handle:
                handle = getattr(module, '_handle', None) # type: ignore
                if not handle:
                    handle_name = name if name else module.__name__.split('.')[-1]
                    handle = getattr(module, handle_name, None) # type: ignore
                    if not handle:
                        raise ValueError(f"Cannot use module {module.__name__} as a command: no attribute named \"Command\", \"handle\" , \"_handle\" or \"{handle_name}\"")
    elif callable(handle):
        module = None
    else:
        raise TypeError(f"Invalid argument 'handle': not a module or a callable")
    
    if isinstance(handle, type): # Command class (e.g. Django management command)
        command_class = handle.__name__.lower()
        command_instance = handle()
        handle = getattr(command_instance, 'handle')
        if not name:
            if command_class.endswith('subcommand') and command_class != 'subcommand':
                name = command_class[:-len('subcommand')]
            elif command_class.endswith('command') and command_class != 'command':
                name = command_class[:-len('command')]
        if not add_arguments:
            add_arguments = getattr(command_instance, 'add_arguments', None)
        if not help:
            help = getattr(command_instance, 'help', None)
        if not doc:
            doc = command_instance.__doc__

    if not name:
        name = getattr(handle, 'name', None)
        if not name:
            if module:
                name = module.__name__.split('.')[-1]
            else:
                name = handle.__name__ # type: ignore

    if not doc:
        doc = getattr(handle, 'doc', None)
        if doc:
            if callable(doc):
                doc = doc()
        else:
            doc = handle.__doc__
            if not doc:
                if module:
                    doc = module.__doc__
                if not doc:
                    doc = help

    if not help:
        help = getattr(handle, 'help', doc)
    
    if not add_arguments:
        add_arguments = getattr(handle, 'add_arguments', None)        
        if not add_arguments and module:
            add_arguments = getattr(module, 'add_arguments', None)

    if parents is None:
        parents = []
    elif isinstance(parents, ArgumentParser):
        parents = [parents]

    cmdparser = subparsers.add_parser(name, help=get_help_text(help), description=get_description_text(doc), formatter_class=RawTextHelpFormatter, parents=parents)

    if add_arguments:
        if self is not None and 'self' in inspect.signature(add_arguments).parameters:
            add_arguments(self, cmdparser) # type: ignore
        else:
            add_arguments(cmdparser)

    cmdparser.set_defaults(handle=handle, **defaults)

    return cmdparser


def get_help_text(doc: str|None):
    if doc is None:
        return None
    
    doc = doc.strip()
    try:
        return doc[0:doc.index('\n')].strip()
    except:
        return doc
    

def get_description_text(doc: str|None):
    if doc is None:
        return None
    
    return dedent(doc)


def get_exit_code(code: Any) -> int:
    if not isinstance(code, int):
        code = 0 if code is None or code is True else 1
    return code


def create_command_parser(prog: str|None = None, *, version: str|None = None, doc: str|None = None, keep_default_help = False) -> ArgumentParser:
    parser = (ArgumentParser if keep_default_help else ExtendedArgumentParser)(prog=prog, description=get_description_text(doc) if doc else None, formatter_class=RawTextHelpFormatter)
 
    if version is not None:
        parser.add_argument('--version', action='version', version=f"{parser.prog} {version}", help=None if keep_default_help else "Show program's version number and exit.")
    
    return parser


class ExtendedArgumentParser(ArgumentParser):
    def __init__(self, *arg, help_help = "Show this help message and exit.", **kwargs):
        super().__init__(*arg, **kwargs)
        self.help_help = help_help

        for action in self._actions:
            if action.dest == 'help':
                action.help = self.help_help
                break


def run_command(handle: ArgumentParser|Callable|dict[str,Any], args: dict|list[str]|None = None, *, default: str|None = None,
                context_builder: Callable[[dict[str,Any],list[str]],AbstractContextManager|Iterable[AbstractContextManager]|None]|None = None,
                additional_args_builders: dict[str,Callable[[],Any]|Callable[[dict[str,Any]],Any]]|None = None):
    """
    Run a command.

    :param handle:
    - An `ArgumentParser` objects: in this case, `run_command` will take care of calling `parse_args` on it.
    - A handle function already parsed before calling this `run_command`.
    - A dictionnary: this is intended for running Django subcommands directly from the keywork arguments of the Django command's `handle(**option)` method. Django-specific options (verbosity, settings, pythonpath, traceback, no_color, force_color and skip_checks) are removed.

    :param context_builder: `(args: dict, handle_parameters: list[str]) -> context manager, list of context managers or None`
    """
    if isinstance(args, list):
        argv = args
        args = {}
    else:
        if args is None:
            args = {}
        argv = sys.argv[1:]
    
    handle_func: Callable|None = None
    remaining_argv = []
    parser: ArgumentParser|None = None
    if isinstance(handle, dict): # Intended for running Django subcommands
        for key, value in handle.items():
            if key == 'handle':
                handle_func = value
            elif key not in {'verbosity', 'settings', 'pythonpath', 'traceback', 'no_color', 'force_color', 'skip_checks'}:
                args[key] = value
    elif isinstance(handle, ArgumentParser):
        parser = handle
        known_args, remaining_argv = parser.parse_known_args(argv)
        known_args = vars(known_args)
        args = {**args, **known_args}
        handle_func = args.pop('handle', None)
    else:
        handle_func = handle

    logger = get_logger(__name__)
    
    if not handle_func:
        if default and parser:
            known_args = vars(parser.parse_args([default, *argv]))
            args = {**args, **known_args}
            handle_func = args.pop('handle', None)
            if not handle_func:
                logger.error("Default command handle not found")
                return 1                
        else:
            logger.error("Missing command")
            return 1
    elif remaining_argv:
        logger.error(f"Unrecognized arguments: {', '.join(remaining_argv)}")
        return 1

    try:
        r = 1
        with ExitStack() as exit_stack:
            if context_builder or additional_args_builders:
                handle_parameters = list(inspect.signature(handle_func).parameters.keys())
                
                if context_builder:
                    context_managers = context_builder(args, handle_parameters)
                    if context_managers is not None:
                        if isinstance(context_managers, AbstractContextManager):
                            context_managers = [context_managers]
                        for manager in context_managers:
                            exit_stack.enter_context(manager)
                
                if additional_args_builders:
                    for arg in handle_parameters:
                        if not arg in args:
                            builder = additional_args_builders.get(arg)
                            if builder:
                                builder_params_count = len(inspect.signature(builder).parameters)
                                additional_arg = builder(args) if builder_params_count > 0 else builder() # type: ignore
                                if isinstance(additional_arg, AbstractContextManager):
                                    additional_arg = exit_stack.enter_context(additional_arg)
                                args[arg] = additional_arg

            r = handle_func(**args)
        return get_exit_code(r)
    except SimpleError as err:
        logger.error(str(err))
        return 1
    except KeyboardInterrupt:
        logger.error("Interrupted")
        return 1
    except BaseException as err:
        message = str(err)
        logger.exception(f"{type(err).__name__}{f': {message}' if message else ''}")
        return 1


def exec_command(handle: ArgumentParser|Callable|dict[str,Any], args: dict|list[str]|None = None, *, default: str|None = None,
                 context_builder: Callable[[dict[str,Any],list[str]],AbstractContextManager|Iterable[AbstractContextManager]|None]|None = None,
                 additional_args_builders: dict[str,Callable[[],Any]|Callable[[dict[str,Any]],Any]]|None = None):
    """
    - `context_builder`: `(args: dict, handle_parameters: list[str]) -> context manager, list of context managers or None`
    """
    r = run_command(handle, args, default=default, context_builder=context_builder, additional_args_builders=additional_args_builders)
    sys.exit(r)
