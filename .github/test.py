#!/usr/bin/env python3

import argparse
import os
import subprocess
import sys
import tuttest

parser = argparse.ArgumentParser()
parser.add_argument('--first-run', action='store_true')
parser.add_argument('--build', action='store_true')
args = parser.parse_args()

# Find paths
script_path = os.path.realpath(sys.argv[0])  # This script
script_dir = os.path.dirname(script_path)  # Dir containing this script
repo_dir = os.path.dirname(script_dir)  # Repo dir - one up from here

# Read snippets
snippets = tuttest.get_snippets(repo_dir + '/README.rst')

# Get some of the snippets
install_paths = snippets['install-paths'].text
virtualenv = snippets['virtualenv'].text
lowrisc_toolchain = snippets['lowrisc-toolchain'].text
# Remove these from the collection; their use depends on env/args
ibex_build = snippets.pop('ibex-build').text
vivado_ibex_build = snippets.pop('vivado-ibex-build').text

if args.first_run:
    # Do the entire prep until patching Yosys/building Ibex
    cmd = '\n\n'.join(map(lambda s: s.text, snippets.values()))
else:
    # Only install and set up paths
    cmd = install_paths

if args.build:
    if not args.first_run:  # Set up the lowRISC toolchain
        cmd += '\n\n' + virtualenv + '\n\n' + lowrisc_toolchain
    cmd += '\n\n' + ibex_build
    if 'CI' not in os.environ or not os.environ['CI']:
        # Only do Vivado step if not in CI
        cmd += '\n\n' + vivado_ibex_build

# Print commands for debugging purposes
print('===== RUNNING: =====')
print(cmd)
print('====================\n')

# Fail on any error
cmd = 'set -e;' + cmd

try:
    subprocess.run(cmd, shell=True, check=True, executable='/bin/bash',
                   env={**os.environ, 'PATCH_DIR': repo_dir})
except subprocess.CalledProcessError:
    exit(1)
