#!/bin/bash -eu

>&2 echo "*** Realigning targeted regions ***"

if [ $# -lt 1 ]
then 
	>&2 echo "Usage: $0 <bam> [regions]"
	exit 1
fi


f=`cd \`dirname $1\`; pwd`/`basename $1`
o=`basename ${f%.bam}`
shift
>&2 echo ">>> Determining (small) suspicious intervals which are likely in need of realignment"
optL=""
cname=""
if [ $# -gt 1 ]; then
	cname="$1.realn"; shift
	for c in $@; do
		optL="$optL -L $c"
	done
else
	cname="realn"
fi

cmd="java -Xms10g -Xmx10g -XX:ParallelGCThreads=4 -Djava.io.tmpdir=$JAVATMP \
	-jar $GATKPATH/GenomeAnalysisTK.jar \
	-T RealignerTargetCreator \
	-R $ref_genome \
	-known $mills_indel \
	-known $thousandgenome_indel \
	-I $f $optL \
	-o $o.$cname.intervals"
echo $cmd 
eval $cmd


>&2 echo ">>> Running the realigner over the targeted intervals"
cmd="java -Xms10g -Xmx10g -XX:ParallelGCThreads=4 -Djava.io.tmpdir=$JAVATMP \
	-jar $GATKPATH/GenomeAnalysisTK.jar \
	-T IndelRealigner \
	-R $ref_genome \
	-targetIntervals $o.$cname.intervals \
	-known $mills_indel \
	-known $thousandgenome_indel \
	-model USE_READS \
	-LOD 5 $optL \
	-I $f \
	-o $o.$cname.bam"
echo $cmd
eval $cmd

>&2 echo "*** Finished realigning targeted regions ***"
