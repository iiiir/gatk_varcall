#!/bin/bash

>&2 echo "*** Variant call (HaplotypeCaller) ***"

if [ $# -lt 1 ]; then 
	>&2 echo "Usage: $0 <bam> [regioname] [regions]"
	exit 1
fi

f=`cd \`dirname $1\`; pwd`/`basename $1`; shift
o=`basename ${f%.bam}`

cname=$1; shift

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
	-o $o.$cname.g.vcf"
echo $cmd
eval $cmd

cmd="bgzip -c $o.g.vcf > $o.g.vcf.gz && tabix $o.g.vcf.gz"
echo $cmd
eval $cmd

>&2 echo "*** Finished variant call ***"
