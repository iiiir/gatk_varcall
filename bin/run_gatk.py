#!/bin/env python
import sys
import os
import re
import argparse
import subprocess
import sjm
import util


p = argparse.ArgumentParser(description='run_gatk.py -b tiny_b38.bam -o `pwd` --tmp /rgs01/scratch_space/ -r $ref_genome.gatk -j cap_tiny.sjm')
p.add_argument('-b','--bam', metavar='STR', required=True, help='Support for aligned and dedupped BAMs as input')
p.add_argument('-j', '--jobfile', metavar='FILE', help='The jobfile name (default: stdout)')
p.add_argument('-o', '--output', metavar='DIR', required=True, help='The output directory, will be created if not present')
p.add_argument('-r','--regions_file', metavar='FILE', required=True, help='A fiel that defines the regions of GATK parallele run')
p.add_argument('-A','--account',metavar='STR', help='Account that were used to run the pipeline')
p.add_argument('-T', '--tmp', metavar='DIR', required=True, help='The TMP directory for storing intermediate files, will be created if not exist (default=output directory')
p.add_argument('--skip_realn_recal',action='store_true',  help='Skip GATK relingment and recalibration')
p.add_argument('--skip_recal', action='store_true', help='Skip GATK recalibration only')
p.add_argument('--submit', action='store_true', help='Submit the jobs')
args = p.parse_args()

if args.jobfile is None:
    jobfile=None
else:
    jobfile=util.File(args.jobfile)

# set up directory
outdir=util.Dir(args.output)
logdir=util.Dir(outdir, 'log')
tmpdir=outdir
if args.tmp: tmpdir=util.Dir(args.tmp)
tmpdir.mkdirs()
outdir.mkdirs()

sjm.Job.name_prefix="GATK"+"."
sjm.Job.memory="20G" # default if not provided
sjm.Job.queue="pcgp"
sjm.Job.project="CompBio"
if args.account: sjm.Job.sge_options="-A %s" % args.account
tmpdir = getattr(__builtins__, 'str')(tmpdir)
outdir = getattr(__builtins__, 'str')(outdir)

def gatk_realn(bamfile, regions_file):
    jobs=[]
    for region_line in open(args.regions_file):
        region_line = region_line.rstrip('\n')
        if region_line.startswith("#"): continue
        region_name, regions = region_line.split(' ',1)
        job = sjm.Job('gatk_realignment-%s-%s'%(bamfile.prefix, region_name))
        job.memory = "20G"
        job.output = os.path.join(tmpdir, '%s.%s.%s' % (bamfile.prefix, region_name,'realn.bam'))
        job.regions = regions
        job.append('gatk_realn.sh %s %s %s'%(job.output, bamfile.path,region_line))
        jobs.append(job)
    return jobs

def gatk_recal(pjobs):
    jobs = []
    for pjob in pjobs:
        bamfile = util.File(pjob.output)
        job = sjm.Job('gatk_recalibrate-%s'%(bamfile.prefix))
        job.memory = "20G"
        job.output = os.path.join(tmpdir, '%s.%s' % (bamfile.prefix, 'recal.bam'))
        job.regions = pjob.regions
        job.append('gatk_recal.sh %s %s'%(job.output, bamfile.path))
        job.depend(pjob)
        jobs.append(job)
    return jobs
        
def gatk_hc(pjobs):
    jobs = []
    for pjob in pjobs:
        bamfile = util.File(pjob.output)
        job = sjm.Job('gatk_haplotypecaller-%s'%(bamfile.prefix))
        job.memory = "40G"
        job.output = os.path.join(tmpdir, '%s.%s' % (bamfile.prefix, 'g.vcf.gz'))
        job.regions = pjob.regions
        job.append('gatk_hc.sh %s %s %s'%(job.output, bamfile.path, pjob.regions))
        job.depend(pjob)
        jobs.append(job)
    return jobs

def gatk_hc_batch(bamfile, regions_file):
    jobs = []
    for region_line in open(args.regions_file):
        region_line = region_line.rstrip('\n')
        if region_line.startswith("#"): continue
        region_name, regions = region_line.split(' ',1)
        job = sjm.Job('gatk_hc_bam-%s-%s'%(bamfile.prefix, region_name))
        job.memory = "40G"
        job.output = os.path.join(tmpdir, '%s.%s.%s' % (bamfile.prefix, region_name,'g.vcf.gz'))
        job.regions = regions
        job.append('gatk_hc_bam.sh %s %s %s'%(job.output, bamfile.path,regions))
        jobs.append(job)
    return jobs

def gatk_gt(pjobs):
    jobs = []
    for pjob in pjobs:
        gvcffile = util.File(pjob.output, iszipfile=True)
        job = sjm.Job('gatk_genotypeGVCFs-%s'%(gvcffile.prefix))
        job.memory = "15G"
        job.output = os.path.join( tmpdir, '%s.%s' % (gvcffile.prefix, 'gt.vcf.gz') )
        job.regions = pjob.regions
        job.append('gatk_gt.sh %s %s %s'%(job.output, gvcffile.path, pjob.regions))
        job.depend(pjob)
        jobs.append(job)
    return jobs

def gatk_mvcf(pjobs):
    vcfs=[pjob.output for pjob in pjobs]
    job = sjm.Job('gatk_CatVCF-%s'%(bamfile.prefix))
    job.memory = "10G"
    job.output = util.File( os.path.join(outdir, '%s.%s' % (bamfile.prefix, 'vcf.gz')) )
    job.append('gatk_catvcf.sh %s %s' % ( job.output, ' '.join(vcfs) ))
    job.depend(*pjobs)
    return job

def gatk_vqsr(pjob):
    jobs=[]
    vcf = pjob.output
    job = sjm.Job('gatk_VQSR-%s'%(vcf.prefix))
    job.memory = "10G"
    job.append('gatk_vqsr.sh %s' % vcf)
    job.depend(pjob)
    return job

bamfile=util.File(args.bam)

# realn
if not args.skip_realn_recal:
    jobs = gatk_realn(bamfile, args.regions_file)

# recal
if not args.skip_realn_recal and not args.skip_recal:
    jobs = gatk_recal(jobs)

# gvcf
if not args.skip_realn_recal:
    jobs = gatk_hc(jobs)
else:
    jobs = gatk_hc_batch(bamfile, args.regions_file)

# genotyping
jobs = gatk_gt(jobs)
# merge vcf
job = gatk_mvcf(jobs)
# VQSR 
job = gatk_vqsr(job)

descout = sys.stdout if jobfile is None else open(jobfile.path, "w")
descout.write(sjm.Job().depend(job).desc())
descout.flush()

if args.submit:
    print >> sys.stderr, "Submitting jobs (%s) through SJM" % jobfile
    os.system("sjm %s &" %jobfile)
