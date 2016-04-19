#!/bin/bash

>&2 echo "*** Variant call (genotyping) ***"

if [ $# -lt 1 ]
then 
	>&2 echo "Usage: $0 <out.vcf> <in1.g.vcf> [in2.g.vcf] ..."
	exit 1
fi


ovcf=$1; shift

gvcfs=""
for f in $@; do
    gvcfs="$gvcfs -V `realpath.sh $f`"
done

>&2 echo ">>> Performing  variant genotyping"
cmd="java -Xms10g -Xmx10g -XX:ParallelGCThreads=8 -Djava.io.tmpdir=$JAVATMP \
	-jar ${GATKPATH}/GenomeAnalysisTK.jar \
	-T GenotypeGVCFs \
	-R $ref_genome \
	-nt 8 \
	-D $dbSNP \
	$gvcfs \
	-o $ovcf"
eval $cmd

>&2 echo "*** -R span[hosts=1] -R rusage[mem=20000] -M 20000 ***"