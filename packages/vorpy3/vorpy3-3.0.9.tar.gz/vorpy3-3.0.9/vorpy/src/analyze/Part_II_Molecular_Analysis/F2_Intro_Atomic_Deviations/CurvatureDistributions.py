import os

import matplotlib.pyplot as plt
import numpy as np
import tkinter as tk
from tkinter import filedialog

import os
import sys

# Get the path to the root vorpy folder
vorpy_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..'))
# Add the root vorpy folder to the system path
sys.path.append(vorpy_root)


from vorpy.src.system.system import System
from vorpy.src.group.group import Group
from vorpy.src.analyze.tools.compare.read_logs import read_logs
from vorpy.src.analyze.tools.plot_templates.box_whisker import box_whisker
from vorpy.src.analyze.tools.plot_templates.line import line_plot


if __name__ == '__main__':
    # Get the dropbox folder
    root = tk.Tk()
    root.withdraw()
    root.wm_attributes('-topmost', 1)
    folder = filedialog.askdirectory()
    # Create the systems
    systems = []
    for root, dir, files in os.walk(folder):
        for file in files:
            if file[-3:] == 'pdb':
                my_sys = System(file=folder + '/' + file)
                my_sys.groups = [Group(sys=my_sys, residues=my_sys.residues)]
                systems.append(my_sys)
    # Sort atoms by number of atoms
    num_atoms = [len(_.atoms) for _ in systems]
    systems = [x for _, x in sorted(zip(num_atoms, systems))]
    # print([_.name for _ in systems])

    # Create the logs dictionary
    my_sys_names = [__.name for __ in systems]
    my_logs = {_: {'vor': None, 'pow': None, 'del': None} for _ in my_sys_names}
    for root, dir, files in os.walk(folder):
        for file in files:
            if file[-3:] == 'csv':
                my_logs[file[:-13]][file[-12:-9]] = folder + '/' + file
    vals = []
    for sys_name in my_sys_names:
        logs = read_logs(my_logs[sys_name]['vor'], return_dict=True)
        vals.append([_['curvature'] for _ in logs['surfs']])
    # Create the labels manually for the systems in question
    graph_labels = [{'EDTA_Mg': 'EDTA', 'cambrin': 'Cambrin', 'hairpin': 'Hairpin', 'p53tet': 'p53tet',
                     'streptavidin': 'STVDN', 'hammerhead': 'H-head', 'NCP': 'NCP', 'pl_complex': 'T4LP Complex',
                     'BSA': 'BSA', '1BNA': '1BNA'}[_] for _ in my_sys_names]

    # Bin the values
    increments = np.linspace(0, max([max(_) for _ in vals]), 300)

    # Set up the x values
    # Set the label codes
    code_dict = {'Na5': 'A', 'EDTA': 'B', 'Hairpin': 'C', 'Cambrin': 'D', 'H-head': 'E', 'p53tet': 'F',
                 'T4LP Complex': 'G', 'STVDN': 'H', 'NCP': 'I', 'BSA': 'J', '1BNA': '1BNA'}
    new_graph_labels = [code_dict[_] for _ in graph_labels]
    colors = {'Na5': 'k', 'EDTA': 'b', 'Hairpin': 'darkgreen', 'Cambrin': 'green', 'H-head': 'darkblue', 'p53tet': 'purple',
              'T4LP Complex': 'b', 'STVDN': 'green', 'NCP': 'grey', 'BSA': 'red', '1BNA': '1BNA'}
    my_colors = [colors[_] for _ in graph_labels]
    scaled_bins, reg_bins = [], []
    for _ in vals:

        # Scale the number of values by the size of the group
        bins = [[__ for __ in _ if increments[j] <= __ < increments[j + 1]] for j in range(len(increments[:-1]))]
        # Count the number based on the number of total values
        scaled_bins.append([len(__) / len(_) for __ in bins])
        reg_bins.append([len(_) for _ in bins])

    def sort_3_lists(lista, listb, listc, listd):
        # Zipping lists together and sorting by the first list
        sorted_lists = sorted(zip(lista, listb, listc, listd), key=lambda x: x[0])

        # Unpacking the sorted lists
        lista, listb, listc, listd = zip(*sorted_lists)

        # Converting tuples back to lists if needed
        lista = list(lista)
        listb = list(listb)
        listc = list(listc)
        listd = list(listd)

        # Return the lists
        return lista, listb, listc, listd
    y_scales = [max(_[10:]) for _ in reg_bins]
    # Unpacking the sorted lists
    labels, values, colors, reg_labels = sort_3_lists(new_graph_labels, scaled_bins, my_colors, graph_labels)
    line_plot([[(increments[j] + increments[j + 1]) / 2 for j in range(len(increments[:-1]))][10:] for _ in range(len(scaled_bins))],
              [_[10:] for _ in values], title='Surface Curvature Distributions By Model',
              x_label='Curvature', y_label='Distribution', legend_title='Model', labels=reg_labels,
              title_size=35, x_label_size=30, y_label_size=30, colors=colors, tick_val_size=30,
              legend_orientation='horizontal')
    # line_plot([[(increments[j] + increments[j + 1]) / 2 for j in range(len(increments[:-1]))][10:] for _ in range(len(scaled_bins))],
    #           [_[10:] for _ in values], title='Surface Curvature Distributions By Model',
    #           x_label='Curvature', y_label='Distribution', legend_title='Model', labels=reg_labels,
    #           title_size=35, x_label_size=30, y_label_size=30, colors=colors, tick_val_size=30,
    #           legend_orientation='horizontal', y_ticks=[int(_) for _ in np.arange(0, y_scales[0], y_scales[0] / 4)],
    #           y_ticks2=[int(_) for _ in np.arange(0, y_scales[1], y_scales[1] / 4)])
    plt.show()

