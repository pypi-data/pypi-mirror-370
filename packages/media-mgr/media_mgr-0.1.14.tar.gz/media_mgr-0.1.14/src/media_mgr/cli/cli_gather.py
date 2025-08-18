#!/usr/bin/env python3
# ------------------------------------------------------------------------------------------------------
# -- CLI Methods for Gathering
# ------------------------------------------------------------------------------------------------------
# ======================================================================================================

# PYTHON_ARGCOMPLETE_OK
import argcomplete, argparse

import json
import os
import sys

from quickcolor.color_def import color
from showexception.showexception import exception_details

from media_mgr.server_cfg import get_available_server_types

from media_mgr.gather import show_retrieved_titles, show_all_retrieved_titles
from media_mgr.gather import show_title_bundles, store_title_bundles
from media_mgr.gather import store_title_bundles_plex_and_worker

# ------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------

def cli():
    try:
        parser = argparse.ArgumentParser(
                    description=f'{"-." * 3}  {color.CYELLOW2}Gathering {color.CEND}for media manager',
                    epilog='-.' * 40)

        parser.add_argument('-v', '--verbose', action='store_true',
                            help='run with verbosity hooks enabled')

        parser.add_argument('--version', action="store_true", help='top-level package version')

        sp = parser.add_subparsers(dest='cmd')

        sp_showRetrievedTitles = sp.add_parser('show.titles', help='Show retrieved titles')
        sp_showRetrievedTitles.add_argument('ipv4', metavar='<ipv4.addr>', help='Server IPV4')
        sp_showRetrievedTitles.add_argument('--type', choices=get_available_server_types(),
                default='plex', metavar='<server.type>', help='Server type')

        sp_showAllRetrievedTitles = sp.add_parser('show.all.titles', help='Show ALL retrieved titles')

        sp_showTitleBundles = sp.add_parser('show.bundles', help='Show title bundles')
        sp_showTitleBundles.add_argument('ipv4', metavar='<ipv4.addr>', help='Server IPV4')
        sp_showTitleBundles.add_argument('--type', choices=get_available_server_types(),
                default='plex', metavar='<server.type>', help='Server type')

        sp_storeTitleBundles = sp.add_parser('store.bundles', help='Store title bundles')
        sp_storeTitleBundles.add_argument('ipv4', metavar='<ipv4.addr>', help='Server IPV4')
        sp_storeTitleBundles.add_argument('--type', choices=get_available_server_types(),
                default='plex', metavar='<server.type>', help='Server type')
        sp_storeTitleBundles.add_argument('--path',
                default=None, metavar='<store.file.path>', help='Store file path')

        sp_showTitleBundlesPlexWorker = sp.add_parser('show.plex.n.worker.bundles',
                help='Show title bundles for Plex and Worker servers')
        sp_showTitleBundlesPlexWorker.add_argument('ipv4_plex',
                metavar='<ipv4.addr.plex.srvr>', help='Plex Server IPV4')
        sp_showTitleBundlesPlexWorker.add_argument('ipv4_worker',
                metavar='<ipv4.addr.worker.srvr>', help='Worker Server IPV4')

        sp_storeTitleBundlesPlexWorker = sp.add_parser('store.plex.n.worker.bundles',
                help='Store title bundles for Plex and Worker servers')
        sp_storeTitleBundlesPlexWorker.add_argument('ipv4_plex',
                metavar='<ipv4.addr.plex.srvr>', help='Plex Server IPV4')
        sp_storeTitleBundlesPlexWorker.add_argument('ipv4_worker',
                metavar='<ipv4.addr.worker.srvr>', help='Worker Server IPV4')
        sp_storeTitleBundlesPlexWorker.add_argument('--path',
                default=None, metavar='<store.file.path>', help='Store file path')

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

        if args.cmd == 'show.titles':
            show_retrieved_titles(ipv4 = args.ipv4,
                                  serverType = args.type,
                                  verbose = args.verbose)

        elif args.cmd == 'show.all.titles':
            show_all_retrieved_titles()

        elif args.cmd == 'show.bundles':
            show_title_bundles(ipv4 = args.ipv4,
                               serverType = args.type,
                               verbose = args.verbose)

        elif args.cmd == 'store.bundles':
            store_title_bundles(ipv4 = args.ipv4,
                                serverType = args.type,
                                storePath = args.path,
                                verbose = args.verbose)

        elif args.cmd == 'show.plex.n.worker.bundles':
            show_title_bundles(ipv4 = args.ipv4_plex, serverType = 'plex')
            show_title_bundles(ipv4 = args.ipv4_worker, serverType = 'worker')

        elif args.cmd == 'store.plex.n.worker.bundles':
            store_title_bundles_plex_and_worker(ipv4Plex = args.ipv4_plex,
                    ipv4Worker = args.ipv4_worker, storePath = args.path)

    except Exception as e:
        exception_details(e, "Media Title Gathering CLI")

# ------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------

