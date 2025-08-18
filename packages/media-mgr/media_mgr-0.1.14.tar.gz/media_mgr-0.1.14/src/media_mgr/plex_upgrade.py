#!/usr/bin/env python3
# ------------------------------------------------------------------------------------------------------
# -- Plex Media Server Upgrade Routines
# ------------------------------------------------------------------------------------------------------
# ======================================================================================================

import os
import re
import requests
import time

from urllib.parse import urlparse

from quickcolor.color_def import color
from delayviewer.spinner import Spinner, handle_spinner
from delayviewer.time_and_delay import time_show

from media_mgr.comms_utility import run_cmd, is_server_active
from media_mgr.media_cfg import MediaConfig
from media_mgr.server_cfg import ServerConfig

# ------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------

def is_plex_server(ipv4 = None, debug = False) -> bool:
    if not ipv4:
        # local server check
        return os.path.isdir('/var/lib/plexmediaserver')

    cmd = f'[[ -d /var/lib/plexmediaserver ]] && echo -e "Plex Found"'
    items_received = run_cmd(ipv4, cmd, cmdGet = True, shell = True, debug = debug)
    return items_received[0] == 'Plex Found'

# ------------------------------------------------------------------------------------------------------

def get_running_plex_server_version(ipv4 = None, debug = False):
    if not is_plex_server(ipv4, debug):
        return 'Not a PLEX server!'

    cmd = f'dpkg --list | grep plexmediaserver | awk ' + "'{print $3}'"
    items_received = run_cmd(ipv4, cmd, cmdGet = True, shell=True, debug = debug)
    return items_received[0]

# ------------------------------------------------------------------------------------------------------

def extract_plex_upgrade_url_path():
    plexDownloadUrl = 'https://plex.tv/downloads/details/1?build=linux-ubuntu-x86_64&channel=16&distro=ubuntu'
    plexUpgradeInfo = requests.get(url = plexDownloadUrl, headers = {'Content-Type': 'application/json'})
    return re.search(r'(?<=url=\")(\S+)(?=\")', plexUpgradeInfo.text).group(0)

# ------------------------------------------------------------------------------------------------------

def get_available_plex_server_version():
    plexUpgradeUrlPath = extract_plex_upgrade_url_path()
    availableInstaller = os.path.basename(urlparse(plexUpgradeUrlPath).path)
    return re.search('plexmediaserver_(.*)_amd64.deb', availableInstaller, re.IGNORECASE).group(1)

# ------------------------------------------------------------------------------------------------------

def is_available_plex_server_version_same_as_running_version(ipv4 = None, debug = False):
    return get_available_plex_server_version() == get_running_plex_server_version(ipv4 = ipv4, debug = debug)

# ------------------------------------------------------------------------------------------------------

@handle_spinner
def show_running_and_available_plex_server_versions(ipv4 = None, debug = False,
        spinner: Spinner = None):
    locationLabel = str(ipv4) if ipv4 else 'local_host'

    print()
    spinner.start(f'{color.CGREEN}-- Getting running and available for PLEX Server versions for ' + \
            f'{color.CWHITE2}{locationLabel}{color.CEND}', 0)
    runningPlexServerVer = get_running_plex_server_version(ipv4 = ipv4, debug = debug)
    availablePlexServerVer = get_available_plex_server_version()
    spinner.stop()

    spinner.start(f'{color.CBLUE}-- Analyzing PLEX Server versions for ' + \
            f'{color.CWHITE2}{locationLabel}{color.CBLUE} vs available online{color.CEND}', 0)
    if is_available_plex_server_version_same_as_running_version(ipv4 = ipv4, debug = debug):
        matchLabel = f'{color.CYELLOW}matching!{color.CEND}'
        runningColor = f'{color.CWHITE2}'
        availableColor = f'{color.CWHITE2}'
    else:
        matchLabel = f'{color.CRED}mismatching!{color.CEND}'
        runningColor = f'{color.CYELLOW2}'
        availableColor = f'{color.CYELLOW}'
    spinner.stop()

    print()
    print(f'{color.CBLUE2}  Running version: {runningColor}{runningPlexServerVer:<30}{matchLabel}')
    print(f'{color.CVIOLET}Available version: {availableColor}{availablePlexServerVer:<30}{matchLabel}')

# ------------------------------------------------------------------------------------------------------

@handle_spinner
def get_available_plex_server_package_name(spinner:Spinner = None, verbose: bool = False):
    if verbose:
        spinner.start(f'-- Getting available {color.CRED2}PLEX installer{color.CEND} name', 0)
    plexUpgradeUrlPath = extract_plex_upgrade_url_path()
    availableInstaller = os.path.basename(urlparse(plexUpgradeUrlPath).path)

    if verbose:
        spinner.stop()
        print(f'{color.CCYAN}-- Available plex server binary: {color.CEND}{availableInstaller} ...')

    return availableInstaller

# ------------------------------------------------------------------------------------------------------

def does_installer_exist_on_target(ipv4 = None, pathToInstallerFile = None, debug = False):
    if ipv4:
        items_received = run_cmd(ipv4, f'ls {pathToInstallerFile}', cmdGet = True, debug = debug)
        return not all('' == s or s.isspace() for s in items_received)

    return os.path.exists(pathToInstallerFile)

# ------------------------------------------------------------------------------------------------------

def backup_existing_installer(ipv4 = None, pathToInstallerFile = None, debug = False):

    location = str(ipv4) if ipv4 else 'local_host'

    if does_installer_exist_on_target(ipv4 = ipv4,
            pathToInstallerFile = pathToInstallerFile, debug = debug):

        print(f'{color.CYELLOW}-- Installer {color.CWHITE2}{location}:' + \
                f'{pathToInstallerFile}{color.CYELLOW} exists and should be backed up {color.CEND}')

        if ipv4:
            renamed_file = f'{pathToInstallerFile}_remote_old'
            run_cmd(ipv4, f'mv {pathToInstallerFile} {renamed_file}', cmdGet=False, debug=debug)
        else:
            renamed_file = f'{pathToInstallerFile}_old'
            os.rename(pathToInstallerFile, f'{renamed_file}')

        print(f'   {color.CRED2}Note: Existing installer renamed: ' + \
                f'{color.CEND}{location}:{renamed_file}')

    else:
        print(f'{color.CBLUE}-- No trace of any existing installer ' + \
                f'{color.CWHITE2}{location}:{pathToInstallerFile}{color.CEND}')

# ------------------------------------------------------------------------------------------------------

@handle_spinner
def retrieve_plex_server_bin(ipv4 = None, downloadDir = None,
        pathToInstallerFile = None, debug = False, spinner:Spinner = None):
    location = str(ipv4) if ipv4 else 'local_host'

    spinner.start(f'{color.CYELLOW}-- Extracting PLEX upgrade URL path{color.CEND}', 0)
    plexUpgradeUrlPath = extract_plex_upgrade_url_path()
    spinner.stop()

    spinner.start(f'{color.CGREEN}-- Downloading PLEX server binary ' + \
            f'{color.CWHITE2}{location}:{pathToInstallerFile}{color.CEND}', 0)
    wgetCmd = f'wget -P {downloadDir} {plexUpgradeUrlPath}'
    run_cmd(ipv4, wgetCmd, cmdGet = False, timeout = 60, shell = True, debug = debug)
    spinner.stop()

# ------------------------------------------------------------------------------------------------------

@handle_spinner
def download_new_plex_server_archive(ipv4 = None, downloadDir = None, debug = False,
        spinner:Spinner = None):
    if not downloadDir:
        downloadDir='/tmp'

    if ipv4 and not is_server_active(ipv4 = ipv4):
        raise ConnectionError(f'Error: {ipv4} is not reachable!')

    location = str(ipv4) if ipv4 else 'local_host'

    spinner.start(f'{color.CVIOLET2}-- Deriving full path to incoming installer{color.CEND}', 0)
    fullPathToIncomingInstaller = downloadDir + '/' + get_available_plex_server_package_name()
    spinner.stop()

    backup_existing_installer(ipv4 = ipv4,
            pathToInstallerFile = fullPathToIncomingInstaller, debug = debug)

    retrieve_plex_server_bin(ipv4 = ipv4, downloadDir = downloadDir,
            pathToInstallerFile = fullPathToIncomingInstaller, debug = debug)

    return fullPathToIncomingInstaller

# ------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------

@handle_spinner
def install_plex_server(ipv4 = None, pathToInstallerFile = None,
        debug = False, spinner:Spinner = None):
    location = str(ipv4) if ipv4 else 'local_host'

    spinner.start(f'{color.CYELLOW}-- Installing new plex server to ' + \
            f'{color.CEND}{location}:{pathToInstallerFile}', 0)
    nextCmd = f'sudo dpkg -i {pathToInstallerFile}'
    run_cmd(ipv4, nextCmd, cmdGet = False, timeout = 120, shell = True, debug = debug)
    time.sleep(2)
    spinner.stop()

# ------------------------------------------------------------------------------------------------------

@handle_spinner
def change_plex_user_and_group(ipv4 = None, user: str = 'edwaldner',
        group: str = 'edwaldner', debug = False, spinner:Spinner = None):

    spinner.start(f'{color.CBLUE}-- Changing plex user and group IDs to ' + \
            f'{color.CEND}{user} {color.CBLUE}and{color.CEND} {group}', 0)
    tmpCmd_1 = f'sudo sed -i \'s/User=plex/User={user}/\' /etc/systemd/system/multi-user.target.wants/plexmediaserver.service'
    tmpCmd_2 = f'sudo sed -i \'s/Group=plex/Group={group}/\' /etc/systemd/system/multi-user.target.wants/plexmediaserver.service'
    nextCmd = f'{tmpCmd_1}; {tmpCmd_2}'
    run_cmd(ipv4, nextCmd, cmdGet = False, timeout = 120, shell = True, debug = debug)
    spinner.stop()

# ------------------------------------------------------------------------------------------------------

@handle_spinner
def change_plex_library_ownership(ipv4 = None, owner: str = 'edwaldner',
        debug = False, spinner:Spinner = None):

    spinner.start(f'{color.CGREEN}-- Changing ownership for {color.CEND}' + \
            f'/var/lib/plexmediaserver {color.CGREEN}to {color.CEND}{owner}', 0)
    # nextCmd = "date +\"%T.%3N\" | tee -a /tmp/chown_time ; sudo chown -R edwaldner. /var/lib/plexmediaserver; date +\"%T.%3N\" | tee -a /tmp/chown_time"
    nextCmd = 'sudo chown -R edwaldner. /var/lib/plexmediaserver'
    run_cmd(ipv4, nextCmd, cmdGet = False, timeout = 120, shell = True, debug = debug)
    time.sleep(1)
    spinner.stop()

# ------------------------------------------------------------------------------------------------------

@handle_spinner
def reload_plex_daemon(ipv4 = None, debug = False, spinner:Spinner = None):
    spinner.start(f'{color.CVIOLET}-- Daemon reload{color.CEND}', 0)
    nextCmd = 'sudo systemctl --system daemon-reload'
    run_cmd(ipv4, nextCmd, cmdGet = False, timeout = 120, shell = True, debug = debug)
    time.sleep(1)
    spinner.stop()

# ------------------------------------------------------------------------------------------------------

@handle_spinner
def restart_plex_service(ipv4 = None, debug = False, spinner:Spinner = None):
    spinner.start(f'{color.CBLUE2}-- Plex service restart{color.CEND}', 0)
    nextCmd = 'sudo systemctl restart plexmediaserver.service'
    run_cmd(ipv4, nextCmd, cmdGet = False, timeout = 120, shell = True, debug = debug)
    time.sleep(1)
    spinner.stop()

# ------------------------------------------------------------------------------------------------------

@time_show
def upgrade_plex_server(ipv4 = None, downloadDir = None, force = False,
        debug = False, spinner: Spinner = None):
    if not ipv4:
        import socket
        hostname = socket.gethostname()
        ipv4show = socket.gethostbyname(hostname)
    else:
        if ipv4 and not is_server_active(ipv4 = ipv4):
            raise ConnectionError(f'Error: {ipv4} is not reachable!')
        ipv4show = ipv4

    if not is_plex_server(ipv4, debug):
        print(f'{color.CRED2}Warning: {color.CWHITE2}{ipv4show}{color.CBLUE2} ' + \
                f'is not a PLEX server!{color.CEND}!\n')
        return

    if not force and is_available_plex_server_version_same_as_running_version(ipv4 = ipv4, debug = debug):
        print(f'{color.CRED2}Warning: {color.CWHITE2}{ipv4show}{color.CBLUE2} ' + \
                f'is running a plex server version matching the latest ' + \
                f'available version{color.CEND}!\n')

        runningPlexServerVer = get_running_plex_server_version(ipv4 = ipv4, debug = debug)
        availablePlexServerVer = get_available_plex_server_version()
        print(f'{color.CYELLOW}  Running version: {color.CWHITE2}{runningPlexServerVer}{color.CEND}')
        print(f'{color.CGREEN}Available version: {color.CWHITE2}{availablePlexServerVer}{color.CEND}')
        print(f'\n{color.CRED2}Skipping upgrade {color.CEND}...')
        return

    print()
    print(f'{color.CRED} Upgrading plex server {color.CWHITE2}{ipv4show}')
    print(f'{color.CYELLOW} -----------------------------------{color.CEND}')
    print(f'.. Currently running plex server version: {color.CBLUE2}' + \
            f'{get_running_plex_server_version(ipv4 = ipv4, debug = debug)}{color.CEND}')

    fullPathToInstallerFile = download_new_plex_server_archive(ipv4, downloadDir, debug)

    install_plex_server(ipv4 = ipv4,
            pathToInstallerFile = fullPathToInstallerFile, debug = debug)

    change_plex_user_and_group(ipv4 = ipv4, user = 'edwaldner',
            group = 'edwaldner', debug = debug)

    change_plex_library_ownership(ipv4 = ipv4, owner = 'edwaldner', debug = debug)

    reload_plex_daemon(ipv4 = ipv4, debug = debug)

    restart_plex_service(ipv4 = ipv4, debug = debug)

    # --------------------------------------------------------------------------------------------------

    if debug:
        nextCmd = 'sudo systemctl status plexmediaserver.service'
        print()
        for line in run_cmd(ipv4, nextCmd, cmdGet = True, debug = debug):
            print(line)

# ------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------

def upgrade_all_plex_servers(downloadDir = None, force = False, debug = False):
    sc = ServerConfig()

    for srvEntry in sc.get_server_list():
        srvName, srvCfg = srvEntry
        if srvCfg['serverType'] =='plex':
            upgrade_plex_server(srvCfg['ipv4'], downloadDir, force, debug)

# ------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------

