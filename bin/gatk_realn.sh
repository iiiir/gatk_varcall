#!/bin/bash -eu

>&2 echo "*** Realigning targeted regions ***"

if [ $# -lt 1 ]
then 
	>&2 echo "Usage: $0 <out.bam> <in.bam> [regions]"
	exit 1
fi


o=`cd \`dirname $1\`; pwd`/`basename $1`; shift
opre=${o%.bam}
f=`cd \`dirname $1\`; pwd`/`basename $1`
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

cmd="java -Xms5g -Xmx5g -XX:ParallelGCThreads=4 -Djava.io.tmpdir=$JAVATMP \
	-jar $GATKPATH/GenomeAnalysisTK.jar \
	-T RealignerTargetCreator \
	-R $ref_genome \
	-known $mills_indel \
	-known $thousandgenome_indel \
	-I $f $optL \
	-o $opre.intervals"
echo $cmd 
eval $cmd


>&2 echo ">>> Running the realigner over the targeted intervals"
cmd="java -Xms5g -Xmx5g -XX:ParallelGCThreads=4 -Djava.io.tmpdir=$JAVATMP \
	-jar $GATKPATH/GenomeAnalysisTK.jar \
	-T IndelRealigner \
	-R $ref_genome \
	-targetIntervals $opre.intervals \
	-known $mills_indel \
	-known $thousandgenome_indel \
	-model USE_READS \
	-LOD 5 $optL \
	-I $f \
	-o $o"
echo $cmd
eval $cmd

>&2 echo "*** Finished realigning targeted regions ***"
