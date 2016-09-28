#!/bin/bash -eu

>&2 echo "*** Recalibrating base quality again (assuming ILLUMINA)***"

if [ $# -lt 1 ]
then 
	>&2 echo "Usage: $0 <in.bam> <prefix>"
	exit 1
fi


f=`cd \`dirname $1\`; pwd`/`basename $1`
opre=$2

optL=""

>&2 echo ">>> Counting covariates again"
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
	-BQSR $opre.grp
	-o $opre.post.grp"
echo $cmd
eval $cmd

>&2 echo ">>> Plotting "
cmd="java -Xms10g -Xmx10g -XX:ParallelGCThreads=4 -Djava.io.tmpdir=$JAVATMP \
    -jar $GATKPATH/GenomeAnalysisTK.jar \
    -T AnalyzeCovariates \
    -R $ref_genome $optL\
    -before $opre.grp \
    -after $opre.post.grp \
    -plots $opre.pdf"
echo $cmd
eval $cmd

>&2 echo "*** Finished recalibrating base quality plot ***"
