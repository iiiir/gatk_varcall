#!/bin/bash -eu

>&2 echo "*** Recalibrating base quality (assuming ILLUMINA)***"

if [ $# -lt 1 ]
then 
	>&2 echo "Usage: $0 <out.bam> <in.bam>"
	exit 1
fi

o=`cd \`dirname $1\`; pwd`/`basename $1`; shift
opre=${o/realn.bam/realn.recal}

f=`cd \`dirname $1\`; pwd`/`basename $1`

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
	-o $opre.grp"
echo $cmd
eval $cmd

>&2 echo ">>> Printing reads"
cmd="java -Xms10g -Xmx10g -XX:ParallelGCThreads=4 -Djava.io.tmpdir=$JAVATMP \
	-jar $GATKPATH/GenomeAnalysisTK.jar \
	-R $ref_genome $optL \
	-T PrintReads \
	-BQSR $opre.grp \
	-I $f \
	-o $o"
echo $cmd
eval $cmd

>&2 echo "*** Finished recalibrating base quality ***"
