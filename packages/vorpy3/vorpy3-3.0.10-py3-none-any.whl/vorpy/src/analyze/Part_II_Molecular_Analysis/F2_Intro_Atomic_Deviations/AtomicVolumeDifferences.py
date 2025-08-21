import os
import sys
import tkinter as tk
from tkinter import filedialog

# Get the path to the root vorpy folder
vorpy_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..'))
# Add the root vorpy folder to the system path
sys.path.append(vorpy_root)

from vorpy.src.system.system import System
from vorpy.src.group.group import Group
from vorpy.src.analyze.tools.compare.read_logs2 import read_logs2
from vorpy.src.analyze.tools.plot_templates.scatter import scatter

from vorpy.src.analyze.tools.batch.get_files import get_all_files



def plot_vols():
    """Plots the average percentage differences for the given systems"""
    folder = tk.Tk()
    folder.withdraw()
    folder = filedialog.askdirectory()
    # get the aw, pow, and prm logs
    aw_logs = read_logs2(os.path.join(folder, 'aw_logs.csv'), all_=False, balls=True)
    pow_logs = read_logs2(os.path.join(folder, 'pow_logs.csv'), all_=False, balls=True)
    prm_logs = read_logs2(os.path.join(folder, 'prm_logs.csv'), all_=False, balls=True)
    # Get the title
    title = folder.split('/')[-1]
    # Create the lists
    aw_vols, pow_vols, prm_vols = [], [], []
    # Loop through the atoms and get the volume differences
    for i, atom in aw_logs['atoms'].iterrows():
        # Get the power atom
        pow_atom = pow_logs['atoms'].loc[pow_logs['atoms']['Index'] == atom['Index']]
        # Get the primitive atom
        prm_atom = prm_logs['atoms'].loc[prm_logs['atoms']['Index'] == atom['Index']]
        # Add the volumes to the lists
        aw_vols.append(atom['Volume'])
        pow_vols.append(pow_atom['Volume'])
        prm_vols.append(prm_atom['Volume'])
    # Plot the data
    scatter(
        xs=[aw_vols],
        ys=[pow_vols], 
        title=title, 
        Show=True
    )

if __name__ == "__main__":
    plot_vols()
    