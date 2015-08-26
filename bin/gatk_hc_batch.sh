#!/bin/bash -eu

>&2 echo "*** Variant call (HaplotypeCaller) ***"

if [ $# -lt 2 ]; then 
	>&2 echo "Usage: $0 <out.g.vcf.gz> <in.bam> [regions]"
	exit 1
fi

ogz=`cd \`dirname $1\`; pwd`/`basename $1`; shift
o=${ogz%.gz}
f=`cd \`dirname $1\`; pwd`/`basename $1`; shift

optL=""
if [[ $# -gt 0 ]]; then
	for c in $@; do
		optL="$optL -L $c"
	done
fi

>&2 echo ">>> Performing raw variant calling"
cmd="java -XX:ParallelGCThreads=4 -Xms10g -Xmx10g -Djava.io.tmpdir=$JAVATMP \
	-jar ${GATKPATH}/GenomeAnalysisTK.jar \
	-T HaplotypeCaller \
	-R $ref_genome \
	--emitRefConfidence GVCF \
	--variant_index_type LINEAR \
	--variant_index_parameter 128000 \
	--dbsnp $dbSNP \
	-I $f $optL \
	-o $o"
echo $cmd
eval $cmd

cmd="bgzip -c $o > $ogz && tabix $ogz"
echo $cmd
eval $cmd

>&2 echo "*** Finished variant call (gvcf) ***"
