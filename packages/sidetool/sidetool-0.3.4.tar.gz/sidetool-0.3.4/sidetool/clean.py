# delete __pycache__ folder
# delete *_ui.py"
# delete *_rc.py"
# delete *_pyc.py"
# delete *_pyo.py"
# delete pyinstaller build folder
# delete pyinstaller dist folder
# delete .spec files in current folder

# -----------------------------------------------------------------
# cleanup pyside6 temp files
# -----------------------------------------------------------------

import sys
import os
import shutil

# -----------------------------------------------------------------
# traverse current directory and all subfolders
# -----------------------------------------------------------------

def main():

    cwd = os.getcwd()
    cwd = cwd.replace("\\", "/")

    print("")
    print("Cleaning %s" % cwd)
    sys.stdout.flush()

    for path, subdirs, files in os.walk(cwd):

        parent, lastfolder = os.path.split(path)     # get last folder in path

        # python prefers forward slashes
        path = path.replace("\\", "/")   # flip all backslashes to forward slashes

        if lastfolder == "__pycache__":
            if os.path.exists(path):
                print("   deleting %s" % path)
                sys.stdout.flush()
                shutil.rmtree(path)  # recursively delete folder
                continue

        for file in files:

            if file.lower().endswith("_ui.py"):
                print("   removing %s" % file)
                sys.stdout.flush()
                os.remove(path+'/'+file)

            if file.lower().endswith("_rc.py"):
                print("   removing %s" % file)
                sys.stdout.flush()
                os.remove(path+'/'+file)

            if file.lower().endswith(".pyc"):
                print("   removing %s" % file)
                sys.stdout.flush()
                os.remove(path+'/'+file)

            if file.lower().endswith(".pyo"):
                print("   removing %s" % file)
                sys.stdout.flush()
                os.remove(path+'/'+file)

    # -----------------------------------------------------------------
    # cleanup pyinstaller build and dist folders
    # -----------------------------------------------------------------

    build_folder = "%s/build" % cwd
    if os.path.exists(build_folder):
        print("   removing %s" % build_folder)
        sys.stdout.flush()
        shutil.rmtree(build_folder)  # recursively delete folder

    dist_folder = "%s/dist" % cwd
    if os.path.exists(dist_folder):
        print("   removing %s" % dist_folder)
        sys.stdout.flush()
        shutil.rmtree(dist_folder)   # recursively delete folder

    # -----------------------------------------------------------------
    # remove .spec files in current folder
    # -----------------------------------------------------------------

    files = os.listdir(cwd)  # get files in current directory

    for file in files:

        base, ext = os.path.splitext(file)

        if ext.lower() == ".spec":
            fullpath = "%s/%s" % (cwd, file)
            print("   removing %s" % fullpath)
            sys.stdout.flush()
            os.remove(fullpath)


if __name__ == "__main__":

    main()   