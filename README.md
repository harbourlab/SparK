# SparK - Publication quality NGS data plotting (Version 2.4.1)

Please cite our article in bioRxiv:
https://www.biorxiv.org/content/10.1101/845529v1.full
Feature requests are welcome! For help, bug reports, and to request features contact Stefan.Kurtenbach@me.com


<img src="https://github.com/harbourlab/SparK/blob/master/Summary.png" width="900">  

Coming soon... interaction arcs for e.g. Hi-C, ChIA-PET, Hi-ChIP or any other interaction data! Preview:
<img src="https://github.com/harbourlab/SparK/blob/master/Screen%20Shot%202020-01-23%20at%2010.32.30%20PM.png" width="300">  


Plot NGS bedgraph tracks including replicates, averaging of replicates, track overlay, standard deviations, and a smart scale bar. Output files are true high-resolution vector graphics (.svg), for easy editing and customization.

This tool uses bedgraph files to generate the figures. To convert BAM files to bedgraph files, you can use deeptools, with "bamCoverage -b bamfile.bam -o outputfilename.bdg -bs 1 -of bedgraph". Make sure to use the "-bs 1" option. This should not be done for ChIP-seq data! For ChIP-seq, use the bedgraphs from the MACS2 output (or any other ChIP-seq pipeline). To convert bigwig (bw) files to bedgraph files you can use for instance the USCS bigWigToBedGraph tool (https://genome.ucsc.edu/goldenpath/help/bigWig.html).

<pre>
Requirements:
  - Python 3 (in theory Python 2 should work too, but I highly reccomend using Python 3)
  - numpy
 

Options (Required):
-cf      control bedgraph files seperated by space
-pr      region to be plotted. Example: "-pr chr1:1647389-272634"


Options (Not required):
-pt      plot type. Choices: "STD", "sine"

-cg      control groups. Defines which plot nr to place the files in
-tg      treatment groups. Defines which plot nr to place the files in
Both, the -cg and -tg option define in which plot number the list of files defined in -cf and -tf will 
be in. E.g., for a list of 5 files, say 2 replicates of RNAseq, and 3 replicates of ChIPseq, 
"-cg 1 1 2 2 2" and "-tg 1 1 2 2 2" will generate 2 plots, where plot 1 includes the first two files of 
both, treatment and control as listed in "-cf" "-tf". The latter 3 files of both will be in plot 2. See 
examples below.

-gl      Label the groups defined in -cg and -tg. e.g. "-gl RNAseq H3K4me3" will label group 1 with 
         RNAseq, and group 2 with H3K4me3
-tf      treatment bedgraph files seperated by space
-l       labels for control and treatment groups. defined above. e.g. "-l brain_cells tumor_cells". 
         1st is controls, second entry treatment group
-ps      Set to "averages" if control and treatment tracks should be averaged. If "averages" is 
         selected, then a "overlap" color box will be plotted.
-gs      group autoscale. usage: "-gs yes". Will autoscale all groups.
-es      exclude groups from autoscaling. e.g. "-es 1"
-f       fill colors for the tracks. Choices: "blue/red" (default), "blue/grey", "all_grey", 
         "blue/green". Two hex colors can be entered alternatively. Examples" "-f blue/grey", 
         "-f 00FF12 848484".
-sp      add significant differences in tracks aka "sparks". Usage: "-sp yes". Significant areas 
         are defined as areas where the delta of the means is greater than the sum of standard 
         deviations of controls and treatment files. 
-sc      spark color. Enter two colors in hex format for significantly increase and decreased areas. 
         Example "-sc 00FF12 848484".
-sm      smoothen tracks. Integer value. (plots are 2000 data points wide. "-sm 10" will smoothen 
         with a window of 10.
-o       output filename. Usage: "-o Experiment1".
-bed     Add bed files to plot here. Usage: "-bed bedfile1.bed bedfile2.bed"...
-bedcol  choose colors for bed tracks (in hex). Default is blue. Choose either one color, or same 
         amount as bed tracks given. If tracks are overlayed, SparK will add transparancy to the color, 
         leading to a less intense color than anticipated. Transparency is required to see all 
         overlayed tracks, but can be changed with any SVG editor if desired.
-gff     link gff file to show genes. Get here: https://www.gencodegenes.org/human/ Please read the section
         on gff files below if you encounter errors or want to use a custom gff file.
-dg      in case not all genes in the region should be plotted, enter the genes to plot here.
         Usage: "-dg GAPDH RS1" Without this option all genes will be shown.
-dt      Display transcripts. By default, all available transcripts for a gene will be merged and 
         plotted as one. If all annotated transcripts should be plotted, set this to "all". 
         Alternatively, transcript IDs can be listed to plot only certain transcripts
-wg      If all or individual transcripts are beeing plotted (-dt function) instead of the merged 
         default, then "-wg yes" can be used to plot gene name instead of transcript ID.
-tss     set to "no" to avoid start_codons and direction of transcription being indicated with arrows.
-scale   Plot scalebar. Set to "no" if no scalebar should be plotted.
-w       Define plot width. Default is 150.


Getting started:

Plotting multiple NGS tracks. Example of a plot of 4 ChIP-seq tracks with standard settings.

<img src="https://github.com/harbourlab/SparK/blob/master/FigureA.png" width="400">  

Code used to generate this plot:
python SparK.py \
-pr chr12:6520512-6640512 \
-cf HepG2_H3K27AC_1_ENCFF495QSO.bigWig.bdg HepG2_H3K27AC_2_ENCFF348RLL.bigWig.bdg HepG2_H3K4me3_1_ENCFF699DRO.bigWig.bdg HepG2_H3K4me3_2_ENCFF400FYO.bigWig.bdg \
-gff gencode.v24.primary_assembly.annotation.txt \
-gl H3K27AC H3K4me3 H3K27AC-2 H3K4me3-2 \
-dg GAPDH IFFO1 NOP2 CHD4 LPAR5

Note: The -dg option is optional and was used to plot only the five major genes in this area, to avoid having
too many genes displayed here. To display all genes, run this without "-dg"


Example of plotting the comparison of ChIP-seq data of two cell lines (HepG2 and K562).

<img src="https://github.com/harbourlab/SparK/blob/master/FigureB.png" width="400"> 

Code used to generate this plot:
python SparK.py \
-pr chr12:6527512-6550512 \
-tf K562_H3K27AC_1_ENCFF779QTH.bigWig.bdg K562_H3K27AC_2_ENCFF945XHA.bigWig.bdg K562_H3K4me3_1_ENCFF804OLI.bigWig.bdg K562_H3K4me3_2_ENCFF352VRB.bigWig.bdg \
-cf HepG2_H3K27AC_1_ENCFF495QSO.bigWig.bdg HepG2_H3K27AC_2_ENCFF348RLL.bigWig.bdg HepG2_H3K4me3_1_ENCFF699DRO.bigWig.bdg HepG2_H3K4me3_2_ENCFF400FYO.bigWig.bdg \
-tg 1 1 2 2 \
-cg 1 1 2 2 \
-gl H3K27AC H3K4me3 \
-l HepG2_cells K562_cells \
-gff gencode.v24.primary_assembly.annotation.txt \
-ps averages \
-dg GAPDH


Example comparing histone acetylation with RNA-seq. Of note! The overlap label will only be plotted when averages are plotted.
Else, due to transparency issues, the overlap plotting multiple tracks is not clearly visible.

<img src="https://github.com/harbourlab/SparK/blob/master/FigureE.png" width="400"> 

Code:
python SparK.py \
-pr chr12:6533612-6539012 \
-tf K562_H3K27AC_1_ENCFF779QTH.bigWig.bdg K562_H3K27AC_2_ENCFF945XHA.bigWig.bdg K562_RNAseq_plus_1_ENCFF682BLJ.bigWig.bdg K562_RNAseq_plus_2_ENCFF745PIR.bigWig.bdg \
-cf HepG2_H3K27AC_1_ENCFF495QSO.bigWig.bdg HepG2_H3K27AC_2_ENCFF348RLL.bigWig.bdg HepG2_RNAseq_plus_1_ENCFF576COO.bigWig.bdg HepG2_RNAseq_plus_2_ENCFF599HGT.bigWig.bdg \
-tg 1 1 2 2 \
-cg 1 1 2 2 \
-gl H3K27AC RNA-seq \
-l HepG2_cells K562_cells \
-gff gencode.v24.primary_assembly.annotation.txt \
-dg GAPDH


Exaple of custom coloring tracks, and adding bed files with custom colors.

<img src="https://github.com/harbourlab/SparK/blob/master/FigureC.png" width="400"> 

Code used to generate this plot:
python SparK.py \
-pr chr12:6527512-6550512 \
-tf K562_H3K27AC_1_ENCFF779QTH.bigWig.bdg K562_H3K27AC_2_ENCFF945XHA.bigWig.bdg K562_H3K4me3_1_ENCFF804OLI.bigWig.bdg K562_H3K4me3_2_ENCFF352VRB.bigWig.bdg \
-cf HepG2_H3K27AC_1_ENCFF495QSO.bigWig.bdg HepG2_H3K27AC_2_ENCFF348RLL.bigWig.bdg HepG2_H3K4me3_1_ENCFF699DRO.bigWig.bdg HepG2_H3K4me3_2_ENCFF400FYO.bigWig.bdg \
-tg 1 1 2 2 \
-cg 1 1 2 2 \
-gl H3K27AC RNA-seq \
-l HepG2_cells K562_cells \
-gff gencode.v24.primary_assembly.annotation.txt \
-ps averages \
-f CE358B 005CFF \
-bed bedfile1.bed bedfile2.bed \
-bedcol EF1414 FFBC00




Example of different smoothing windows, applied with "-sm".

<img src="https://github.com/harbourlab/SparK/blob/master/smoothing2.png" width="400">  



Example of sparks (significant changes) beeing added to a plot with grey color scheme.

<img src="https://github.com/harbourlab/SparK/blob/master/FigureD.png" width="400"> 

Code used to generate this figure:
python SparK.py \
-pr chr12:6527512-6550512 \
-tf K562_H3K27AC_1_ENCFF779QTH.bigWig.bdg K562_H3K27AC_2_ENCFF945XHA.bigWig.bdg K562_H3K4me3_1_ENCFF804OLI.bigWig.bdg K562_H3K4me3_2_ENCFF352VRB.bigWig.bdg \
-cf HepG2_H3K27AC_1_ENCFF495QSO.bigWig.bdg HepG2_H3K27AC_2_ENCFF348RLL.bigWig.bdg HepG2_H3K4me3_1_ENCFF699DRO.bigWig.bdg HepG2_H3K4me3_2_ENCFF400FYO.bigWig.bdg \
-tg 1 1 2 2 \
-cg 1 1 2 2 \
-gl H3K27AC H3K4me3 \
-l HepG2_cells K562_cells \
-gff gencode.v24.primary_assembly.annotation.txt \
-f all_grey \
-sp yes


Other plot types:
Spark allows to plot the standard deviation of NGS replicates:

<img src="https://github.com/harbourlab/SparK/blob/master/FigureF.png" width="400"> 

Code used:
python SparK.py \
-pr chr12:6540512-6545512 \
-tf K562_H3K27AC_1_ENCFF779QTH.bigWig.bdg K562_H3K27AC_2_ENCFF945XHA.bigWig.bdg K562_H3K4me3_1_ENCFF804OLI.bigWig.bdg K562_H3K4me3_2_ENCFF352VRB.bigWig.bdg \
-cf HepG2_H3K27AC_1_ENCFF495QSO.bigWig.bdg HepG2_H3K27AC_2_ENCFF348RLL.bigWig.bdg HepG2_H3K4me3_1_ENCFF699DRO.bigWig.bdg HepG2_H3K4me3_2_ENCFF400FYO.bigWig.bdg \
-tg 1 1 2 2 \
-cg 1 1 2 2 \
-gl H3K27AC H3K4me3 \
-l HepG2_cells K562_cells \
-gff gencode.v24.primary_assembly.annotation.txt \
-pt STD

Sine plot (experimental). 

<img src="https://github.com/harbourlab/SparK/blob/master/FigureG.png" width="400"> 

python SparK.py \
-pr chr12:6533612-6539012 \
-tf K562_H3K27AC_1_ENCFF779QTH.bigWig.bdg K562_H3K27AC_2_ENCFF945XHA.bigWig.bdg K562_H3K4me3_1_ENCFF804OLI.bigWig.bdg K562_H3K4me3_2_ENCFF352VRB.bigWig.bdg \
-cf HepG2_H3K27AC_1_ENCFF495QSO.bigWig.bdg HepG2_H3K27AC_2_ENCFF348RLL.bigWig.bdg HepG2_H3K4me3_1_ENCFF699DRO.bigWig.bdg HepG2_H3K4me3_2_ENCFF400FYO.bigWig.bdg \
-tg 1 1 2 2 \
-cg 1 1 2 2 \
-gl H3K27AC H3K4me3 \
-l HepG2_cells K562_cells \
-gff gencode.v24.primary_assembly.annotation.txt \
-pt sine



Modify gene annotations:

<img src="https://github.com/harbourlab/SparK/blob/master/summary_genes.png" width="900">  

A: Standard plot settings, all transcript IDs in the gff file will be merged for each gene, and the 
first start_codon is annotated

B: All known transcripts can be plotted, using the setting "-dt all"

C: Selected transcripts can be plotted using the "-dt" setting followed by the relevant transcripts. 
Here: "-dt ENST00000396859.5 ENST00000436152.6"

D: When plotting transcript IDs, the gene names can be plotted instead. Here same plot as in C, 
but with "-wg yes".

Of note, as the output of SparK are true vector graphics, all text, as well as any coloring, lines ect. 
can be easily changed in any SVG editor manually after plotting.

</pre>




### Problems with gff files/use of custom gff files:
SparK will exctract gene and transcript information from column 3 of the gff file. In particular, from rows which have "gene", "CDS", "exon", "transcript", and "start_codon" in column 2. Check if your gff file labels these entries like that if some are missing or problems are encountert; e.g. your gff file doesn't use for instance "mRNA" instead of "transcript". In the latter "mRNA" should be replaced with "transcript".
Further, SparK expects the gene name, and transcript name to be in column 9 of the gff file. It will try extract the information from ... ; gene_name "XXX"; ... and ... ; transcript_id "XXX"; ... . You can download a standard gff file from the link mentioned above and have a look at how these gff files are built. If encountering problems with your gff file please check if those two entries are present in the same format. If not, download an updated version of your gff files that includes these entries in the same format. If this is not available, e.g. when working with custom genomes, then there are two options: Either those entries need to be added to the file (e.g. with Excel), or, the SparK pyhton file can be easily modified to recognize other formats. Where Python extracts the gene name and transcript ID's is specified in the "get_gene_name" and "get_transcript_name" functions at the beginning of the script. Of note, the  entry transcript_ID is only neccecary if individual transcriptd were to be plotted. If only genes are plotted, then a "gene_name" entry is enough in the gff file.


