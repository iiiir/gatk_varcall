#!/bin/env python
import sys
import os
import re
import argparse
import subprocess
import sjm
import util


p = argparse.ArgumentParser(description='Generating the job file for the HugeSeq variant detection pipeline')
p.add_argument('-b','--bam', metavar='STR', required=True, help='Support for aligned and dedupped BAMs as input')
p.add_argument('--skip_realn_recal',action='store_true',  help='Skip GATK relingment and recalibration')
p.add_argument('--skip_recal', action='store_true', help='Skip GATK recalibration only')
p.add_argument('-j', '--jobfile', metavar='FILE', help='The jobfile name (default: stdout)')
p.add_argument('--regions_file', metavar='FILE', default='/nfs_exports/genomes/1/Homo_sapiens/GRCh38/GRCh38_no_alt/GCA_000001405.15_GRCh38_no_alt_analysis_set.fna.gatk', help='A fiel that defines the regions of GATK parallele run')
p.add_argument('-o', '--output', metavar='DIR', required=True, help='The output directory')
p.add_argument('-T', '--tmp', metavar='DIR', help='The TMP directory for storing intermediate files (default=output directory')
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
#logdir.mkdirs()

sjm.Job.name_prefix="GATK"+"."
sjm.Job.memory="%sG"%"10"
sjm.Job.queue="pcgp"
sjm.Job.project="CompBio"
#sjm.Job.cmd_prefix="/home/swang/bin/"
tmpdir = getattr(__builtins__, 'str')(tmpdir)
#sjm.Job.cmd_prefix = sjm.Job.cmd_prefix + ' ' + tmpdir
#sjm.Job.log_dir=logdir.path


def gatk_realn(bamfile, regions_file):
    jobs=[]
    for region_line in open(args.regions_file):
        region_line = region_line.rstrip('\n')
        if region_line.startswith("#"): continue
        region_name, regions = region_line.split(' ',1)
        job = sjm.Job('gatk_realignment-%s-%s'%(bamfile.prefix, region_name))
        job.memory = "14G"
        job.sge_options="-A %s"%'swang'
        job.append('gatk_realn.sh %s %s'%(bamfile.path,region_line))
        job.output = '%s.%s.%s' % (bamfile.prefix, region_name,'realn.bam')
        job.regions = regions
        jobs.append(job)
    return jobs

def gatk_recal(pjobs):
    jobs = []
    for pjob in pjobs:
        bamfile = util.File(pjob.output)
        job = sjm.Job('gatk_recalibrate-%s'%(bamfile.prefix))
        job.memory = "14G"
        job.sge_options="-A %s"%'swang'
        job.append('gatk_recal.sh %s'%(bamfile.path))
        job.output = '%s.%s' % (bamfile.prefix, 'recal.bam')
        job.regions = pjob.regions
        job.depend(pjob)
        jobs.append(job)
    return jobs
        
def gatk_hc(pjobs):
    jobs = []
    for pjob in pjobs:
        bamfile = util.File(pjob.output)
        job = sjm.Job('gatk_haplotypecaller-%s'%(bamfile.prefix))
        job.memory = "14G"
        job.sge_options="-A %s"%'swang'
        job.append('gatk_hc.sh %s %s'%(bamfile.path, pjob.regions))
        job.output = '%s.%s' % (bamfile.prefix, 'g.vcf.gz')
        job.regions = pjob.regions
        job.depend(pjob)
        jobs.append(job)
    return jobs

def gatk_hc_batch(bamfile, regions_file):
    jobs = []
    for region_line in open(args.regions_file):
        region_line = region_line.rstrip('\n')
        if region_line.startswith("#"): continue
        region_name, regions = region_line.split(' ',1)
        job = sjm.Job('gatk_hc_batch-%s-%s'%(bamfile.prefix, region_name))
        job.memory = "14G"
        job.sge_options="-A %s"%'swang'
        job.append('gatk_hc_batch.sh %s %s'%(bamfile.path,region_line))
        job.output = '%s.%s.%s' % (bamfile.prefix, region_name,'g.vcf.gz')
        job.regions = regions
        jobs.append(job)
    return jobs

def gatk_gt(pjobs):
    jobs = []
    for pjob in pjobs:
        gvcffile = util.File(pjob.output, iszipfile=True)
        job = sjm.Job('gatk_genotypeGVCFs-%s'%(gvcffile.prefix))
        job.memory = "14G"
        job.sge_options="-A %s"%'swang'
        job.output = '%s.%s' % (gvcffile.prefix, 'gt.vcf.gz')
        job.append('gatk_gt.sh %s %s %s'%(job.output, gvcffile.path, pjob.regions))
        job.regions = pjob.regions
        job.depend(pjob)
        jobs.append(job)
    return jobs

def gatk_mvcf(pjobs):
    jobs=[]
    vcfs=[pjob.output for pjob in pjobs]
    job = sjm.Job('gatk_CatVCF-%s'%(bamfile.prefix))
    job.memory = "14G"
    job.sge_options="-A %s"%'swang'
    job.output = '%s.%s' % (bamfile.prefix, 'vcf.gz')
    job.append('gatk_catvcf.sh %s %s' % ( job.output, ' '.join(vcfs) ))
    job.depend(*pjobs)
    jobs.append(job)
    return jobs

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
jobs = gatk_mvcf(jobs)

# VQSR
#jobs = gatk_vqsr(jobs, ext)

descout = sys.stdout if jobfile is None else open(jobfile.path, "w")
descout.write(sjm.Job().depend(*jobs).desc())
descout.flush()
