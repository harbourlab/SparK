# SparK - Publication quality NGS data plotting (Version 2)
Feature requests are welcome! For help, bug reports, and to request features contact Stefan.Kurtenbach@me.com
<pre>
Plot NGS bedgraph tracks including replicates, overlay, and standard deviations. 
Output files are true vector graphics (.svg) for easy editing.

Requirements:
  - numpy
 
 
Options (Required):
-cf   control bedgraph files seperated by space
-pr   region to be plotted. Example: "-pr chr1:1647389-272634"


Options (Not required):
-pt      plot type. Choices: "standard", "STD", "sine"
-cg      control groups. Will seperately plot groups. e.g. "-cg 1 1 2 2" will generate 2 plots,
         where plot 1 includes the first two files listed in "-cf", and plot 2 file 3 and 4
-tg      Define treatment groups here.
-gl      Label the groups defined in -cg and -tg. e.g. "-gl RNAseq H3K4me3" will label group 1 with RNAseq, 
         and group 2 with H3K4me3
-tf      treatment bedgraph files seperated by space
-l       labels for control and treatment groups. defined above. e.g. "-l brain_cells tumor_cells". 1st
         1st is controls, second entry treatment group
-gs      group autoscale. usage: "-gs yes". Will autoscale all groups.
-es      exclude groups from autoscaling. e.g. "-es 1"
-ps      Set to "averages" if control and treatment tracks should be averaged.
-f       fill colors for the tracks. Choices: "blue/red" (default), "blue/grey", "all_grey", "blue/green".
         Two hex colors can be entered alternatively. Examples" "-f blue/grey", "-f 00FF12 848484".
-sp      add significant differences in tracks aka "sparks". Usage: "-sp yes". Significant areas 
         are defined as areas where the delta of the means is greater than the sum of standard deviations 
         of controls and treatment files. 
-sc      spark color. Enter two colors in hex format for significantly increase and decreased areas. 
         Example "-sc 00FF12 848484".
-sm      smoothen tracks. Integer value. (plots are 2000 data points wide. "-sm 10" will smoothen 
         with a window of 10.
-o       output filename. Usage: "-o Experiment1".
-bed     Add bed files to plot here. Usage: "-bed bedfile1.bed bedfile2.bed"...
-bedcol  choose colors for bed tracks (in hex). Default is blue. Choose either one color, or same amount 
         as bed tracks given
-gff     link gff file to show genes. Get here: https://www.gencodegenes.org/human/
-dg      in case not all genes in the region plotted should be displayed, enter the genes to plot here.
         Usage: "-dg GAPDH RS1"
-dt      Display transcripts. By default, all available transcripts for a gene will be merged and plotted as one. If 
         If all annotated transcripts should be plotted, set this to "all". Alternatively, transcript IDs can be listed 
         to plot only certain transcripts
-wg      If all or individual transcripts are beeing plotted (-dt function) instead of the merged default, then "-wg yes" can
         be used to plot gene name instead of transcript ID.
-tss     set to "no" to avoid TSS sites and direction of transcription being indicated with arrows.
-scale   Plot scalebar. Set to "no" if no scalebar should be plotted.
-w       Define plot width. Default is 150.


Getting started:

Plotting multiple NGS tracks. Example of a plot of 4 ChIP-seq tracks with standard settings.

<img src="https://github.com/StefanKurtenbach/SparK/blob/master/FigureA.png" width="400">  

Code:
python SparK.py \
-pr chr12:6520512-6640512 \
-cf HepG2_H3K27AC_1_ENCFF495QSO.bigWig.bdg HepG2_H3K27AC_2_ENCFF348RLL.bigWig.bdg HepG2_H3K4me3_1_ENCFF699DRO.bigWig.bdg HepG2_H3K4me3_2_ENCFF400FYO.bigWig.bdg \
-gff gencode.v24.primary_assembly.annotation.txt \
-gl H3K27AC H3K4me3 H3K27AC-2 H3K4me3-2 \
-dg GAPDH IFFO1 NOP2 CHD4 LPAR5

Note: The -dg option is optional and was used to plot only the five major genes in this area.


Example of plotting the comparison of ChIP-seq data of two cell lines (HepG2 and K562).

<img src="https://github.com/StefanKurtenbach/SparK/blob/master/FigureB.png" width="400"> 

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

Note: In this example figure, using -dg only GAPDH was plotted.




<img src="https://github.com/StefanKurtenbach/SparK/blob/master/bedfile%20examples.png" width="400">

Left: Example of a larger stretch (110kb) beeing plotted with standard colors, subset of genes,
TSS sites with direction of transcription, and scale bar. Right: Example with "blue/green" color 
scheme and bed files with custom colors. Scale bar and TSS sites were not plotted.


<img src="https://github.com/StefanKurtenbach/SparK/blob/master/smoothing2.png" width="400">  <img src="https://raw.githubusercontent.com/StefanKurtenbach/SparK/master/sparks.png" width="400">
Left: Example of different smoothing windows. Right: Example of sparks beeing added to a plot 
with blue/grey color scheme.


<img src="https://raw.githubusercontent.com/StefanKurtenbach/SparK/master/Example1.jpg" width="400">

Example comparing different datatypes for 2 cell lines (K562 and HepG2) 
which was used to generate the left figure above:

python SparK.py -pt standard -ps averages -pr chr12:6533888-6539592 \
-tf K562_H3K27AC_1.bdg K562_H3K27AC_2.bdg K562_H3K4me3_1.bdg K562_H3K4me3_2_ENCFF352VRB.bigWig.bdg K562_H3K27me3_1.bdg K562_H3K27me3_2.bdg K562_RNAseq.bdg K562_RNAseq.bdg K562_DNAseseq_1.bdg K562_DNAseseq_2.bdg \
-cf HepG2_H3K27AC_1.bdg HepG2_H3K27AC_2_ENCFF348RLL.bdg HepG2_H3K4me3_1.bdg HepG2_H3K4me3_2.bdg HepG2_H3K27me3_1.bdg H3K27me3_2.bdg HepG2_RNAseq_plus_1.bdg /HepG2_RNAseq_2.bdg HepG2_DNAseseq_1.bdg K562_DNAseseq_2.bdg \
-cg 1 1 2 2 3 3 4 4 5 5 \
-tg 1 1 2 2 3 3 4 4 5 5 \
-gl H3K27AC H3K4me3 H3K27me3 RNAseq DNaseseq \
-l K562 HepG2 \
-gff gencode.v24.primary_assembly.annotation.txt \
-gs yes \
-es 5


<img src="https://raw.githubusercontent.com/StefanKurtenbach/SparK/master/Picture2.png" width="400">
Example of other plot types.



</pre>
