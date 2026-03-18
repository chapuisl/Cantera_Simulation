"""
# ===================================================================================================================
#  Cantera Evolution Plotting Utility
# ===================================================================================================================
#
#  Author          : Lilian CHAPUIS
#  Affiliation     : IMFT - Institut de Mécanique des Fluides de Toulouse
#  Location        : Toulouse, France
#  Creation Date   : 17 February 2026
#  Last Modified   : 17 February 2026
#  Version         : 1.0.01
#
# -------------------------------------------------------------------------------------------------------------------
#  DESCRIPTION
# -------------------------------------------------------------------------------------------------------------------
#  This function provides a flexible, configurable tool for plotting time-series or parametric evolution data.
#  It supports single plots, multiple curves, optional subplots, and secondary axes for additional datasets.
#  
#  The main purpose is to standardize and simplify plotting of simulation results, 
#  while giving full control over colors, line styles, labels, and figure properties.
#
#  Key features:
#    - Plot single or multiple datasets on a primary axis.
#    - Optional secondary y-axis for plotting a second dataset with independent scaling.
#    - Supports multiple subplots with individual titles.
#    - Customizable figure size, line colors, styles, markers, axis labels, title, legend, and grid.
#    - Automatic layout adjustment for clarity and readability.
#    - Option to save figures to disk with sanitized filenames.
#    - Option to display figures interactively.
#
#  Parameters:
#    - t                  : Array-like X-axis values or list of arrays for multiple curves/subplots.
#    - data               : Array-like or list of arrays. Y-axis values to plot.
#    - labels             : List[str] Legend labels for each curve on the primary axis.
#    - colors             : List[str] Colors for primary curves.
#    - styles             : List[str] Line styles for primary curves ('-', '--', etc.).
#    - xlabel             : str Label for the X-axis.
#    - ylabel             : str. Label for the Y-axis.
#    - title              : str Title of the figure.
#    - legend_loc         : str Location of the legend ('upper right', 'center left', etc.).
#    - grid               : bool to display a grid.
#    - marker             : Marker style for the curves.
#    - x_limit_left       : float Left limit of the X-axis.
#    - x_limit_right      : float Right limit of the X-axis.
#    - type_x_scale       : str Scale of the X-axis ('linear', 'log', etc.).
#    - type_y_scale       : str Scale of the Y-axis ('linear', 'log', etc.).
#    - line_value         : List[str]  Position of the line (Make sur that it macth with the orientation) 
#    - line_orientation   : List[str]  Orientation line ('H': Horizontal, 'V': Vertival).
#    - secondary_data     : Array-like or list of arrays. Data for the secondary Y-axis.
#    - secondary_label    : str or list[str]. Label(s) for secondary axis curves.
#    - secondary_color    : str or list[str]. Colors for secondary axis curves.
#    - secondary_ylabel   : str Label for the secondary Y-axis.
#    - figsize            : tuple Custom figure size (width, height).
#    - subplot_titles     : list[str]. Titles for each subplot (if plotting multiple subplots).
#    - plot_fig           : bool Whether to display the figure interactively.
#    - save_fig           : bool Whether to save the figure to disk.
#    - save_path          : str Directory path to save the figure.
#    - name_fig           : str Filename for the saved figure (will be sanitized).
#
#  Returns:
#    - None
#
#  Usage examples:
#    # Single plot
#    plot_evolution(t, y_data, labels=['Simulation'], xlabel='Time (s)', ylabel='Temperature (K)',
#                   title='Temperature Evolution', plot_fig=True)
#
#    # Multiple subplots with secondary axis
#    plot_evolution([t1, t2], [y1, y2], subplot_titles=['Pressure', 'Velocity'],
#                   secondary_data=[y_sec1, y_sec2], secondary_label=['Heat Flux', 'Momentum'],
#                   save_fig=True, save_path='./figures', name_fig='multi_plot')
#
# -------------------------------------------------------------------------------------------------------------------
#  COPYRIGHT NOTICE
# -------------------------------------------------------------------------------------------------------------------
#  © 2026 Lilian CHAPUIS – All Rights Reserved.
#
#  This file and its structure are protected by intellectual property rights.
#  Unauthorized copying, distribution, modification, or use of this file
#  without prior written permission of the author is strictly prohibited.
#
#  This configuration file is intended solely for use within the associated
#  simulation framework developed by the author.
#
# ===================================================================================================================
"""

"""
# ===================================================================================================================
#  Imports from other modules
# ===================================================================================================================
"""
import Graphic_Configuration as GC 

"""
# ===================================================================================================================
#  Import library
# ===================================================================================================================
"""
from matplotlib.ticker import MaxNLocator,FormatStrFormatter
from matplotlib.legend_handler import HandlerTuple
import matplotlib.pyplot as plt
import os

"""
# ===================================================================================================================
#  Function
# ===================================================================================================================
"""

            
def plot_evolution(t, data, labels=None, colors=None, styles=None , xlabel=None,  ylabel=None,figsize = None,
                   title="", legend_loc="best", grid=True, marker = None,x_limit_left= None, x_limit_right= None,type_x_scale='linear',type_y_scale='linear',
                   line_value=None, line_orientation='H',
                   secondary_data=None, secondary_label=None,
                   secondary_color=None, secondary_ylabel=None, subplot_titles=None,
                   plot_fig = False ,save_fig = False, save_path = None,name_fig = None):
    
    if subplot_titles is not None and isinstance(data, (list, tuple)):
         n_subplots = len(data)
         fig, axes = plt.subplots(n_subplots, 1, figsize=plt.rcParams["figure.figsize"])
         if n_subplots == 1:
             axes = [axes]  # pour uniformiser
         fig.suptitle(title, fontsize=14, fontweight='bold')
    
         for i, ax in enumerate(axes):
             ax.plot(t, data[i], color=(colors[i] if colors else None))
             
             ax.xaxis.set_major_locator(MaxNLocator(5))
             ax.yaxis.set_major_locator(MaxNLocator(6))
             ax.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))
             ax.xaxis.set_major_formatter(FormatStrFormatter('%.2f'))
             ax.grid(True, which="major")
    
             ax.set_ylabel(subplot_titles[i])
             if i == n_subplots - 1:
                 ax.set_xlabel(xlabel)
                 ax.set_xlim(x_limit_left, x_limit_right)
    
         plt.tight_layout(rect=[0, 0, 1, 0.95])
    
         if save_fig and save_path is not None:
             save_dir = os.path.join(save_path)
             os.makedirs(save_dir, exist_ok=True)
             safe_title = title.replace(" ", "_").replace("/", "_").replace("\\", "_")
             plt.savefig(os.path.join(save_dir, f"{safe_title}.png"), dpi=300)
             plt.close()   
    
         if plot_fig:
             plt.show()
         return

    # --- Cas simple : un seul graphique ---
    fig, ax1 = plt.subplots(figsize=figsize)
    
    ax1.xaxis.set_major_locator(MaxNLocator(5))
    ax1.yaxis.set_major_locator(MaxNLocator(6))
    ax1.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))
    ax1.xaxis.set_major_formatter(FormatStrFormatter('%.2f'))
    ax1.grid(True, which="both")
    ax1.set_yscale(type_y_scale)
    ax1.set_xscale(type_x_scale)
    

    
    if isinstance(data, (list, tuple)) and len(data) > 0 and isinstance(data[0], (list, tuple)):
        data_list = data
    else:
        data_list = [data]
    
    n_curves = len(data_list)
    
    if isinstance(t, (list, tuple)) and len(t) > 0 and isinstance(t[0], (list, tuple)):
        t_list = t
    else:
        t_list = [t] * n_curves
    
    for i in range(n_curves):
        ax1.plot(
            t_list[i],
            data_list[i],
            color=(colors[i] if colors and i < len(colors) else '0.5'),
            linestyle=(styles[i] if styles and i < len(styles) else "-"),
            label=(labels[i] if labels and i < len(labels) else None),
            marker=marker
        )
    
    # Ajouter une ligne pointillée si line_value est spécifié
    if line_value is not None and len(line_value) == len(line_orientation):

        offset_h = 0
        offset_v = 0
    
        y_min, y_max = ax1.get_ylim()
        x_min, x_max = ax1.get_xlim()
    
        y_range = y_max - y_min
        x_range = x_max - x_min
    
        for i in range(len(line_value)):
    
            if line_orientation[i] == 'H':
    
                ax1.axhline(y=line_value[i], color='red', linestyle='--', linewidth=2)
    
                # Décalage vertical progressif
                if type_y_scale == 'log':
                    y_text = y_max / (10 ** (0.1 * offset_h))
                    x_text = x_max + 0.2 * x_range
                else:
                    x_text = x_max + 0.2 * x_range
                    y_text = line_value[i] + offset_h * 0.1 * y_range
                
                ax1.annotate(f'{line_value[i]:.2e}', xy=(x_max, line_value[i]), xytext=(x_text, y_text), color='red', va='center', ha='left', 
                             arrowprops=dict(arrowstyle='-', color='red', lw=0.8), 
                             bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.3', linewidth=1)) 
    
                offset_h += 1
    
    
            elif line_orientation[i] == 'V':
    
                ax1.axvline(x=line_value[i], color='b', linestyle='--', linewidth=2)
    
                # Décalage horizontal progressif
                if type_x_scale == 'log':
                    x_text = x_max / (10 ** (0.1 * offset_v))
                    y_text = y_max + 0.2 * y_range
                    
                
                else:
                    x_text = line_value[i] + offset_v * 0.1 * x_range
                    y_text = y_max + 0.2 * y_range
                
                ax1.annotate(f'{line_value[i]:.2e}', xy=(line_value[i], y_max), xytext=(x_text, y_text), color='b', va='bottom', ha='right', rotation=90, 
                             arrowprops=dict(arrowstyle='-', color='b', lw=0.8), 
                             bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.3', linewidth=1))
                
             
                offset_v += 1
    
        # Agrandit légèrement les limites pour voir le texte
        ax1.set_xlim(x_min, x_max + 0.15 * x_range)
        ax1.set_ylim(y_min, y_max + 0.15 * y_range)
            
    ax1.set_xlabel(xlabel)
    ax1.set_ylabel(ylabel)
    ax1.set_xlim(x_limit_left, x_limit_right)
    ax1.set_title(title)
    
    ax1.legend(loc="best") 
            
    # --- Axe secondaire optionnel ---
    if secondary_data is not None:
        
    
        ax2 = ax1.twinx()
    
        # ---------- NORMALISATION secondary_data ----------
        if isinstance(secondary_data, (list, tuple)) and len(secondary_data) > 0 and isinstance(secondary_data[0], (list, tuple)):
            secondary_data_list = secondary_data
        else:
            secondary_data_list = [secondary_data]
    
        n_sec_curves = len(secondary_data_list)
        
        # ---------- SECONDARY color ----------
        if secondary_color is None:
            sec_color = GC.Red_Black()
            
        elif isinstance(secondary_color, (list, tuple)):
            sec_color = secondary_color
        
        # ---------- NORMALISATION t ----------
        if isinstance(t, (list, tuple)) and len(t) > 0 and isinstance(t[0], (list, tuple)):
            t_sec_list = t
        else:
            t_sec_list = [t] * n_sec_curves
            
        if secondary_label is None:
            secondary_label = labels
        
        # ---------- PLOT ----------
        for i in range(n_sec_curves):
            ax2.plot(
                t_sec_list[i],
                secondary_data_list[i],
                color=(sec_color[i] if sec_color and i < len(sec_color) else '0.5'),
                linestyle='--',
                label=(secondary_label[i] if secondary_label and i < len(secondary_label) else None),
                marker=marker
            )
        
        # ---------- STYLE AXE 2 ----------
        ax2.set_ylabel(
            secondary_ylabel if secondary_ylabel else "",
            color= '0.0' 
        )
        ax2.tick_params(axis='y', labelcolor=sec_color[0])
        ax2.yaxis.set_major_locator(MaxNLocator(6))
    
        # ---------- LÉGENDE COMBINÉE ----------
        
        lines_1, labels_1 = ax1.get_legend_handles_labels()
        lines_2, labels_2 = ax2.get_legend_handles_labels()
        
        handles = []
        labels = []
        
        for l1, l2, lab in zip(lines_1, lines_2, labels_1):
            handles.append((l1, l2))
            labels.append(lab)
        
        ax1.legend(
            handles,
            labels,
            handler_map={tuple: HandlerTuple(ndivide=None)},
            loc=legend_loc
        )

    else:
        if labels:
            ax1.legend(loc=legend_loc)
    
    plt.tight_layout()
    
    if save_fig and save_path is not None:
        save_dir = os.path.join(save_path)
        os.makedirs(save_dir, exist_ok=True)
        save_name = name_fig.replace(" ", "_").replace("/", "_").replace("\\", "_")
        plt.savefig(os.path.join(save_dir, f"{save_name}.png"), dpi=300)
        plt.close()     

    
    if plot_fig:
        plt.show()
