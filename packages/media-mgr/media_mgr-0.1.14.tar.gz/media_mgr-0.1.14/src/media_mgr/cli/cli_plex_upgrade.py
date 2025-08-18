#!/usr/bin/env python3
# ------------------------------------------------------------------------------------------------------
# -- CLI Methods for Plex Upgrade
# ------------------------------------------------------------------------------------------------------
# ======================================================================================================

# PYTHON_ARGCOMPLETE_OK
import argcomplete, argparse
from argcomplete.completers import EnvironCompleter     # used for file/path arguments

import json
import os
import sys

from quickcolor.color_def import color
from showexception.showexception import exception_details

from media_mgr.plex_upgrade import get_available_plex_server_package_name
from media_mgr.plex_upgrade import show_running_and_available_plex_server_versions
from media_mgr.plex_upgrade import download_new_plex_server_archive

from media_mgr.plex_upgrade import upgrade_plex_server, upgrade_all_plex_servers

# ------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------

def cli():
    try:
        parser = argparse.ArgumentParser(
                    description=f'{"-." * 3}  {color.CYELLOW2}PLEX Upgrade General Purpose {color.CEND}for media manager',
                    epilog='-.' * 40)

        parser.add_argument('-v', '--verbose', action='store_true',
                            help='run with verbosity hooks enabled')

        parser.add_argument('--version', action="store_true", help='top-level package version')

        subparsers = parser.add_subparsers(dest='cmd')

        p_show_avail_installer = subparsers.add_parser('show.avail.installer',
                help='show available PLEX server binary')

        p_plex_version = subparsers.add_parser('plex.ver',
                help='show running and available PLEX server versions')
        p_plex_version.add_argument('--ipv4', metavar='<server.addr>',
                default=None, help='PLEX Server IPV4')

        p_download = subparsers.add_parser('download.bin',
                help='download new PLEX server binary')
        p_download.add_argument('--ipv4', metavar='<server.addr>',
                default=None, help='PLEX Server IPV4')
        p_download.add_argument('--dir', default='/tmp',
                metavar='<dwnld.path>', help='PLEX bin download path').completer = EnvironCompleter

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

        if args.cmd == 'show.avail.installer':
            get_available_plex_server_package_name(verbose = True)

        elif args.cmd == 'plex.ver':
            show_running_and_available_plex_server_versions(ipv4 = args.ipv4,
                    debug = args.verbose)

        elif args.cmd == 'download.bin':
            download_new_plex_server_archive(ipv4 = args.ipv4,
                    downloadDir = args.dir, debug = args.verbose)

    except Exception as e:
        exception_details(e, "Plex Upgrade Utility CLI", raw=True)

# ------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------

def cli_plex_upgrade():
    try:
        parser = argparse.ArgumentParser(
                    description=f'{"-." * 3}  {color.CYELLOW2}PLEX Server Upgrade {color.CEND}for media manager',
                    epilog='-.' * 40)

        parser.add_argument('--version', action="store_true", help='top-level package version')

        parser.add_argument('-v', '--verbose', action='store_true',
                help='run with verbosity hooks enabled')

        parser.add_argument('--ipv4', metavar='<server.addr>',
                default=None, help='PLEX Server IPV4')
        parser.add_argument('--dir', default='/tmp',
                metavar='<dwnld.path>', help='PLEX bin download path').completer = EnvironCompleter
        parser.add_argument("--force", action='store_true', help='force upgrade even if versions match')

        argcomplete.autocomplete(parser)
        args = parser.parse_args()
        # print(args)

        if args.version:
            from importlib.metadata import version
            import media_mgr
            print(f'{color.CGREEN}{os.path.basename(sys.argv[0])}{color.CEND} resides in package ' + \
                    f'{color.CBLUE2}{media_mgr.__package__}{color.CEND} ' + \
                    f'version {color.CVIOLET2}{version("media_mgr")}{color.CEND} ...')
            sys.exit(0)

        upgrade_plex_server(ipv4 = args.ipv4, downloadDir = args.dir,
                force = args.force, debug = args.verbose)

    except Exception as e:
        exception_details(e, "Plex Server Upgrade CLI")

# ------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------

def cli_plex_upgrade_all_servers():
    try:
        parser = argparse.ArgumentParser(
                    description=f'{"-." * 3}  {color.CYELLOW2}PLEX Server Upgrade ' + \
                            f'{color.CBLUE2}(All Servers) {color.CEND}for media manager',
                    epilog='-.' * 40)

        parser.add_argument('--version', action="store_true", help='top-level package version')

        parser.add_argument('-v', '--verbose', action='store_true',
                help='run with verbosity hooks enabled')

        parser.add_argument('--dir', default='/tmp',
                metavar='<dwnld.path>', help='PLEX bin download path').completer = EnvironCompleter
        parser.add_argument("--force", action='store_true', help='force upgrade even if versions match')

        argcomplete.autocomplete(parser)
        args = parser.parse_args()
        # print(args)

        if args.version:
            from importlib.metadata import version
            import media_mgr
            print(f'{color.CGREEN}{os.path.basename(sys.argv[0])}{color.CEND} resides in package ' + \
                    f'{color.CBLUE2}{media_mgr.__package__}{color.CEND} ' + \
                    f'version {color.CVIOLET2}{version("media_mgr")}{color.CEND} ...')
            sys.exit(0)

        upgrade_all_plex_servers(downloadDir = args.dir, force = args.force,
                debug = args.verbose)

    except Exception as e:
        exception_details(e, "Plex Server Upgrade (All Servers) CLI")

# ------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------

