#!/bin/bash -eu

>&2 echo "*** Recalibrating base quality (assuming ILLUMINA)***"

if [ $# -lt 1 ]
then 
	>&2 echo "Usage: $0 <bam>"
	exit 1
fi

f=`cd \`dirname $1\`; pwd`/`basename $1`
o=`basename ${f%.bam}`
o=${o/realn/realn.recal}

optL=""

>&2 echo ">>> Counting covariates"
cmd="java -Xms10g -Xmx10g -XX:ParallelGCThreads=4 -Djava.io.tmpdir=$JAVATMP \
	-jar $GATKPATH/GenomeAnalysisTK.jar \
	-T BaseRecalibrator \
   	-R $ref_genome $optL\
   	-knownSites $dbSNP \
	-knownSites $mills_indel \
	-knownSites $thousandgenome_indel \
	--default_platform ILLUMINA \
	--force_platform ILLUMINA \
	-I $f \
	-o $o.grp"
echo $cmd
eval $cmd

>&2 echo ">>> Printing reads"
cmd="java -Xms10g -Xmx10g -XX:ParallelGCThreads=4 -Djava.io.tmpdir=$JAVATMP \
	-jar $GATKPATH/GenomeAnalysisTK.jar \
	-R $ref_genome $optL \
	-T PrintReads \
	-BQSR $o.grp \
	-I $f \
	-o $o.bam"
echo $cmd
eval $cmd

>&2 echo "*** Finished recalibrating base quality ***"
