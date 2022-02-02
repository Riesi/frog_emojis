#!/usr/bin/env python3

###########################################################################
#    Copyright (C) 2022  Stefan Riesenberger
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
###########################################################################

import glob
import ntpath
import subprocess
import sys
import os
import platform
# Dependencies: (optional) git, inkscape, python 3.9


# deletes raster graphics with given name
def delete_graphics(name):
    for f in name:
        for d in glob.glob("./png/**/"+str(f)+".png", recursive=True):
            print('deleting: ' +str(d))
            os.remove(d)

# rasters SVGs via Inkscape
def raster_graphics(files):
    # TODO: make this adjustable via option/parameter
    sizes = [72, 512, 1024]
    frogs = len(files)-1
    for f in files:
        name = ntpath.basename(f).replace(".svg", "")
        print('\n------------------------------\n'+ str(frogs) + ' remaining...\nRastering ' + str(name)+'\n')
        frogs = frogs - 1
        for s in sizes:
            # make sure the subdirectories exist
            raster_path = "./png/"+str(s)+"/"+str(os.path.dirname(f.removeprefix('svg/').removesuffix('.svg')))
            if not(os.path.exists(raster_path) ):
                os.makedirs(raster_path ,exist_ok=True)
            # invoke Inkscape to raster the given vector graphics
            subprocess.run(["inkscape", f, "-C", "-h", str(s), "--export-filename="+str(raster_path)+"/"+name+".png"],timeout=30)

# git add given files
def git_add_raster(files):
    for f in files:
        f = f.removeprefix('svg/').removesuffix('.svg')
        stream = os.popen('git add ./png/**/'+str(f)+'.png') 
        print(stream.read())

# git commit given files
def git_commit_raster():
    stream = os.popen('git commit -m "[png] generate PNGs"') 
    print(stream.read())
    
# create a new tag
def create_tag():
    # get tags
    stream = os.popen('git tag -l "auto-v*"') 
    output = stream.read()
    tags = output.split('\n')
    tags.remove('')
    # create new tag
    stream = os.popen('git tag auto-v'+str(len(tags))) 
    print(stream.read())
    
# print help message
def print_help():
    print("gen_png.py [OPTION]")
    print("")
    print("-h, --help                       Shows this help message.")
    print("-a, --all                        Regenerates all PNGs.")
    print("-s, --specific [FILENAME]...     Regenerate the PNGs for each FILENAME in the \"svg\" folder. The '.svg' suffix is optional.")
    print("-g, --git                        Regenerates all PNGs and creates a git commit for them. Requires 'git' to be installed and located in PATH.")
    
# -------------------------------------------------------------------------------------------------------------------------#
# main section
#
files = list()
# if there are no arguments (or help parameter was specified), print help and exit
if len(sys.argv) == 1 or sys.argv[1] == '-h' or sys.argv[1] == '--help':
    print_help()
    exit(1)
# if "git" parameter was specified, regenerate since last tag + create git commit
elif sys.argv[1] == '-g' or sys.argv[1] == '--git':
    # get modified, added, renamed, deleted SVGs since last tag
    # call this on windows a) with PS for the $() and b) replace grep with PS' equivalent
    gitCommand = 'git diff --name-status $(git describe --tags --abbrev=0 --match "auto-v*") HEAD'
    if sys.platform == "win32":
        os.environ["COMSPEC"] = 'powershell'
        stream = os.popen(gitCommand + ' | Select-String svg/')
    else:
        stream = os.popen(gitCommand + ' | grep svg/')
    output = stream.read()
    files = output.split('\n')
    files.remove('')

    if len(files) == 0:
        print('No SVGs to regenerate!')
        exit()
    additions = [s.removeprefix('A\t') for s in files if 'A\t' in s]
    modifications = [s.removeprefix('M\t') for s in files if 'M\t' in s]
    deleted = [s.removeprefix('D\tsvg/').removesuffix('.svg') for s in files if 'D\t' in s]
    renamed = [s.removeprefix('R100\t').split('\t') for s in files if 'R100\t' in s]
    
    # also delete the renamed files and regenerate with the new name
    for r in renamed:
        deleted.append(r[0].removeprefix('svg/').removesuffix('.svg'))
        modifications.append(r[1])

    #print('A:' + str(additions))
    #print('M:' + str(modifications))
    #print('D:' + str(deleted))
    #print('R100:' + str(renamed))

    delete_graphics(deleted)
    git_add_raster(deleted)
    print('\nAdditions:')
    raster_graphics(additions)
    git_add_raster(additions)
    print('\nModifications:')
    raster_graphics(modifications)
    git_add_raster(modifications)

    # commit and tag
    git_commit_raster()
    create_tag()
# if "all" parameter was specified, raster all svgs including subfolders
elif sys.argv[1] == '-a' or sys.argv[1] == '--all':
    files = [f for f in glob.glob("svg/**/*.svg", recursive=True)]
    raster_graphics(files)
# if "specific" parameter was specified, only render those
elif sys.argv[1] == '-s' or sys.argv[1] == '--specific':
    if len(sys.argv) == 2:
        print("Please specify at least one file!")
        exit(1)

    for f in sys.argv:
        f = f.removeprefix('svg/').removesuffix('.svg')
        if os.path.exists("svg/"+f+".svg"):
            files.append("svg/"+f+".svg")
    raster_graphics(files)
# unknown option
else:
    print("Unknown option!")
    print("Try 'gen_png.py --help' for more information.")
    
