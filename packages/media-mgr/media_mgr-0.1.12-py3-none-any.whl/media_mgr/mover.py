#!/usr/bin/env python3
# ------------------------------------------------------------------------------------------------------
# -- Media Relocation Methods
# ------------------------------------------------------------------------------------------------------
# ======================================================================================================

from collections import defaultdict

import json
import os
import getpass
import paramiko

from quickcolor.color_def import color
from delayviewer.time_and_delay import time_execution

from media_mgr.comms_utility import run_cmd, is_server_active, group_list

from media_mgr.media_cfg import MediaConfig
from media_mgr.server_cfg import ServerConfig

from media_mgr.search import find_items_in_search_paths

# ------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------

def move_title(ipv4: str | None = None, searchTerms: str | None = None,
        fromBaseDir: str = "Movies", toBaseDir: str = "Primo-Movies",
        testMove: bool = False, verbose: bool = False):

    if fromBaseDir == toBaseDir:
        print(f'\n{color.CRED2}-- Moving content from {color.CYELLOW2}{fromBaseDir} ' + \
                f'{color.CRED2}to {color.CYELLOW2}{toBaseDir} {color.CRED2}would ' + \
                f'be counter productive{color.CEND}!')
        return

    ipv4List = []
    if ipv4:
        ipv4List.append(ipv4)
    else:
        sc = ServerConfig()
        for srvName, srvCfg in sc.get_server_list():
            if srvCfg['serverType'] == 'plex':
                ipv4List.append(srvCfg['ipv4'])

    print("")
    for server in ipv4List:
        matchedTitles = []
        try:
            matchedTitles = find_items_in_search_paths(ipv4=server, searchPathList=None, searchTerms=searchTerms)

        except Exception as e:
            print(f'{color.CRED2}-- Processing error: Search aborted for ' + \
                    f'titles matching {color.CWHITE}--> {color.CYELLOW}' + \
                    f'{" ".join(searchTerms)} {color.CWHITE}<-- {color.CRED2}' + \
                    f'on {color.CWHITE}{server}\n{color.CRED2}   Investigate ' + \
                    f'{color.CWHITE}{server}{color.CRED2} for problems with ' + \
                    f'drive mounts!{color.CEND}\n{e}')
            return

        if not matchedTitles:
            test_move_msg = '(test move) ' if testMove else ''
            print(f'{color.CRED2}-- Did not find any titles matching ' + \
                    f'{color.CWHITE}--> {color.CYELLOW}{" ".join(searchTerms)}' + \
                    f'{color.CWHITE}<-- {color.CRED2}for {test_move_msg}' + \
                    f'relocation on {color.CWHITE}{server}{color.CEND}')
            continue

        if verbose:
            print(json.dumps(matchedTitles, indent=4))

        failedToMoveMatch = False
        numTitlesMoved = 0
        for key in matchedTitles:
            dirLabel = os.path.basename(key)
            dirRoot = os.path.dirname(key)

            for entry in matchedTitles[key]:
                title = entry['title']
                if dirLabel == fromBaseDir:
                    fromPathAndFile = key + "/" + title
                    toPath = dirRoot + "/" + toBaseDir
                    toPathAndFile = toPath + "/" + title

                    if not run_cmd(ipv4=server, cmd="ls \"%s\"" % (fromPathAndFile)):
                        print(f'-- {color.CRED}could not find {color.CWHITE2}' + \
                                f'{fromPathAndFile}{color.CRED2} on ' + \
                                f'{color.CYELLOW}{server}{color.CEND}')
                        failedToMoveMatch = True
                        continue

                    if not run_cmd(ipv4=server, cmd="[[ -d \"%s\" ]] && echo -e \"Found %s\"" % (toPath, toPath)):
                        print(f'-- {color.CRED}could not find path ' + \
                                f'{color.CWHITE2}{toPath}{color.CRED} on ' + \
                                f'{color.CYELLOW}{server}{color.CEND}')
                        failedToMoveMatch = True
                        continue

                    if testMove:
                        pretext = 'testing move of '
                    else:
                        pretext = 'moving '

                    print(f'-- {pretext}{color.CYELLOW}{title}{color.CEND} ' + \
                            f'residing on {color.CRED2}{server}{color.CEND}')
                    print(f'      from: {color.CBLUE2}{key}{color.CEND}')
                    print(f'        to: {color.CBLUE}{dirRoot}/{toBaseDir}{color.CEND}')
                    print('')

                    if not testMove:
                        cmd = "mv \"%s\" \"%s\"" % (fromPathAndFile, toPathAndFile)
                        if verbose:
                            print(f'... {color.CVIOLET2}running cmd:{color.CEND}\n{cmd}')
                        dumpThis = run_cmd(ipv4=server, cmd=cmd)
                        numTitlesMoved += 1

        if not testMove and numTitlesMoved == 0 and failedToMoveMatch == False:
            print(f'-- {color.CRED}could not find {color.CWHITE}any titles ' + \
                    f'{color.CRED}from path {color.CCYAN}{fromBaseDir} ' + \
                    f'{color.CRED} matching search terms ({color.CWHITE}' + \
                    f'{" ".join(searchTerms)}{color.CRED}) to move on ' + \
                    f'{color.CYELLOW}{server}{color.CEND}')

# ------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------

# 2025-0201 -- not currently used anywhere
def walk_local_directory(localPath: str, mediaType: str = 'mkv') -> dict:
    fileList = {}
    for (dirpath, dirnames, filenames) in os.walk(localPath):
        for filename in filenames:
            if filename.endswith(f'.{mediaType}'):
                fileList[filename] = os.sep.join([dirpath, filename])

    # print(json.dumps(fileList, indent=4))
    return fileList


def walk_remote_directory(sftp, remotePath: str):
    '''Recursively walk a directory on the remote server returning full file paths'''
    for entry in sftp.listdir_attr(remotePath):
        if entry.st_mode & 0o40000:  # Check if it's a directory
            yield from walk_remote_directory(sftp, f'{remotePath}/{entry.filename}')
        else:
            yield f'{remotePath}/{entry.filename}'


# @time_execution
def consolidate(ipv4: str, rootAbsPath: str, targetFolder: str,
                mediaType: str, testConsolidation: bool = False,
                verbose: bool = False):

    privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
    with paramiko.SSHClient() as ssh:
        '''
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ipv4,
                     username = getpass.getuser(),
                     pkey = paramiko.RSAKey.from_private_key_file(privatekeyfile))
        '''
        ssh.load_system_host_keys()
        ssh.connect(ipv4)

        stdin, stdout, stderr = ssh.exec_command(f'[[ -d {rootAbsPath} ]] && echo -e \"Found path\"')
        if 'Found path' not in stdout.read().decode():
            raise FileNotFoundError(f'Error: {rootAbsPath} is not recognized as a valid directory!')

        if targetFolder != '.':
            consolidatedPath = f'{rootAbsPath}/{targetFolder}'

            stdin, stdout, stderr = ssh.exec_command(f'[[ -d {consolidatedPath} ]] && echo -e \"Found path\"')
            if 'Found path' in stdout.read().decode():
                raise ValueError(f'Error: {consolidatedPath} already exists! Remove or rename and retry...')

            stdin, stdout, stderr = ssh.exec_command(f'mkdir \"{consolidatedPath}\"')
            # stdin, stdout, stderr = ssh.exec_command(f'cd \"{consolidatedPath}\"; pwd; tree \"{consolidatedPath}\"')
            if verbose:
                print(stdout.read().decode())
        else:
            consolidatedPath = f'{rootAbsPath}'


        with ssh.open_sftp() as sftp:
            walkResults = walk_remote_directory(sftp, rootAbsPath)
            if verbose:
                print(f'{color.CYELLOW}Found by walking {color.CGREEN}{rootAbsPath}:{color.CEND}\n{walkResults}')
            numItemsConsolidated = 0
            for fileName in walkResults:
                if testConsolidation:
                    print(f'\n -- {color.CBLUE2}Test Moving {color.CWHITE2}{fileName}' + \
                            f'\n ........... {color.CBLUE2}to {color.CYELLOW}{consolidatedPath}{color.CEND}!')
                    numItemsConsolidated += 1
                    continue

                stdin, stdout, stderr = ssh.exec_command(f'mv \"{fileName}\" \"{consolidatedPath}\"')
                print(f'\n -- {color.CBLUE2}Moving {color.CWHITE2}{fileName}' + \
                        f'\n ...... {color.CBLUE2}to {color.CYELLOW}{consolidatedPath}{color.CEND}!')
                numItemsConsolidated += 1

            testPrefix = 'Test ' if testConsolidation else ''
            print(f'\n{testPrefix}Consolidated {color.CCYAN}{numItemsConsolidated}{color.CEND} items this run!\n')


# ------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------

