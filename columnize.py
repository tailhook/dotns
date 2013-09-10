import sys
import os
import fcntl
from time import sleep

files = []

for fn in sys.argv[1:]:
	f = open(fn, 'rt')
	fcntl.fcntl(f.fileno(), fcntl.F_SETFD, os.O_NDELAY)
	files.append(f)

fmt = '{:10.10s} '*len(files)
while True:
	sleep(1)
	data = [f.readline().strip() for f in files]
	print(fmt.format(*data))
