
import glob
import ntpath
import subprocess
import sys
import os

files = list()
if len(sys.argv) == 1:
    files = [f for f in glob.glob("./**/*.svg", recursive=True)]
else:
    for f in sys.argv:
        if os.path.exists("./svg/"+f+".svg"):
            files.append("./svg/"+f+".svg")

sizes = [16, 32, 64, 128, 256, 512, 1024, 4096]

for f in files:
    name = ntpath.basename(f).replace(".svg", "")
    for s in sizes:
        subprocess.run(["inkscape", "-z", "-C", "-w", str(s), "-e", "./png/"+str(s)+"/"+name+".png", "-f", f])
#        subprocess.run(["inkscape", "-z", "-C", "-w", str(s), "--export-file=./png/"+str(s)+"/"+name+".png", f])        
