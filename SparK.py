SparK_Version = "1.3"
# Stefan Kurtenbach
# Stefan.Kurtenbach@med.miami.edu

# FIX what happens if region is smaller than 2000?

import numpy as np
import copy
import os
import argparse
import math
import sys

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
        #raw_data_filled_smooth = [[0] * (stretch[2] - stretch[1]) for r in range(len(files))]
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
    max_v = 0
    for datafile1 in datasets1:
        if max(datafile1) > max_v:
            max_v = max(datafile1)
    for datafile2 in datasets2:
        if max(datafile2) > max_v:
            max_v = max(datafile2)
    return max_v
def get_relative_hight(raw_value): # FIX make sure maxvalue can be 0 too
    if raw_value == 0:
        return(0)
    else:
        return((raw_value * hight * 0.85) / max_value) # to not go up to the max
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
parser.add_argument('-pt','--plot_type', help='choices: standard, STD, sine', required=True, type=str)
parser.add_argument('-ps','--show_plots', help='choices: all, averages', required=True, type=str)
parser.add_argument('-pr','--region', help='example: chr1:1647389-272634', required=True, type=str)
parser.add_argument('-cf','--control_files', help='separate by space', required=True, nargs='+', type=str)
parser.add_argument('-tf','--treat_files', help='separate by space', required=True, nargs='+', type=str)
parser.add_argument('-cg','--control_groups', help='group numbers separate by spacse', required=False, nargs='+', type=int)
parser.add_argument('-tg','--treat_groups', help='group numbers separate by space', required=False, nargs='+', type=int)
parser.add_argument('-gl','--group_labels', help='set group labels', required=False, nargs='+', type=str)
parser.add_argument('-l','--labels', help='set labels for controls and treatment', required=False, nargs='+', type=str)
parser.add_argument('-gs','--group_autoscale', help='set to "yes" if wanted', required=False, type=str)
parser.add_argument('-es','--exclude_from_group_autoscale', help='group numbers of groups to be excluded from autoscale', required=False, nargs='+', type=int)
parser.add_argument('-eg','--exclude_groups', help='Exclude groups from the analysis', required=False, nargs='+', type=int)
parser.add_argument('-f','--fills', help='enter two colors in hex format', required=False, nargs='+', type=str)
parser.add_argument('-gff', '--gfffile', help='link gff file for drawing genes here', required=False, type=str)
parser.add_argument('-sp', '--spark', help='display significant change "yes"', required=False, type=str)
parser.add_argument('-sc', '--spark_color', help='spark color', required=False, type=str, nargs='+')
parser.add_argument('-sm', '--smoothen', help='smoothen tracks, int', required=False, type=int)
parser.add_argument('-o','--output_name', help='output graph name, str', required=False, type=str)
parser.add_argument('-bed','--bed_files', help='bed files to be plotted', required=False, type=str, nargs='+')
parser.add_argument('-w','--track_width', help='width of the track, default = 150, int', required=False, type=int)
parser.add_argument('-dg','--display_genes', help='genes to display from the gff file', nargs='+', required=False, type=str)
args = vars(parser.parse_args())

print(" ")
print('''SparK Version ''' + SparK_Version + ''' initiated''')

# Additional Arguments #########################################
hight = 30
x_start = 50
spark_opacity = 1
stroke_width = 0  # 0.1 stroke widths good
stroke_width_spark = 0
################################################################

# import arguments #############################################
bed_files = args["bed_files"]

smoothen_tracks = args['smoothen']

output_filename = args['output_name']
if output_filename is None:
    output_filename = "graph.svg"
else:
    output_filename += ".svg"

display_genes = args['display_genes']

width = args['track_width']
if width is not None:
    total_width = int(width)
else:
    total_width = 150


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
    else:
        pass

spark = args['spark']
if spark == "yes":
    print("Sparks will be drawn")
    spark_color = args['spark_color']
    if spark_color is not None:
        if spark_color != 2:
            print('''Error: Spark color definition not correct. Enter two hex colors e.g. "-sc #00FF12 #848484"''')
            sys.exit()
    else:
        spark_color = ["#FF9D00", "#00FF00"]  # green/orange
        stroke_width_spark = 0.05
        spark_opacity = 0.5

all_control_files = args['control_files']
if all_control_files is None:
    print("Error: No control files set")
    sys.exit()
all_treat_files = args['treat_files']
if all_treat_files is None:
    print("Error: No treat files set")
    sys.exit()

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
if control_groups is None and treat_groups is None:
    nr_of_groups = len(all_treat_files + all_control_files)
    number = 1
    control_groups = []
    treat_groups = []
    for i in range(len(all_control_files)):
        control_groups.append(number)
        number += 1
    for i in range(len(all_treat_files)):
        treat_groups.append(number)
        number += 1
else:
    nr_of_groups = max([max(control_groups), max(treat_groups)])

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

fills = args['fills']  # left is treat, right is control

if fills is None:
    fills = ["blue/red", "N/A"]

if fills[0] == "blue/red":
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

elif len(fills) < 2:
    print("Error: Track fill color entered wrong.")
    sys.exit()

elif len(fills) > 1:
    for i in range(len(fills)):
        fills[i] = "#" + fills[i]
        opacity = 0.6


gff_file = args['gfffile']

if os.path.exists(output_filename):
    os.remove(output_filename)
#############################################################################################################

write_to_file('''<svg viewBox="0 0 300 ''' + str(100 + (hight * 2 * nr_of_groups)) + '''" xmlns="http://www.w3.org/2000/svg">''')

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

    autoscale_max = max([max(ctrl_averages), max(treat_averages)])
#############################################################################################################

if (region[2] - region[1]) <= 2000:
    quantile = float(total_width)/(region[2] - region[1])
else:
    quantile = float(total_width)/2000

for group in range(nr_of_groups):
    y_start = 100 + group * hight * 1.5
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
    if group_autoscale == "yes":
        if (group + 1) not in group_autoscale_excluded:
            max_value = autoscale_max # global_max_value is derived only from the groups that were not excluded
        else:
            max_value = get_max_value(control_data, treat_data)
    else:
        max_value = get_max_value(control_data, treat_data)

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
        coords = []
        for x in range(len((control_data[0]))):
            x_pos = x_start + (x * quantile)  # y/x
            values = []
            for p, i in enumerate(control_data):
                values.append(control_data[p][x])
            coords.append([get_relative_hight(np.average(values) + np.std(values)), x_pos])
            coords.insert(0, [get_relative_hight(np.average(values) - np.std(values)), x_pos])
        write_to_file(draw_polygon(coords, 0.4, fills[0], stroke_width))
        coords = []
        for x in range(len((treat_data[0]))):
            x_pos = x_start + (x * quantile)  # y/x
            values = []
            for p, i in enumerate(treat_data):
                values.append(treat_data[p][x])
            coords.append([get_relative_hight(np.average(values) + np.std(values)), x_pos])
            coords.insert(0, [get_relative_hight(np.average(values) - np.std(values)), x_pos])
        write_to_file(draw_polygon(coords, 0.4, fills[1], stroke_width))

        if spark == "yes":
            draw_standard_spark()

    elif plot_type == "sine": # treat points up, control points down #FIX combined with averages does not work
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

# Draw axis and labels
##################################################
# Y scale bars
    write_to_file('''<line x1="''' + str(x_start - 10) + '''" y1="''' + str(y_start) + '''" x2="''' + str(x_start - 10) + '''" y2="''' + str(y_start - hight) + '''" stroke="black" stroke-width="1" />''')
    write_to_file('''<line x1="''' + str(x_start - 10.5) + '''" y1="''' + str(y_start) + '''" x2="''' + str(x_start - 5) + '''" y2="''' + str(y_start) + '''" stroke="black" stroke-width="1" />''')
    write_to_file('''<line x1="''' + str(x_start - 10.5) + '''" y1="''' + str(y_start - hight) + '''" x2="''' + str(x_start - 5) + '''" y2="''' + str(y_start - hight) + '''" stroke="black" stroke-width="1" />''')

# Y labels
    write_to_file('''<text text-anchor="end" x="''' + str(x_start - 14) + '''" y="''' + str(y_start + 4) + '''" font-size="9" >0</text>''')
    write_to_file('''<text text-anchor="end" x="''' + str(x_start - 14) + '''" y="''' + str(y_start - hight + 4) + '''" font-size="9" >''' + str(round(max_value, 1)) + '''</text>''')

# Group labels
if group_labels is not None:
    for x, i in enumerate(range(nr_of_groups)):
        write_to_file('''<text text-anchor="start" x="''' + str(x_start + total_width + 15) + '''" y="''' + str(100 + x * hight * 1.5 - int((hight/2)) - 1.788) + '''" font-size="9" >''' + group_labels[x] + '''</text>''')

# Squares and labels
if labels is not None:
    write_to_file(draw_rect(x_start - 10.5, 34, fills[0], 10, 10, opacity))
    write_to_file('''<text text-anchor="start" x="''' + str(x_start + 3) + '''" y="''' + str(34 - 1.788) + '''" font-size="9" >''' + str(labels[0]) + '''</text>''')
    write_to_file(draw_rect(x_start - 10.5, 47, fills[1], 10, 10, opacity))
    write_to_file('''<text text-anchor="start" x="''' + str(x_start + 3) + '''" y="''' + str(47 - 1.788) + '''" font-size="9" >''' + str(labels[1]) + '''</text>''')
    write_to_file(draw_rect(x_start - 10.5, 60, fills[0], 10, 10, opacity))
    write_to_file(draw_rect(x_start - 10.5, 60, fills[1], 10, 10, opacity))
    write_to_file('''<text text-anchor="start" x="''' + str(x_start + 3) + '''" y="''' + str(60 - 1.788) + '''" font-size="9" >''' + "Overlap" + '''</text>''')

    if spark == "yes":
        write_to_file(draw_rect(x_start + 51.5, 34, spark_color[1], 10, 10, 0.5))
        write_to_file('''<text text-anchor="start" x="''' + str(x_start + 65) + '''" y="''' + str(34 - 1.788) + '''" font-size="9" >''' + str(labels[0]) + ''' up</text>''')
        write_to_file(draw_rect(x_start + 51.5, 47, spark_color[0], 10, 10, 0.5))
        write_to_file('''<text text-anchor="start" x="''' + str(x_start + 65) + '''" y="''' + str(47 - 1.788) + '''" font-size="9" >''' + str(labels[1]) + ''' up</text>''')

# add bed files
y_position_bed = 110 + (nr_of_groups - 1) * hight * 1.5
if bed_files is not None:
    for bed_file in bed_files:
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
                    write_to_file(draw_rect(x_start + (((region_to_draw[0] - region[1]) * total_width) / float((region[2] - region[1]))), y_position_bed - 0.3 + (2 / 2), "#0B34FF", ((region_to_draw[1] - region_to_draw[0]) * 150) / float(region[2] - region[1]), 2, 1))
        write_to_file('''<text text-anchor="start" x="''' + str(x_start + total_width + 15) + '''" y="''' + str(y_position_bed + 3) + '''" font-size="9" >''' + bed_file + '''</text>''')
        y_position_bed += 8

# add gene plots
if gff_file is not None:
    with open(gff_file) as f:
        gene_names = []
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

            try:
                if line_split[0] == region[0]:  # check if same chr
                    to_draw = get_region_to_draw()
                    if to_draw != 0:
                        if line_split[2] == "gene":
                            gene = line_split[8].split("gene_name ")[1].split('''"''')[1]
                            if display_genes is not None:
                                if gene in display_genes:
                                    if gene not in gene_names:
                                        y_genestart += 10
                                    gene_names.append(gene)
                                    write_to_file('''<text text-anchor="start" x="''' + str(x_start + total_width + 15) + '''" y="''' + str(y_genestart + 3) + '''" font-size="9" >''' + gene + '''</text>''')
                                    drawhight = 1.0
                                    write_to_file(draw_rect(x_start + (((to_draw[0] - region[1]) * total_width) / float((region[2] - region[1]))), y_genestart - 0.3 + (drawhight / 2), "#0B34FF", ((to_draw[1] - to_draw[0]) * 150) / float(region[2] - region[1]), drawhight, 1))
                            else:
                                y_genestart += 10
                                write_to_file('''<text text-anchor="start" x="''' + str(x_start + total_width + 15) + '''" y="''' + str(y_genestart + 3) + '''" font-size="9" >''' + gene + '''</text>''')
                                drawhight = 1.0
                                write_to_file(draw_rect(x_start + (((to_draw[0] - region[1]) * total_width) / float((region[2] - region[1]))), y_genestart - 0.3 + (drawhight / 2), "#0B34FF", ((to_draw[1] - to_draw[0]) * 150) / float(region[2] - region[1]), drawhight, 1))

                        if line_split[2] == "CDS":
                            if line_split[8].split("gene_name ")[1].split('''"''')[1] == gene:
                                if display_genes is not None:
                                    if gene in display_genes:
                                        drawhight = 6.0
                                        write_to_file(draw_rect(x_start + (((to_draw[0] - region[1]) * total_width) / float((region[2] - region[1]))), y_genestart - 0.3 + (drawhight / 2), "#0B34FF", ((to_draw[1] - to_draw[0]) * 150) / float(region[2] - region[1]), drawhight, 1))
                                else:
                                    drawhight = 6.0
                                    write_to_file(draw_rect(x_start + (((to_draw[0] - region[1]) * total_width) / float((region[2] - region[1]))), y_genestart - 0.3 + (drawhight / 2), "#0B34FF", ((to_draw[1] - to_draw[0]) * 150) / float(region[2] - region[1]), drawhight, 1))

                        if line_split[2] == "exon":
                            if line_split[8].split("gene_name ")[1].split('''"''')[1] == gene:
                                if display_genes is not None:
                                    if gene in display_genes:
                                        drawhight = 3.0
                                        write_to_file(draw_rect(x_start + (((to_draw[0] - region[1]) * total_width) / float((region[2] - region[1]))), y_genestart - 0.3 + (drawhight / 2), "#0B34FF", ((to_draw[1] - to_draw[0]) * 150) / float(region[2] - region[1]), drawhight, 1))
                                else:
                                    drawhight = 3.0
                                    write_to_file(draw_rect(x_start + (((to_draw[0] - region[1]) * total_width) / float((region[2] - region[1]))), y_genestart - 0.3 + (drawhight / 2), "#0B34FF", ((to_draw[1] - to_draw[0]) * 150) / float(region[2] - region[1]), drawhight, 1))
            except:
                print("excluding row:" + str(line_split))

write_to_file("</svg>")
