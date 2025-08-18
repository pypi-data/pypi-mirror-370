#!/usr/bin/env python3
# ------------------------------------------------------------------------------------------------------
# Comms (and shell specific) utilities
# ------------------------------------------------------------------------------------------------------
# ======================================================================================================

import json
import sys
import subprocess

import asyncio, asyncssh

from quickcolor.color_def import color

# ------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------

# Note: this method of retrieving remote content is REALLY SLOW - zsh/bash kicks ass:
# -- show_drives_on_server 10.114.108.70 takes 250 msec
# -- running this python script takes
def run_ssh_send_cmd(ipv4: str, cmd: str = 'ls -als',
        timeout: int = 5, debug: bool = False):
    if debug:
        print(f'---- sending {color.CRED2}run_ssh_send_cmd{color.CEND} ' + \
                f'SEND CMD to {color.CBLUE2}{ipv4}:\n' + \
                f'{color.CBLUE}{cmd}{color.CEND}')

    session = subprocess.run(
            ["ssh", "%s" % ipv4, cmd],
            capture_output = True,
            text = True,
            timeout = timeout)

# ------------------------------------------------------------------------------------------------------

# Note: this method of retrieving remote content is REALLY SLOW - bash kicks ass:
# -- show_drives_on_server 10.114.108.70 takes 250 msec
# -- running this python script takes
def run_ssh_cmd(ipv4: str, cmd: str = 'ls -als',
        jsonOutput: bool = False, timeout: int = 5,
        debug: bool = False):
    if debug:
        print(f'---- sending {color.CYELLOW}run_ssh_cmd{color.CEND} ' + \
                f'CMD to {color.CBLUE2}{ipv4}:\n' + \
                f'{color.CYELLOW}{cmd}{color.CEND}')

    session = subprocess.run(
            ["ssh", "%s" % ipv4, cmd],
            stdout = subprocess.PIPE,
            stderr = subprocess.PIPE,
            # capture_output = True,
            text = True,
            timeout = timeout)

    try:
        if jsonOutput:
            returnResult = json.loads(session.stdout)
        else:
            result = session.stdout.strip("\n")
            returnResult = result.split('\n')

        if debug:
            print(f"{color.CRED}Received:{color.CEND}\n{str(returnResult)}")

        return returnResult

    except Exception as e:
        # error = session.stderr.readlines()
        error = session.stderr
        print(f'Error:\n{error}\n{str(e)}', file = sys.stderr)
        return None

# ------------------------------------------------------------------------------------------------------

def run_cmd(ipv4: str | None = None, cmd: str = 'ls -als',
            cmdGet: bool = True, jsonOutput: bool = False,
            timeout: int = 5, shell: bool = False,
            retCodeOnly: bool = False, debug: bool = False):

    if not ipv4:
        if debug:
            print(f'---- sending {color.CRED}run_cmd{color.CEND} ' + \
                    f'SEND CMD to {color.CBLUE2} the local system:\n' + \
                    f'{color.CBLUE}{cmd}{color.CEND}')

        cmdList = []
        cmdList.append(cmd)
        cmdResult = subprocess.run(
            cmdList,
            # stdout = subprocess.PIPE,
            # stderr = subprocess.PIPE,
            capture_output = True,
            text = True,
            shell = shell,
            timeout = timeout)

        if isinstance(cmdResult, subprocess.CompletedProcess) and cmdResult.returncode and debug:
            raise SystemError(f'Warning: Problem running local cmd ->{cmd}<- ' + \
                    f'... returncode: {cmdResult.returncode}\n... complete cmdREsult: {cmdResult}')

        if retCodeOnly:
            returnResult = cmdResult.returncode

        elif jsonOutput:
            returnResult = json.loads(cmdResult.stdout)
        else:
            result = cmdResult.stdout.strip("\n")
            returnResult = result.split('\n')

        if debug:
            print(f"{color.CRED}Received:{color.CEND}\n{str(returnResult)}")

        return returnResult

    else:
        if cmdGet:
            cmdResult = run_ssh_cmd(ipv4, cmd, jsonOutput, timeout, debug)
            if isinstance(cmdResult, subprocess.CompletedProcess) and cmdResult.returncode:
                raise SystemError(f'Warning: Problem running cmd ->{cmd}<- ' + \
                        f'on {ipv4} ... returncode: {cmdResult.returncode}')
        else:
            cmdResult = run_ssh_send_cmd(ipv4, cmd, timeout, debug)

    return cmdResult

# ------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------

def is_server_active(ipv4: str = None):
    if not ipv4:
        raise ValueError(f"Need a valid IPV4 address!")

    retCode = run_cmd(ipv4 = None,
            cmd = f'ping -c 1 -W 1 -q {ipv4}',
            timeout = 2, shell = True, retCodeOnly = True)

    return retCode == 0

# ------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------

def group_list(inputList = None, separator = None):
    group = []
    for item in inputList:
        if separator in item:
            yield group
            group = []
        group.append(item)
    yield group

# ------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------

async def run_ssh_cmd_async_task(ipv4: str, remoteCmd: str, evalExitStatus: bool = True):
    async with asyncssh.connect(ipv4, known_hosts=None) as conn:
        try:
            '''
            print(f'{color.CYELLOW2}Running ->{remoteCmd}<- on {color.CVIOLET2}{ipv4}{color.CEND}')
            '''
            result = await conn.run(remoteCmd, check = evalExitStatus, timeout = None)
            '''
            stdoutList = result.stdout.split('\n')
            print(f'{color.CGREEN}Result {color.CVIOLET2}{ipv4} {color.CWHITE2}{len(stdoutList)} items in result --')
            print(f'{color.CWHITE2}{result.stdout}{color.CEND}')
            '''
        except asyncssh.ProcessError as exc:
            print(exc.stderr, end='')
            print(f'Waldner ProcessError detected for {ipv4} running remote cmd:')
            for sliver in remoteCmd.split(';'):
                print(f" .... {color.CBLUE2}{sliver}{color.CEND}")
            print(f'\n{remoteCmd}\n')

            print(f'Waldner ProcessError: Process exited with status {exc.exit_status}', file=sys.stderr)
            raise
        except asyncssh.ChannelOpenError as exc:
            print(exc.stderr, end='')
            print(f'ChannelOpenError: Process exited with status {exc.exit_status}', file=sys.stderr)
            raise
        except asyncssh.TimeoutError as exc:
            print(exc.stderr, end='')
            print(f'TimeoutError: Process exited with status {exc.exit_status}', file=sys.stderr)
            raise
        except Exception as exc:
            print(exc.stderr, end='')
            print(f'Unfiltered Exception: Process exited with status {exc.exit_status}', file=sys.stderr)
            raise

        if result.returncode and evalExitStatus:
            raise ValueError(f"Dude, que passa?\n{result.stderr}")

        if '\n' in result.stdout:
            # print(f'result.stdout:\n->{result.stdout.split('\n')}<-')
            return (ipv4, [x for x in result.stdout.split('\n') if len(x)])

        # print(f'result.stdout:\n->{result.stdout}<-')
        return (ipv4, result.stdout)

# ------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------

async def run_ssh_cmd_async_multi_server(ipv4List: list, remoteCmd: str, evalExitStatus: bool = True):
    if not ipv4List:
        raise ValueError('Need a list of servers to reach out and touch!')

    tasks = []
    for ipv4 in ipv4List:
        tasks.append(asyncio.create_task(run_ssh_cmd_async_task(ipv4, remoteCmd, evalExitStatus)))
    return await asyncio.gather(*tasks)

# ------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------

def run_ssh_cmd_via_asyncio(ipv4List: list, remoteCmd: str, evalExitStatus: bool = True):
    return asyncio.run(run_ssh_cmd_async_multi_server(ipv4List, remoteCmd, evalExitStatus))

# ------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------

async def run_ssh_cmds_async_multi_server(remoteCmdPerIpv4: dict, evalExitStatus: bool = True):
    if not remoteCmdPerIpv4:
        raise ValueError('Need a dictionary of servers and cmds to reach out and touch!')

    tasks = []
    for ipv4, remoteCmd in remoteCmdPerIpv4.items():
        tasks.append(asyncio.create_task(run_ssh_cmd_async_task(ipv4, remoteCmd, evalExitStatus)))
    return await asyncio.gather(*tasks)

# ------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------

def run_ssh_cmds_via_asyncio(remoteCmdPerIpv4: dict, evalExitStatus: bool = True):
    return asyncio.run(run_ssh_cmds_async_multi_server(remoteCmdPerIpv4, evalExitStatus))

# ------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------

