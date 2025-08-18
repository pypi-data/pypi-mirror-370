#!/usr/bin/env python3
# ------------------------------------------------------------------------------------------------------
# -- CLI Methods for Search
# ------------------------------------------------------------------------------------------------------
# ======================================================================================================

# PYTHON_ARGCOMPLETE_OK
import argcomplete, argparse

import json
import os
import sys

from quickcolor.color_def import color
from showexception.showexception import exception_details

from media_mgr.server_cfg import ServerConfig
from media_mgr.media_cfg import MediaConfig

from media_mgr.search import show_titles_in_paths, show_matched_titles, show_all_matched_titles
from media_mgr.search import show_all_matched_titles_multiserver

# ------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------

def cli():
    try:
        preMc = MediaConfig()

        parser = argparse.ArgumentParser(
                    description=f'{"-." * 3}  {color.CYELLOW2}Search {color.CEND}for media manager',
                    epilog='-.' * 40)

        parser.add_argument('-v', '--verbose', action="store_true",
                            help='run with verbosity hooks enabled')

        parser.add_argument('--version', action="store_true", help='top-level package version')

        subparsers = parser.add_subparsers(dest='cmd')

        p_showTitlesInPaths = subparsers.add_parser('show.titles.in.paths', help='show titles in one or more paths')
        p_showTitlesInPaths.add_argument('--ipv4', default=None, metavar='<ipv4.addr>', help='Server IPV4')
        p_showTitlesInPaths.add_argument('--type', default='plex',
                metavar='<srvType>', choices=['plex', 'worker'], help='Server types')
        p_showTitlesInPaths.add_argument("paths", metavar='<path_1> .. <path_n>', nargs=argparse.REMAINDER,
                choices=preMc.get_configured_entries(),
                help='Search paths to probe')

        p_showMatchedTitles = subparsers.add_parser('show.match', help='show matched titles')
        p_showMatchedTitles.add_argument('--ipv4', default=None, metavar='<ipv4.addr>', help='Server IPV4')
        p_showMatchedTitles.add_argument('--type', default='plex',
                metavar='<srvType>', choices=['plex', 'worker'], help='Server types')
        p_showMatchedTitles.add_argument("terms", metavar='<term_1> .. <term_n>', nargs=argparse.REMAINDER,
                help='Search terms to match')

        p_showAllMatchedTitles = subparsers.add_parser('show.all.matches', help='show matched titles from all servers')
        p_showAllMatchedTitles.add_argument("terms", metavar='<term_1> .. <term_n>', nargs='*',
                help='Search terms to match')

        p_asyncShowAllMatchedTitles = subparsers.add_parser('async.show.all.matches', help='show matched titles from all servers (asyncio)')
        p_asyncShowAllMatchedTitles.add_argument("terms", metavar='<term_1> .. <term_n>', nargs='*',
                help='Search terms to match')

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

        if args.cmd == 'show.titles.in.paths':
            show_titles_in_paths(ipv4 = args.ipv4, serverType = args.type,
                    paths = args.paths, verbose = args.verbose)

        elif args.cmd == 'show.match':
            show_matched_titles(ipv4 = args.ipv4, serverType = args.type,
                    searchTerms = args.terms)

        elif args.cmd == 'show.all.matches':
            show_all_matched_titles(searchTerms = args.terms)

        elif args.cmd == 'async.show.all.matches':
            show_all_matched_titles_multiserver(searchTerms = args.terms,
                                                verbose = args.verbose)

    except Exception as e:
        exception_details(e, "Search CLI")

# ------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------

def cli_search_plex():
    try:
        parser = argparse.ArgumentParser(
                    description=f'{"-." * 3}  {color.CBLUE2}Search {color.CYELLOW2}All Servers {color.CEND}utility',
                    epilog='-.' * 40)

        parser.add_argument('-v', '--verbose', action="store_true",
                            help='run with verbosity hooks enabled')

        parser.add_argument('--version', action='store_true', help='top-level package version')

        parser.add_argument('--ipv4', default=None, metavar='<ipv4.addr>', help='Server IPV4')

        parser.add_argument("terms", metavar='<term_1> .. <term_n>', nargs='*',
                help='Search terms to match')

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

        if args.ipv4:
            srv = ServerConfig()
            for serverLabel in srv.get_server_name_list():
                if args.ipv4 == srv.get_server_address(serverLabel = serverLabel):
                    return show_matched_titles(ipv4 = args.ipv4,
                                               serverType = srv.get_server_type(serverLabel = serverLabel),
                                               searchTerms = args.terms,
                                               verbose = args.verbose)

            print(f'{color.CRED2}Error: {color.CYELLOW}{args.ipv4}{color.CEND} ' + \
                    f'is not registered as either a Plex or Worker server!')

        else:
            # show_all_matched_titles(searchTerms = args.terms, verbose = args.verbose)
            show_all_matched_titles_multiserver(searchTerms = args.terms,
                                                verbose = args.verbose)

    except Exception as e:
        exception_details(e, "Search Plex/Worker Server(s) CLI")

# ------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------

