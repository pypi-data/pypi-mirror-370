#!/usr/bin/env python3
# ------------------------------------------------------------------------------------------------------
# -- CLI for Server Config
# ------------------------------------------------------------------------------------------------------
# ======================================================================================================

# PYTHON_ARGCOMPLETE_OK
import argcomplete, argparse

import json
import os
import sys

from quickcolor.color_def import color
from showexception.showexception import exception_details

from media_mgr.server_cfg import ServerConfig, serverTypeLkup

# ------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------

def cli():
    try:
        preParsingSc = ServerConfig()

        parser = argparse.ArgumentParser(
                    description=f'{"-." * 3}  {color.CBLUE2}Media {color.CYELLOW2}Server {color.CEND}configuration',
                    epilog='-.' * 40)

        parser.add_argument('--version', action="store_true", help='top-level package version')

        parser.add_argument('-v', '--verbose', action="store_true",
                            help='run with verbosity hooks enabled')

        subparsers = parser.add_subparsers(dest='cmd')

        p_regServerCfg = subparsers.add_parser('reg', help='Register server label, ipv4 and type')
        p_regServerCfg.add_argument('label', metavar='<label>', help='Media server label')
        p_regServerCfg.add_argument('ipv4', metavar='<ipv4-addr>', help='IPV4 address for the server')
        p_regServerCfg.add_argument('type', metavar='<server-type>',
                choices=serverTypeLkup.keys(), help='Media server type')

        p_unregServerCfg = subparsers.add_parser('unreg', help='Unregister specified media server')
        p_unregServerCfg.add_argument('label', metavar='<existing.label>',
                choices=preParsingSc.get_server_name_list(), help='Media server label')

        p_showCfgLabels = subparsers.add_parser('show.labels', help='Show configured labels')

        p_getSrvLabels = subparsers.add_parser('get.srv.labels', help='Debug - get configured server labels')

        p_getSrvInfo = subparsers.add_parser('get.srv.cfg', help='Debug - get server configs')

        argcomplete.autocomplete(parser)
        args = parser.parse_args()
        # print(args)

        sc = ServerConfig()

        if len(sys.argv) == 1:
            sc.show_server_config()
            sys.exit(1)

        if args.version:
            from importlib.metadata import version
            import media_mgr
            print(f'{color.CGREEN}{os.path.basename(sys.argv[0])}{color.CEND} resides in package ' + \
                    f'{color.CBLUE2}{media_mgr.__package__}{color.CEND} ' + \
                    f'version {color.CVIOLET2}{version("media_mgr")}{color.CEND} ...')
            sys.exit(0)

        if args.cmd == 'reg':
            sc.register_server(serverName = args.label,
                    ipv4 = args.ipv4, serverType = args.type)
            sc.show_server_config()

        elif args.cmd == 'unreg':
            sc.unregister_server(serverName = args.label)
            sc.show_server_config()

        elif args.cmd == 'show.labels':
            sc.show_server_config_labels()

        elif args.cmd == 'get.srv.labels':
            print(sc.get_server_name_list())

        elif args.cmd == 'get.srv.cfg':
            print(sc.get_server_list())

    except Exception as e:
        exception_details(e, "Media Manager - Server Configuration CLI")

# ------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------

