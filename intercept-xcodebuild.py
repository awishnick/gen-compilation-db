#!/usr/bin/env python
import os
import os.path as path
from subprocess import Popen, PIPE
import sys

script_path = path.dirname(os.path.realpath(__file__))
intercept_path = path.join(script_path, 'intercept.py')
command_list_path = path.join(os.getcwd(), 'compile_commands.json')

with open(command_list_path, 'w') as f:
    f.write('[\n')

new_env = dict(os.environ,
               INTERCEPT_COMMAND_LIST=command_list_path,
               CC=intercept_path,
               CXX=intercept_path)

args = list(sys.argv)
args[0] = 'xcodebuild'
p = Popen(args, env=new_env, stdin=PIPE, stdout=PIPE)
(stdoutdata, stderrdata) = p.communicate()

with open(command_list_path, 'a') as f:
    f.write(']')
