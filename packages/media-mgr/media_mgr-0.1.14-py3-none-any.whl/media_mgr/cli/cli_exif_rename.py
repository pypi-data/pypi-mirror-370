#!/usr/bin/env python3
# ------------------------------------------------------------------------------------------------------
# -- CLI Methods for EXIF rename
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

from media_mgr.exif_rename import show_path_info, show_exif_info, get_exif_datetime_original
from media_mgr.exif_rename import rename_all_jpg_in_path_to_exif_dates
from media_mgr.exif_rename import rename_all_jpg_in_all_sub_paths_to_exif_dates

# ------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------

def cli():
    try:
        parser = argparse.ArgumentParser(
                    description=f'{"-." * 3}  {color.CYELLOW2}EXIF Rename {color.CEND}for media manager',
                    epilog='-.' * 40)

        parser.add_argument('--version', action="store_true", help='top-level package version')

        subparsers = parser.add_subparsers(dest='cmd')

        p_showPathInfo = subparsers.add_parser('path.info', help='Show path info')
        p_showPathInfo.add_argument("pathToFile", metavar='<path>',
                help='Full path to JPG file').completer = EnvironCompleter

        p_showExifInfo = subparsers.add_parser('exif.info', help='Show EXIF info')
        p_showExifInfo.add_argument("pathToFile", metavar='<path>',
                help='Full path to JPG file').completer = EnvironCompleter

        p_getExifDateTimeOrig = subparsers.add_parser('get.datetime', help='Get EXIF date/time original')
        p_getExifDateTimeOrig.add_argument("pathToFile", metavar='<path>',
                help='Full path to JPG file').completer = EnvironCompleter

        p_renameAllInPathToExif = subparsers.add_parser('to.exif.path', help='Rename all in path to EXIF')
        p_renameAllInPathToExif.add_argument("pathToFolder", metavar='<path>',
                help='Full path to JPG file folder').completer = EnvironCompleter

        p_renameAllInSubPathsToExif = subparsers.add_parser('all.to.exif',
                help='Rename all in path recursive to EXIF')
        p_renameAllInSubPathsToExif.add_argument("pathToRootFolder", metavar='<path>',
                help='Full path to JPG root folder').completer = EnvironCompleter

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

        if args.cmd == 'path.info':
            show_path_info(fullPathToFile = args.pathToFile)

        elif args.cmd == 'exif.info':
            show_exif_info(fullPathToFile = args.pathToFile)

        elif args.cmd == 'get.datetime':
            print(get_exif_datetime_original(fullPathToFile = args.pathToFile))

        elif args.cmd == 'to.exif.path':
            rename_all_jpg_in_path_to_exif_dates(pathToJpgs = args.pathToFolder)

        elif args.cmd == 'all.to.exif':
            rename_all_jpg_in_all_sub_paths_to_exif_dates(rootPath = args.pathToRootFolder)

    except Exception as e:
        exception_details(e, "EXIF File Rename CLI")

# ------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------

