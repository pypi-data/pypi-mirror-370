#!/usr/bin/env python3
# ------------------------------------------------------------------------------------------------------
# -- CLI for Media Config
# ------------------------------------------------------------------------------------------------------
# ======================================================================================================

# PYTHON_ARGCOMPLETE_OK
import argcomplete, argparse

import json
import os
import sys

from quickcolor.color_def import color
from showexception.showexception import exception_details

from media_mgr.media_cfg import MediaConfig, mediaCategoryLkup, colorTypeLkup

# ------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------

def cli():
    try:
        preParsingMc = MediaConfig()

        parser = argparse.ArgumentParser(
                    description=f'{"-." * 3}  {color.CBLUE2}Media {color.CYELLOW2}Manager {color.CEND}configuration',
                    epilog='-.' * 40)

        parser.add_argument('--version', action="store_true", help='top-level package version')

        parser.add_argument('-v', '--verbose', action="store_true",
                            help='run with verbosity hooks enabled')

        subparsers = parser.add_subparsers(dest='cmd')

        p_regMediaCfg = subparsers.add_parser('reg', help='Register media label, category and color')
        p_regMediaCfg.add_argument('label', metavar='<label>', help='Media type label')
        p_regMediaCfg.add_argument('category', metavar='<category>',
                choices=mediaCategoryLkup.keys(), help='Media category')
        p_regMediaCfg.add_argument('dirColor', metavar='<dir-color>',
                choices=colorTypeLkup.keys(), help='Directory color')

        p_unregMediaCfg = subparsers.add_parser('unreg', help='Unregister specified media config')
        p_unregMediaCfg.add_argument('label', metavar='<existing.label>',
                choices=preParsingMc.get_configured_entries(), help='Media type label')

        p_showCfgLabels = subparsers.add_parser('show.labels', help='Show configured labels')

        p_getColorLabel = subparsers.add_parser('get.color.label', help='Get configured colorized label')
        p_getColorLabel.add_argument('label', metavar='<label>',
                choices=preParsingMc.get_configured_entries(), help='Media type label')

        argcomplete.autocomplete(parser)
        args = parser.parse_args()
        # print(args)

        mc = MediaConfig()

        if len(sys.argv) == 1:
            mc.show_media_config()
            sys.exit(1)

        if args.version:
            from importlib.metadata import version
            import media_mgr
            print(f'{color.CGREEN}{os.path.basename(sys.argv[0])}{color.CEND} resides in package ' + \
                    f'{color.CBLUE2}{media_mgr.__package__}{color.CEND} ' + \
                    f'version {color.CVIOLET2}{version("media_mgr")}{color.CEND} ...')
            sys.exit(0)

        if args.cmd == 'reg':
            mc.register_media_category(pathLabel = args.label,
                    category = args.category, dirColor = args.dirColor)
            mc.show_media_config()

        elif args.cmd == 'unreg':
            mc.unregister_media_category(pathLabel = args.label)
            mc.show_media_config()

        elif args.cmd == 'show.labels':
            mc.show_media_config_labels()

        elif args.cmd == 'get.color.label':
            colorLabel, colorCode = mc.get_color_label(pathLabel = args.label)
            print(f'\nThis label should display as ' + \
                    f'{colorCode}{colorLabel}{color.CEND} ...  ' + \
                    f'eg: {colorCode}{args.label}{color.CEND}')

    except Exception as e:
        exception_details(e, "Media Manager - Media Configuration CLI")

# ------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------

