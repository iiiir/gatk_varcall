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
cmd="java -Xms15g -Xmx15g -XX:ParallelGCThreads=8 -Djava.io.tmpdir=$JAVATMP \
	-jar ${GATKPATH}/GenomeAnalysisTK.jar \
	-T GenotypeGVCFs \
	-R $ref_genome \
	-nt 4 \
	-D $dbSNP \
	$gvcfs \
	-o $ovcf"
eval $cmd

>&2 echo "*** -R span[hosts=1] -R rusage[mem=10000] -n 4 -q pcgp ***"
