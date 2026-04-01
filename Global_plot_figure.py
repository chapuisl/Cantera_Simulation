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
from matplotlib.ticker import LogLocator, LogFormatterSciNotation, NullFormatter, FuncFormatter
from matplotlib.legend_handler import HandlerTuple
import matplotlib.pyplot as plt
import numpy as np
import os

"""
# ===================================================================================================================
#  Function
# ===================================================================================================================
"""

def _to_list(x):
    """Wrap a single array/list into a list-of-lists."""
    if isinstance(x, (list, tuple)) and len(x) > 0 and isinstance(x[0], (list, tuple, np.ndarray)):
        return x
    return [x]


def _nice_ticks(vmin, vmax, n_target=5):
    """
    Retourne (ticks, new_vmin, new_vmax) avec des valeurs "rondes".

    Stratégie : on cherche le pas "propre" (1/2/2.5/5 × 10^k) qui génère
    entre n_target-2 et n_target+2 ticks en débordant le moins possible
    au-delà des bornes réelles.

    Exemple : données [1, 30] → step=5 → ticks [0,5,10,15,20,25,30] ✓
              données [0.5, 1.7] → step=0.25 → ticks [0.5,0.75,1,1.25,1.5,1.75] ✓
    """
    span = vmax - vmin
    if span == 0:
        return np.array([vmin]), vmin, vmax

    best = None
    best_score = np.inf

    # On teste des pas "propres" autour de l'ordre de grandeur du span
    mag = 10 ** np.floor(np.log10(span))
    for exp_offset in [-1, 0, 1]:          # ordres de grandeur voisins
        m = mag * (10 ** exp_offset)
        for factor in [1, 2, 2.5, 5]:
            step = factor * m
            new_vmin = np.floor(vmin / step) * step
            new_vmax = np.ceil(vmax / step) * step
            ticks = np.arange(new_vmin, new_vmax + step * 0.5, step)
            n = len(ticks)

            # Pénalité : écart au nombre cible + débordement relatif
            overshoot = ((new_vmax - vmax) + (vmin - new_vmin)) / span
            score = abs(n - n_target) * 2 + overshoot
            if score < best_score:
                best_score = score
                best = (ticks, new_vmin, new_vmax)

    return best


def _set_axis_ticks(ax, scale_x, scale_y, xmin, xmax, ymin, ymax):
    """
    Calcule les ticks propres depuis les bornes RÉELLES des données
    (pas depuis get_xlim qui inclut les marges matplotlib) puis applique
    set_xlim / set_ylim avec les nouvelles bornes arrondies.
    """
    for axis, scale, vmin, vmax in [('x', scale_x, xmin, xmax),
                                     ('y', scale_y, ymin, ymax)]:
        if scale == 'log':
            continue
        setter    = ax.set_xlim   if axis == 'x' else ax.set_ylim
        set_ticks = ax.set_xticks if axis == 'x' else ax.set_yticks
        fmt_axis  = ax.xaxis      if axis == 'x' else ax.yaxis

        ticks, new_min, new_max = _nice_ticks(vmin, vmax, n_target=5)
        setter(new_min, new_max)
        set_ticks(ticks)

        # Formateur : scientifique si grands/petits nombres
        if abs(new_max) > 1e4 or (new_max != 0 and new_min != 0 and abs(new_min / new_max) < 1e-2):
            fmt_axis.set_major_formatter(FuncFormatter(
                lambda x, _: f'{x:.2e}' if x != 0 else '0'
            ))
        else:
            step = ticks[1] - ticks[0] if len(ticks) > 1 else 1
            dec = max(0, -int(np.floor(np.log10(abs(step)))) if step != 0 else 0)
            fmt_axis.set_major_formatter(FuncFormatter(
                lambda x, _, d=dec: f'{x:.{d}f}'
            ))


def _set_log_axis(ax, axis):
    """Configure un axe en log avec labels sur les ticks mineurs."""
    a = ax.xaxis if axis == 'x' else ax.yaxis
    a.set_major_locator(LogLocator(base=10, numticks=10))
    a.set_major_formatter(LogFormatterSciNotation(base=10))
    a.set_minor_locator(LogLocator(base=10, subs='auto', numticks=10))
    a.set_minor_formatter(LogFormatterSciNotation(base=10, minor_thresholds=(2, 0.5)))

    # Ticks mineurs : penchés + plus petits
    tick_axis = 'x' if axis == 'x' else 'y'
    ax.tick_params(axis=tick_axis, which='minor', labelsize=14, rotation=45)

def _add_ref_lines(ax, line_value, line_orientation, type_x_scale, type_y_scale):
    """Trace les lignes de référence H/V avec annotation."""
    x_min, x_max = ax.get_xlim()
    y_min, y_max = ax.get_ylim()
    x_range, y_range = x_max - x_min, y_max - y_min

    offset_h = offset_v = 0
    for val, ori in zip(line_value, line_orientation):
        if ori == 'H':
            ax.axhline(y=val, color='red', linestyle='--', linewidth=2)
            x_text = x_max + 0.2 * x_range
            y_text = val + offset_h * 0.1 * y_range
            ax.annotate(f'{val:.2e}', xy=(x_max, val), xytext=(x_text, y_text),
                        color='red', va='center', ha='left',
                        arrowprops=dict(arrowstyle='-', color='red', lw=0.8),
                        bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.3'))
            offset_h += 1
        elif ori == 'V':
            ax.axvline(x=val, color='b', linestyle='--', linewidth=2)
            x_text = val + offset_v * 0.1 * x_range
            y_text = y_max + 0.2 * y_range
            ax.annotate(f'{val:.2e}', xy=(val, y_max), xytext=(x_text, y_text),
                        color='b', va='bottom', ha='right', rotation=90,
                        arrowprops=dict(arrowstyle='-', color='b', lw=0.8),
                        bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.3'))
            offset_v += 1


# ───────────────────────────────────────────────────────────────
#  Fonction principale
# ───────────────────────────────────────────────────────────────

def plot_evolution(
    t, data,
    labels=None, colors=None, styles=None,
    xlabel=None, ylabel=None, figsize=None, title="", legend_loc="best",
    x_limit_left=None, x_limit_right=None, y_limit_bot=None, y_limit_top=None,
    type_x_scale='linear', type_y_scale='linear',
    line_value=None, line_orientation=None,
    secondary_data=None, secondary_label=None, secondary_color=None, secondary_ylabel=None,
    marker=None, plot_fig=False, save_fig=False, save_path=None, name_fig=None,
):
    fig, ax1 = plt.subplots(figsize=figsize)
    ax1.grid(True, which="both")
    ax1.set_xscale(type_x_scale)
    ax1.set_yscale(type_y_scale)

    if type_x_scale == 'log':
        _set_log_axis(ax1, 'x')
    if type_y_scale == 'log':
        _set_log_axis(ax1, 'y')

    # ── Tracé des courbes principales ──
    data_list = _to_list(data)
    t_list = _to_list(t)
    if len(t_list) == 1:
        t_list = t_list * len(data_list)

    for i, (ti, di) in enumerate(zip(t_list, data_list)):
        ax1.plot(ti, di,
                 color=colors[i] if colors and i < len(colors) else '0.5',
                 linestyle=styles[i] if styles and i < len(styles) else '-',
                 label=labels[i] if labels and i < len(labels) else None,
                 marker=marker)

    # ── Bornes réelles des données (bypass des marges matplotlib) ──
    all_x = np.concatenate([np.asarray(ti).ravel() for ti in t_list])
    all_y = np.concatenate([np.asarray(di).ravel() for di in data_list])
    raw_xmin = x_limit_left  if x_limit_left  is not None else float(np.nanmin(all_x))
    raw_xmax = x_limit_right if x_limit_right is not None else float(np.nanmax(all_x))
    raw_ymin = y_limit_bot   if y_limit_bot   is not None else float(np.nanmin(all_y))
    raw_ymax = y_limit_top   if y_limit_top   is not None else float(np.nanmax(all_y))

    # ── Ticks propres calculés sur les vraies bornes, applique aussi set_xlim/ylim ──
    _set_axis_ticks(ax1, type_x_scale, type_y_scale, raw_xmin, raw_xmax, raw_ymin, raw_ymax)

    ax1.set_xlabel(xlabel)
    ax1.set_ylabel(ylabel)
    ax1.set_title(title)
    plt.setp(ax1.get_xticklabels(), rotation=45, ha='right')

    # ── Lignes de référence ──
    if line_value is not None and line_orientation is not None:
        _add_ref_lines(ax1, line_value, line_orientation, type_x_scale, type_y_scale)

    # ── Axe secondaire ──
    if secondary_data is not None:
        ax2 = ax1.twinx()
        sec_list = _to_list(secondary_data)
        sec_colors = (secondary_color if isinstance(secondary_color, (list, tuple))
                      else [secondary_color or 'darkred'] * len(sec_list))
        sec_labels = secondary_label or labels
        t_sec = t_list if len(t_list) == len(sec_list) else [t_list[0]] * len(sec_list)

        for i, (ti, di) in enumerate(zip(t_sec, sec_list)):
            ax2.plot(ti, di,
                     color=sec_colors[i] if i < len(sec_colors) else 'darkred',
                     linestyle='--',
                     label=sec_labels[i] if sec_labels and i < len(sec_labels) else None,
                     marker=marker)

        ax2.set_ylabel(secondary_ylabel or "", color='black')
        ax2.tick_params(axis='y', labelcolor=sec_colors[0])

        all_sx = np.concatenate([np.asarray(ti).ravel() for ti in t_sec])
        all_sy = np.concatenate([np.asarray(di).ravel() for di in sec_list])
        _set_axis_ticks(ax2, 'linear', 'linear',
                        float(np.nanmin(all_sx)), float(np.nanmax(all_sx)),
                        float(np.nanmin(all_sy)), float(np.nanmax(all_sy)))

        # Légende combinée
        h1, l1 = ax1.get_legend_handles_labels()
        h2, _ = ax2.get_legend_handles_labels()
        ax1.legend([(a, b) for a, b in zip(h1, h2)], l1,
                   handler_map={tuple: HandlerTuple(ndivide=None)}, loc=legend_loc)
    else:
        if labels:
            ax1.legend(loc=legend_loc)

    # ── Sauvegarde ──
    if save_fig and save_path:
        os.makedirs(save_path, exist_ok=True)
        fname = name_fig.replace(" ", "_").replace("/", "_").replace("\\", "_")
        plt.savefig(os.path.join(save_path, f"{fname}.png"), dpi=300)
        plt.close()

    if plot_fig:
        plt.show()