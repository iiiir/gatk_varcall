### gatk_varcall
GATK best practice variant calling pipeline for SNPs and INDELs

### dependencies
+ python 2.7
+ SJM (simple job manager)
+ GATK 3.0+
+ bgzip and tabix 1.2.1
+ LSF batch system (or other)

### usage
$ run_gatk.py --bam NA12878.bam --regions_file GRCh37-lite.fa.gatk --out \`pwd\` > NA12878.sjm    
$ sjm NA12878.sjm

### Acknowledgement
This pipeline is built based on hugeseq, but does variant call only
https://github.com/StanfordBioinformatics/HugeSeq
