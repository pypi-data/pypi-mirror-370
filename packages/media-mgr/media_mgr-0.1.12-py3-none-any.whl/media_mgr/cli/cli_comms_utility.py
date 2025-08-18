#!/usr/bin/env python3
# ------------------------------------------------------------------------------------------------------
# -- CLI for Comms Utility Methods
# ------------------------------------------------------------------------------------------------------
# ======================================================================================================

# PYTHON_ARGCOMPLETE_OK
import argcomplete, argparse

import json
import os
import sys

from quickcolor.color_def import color
from showexception.showexception import exception_details

from ..comms_utility import run_cmd, is_server_active

# ------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------

def cli():
    try:
        parser = argparse.ArgumentParser(
                    description=f'{"-." * 3}  {color.CBLUE2}Comms {color.CYELLOW2}Utilities {color.CEND}for media manager',
                    epilog='-.' * 40)

        parser.add_argument('--version', action="store_true", help='top-level package version')

        parser.add_argument( '--ipv4', metavar='<address>',
                default=None, help='IPV4 to server')

        parser.add_argument('-v', '--verbose', action="store_true",
                            help='run with verbosity hooks enabled')

        subparsers = parser.add_subparsers(dest='cmd')

        p_dfh = subparsers.add_parser('dfh', help='List of drives (local or remote)')

        p_ls = subparsers.add_parser('ls', help='List files in dir')

        p_lsblk = subparsers.add_parser('lsblk', help='Show mountables')

        p_serverChk = subparsers.add_parser('server.chk', help='Server ping')

        argcomplete.autocomplete(parser)
        args = parser.parse_args()
        # print(args)

        if len(sys.argv) == 1:
            parser.print_help(sys.stderr)
            sys.exit(1)

        if args.version:
            from importlib.metadata import version
            import media_mgr
            print(f'{color.CGREEN}{os.path.basename(sys.argv[0])}{color.CEND} resides in package ' + \
                    f'{color.CBLUE2}{media_mgr.__package__}{color.CEND} ' + \
                    f'version {color.CVIOLET2}{version("media_mgr")}{color.CEND} ...')
            sys.exit(0)

        if args.cmd == 'dfh':
            # note quotes around grep argument
            # -- grep on zsh target env does not work without quotes
            cmd = 'df -h | grep "sd[b-z]" | sort -k 5'
            print(run_cmd(ipv4 = args.ipv4, cmd = cmd,
                cmdGet = True, debug = args.verbose))

        elif args.cmd == 'ls':
            print(run_cmd(ipv4 = args.ipv4, cmd = "ls -als .",
                cmdGet = True, debug = args.verbose))

        elif args.cmd == 'lsblk':
            print(run_cmd(ipv4 = args.ipv4, cmd = "lsblk -b --json",
                cmdGet = True, jsonOutput = True, debug = args.verbose))

        elif args.cmd == 'server.chk':
            serverInfo = f'-- Server {color.CYELLOW}{args.ipv4}{color.CEND}'
            if (is_server_active(ipv4 = args.ipv4)):
                print(f'{serverInfo} is {color.CGREEN}active{color.CEND}!')
            else:
                print(f'{serverInfo} is {color.CRED2}dead{color.CEND}!')

    except Exception as e:
        exception_details(e, "Comms Utility CLI")

# ------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------

