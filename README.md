# SparC

 <img src="https://raw.githubusercontent.com/StefanKurtenbach/SparC/master/Example1.jpg" width="400">

<pre>
Plot NGS bedgraph tracks including replicates, overlay and color functions, standard deviations and more. 
Output files are true vector graphics (.svg) for easy editing.

Requirements:
  - numpy
 
Options (Required):
-cf   control bedgraph files seperated by space
-tf   treatment bedgraph files seperated by space
-pr   region to be plotted example: chr1:1647389-272634
-ps   which plots to show. Choices: all, averages. Plots average tracks of control and treatment files
-pt   plot type. Choices: standard, STD, sine


Options (Not required):
-cg   control groups. Will seperately plot groups. e.g. "-cg 1 1 2 2" will generate 2 plots
-tg   treatment groups. Will seperately plot groups. e.g. "-cg 1 1 2 2" will generate 2 plots
-l    labels for groups defined above. e.g. "RNaseq H3K4me3"
-gs   group autoscale. usage: "-gs yes". Will autoscale all groups
-es   exclude groups from autoscaling. e.g. "-es 1"
-f    fill colors. Enter two colors in hex format.
-gff  link gff file to show genes
-sp   add "sparcs" - significant differences. Usage: "-sp yes"
-sc   sparc color. Enter one color in hex format
-sm   smoothen tracks. Integer value. (plots are 2000 data points wide. "-sm 10" will smoothen with a window of 10.


Example comparing different datatypes for 2 cell lines (K562 and HepG2) which was used to generate the figure above:

python SparC -pt standard -ps averages -pr chr12:6533888-6539592 \
-tf K562_H3K27AC_1.bdg K562_H3K27AC_2.bdg K562_H3K4me3_1.bdg K562_H3K4me3_2_ENCFF352VRB.bigWig.bdg K562_H3K27me3_1.bdg K562_H3K27me3_2.bdg K562_RNAseq.bdg K562_RNAseq.bdg K562_DNAseseq_1.bdg K562_DNAseseq_2.bdg \
-cf HepG2_H3K27AC_1.bdg HepG2_H3K27AC_2_ENCFF348RLL.bdg HepG2_H3K4me3_1.bdg HepG2_H3K4me3_2.bdg HepG2_H3K27me3_1.bdg H3K27me3_2.bdg HepG2_RNAseq_plus_1.bdg /HepG2_RNAseq_2.bdg HepG2_DNAseseq_1.bdg K562_DNAseseq_2.bdg \
-cg 1 1 2 2 3 3 4 4 5 5 \
-tg 1 1 2 2 3 3 4 4 5 5 \
-gl H3K27AC H3K4me3 H3K27me3 RNAseq DNaseseq \
-l K562 HepG2 \
-gff gencode.v24.primary_assembly.annotation.txt \
-gs yes \
-es 5


Other examples:
 <img src="https://raw.githubusercontent.com/StefanKurtenbach/SparC/master/Picture2.png" width="400">
 
</pre>
