#!/bin/bash -e

>&2 echo "*** VQSR (snp and indel) ***"

if [ $# -lt 1 ]
then 
	echo "Usage: $0 <vcf> [platform default=WGS]"
	exit 1
fi

f=`cd \`dirname $1\`; pwd`/`basename $1`
[[ $f = *.vcf.gz ]] && fname=`basename ${f%.vcf.gz}` || fname=`basename ${f%.vcf}`

# define platform
platform="WGS"
[[ ! -z $2 ]] && platform=$2
>&2 echo "Platform is: $platform"

# optional annotation for WGS
#-an DP # depth of coverage is not good for exome data ...
if [[ $platform = "WGS" ]]; then
	optL="-an DP"
else
	optL=""
fi

>&2 echo ">>> Performing snp recalibration"
#-an HaplotypeScore # option for unified genotyper
#-an InbreedingCoeff  # option when there are at least 10 samples
# SW 4/15/2016: added QD and SOR
# -an SOR give error:  not detected for ANY training variant in the input callset
# --maxGaussians 4 group variants into 4 clusters ( for smaller number of variants)
cmd="java -Xms20g -Xmx20g -XX:ParallelGCThreads=4 -Djava.io.tmpdir=$JAVATMP \
	-jar ${GATKPATH}/GenomeAnalysisTK.jar \
	-T VariantRecalibrator \
	-R $ref_genome \
	-nt 4 \
	-resource:hapmap,known=false,training=true,truth=true,prior=15.0 $hapmap \
	-resource:omni,known=false,training=true,truth=true,prior=12.0 $omni \
	-resource:1000G,known=false,training=true,truth=false,prior=10.0 $thousandgenome_snp \
	-resource:dbsnp,known=true,training=false,truth=false,prior=2.0 $dbSNP_129 \
	-an QD $optL\
	-an FS \
	-an SOR \
	-an MQ \
	-an MQRankSum \
	-an ReadPosRankSum \
	-tranche 100.0 -tranche 99.9 -tranche 99.0 -tranche 90.0 \
	-mode SNP \
	-input $f \
	-recalFile $fname.snp.recal \
	-tranchesFile $fname.snp.tranches \
	-rscriptFile $fname.snp.plots.R \
	-log $fname.snp.recal.log"
>&2 echo $cmd
eval $cmd

>&2 echo ">>> Applying snp recalibration"
cmd="java -Xms10g -Xmx10g -XX:ParallelGCThreads=4 -Djava.io.tmpdir=$JAVATMP \
	-jar ${GATKPATH}/GenomeAnalysisTK.jar \
	-T ApplyRecalibration \
	-R $ref_genome \
	-nt 4 \
	--ts_filter_level 99.5 \
	-mode SNP \
	-input $f \
	-recalFile $fname.snp.recal \
	-tranchesFile $fname.snp.tranches \
	-log $fname.snp.vqsr.log \
	-o $fname.snp.vcf.gz"
>&2 echo $cmd
eval $cmd

>&2 echo ">>> Performing indel recalibration"
cmd="java -Xms20g -Xmx20g -XX:ParallelGCThreads=4 -Djava.io.tmpdir=$JAVATMP \
    -jar ${GATKPATH}/GenomeAnalysisTK.jar \
    -T VariantRecalibrator \
    -R $ref_genome \
    -resource:mills,known=false,training=true,truth=true,prior=12.0 $mills_indel \
    -resource:dbsnp,known=true,training=false,truth=false,prior=2.0 $dbSNP_129 \
    --maxGaussians 4 \
    -an QD $optL\
    -an FS \
    -an SOR \
    -an MQ \
    -an MQRankSum \
    -an ReadPosRankSum \
    -mode INDEL \
    -input $fname.snp.vcf.gz \
    -recalFile $fname.snp.indel.recal \
    -tranchesFile $fname.snp.indel.tranches \
    -rscriptFile $fname.snp.indel.plots.R \
    -log $fname.snp.indel.recal.log"
>&2 echo $cmd
eval $cmd

>&2 echo ">>> Applying indel recalibration"
cmd="java -Xms10g -Xmx10g -XX:ParallelGCThreads=4 -Djava.io.tmpdir=$JAVATMP \
    -jar ${GATKPATH}/GenomeAnalysisTK.jar \
    -T ApplyRecalibration \
    -R $ref_genome \
    --ts_filter_level 99.0 \
    -mode INDEL \
    -input $fname.snp.vcf.gz \
    -recalFile $fname.snp.indel.recal \
    -tranchesFile $fname.snp.indel.tranches \
    -log $fname.snp.indel.vqsr.log \
    -o $fname.vqsr.vcf.gz"
>&2 echo $cmd
eval $cmd

>&2 echo "*** Finished VQSR ***"
