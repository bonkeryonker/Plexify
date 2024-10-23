import os
import sys
import re
import shutil

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

    TODO:
        Fix case where shutil.move will raise an exception if destination directory already has file with same name as source. 
        (https://stackoverflow.com/questions/31813504/move-and-replace-if-same-file-name-already-exists)

        Also, shutil.move simply calls os.rename in most cases. If unexpected errors occur, look into this as well.

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
            print("Creating directory: %s" % currentSeasonPath)
            os.makedirs(currentSeasonPath)
        movedCount += 1
        shutil.move(_path + '/' + f, currentSeasonPath + '/' + f)
    print("%d files sorted into %d unique Seasons." % (movedCount, seasonCount))       
    
     
if __name__ == "__main__":
    #Verify that the user has correct number of args
    if len(sys.argv) == 3:
        path = sys.argv[1]
        extension = sys.argv[2]

        print("Looking in %s for *%s" % (path, extension))
        fileList = trimFiles(getFiles(path), extension)
        fileList = renameFiles(fileList, path)
        makeSeasonDirs(fileList, path)
    else:
        print("Two arguments expected.\n\t(Example: plexify.py /path/to/file .fileExtension)")