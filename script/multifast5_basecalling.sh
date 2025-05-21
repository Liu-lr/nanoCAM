#!/bin/bash
SampleID=$1
GPUS=$2
Inputpath=$3
Outputpath=$4
Conf_file=$5
Rrun=$6

Exportpath="${Outputpath}/${SampleID}"
mkdir -p ${Exportpath}/fail
mkdir -p ${Exportpath}/pass
mkdir -p ${Exportpath}/summary
mkdir -p ${Exportpath}/fast5
TempDir="/tmpdir/workdir/${SampleID}"
# get all fast5
cd ${Inputpath}
fast5s=(`ls *.fast5`)
mkdir -p ${TempDir}


for f5filename in ${fast5s[@]}; do
	# get f5id
	f5id=`basename ${f5filename} .fast5`
	# if finished, continue
	if ls ${Exportpath}/pass | grep "${f5id}.fastq.gz"; then
		echo "${f5filename} has already been called!"
		# if find fastq files continue
		continue
	fi

	mkdir -p ${TempDir}/${f5id}
    mkdir -p "${TempDir}/RawFast5"
	echo "***Run ${f5id}***"
	# copy fast5 files
	cp ${Inputpath}/${f5filename} ${TempDir}/RawFast5/${f5filename}

	# remove previous 
    compress_fast5 -i ${TempDir}/RawFast5 \
    -s ${TempDir} \
    --compression vbz --recursive --threads 20 --sanitize 
    rm ${TempDir}/RawFast5/${f5filename}

	while nvidia-smi | grep  "No devices were found"; do
		echo "No devices were found, retry"
	done

## Basecalling
guppy_basecaller \
-i ${TempDir} \
-s ${TempDir}/${f5id} \
-c ${Conf_file}  \
-x cuda:0 \
-r -q 0 \
--min_qscore 7 \
--compress_fastq \
--fast5_out 


	# Export
	datestr=`date "+%Y-%m-%d_%H:%M:%S"`
	if ls ${TempDir}/${f5id}/pass | grep "fastq.gz" ; then
		echo "${f5id} ${f5filename} ${datestr} OK" >> ${Exportpath}/basecalling.log
		mv ${TempDir}/${f5id}/sequencing_summary* ${Exportpath}/summary/sequencing_summary_${f5id}.txt
		mv ${TempDir}/${f5id}/pass/*.fastq.gz ${Exportpath}/pass/${f5id}.fastq.gz
		mv ${TempDir}/${f5id}/fail/*.fastq.gz ${Exportpath}/fail/${f5id}.fastq.gz
    mv ${TempDir}/${f5id}/workspace/*.fast5 ${Exportpath}/fast5/${f5id}.fast5
		#rm -r ${TempDir}/*
	else
		echo "${f5id} ${f5filename} ${datestr} Error" >> ${Exportpath}/basecalling.log
	fi
	rm -r ${TempDir}/*
done

rm -r ${TempDir}
