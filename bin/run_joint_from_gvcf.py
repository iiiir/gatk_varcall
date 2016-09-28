#!/bin/env python
import sys
import os
import argparse
import subprocess
import sjm
import util
import random
import string

p = argparse.ArgumentParser(description='run_joint_from_gvcf.py -c 30 -v 1.chr1.g.vcf.gz 2.chr1.g.vcf.gz -o chr1.gt.vcf.gz -O folder -t chr1.merge -T chr1 -j jobs.sjm')
g = p.add_mutually_exclusive_group(required=True)
g.add_argument('-v', '--gvcfs', metavar='FILE', nargs="+", help='gvcf files, >200 expected')
g.add_argument('-V', '--gvcf_list', metavar='FILE', help='gvcf files, >200 expected')
p.add_argument('-c', '--merge_count', metavar='COUNT', type=int, default=50, help='Merge by N samples: default[50]')
p.add_argument('-o', '--output', metavar='NAME', required=True, help='The joint call VCF')
p.add_argument('-O', '--outdir', metavar='DIR', required=True, help='The output directory for vcf file')
p.add_argument('-t', '--temp_prefix', metavar='NAME', required=True, help='The merged gvcf file prefix')
p.add_argument('-T', '--tempdir', metavar='DIR', required=True, help='The directory to hold merged gvcfs')
p.add_argument('-j', '--jobfile', metavar='FILE', help='The jobfile name (default: stdout)')
args = p.parse_args()

outdir = util.Dir(args.outdir)
outdir.mkdirs()
tmpdir = util.Dir(args.tempdir)
tmpdir.mkdirs()

if args.jobfile is None:
    jobfile=None
else:
    jobfile=util.File(args.jobfile)

sjm.Job.name_prefix="GATK-joint"+"."
sjm.Job.memory="12G"
sjm.Job.queue="pcgp"
sjm.Job.project="CompBio"

outdir = getattr(__builtins__, 'str')(outdir)

def merge_gvcf(gvcfs):
    jobs  = []
    gvcf_batches = [gvcfs[x:x+args.merge_count] for x in range(0,len(gvcfs),args.merge_count)]
    for i, gvcf_batch in enumerate(gvcf_batches):
        ogvcf = util.File(os.path.join( args.tempdir, '%s.batch%d.g.vcf.gz' % (args.temp_prefix, i) ))
        job = sjm.Job('gatk_combine_gvcf-%s' % ogvcf.name )
        job.memory = "40G"
        job.output = ogvcf
        job.append('gatk_combine_gvcf.sh %s %s' % (job.output, " ".join(gvcf_batch)) )
        jobs.append(job)
    return jobs

def gatk_joint(pjobs):
    jobs   = []
    gvcfs  = [pjob.output.path for pjob in pjobs]
    outvcf = util.File(os.path.join(args.outdir, args.output))
    job = sjm.Job('GATK-joint-gt-%s' % outvcf.name )
    job.memory = "20G"
    job.output = outvcf
    job.append('gatk_gt_joint.sh %s %s'%(job.output, ' '.join( gvcfs ) ) )
    job.depend(*pjobs)
    jobs.append(job)
    return jobs

def main(gvcfs):
    jobs = merge_gvcf(gvcfs)
    jobs = gatk_joint(jobs)

    descout = sys.stdout if jobfile is None else open(jobfile.path, "w")
    descout.write(sjm.Job().depend(*jobs).desc())
    descout.flush()

if __name__ == "__main__":
    if args.gvcf_list:
        gvcfs = [f.rstrip() for f in open(gvcf_list).readlines()]
    else:
        gvcfs = args.gvcfs
    #print gvcfs
    main(gvcfs)
