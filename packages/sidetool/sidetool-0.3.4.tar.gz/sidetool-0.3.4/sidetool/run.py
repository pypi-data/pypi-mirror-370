import sys
import os
import argparse   
import subprocess
import sidetool

# read commandline parameters
# call build.run so we can prebuild pyside6 components before we execute the main script
# run the main script via pythonw.exe

def main():
    
    #===================================================================
    # process commandline options 
    #===================================================================

    parser = argparse.ArgumentParser(description='Build ui and qrc files, then run python source')

    parser.add_argument('file',help='python file to run')

    parser._positionals.title = "positional parameters"
    parser._optionals.title = "parameters"

    argcount = len(sys.argv)

    if argcount == 1:
        parser.print_help()
        print('ERROR: No arguments supplied for PythonRun', file=sys.stderr) 
        sys.exit(1)

    args = parser.parse_args()   # will exit here if required parms are not provided

    pythonfile = args.file
    pythonfile = pythonfile.strip("\"' ")   # strip possible quotes and spaces
    pythonfile = os.path.abspath(pythonfile)  # convert to absolute path
    pythonfile = pythonfile.replace("\\", "/")   # flip all backslashes to forward slashes because python prefers

    if not os.path.isfile(pythonfile):    # use unicode instead of str to convert unicode qstring to python string
        print(f"Python file does not exist: {pythonfile}", file=sys.stderr) 
        sys.exit(1)

    #===================================================================
    # build .ui and .qrc files in current folder and all sub folders
    #===================================================================

    sidetool.build()

    #===================================================================
    # call pythonw
    #===================================================================

    command = ['pythonw.exe', '-u', pythonfile]     # this is the new python launcher (pyw.exe) which looks for shebang at top of python source and is installed with python3 but will run python2
    p = subprocess.Popen(command,shell=True) #,stdout = subprocess.PIPE, stderr= subprocess.PIPE) #, startupinfo=startupinfo)

    sys.stdout.flush()

    rc = p.wait()

    output,error = p.communicate()

    sys.stdout.flush()


if __name__ == "__main__":

    main()   