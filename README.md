# SparK - Publication quality and pipeline integratable NGS data plotting (Version 2.6.2)


Please cite our article in bioRxiv, a citation can be downloaded here and imported in Endnote or such:
https://www.biorxiv.org/content/10.1101/845529v1.full
Feature requests are welcome! For help, bug reports, and to request features please open a issue here on GitHub.


<img src="https://github.com/harbourlab/SparK/blob/master/Summary.png" width="900">

Coming soon... interaction arcs for e.g. Hi-C, ChIA-PET, Hi-ChIP or any other interaction data! Preview:
<img src="https://github.com/harbourlab/SparK/blob/master/Screen%20Shot%202020-01-23%20at%2010.32.30%20PM.png" width="300">


Plot NGS bedgraph tracks including replicates, averaging of replicates, track overlay, standard deviations, and a smart scale bar. Output files are true high-resolution vector graphics (.svg), for easy editing and customization.

This tool uses bedgraph files to generate the figures. To convert BAM files to bedgraph files, you can use deeptools, with "bamCoverage -b bamfile.bam -o outputfilename.bdg -bs 1 -of bedgraph". Make sure to use the "-bs 1" option. This should not be done for ChIP-seq data! For ChIP-seq, use the bedgraphs from the MACS2 output (or any other ChIP-seq pipeline). To convert bigwig (bw) files to bedgraph files you can use for instance the USCS bigWigToBedGraph tool (https://genome.ucsc.edu/goldenpath/help/bigWig.html).

For faster retrieval of data from regions of a bedgraph, compress your bedgraph files with [bgzip](http://www.htslib.org/doc/bgzip.html) and index them with [tabix](http://www.htslib.org/doc/tabix.html) using the command `tabix -p bed <filename>`.
<pre>
Requirements:
  - Python 3
  - numpy

Example usage:
python SparK -cf mybedgraphfile.bdg -pr chr1:10000-200000

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
-ps      Set to "averages" if replicates of control and treatment tracks should be averaged for all groups.

y-axis scaling options:
By default, sparc will automatically pick y-axis for all groups.
-gs      group autoscale. usage: "-gs yes". This will autoscale all groups to the same y-axis.
-es      exclude groups from autoscaling. e.g. "-es 1"
-cs      custom scaling. This can be used together with -gs and -es. Enter values for y-axis of groups.
         use "D" to not change settings of y-axis. E.g, if you plot 4 groups, "-cs 1.2 12 D 100" will
         scale y-axis of group 1 to 1.2, group 2 to 12, not change settings for group 3, and scale
         group 4 to 100.

-dc      this setting can be used to change how the chromosome location is plotted. Options:
         top_left (default), top_right, bottom_left, bottom_right. Set to "no" to not plot the
         chromosomal location.
-f       fill colors for the tracks. One or two hex colors can be entered. In case two colors are
         entered, the first one is used for the treatment group, the right one for the control group.
         Examples" "-f blue/grey", "-f 00FF12 848484", "-f #000000". The presets "blue/red" (default),
         "blue/grey", "all_grey", or "blue/green" can be entered alternatively.
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
-bedlab  labels for bed tracks. Usage: "-bedlab bed_track1 bed_track2".
-gtf     link gtf file to show genes. Get here: https://www.gencodegenes.org/human/ Please read the section
         on gtf files below if you encounter errors or want to use a custom gtf file.
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
-gtf gencode.v24.primary_assembly.annotation.txt \
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
-gtf gencode.v24.primary_assembly.annotation.txt \
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
-gtf gencode.v24.primary_assembly.annotation.txt \
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
-gtf gencode.v24.primary_assembly.annotation.txt \
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
-gtf gencode.v24.primary_assembly.annotation.txt \
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
-gtf gencode.v24.primary_assembly.annotation.txt \
-pt STD

Sine plot (experimental).

<img src="https://github.com/harbourlab/SparK/blob/master/FigureG.png" width="400">

python SparK.py \
-pr chr12:6533612-6539012 \
-tf K562_H3K27AC_1_ENCFF779QTH.bigWig.bdg K562_H3K27AC_2_ENCFF945XHA.bigWig.bdg K562_H3K4me3_1_ENCFF804OLI.bigWig.bdg K562_H3K4me3_2_ENCFF352VRB.bigWig.bdg \
-cf HepG2_H3K27AC_1_ENCFF495QSO.bigWig.bdg HepG2_H3K27AC_2_ENCFF348RLL.bigWig.bdg HepG2_H3K4me3_1_ENCFF699DRO.bigWig.bdg HepG2_H3K4me3_2_ENCFF400FYO.bigWig.bdg \
-tg 1 1 2 \
-cg 1 1 2 \
-gl H3K27AC H3K4me3 \
-l HepG2_cells K562_cells \
-gtf gencode.v24.primary_assembly.annotation.txt \
-pt sine \
-o 10_sine



Modify gene annotations:

<img src="https://github.com/harbourlab/SparK/blob/master/summary_genes.png" width="900">

A: Standard plot settings, all transcript IDs in the gtf file will be merged for each gene, and the
first start_codon is annotated

B: All known transcripts can be plotted, using the setting "-dt all"

C: Selected transcripts can be plotted using the "-dt" setting followed by the relevant transcripts.
Here: "-dt ENST00000396859.5 ENST00000436152.6"

D: When plotting transcript IDs, the gene names can be plotted instead. Here same plot as in C,
but with "-wg yes".

</pre>




### Problems with gtf files/use of custom gtf files:
SparK will exctract gene and transcript information from column 3 of the gtf file. In particular, from rows which have "gene", "CDS", "exon", "transcript", and "start_codon" in column 2. Check if your gtf file labels these entries like that if some are missing or problems are encountert; e.g. your gtf file doesn't use for instance "mRNA" instead of "transcript". In the latter "mRNA" should be replaced with "transcript".
Further, SparK expects the gene name, and transcript name to be in column 9 of the gtf file. It will try extract the information from ... ; gene_name "XXX"; ... and ... ; transcript_id "XXX"; ... . You can download a standard gtf file from the link mentioned above and have a look at how these gtf files are built. If encountering problems with your gtf file please check if those two entries are present in the same format. If not, download an updated version of your gtf files that includes these entries in the same format. If this is not available, e.g. when working with custom genomes, then there are two options: Either those entries need to be added to the file (e.g. with Excel), or, the SparK pyhton file can be easily modified to recognize other formats. Where Python extracts the gene name and transcript ID's is specified in the "get_gene_name" and "get_transcript_name" functions at the beginning of the script. Of note, the  entry transcript_ID is only neccecary if individual transcripts were to be plotted. If only genes are plotted, then a "gene_name" entry is enough in the gtf file.



### Dealing with methylation data/my data has the wrong y-Axis/looks different than in IGV:
If you are working with data that has very sharp and narrow peaks, like methylation data, or plotting larger regions with data that has sharp peaks you might encounter the following: The y-axis indicates lower values for your data than what you expected, and your data looks different from what you have seen in IGV. If you plot a large region like 100 kb, then you have more data points than pixels in your plot. There are different ways of dealing with this, and SparK will calculate the average signal for each pixel of the plot. Say you have to squeeze 10 data points into each pixel of the plot, and you only have one methylation site (one single base) with a value of 1.0 for a stretch of 10 bases, then you will end up with an average value of 0.1 for that one pixel in the SparK plot. IGV will show you a peak with 1.0. when in default setting. See the attached example. I have plotted a larger region of methylation data with IGV, you can see that the data ranges to 1.0, which is what you were expecting. However, the data is so highly clustered that it really doesn't tell you anything. See for instance the red square (1). If we zoom in once, we can notice that what looked as one massive block of methylation is actually two distinct sites (2). Further, both sites seem to have the same amount of methylation. If we zoom in again, we can see that those two sites are not the same at all, but in fact very different in amount of methylation that is present (3). So even zooming in once doesn't give us meaningful data in IGV yet. In SparK plots the values don't go up to 1, but SparK plots depict a meaningful representation of the data, even in the most zoomed out version.
<img src="https://github.com/harbourlab/SparK/blob/master/methylation_example.png" width="900">
