import os
import sys
import re
import shutil

def digoutDirectories(_path, warnFileCount = 100):
    """Recursively loops through all subdirectories and moves all files up to the folder denoted by _path.
        If totalFilecount >= warnFileCount, ask the user if they're sure they want to continue.
    
    TODO:
        Rename files that may be duplicate named so shutil.move works
        Clean up all directories

    Returns:
        bool: True if the user did not abort.
    """
    totalFileCount = 0
    totalDirCount = 0
    fileList = []
    for root, dirs, files in os.walk(_path):
        totalDirCount += len(dirs)
        for file in files:
            totalFileCount += 1
            fileList.append( (root, file) )
    
    if totalFileCount >= warnFileCount: #Ask user for confirmation if lots of files
        print("This operation will move %d files into the %s directory, and delete %d source directories.\nAre you sure you want to continue? (y/N)" % (totalFileCount, _path, totalDirCount))
        while(True):
            userin = input().upper()
            if userin == "Y":
                break
            else:
                return False
    
    #move files
    duplicateFileCount = 0
    for f in fileList:
        sourcePath = f[0] + '/' + f[1]
        destPath = _path + '/' + f[1]
        if not os.path.exists(destPath):
            shutil.move(sourcePath, destPath)
        else:
            duplicateFileCount += 1
            duplicateFileCountStr = str(duplicateFileCount)
            shutil.move(sourcePath, _path + "/Copy (" + duplicateFileCountStr + ") - " + f[1])

    #delete all directories and subdirectories
    for dirpath, _, _ in os.walk(_path, topdown=False):
        if dirpath == _path:
            break
        try:
            os.rmdir(dirpath)
        except OSError as ex:
            print(ex)
    
    print("Moved %d files into %s. %d source directories deleted." % (totalFileCount, _path, totalDirCount))
    return True
    

    


def getFiles(_path):
    """Gets all files in passed directory.

    Returns:
        list: A list of all filenames in the current directory.
    """
    fileList = [f for f in os.listdir(_path) if os.path.isfile(_path + '/' + f)]
    return fileList

def trimFiles(_fileList, _fileExtension):
    """Loops through the list and checks if the file extensions match the passed argument.

    Returns:
        list: A list of all filenames that share the _fileExtension extension.
    """
    fileCount = 0
    retList = []
    for f in _fileList:
        tupleName = os.path.splitext(f)
        if tupleName[1] == _fileExtension:
            fileCount += 1
            retList.append(tupleName)
    print("%d files found of type %s" % (fileCount, _fileExtension))
    return retList

def renameFiles(_fileList, _path):
    """Loops through the list and renames all files to work nicely with Plex.
        IE: 'myshow.random.S01E01.720p.HEVC.x265.mkv' becomes 'S01E01.mkv'

    Returns:
        list: A list of all filenames formatted to match the above example
    """
    matchCounter = 0
    regexPattern = r"[sS]\d\d[eE]\d\d"
    retList = []

    for f in _fileList:
        match = re.search(regexPattern, f[0])
        if match:
            matchCounter += 1
            #print(match.group())
            oldName = f[0] + f[1]
            newName = (match.group()).upper() + f[1]
            retList.append(newName)
            os.rename(_path + '/' + oldName, _path + '/' + newName)
    print("%d matches found and renamed." % matchCounter)
    return retList

def makeSeasonDirs(_fileList, _path):
    """Counts how many unique seasons are in the list, and creates that many directories. Sorts files into their respective directories.

    Returns:
        void
    """
    seasonCount = 0
    movedCount = 0
    seasonPath = _path + "/Season_"

    for f in _fileList:
        seasonInt = int(f[1:3]) #f[0] is already in format of "S01E01.mkv", so we can directly index the string        
        currentSeasonPath = seasonPath + str(seasonInt) 

        if not os.path.exists(currentSeasonPath):
            seasonCount += 1
            #print("Creating directory: %s" % currentSeasonPath)
            os.makedirs(currentSeasonPath)
        movedCount += 1
        shutil.move(_path + '/' + f, currentSeasonPath + '/' + f)
    print("%d files sorted into %d unique Season directories." % (movedCount, seasonCount))       

def promptAndCleanup(_path):
    """Prompts the user if they'd like to remove all remaining files in the root directory.

    Returns:
        void
    """
    print("Would you like to delete all non-directory files in %s? (Y/n)" % _path)
    while True:
        userin = input().upper()
        if userin == "N":
            return
        else:
            break
    for f in getFiles(_path):
        os.remove(_path + '/' + f)
    
    
     
if __name__ == "__main__":
    #Verify that the user has correct number of args
    if len(sys.argv) == 3:
        path = sys.argv[1]
        extension = sys.argv[2]

        if not digoutDirectories(path):
            print("Aborted.")
            exit()
        
        fileList = trimFiles(getFiles(path), extension)
        fileList = renameFiles(fileList, path)
        makeSeasonDirs(fileList, path)
        promptAndCleanup(path)
            
    else:
        print("Two arguments expected.\n\t(Example: plexify.py /path/to/file .fileExtension)")