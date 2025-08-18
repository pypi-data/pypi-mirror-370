#!/usr/bin/env python3
# ------------------------------------------------------------------------------------------------------
# -- Search Methods
# ------------------------------------------------------------------------------------------------------
# ======================================================================================================

from collections import defaultdict

import subprocess
import json
import os
import re

from delayviewer.spinner import handle_spinner
from delayviewer.time_and_delay import time_execution
from quickcolor.color_def import color
from showexception.showexception import exception_details

from media_mgr.comms_utility import run_cmd, is_server_active, group_list
from media_mgr.comms_utility import run_ssh_cmd_via_asyncio
from media_mgr.comms_utility import run_ssh_cmds_via_asyncio

from media_mgr.media_cfg import MediaConfig
from media_mgr.server_cfg import ServerConfig

from media_mgr.paths_and_drives import get_filtered_media_paths, get_filtered_media_paths_multiserver

# ------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------
# 2025-0201
# Search for titles in search path lists on servers
# - search is performed with run_cmd / subprocess via ssh
# - search contents are retrieved in lists for display
# - only search titles matching regex are returned
# ------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------

# @time_execution
def extract_search_path_collection(ipv4: str | None = None,
                                   cmd: str | None = None,
                                   getAllGroups: bool = False,
                                   shell: bool = False,
                                   verbose: bool = False):
    collection = defaultdict(list)

    cmdOutput = run_cmd(ipv4, cmd, shell = shell)
    if isinstance(cmdOutput, subprocess.CompletedProcess):
        if cmdOutput.returncode:
            raise ValueError(f'Warning: Problem retrieving command output!')

    if verbose:
        # print(json.dumps(cmdOutput,indent=4))
        pass

    medium = list(group_list(cmdOutput, 'Drive.path: '))
    if verbose:
        # print(json.dumps(medium,indent=4))
        pass

    for drivePathContents in medium:
        if not drivePathContents:
            continue
        groupId, groupContents = drivePathContents[:1], drivePathContents[1:]
        groupIdStr=''
        for groupIdElement in groupId:
            groupIdStr += groupIdElement

        if not groupIdStr:
            continue
        dumpIt, groupLabel = groupIdStr.split(' ')
        if groupContents or getAllGroups:
            collection[groupLabel] = groupContents

    return collection

# ------------------------------------------------------------------------------------------------------

def extract_search_path_collection_multiserver(remoteCmdPerIpv4: dict | None = None,
                                               getAllGroups: bool = False,
                                               shell: bool = False,
                                               verbose: bool = False):

    multiServerCollections = {}
    for ipv4, cmdOutput in run_ssh_cmds_via_asyncio(remoteCmdPerIpv4, evalExitStatus = False):
        if verbose:
            # print(json.dumps(cmdOutput,indent=4))
            pass

        collection = defaultdict(list)

        medium = list(group_list(cmdOutput, 'Drive.path: '))
        if verbose:
            # print(json.dumps(medium,indent=4))
            pass

        for drivePathContents in medium:
            if not drivePathContents:
                continue
            groupId, groupContents = drivePathContents[:1], drivePathContents[1:]
            groupIdStr=''
            for groupIdElement in groupId:
                groupIdStr += groupIdElement

            if not groupIdStr:
                continue
            groupLabel = groupIdStr.removeprefix('Drive.path: ')
            if groupContents or getAllGroups:
                collection[groupLabel] = groupContents

            multiServerCollections[ipv4] = collection

            '''
            #
            # 2025-0816 -- ancient way of extracting path
            #
            splitItems = groupIdStr.split(' ')
            try:
                # _, groupLabel = splitItems
                if groupContents or getAllGroups:
                    collection[groupLabel] = groupContents

                multiServerCollections[ipv4] = collection

            except:
                print(f'{color.CBLUE2}Split Items{color.CEND} for -->{groupIdStr}<--')
                for item in splitItems:
                    print(f' -- {item} --')
                sec = input('Press a key to continue ...')
            '''

    return multiServerCollections

# ------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------

def get_matching_items_in_search_paths(ipv4: str | None = None,
                                       searchPathList: list | None = None,
                                       searchTerms : list | None = None,
                                       verbose: bool = False):
    searchRegex = ''
    for term in searchTerms:
        searchRegex += term + '.*'

    if verbose:
        '''
        print(json.dumps(searchPathList, indent = 4))
        print(f'{searchRegex=}')
        '''
        pass

    cmd = ''
    for path in searchPathList:
        cmd += f'echo \"Drive.path: {path}\" ; ls --size -h {path} | grep -i \'{searchRegex}\' ; '

    return extract_search_path_collection(ipv4 = ipv4, cmd = cmd, shell = True, verbose = verbose)

# ------------------------------------------------------------------------------------------------------

def get_matching_items_in_search_paths_multiserver(multiserverSearchPathLists: list | None = None,
                                                   searchTerms : list | None = None,
                                                   verbose: bool = False):
    searchRegex = ''
    for term in searchTerms:
        searchRegex += term + '.*'

    if verbose:
        '''
        print(json.dumps(searchPathDict, indent = 4))
        print(f'{searchRegex=}')
        '''
        pass

    cmdPerIpv4 = {}
    for ipv4, searchPathList in multiserverSearchPathLists:
        cmd = ''
        for path in searchPathList:
            cmd += f'echo \"Drive.path: {path}\" ; ls --size -h \"{path}\" | grep -i \'{searchRegex}\' ; '
        cmdPerIpv4[ipv4] = cmd

    if verbose:
        print(f'{color.CRED} -- Begin Cmds Per IPV4 List -- {color.CEND}')
        for ipv4, cmdset in cmdPerIpv4.items():
            print(f" -- IPV4: {ipv4}")
            for sliver in cmdset.split(';'):
                print(f" .... {sliver}")
        # print(json.dumps(cmdPerIpv4, indent=4))
        print(f'{color.CRED} -- End Cmds Per IPV4 List -- {color.CEND}')
        pass

    return extract_search_path_collection_multiserver(remoteCmdPerIpv4 = cmdPerIpv4, shell = True, verbose = verbose)


# ------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------

# @time_execution
def find_items_in_search_paths(ipv4: str | None = None,
                               serverType = 'plex',
                               searchPathList: list | None = None,
                               searchTerms: list | None = None,
                               verbose: bool = False):
    if ipv4:
        if not is_server_active(ipv4 = ipv4):
            return defaultdict(list)

    if not searchPathList:
        searchPathList = get_filtered_media_paths(ipv4 = ipv4, serverType = serverType)

    if verbose:
        print(f'{color.CRED} -- Begin Search Path List -- {color.CEND}')
        print(json.dumps(searchPathList,indent=4))
        print(f'{color.CRED} -- End Search Path List -- {color.CEND}')
        pass

    collection = get_matching_items_in_search_paths(ipv4 = ipv4,
                                                    searchPathList = searchPathList,
                                                    searchTerms = searchTerms,
                                                    verbose = verbose)
    if verbose:
        '''
        print(f'{color.CRED} -- Begin Collection -- {color.CEND}')
        print(json.dumps(collection,indent=4))
        print(f'{color.CRED} -- End Collection -- {color.CEND}')
        '''
        pass

    # create a matched dictionary list (titles by paths)
    # filtering paths with matching titles (no empty paths)
    matchedTitles = defaultdict(list)
    for path in collection:
        if collection[path]:
            for item in collection[path]:
                size, _, title = item.lstrip().partition(' ')
                entry = {}
                entry['size'] = size
                entry['title'] = title
                matchedTitles[path].append(entry)

    if verbose:
        '''
        print(f'{color.CRED} -- Begin MatchedTitles -- {color.CEND}')
        print(json.dumps(matchedTitles,indent=4))
        print(f'{color.CRED} -- End MatchedTitles -- {color.CEND}')
        '''
        pass

    return matchedTitles

# ------------------------------------------------------------------------------------------------------

def find_items_in_search_paths_multiserver(searchTerms: list | None = None,
                                           verbose: bool = False):

    multiserverSearchPathLists = get_filtered_media_paths_multiserver()

    if verbose:
        print(f'{color.CRED} -- Begin Multi-Server Search Path List -- {color.CEND}')
        print(json.dumps(multiserverSearchPathLists, indent=4))
        print(f'{color.CRED} -- End Multi-Server Search Path List -- {color.CEND}')
        pass

    multiserverCollections = get_matching_items_in_search_paths_multiserver(multiserverSearchPathLists = multiserverSearchPathLists,
                                                                            searchTerms = searchTerms,
                                                                            verbose = verbose)
    if verbose:
        '''
        print(f'{color.CRED} -- Begin Multi-Server Collection -- {color.CEND}')
        print(json.dumps(multiserverCollections, indent=4))
        print(f'{color.CRED} -- End Multi-Server Collection -- {color.CEND}')
        '''
        pass

    matchedTitlesPerIpv4 = {}
    for ipv4, collection in multiserverCollections.items():
        # create a matched dictionary list (titles by paths)
        # filtering paths with matching titles (no empty paths)
        matchedTitles = defaultdict(list)
        for path in collection:
            if collection[path]:
                for item in collection[path]:
                    size, _, title = item.lstrip().partition(' ')
                    entry = {}
                    entry['size'] = size
                    entry['title'] = title
                    matchedTitles[path].append(entry)

        matchedTitlesPerIpv4[ipv4] = matchedTitles

    if verbose:
        '''
        print(f'{color.CRED} -- Begin Multi-Server MatchedTitles -- {color.CEND}')
        print(json.dumps(matchedTitlesPerIpv4, indent=4))
        print(f'{color.CRED} -- End Multi-Server MatchedTitles -- {color.CEND}')
        '''
        pass

    return matchedTitlesPerIpv4

# ------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------

def get_all_items_in_paths(ipv4: str | None = None,
                           pathList: list | None = None,
                           verbose: bool = False):
    cmd = ''
    for path in pathList:
        cmd += f'echo \"Drive.path: {path}\" ; ls --size -h {path} ; '

    collection = extract_search_path_collection(ipv4 = ipv4, cmd = cmd, shell = True, verbose = verbose)

    organizedTitles = defaultdict(list)
    for path in collection:
        if collection[path]:
            for item in collection[path]:
                size, _, title = item.lstrip().partition(' ')
                if size == 'total':
                    continue
                entry = {}
                entry['size'] = size
                entry['title'] = title
                organizedTitles[path].append(entry)

    if verbose:
        '''
        print(f'{color.CRED} -- Begin OrganizedTitles -- {color.CEND}')
        print(json.dumps(organizedTitles,indent=4))
        print(f'{color.CRED} -- End OrganizedTitles -- {color.CEND}')
        '''
        pass

    return organizedTitles

# ------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------

# @time_execution
def grab_all_titles_in_paths(ipv4: str | None = None,
                             serverType = 'plex',
                             pathList: list | None = None,
                             verbose: bool = False):

    if ipv4:
        if not is_server_active(ipv4 = ipv4):
            return defaultdict(list)

    filteredPathList = get_filtered_media_paths(ipv4 = ipv4, serverType = serverType, lookingFor = pathList)

    foundTitles = get_all_items_in_paths(ipv4 = ipv4, pathList = filteredPathList, verbose = verbose)

    if verbose:
        '''
        print(f'{color.CRED} -- Begin FoundTitles -- {color.CEND}')
        print(json.dumps(foundTitles,indent=4))
        print(f'{color.CRED} -- End FoundTitles -- {color.CEND}')
        '''
        pass

    return foundTitles

# ------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------
def get_num_titles(collection = None):
    numTitles = 0
    for path in collection:
        numTitles += len(collection[path])

    return numTitles

# ------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------

def show_titles_in_paths(ipv4: str | None = None,
                         serverType = 'plex',
                         paths: list = [],
                         verbose: bool = False):

    if not len(paths):
        print(f'{color.CRED2}Warning{color.CEND}: No paths specified! Need paths... Need PATHS!!!!')
        return

    location = str(ipv4) if ipv4 else "local machine"

    try:
        allTitles = grab_all_titles_in_paths(ipv4 = ipv4,
                                             serverType = serverType,
                                             pathList = paths,
                                             verbose = verbose)
    except Exception as e:
        print(f'{color.CRED2}-- Processing error: Search aborted for all titles ' + \
                f'in paths on {color.CWHITE}{location}\n' + \
                f'{color.CRED}   Investigate {color.CWHITE}{location}{color.CRED2} ' + \
                f'for problems with drive mounts!{color.CEND}' + \
                f'\n{e}')
        exception_details(e, "organize_titles_in_paths run", raw=True)

        return

    print('')
    print('- ' * 50)

    if not allTitles:
        print(f'{color.CRED2}-- Did not find any titles on {color.CWHITE}{location}{color.CEND}')
        return

    mc = MediaConfig()
    print(f'{color.CGREEN}-- Found {color.CWHITE}{get_num_titles(allTitles)} ' + \
            f'{color.CGREEN}titles on {color.CWHITE}{location}{color.CEND}')

    if verbose:
        print(json.dumps(allTitles, indent = 4))
        return

    numProcessedTitles = 0
    for path in allTitles:
        _, colorCode = mc.get_color_label(os.path.basename(path))
        colorCode = colorCode if colorCode else color.CRED
        for entry in allTitles[path]:
            numProcessedTitles += 1
            print(f'{color.CWHITE}{numProcessedTitles:>3}. {colorCode}{path}/{entry["title"]}{color.CWHITE2} ' + \
                    f'({entry["size"]}){color.CEND}')

# ------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------

def show_matched_titles(ipv4: str | None = None,
                        serverType = 'plex',
                        searchTerms: list = ["the", "duff"],
                        verbose: bool = False):

    location = str(ipv4) if ipv4 else "local machine"

    try:
        matchedTitles = find_items_in_search_paths(ipv4 = ipv4,
                                                   serverType = serverType,
                                                   searchTerms = searchTerms,
                                                   verbose = verbose)

    except Exception as e:
        print(f'{color.CRED2}-- Processing error: Search aborted for titles ' + \
                f'matching {color.CWHITE}--> {color.CYELLOW}{" ".join(searchTerms)}' + \
                f'{color.CWHITE}<-- {color.CRED2}on {color.CWHITE}{location}\n' + \
                f'{color.CRED}   Investigate {color.CWHITE}{location}{color.CRED2} ' + \
                f'for problems with drive mounts!{color.CEND}' + \
                f'\n{e}')
        exception_details(e, "find_item_in_search_paths run", raw=True)

        return

    print('')
    print('- ' * 50)

    if not matchedTitles:
        print(f'{color.CRED2}-- Did not find any titles matching ' + \
                f'{color.CWHITE}--> {color.CYELLOW}{" ".join(searchTerms)} ' + \
                f'{color.CWHITE}<-- {color.CRED2}on {color.CWHITE}{location}{color.CEND}')
        return

    mc = MediaConfig()
    print(f'{color.CGREEN}-- Found {color.CWHITE}{get_num_titles(matchedTitles)} ' + \
            f'{color.CGREEN}titles matching {color.CWHITE}--> {color.CYELLOW}' + \
            f'{" ".join(searchTerms)} {color.CWHITE}<-- {color.CGREEN}on ' + \
            f'{color.CWHITE}{location}{color.CEND}')

    if verbose:
        # print(json.dumps(matchedTitles, indent = 4))
        return

    numMatchingTitles = 0
    for path in matchedTitles:
        _, colorCode = mc.get_color_label(os.path.basename(path))
        colorCode = colorCode if colorCode else color.CRED
        for entry in matchedTitles[path]:
            numMatchingTitles += 1
            print(f'{color.CWHITE}{numMatchingTitles:>3}. {colorCode}{path}/{entry["title"]}{color.CWHITE2} ' + \
                    f'({entry["size"]}){color.CEND}')

# ------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------

@time_execution
def show_all_matched_titles(searchTerms: list | None = None,
                            verbose: bool = False,
                            spinner = None):
    srv = ServerConfig()

    for server in srv.get_server_name_list():
        show_matched_titles(ipv4 = srv.get_server_address(serverLabel = server),
                            serverType = srv.get_server_type(serverLabel = server),
                            searchTerms = searchTerms,
                            verbose = verbose)

# ------------------------------------------------------------------------------------------------------

@handle_spinner
def show_all_matched_titles_multiserver(searchTerms: list | None = None,
                                        verbose: bool = False,
                                        spinner = None):
    try:
        spinner.start(f'\n-- Searching all servers for {color.CYELLOW2}{' '.join(searchTerms)}{color.CEND} ...')
        matchedTitlesPerIpv4 = find_items_in_search_paths_multiserver(searchTerms = searchTerms,
                                                                      verbose = verbose)
        spinner.stop()

    except Exception as e:
        print(f'{color.CRED2}-- Processing error: Search aborted for titles ' + \
                f'matching {color.CWHITE}--> {color.CYELLOW}{" ".join(searchTerms)}' + \
                f'{color.CWHITE}<-- {color.CRED2}on {color.CWHITE}all{color.CRED} servers!\n' + \
                f'{color.CRED}   Investigate {color.CWHITE}servers{color.CRED2} ' + \
                f'for problems with drive mounts!{color.CEND}' + \
                f'\n{e}')
        exception_details(e, "find_item_in_search_paths_multiserver run", raw=True)
        return

    for location, matchedTitles in matchedTitlesPerIpv4.items():
        print('')
        print('- ' * 50)

        if not matchedTitles:
            print(f'{color.CRED2}-- Did not find any titles matching ' + \
                    f'{color.CWHITE}--> {color.CYELLOW}{" ".join(searchTerms)} ' + \
                    f'{color.CWHITE}<-- {color.CRED2}on {color.CWHITE}{location}{color.CEND}')

        mc = MediaConfig()
        print(f'{color.CGREEN}-- Found {color.CWHITE}{get_num_titles(matchedTitles)} ' + \
                f'{color.CGREEN}titles matching {color.CWHITE}--> {color.CYELLOW}' + \
                f'{" ".join(searchTerms)} {color.CWHITE}<-- {color.CGREEN}on ' + \
                f'{color.CWHITE}{location}{color.CEND}')

        if verbose:
            # print(json.dumps(matchedTitles, indent = 4))
            return

        numMatchingTitles = 0
        for path in matchedTitles:
            _, colorCode = mc.get_color_label(os.path.basename(path))
            colorCode = colorCode if colorCode else color.CRED
            for entry in matchedTitles[path]:
                numMatchingTitles += 1
                print(f'{color.CWHITE}{numMatchingTitles:>3}. {colorCode}{path}/{entry["title"]}{color.CWHITE2} ' + \
                        f'({entry["size"]}){color.CEND}')

# ------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------

