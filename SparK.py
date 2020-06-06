SparK_Version = "2.6.2"
# Stefan Kurtenbach
# Stefan.Kurtenbach@me.com

# FIX what happens if region is smaller than 2000?
# could make resolution choosable. 2000 now

import numpy as np
import copy
import os
import argparse
import math
import sys

def get_gene_name():
    return(line_split[8].split("gene_name ")[1].split('''"''')[1])
def get_transcript_name():
    try:
        return(line_split[8].split("transcript_id ")[1].split('''"''')[1])
    except:
        print("Error: SparK tried to extract information to plot genes in the selected area from the following line in the gtf file but failed. Please check the format thoroughly, and read the SparK github page for how the gtf needs to be structured for genes to be plotted, or how to change this python script to work with this specific gtf.")
        print(line_split)
def draw_line(coordinates, thickness, color):
    output = '''<path d="'''
    for x, i in enumerate(coordinates):
        if x == 0:
            output += "M "
        else:
            output += " L "
        output += str(i[1]) + " " + str(y_start - i[0])
    output += '''" style="stroke:'''+ color + '''; stroke-width:'''+ str(thickness) +'''; fill:none "/>'''
    return(output)
def make_raw_data_filled(stretch, files, offset):  # files[ctrl,treat]
    raw_data_filled = [[0] * (stretch[2] - stretch[1]) for r in range(len(files))]
    for a, datafile2 in enumerate(files):
        with open(datafile2) as f:
            found_chromosome = "no"
            for line in f:
                line_split = line.split("\t")
                try:
                    if line_split[0][:3] == "chr" or line_split[0][:3] == "Chr":
                        line_split[0] = line_split[0][3:]
                except:
                    pass
                if found_chromosome == "yes" and line_split[0] != stretch[0]:
                    break

                if line_split[0] == stretch[0]:
                    try:
                        line_split[3] = float(line_split[3].split("\n")[0])
                    except:
                        print("Warning! Could not import following row from: " + datafile2)
                        print(line)
                        print("Continuing to Import...")
                        print("")
                    found_chromosome = "yes"
                    if int(line_split[2]) >= stretch[1] + offset:
                        if int(line_split[1]) <= stretch[2] + offset:
                            for iteration in range(int(line_split[2]) - int(line_split[1])):
                                try:
                                    raw_data_filled[a][int(line_split[1]) + iteration - stretch[1] + offset] = line_split[3]
                                except:
                                    pass

    # shrink to max_datapoints if bigger
    max_datapoints = 2000
    if stretch[2] - stretch[1] > max_datapoints:
        binfactor_split = math.modf(float((float(stretch[2] - stretch[1]))/max_datapoints))  # get values after and before period
        binfactor = sum(binfactor_split)
        temp_data = [[] for u in range(len(files))]  # new data list
        for workingfilenr in range(len(files)):
            for position in range(max_datapoints):
                start_postition_split = math.modf(position * binfactor)  # after and before period

                # first add fraction of start position or entire value if no fraction
                temp_value = float(raw_data_filled[workingfilenr][(int(start_postition_split[1]))] * (1 - start_postition_split[0]))
                binfactor_left = binfactor - (1 - start_postition_split[0])

                # add all values with no fractions
                iteration = 0
                while binfactor_left > 1:
                    temp_value += raw_data_filled[workingfilenr][int(start_postition_split[1]) + 1 + iteration]
                    iteration += 1
                    binfactor_left -= 1

                # add last fraction or value if no fraction
                if binfactor_left > 0:
                    if float((start_postition_split[1]) + 1 + iteration) < len(raw_data_filled[0]):
                        temp_value += raw_data_filled[workingfilenr][int(start_postition_split[1]) + 1 + iteration] * binfactor_left
                        temp_data[workingfilenr].append(temp_value/sum(binfactor_split))
        raw_data_filled = copy.deepcopy(temp_data)

    if smoothen_tracks is not None:
        raw_data_filled_smooth = [[0] * 2000 for r in range(len(files))]
        for x, dataset in enumerate(raw_data_filled):
            temp = [dataset[0]] * smoothen_tracks
            for p, i in enumerate(dataset):
                temp.append(i)
                temp.pop(0)
                raw_data_filled_smooth[x][p] = np.average(temp)
        raw_data_filled = copy.deepcopy(raw_data_filled_smooth)
    return raw_data_filled
def write_to_file(row):
    with open(output_filename, "a") as f:
        f.write(row)
        f.write("\n")
def get_max_value(datasets1, datasets2):
    plottingaverages = False
    if show_plots == "averages":
        plottingaverages = True
    max_1 = []
    for datafile1 in datasets1:
        max_1.append(max(datafile1))
    max_2 = []
    for datafile2 in datasets2:
        max_2.append(max(datafile2))
    if plottingaverages == True:
        if max_2 != []:
            if max_2 != []:
                return max([np.average(max_1), np.average(max_2)])
            else:
                return(np.average(max_1))
    elif plottingaverages == False:
        if max_2 != []:
            return max([max(max_1), max(max_2)])
        else:
            return(max(max_1))
def get_relative_hight(raw_value): # FIX make sure maxvalue can be 0 too
    if raw_value == 0:
        return(0)
    else:
        return((raw_value * hight * relative_track_hight_percentage) / max_value) # to not go up to the max
def draw_rect(x_coord, y_0, color, width, hight1, opacity):
    return '''<rect x="''' + str(x_coord) + '''" opacity="''' + str(opacity) + '''" y="''' + str(y_0 - hight1) + '''" fill="''' + color + '''" width="''' + str(width) + '''" height="''' + str(hight1) + '''"/>'''
def draw_polygon(coordinates, opacity, color, stroke_width):
    for q, w in enumerate(coordinates):
        coordinates[q][0] = y_start - coordinates[q][0]
    string = '''<polygon points="'''
    for h, c in enumerate(coordinates):
        if h == 0:
            string += str(c[1]) + "," + str(c[0])
        else:
            string += " " + str(c[1]) + "," + str(c[0])
    string += '''" opacity="''' + str(opacity) + '''" fill="''' + color + '''"''' + ''' stroke="black" stroke-width="''' + str(stroke_width) + '''"/>'''
    return string
def draw_standard_spark():
    if len(control_data) > 1 and len(treat_data) > 1:
        last_xpos = -1
        coords = []  # y/x, spark color
        last_value = ""
        for x, value in enumerate(control_data[0]):
            x_pos = x_start + (x * quantile)  # y/x
            ctrl_values = []
            treat_values = []
            for p, i in enumerate(control_data):
                ctrl_values.append(control_data[p][x])
            for p, i in enumerate(treat_data):
                treat_values.append(treat_data[p][x])

            sum_std = np.std(ctrl_values) + np.std(treat_values)
            if abs(np.average(ctrl_values) - np.average(treat_values)) > sum_std:
                if np.average(ctrl_values) > np.average(treat_values):
                    if last_value == "" or last_value == "up":
                        if (last_xpos + 1) == x:
                            coords.append([get_relative_hight(np.average(ctrl_values) - np.std(ctrl_values)), x_pos])
                            coords.insert(0, [get_relative_hight(np.average(treat_values) + np.std(treat_values)), x_pos])
                            last_xpos = x
                        else:
                            if len(coords) > 0:
                                write_to_file(draw_polygon(coords, 0.8, spark_color[1], stroke_width_spark))
                            coords = [[get_relative_hight(np.average(ctrl_values) - np.std(ctrl_values)), x_pos]]
                            coords.insert(0, [get_relative_hight(np.average(treat_values) + np.std(treat_values)), x_pos])
                            last_xpos = x
                            last_value = "up"
                    else:
                        if len(coords) > 0:
                            write_to_file(draw_polygon(coords, 0.8, spark_color[0], stroke_width_spark))
                        coords = [[get_relative_hight(np.average(ctrl_values) - np.std(ctrl_values)), x_pos]]
                        coords.insert(0, [get_relative_hight(np.average(treat_values) + np.std(treat_values)), x_pos])
                        last_xpos = x
                        last_value = "up"

                if np.average(ctrl_values) < np.average(treat_values):
                    if last_value == "" or last_value == "down":
                        if (last_xpos + 1) == x:
                            coords.append([get_relative_hight(np.average(treat_values) - np.std(treat_values)), x_pos])
                            coords.insert(0, [get_relative_hight(np.average(ctrl_values) + np.std(ctrl_values)), x_pos])
                            last_xpos = x
                        else:
                            if len(coords) > 0:
                                write_to_file(draw_polygon(coords, 0.8, spark_color[0], stroke_width_spark))
                            coords = [[get_relative_hight(np.average(treat_values) - np.std(treat_values)), x_pos]]
                            coords.insert(0, [get_relative_hight(np.average(ctrl_values) + np.std(ctrl_values)), x_pos])
                            last_xpos = x
                            last_value = "down"
                    else:
                        if len(coords) > 0:
                            write_to_file(draw_polygon(coords, 0.8, spark_color[1], stroke_width_spark))
                        coords = [[get_relative_hight(np.average(treat_values) - np.std(treat_values)), x_pos]]
                        coords.insert(0, [get_relative_hight(np.average(ctrl_values) + np.std(ctrl_values)), x_pos])
                        last_xpos = x
                        last_value = "down"
        if len(coords) > 0:
            if last_value == "up":
                write_to_file(draw_polygon(coords, spark_opacity, spark_color[0], stroke_width_spark))
            elif last_value == "down":
                write_to_file(draw_polygon(coords, spark_opacity, spark_color[1], stroke_width_spark))
    else:
        print("Error: Some Sparks not plotted as sparks require at least 2 control and treatment files per plot")
def get_region_to_draw():
    region_to_draw = 0
    if line_split[4] > region[1] and line_split[3] < region[2]: # check if there is something to draw
        region_to_draw = [float(line_split[3]), float(line_split[4])]
        if line_split[3] < region[1]:
            region_to_draw[0] = float(region[1])
        if line_split[4] > region[2]:
            region_to_draw[1] = float(region[2])
    return(region_to_draw)

parser = argparse.ArgumentParser(description='SparC_args')
parser.add_argument('-pt','--plot_type', help='choices: standard, STD, sine', required=False, type=str, default="standard")
parser.add_argument('-ps','--show_plots', help='choices: all, averages', required=False, type=str, default="all")
parser.add_argument('-pr','--region', help='example: chr1:1647389-272634', required=True, type=str)
parser.add_argument('-cf','--control_files', help='separate by space', required=True, nargs='+', type=str)
parser.add_argument('-tf','--treat_files', help='separate by space', required=False, nargs='+', type=str, default=[])
parser.add_argument('-cg','--control_groups', help='group numbers separate by spacse', required=False, nargs='+', type=int, default=[])
parser.add_argument('-tg','--treat_groups', help='group numbers separate by space', required=False, nargs='+', type=int, default=[])
parser.add_argument('-gl','--group_labels', help='set group labels', required=False, nargs='+', type=str)
parser.add_argument('-l','--labels', help='set labels for controls and treatment', required=False, nargs='+', type=str)
parser.add_argument('-gs','--group_autoscale', help='set to "yes" to autoscale all groups(plots), except the groups excluded in -eg', required=False, type=str)
parser.add_argument('-es','--exclude_from_group_autoscale', help='group numbers of groups to be excluded from autoscale', required=False, nargs='+', type=int)
parser.add_argument('-eg','--exclude_groups', help='Exclude groups from the analysis', required=False, nargs='+', type=int)
parser.add_argument('-f','--fills', help='track colors. One or two colors in hex format for control and treatment tracks', required=False, nargs='+', type=str, default=None)
parser.add_argument('-cs','--custom_y_axis_scales', help='Enter y-axis values for all groups(plots). All groups need a value. Enter "D" for each group no value should be assigned, e.g. to keep autoscaling functionality for some groups', required=False, nargs='+', type=str)
parser.add_argument('-dc','--display_chrom_location', help='set to "no" if you do not want to plot the chromosomal coordinates', required=False, type=str, default="top_left")
parser.add_argument('-gtf', '--gtffile', help='link gtf file for drawing genes here', required=False, type=str)
parser.add_argument('-tss', '--drawtss', help='set to "no" if TSS sites should not be indicated', required=False, type=str, default="yes")
parser.add_argument('-genestart', '--draw_genestart', help='set to "yes" if TSS sites should be indicated', required=False, type=str, default="no")
parser.add_argument('-sp', '--spark', help='display significant change "yes"', required=False, type=str)
parser.add_argument('-sc', '--spark_color', help='spark color', required=False, type=str, nargs='+')
parser.add_argument('-sm', '--smoothen', help='smoothen tracks, int', required=False, type=int)
parser.add_argument('-o','--output_name', help='output graph name, str', required=False, type=str)
parser.add_argument('-bed','--bed_files', help='bed files to be plotted', required=False, type=str, nargs='+')
parser.add_argument('-bedcol','--bed_color', help='colors of bed files in hex', required=False, type=str, nargs='+')
parser.add_argument('-bedlab','--bed_labels', help='set labels for bed tracks', required=False, nargs='+', type=str)
parser.add_argument('-w','--track_width', help='width of the track, default = 150, int', required=False, type=int, default=150)
parser.add_argument('-dg','--display_genes', help='genes to display from the gtf file', nargs='+', required=False, type=str)
parser.add_argument('-dt','--display_transcripts', help='display custom transcripts. By default, all transcripts annotated in the gtf file will be merged and displayed as one gene. Alternatively all can be plotted seperatelly by setting this to "all". Further, Transcript IDs can be listed to plot only certain transcripts', nargs='+', required=False, type=str, default=["mergeall"])
parser.add_argument('-wg','--write_genenames', help='write genename instead of transcript ID when transcripts are plotted. Set to "yes".', required=False, type=str, default="no")

parser.add_argument('-scale','--display_scalebar', help='set to "no" to remove scalebar', required=False, type=str, default="yes")
args = vars(parser.parse_args())

print(" ")
print('''SparK Version ''' + SparK_Version + ''' initiated''')

# Additional Arguments #########################################
hight = 30  # hight of plots
x_start = 50
spark_opacity = 1
stroke_width = 0  # 0.1 stroke widths good
stroke_width_spark = 0
plot_all_TSS = False  ## could plot all TSS sites
relative_track_hight_percentage = 0.9
################################################################

# import arguments #############################################
bed_files = args["bed_files"]
bed_color = args['bed_color']
draw_TSS = args['drawtss']

display_transcripts = args['display_transcripts']
plot_gene_name_instead_transcriptID = args['write_genenames']
if plot_gene_name_instead_transcriptID not in ["yes", "no"]:
    print("Error: 'write_genenames' is not set to 'yes' or 'no'.")


bed_labels = args['bed_labels']
if bed_files is not None:
    if bed_labels is not None:
        if len(bed_labels) != len(bed_files):
            print("Error: Number of bed lables does not match number of bed tracks")
            sys.exit()
    else:
        bed_labels = bed_files


if bed_files is not None:
    if bed_color is not None:
        if len(bed_color) == len(bed_files):
            for i in range(len(bed_color)):
                bed_color[i] = "#" + bed_color[i]
        elif len(bed_color) == 1:
            bed_color = ["#" + bed_color[0]] * len(bed_files)

        else:
            print("Error loading colors for bed files. Choose either one, or same number of colors as bed tracks given")
    else:
        bed_color = ["#0B34FF"] * len(bed_files)

smoothen_tracks = args['smoothen']

output_filename = args['output_name']
if output_filename is None:
    output_filename = "SparK_graph.svg"
else:
    output_filename += ".svg"

display_genes = args['display_genes']

display_genestart = args['draw_genestart']

width = args['track_width']
if width is not None:
    total_width = int(width)

fills = args['fills']  # [0] is control, [1] is treatment group
if fills is None:
    if args['treat_groups'] == []:  # color if there is no treat group
        fills = ["#0000C1", "0"]
        opacity = 1
    elif args['treat_groups'] != []:
        fills = ["#FF1800", "#005CFF"]  # blue/red as default
        opacity = 0.6

elif fills[0] == "blue/red":
    fills = ["#FF1800", "#005CFF"]  # right is ctrl blue
    opacity = 0.6

elif fills[0] == "blue/grey":
    fills = ["#005CFF", "#A3A3A3"]  # right is ctrl grey
    opacity = 0.3

elif fills[0] == "all_grey":
    fills = ["#848484", "#848484"]
    opacity = 0.6

elif fills[0] == "blue/green":
    fills = ["#00FF12", "#005CFF"]
    opacity = 0.5

elif len(fills) == 1:
    fills = ["#" + fills[0], "#" + fills[0]] # fills has to be len 2 for code below
    opacity = 1

elif len(fills) == 2:
    for i in range(len(fills)):
        fills[i] = "#" + fills[i]
        opacity = 0.6

plot_type = args['plot_type']  # standard, STD, sine
if plot_type not in ["standard", "STD", "sine"]:
    print("Error: No valid plot type entered. Choose 'standard', 'STD', or 'sine'")
    sys.exit()

show_plots = args['show_plots']  # all, averages
if show_plots not in ["all", "averages"]:
    print("Error: Not valid option for plots selected, choose 'all' or 'averages'")
    sys.exit()
elif show_plots == "averages":
    print("Plotting averages")

elif show_plots == "standard":
    print("Plotting individual tracks")

region = [args['region'].split(":")[0], int(args['region'].split(":")[1].split("-")[0]), int(args['region'].split(":")[1].split("-")[1])] # [chr, start, stop]
if region is None:
    print("No region defined")
else:
    try:
        region = [args['region'].split(":")[0], int(args['region'].split(":")[1].split("-")[0]), int(args['region'].split(":")[1].split("-")[1])]
    except:
        print("Error: Region defined seems to have a weird format. Use 'chr1:123-345' format.")
        sys.exit()

    print("Plotting region: " + args['region'])
    if region[0][:3] == "chr" or region[0][:3] == "Chr":
        region[0] = region[0][3:]

display_scalebar = args['display_scalebar']

spark = args['spark']
if spark == "yes":
    print("Sparks will be drawn")
    spark_color = args['spark_color']
    if spark_color is not None:
        if len(spark_color) != 2:
            print('''Error: Spark color definition not correct. Enter two hex colors e.g. "-sc 00FF12 848484"''')
            sys.exit()
        else:
            spark_color[0] = "#" + spark_color[0]
            spark_color[1] = "#" + spark_color[1]
    else:
        spark_color = ["#FF0000", "#00FF00"]  # red/green
        stroke_width_spark = 0.05
        spark_opacity = 0.5

all_control_files = args['control_files']
if all_control_files is None:
    print("Error: No control files set")
    sys.exit()
all_treat_files = args['treat_files']

group_autoscale = args['group_autoscale']
if group_autoscale is not None:
    if group_autoscale != "yes":
        print("Error: Group autoscale is set but not with 'yes'. Do you want to autoscale?")
        sys.exit()
    else:
        print("Autoscaling enabled")
group_autoscale_excluded = args['exclude_from_group_autoscale']
if group_autoscale_excluded is not None:
    print("Excluding the following groups from autoscaling: " + str(group_autoscale_excluded))
else:
    group_autoscale_excluded = []

control_groups = args["control_groups"]
treat_groups = args["treat_groups"]

if control_groups == [] and treat_groups == []: # this sets the groups when none are defined
    if show_plots == "averages": # makes only one group in this case
        nr_of_groups = 1
        for i in range(len(all_control_files)):
            control_groups.append(1)
        for i in range(len(all_treat_files)):
            treat_groups.append(1)
    else:
        nr_of_groups = len(all_treat_files + all_control_files) # plots all individually
        number = 1
        for i in range(len(all_control_files)):
            control_groups.append(number)
            number += 1
        for i in range(len(all_treat_files)):
            treat_groups.append(number)
            number += 1
else:
    if treat_groups == []:
        nr_of_groups = max(control_groups)
    else:
        nr_of_groups = max([max(control_groups), max(treat_groups)])

custom_scales = args["custom_y_axis_scales"]
if custom_scales is not None:
    if len(custom_scales) != nr_of_groups:
        print("Error: Number of custom y-scales is not the same as number of groups(plots)")
        sys.exit()

group_labels = args['group_labels']
if group_labels is not None:
    if len(group_labels) != nr_of_groups:
        print("Error: Number of group lables does not match number of groups set")
        sys.exit()

labels = args['labels']
if labels is not None:
    if len(labels) != 2:
        print("Error: Two arguments have to be provided for labels (-l), not more or less")
        sys.exit()

exclude_groups = args["exclude_groups"]
if exclude_groups is None:
    exclude_groups = []
else:
    print("Excluding following groups: " + str(exclude_groups))


gff_file = args['gtffile']

if os.path.exists(output_filename):
    os.remove(output_filename)
#############################################################################################################


#check how many genes will be plotted in that region to make file size correct... for the future
hight_bed = 0
write_to_file('''<svg viewBox="0 0 320 ''' + str(150 + (hight * 2 * nr_of_groups) + hight_bed) + '''" xmlns="http://www.w3.org/2000/svg">''')

# make list of files and global max - useful for autoscaling only ###########################################
if group_autoscale == "yes":
    ctrl_averages = []
    treat_averages = []
    for group in range(nr_of_groups):
        control_files = []
        treat_files = []
        for x, i in enumerate(control_groups):
            if i not in group_autoscale_excluded:
                if i == group + 1:
                    if i not in exclude_groups:
                        control_files.append(all_control_files[x])
        for x, i in enumerate(treat_groups):
            if i not in group_autoscale_excluded:
                if i == group + 1:
                    if i not in exclude_groups:
                        treat_files.append(all_treat_files[x])
        if control_files != []:
            ctrl_averages.append(np.average([max(sublist) for sublist in make_raw_data_filled(region, control_files, 0)]))
        if treat_files != []:
            treat_averages.append(np.average([max(sublist) for sublist in make_raw_data_filled(region, treat_files, 0)]))

    if treat_averages == []:
        autoscale_max = max(ctrl_averages)
    else:
        autoscale_max = max([max(ctrl_averages), max(treat_averages)])
#############################################################################################################


# Plot NGS tracks
if (region[2] - region[1]) <= 2000:
    quantile = float(total_width)/(region[2] - region[1])
else:
    quantile = float(total_width)/2000
additional_hight = 0

for group in range(nr_of_groups):
    y_start = 100 + group * hight * 1.5 + additional_hight # neccessary for sine plots
    control_files = []
    treat_files = []
    for x, i in enumerate(control_groups):
        if i == group + 1:
            if i not in exclude_groups:
                control_files.append(all_control_files[x])
    for x, i in enumerate(treat_groups):
        if i == group + 1:
            if i not in exclude_groups:
                treat_files.append(all_treat_files[x])

    control_data = make_raw_data_filled(region, control_files, 0)
    treat_data = make_raw_data_filled(region, treat_files, 0)

# here the max value for the group(plot) is determined
    if group_autoscale == "yes":
        if (group + 1) not in group_autoscale_excluded:
            max_value = autoscale_max # global_max_value is derived only from the groups that were not excluded
        else:
            max_value = get_max_value(control_data, treat_data)
    else:
            max_value = get_max_value(control_data, treat_data)
    if custom_scales is not None:
        if custom_scales[group] != "D":
            max_value = float(custom_scales[group])


    if plot_type == "standard":
        if show_plots == "all":
            for datafile in control_data:
                coords = []  # y/x
                for x, value in enumerate(datafile):
                    x_pos = x_start + (x * quantile)
                    coords.append([get_relative_hight(value), x_pos])
                coords[-1][0] = 0
                coords[0][0] = 0
                write_to_file(draw_polygon(coords, opacity, fills[0], stroke_width))
            for datafile in treat_data:
                coords = []  # y/x
                for x, value in enumerate(datafile):
                    x_pos = x_start + (x * quantile)
                    coords.append([get_relative_hight(value), x_pos])
                coords[-1][0] = 0
                coords[0][0] = 0
                write_to_file(draw_polygon(coords, opacity, fills[1], stroke_width))

        if show_plots == "averages":
            coords = []
            for x in range(len(control_data[0])):
                averages = []
                x_pos = x_start + (x * quantile)
                for datafile in control_data:
                    averages.append(datafile[x])
                coords.append([get_relative_hight(np.average(averages)), x_pos])
            coords[-1][0] = 0
            coords[0][0] = 0
            write_to_file(draw_polygon(coords, opacity, fills[0], stroke_width))
            coords = []
            if treat_data != []:
                for x in range(len(treat_data[0])):
                    averages = []
                    x_pos = x_start + (x * quantile)
                    for datafile in treat_data:
                        averages.append(datafile[x])
                    coords.append([get_relative_hight(np.average(averages)), x_pos])
                coords[-1][0] = 0  # make first and last value zero FIX
                coords[0][0] = 0
                write_to_file(draw_polygon(coords, opacity, fills[1], stroke_width))
        if spark == "yes":

            draw_standard_spark()

    elif plot_type == "STD":
        if len(control_data) > 1 and len(treat_data) > 1:
            coords = []
            ctrl_line = []
            for x in range(len((control_data[0]))):
                x_pos = x_start + (x * quantile)  # y/x
                values = []
                for p, i in enumerate(control_data):
                    values.append(control_data[p][x])
                coords.append([get_relative_hight(np.average(values) + np.std(values)), x_pos])
                coords.insert(0, [get_relative_hight(np.average(values) - np.std(values)), x_pos])
                ctrl_line.append([get_relative_hight(np.average(values)), x_pos])
            write_to_file(draw_polygon(coords, 0.4, fills[0], stroke_width))
            write_to_file(draw_line(ctrl_line, 0.3, str(fills[0])))
            coords = []
            treat_line = []
            for x in range(len((treat_data[0]))):
                x_pos = x_start + (x * quantile)  # y/x
                values = []
                for p, i in enumerate(treat_data):
                    values.append(treat_data[p][x])
                coords.append([get_relative_hight(np.average(values) + np.std(values)), x_pos])
                coords.insert(0, [get_relative_hight(np.average(values) - np.std(values)), x_pos])
                treat_line.append([get_relative_hight(np.average(values)), x_pos])
            write_to_file(draw_polygon(coords, 0.4, fills[1], stroke_width))
            write_to_file(draw_line(treat_line, 0.3, str(fills[1])))

            if spark == "yes":
                draw_standard_spark()
        else:
            print("Error: STD plots require at least 2 control and treatment files per plot")

    elif plot_type == "sine": # treat points up, control points down #FIX combined with averages does not work
        if len(control_data) >= 1 and len(treat_data) >= 1:
            for datafile in control_data:
                coords = []  # y, x
                for x, value in enumerate(datafile):
                    x_pos = x_start + (x * quantile)
                    coords.append([get_relative_hight(-value), x_pos])
                coords[-1][0] = 0
                coords[0][0] = 0
                write_to_file(draw_polygon(coords, opacity, fills[0], stroke_width))
            for datafile in treat_data:
                coords = []  # y, x
                for x, value in enumerate(datafile):
                    x_pos = x_start + (x * quantile)
                    coords.append([get_relative_hight(value), x_pos])
                coords[-1][0] = 0
                coords[0][0] = 0
                write_to_file(draw_polygon(coords, opacity, fills[1], stroke_width))
            additional_hight += 30  # sine plots need extra hight
            if spark == "yes":
                last_xpos = -1
                coords = []
                last_value = ""
                for x in range(len((control_data[0]))):
                    x_pos = x_start + (x * quantile)
                    ctrl_values = []
                    treat_values = []
                    for p, i in enumerate(control_data):
                        ctrl_values.append(control_data[p][x])
                    for p, i in enumerate(treat_data):
                        treat_values.append(treat_data[p][x])
                    if abs(np.average(ctrl_values) - np.average(treat_values)) > (np.std(ctrl_values) + np.std(treat_values)):
                        if np.average(ctrl_values) > np.average(treat_values):
                            if last_value == "" or last_value == "ctrl_up":
                                if (last_xpos + 1) == x:
                                    coords.append([-1 * get_relative_hight((abs(np.average(ctrl_values)-np.average(treat_values)) - np.std(treat_values) - np.std(ctrl_values))), x_pos])
                                    coords.append([-1 * get_relative_hight((abs(np.average(ctrl_values)-np.average(treat_values)) - np.std(treat_values) - np.std(ctrl_values))), x_pos])
                                    last_xpos = x
                                else:
                                    if len(coords) > 0:
                                        coords.insert(0, [get_relative_hight(0), coords[0][1] - quantile])
                                        coords.append([get_relative_hight(0), coords[-1][1] + quantile])
                                        write_to_file(draw_polygon(coords, 1, spark_color[1], stroke_width_spark))
                                    coords = []
                                    coords.append([-1 * get_relative_hight((abs(np.average(ctrl_values)-np.average(treat_values)) - np.std(treat_values) - np.std(ctrl_values))), x_pos])
                                    coords.append([-1 * get_relative_hight((abs(np.average(ctrl_values)-np.average(treat_values)) - np.std(treat_values) - np.std(ctrl_values))), x_pos])
                                    last_xpos = x
                                    last_value = "ctrl_up"
                            elif last_value == "treat_up":
                                if len(coords) > 0:
                                    coords.insert(0, [get_relative_hight(0), coords[0][1]-quantile])
                                    coords.append([get_relative_hight(0), coords[-1][1] + quantile])
                                    write_to_file(draw_polygon(coords, 1, spark_color[0], stroke_width_spark))
                                coords = []
                                coords.append([-1 * get_relative_hight((abs(np.average(ctrl_values)-np.average(treat_values)) - np.std(treat_values) - np.std(ctrl_values))), x_pos])
                                coords.append([-1 * get_relative_hight((abs(np.average(ctrl_values)-np.average(treat_values)) - np.std(treat_values) - np.std(ctrl_values))), x_pos])
                                last_xpos = x
                                last_value = "ctrl_up"
                        elif np.average(ctrl_values) < np.average(treat_values):
                            if last_value == "" or last_value == "treat_up":
                                if (last_xpos + 1) == x:
                                    coords.append([get_relative_hight((abs(np.average(ctrl_values) - np.average(treat_values)) - np.std(treat_values) - np.std(ctrl_values))), x_pos])
                                    coords.append([get_relative_hight((abs(np.average(ctrl_values) - np.average(treat_values)) - np.std(treat_values) - np.std(ctrl_values))), x_pos])
                                    last_xpos = x
                                else:
                                    if len(coords) > 0:
                                        coords.insert(0, [get_relative_hight(0), coords[0][1] - quantile])
                                        coords.append([get_relative_hight(0), coords[-1][1] + quantile])
                                        write_to_file(draw_polygon(coords, 1, spark_color[0], stroke_width_spark))
                                    coords = []
                                    coords.append([get_relative_hight((abs(np.average(ctrl_values) - np.average(treat_values)) - np.std(treat_values) - np.std(ctrl_values))), x_pos])
                                    coords.append([get_relative_hight((abs(np.average(ctrl_values) - np.average(treat_values)) - np.std(treat_values) - np.std(ctrl_values))), x_pos])
                                last_xpos = x
                                last_value = "treat_up"
                            else:
                                if len(coords) > 0:
                                    coords.insert(0, [get_relative_hight(0), coords[0][1] - quantile])
                                    coords.append([get_relative_hight(0), coords[-1][1] + quantile])
                                    write_to_file(draw_polygon(coords, 1, spark_color[1], stroke_width_spark))
                                coords = []
                                coords.append([get_relative_hight((abs(np.average(ctrl_values) - np.average(treat_values)) - np.std(treat_values) - np.std(ctrl_values))), x_pos])
                                coords.append([get_relative_hight((abs(np.average(ctrl_values) - np.average(treat_values)) - np.std(treat_values) - np.std(ctrl_values))), x_pos])
                                last_xpos = x
                                last_value = "treat_up"
                if len(coords) > 0:
                    if last_value == "ctrl_up":
                        coords.insert(0, [get_relative_hight(0), coords[0][1] - quantile])
                        coords.append([get_relative_hight(0), coords[-1][1] + quantile])
                        write_to_file(draw_polygon(coords, 0.8, spark_color[0], stroke_width_spark))
                    elif last_value == "treat_up":
                        write_to_file(draw_polygon(coords, 0.8, spark_color[1], stroke_width_spark))
        else:
            print("Error: no input files for treatment and/or control")

# Draw axis and labels
##################################################
# Y scale bars
    write_to_file('''<line x1="''' + str(x_start - 10) + '''" y1="''' + str(y_start) + '''" x2="''' + str(x_start - 10) + '''" y2="''' + str(y_start - hight) + '''" stroke="black" stroke-width="1" />''')
    write_to_file('''<line x1="''' + str(x_start - 10.5) + '''" y1="''' + str(y_start) + '''" x2="''' + str(x_start - 6.5) + '''" y2="''' + str(y_start) + '''" stroke="black" stroke-width="1" />''')
    write_to_file('''<line x1="''' + str(x_start - 10.5) + '''" y1="''' + str(y_start - hight) + '''" x2="''' + str(x_start - 6.5) + '''" y2="''' + str(y_start - hight) + '''" stroke="black" stroke-width="1" />''')

# Y labels
    write_to_file('''<text text-anchor="end" font-family="Arial" x="''' + str(x_start - 14) + '''" y="''' + str(y_start + 4) + '''" font-size="8" >0</text>''')
    write_to_file('''<text text-anchor="end" font-family="Arial" x="''' + str(x_start - 14) + '''" y="''' + str(y_start - hight + 4) + '''" font-size="8" >''' + str(round(max_value*(1+(1-relative_track_hight_percentage)), 1)) + '''</text>''')

# Scalebar
if display_scalebar == "yes":
    delta_region = region[2] - region[1]
    fivepercent = int(delta_region * 0.05)
    scalebar_width = "1"
    for i in range(len(str(fivepercent))):
        scalebar_width += "0"
    scalebar_width = float(scalebar_width)
    scalebar_display = str(int(scalebar_width))
    scalebar_units = [" bp", " kb", " Mb", " Gb", " Tb", " Pb", " Eb", " Zb", " Yb"]
    counter = 0
    while len(scalebar_display) > 3:
        counter += 1
        scalebar_display = scalebar_display[:-3]

    normalized_scalebar_width = (scalebar_width * total_width) / float((region[2] - region[1]))

    if normalized_scalebar_width/2 > 15:
        normalized_scalebar_width /= 2
        scalebar_display = str(int(int(scalebar_display)*1000/2))
        counter -= 1
        if len(str(scalebar_display)) > 3:
            scalebar_display = scalebar_display[:-3]
            counter += 1
        scalebar_display += scalebar_units[counter]
    else:
        scalebar_display += scalebar_units[counter]

    write_to_file(draw_rect(total_width + x_start - normalized_scalebar_width, 100-hight+8, "000000", normalized_scalebar_width, 1, 1))
    write_to_file('''<text text-anchor="middle" font-family="Arial" x="''' + str(total_width + x_start - (normalized_scalebar_width/2)) + '''" y="''' + str(96-hight+8) + '''" font-size="7" >''' + scalebar_display + '''</text>''')

# Group labels
if group_labels is not None:
    for x, i in enumerate(range(nr_of_groups)):
        write_to_file('''<text text-anchor="start" font-family="Arial" x="''' + str(x_start + total_width + 15) + '''" y="''' + str(100 + x * hight * 1.5 - int((hight/2)) + 2.401) + '''" font-size="8" >''' + group_labels[x] + '''</text>''')



# Squares and labels for groups
if labels is not None:
    write_to_file(draw_rect(x_start - 10.5, 34, fills[0], 10, 10, opacity))
    write_to_file('''<text text-anchor="start" font-family="Arial" x="''' + str(x_start + 3) + '''" y="''' + str(34 - 1.788) + '''" font-size="8" >''' + str(labels[0]) + '''</text>''')
    write_to_file(draw_rect(x_start - 10.5, 47, fills[1], 10, 10, opacity))
    write_to_file('''<text text-anchor="start" font-family="Arial" x="''' + str(x_start + 3) + '''" y="''' + str(47 - 1.788) + '''" font-size="8" >''' + str(labels[1]) + '''</text>''')

    if show_plots == "averages":
        write_to_file(draw_rect(x_start - 10.5, 60, fills[0], 10, 10, opacity))
        write_to_file('''<text text-anchor="start" font-family="Arial" x="''' + str(x_start + 3) + '''" y="''' + str(60 - 1.788) + '''" font-size="8" >''' + "Overlap" + '''</text>''')
        write_to_file(draw_rect(x_start - 10.5, 60, fills[1], 10, 10, opacity))

    if spark == "yes":
        write_to_file(draw_rect(x_start + 59.5, 34, spark_color[1], 10, 10, 0.75))
        write_to_file('''<text text-anchor="start" font-family="Arial" x="''' + str(x_start + 73) + '''" y="''' + str(34 - 1.788) + '''" font-size="8" >''' + str(labels[0]) + ''' up</text>''')
        write_to_file(draw_rect(x_start + 59.5, 47, spark_color[0], 10, 10, 0.75))
        write_to_file('''<text text-anchor="start" font-family="Arial" x="''' + str(x_start + 73) + '''" y="''' + str(47 - 1.788) + '''" font-size="8" >''' + str(labels[1]) + ''' up</text>''')

# chromosome location
if args['display_chrom_location'] != "no":
    if args['display_chrom_location'] == "bottom_left":
        y_value_chr_label = y_start + 9
        x_value_chr_label = x_start - 10.5
        text_anchor = "start"
    elif args['display_chrom_location'] == "top_left":
        y_value_chr_label = 66
        x_value_chr_label = x_start - 10.5
        text_anchor = "start"
    elif args['display_chrom_location'] == "bottom_right":
        y_value_chr_label = y_start + 9
        x_value_chr_label = x_start + width
        text_anchor = "end"
    elif args['display_chrom_location'] == "top_right":
        y_value_chr_label = 66
        x_value_chr_label = x_start + width
        text_anchor = "end"
    write_to_file('''<text text-anchor="''' + text_anchor + '''''''" font-family="Arial" x="''' + str(x_value_chr_label) + '''" y="''' + str(y_value_chr_label) + '''" font-size="7" >Chr''' + str(region[0]) + ''': ''' + str(f"{region[1]:,}") + '''-''' + str(f"{region[2]:,}") + '''</text>''')

# add bed files
y_position_bed = 110 + (nr_of_groups - 1) * hight * 1.5 + additional_hight # dirty. y_position_bed is also start for gtf genes
if bed_files is not None:
    for nr_bed, bed_file in enumerate(bed_files):
        with open(bed_file) as b:
            for line in b:
                region_to_draw = [0, 0]
                line_split = line.split("\t")
                if line_split[0] != "":
                    if line_split[0][:3] == "chr" or line_split[0][:3] == "Chr":
                        line_split[0] = line_split[0][3:]
                    else:
                        pass
                if line_split[0] == region[0]:  # if same chromosome
                    line_split[1] = int(line_split[1])
                    line_split[2] = int(line_split[2])
                    if line_split[2] > region[1] and line_split[1] < region[2]:  # check if there is something to draw
                        region_to_draw = [line_split[1], line_split[2]]
                        if line_split[1] < region[1]:
                            region_to_draw[0] = region[1]
                        if line_split[2] > region[2]:
                            region_to_draw[1] = region[2]
                if region_to_draw != [0, 0]:
                    write_to_file(draw_rect(x_start + (((region_to_draw[0] - region[1]) * total_width) / float((region[2] - region[1]))), y_position_bed - 0.3 + (2 / 2), bed_color[nr_bed], ((region_to_draw[1] - region_to_draw[0]) * total_width) / float(region[2] - region[1]), 2, 1))
        write_to_file('''<text text-anchor="start" font-family="Arial" x="''' + str(x_start + total_width + 15) + '''" y="''' + str(y_position_bed + 3) + '''" font-size="8" >''' + bed_labels[nr_bed] + '''</text>''')
        y_position_bed += 8

# add gene plots from gtf file
if gff_file is not None:
    plot_transcripts = False

    with open(gff_file) as f:
        gene_or_transcript_names_to_plot = []
        transcripts = []
        tss_plotted_genes = []
        y_genestart = y_position_bed
        exons = []
        UTRs = []
        for line in f:
            line_split = line.split("\t")
            try:
                line_split[3] = int(line_split[3])
            except:
                pass
            try:
                line_split[4] = int(line_split[4])
            except:
                pass
            try:
                line_split[len(line_split) - 1] = line_split[len(line_split) - 1].split("\n")[0]
            except:
                pass
            try:
                if line_split[0][:3] == "chr" or line_split[0][:3] == "Chr":
                    line_split[0] = line_split[0][3:]
            except:
                pass
            if line_split[0] == region[0]:  # check if same chr
                to_draw = get_region_to_draw()
                if to_draw != 0:

                    # the following gets either the gene name, or the transcript name, plot_transcripts indicates what
                    if line_split[2] in ["gene", "CDS", "exon", "transcript", "start_codon"]:
                        gene_or_transcript_name = ""
                        if display_transcripts[0] == "mergeall":
                            if display_genes is None:
                                gene_or_transcript_name = get_gene_name() # Get gene name if all merged genes are to be plotted
                            else:
                                if get_gene_name() in display_genes:
                                    gene_or_transcript_name = get_gene_name() # Get gene name only certain merged genes are to be plotted
                        else: # if individual transcripts should be plotted
                            if "transcript_id " in line_split[8]:
                                if display_transcripts[0] == "all":
                                    gene_or_transcript_name = get_transcript_name() # Get transcript ID if all individual transcripts instead of genes are to be plotted
                                    plot_transcripts = True # mark that instead of only genes, transcripts will be plotted
                                else:
                                    if get_transcript_name() in display_transcripts:
                                        gene_or_transcript_name = get_transcript_name()
                                        plot_transcripts = True  # mark that instead of only genes, transcripts will be plotted

                        plot_gene = False
                        if gene_or_transcript_name != "":  # only if transcript name is not empty it will be plotted
                            if gene_or_transcript_name not in gene_or_transcript_names_to_plot: # checks which genes have been plotted
                                if display_transcripts[0] != "mergeall":
                                    if display_transcripts[0] == "all":
                                        y_genestart += 12
                                        gene_or_transcript_names_to_plot.append(gene_or_transcript_name)
                                    else:
                                        if gene_or_transcript_name in display_transcripts:
                                            y_genestart += 12
                                            gene_or_transcript_names_to_plot.append(gene_or_transcript_name)
                                else:
                                    y_genestart += 12
                                    gene_or_transcript_names_to_plot.append(gene_or_transcript_name)


                            if display_transcripts[0] != "mergeall": # if transcripts to plot were defined
                                if gene_or_transcript_name in display_transcripts: # check if this one should be plotted
                                    plot_gene = True
                                elif display_transcripts[0] == "all":
                                    plot_gene = True

                            elif display_genes is not None:
                                if gene_or_transcript_name in display_genes:
                                    plot_gene = True
                            else:
                                plot_gene = True

                        if plot_gene == True:
                            draw_gene_or_transcript = False
                            if plot_transcripts == True:
                                if line_split[2] == "transcript":
                                    draw_gene_or_transcript = True #plot only transcripts
                            elif line_split[2] == "gene":
                                draw_gene_or_transcript = True # plot only genes if transcripts are not defined

                            if draw_gene_or_transcript == True:
                                if plot_gene_name_instead_transcriptID == "yes":
                                    gene_label = line_split[8].split("gene_name ")[1].split('''"''')[1]
                                else:
                                    gene_label = gene_or_transcript_name
                                write_to_file('''<text text-anchor="start" font-family="Arial" x="''' + str(x_start + total_width + 15) + '''" y="''' + str(y_genestart + 3) + '''" font-size="8" >''' + gene_label + '''</text>''')
                                drawhight = 1.0
                            elif line_split[2] == "CDS":
                                drawhight = 6.0
                            elif line_split[2] == "exon":
                                drawhight = 3.0

                            if draw_gene_or_transcript == True or line_split[2] in ["CDS", "exon"]:
                                write_to_file(draw_rect(x_start + (((to_draw[0] - region[1]) * total_width) / float((region[2] - region[1]))), y_genestart - 0.3 + (drawhight / 2), "#0B34FF", ((to_draw[1] - to_draw[0]) * total_width) / float(region[2] - region[1]), drawhight, 1))

                            if line_split[2] == "start_codon":
                                if draw_TSS == "yes":
                                    plot = True
                                    if plot_transcripts == False:  # makes sure there is only one TSS plotted if merged gene is selected
                                        plot = False
                                        plotted_TSS = True
                                        if gene_or_transcript_name not in tss_plotted_genes:
                                            plotted_TSS = False
                                            tss_plotted_genes.append(gene_or_transcript_name)
                                        plot = False
                                        if plotted_TSS == False or plot_all_TSS == True:
                                            plot = True
                                        if display_genes is not None and gene_or_transcript_name not in display_genes:
                                            plot = False
                                    if plot == True:
                                        hight = 5
                                        width = 6.156
                                        thickness = 0.7
                                        x_0 = x_start + (((to_draw[0] - region[1]) * total_width) / float((region[2] - region[1])))
                                        y_0 = 4
                                        y_start = y_genestart # Dirty... quick fix as the polygon function uses y_start...
                                        if line_split[6] == "+":
                                            arrow_coords = [[y_0, x_0], [y_0 + (hight * 0.8), x_0], [y_0 + (hight * 0.8), x_0 + (width * 0.8)], [y_0 + hight, x_0 + (width * 0.8)], [(y_0 + (hight * 0.8)) - (float(thickness) / 2), x_0 + width], [y_0 + (hight * 0.8) - thickness - hight * 0.2, x_0 + (width * 0.8)], [y_0 + (hight * 0.8) - thickness, x_0 + (width * 0.8)], [y_0 + (hight * 0.8) - thickness, x_0 + thickness], [y_0, x_0 + thickness]]
                                        elif line_split[6] == "-":
                                            arrow_coords = [[y_0, x_0], [y_0 + (hight * 0.8), x_0], [y_0 + (hight * 0.8), x_0 - (width * 0.8)], [y_0 + hight, x_0 - (width * 0.8)], [(y_0 + (hight * 0.8)) - (float(thickness) / 2), x_0 - width], [y_0 + (hight * 0.8) - thickness - hight * 0.2, x_0 - (width * 0.8)], [y_0 + (hight * 0.8) - thickness, x_0 - (width * 0.8)], [y_0 + (hight * 0.8) - thickness, x_0 - thickness], [y_0, x_0 - thickness]]
                                        write_to_file(draw_polygon(arrow_coords,1,"#000000",0))
                                        plotted_TSS = True

write_to_file("</svg>")
