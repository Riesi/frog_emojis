
import glob
import ntpath
import subprocess

files = [f for f in glob.glob("./**/*.svg", recursive=True)]
sizes = [16, 32, 64, 128, 256, 512, 1024, 4096]

for f in files:
    name = ntpath.basename(f).replace(".svg", "")
    for s in sizes:
        subprocess.run(["inkscape", "-z", "-C", "-w", str(s), "-e", "./png/"+str(s)+"/"+name+".png", "-f", f])
