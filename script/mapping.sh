#!/bin/bash
Softdir="/home/AMDs1/ZJY/Falign/Linux-amd64/bin"
ref="~/GCA_000001405.15_GRCh38_major_chr.fa"
reads="~/pass"
Exportdir="~/mapping"
mkdir -p $Exportdir
${Softdir}/falign -num_threads 80 -outfmt 'sam' -dump_by_file -out_dir ${Exportdir} ^GATC ${ref} ${reads}

## sam2bam
#!/bin/bash
Samdir="/path/to/samfile"
Samfiles=(`find $Samdir -name  "*.sam"`)
cd $Samdir
for sfile in ${Samfiles[@]}; do
echo $sfile
sbase=`basename $sfile .fastq.gz.sam`
samtools sort -@5 $sfile | samtools view -bS - > $sbase.bam
rm $sfile
done
