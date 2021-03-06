""" Mamba command line launcher """
import sys
from os import path, getcwd
from os.path import exists, join
from argparse import ArgumentParser

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

import mamba  # noqa
from mamba.commands import MambaCommand  # noqa
from mamba.core.utils import get_classes_from_module  # noqa


def execute(argv=None):
    """ Mamba command line launcher """
    if argv is None:
        argv = sys.argv

    cmds = get_classes_from_module('mamba.commands', MambaCommand)
    cmdname = _pop_command_name(argv)
    parser = ArgumentParser()

    if cmdname is None:
        _print_commands()
        sys.exit(0)
    elif cmdname not in cmds:
        _print_unknown_command(cmdname)
        sys.exit(2)

    cmd = cmds[cmdname]
    parser.usage = "mamba %s %s" % (cmdname, cmd.syntax())
    parser.description = cmd.long_desc()
    cmd.add_arguments(parser)

    args = parser.parse_args(args=argv[1:])

    mamba_dir = path.dirname(path.abspath(__file__))

    if exists(join(getcwd(), 'mamba.cfg')):
        project_dir = getcwd()
        sys.path.insert(0, join(project_dir))
    else:
        project_dir = None

    sys.exit(cmd.run(args, mamba_dir, project_dir))


# Internal


def _pop_command_name(argv):
    i = 0
    for arg in argv[1:]:
        if not arg.startswith('-'):
            del argv[i]
            return arg
        i += 1
    return None


def _print_header():
    print(f"Mamba {mamba.__version__}\n")


def _print_commands():
    _print_header()
    print("Usage:")
    print("  mamba <command> [args]\n")
    print("Available commands:")
    cmds = get_classes_from_module('mamba.commands', MambaCommand)
    for cmdname, cmdclass in sorted(cmds.items()):
        print("  %-13s %s" % (cmdname, cmdclass.short_desc()))
    print()
    print('Use "mamba <command> -h" to see more info about a command')


def _print_unknown_command(cmdname):
    _print_header()
    print("Unknown command: %s\n" % cmdname)
    print('Use "mamba" to see available commands')


if __name__ == '__main__':
    execute()
