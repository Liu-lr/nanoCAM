# Promoter
TSS="gene_region.txt"
Bigfile="~/process_data"

computeMatrix scale-regions \
-m 5000 -b 3000 -a 3000 \
-R ${TSS} \
-o GMCGregion_matrix.mat.gz \
--skipZeros \
-p 24 \
--binSize 20 \
--samplesLabel nanoCAMP WGBS \
-S ${Bigfile}/GM12878_Integrated_CpG.bigWig \
${Bigfile}/GM12878_WGBS_ENCFF570TIL_filterchr_sorted.bigWig


echo "Done!"
