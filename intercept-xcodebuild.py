#!/usr/bin/env python
"""Build a compilation database in JSON format, suitable for clang.

This is done by intercepting the compiler, and running xcodebuild.
"""

import os
import os.path as path
from subprocess import Popen, PIPE
import sys


def intercept_xcodebuild(xcodebuild_args, intercept_path, command_list_path):
    """Run xcodebuild, substituting intercept.py for the compiler.

    intercept.py will write the commands out to command_list_path.
    """
    with open(command_list_path, 'w') as f:
        f.write('[\n')

    new_env = dict(os.environ,
                   INTERCEPT_COMMAND_LIST=command_list_path,
                   CC=intercept_path,
                   CXX=intercept_path)

    args = list(xcodebuild_args)
    args.insert(0, 'xcodebuild')
    p = Popen(args, env=new_env, stdin=PIPE, stdout=PIPE)
    p.communicate()

    with open(command_list_path, 'a') as f:
        f.write(']')


def main(args):
    script_path = path.dirname(os.path.realpath(__file__))
    intercept_path = path.join(script_path, 'intercept.py')
    command_list_path = path.join(os.getcwd(), 'compile_commands.json')

    intercept_xcodebuild(args[1:],
                         intercept_path,
                         command_list_path)


if __name__ == '__main__':
    sys.exit(main(sys.argv))
