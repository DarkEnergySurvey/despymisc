#!/usr/bin/env python
# A very simple script to remove duplicates from a list.

import sys

filename = sys.argv[1]
col      = int(sys.argv[2])

IDs = []
for line in open(filename).readlines():

    if line[0] == "#":
        continue

    vals = line.split()
    ID   = vals[col]
    if ID not in IDs:
        print line.rstrip()
        IDs.append(ID)
