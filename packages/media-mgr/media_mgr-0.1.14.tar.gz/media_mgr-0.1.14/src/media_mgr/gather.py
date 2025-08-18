#!/usr/bin/env python3
# ------------------------------------------------------------------------------------------------------
# -- Media Gathering Routines
# ------------------------------------------------------------------------------------------------------
# ======================================================================================================

from collections import defaultdict

import json
import os
from datetime import datetime

from quickcolor.color_def import color
from quickcolor.color_filter import strip_ansi_esc_sequences_from_string
from delayviewer.stopwatch import Stopwatch, handle_stopwatch

from media_mgr.comms_utility import is_server_active

from media_mgr.media_cfg import MediaConfig
from media_mgr.server_cfg import ServerConfig

from media_mgr.paths_and_drives import get_filtered_media_paths
from media_mgr.search import get_num_titles, extract_search_path_collection

# ------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------

def get_all_items_in_search_paths(ipv4 = None,
                                  serverType = 'plex',
                                  searchPathList = None,
                                  verbose: bool = False):
    if not searchPathList:
        searchPathList = get_filtered_media_paths(ipv4 = ipv4, serverType = serverType)

    cmd =''
    for path in searchPathList:
        # note - returned ls output always starts with a total <size> line -- the grep -wv removes it
        cmd += f'echo \"Drive.path: {path}\" ; ls --size -h {path} | grep -wv \"^total\" ; '

    # retrieve a dictionary list (titles by paths) unfiltered
    return extract_search_path_collection(ipv4 = ipv4,
                                          cmd = cmd,
                                          getAllGroups = True,
                                          verbose = verbose)

# ------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------

def sort_retrieved_items_by_type(collection, verbose: bool = False):
    sortedCollection = defaultdict(list)

    for path in collection:
        label = os.path.basename(path)
        driveName = os.path.basename(os.path.dirname(path))
        if collection[path]:
            modifiedCollection = []
            for entry in collection[path]:
                size, _, title = entry.lstrip().partition(' ')
                sortEntry = {}
                sortEntry['size'] = size
                sortEntry['drive'] = driveName
                sortEntry['title'] = title
                modifiedCollection.append(sortEntry)

            sortedCollection[label] += modifiedCollection

    if verbose:
        # print(json.dumps(sortedCollection, indent=4))
        pass

    for label in sortedCollection:
        sortedCollection[label] = sorted(sortedCollection[label], key=lambda x: x['title'])

    if verbose:
        # print(json.dumps(sortedCollection, indent=4))
        pass

    return sortedCollection

# ------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------

def get_sorted_title_bundles(ipv4 = None, serverType = 'plex', verbose: bool = False):
    try:
        retrievedTitles = get_all_items_in_search_paths(ipv4 = ipv4,
                                                        serverType = serverType,
                                                        verbose = verbose)

    except Exception as e:
        print(f'{color.CRED2}-- Processing error: Sorted title bundle retrieval ' + \
                f'aborted for items on {color.CWHITE2}{ipv4}{color.CRED2} and ' + \
                f'server type {color.CWHITE}{serverType}\n' + \
                f'{color.CRED2}   Investigate {color.CWHITE}{ipv4}{color.CRED2}' + \
                f'for problems with drive mounts!{color.CEND}')
        return None

    if not retrievedTitles:
        location = str(ipv4) if ipv4 else 'local machine'
        print(f'\n{color.CRED2}-- Did not find any titles in any search path on {color.CYELLOW}{location}{color.CEND}')
        return None

    if verbose:
        # print(json.dumps(retrievedTitles, indent=4))
        pass

    return sort_retrieved_items_by_type(retrievedTitles, verbose = verbose)

# ------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------

def show_retrieved_titles(ipv4 = None, serverType = 'plex', verbose: bool = False):
    if not is_server_active(ipv4 = ipv4):
        print(f'\n{color.CWHITE2}-- Warning: {color.CRED2}Could not reach server ' + \
                f'{color.CYELLOW}{ipv4}{color.CRED2} -- it is dead!{color.CEND}')
        return

    retrievedTitles = []
    try:
        retrievedTitles = get_all_items_in_search_paths(ipv4 = ipv4,
                                                        serverType = serverType,
                                                        verbose = verbose)

        if verbose:
            # print(json.dumps(retrievedTitles, indent = 4))
            pass

    except Exception as e:
        print(f'{color.CRED2}-- Processing error: Title retrieval aborted for items on' + \
                f'{color.CWHITE}{ipv4}{color.CRED2} and server type {color.CWHITE}{serverType}\n' + \
                f'{color.CRED2}   Investigate {color.CWHITE}{ipv4}{color.CRED2} for problems ' + \
                f'with drive mounts!{color.CEND}')
        return

    if not retrievedTitles:
        location = str(ipv4) if ipv4 else "local machine"
        print(f"\n{colors.fg.red}-- Did not find any titles in any search path on {colors.fg.yellow}{location}{colors.off}")
        return

    mc = MediaConfig()

    location = str(ipv4) if ipv4 else "local machine"
    print(f'{color.CGREEN}-- Found {color.CWHITE}{get_num_titles(retrievedTitles)} ' + \
            f'{color.CGREEN}total titles on {color.CWHITE}{location}{color.CEND}')

    numTitles = 0
    for pathIdx, path in enumerate(retrievedTitles):
        _, colorCode = mc.get_color_label(os.path.basename(path))
        colorCode = colorCode if colorCode else color.CVIOLET

        if verbose:
            # print(json.dumps(retrievedTitles[path], indent=4))
            pass

        print(color.CRED2)
        print('- ' * 60)
        print(color.CEND)
        for titleIdx, entry in enumerate(retrievedTitles[path]):
            size, _, title = entry.lstrip().partition(' ')
            numTitles += 1
            print(f'{color.CVIOLET}{pathIdx:>3}-{titleIdx:<4} - {color.CWHITE}' + \
                    f'{numTitles:>3}. {colorCode}{path}/{title} {color.CWHITE2}({size}){color.CEND}')
        # input("Press enter to continue...")

# ------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------

def show_all_retrieved_titles():
    sc = ServerConfig()

    for name, serverCfg in sc.get_server_list():
        show_retrieved_titles(ipv4 = serverCfg['ipv4'], serverType = serverCfg['serverType'])

        print('-' * 120)

# ------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------

def get_header_in_collection(area, numTitlesInArea):
    header = f'\n{color.CRED2}'
    header += '- ' * 60

    if numTitlesInArea > 1:
        header += f'\n{color.CGREEN}-- There are {color.CWHITE}{numTitlesInArea} {color.CGREEN}titles in the'
    else:
        header += f'\n{color.CGREEN}-- There is {color.CWHITE}{numTitlesInArea} {color.CGREEN}title in the'

    return f'{header} {color.CYELLOW}{area} {color.CGREEN}area{color.CEND}\n'

# ------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------

@handle_stopwatch
def show_title_bundles(ipv4 = None, serverType = 'plex', stopwatch = None, verbose: bool = False):
    print()
    stopwatch.start(f'{color.CBLUE2}-- Bundle retrieval in progress ...{color.CEND}')
    sortedCollection = get_sorted_title_bundles(ipv4 = ipv4,
                                                serverType = serverType,
                                                verbose = verbose)
    if not sortedCollection:
        stopwatch.stop(f'{color.CRED2}Error in sorted collection retrieval!{color.CEND}')
        return
    stopwatch.stop()

    if verbose:
        # print(json.dumps(sortedCollection, indent = 4))
        pass

    mc = MediaConfig()

    for label in sortedCollection:
        print(get_header_in_collection(area = label,
                                       numTitlesInArea = len(sortedCollection[label])))

        _, colorCode = mc.get_color_label(label)
        colorCode = colorCode if colorCode else color.CRED

        numTitles = 0
        for entry in sortedCollection[label]:
            numTitles += 1
            print(f'{color.CWHITE}{numTitles:>3}. {colorCode}{entry["title"]} ' + \
                    f'{color.CWHITE2}({entry["size"]}){color.CEND} -- {entry["drive"]}')

    print('=' * 120)

# ------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------

@handle_stopwatch
def store_title_bundles(ipv4 = None,
                        serverType = 'plex',
                        storePath = None,
                        verbose: bool = False,
                        stopwatch = None):
    print()
    stopwatch.start(f'{color.CBLUE2}-- Bundle retrieval in progress ...{color.CEND}')
    sortedCollection = get_sorted_title_bundles(ipv4 = ipv4,
                                                serverType = serverType,
                                                verbose = verbose)
    if not sortedCollection:
        stopwatch.stop(f'{color.CRED2}Error in sorted collection retrieval!{color.CEND}')
        return
    stopwatch.stop()

    print(f'{color.CBLUE2}-- Retrieved title bundles from {color.CWHITE}{ipv4}{color.CBLUE2} ', end='', flush=True)

    mc = MediaConfig()

    if not storePath:
        storePath = '/tmp'
    elif not os.path.isdir(storePath):
        storePath = '/tmp'

    fullBundlePath = f'{storePath}/title_bundles_{datetime.now().strftime("%Y-%m-%d_%H_%M_%S")}.txt'
    with open(fullBundlePath, "w") as fileHandle:

        for label in sortedCollection:
            fileHandle.write(strip_ansi_esc_sequences_from_string(get_header_in_collection(area = label,
                numTitlesInArea = len(sortedCollection[label]))) + '\n')

            for idx, entry in enumerate(sortedCollection[label]):
                fileHandle.write(f'{idx+1:>3}. {entry["title"]} -- {entry["size"]} -- {entry["drive"]}\n')

            fileHandle.write('\n')

    print(f'{color.CBLUE2}and storing to {color.CWHITE}{fullBundlePath}{color.CEND}')

# ------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------

@handle_stopwatch
def store_title_bundles_plex_and_worker(ipv4Plex = None, ipv4Worker = None,
        storePath = None, stopwatch = None):

    print()
    stopwatch.start(f'{color.CBLUE2}-- Plex bundle retrieval in progress ...{color.CEND}')
    sortedCollection_Plex = get_sorted_title_bundles(ipv4 = ipv4Plex, serverType = 'plex')
    if not sortedCollection_Plex:
        stopwatch.stop(f'{color.CRED2}Error in retrieval!{color.CEND}')
        return
    stopwatch.stop()

    stopwatch.start(f'{color.CBLUE2}-- Worker bundle retrieval in progress ...{color.CEND}')
    sortedCollection_Worker = get_sorted_title_bundles(ipv4 = ipv4Worker, serverType = 'worker')
    if not sortedCollection_Worker:
        stopwatch.stop(f'{color.CRED2}Error in retrieval!{color.CEND}')
        return
    stopwatch.stop()

    print(f'{color.CBLUE2}-- Retrieved title bundles from {color.CWHITE}' + \
            f'{ipv4Plex}{color.CBLUE2} and {color.CWHITE}{ipv4Worker}' + \
            f'{color.CBLUE2} ', end='', flush=True)

    mc = MediaConfig()

    if not storePath:
        storePath = '/tmp'
    elif not os.path.isdir(storePath):
        storePath = '/tmp'

    sortedCollection = sortedCollection_Plex | sortedCollection_Worker

    fullBundlePath = f'{storePath}/title_bundles_{datetime.now().strftime("%Y-%m-%d_%H_%M_%S")}.txt'
    with open(fullBundlePath, "w") as fileHandle:
        for label in sortedCollection:
            fileHandle.write(strip_ansi_esc_sequences_from_string(get_header_in_collection(area = label,
                numTitlesInArea = len(sortedCollection[label]))) + "\n")

            for idx, entry in enumerate(sortedCollection[label]):
                fileHandle.write(f'{idx+1:>3}. {entry["title"]} -- {entry["size"]} -- {entry["drive"]}\n')

            fileHandle.write('\n')

    print(f'{color.CBLUE2}and storing to {color.CWHITE}{fullBundlePath}{color.CEND}')

# ------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------

