#!/usr/bin/env python3
# ------------------------------------------------------------------------------------------------------
# -- Media EXIF Rename
# ------------------------------------------------------------------------------------------------------
# ======================================================================================================

import sys
import os
import json
import time
import datetime
import random
import contextlib


import imghdr   # now dependant on the standard-imghdr package (pip)
import exiv2

from quickcolor.color_def import color
from delayviewer.stopwatch import Stopwatch, handle_stopwatch

# ------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------

def get_path_info(fullPathToFile = None):
    if not os.path.isfile(fullPathToFile):
        raise ValueError(f'Error! ->{fullPathToFile}<- is not a file!')

    dirName = os.path.dirname(fullPathToFile)
    baseName = os.path.basename(fullPathToFile)
    fileName, extension = os.path.splitext(fullPathToFile)

    return dirName, baseName, fileName, extension

# ------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------

def get_exif_data(fullPathToFile = None):
    if not os.path.isfile(fullPathToFile):
        raise ValueError(f'Error! ->{fullPathToFile}<- is not a file!')

    if imghdr.what(fullPathToFile) not in ['jpeg', 'gif']:
        raise ValueError(f'Error! ->{fullPathToFile}<- is neither a JPEG nor a GIF!')

    # workaround to not having the function calls print:
    # "Directory Canon has an unexpected next pointer; ignored."
    # with contextlib.redirect_stdout(None) and contextlib.redirect_stderr(None):
    with contextlib.redirect_stderr(None):
        image = exiv2.ImageFactory.open(fullPathToFile)
        image.readMetadata()

        exifDict = {}
        for entry in image.exifData():
            entryStrList = entry.__str__().split(f'{entry.key()}:')
            entryStrList = [ s.strip() for s in entryStrList ]
            exifDict[entry.key()] = entryStrList[1]

        return exifDict

# ------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------

def get_exif_datetime_original(fullPathToFile = None):
    exifData = get_exif_data(fullPathToFile)

    try:
        dateTimeOrig = exifData['Exif.Photo.DateTimeOriginal'].replace(':', '-')
        dateTimeOrig = dateTimeOrig.replace(' ', '_')
        return dateTimeOrig

    except:
        print(f'{color.CRED2}Warning:{color.CEND} Problem extracting EXIF data ' + \
                f'from {color.CYELLOW}{fullPathToFile}{color.CEND}')
        raise

# ------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------

@handle_stopwatch
def rename_all_jpg_in_path_to_exif_dates(pathToJpgs = None, stopwatch = None):
    if not os.path.isdir(pathToJpgs):
        raise ValueError(f'Error! ->{pathToJpgs}<- is not a directory!')

    files = [ f for f in os.listdir(pathToJpgs) if os.path.isfile(os.path.join(pathToJpgs, f)) ]
    if not len(files):
        print(f'{color.CRED2}Warning:{color.CEND} Could not find EXIF media ' + \
                f'in {color.CYELLOW}{pathToJpgs}{color.CEND}')
        return

    errorRenamingTheseFiles = []
    stopwatch.start(f'{color.CBLUE2}-- Attempting to rename {color.CWHITE2}{len(files)}' + \
            f'{color.CBLUE2} file(s) to EXIF datestamps...{color.CEND}', 85)
    for file in files:
        fullPathToFile = pathToJpgs + '/' + file
        try:
            exifData = get_exif_datetime_original(fullPathToFile)
            if exifData:
                fullPathToChangedFile = pathToJpgs + '/' + str(exifData) + '.jpg'
                os.rename(fullPathToFile, fullPathToChangedFile)
        except:
            errorRenamingTheseFiles.append(fullPathToFile)

    if len(errorRenamingTheseFiles):
        stopwatch.stop(f'{color.CRED2}Completed with errors{color.CEND}!')
        print(f'{color.CRED2}Warning:{color.CEND} Could not do anything with the following files:')
        for file in errorRenamingTheseFiles:
            print(f' -- {color.CYELLOW}{file}{color.CEND}')
    else:
        stopwatch.stop()

# ------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------

def get_recursive_subdir_list(startPath):
    dirsInDir = [ f'{startPath}/{x}' for x in os.listdir(startPath) if os.path.isdir(f'{startPath}/{x}')]

    if len(dirsInDir):
        for item in dirsInDir:
            moreDirs = get_recursive_subdir_list(startPath = item)
            if len(moreDirs):
                dirsInDir.extend(moreDirs)

    return dirsInDir

# ------------------------------------------------------------------------------------------------------

def rename_all_jpg_in_all_sub_paths_to_exif_dates(rootPath, debug = False):
    if not os.path.isdir(rootPath):
        raise ValueError(f'Error! ->{rootPath}<- is not a directory!')

    subdirs = get_recursive_subdir_list(startPath=rootPath)

    for subdir in subdirs:
        print(f'{color.CBLUE2}EXIF change in process for {color.CWHITE}' + \
                f'{subdir} for {color.CYELLOW}{len(os.listdir(subdir))}' + \
                f'{color.CEND} files')
        rename_all_jpg_in_path_to_exif_dates(pathToJpgs = subdir)

# ------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------

def show_path_info(fullPathToFile = None):
    dirName, baseName, fileName, extension = get_path_info(fullPathToFile)

    print(f'Active file: {color.CYELLOW}{fullPathToFile}{color.CEND}')
    print(f'Dirname:     {color.CVIOLET}{dirName}{color.CEND}')
    print(f'Basename:    {color.CCYAN}{baseName}{color.CEND}')
    print(f'Filename:    {color.CWHITE}{fileName}{color.CEND}')
    print(f'Extension:   {color.CBLUE}{extension}{color.CEND}')

# ------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------

def show_exif_info(fullPathToFile = None):
    exifData = get_exif_data(fullPathToFile)

    if not exifData:
        print(f'{color.CRED2}Warning! {color.CWHITE2}No EXIF info {color.CRED2}' + \
                f'retrieved from specified file - {color.CWHITE2}' + \
                f'{fullPathToFile}{color.CEND}')
        return

    tagCount = 0

    for key, val in exifData.items():
        print(f'{color.CBLUE}{key}: {color.CEND}{val}')
        tagCount += 1

    '''
    for entry in exifData:
        entryStrList = entry.__str__().split(':')
        entryStrList = [ s.strip() for s in entryStrList ]

        print(f'{color.CBLUE}{entry.key()}: {color.CEND}{entryStrList[1:]}')
        tagCount += 1

        if tagCount == len(exifData):
            for attr in dir(entry):
                print(f' ---> {color.CGREEN}{attr}:{color.CEND} {getattr(entry, attr)}')
    '''

    '''
        if tagCount < len(exifData):
            print(f'{color.CYELLOW}{entry.familyName()}.{entry.groupName()}.{entry.tagName()}{color.CEND}: {entry.tagLabel()}')
            print(f'{color.CRED2}{entry.familyName()}.{entry.groupName()}.{entry.tagName()}{color.CEND}: {entry.print()}')
            print(f'{color.CGREEN}{entry.key()}{color.CEND} -- {entry.__str__()}')
            print(f'{color.CVIOLET2}{entry.__str__().split(":")[1]}{color.CEND}')
            print(f'{type(entry.value())}')
        else:
            print(f'{color.CYELLOW}{entry.familyName()}.{entry.groupName()}.{entry.tagName()}{color.CEND} dir: {dir(entry)}')
    '''

    '''
            import inspect
            for name, value in inspect.getmembers(entry):
                print(f' ---> {color.CVIOLET2}{name}:{color.CEND} {value}')
    '''

# ------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------

