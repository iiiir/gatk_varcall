#!/bin/bash

>&2 echo "*** Variant call (genotyping) ***"

if [ $# -lt 1 ]
then 
	>&2 echo "Usage: $0 <out.vcf> <in.g.vcf> [regions] ..."
	exit 1
fi


ovcfgz=$1; shift
[[ $ovcfgz = *.gz ]] && ovcf=${ovcfgz%.gz} || (echo "File is not gzipped!"; exit 0)

gvcf=`realpath.sh $1`; shift
optL=""
for c in $@; do
    optL="$optL -L $c"
done

>&2 echo ">>> Performing  variant genotyping"
cmd="java -Xms10g -Xmx10g -XX:ParallelGCThreads=8 -Djava.io.tmpdir=$JAVATMP \
	-jar ${GATKPATH}/GenomeAnalysisTK.jar \
	-T GenotypeGVCFs \
	-R $ref_genome \
	-nt 8 \
	-D $dbSNP \
	-V $gvcf $optL \
	-o $ovcf"
echo $cmd
eval $cmd

cmd="bgzip -c $ovcf > $ovcfgz && tabix $ovcfgz"
echo $cmd
eval $cmd

>&2 echo "*** -R span[hosts=1] -R rusage[mem=20000] -M 20000 ***"
