#---------------------------------------------------------------------
# console app to compile python source to exe using pyinstaller
# 
# 1. read commandline params
# 2. build spec file for desired compiletype
# 3. call pyinstaller build
#---------------------------------------------------------------------

import sys
import os
import argparse   # commandline option parsing
import subprocess

import sidetool

def main():

    #---------------------------------------------------------------------
    # process commandline options 
    #---------------------------------------------------------------------

    parser = argparse.ArgumentParser(description='Compile python source into exe using pyinstaller')

    parser.add_argument('--file', 
                        dest='file',
                        required=True,
                        help='python file to compile to exe')      

    parser.add_argument('--type',
                        dest='type',
                        required=True,
                        choices=['onefile', 'onedir', 'console'],
                        help='type of exe to build')

    parser.add_argument('--icon',
                        dest='icon',
                        default='',
                        help='ico file') 

    parser.add_argument('--embed',
                        dest='embed',
                        default='',
                        help='comma delimited list of files to embed') 

    parser._positionals.title = "positional parameters"
    parser._optionals.title = "parameters"

    argcount = len(sys.argv)

    # if no args supplied, then display help
    if argcount == 1:
        parser.print_help()
        sys.exit()

    args = parser.parse_args()   # will exit here if required parms are not provided

    pythonfile     = args.file
    iconfile       = args.icon
    compiletype    = args.type
    embedlist      = args.embed

    # strip possible quotes and spaces
    pythonfile     = pythonfile.strip("\"' ")   
    iconfile       = iconfile.strip("\"' ")   
    compiletype    = compiletype.strip("\"' ")   
    embedlist      = embedlist.strip("\"' ")   

    # file must be a file and must exist
    if not os.path.isfile(pythonfile):    # use unicode instead of str to convert unicode qstring to python string
        print ( f"ERROR: Python file does not exist: {pythonfile}")
        #sys.stdout.flush()
        sys.exit()

    # file must be a file and must exist
    if iconfile != "":
        if not os.path.isfile(iconfile):    # use unicode instead of str to convert unicode qstring to python string
            print ( f"ERROR: Icon file does not exist: {iconfile}")
            sys.exit()

    pythonfile = os.path.abspath(pythonfile)  # convert to absolute path (spec file expects absolute path)
    pythonfile = pythonfile.replace("\\", "/")  

    pgm_path = os.path.dirname(pythonfile)
    pgm_filename = os.path.basename(pythonfile)
    pgm_basename, pgm_ext = os.path.splitext(pgm_filename) 

    print ("\n__________________ Compile __________________")

    print ("----------- Settings -----------")
    print (f"    python file: {pgm_filename}")
    print (f"      icon file: {iconfile}")
    print (f"   compile type: {compiletype}")
    print (f"     embed list: {embedlist}")

    sys.stdout.flush()

    #-------------------------------------------------------------------
    # build .ui and .qrc files in current folder and all sub folders
    #-------------------------------------------------------------------

    sidetool.build()

    #-------------------------------------------------------------------
    # build spec file data list for embedding files
    # typically for embedding dll, exe, chm ... etc.
    #-------------------------------------------------------------------

    # Example a.datas line for file Excel2MySQL.chm
    # a.datas += [('Excel2MySQL.chm', 'Excel2MySQL.chm', 'DATA')] 

    if embedlist == "":
        data = ""
    else:
        data = ""
        embedlist = embedlist.split(',')   # convert comma delimited list into a python list using split method
        for item in embedlist:
            filename = os.path.basename(item)
            data += f"a.datas += [('{filename}', '{item}', 'DATA')]\n"
        data = data.strip()   # remove leading and trailing blank lines

    # these files appear unused in many python programs and would therefore only bloat the dist exe.
    # HOWEVER, if your exe crashes or is strangely missing functionality that otherwise appears when you run .py
    # then maybe you need to no longer exclude 1 or more of the following excluded files
    excludeDLLs = f"""
to_keep = []
to_exclude = ['opengl32sw.dll', 
              'Qt6Network.dll', 
              'Qt6Pdf.dll', 
              'Qt6Pdf.dll.dll', 
              'Qt6QmlModels.dll', 
              'Qt6Qml.dll', 
              'libssl-3.dll', 
              'Qt6Quick.dll', 
              'Qt6Svg.dll', 
              'libcrypto-3.dll', 
              'QtNetwork.pyd', 
              'Qt6VirtualKeyboard.dll', 
              'qtuiotouchplugin.dll', 
              'qsvgicon.dll', 
              'qnetworklistmanager.dll', 
              'qtvirtualkeyboardplugin.dll', 
              'qwindowsvistastyle.dll', 
              'qcertonlybackend.dll', 
              'qopensslbackend.dll', 
              'qschannelbackend.dll', 
              'Qt6OpenGL.dll']
for (dest, source, kind) in a.binaries:   # Iterate through the list of included binaries.
    if os.path.split(dest)[1] in to_exclude: continue
    to_keep.append((dest, source, kind))
a.binaries = to_keep  # Replace list of data files with filtered one.
    """

              # 'unicodedata.pyd', 

    #-------------------------------------------------------------------
    # define iconspec
    #-------------------------------------------------------------------

    # examples:
    # iconfile = f"myicon.ico"
    # iconfile = f"./icons/myicon.ico"

    if iconfile != "": 
        iconspec = f", icon='{iconfile}'"
    else:
        iconspec = ""

    #-------------------------------------------------------------------
    # create spec file name
    #-------------------------------------------------------------------

    specfile = pgm_path + "/" + pgm_basename + ".spec"
    print (f"specfile={specfile}")
    sys.stdout.flush()

    #-------------------------------------------------------------------
    # build specdata for console or onefile
    #-------------------------------------------------------------------

    if compiletype != "onedir":

        if compiletype == "console":
            value = "True"
        elif compiletype == "onefile":
            value = "False"

        specdata = f"""
# -*- mode: python -*-
a = Analysis(['{pythonfile}'],
             pathex=['./lib',
                     '../lib',
                     '../../lib',
                     '../../../lib',
                     './widgets',
                     './dialogs',                     
                     './views',                     
                     '{pgm_path}',                     
                    ],
             hiddenimports=[])
{data}

{excludeDLLs}

for d in a.datas:
    if 'pyconfig' in d[0]:
        a.datas.remove(d)
        break
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='{pgm_basename}.exe',
          debug=False,
          strip=None,
          upx=False,
          console={value} {iconspec})
        """

    #-------------------------------------
    # build specdata for onedir
    #-------------------------------------

    if compiletype == "onedir":

        specdata = f"""
# -*- mode: python -*-
a = Analysis(['{pythonfile}'],
             pathex=['./lib',
                     '../lib',
                     '../../lib',
                     '../../../lib',
                     './widgets',
                     './dialogs',                     
                     './views',  
                     '{pgm_path}',                     
                    ],
             hiddenimports=[])
{data}

{excludeDLLs}

pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='{pgm_basename}.exe',
          debug=False,
          strip=None,
          upx=False,
          console=False {iconspec})
coll = COLLECT(exe,
               a.binaries,
               a.datas,
               strip=None,
               upx=False,
               name='{pgm_basename}')
        """

    #-------------------------------------------------------------------
    # write specdata to file
    #-------------------------------------------------------------------

    specdata = specdata.strip()   # remove leading and trailing blank lines caused by """ notation

    fout = open(specfile, 'w')      # open file for write
    fout.write(specdata)
    fout.close()

    print (f"Generated specfile = {specfile}")

    #-------------------------------------------------------------------
    # calls pyinstaller build
    # c:\python27\python.exe -OO c:\pyinstaller\utils\build.py excel2mysqlCLI.spec
    #-------------------------------------------------------------------

    print ("Calling Pyinstaller Build...")
    sys.stdout.flush()

    #sys.stdout.flush()   # this will flush and force the print statements to appear immediately.

    # hide the command window
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

    # run with basic optimizations
    # python -O -m PyInstaller myscript.py
    # OR discard docstrings
    # python -OO -m PyInstaller myscript.py

    # command = [sys.executable,'-OO','c:/python37/scripts/pyinstaller-script.py', specfile ]   # removes docstrings, so it is slightly smaller than above
    # command = [sys.executable, '-OO', '-m', 'PyInstaller', specfile]  
    command = [sys.executable, '-m', 'PyInstaller', specfile]     # had to disable -OO because winevt and pycparser has a known bug which crashes pyinstaller

    p = subprocess.Popen(command,shell=True) #,stdout = subprocess.PIPE, stderr= subprocess.PIPE) #, startupinfo=startupinfo)

    p.wait()
    output,error = p.communicate()

    # print ("Compile Done.")
    print("___________________________________________________")
    print("")
    sys.stdout.flush()

if __name__ == "__main__":

    main()   