#!/usr/bin/env python3
# ------------------------------------------------------------------------------------------------------
# -- CLI Methods for Moving
# ------------------------------------------------------------------------------------------------------
# ======================================================================================================

# PYTHON_ARGCOMPLETE_OK
import argcomplete, argparse

import json
import os
import sys

from quickcolor.color_def import color
from showexception.showexception import exception_details

from media_mgr.media_cfg import MediaConfig

from media_mgr.mover import move_title, consolidate

# ------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------

def cli_move_plex():
    try:
        preMc = MediaConfig()

        parser = argparse.ArgumentParser(
                    description=f'{"-." * 3}  {color.CYELLOW2}Move {color.CEND}for media manager',
                    epilog='-.' * 40)

        parser.add_argument('--version', action="store_true", help='top-level package version')

        parser.add_argument('-v', '--verbose', action='store_true',
                            help='run with verbosity hooks enabled')

        parser.add_argument('--ipv4', default=None, metavar='<ipv4.addr>', help='Server IPV4')
        parser.add_argument('--test', action='store_true', help='Test move operation')

        parser.add_argument('from_basedir', metavar='<from.dir>',
                choices=preMc.get_configured_entries(), help='FROM base directory name')
        parser.add_argument('to_basedir', metavar='<to.dir>',
                choices=preMc.get_configured_entries(), help='TO base directory name')
        parser.add_argument("terms", metavar='<term_1> .. <term_n>',
                nargs=argparse.REMAINDER, help='search terms for move operation')

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

        move_title(ipv4 = args.ipv4, searchTerms = args.terms,
                fromBaseDir = args.from_basedir,
                toBaseDir = args.to_basedir,
                testMove = args.test,
                verbose = args.verbose)

    except Exception as e:
        exception_details(e, "Plex Media Relocation CLI")

# ------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------

def cli_consolidate():
    try:
        parser = argparse.ArgumentParser(
                    description=f'{"-." * 3}  {color.CYELLOW2}Media Consolidator {color.CEND}for media manager',
                    epilog='-.' * 40)

        parser.add_argument('--version', action="store_true", help='top-level package version')

        parser.add_argument('-v', '--verbose', action='store_true',
                            help='run with verbosity hooks enabled')

        parser.add_argument('--mediatype', default='mkv',
                            choices=['mkv', 'mp4', 'mov'], help='Media type (extensions)')
        parser.add_argument('--test', action='store_true', help='Test consolidate operation')

        parser.add_argument('ipv4', metavar='<ipv4.addr>', help='Server IPV4')
        parser.add_argument('rootAbsPath', metavar='<absolute.root.path>',
                help='top level directory from which to scan folders with media to consolidate')
        parser.add_argument('targetFolder', metavar='<tgt.folder.name>',
                help='Consolidation target folder name or \'.\'')

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

        consolidate(ipv4 = args.ipv4, rootAbsPath = args.rootAbsPath,
                    targetFolder = args.targetFolder,
                    mediaType = args.mediatype, testConsolidation = args.test,
                    verbose = args.verbose)

    except Exception as e:
        exception_details(e, "Plex Media Consolidation CLI")

# ------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------

