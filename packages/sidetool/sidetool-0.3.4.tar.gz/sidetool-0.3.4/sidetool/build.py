import sys
import subprocess
import os

# build .ui and .qrc files in current folder and all sub folders
# this is typically called from sidetool-run or sidetool-compile
    
def processfile(fullpath):

    python3path = os.path.dirname(sys.executable)
    pyrcc = os.path.join(python3path,"Scripts/pyside6-rcc.exe")
    pyuic = os.path.join(python3path,"Scripts/pyside6-uic.exe")

    path,file = os.path.split(fullpath)    
    basename, ext = os.path.splitext(file)

    infile = path + "/" + file

    if ext.lower() != ".qrc" and ext.lower() != ".ui": return
    
    # process .qrc files
    if ext.lower() == ".qrc":

        outfile = path + "/" + basename + '_rc.py'

        if comparefiles(infile, outfile):
            sys.stdout.flush()

            command = [sys.executable,    # path to python interpreter
                       pyrcc, 
                       infile, 
                       '-o', outfile ]

            p = subprocess.Popen(command,shell=True) #,stdout = subprocess.PIPE, stderr= subprocess.PIPE) #, startupinfo=startupinfo)
            rc = p.wait()
            # output,error = p.communicate()

    # process .ui files
    if ext.lower() == ".ui":

        outfile = path + "/" + basename + '_ui.py'

        if comparefiles(infile, outfile):
            sys.stdout.flush()

            command = [sys.executable,   # path to python interpreter
                       pyuic, 
                       infile, 
                       '-o', outfile ]

            p = subprocess.Popen(command,shell=True) #,stdout = subprocess.PIPE, stderr= subprocess.PIPE) #, startupinfo=startupinfo)
            rc = p.wait()

def walk(top, maxdepth):
    dirs, nondirs = [], []
    for name in os.listdir(top):
        (dirs if os.path.isdir(os.path.join(top, name)) else nondirs).append(name)
    yield top, dirs, nondirs
    if maxdepth > 1:
        for name in dirs:
            for x in walk(os.path.join(top, name), maxdepth-1):
                yield x

def comparefiles(infile,outfile):
    """
    compare file dates
    return true if infile is newer or if outfile doesn't exist
    """

    if not os.path.isfile(outfile):   # outfile does not exist 
        return True
    else:             # outfile does exist
        # get infile date and outfile date
        # infile_date = os.path.getmtime(infile)
        # outfile_date = os.path.getmtime(outfile)

        infile_date = os.stat(infile).st_mtime      # quicker than getmtime
        outfile_date = os.stat(outfile).st_mtime    # quicker than getmtime
        
        # if outfile date < infile date then flag = True
        if (outfile_date < infile_date):
            return True

    return False

def main():

    python3path = os.path.dirname(sys.executable)
    pyrcc = os.path.join(python3path,"Scripts/pyside6-rcc.exe")
    pyuic = os.path.join(python3path,"Scripts/pyside6-uic.exe")

    if not os.path.isfile(pyrcc):
        print("Warning: pyrcc not found: {}".format(pyrcc), file=sys.stderr)
        sys.exit(1)

    if not os.path.isfile(pyuic):
        print("Warning: pyuic not found: {}".format(pyuic), file=sys.stderr)
        sys.exit(1)

    #-----------------------------------------------------------------
    # build .ui and .qrc files in current folder and all sub folders
    #-----------------------------------------------------------------

    cwd = os.getcwd()  # e.g. cwd = E:\EDMS\python3\MUD

    # traverse but only to a max depth of 2
    depth = 2
    for path, subdirs, files in walk(cwd, depth):
        path = path.replace("\\", "/")   # flip all backslashes to forward slashes because python prefers
        for file in files:
            fullpath = os.path.join(path,file) 
            processfile(fullpath)

    sys.stdout.flush()

if __name__ == "__main__":

    main()     