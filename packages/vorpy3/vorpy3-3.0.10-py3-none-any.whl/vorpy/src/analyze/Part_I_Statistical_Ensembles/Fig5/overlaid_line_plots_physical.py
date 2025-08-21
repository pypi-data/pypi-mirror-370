import csv
import os
import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter.filedialog import askopenfilename
from matplotlib.cm import ScalarMappable
from matplotlib.colors import Normalize

root = tk.Tk()
root.withdraw()
root.wm_attributes('-topmost', 1)
my_foams_file = askopenfilename()


with open(my_foams_file, 'r') as my_foam_data:

    my_data = []
    # x, y, z1, z2 = [], [], [], []
    foam_data = csv.reader(my_foam_data)
    for k, my_line in enumerate(foam_data):
        if len(my_line) <= 1:
            continue
        file = my_line[0]
        name = file.split('/')[-1]
        if 'lemlich' in name:
            phys_type = 'lemlich'
        elif 'gal_or' in name:
            phys_type = 'gal_or'
        elif 'devries' in name:
            phys_type = 'devries'
        else:
            continue
        try:
            if len(my_line) <= 1:
                continue
            my_data.append({'num': my_line[0], 'avg rad size': float(my_line[2]), 'box size': float(my_line[1]),
                            'rad std': float(my_line[3]), 'num balls': int(my_line[4]), 'type': phys_type,
                            'density': float(my_line[5]), 'vol diff vor': float(my_line[6]),
                            'sa diff vor': float(my_line[7]), 'vol diff pow': float(my_line[8]), 'sa diff pow': float(my_line[9])})

        except ValueError:
            if len(my_line) <= 1:
                continue
            my_data.append({'num': my_line[0], 'avg rad size': float(my_line[5][:-1]), 'box size': float(my_line[1][:-1]),
                            'rad std': float(my_line[8][:-1]), 'num balls': int(my_line[14][:-1]), 'type': phys_type,
                            'density': float(my_line[17][:-1]), 'vol diff vor': float(my_line[36]),
                            'sa diff vor': float(my_line[37]), 'vol diff pow': float(my_line[38]),
                            'sa diff pow': float(my_line[39])})
        except ValueError:
            continue

plot_type = 'Physics-Based Models'
cell_type = 'Closed'

lists = {}

for dp in my_data:
    # Check if the data has been added before
    if dp['type'] in lists:
        if dp['density'] in lists[dp['type']]:
            lists[dp['type']][dp['density']][0].append(dp['vol diff vor'])
            lists[dp['type']][dp['density']][1].append(dp['sa diff vor'])
            lists[dp['type']][dp['density']][2].append(dp['vol diff pow'])
            lists[dp['type']][dp['density']][3].append(dp['sa diff pow'])
        else:
            lists[dp['type']][dp['density']] = [[dp['vol diff vor']], [dp['sa diff vor']], [dp['vol diff pow']],
                                                   [dp['sa diff pow']]]
    else:
        lists[dp['type']] = {
            dp['density']: [[dp['vol diff vor']], [dp['sa diff vor']], [dp['vol diff pow']], [dp['sa diff pow']]]}

# for _ in lists:
#     print(_, [__ for __ in lists[_]])

my_densities = [round(_, 3) for _ in np.linspace(0.05, 0.5, 19)]
my_sds = ['devries', 'lemlich', 'gal_or']
colors = ['purple', 'orange', 'green']
# Initialize lists using list comprehensions
datavvm, datavsm, datapvm, datapsm = [[] for _ in my_sds], [[] for _ in my_sds], [[] for _ in my_sds], [[] for _ in my_sds]
datavvms, datavsms, datapvms, datapsms = [[] for _ in my_sds], [[] for _ in my_sds], [[] for _ in my_sds], [[] for _ in my_sds]
datavvps, datavsps, datapvps, datapsps = [[] for _ in my_sds], [[] for _ in my_sds], [[] for _ in my_sds], [[] for _ in my_sds]


# Iterate over my_sds and my_densities using nested loops
for i, num in enumerate(my_sds):
    for j, num2 in enumerate(my_densities):
        # if num2 == 0.05:
        #     continue
        means = []
        sds = []
        # Get the current Data
        try:
            curr_data = lists[num][num2]
        except KeyError:
            curr_data = np.nan
            print(num, num2)
            datavvm[i].append(np.nan);
            datavvms[i].append(np.nan);
            datavvps[i].append(np.nan)
            datavsm[i].append(np.nan);
            datavsms[i].append(np.nan);
            datavsps[i].append(np.nan)
            datapvm[i].append(np.nan);
            datapvms[i].append(np.nan);
            datapvps[i].append(np.nan)
            datapsm[i].append(np.nan);
            datapsms[i].append(np.nan);
            datapsps[i].append(np.nan)
            continue

        for data1 in curr_data:
            # Calculate the Z-scores
            z_scores = np.abs((data1 - np.mean(data1)) / np.std(data1))

            # Set a Z-score threshold (e.g., 3)
            z_score_threshold = 1

            # Exclude outliers based on the Z-score
            filtered_data = np.array(data1)[z_scores < z_score_threshold]
            means.append(100*np.mean(filtered_data))
            sds.append(np.std([_ * 100 for _ in filtered_data]))

        # Append means and mean +/- SD to respective lists
        datavvm[i].append(means[0]); datavvms[i].append(means[0] - sds[0]); datavvps[i].append(means[0] + sds[0])
        datavsm[i].append(means[1]); datavsms[i].append(means[1] - sds[1]); datavsps[i].append(means[1] + sds[1])
        datapvm[i].append(means[2]); datapvms[i].append(means[2] - sds[2]); datapvps[i].append(means[2] + sds[2])
        datapsm[i].append(means[3]); datapsms[i].append(means[3] - sds[3]); datapsps[i].append(means[3] + sds[3])


label_dict = {'devries': 'A. J. Devries', 'gal_or': 'B. Gal-Or & H Hoelscher', 'lemlich': 'R. Lemlich'}

for value in ['vol', 'sa']:
    # Coefficient of Variation (CV) and Density values
    # cmap = plt.cm.rainbow  # Choose a colormap that does not have yellow and works well in grayscale
    # norm = Normalize(vmin=min(my_sds), vmax=max(my_sds))
    # sm = ScalarMappable(norm=norm, cmap=cmap)
    fig, ax = plt.subplots(figsize=(6, 6))

    for i, sd in enumerate(my_sds):
        # Colors for each line based on 'sd' which is used as an index into the colormap
        # color = cmap(norm(sd))
        if value == 'vol':
            ax.plot(my_densities[1:], datavvm[i][1:], label=label_dict[sd], color=colors[i])
            ax.fill_between(my_densities[1:], datavvms[i][1:], datavvps[i][1:], alpha=0.2, color=colors[i])
        elif value == 'sa':
            ax.plot(my_densities[1:], datavsm[i][1:], label=label_dict[sd], c=colors[i])
            ax.fill_between(my_densities[1:], datavsms[i][1:], datavsps[i][1:], alpha=0.2, color=colors[i])


    # plt.legend(fontsize=25)

    # Adding a color bar that uses the created ScalarMappable
    # sm.set_array([])
    # cbar = plt.colorbar(sm, ax=ax)
    # cbar.set_label('Coefficient of Variation (CV)', fontdict=dict(size=25))


    # Set plot titles and labels
    ax.set_xticks(np.arange(my_densities[0] + 0.05, my_densities[-1] + 0.05, 0.1))
    ax.set_ylim([0, 100])
    ax.set_title('{} {}\nAbsolute % Difference'.format(plot_type, {'sa': 'Surface Area', 'vol': 'Volume'}[value]), fontsize=20)
    ax.set_xlabel('Density', fontsize=25)
    ax.set_ylabel('Absolute Difference', fontsize=25)
    ax.tick_params(axis='both', which='major', labelsize=20, width=2, length=12)

    # cbar.ax.tick_params(labelsize=20, size=10, width=2, length=12)
    plt.tight_layout()

    # Show the plot
    plt.show()

# Create a single plot
# fig, ax = plt.subplots(figsize=(8, 6))
# for i in range(len(datavvm)):
#     ax.plot(my_densities[2:], datavvm[i][2:], label=str(my_sds[i]))
#     ax.fill_between(my_densities[2:], datavvms[i][2:], datavvps[i][2:], alpha=0.2)
#
#
# # Set plot title and legend
# ax.set_xticks(np.arange(my_densities[1], my_densities[-1] + 0.05, 0.05))
# ax.set_title('Power Volume Deviation (Closed)', fontsize=30)
# ax.set_xlabel('Density', fontsize=20)
# ax.set_ylabel('% Difference', fontsize=20)
# ax.tick_params(axis='both', which='major', labelsize=15)
# legend = ax.legend(loc='upper right', bbox_to_anchor=(1.25, 1))
# legend.set_title('CV')
#
# # Adjust the right margin to make room for the legend
# plt.subplots_adjust(right=0.8)
#
# # Show the plot
# plt.show()
