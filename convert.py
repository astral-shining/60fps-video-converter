import os
import argparse
import subprocess

cores = os.cpu_count()

parser = argparse.ArgumentParser(description='Convert videos to 60fps')
parser.add_argument("file", metavar='FILE', type=str, nargs='?', help='Input file')
parser.add_argument("-s", "--start", default=0, metavar="<seconds>", type=float, help="Start in seconds")
parser.add_argument("-e", "--end", metavar="<seconds>", type=float, help="End in seconds")
parser.add_argument("-j", "--jobs", default=cores, metavar="<jobs>", type=int, help="Number of jobs (default n of cores)")
parser.add_argument("-o", "--output", metavar="<file>", default="output.mp4", type=str, help="output file")

args = parser.parse_args()

if args.end == None:
    p=subprocess.run("ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 " + args.file, shell=True, stdout=subprocess.PIPE)
    if p.returncode != 0:
        exit(p.returncode)
    args.end = float(p.stdout)

d = (args.end-args.start)/6
p = []

files = []
print("Extracting audio...")
subprocess.run("ffmpeg -i {} -ss {} -to {} -ac 1 -c:a copy output.wav".format(args.file, args.start, args.end), shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
print("Done")

print("Converting...")
for i in range(args.jobs):
    foutput = args.output.split(".")[0] + "-" + str(i) + "." + args.output.split(".")[1]
    command = "nice -n 19 ffmpeg -ss {start} -to {end} -i {file} -ac 1 -an -vf \"minterpolate=fps=60:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1\" {output}".format(
        n=foutput,
        output=foutput,
        start=args.start+i*d,
        file=args.file,
        end=args.start+(i+1)*d#-0.016666666666666666
    )
    p.append(subprocess.Popen(command, shell=True, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL))
    files.append(foutput)

files.append("output.opus")
for i in p:
    i.wait()
print("Done")

f = open("join.txt", "w")
for file in files:
    f.write("file '{}'\n".format(file))
f.close()

subprocess.run("ffmpeg -f concat -safe 0 -i join.txt -i output.opus -map 0:v -map 1:a -c copy " + args.output, shell=True)

for file in files:
    os.remove(file)

#f = sys.argv[1]
#start = int(sys.argv[2])
#end = int(sys.argv[3])

#
