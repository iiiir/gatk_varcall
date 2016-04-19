#!/bin/bash

>&2 echo "*** Concatenating vcf/g.vcf files ***"

if [ $# -lt 2 ]
then 
	>&2 echo "Usage: $0 <output.vcf.gz> <1.vcf> [2.vcf]"
	exit 1
fi

# output
ogz=`cd \`dirname $1\`; pwd`/`basename $1`
o=${ogz%.gz}
shift
[[ -f $o ]] && echo "$o exist! Please provide a NEW output file name!" && exit 1


vcfs=""
for v in $@; do
	vcfs="$vcfs -V $v"
done

cmd="java -cp ${GATKPATH}/GenomeAnalysisTK.jar org.broadinstitute.gatk.tools.CatVariants\
	-R $ref_genome \
	$vcfs \
	--assumeSorted \
	-out $o"
echo $cmd
eval $cmd

cmd="bgzip -c $o > $ogz && tabix $ogz"
echo $cmd
eval $cmd

>&2 echo "*** Finished concatenating vcf/g.vcf files  ***"
