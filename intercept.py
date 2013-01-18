#!/usr/bin/env python
import os
import os.path as path
import sys
from textwrap import dedent
from string import Template
from subprocess import Popen


def fall_back_on_xcode(compiler_path, args):
    """Take the arguments we intercepted, and pass them to the real compiler.
    """
    args = list(args)
    args[0] = compiler_path
    p = Popen(args)
    (stdoutdata, stderrdata) = p.communicate()
    sys.stdout.write(stdoutdata)
    sys.stderr.write(stderrdata)
    return p.returncode


def parse_args(args):
    command_list_path = os.environ['INTERCEPT_COMMAND_LIST']
    compiler_path = os.environ.get('INTERCEPT_CC', 'clang')

    # If this is a precompiled header, let xcode do its thing. This makes it so
    # precompiled headers are still generated, which is useful for code
    # completion.
    try:
        filetype_idx = args.index('-x') + 1
        if args[filetype_idx].endswith('-header'):
            return fall_back_on_xcode(compiler_path, args)
    except:
        pass

    # Xcode seems to pass the filename after the '-c' argument. It's probably
    # not very safe to rely on this, but the right way would be to have
    # knowledge about all of clang's arguments.
    file_idx = args.index('-c') + 1
    if file_idx >= len(args):
        return 0
    filename = path.abspath(args[file_idx])

    if filename == '/dev/null':
        return fall_back_on_xcode(args)

    tpl_str = dedent('''\
        { "directory": "$directory",
          "command": "$command",
          "file": "$filename" },''')
    tpl_lines = []
    for line in tpl_str.splitlines():
        tpl_lines.append('\t' + line)
    tpl_lines.append('')
    tpl_str = '\n'.join(tpl_lines)
    tpl = Template(tpl_str)

    args[0] = compiler_path

    with open(command_list_path, 'a') as f:
        f.write(tpl.substitute(directory=os.getcwd(),
                               command=' '.join(args),
                               filename=filename))

    return 0

if __name__ == '__main__':
    try:
        sys.exit(parse_args(sys.argv))
    except:
        sys.exit(0)
