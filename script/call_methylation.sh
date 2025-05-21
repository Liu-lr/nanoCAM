#!/bin/bash
Rawdir="~/GM12878_Rep1_pc/fast5_pass"
Fastqdir="~/GM12878_Rep1_pc/Rawdata"
Exportdir="~/GM12878_Rep1_pc/Methylation"
ref="~/GCA_000001405.15_GRCh38_major_chr.fa"
Tmpdir="~/CpGGpC1"
Bamdir="~/SplitBam"
Threads=8
mkdir -p $Tmpdir
mkdir -p $Exportdir

runs=0
f5files=(`find $Rawdir -name "*.fast5"`)
#PAK05673_pass_096968b5_9.fast5
for f5 in ${f5files[@]}; do
sname=`basename $f5 .fast5`
if [ -e ${Exportdir}/${sname}.cpggpc_methylation_calls.tsv ]; then
echo "$sname has been finished!"
continue
fi

Workdir="${Tmpdir}/${sname}"
mkdir -p $Workdir
# cp $f5files "${Workdir}/run.fast5"
cp $f5 "${Workdir}/run.fast5"
cp ${Fastqdir}/${sname}.fastq "${Workdir}/run.fastq"
# cp /data2/ZJY/PoreC_GpC/K562GpC/Porecmap/test "${Workdir}/run.bam"
cp ${Bamdir}/${sname}.bam "${Workdir}/run.bam"

cd $Workdir
/home/AMDs1/Software/nanopolish-cpggpc_new_train/nanopolish  index -d . run.fastq && \
samtools index run.bam && \
/home/AMDs1/Software/nanopolish-cpggpc_new_train/nanopolish call-methylation -q cpggpc -t 5 -r run.fastq -b run.bam -g ${ref}  > cpggpc_methylation_calls.tsv && \
mv cpggpc_methylation_calls.tsv "${Exportdir}/${sname}.cpggpc_methylation_calls.tsv" &&\
echo "Finished $sname !" &&\
rm -r $Workdir &

let runs++
while [ $runs -gt $Threads ]; # 5个程序同时跑
do
works=`ps -ef | grep "nanopolish call-methylation" | wc -l`
if [ $works -lt $Threads ]; then
let runs--
fi
sleep 10s
done


done
