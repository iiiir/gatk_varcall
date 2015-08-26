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
$ vi gatk_varcall/modulefiles/gatk_varcall_v3.4/b38    
  change "set pipeline_dir /home/swang/app/gatk_varcall" to point to correct path    
$ chmod +x gatk_varcall/bin/*    

### usage
$ cd gatk_varcall/test/
$ run_gatk.py -b tiny_b38.bam -o `pwd` --tmp /rgs01/scratch_space/cap_tiny_test -r ../scripts/GCA_000001405.15_GRCh38_no_alt_analysis_set.fna.gatk -j cap_tiny.sjm    
$ sjm NA12878.sjm

### Acknowledgement
This pipeline is built based on hugeseq, but does variant call only
https://github.com/StanfordBioinformatics/HugeSeq
