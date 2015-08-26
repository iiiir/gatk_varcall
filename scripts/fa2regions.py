#!/bin/env python
import sys
import os
import argparse

p = argparse.ArgumentParser()
p.add_argument('--fai',help='FASTA fai indexing file')
p.add_argument('--size', type=int, help='size in mega bases for partitioning parrallele jobs')
args = p.parse_args()

if os.path.isfile(args.fai):
    faidx = args.fai
else:
    print >> sys.stderr, "Does not exist: %s" % args.fai
    sys.exit(1)

region_size = args.size*1000*1000 # Megabytes

print "#NAME REGIONS"
for line in open(faidx):
    fields = line.strip().split("\t")
    chrom_name = fields[0]
    chrom_length = int(fields[1])
    region_start = 1
    while region_start < chrom_length:
        start = region_start
        end = region_start + region_size -1
        if end > chrom_length:
            end = chrom_length
        optN = chrom_name + "_" + str(region_start) + "_" + str(end)
        optL = chrom_name + ":" + str(region_start) + "-" + str(end)
        print "%s %s" % (optN, optL)
        region_start = end + 1


