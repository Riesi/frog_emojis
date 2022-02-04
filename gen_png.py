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

import argparse
import glob
import ntpath
import os
import subprocess
import sys
# Dependencies: (optional) git, inkscape, python 3.9


# deletes raster graphics with given name
def delete_graphics(name):
    """Delete each PNG file in name"""
    for file in name:
        for directory in glob.glob(f"./png/**/{file}.png", recursive=True):
            print(f"deleting: {directory}")
            os.remove(directory)

# rasters SVGs via Inkscape
def raster_graphics(files, sizes = None):
    """Rasters each file in files via Inkscape"""
    sizes = [72, 512, 1024] if sizes is None else sizes
    frogs = len(files)-1
    for file in files:
        name = ntpath.basename(file).replace(".svg", "")
        print('\n------------------------------')
        print(f"{frogs} remaining...\nRastering {name}\n")
        frogs = frogs - 1
        for size in sizes:
            # make sure the subdirectories exist
            raster_path = f"./png/{size}/{os.path.dirname(file.removeprefix('svg/').removesuffix('.svg'))}"
            if not os.path.exists(raster_path) :
                os.makedirs(raster_path ,exist_ok=True)
            # invoke Inkscape to raster the given vector graphics
            subprocess.run(["inkscape", file, "-C", "-h", str(size),
                            f"--export-filename={raster_path}/{name}.png"],timeout=30, check=True)

# git add given files
def git_add_raster(files):
    """Git add's each file in files"""
    for file in files:
        file = file.removeprefix('svg/').removesuffix('.svg')
        stream = os.popen(f"git add ./png/**/{file}.png")
        print(stream.read())

# git commit given files
def git_commit_raster():
    """Creates a new autogenerated git commit with the PNGs"""
    stream = os.popen('git commit -m "[png] generate PNGs"')
    print(stream.read())

# create a new tag
def create_tag():
    """Creates a new git tag and names it appropriately"""
    # get tags
    stream = os.popen('git tag -l "auto-v*"')
    output = stream.read()
    tags = output.split('\n')
    tags.remove('')
    # create new tag
    stream = os.popen(f"git tag auto-v{len(tags)}")
    print(stream.read())

# -------------------------------#
#           main section
# -------------------------------#
def main():
    """Main Method"""

    # parse arguments
    parser = argparse.ArgumentParser(description='Automate rasterization of SVGs to PNGs.')
    mutex_group = parser.add_mutually_exclusive_group(required=True)
    mutex_group.add_argument("-a", "--all", action="store_true", help="Generate PNGs of all SVGs.")
    mutex_group.add_argument("-s", "--specific", metavar='S', type=str, nargs="+",
                             help="Generate PNGs for each S in the \"svg\" folder. " +
                                  "The '.svg' suffix is optional.")
    parser.add_argument("-r", "--resolution", metavar='R', type=int, nargs="+",
                        help="Custom resolutions that will be generated instead of the defaults (72, 512, 1024).")
    mutex_group.add_argument("-g", "--git", action="store_true",
                             help="Generates PNGs of SVGs that changed since last auto tag and creates a git commit with them. " +
                                  "Requires 'git' to be installed and located in PATH.")
    # this will error out on invalid argument configurations
    args = parser.parse_args()

    sizes = args.resolution # this is None when no argument is supplied
    files = []

    # if "git" parameter was specified, regenerate since last tag + create git commit
    if args.git:
        # get modified, added, renamed, deleted SVGs since last tag
        # call this on windows a) with PS for the $() and b) replace grep with PS' equivalent
        git_command = 'git diff --name-status $(git describe --tags --abbrev=0 --match "auto-v*") HEAD'
        if sys.platform == "win32":
            os.environ["COMSPEC"] = 'powershell'
            stream = os.popen(f"{git_command} | Select-String svg/")
        else:
            stream = os.popen(f"{git_command} | grep svg/")
        output = stream.read()
        files = output.split('\n')
        files.remove('')

        if len(files) == 0:
            print('No SVGs to regenerate!')
            sys.exit(1)
        additions = [s.removeprefix('A\t') for s in files if 'A\t' in s]
        modifications = [s.removeprefix('M\t') for s in files if 'M\t' in s]
        deleted = [s.removeprefix('D\tsvg/').removesuffix('.svg') for s in files if 'D\t' in s]
        renamed = [s.removeprefix('R100\t').split('\t') for s in files if 'R100\t' in s]

        # also delete the renamed files and regenerate with the new name
        for ren in renamed:
            deleted.append(ren[0].removeprefix('svg/').removesuffix('.svg'))
            modifications.append(ren[1])

        #print('A:' + str(additions))
        #print('M:' + str(modifications))
        #print('D:' + str(deleted))
        #print('R100:' + str(renamed))

        delete_graphics(deleted)
        git_add_raster(deleted)
        print('\nAdditions:')
        raster_graphics(additions, sizes)
        git_add_raster(additions)
        print('\nModifications:')
        raster_graphics(modifications, sizes)
        git_add_raster(modifications)

        # commit and tag
        git_commit_raster()
        create_tag()
    # if "all" parameter was specified, raster all svgs including subfolders
    if args.all:
        files = list(glob.glob('svg/**/*.svg', recursive=True))
        raster_graphics(files, sizes)
    # if "specific" parameter was specified, only render those
    if args.specific:
        if len(sys.argv) == 2:
            print("Please specify at least one file!")
            sys.exit(1)

        for file in sys.argv:
            file = file.removeprefix('svg/').removesuffix('.svg')
            if os.path.exists(f"svg/{file}.svg"):
                files.append(f"svg/{file}.svg")
        raster_graphics(files, sizes)

if __name__ == "__main__":
    main()
