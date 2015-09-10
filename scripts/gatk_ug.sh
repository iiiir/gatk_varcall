#!/bin/bash


function usage () {
   cat <<EOF
Usage: $progname [-d|-c int] [-m int] [-l chr1:123-456] <out.vcf> <in.1.bam> [in.2.bam]
where:
    -c Change the default coverage per-sample
    -d Disable the downsampler
    -l Target regions for variant calling
    -m Maximum reads in an active region (HaplotypeCaller option where downsampling not work)
EOF
   exit 0
}

# set options
while getopts ":c:m:d" opt; do
    case $opt in
        c)  [[ -n $optDT ]]  && usage || optCov="-dcov $OPTARG" ;;
		d)  [[ -n $optCov ]] && usage || optDT="-dt NONE" ;;
		l)  optL="-L $OPTARG" ;;
		m)  optCov="--maxReadsInRegionPerSample $OPTARG" ;;
    esac
done
shift $((OPTIND-1))

# make sure output/inputs provided
[[ $# -lt 2 ]] && usage && exit 0

# set output
ovcf=$1; shift

# get bam files
bams=$@
inputs=
if [[ $# -gt 10 ]]; then
	echo $@ | tr " " "\n" > $oname.bam.list
	inputs="-I $oname.bam.list"
else
	for bam in $bams; do
		inputs="-I $bam $inputs"
	done
fi

>&2 echo "*** Calling variants using UnifiedGenotyper ***"

cmd="java -Xms20g -Xmx20g -XX:ParallelGCThreads=4 -XX:ParallelGCThreads=4 -Djava.io.tmpdir=$JAVATMP \
	-jar $GATKPATH/GenomeAnalysisTK.jar \
	-T UnifiedGenotyper \
	--dbsnp $dbSNP \
	-stand_call_conf 30.0 \
	-stand_emit_conf 10.0 \
	-nct 4 \
	-gt_mode DISCOVERY \
	--genotype_likelihoods_model BOTH $optDT $optCov $optL \
	-R $ref_genome \
	$inputs \
	-o $ovcf"
echo $cmd
eval $cmd

>&2 echo "*** Finished GATK UnifiedGenotyper variant calling ***"
