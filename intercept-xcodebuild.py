#!/usr/bin/env python
"""Build a compilation database in JSON format, suitable for clang.

Usage:
intercept-xcodebuild.py <output-db> <compiler-path> [xcodebuild args]

The compilation database may already exist, and if it does, the new results
will be merged with it. The passed-in compiler will be used to generate any
precompiled headers, and will end up as the compiler in the compilation
database. All remaining arguments are passed to xcodebuild.
"""

import os
import os.path as path
from subprocess import Popen, PIPE
import sys
import json
from shutil import copyfile
from tempfile import mkstemp


def intercept_xcodebuild(xcodebuild_args, intercept_path, compiler_path,
                         command_list_path):
    """Run xcodebuild, substituting intercept.py for the compiler.

    intercept.py will write the commands out to command_list_path.
    """
    with open(command_list_path, 'w') as f:
        f.write('[\n')

    new_env = dict(os.environ,
                   INTERCEPT_COMMAND_LIST=command_list_path,
                   INTERCEPT_CC=compiler_path,
                   CC=intercept_path,
                   CXX=intercept_path)

    args = list(xcodebuild_args)
    args.insert(0, 'xcodebuild')
    p = Popen(args, env=new_env, stdin=PIPE, stdout=PIPE)
    p.communicate()

    # intercept.py doesn't actually parse or write JSON, so it'll end up with a
    # trailing comma and newline. Remove the comma but keep the newline.
    with open(command_list_path, 'r') as f:
        contents = f.read()
    contents = contents[:-2] + '\n]'
    with open(command_list_path, 'w') as f:
        f.write(contents)


def build_command_dict(commands):
    """Take a list of command objects, and make a dict keyed by filename."""
    return {command['file']: command for command in commands}


def merge_compile_commands(new_commands, existing):
    """Take an existing list of commands, and a new list, and merge them.

    Commands are merged as dictionaries keyed by the filenames. Files that do
    not already exist are added, and files that already existed are updated
    with the new directory/command.
    """
    existing_dict = build_command_dict(existing)
    existing_dict.update(build_command_dict(new_commands))
    return [command for _, command in existing_dict.iteritems()]

JSON_OPTIONS = {
    'indent': 2,
    'separators': (',', ': '),
}


def update_merged_command_list(command_list_path, merged_path):
    """Load the new and existing command lists, and merge to the existing one.
    """
    with open(command_list_path, 'r') as command_list_file, \
            open(merged_path, 'r') as merged_file:
        merged = merge_compile_commands(json.loads(command_list_file.read()),
                                        json.loads(merged_file.read()))
    with open(merged_path, 'w') as merged_file:
        merged_file.write(json.dumps(merged, **JSON_OPTIONS))


class TemporaryFileWithCleanup:
    def __enter__(self):
        (self.handle, self.filename) = mkstemp()
        return self.filename

    def __exit__(self, type, value, traceback):
        os.remove(self.filename)


def usage():
    """Print the usage string and return an appropriate error code."""
    print __doc__
    return 0


def main(args):
    script_path = path.dirname(os.path.realpath(__file__))
    intercept_path = path.join(script_path, 'intercept.py')

    if len(args) < 3:
        return usage()
    if args[1] == '-h':
        return usage()

    with TemporaryFileWithCleanup() as command_list_path:
        merged_path = args[1]
        compiler_path = args[2]

        intercept_xcodebuild(args[3:],
                             intercept_path,
                             compiler_path,
                             command_list_path)

        if path.exists(merged_path):
            update_merged_command_list(command_list_path, merged_path)
        else:
            copyfile(command_list_path, merged_path)

if __name__ == '__main__':
    sys.exit(main(sys.argv))
