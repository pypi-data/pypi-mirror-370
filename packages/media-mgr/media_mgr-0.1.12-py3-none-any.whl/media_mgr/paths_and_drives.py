#!/usr/bin/env python3
# ------------------------------------------------------------------------------------------------------
# -- Path and Drive Handling
# ------------------------------------------------------------------------------------------------------
# ======================================================================================================

from collections import defaultdict

import os
import getpass
import paramiko

import subprocess
import re
import json

from quickcolor.color_def import color
from delayviewer.spinner import Spinner, handle_spinner
from delayviewer.time_and_delay import time_show

from media_mgr.comms_utility import run_cmd, is_server_active
from media_mgr.comms_utility import run_ssh_cmd_via_asyncio
from media_mgr.comms_utility import run_ssh_cmds_via_asyncio
from media_mgr.media_cfg import MediaConfig
from media_mgr.server_cfg import ServerConfig

# ------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------

def get_drive_stats(ipv4: str | None = None):
    # returns value is a list of strings (ie: CRLF separated lines)
    allDriveStats = run_cmd(ipv4, 'df -h | grep "sd[b-z]" | sort -k 6', shell = True)
    if allDriveStats == [''] or ('returncode' in allDriveStats and allDriveStats.returncode != 0):
        raise BlockingIOError(f'Warning: Could not retrieve drive paths from IPV4 {ipv4}!')

    return parse_drive_stats(allDriveStats)

# ------------------------------------------------------------------------------------------------------

def get_drive_stats_multiserver():
    sc = ServerConfig()
    ipv4List = sc.get_server_ipv4_list()

    allDriveStatsAllServers = run_ssh_cmd_via_asyncio(ipv4List, 'df -h | grep "sd[b-z]" | sort -k 6')
    parsedDriveStats = {}
    for allDriveStatsForServer in allDriveStatsAllServers:
        ipv4, allDriveStats = allDriveStatsForServer
        parsedDriveStats[ipv4] = parse_drive_stats(allDriveStats)

    return parsedDriveStats

# ------------------------------------------------------------------------------------------------------

def parse_drive_stats(allDriveStats: list):
    driveStats = defaultdict(list)

    for driveInfo in allDriveStats:
        if not len(driveInfo):
            continue
        # separate string into list of ascii fields separated by white space
        driveItems = re.sub(' +', ' ', driveInfo).split(' ')

        # allocate indexed item components into dictionary of lists
        # each list contains type specific contents
        driveStats['size'].append(driveItems[1])
        driveStats['used'].append(driveItems[2])
        driveStats['avail'].append(driveItems[3])
        driveStats['percent'].append(driveItems[4])
        driveStats['path'].append(driveItems[5])

    return driveStats

# ------------------------------------------------------------------------------------------------------

# @time_show
def show_drive_info(ipv4: str | None = None, driveStats: dict | None = None):
    if not driveStats:
        driveStats = get_drive_stats(ipv4 = ipv4)

    print(f'\n{color.CBLUE2}Drive Info     - {color.CBLUE}{ipv4 if ipv4 else "Local"}')
    print(f'{color.CWHITE}----- ----')

    for idx, zipItems in enumerate(zip(driveStats['size'], driveStats['used'],
        driveStats['avail'], driveStats['percent'], driveStats['path'])):
        size, used, avail, percent, path = zipItems
        print(f'{color.CGREEN}{idx+1:>3}. {path:<40} {color.CYELLOW} ' + \
                f'{size:<5} {used:<5} {avail:<5} {color.CCYAN}' + \
                f'{percent:>5}{color.CEND}')

# ------------------------------------------------------------------------------------------------------

@time_show
def show_drive_info_multiserver():
    multiServerDriveStats = get_drive_stats_multiserver()

    for ipv4, driveStats in multiServerDriveStats.items():
        show_drive_info(ipv4 = ipv4, driveStats = driveStats)

# ------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------

def get_drive_paths(ipv4: str | None = None, serverType: str = 'plex'):
    if serverType != 'plex':
        return [ run_cmd(ipv4, "pwd")[0] + "/Desktop/Incoming-Media" ]

    cmdResult = run_cmd(ipv4, "df -h | grep 'sd[b-z]' | sort -k 6 | awk '{ print $6 }'", shell = True)
    if type(cmdResult) is subprocess.CompletedProcess and cmdResult.returncode != 0:
        raise BlockingIOError(f"Warning: Could not retrieve drive paths from IPV4 {ipv4}!")

    return cmdResult

# ------------------------------------------------------------------------------------------------------

def get_drive_paths_multiserver():
    sc = ServerConfig()

    ipv4List = []
    for srvLabel, srvInfo in sc.get_server_list():
        '''
        if srvInfo['serverType'] == 'plex':
            ipv4List.append(srvInfo['ipv4'])
        '''
        ipv4List.append(srvInfo['ipv4'])

    return run_ssh_cmd_via_asyncio(ipv4List, "df -h | grep 'sd[b-z]' | sort -k 6 | awk '{ print $6 }'")

# ------------------------------------------------------------------------------------------------------

@time_show
def show_drive_paths(ipv4: str | None = None, serverType: str = 'plex'):
    print('-' * 100)
    print(f'{color.CYELLOW}Drive Paths ({ipv4 if ipv4 else "Local"})!{color.CEND}')
    print('-' * 100)
    paths = get_drive_paths(ipv4 = ipv4, serverType = serverType)
    for idx, path in enumerate(paths):
        print(f'{color.CGREEN2}{idx+1:>3}. {color.CEND}{color.CGREEN}{path}{color.CEND}')
        if idx % 20 == 19:
            print('-' * 100)
    print('-' * 100)

# ------------------------------------------------------------------------------------------------------

@time_show
def show_drive_paths_multiserver():
    for ipv4, pathList in get_drive_paths_multiserver():
        print('-' * 100)
        print(f'{color.CYELLOW}Drive Paths ({ipv4 if ipv4 else "Local"})!{color.CEND}')
        print('-' * 100)
        for idx, path in enumerate(pathList):
            print(f'{color.CGREEN2}{idx+1:>3}. {color.CEND}{color.CGREEN}{path}{color.CEND}')
            if idx % 20 == 19:
                print('-' * 100)
        # print('-' * 100)
        print()

# ------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------

def get_all_media_paths(ipv4: str | None = None, serverType: str = 'plex'):
    '''
    For Plex servers, retrieve all existing drive mounts with media sub-paths that actually exist
    in the file system
    '''
    paths = run_cmd(ipv4, f'ls -d /media/{getpass.getuser()}/*/*', shell = True) if serverType == 'plex' else \
            run_cmd(ipv4, f'ls -d /home/{getpass.getuser()}/Desktop/Incoming-Media/* | grep Incoming', shell = True)

    if type(paths) is subprocess.CompletedProcess:
        raise BlockingIOError(f"Warning: Could not retrieve drive paths from IPV4 {ipv4}!")

    return sorted(paths)

# ------------------------------------------------------------------------------------------------------

def get_all_media_paths_multiserver():
    '''
    For Plex servers, retrieve all existing drive mounts with media sub-paths that actually exist
    in the file system for each of the specified servers (based on discrete server types)
    '''
    sc = ServerConfig()

    remoteCmdPerIpv4 = {}
    for srvLabel, srvInfo in sc.get_server_list():
        if srvInfo['serverType'] == 'plex':
            remoteCmdPerIpv4[srvInfo['ipv4']] = f'ls -d /media/{getpass.getuser()}/*/*'
        else:
            remoteCmdPerIpv4[srvInfo['ipv4']] = f'ls -d /home/{getpass.getuser()}/Desktop/Incoming-Media/* | grep Incoming'

    # may use for debugging -- comment out return below
    '''
    # print(f'{color.CCYAN2} ---> start getting all media paths -- multiserver -- {color.CEND}')
    mediaPaths = run_ssh_cmds_via_asyncio(remoteCmdPerIpv4)
    # print(f'{color.CBLUE2} ---> finished getting all media paths -- multiserver -- {color.CEND}')
    # print(f'{color.CCYAN2}All Server Media Paths:\n{color.CWHITE2}{mediaPaths}{color.CEND}')
    return mediaPaths
    '''

    return run_ssh_cmds_via_asyncio(remoteCmdPerIpv4)

# ------------------------------------------------------------------------------------------------------

@time_show
def show_all_media_paths(ipv4: str | None = None, serverType: str = 'plex', paths: list | None = None):
    if not paths:
        paths = get_all_media_paths(ipv4 = ipv4, serverType = serverType)

    print('-' * 100)
    print(f'{color.CYELLOW}Get All Media Paths ({ipv4 if ipv4 else "Local"})!{color.CEND}')
    print('-' * 100)
    lastDriveName = 'unknown'
    idxColor = color.CGREEN2
    driveColor = color.CGREEN
    for idx, path in enumerate(paths):
        driveName = path.split('/')[3]
        if driveName != lastDriveName:
            lastDriveName = driveName
            idxColor = color.CYELLOW2 if idxColor == color.CGREEN2 else color.CGREEN2
            driveColor = color.CYELLOW if driveColor == color.CGREEN else color.CGREEN
            print('-' * 100)
        print(f'{idxColor}{idx+1:>3}. {driveColor}{path}{color.CEND}')
    print('-' * 100)

# ------------------------------------------------------------------------------------------------------

@time_show
def show_all_media_paths_multiserver():
    for ipv4, allMediaPaths in get_all_media_paths_multiserver():
        show_all_media_paths(ipv4 = ipv4, paths = allMediaPaths)

# ------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------

def create_full_search_path_list_for_drive(drivePath: str):
    mc = MediaConfig()
    searchNameList = mc.get_configured_entries()

    fullSearchPathListForDrive = []
    for searchName in searchNameList:
        fullSearchPathListForDrive.append(f'{drivePath}/{searchName}')

    return fullSearchPathListForDrive

# ------------------------------------------------------------------------------------------------------

def get_full_search_paths_all_drives(ipv4: str | None = None, serverType: str = 'plex'):
    '''
    For Plex servers, merge all discovered drive mount paths with possible media sub-paths
    Media sub-paths are specified in pathNames.json in the personal cfg dir
    These are potential paths configured, not necessarily paths that exist
    The filtering method below is intended to filter out what does not exist
    as well as specific paths that exist but that are not part of config!
    '''
    drivePaths = get_drive_paths(ipv4, serverType)

    fullSearchPathsAllDrives = []

    if serverType == 'plex':
        for drivePath in drivePaths:
            searchPathListForDrive = create_full_search_path_list_for_drive(drivePath)
            fullSearchPathsAllDrives += searchPathListForDrive

    elif serverType == 'worker':
        fullSearchPathsAllDrives = get_all_media_paths(ipv4, serverType)

    return sorted(fullSearchPathsAllDrives)

# ------------------------------------------------------------------------------------------------------

def get_full_search_paths_all_drives_multiserver():
    allServerDrivePaths = get_drive_paths_multiserver()
    # print(f'{color.CGREEN2}full search paths multiserver:\n{color.CRED2}{allServerDrivePaths}{color.CEND}')

    sc = ServerConfig()

    fullSearchPathsAllDrivesAllServers = []

    for ipv4, drivePaths in allServerDrivePaths:
        fullSearchPathsAllDrives = []

        serverType = sc.get_server_type_for_ipv4(ipv4)
        if serverType == 'plex':
            for drivePath in drivePaths:
                searchPathListForDrive = create_full_search_path_list_for_drive(drivePath)
                fullSearchPathsAllDrives += searchPathListForDrive

        elif serverType == 'worker':
            fullSearchPathsAllDrives += get_all_media_paths(ipv4, serverType)

        fullSearchPathsAllDrivesAllServers.append((ipv4, sorted(fullSearchPathsAllDrives)))

    # print(f'{color.CBLUE2}full search paths all drives multiserver:\n{color.CVIOLET2}{fullSearchPathsAllDrivesAllServers}{color.CEND}')
    return fullSearchPathsAllDrivesAllServers

# ------------------------------------------------------------------------------------------------------

@time_show
def show_full_search_paths_all_drives(ipv4: str | None = None, serverType: str = 'plex', paths: list | None = None):
    if not paths:
        paths = get_full_search_paths_all_drives(ipv4 = ipv4, serverType = serverType)

    print('-' * 100)
    print(f'{color.CYELLOW}Get Full Search Paths All Drives from {ipv4 if ipv4 else "Local"}!{color.CEND}')
    print('-' * 100)
    lastDriveName = 'unknown'
    idxColor = color.CBLUE
    pathColor = color.CCYAN
    for idx, path in enumerate(paths):
        driveName = path.split('/')[3]
        if driveName != lastDriveName:
            lastDriveName = driveName
            idxColor = color.CYELLOW if idxColor == color.CBLUE else color.CBLUE
            pathColor = color.CYELLOW if pathColor == color.CCYAN else color.CCYAN
            print('-' * 100)
        print(f'{idxColor}{idx+1:>3}. {pathColor}{path}{color.CEND}')
    print('-' * 100)

# ------------------------------------------------------------------------------------------------------

@time_show
def show_full_search_paths_all_drives_multiserver(ipv4: str | None = None, serverType: str = 'plex'):
    for ipv4, paths in get_full_search_paths_all_drives_multiserver():
        show_full_search_paths_all_drives(ipv4 = ipv4, paths = paths)

# ------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------

def get_filtered_media_paths(ipv4: str | None = None, serverType: str = 'plex', lookingFor: list | None = None):
    '''
    Taking all media paths that exist (drive mount paths plus media sub paths) and filter against
    all possible search paths on all mount paths - subset represents searchable paths that exist
    in the file system and that are part of the configured pathNames.json group
    '''
    paths = get_all_media_paths(ipv4, serverType)

    if lookingFor:
        paths = [ path for path in paths if os.path.basename(path) in lookingFor ]
    fullPaths = get_full_search_paths_all_drives(ipv4, serverType)

    if len(paths):
        return sorted(list(set(paths).intersection(fullPaths)))

    return []

# ------------------------------------------------------------------------------------------------------

def get_filtered_media_paths_multiserver(lookingFor: list | None = None):
    '''
    Taking all media paths that exist on multiple servers (drive mount paths plus media sub paths)
    and filter against all possible search paths on all mount paths - subset represents searchable paths
    that exist in the file system on all servers and that are part of the configured pathNames.json group
    '''
    allPaths = get_all_media_paths_multiserver()
    fullPaths = get_full_search_paths_all_drives_multiserver()
    referencePaths = {}
    for ipv4, paths in fullPaths:
        referencePaths[ipv4] = paths
    '''
    print(f'Reference Paths {json.dumps(referencePaths, indent=4)}')
    print(f'All Media Path Servers: {allPaths}')
    '''

    filteredPaths = []
    for ipv4, paths in allPaths:
        if lookingFor:
            paths = [ path for path in paths if os.path.basename(path) in lookingFor ]

        '''
        if ipv4 not in referencePaths.keys():
            print(f'Warning: {color.CRED2}Could not find {color.CWHITE}{ipv4}{color.CRED2} in reference paths dict!{color.CEND}')
            continue
        '''

        # print(f'Paths for {ipv4} while looking for {lookingFor} -- len paths = {len(paths)}\n{paths}')
        if len(paths):
            filteredPaths.append((ipv4, sorted(list(set(paths).intersection(referencePaths[ipv4])))))
        else:
            filteredPaths.append((ipv4, []))

    return filteredPaths

# ------------------------------------------------------------------------------------------------------

@time_show
def show_filtered_media_paths(ipv4: str | None = None, serverType: str = 'plex',
                              lookingFor: list | None = None, paths: list | None = None):
    print('-' * 100)
    print(f'{color.CVIOLET2}Get Filtered Media Paths ({ipv4 if ipv4 else "Local"})!{color.CEND}')
    print('-' * 100)
    lastDriveName = 'unknown'
    idxColor = color.CBLUE
    pathColor = color.CCYAN
    for idx, path in enumerate(paths):
        driveName = path.split('/')[3]
        if driveName != lastDriveName:
            lastDriveName = driveName
            idxColor = color.CYELLOW if idxColor == color.CBLUE else color.CBLUE
            pathColor = color.CYELLOW if pathColor == color.CCYAN else color.CCYAN
            print('-' * 100)
        print(f'{idxColor}{idx+1:>3}. {pathColor}{path}{color.CEND}')
    print('-' * 100)

# ------------------------------------------------------------------------------------------------------

@time_show
def show_filtered_media_paths_multiserver(lookingFor: list | None = None):
    for ipv4, paths in get_filtered_media_paths_multiserver(lookingFor = lookingFor):
        show_filtered_media_paths(ipv4 = ipv4, paths = paths)

# ------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------

def get_lsblk_devices_and_mounts(ipv4: str | None = None):
    cmdResult = run_cmd(ipv4, "lsblk -b --json", jsonOutput=True)
    # cmdResult = run_cmd(ipv4, "lsblk -b | grep 'sd[b-z]' | grep 'part|disk' | awk '{ print $1, $4, $7 }'")
    if type(cmdResult) is subprocess.CompletedProcess:
        raise BlockingIOError(f"Warning: Could not retrieve devices and mount paths from IPV4 {ipv4}!")

    # print(json.dumps(cmdResult, indent=4))
    mountableDevices = []
    for dev in cmdResult['blockdevices']:
        if re.match("sd[b-z]", dev['name']):
            mountableDevices.append(dev)

    return mountableDevices

# ------------------------------------------------------------------------------------------------------

def get_lsblk_mountable_partitions(ipv4: str | None = None):
    mountableDevices = get_lsblk_devices_and_mounts(ipv4=ipv4)
    mountablePartitions = []
    for dev in mountableDevices:
        for child in dev['children']:
            if child['size'] > 1_000_000_000:
                mountablePartitions.append(child)

    return mountablePartitions

# ------------------------------------------------------------------------------------------------------

def show_dev_partitions(ipv4: str | None = None,
        partitionsThatAreAlreadyMounted: list | None = None,
        partitionsThatAreUnmounted : list | None = None):
    availablePartitions = []
    if not partitionsThatAreAlreadyMounted:
        availablePartitions = get_lsblk_mountable_partitions(ipv4=ipv4)
        partitionsThatAreAlreadyMounted = [ x for x in availablePartitions if x['mountpoints'] != [ None ] ]

    if not partitionsThatAreUnmounted:
        if not availablePartitions:
            availablePartitions = get_lsblk_mountable_partitions(ipv4=ipv4)
        partitionsThatAreUnmounted = [ x for x in availablePartitions if x['mountpoints'] == [ None ] ]

    if partitionsThatAreAlreadyMounted:
        print(f'\n{color.CBLUE2}-- The following {color.CWHITE}{len(partitionsThatAreAlreadyMounted)}' + \
                f'{color.CBLUE2} devices on {color.CWHITE}{ipv4}{color.CBLUE2} are mounted!{color.CEND}\n')
        for idx, partition in enumerate(partitionsThatAreAlreadyMounted):
            print(f'   {color.CGREEN2}{idx+1:>3}. {color.CEND}Device ' + \
                    f'{color.CCYAN}/dev/{partition["name"]}{color.CEND} ' + \
                    f'mount point is {color.CYELLOW}{partition["mountpoints"][0]}{color.CEND}')

    if partitionsThatAreUnmounted:
        print(f'\n{color.CBLUE2}-- The following {color.CWHITE}{len(partitionsThatAreUnmounted)}' + \
                f'{color.CBLUE2} devices on {color.CWHITE}{ipv4}{color.CBLUE2} are not mounted!{color.CEND}\n')
        for idx, partition in enumerate(partitionsThatAreUnmounted):
            print(f'   {color.CGREEN2}{idx+1:>3}. {color.CEND}Device ' + \
                    f'{color.CCYAN}/dev/{partition["name"]}{color.CEND} has no mount point!')

# ------------------------------------------------------------------------------------------------------

@time_show
@handle_spinner
def mount_dev_partitions(ipv4: str | None = None, spinner: Spinner | None = None):
    if ipv4 and not is_server_active(ipv4 = ipv4):
        raise ConnectionError(f'Error: {ipv4} is not reachable!')

    availablePartitions = get_lsblk_mountable_partitions(ipv4 = ipv4)
    partitionsThatAreUnmounted = [ x for x in availablePartitions if x['mountpoints'] == [ None ] ]
    partitionsThatAreAlreadyMounted = [ x for x in availablePartitions if x['mountpoints'] != [ None ] ]
    print('')
    if not partitionsThatAreUnmounted:
        print(f'{color.CRED2}-- There are no available partitions to mount! ' + \
                f'{color.CWHITE}All device partitions are mounted!{color.CEND}')
        show_dev_partitions(ipv4 = ipv4,
                partitionsThatAreAlreadyMounted = partitionsThatAreAlreadyMounted,
                partitionsThatAreUnmounted = partitionsThatAreUnmounted)
        return

    print(f'....  {color.CYELLOW2}{len(partitionsThatAreUnmounted)}' + \
            f'{color.CEND} of {color.CVIOLET2}{len(availablePartitions)}' + \
            f'{color.CEND} partitions are available to be mounted!')

    for idx, partition in enumerate(partitionsThatAreUnmounted):
        '''
        mountingPhrase = f'       Mounting {color.CCYAN}/dev/{partition["name"]}{color.CEND} ......   {color.CYELLOW}'
        print(mountingPhrase, end=' ', flush=True)
        '''
        spinner.start(f'{color.CGREEN}-- {color.CWHITE}{idx+1:>3}. ' + \
                f'{color.CGREEN}Mounting {color.CCYAN}/dev/{partition["name"]}' + \
                f'{color.CEND} ...', 60)
        cmdResult = run_cmd(ipv4, f"udisksctl mount -b /dev/{partition['name']}", timeout=15)
        spinner.stop()
        '''
        print('\r', end='', flush=True)
        print(f'{color.CGREEN}-- {color.CWHITE}{idx+1:>3}. ' + \
                f'{color.CGREEN}Mounted {color.CCYAN}/dev/{partition["name"]}' + \
                f'{color.CEND} in {color.CVIOLET2}{duration}{color.CEND}')
        '''

    show_dev_partitions(ipv4 = ipv4)

# ------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------

