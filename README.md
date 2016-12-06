### gatk_varcall
GATK best practice variant calling pipeline for SNPs and INDELs
The pipeline is for GRCh37 and GRCh38.

### dependencies
+ python 2.7
+ SJM (simple job manager)
+ GATK 3.0+
+ bgzip and tabix 1.2.1
+ LSF batch system (or other)

### pipeline set up
$ vi gatk_varcall/modulefiles/gatk_varcall/b38    
  change "set pipeline_dir /home/swang/app/gatk_varcall" to point to correct path    
$ chmod +x gatk_varcall/bin/*    

### usage
#### 1. variant call for individual sample
$ cd gatk_varcall/test/
$ run_gatk.py -b tiny_b38.bam -o `pwd` --tmp /rgs01/scratch_space/cap_tiny_test -r ../scripts/GCA_000001405.15_GRCh38_no_alt_analysis_set.fna.gatk -j cap_tiny.sjm    
$ sjm NA12878.sjm    

#### 2. joint genotyping of less than 200 samples
$ run_gatk_batch.py -B bam.lst -o `pwd` --tmp /rgs01/scratch_space -r $ref_genome.gatk -j joint.sjm -v joint_call    
$ sjm joint.sjm    

#### 3. merging g.vcf and joint genotyping for > 200 samples
( assuming g.vcf exited for each sample )
##### 3a. manually run for chromosome 1, merge gvcfs into 30 sample batches and joint genotyping all
$ run_joint_from_gvcf.py -c 30 -v 1.chr1.g.vcf.gz 2.chr1.g.vcf.gz -o chr1.gt.vcf.gz -O folder -t chr1.merge -T chr1 -j jobs.sjm    
$ sjm jobs.sjm    

** note **    
- merging gvcf would require LARGE RAM and will be slow especially >100 samples    

##### 3b. modify gatk_varcall/scripts/setup_joint_gt.sh    

### recommanded changes
Add the following line to your .bashrc (especially you frequently switch between b37 and b38):    
export PS1='[\h \[\e[0;36m\]$ref_build\[\e[0m\] \W]\[\e[0;91m\]\$\[\e[0m\] '    

This will tell in the command line that:    
a) gatk_varcall is loaded and    
b) the genome build version    


### understand ID and SM in RG tag    
ID:    
- ID is taged for each read in teh BAM    
- ID do not need to carry any meaning as it is used as uniq key.    
- Can be used to distinguish the reads from different experiments. for example if your initial sequencing    
does not have enough coverage, and a topoff was done to get more reads. ID could be "NA12878" and "NA12878-topoff" to distinguish every reads.    
    
SM:    
- Every BAM is encouraged to have one SM tag, unless in rare scenario you need to merge numtiple samples together.    
- SM is used by GATK as sample name in variant call step (write to VCF file). if there are multiple SM tag in a BAM GATK HC caller (gvcf mode) would be confused.    
- SM can be identical to ID for one sample, one experiemnts cases.    

### Acknowledgement
This pipeline is built based on hugeseq, but does variant call only    
https://github.com/StanfordBioinformatics/HugeSeq    
