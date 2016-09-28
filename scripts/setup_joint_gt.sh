#!/bin/bash

[[ $# -lt 1 ]] && echo "$0 <sample.list>" && exit 0

sample_list=$1
SCDPATH=/research/rgs01/resgen/prod/tartan/index/data/SCD/SCD

for cnum in `seq 22` X Y M; do
	gvcfs=""
	for sample in `cat $sample_list`; do
		gvcf="$SCDPATH/$sample/WHOLE_GENOME/snv-indel-unpaired-raw-gatk/raw/$sample.chr$cnum.realn.recal.g.vcf.gz"
		[[ ! -f $gvcf ]] && echo ">>> ERROR: doews not exist: $gvcf" && exit 0
		gvcfs="$gvcfs $SCDPATH/$sample/WHOLE_GENOME/snv-indel-unpaired-raw-gatk/raw/$sample.chr$cnum.realn.recal.g.vcf.gz"
	done
	run_joint_from_gvcf.py -c 30 -v $gvcfs -o "chr$cnum.gt.vcf.gz" -O "vcf-raw" -t "chr$cnum.gvcf.merged" -T "chr$cnum" -j "run_chr$cnum.sjm"
done

