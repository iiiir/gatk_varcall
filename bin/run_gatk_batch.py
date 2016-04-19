#!/bin/env python
import sys
import os
import re
import argparse
import subprocess
import sjm
import util

# run_gatk_batch.py -B bam.lst -o `pwd` --tmp /rgs01/scratch_space -r $ref_genome.gatk -j joint.sjm -v joint_call

p = argparse.ArgumentParser(description='run_gatk_batch.py -B bam.lst -o `pwd` --tmp /rgs01/scratch_space -r $ref_genome.gatk -j joint.sjm -v joint_call')
g1 = p.add_mutually_exclusive_group(required=True)
g2 = p.add_mutually_exclusive_group()
p.add_argument('-A','--account',metavar='STR', help='Account that were used to run the pipeline')
g1.add_argument('-b','--bam', metavar='STR', help='Support for aligned and dedupped BAMs as input')
g1.add_argument('-B','--bamlist', metavar='STR', help='Support for aligned and dedupped BAMs as input, a file contain list of bams')
p.add_argument('-j', '--jobfile', metavar='FILE', help='The jobfile name (default: stdout)')
p.add_argument('-o', '--output', metavar='DIR', required=True, help='The output directory, will be created if not present')
p.add_argument('-r','--regions_file', metavar='FILE', required=True, help='A fiel that defines the regions of GATK parallele run')
p.add_argument('-T', '--tmp', metavar='DIR', required=True, help='The TMP directory for storing intermediate files (default=output directory')
p.add_argument('-v', '--joint_call_vcf',metavar='FILE', required=True, help='Final single vcf output file if choose joint call')
g2.add_argument('--skip_realn_recal',action='store_true',  help='Skip GATK relingment and recalibration')
g2.add_argument('--skip_recal', action='store_true', help='Skip GATK recalibration only')
p.add_argument('--submit', action='store_true', help='Submit the jobs')
args = p.parse_args()

if args.jobfile is None:
    jobfile=None
else:
    jobfile=util.File(args.jobfile)

outdir=util.Dir(args.output)
logdir=util.Dir(outdir, 'log')
tmpdir=outdir
if args.tmp: tmpdir=util.Dir(args.tmp)
tmpdir.mkdirs()
outdir.mkdirs()

sjm.Job.name_prefix="GATK"+"."
sjm.Job.memory="20G" 
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

def gatk_hc_bam(bamfile, regions_file):
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

def gatk_gt_joint(pjobs, args, suffix):
    jobs = []
    for region_line in open(args.regions_file):
        region_line = region_line.rstrip('\n')
        if region_line.startswith("#"): continue
        region_name, regions = region_line.split(' ',1)
        ext = '.' + region_name + suffix + '.vcf.gz'
        job = sjm.Job('gatk_genotypeGVCFs-joint-%s'%region_name )
        job.memory = "15G"
        job.output = os.path.join( tmpdir, '%s%s' % (args.joint_call_vcf, ext) )
         
        pjobs_reg   = [pjob for pjob in pjobs if pjob.output.endswith(ext)]
        job_input = [pjob.output for pjob in pjobs_reg]
        job.append('gatk_gt_joint.sh %s %s'%(job.output, ' '.join(job_input)) )
        job.depend(*pjobs_reg)
        jobs.append(job)
    return jobs

def gatk_mvcf(pjobs, vcfout):
    vcfs=[pjob.output for pjob in pjobs]
    job = sjm.Job('gatk_CatVCF-%s'%(bamfile.prefix))
    job.memory = "10G"
    job.output = util.File( os.path.join(outdir, vcfout) )
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

if args.bamlist is not None:
    jobs = []
    suffix = ''
    vcfout = '%s.%s' % (args.joint_call_vcf, 'vcf.gz')
    if args.skip_realn_recal:
        print("not supported yet")
        sys.exit(0)
        jobs = gatk_hc_bam(bamfile, args.regions_file)
    else:
        for bam in open(args.bamlist):
            bamfile=util.File(bam.strip())
            jobs = jobs + gatk_realn(bamfile, args.regions_file)
        suffix = suffix + '.realn'

        if not args.skip_recal:
            jobs = gatk_recal(jobs)
            suffix = suffix + '.recal'
        jobs = gatk_hc(jobs)
        suffix = suffix + '.g'

else:
    bamfile=util.File(args.bam)
    vcfout = '%s.%s' % (bamfile.prefix, 'vcf.gz')
    if args.skip_realn_recal:
        jobs = gatk_hc_bam(bamfile, args.regions_file)
    else:
        jobs = gatk_realn(bamfile, args.regions_file)
        if not args.skip_recal:
            jobs = gatk_recal(jobs)
        jobs = gatk_hc(jobs)

if args.joint_call_vcf:
    jobs = gatk_gt_joint(jobs, args, suffix)
else:
    jobs = gatk_gt(jobs)

job = gatk_mvcf(jobs, vcfout)
job = gatk_vqsr(job)

descout = sys.stdout if jobfile is None else open(jobfile.path, "w")
descout.write(sjm.Job().depend(job).desc())
descout.flush()

if args.submit:
    print >> sys.stderr, "Submitting jobs (%s) through SJM" % jobfile
    os.system("sjm %s &" %jobfile)
