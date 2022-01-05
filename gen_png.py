#!/usr/bin/env python3

import glob
import ntpath
import subprocess
import sys
import os
# Dependencies: grep, git, inkscape, python 3.9


# deletes raster graphics with given name
def delete_graphics(name):
    for f in name:
        for d in glob.glob("./png/**/"+str(f)+".png", recursive=True):
            print('deleting: ' +str(d))
            os.remove(d)

# rasters SVGs via Inkscape
def raster_graphics(files):
    sizes = [16, 32, 64, 128, 256, 512, 1024, 4096]
    frogs = len(files)-1
    for f in files:
        name = ntpath.basename(f).replace(".svg", "")
        print('\n------------------------------\n'+ str(frogs) + ' remaining...\nRastering ' + str(name)+'\n')
        frogs = frogs - 1
        for s in sizes:
            # make sure the subdirectories exist
            width_path = "./png/fixed_width/"+str(s)+"/"+str(os.path.dirname(f.removeprefix('svg/').removesuffix('.svg')))
            height_path = "./png/fixed_height/"+str(s)+"/"+str(os.path.dirname(f.removeprefix('svg/').removesuffix('.svg')))
            if not( os.path.exists(width_path) and os.path.exists(height_path) ):
                os.makedirs(width_path ,exist_ok=True)
                os.makedirs(height_path ,exist_ok=True)
            # invoke Inkscape to raster the given vector graphics
            subprocess.run(["inkscape", f, "-C", "-w", str(s), "--export-filename="+str(width_path)+"/"+name+".png"],timeout=30)
            subprocess.run(["inkscape", f, "-C", "-h", str(s), "--export-filename="+str(height_path)+"/"+name+".png"],timeout=30)

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
# -------------------------------------------------------------------------------------------------------------------------#
# main section
#
files = list()
if len(sys.argv) == 1:
    # get modified, added, renamed, deleted SVGs since last tag
    stream = os.popen('git diff --name-status $(git describe --tags --abbrev=0 --match "auto-v*") HEAD | grep svg/')
    output = stream.read()
    files = output.split('\n')
    files.remove('')

    if len(files) == 0:
        print('nothing to do!')
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
else:
    if sys.argv[1] == 'all':
        files = [f for f in glob.glob("svg**/*.svg", recursive=True)]
    else:
        for f in sys.argv:
            f = f.removeprefix('svg/').removesuffix('.svg')
            if os.path.exists("svg/"+f+".svg"):
                files.append("svg/"+f+".svg")
    raster_graphics(files)

