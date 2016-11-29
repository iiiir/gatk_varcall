#!/bin/bash -e

# InvocationTargetException 
# would likely due to damaged index of vcf. 
# Delete and let GATK index again

[[ $# -lt 2 ]] && echo "$0 <o.vcf.gz> <in.1.vcf.gz> <in.2.vcf.gz> [in.3.vcf.gz] [...]"

ogvcf=$1; shift
gvcfs=""
for gvcf in $@; do 
	gvcfs="$gvcfs -V $gvcf"
done

cmd="java -XX:ParallelGCThreads=4 -Xms20g -Xmx20g -Djava.io.tmpdir=$JAVATMP 
	-jar $GATKPATH/GenomeAnalysisTK.jar \
	-T CombineGVCFs \
	-R $ref_genome \
	$gvcfs \
	-o $ogvcf"

echo $cmd
eval $cmd
