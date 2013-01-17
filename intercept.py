#!/usr/bin/env python
import os
import sys
from textwrap import dedent
from string import Template


def parse_args(args):
    command_list_path = os.environ['INTERCEPT_COMMAND_LIST']

    # Xcode seems to pass the filename after the '-c' argument. It's probably
    # not very safe to rely on this, but the right way would be to have
    # knowledge about all of clang's arguments.
    file_idx = args.index('-c') + 1
    if file_idx >= len(args):
        return 0

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

    args[0] = 'clang'

    with open(command_list_path, 'a') as f:
        f.write(tpl.substitute(directory=os.getcwd(),
                               command=' '.join(args),
                               filename=args[file_idx]))

    return 0

if __name__ == '__main__':
    try:
        sys.exit(parse_args(sys.argv))
    except:
        sys.exit(0)
