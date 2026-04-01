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
#  This module provides utilities to standardize and customize the appearance of matplotlib plots.
#  It includes:
#    1. `config_plot` : a function to globally configure figure aesthetics such as size, font sizes, colors,
#       line styles, tick and grid formatting, and legend properties.
#    2. `Color Configuration` : Different utility function that return a custum of 10 color gradient palette ranging 
#       from oen color to a other
#    3. `Line Configuration` : Different utility function that return a custum of 10 line gradient palette ranging 
#    4. 'test function': This function is use to show the plot for each different color function 
#    
#
#  These utilities are intended to create consistent, publication-quality figures with minimal repetitive
#  setup code.
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
#  Import library
# ===================================================================================================================
"""
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np

"""
# ===================================================================================================================
#  Function
# ===================================================================================================================
"""

def config_plot(style="default", figsize=(12, 8), title_size=40, label_size=40, tick_size=36, grid=True, background="#f9f9f9"):
    plt.style.use(style)
    mpl.rcParams.update({
        "figure.figsize": figsize,
        "font.size": 18,
        "figure.facecolor": background,
        "axes.facecolor": "white",
        "axes.edgecolor": "#333333",
        "axes.labelsize": label_size,
        "axes.titlesize": title_size,
        "axes.titleweight": "bold",
        "grid.alpha": 1.0,
        "grid.color": "#888888",
        "xtick.labelsize": tick_size,
        "ytick.labelsize": tick_size,
        "legend.fontsize": 20,
        "legend.frameon": True,
        "legend.facecolor": "#f0f0f0",
        "legend.edgecolor": "#cccccc",
        "lines.linewidth": 4,
        "axes.linewidth": 2.5,
        "grid.linewidth": 2.0,
        "lines.markersize": 25,
        "lines.markeredgewidth": 2,
        "xtick.major.width": 6,
        "ytick.major.width": 6,
        "xtick.major.size": 10,
        "ytick.major.size": 10,
        "xtick.major.pad": 12,
        "ytick.major.pad": 12,
        "xtick.minor.width": 1.5,
        "ytick.minor.width": 1.5,
        "xtick.minor.size": 5,  # Ajustez la taille des ticks mineurs ici
        "ytick.minor.size": 5, 
        "figure.dpi": 500,
        "savefig.dpi": 300,
        "savefig.bbox": "tight"
    })
    
####################################################################################################################################
#                                                                                                                                  #                                                                                                                                                                          
#                                                       Color Configurqtion                                                        #
#                                                                                                                                  #           
####################################################################################################################################


def Black_Gray():
    # Dégradé de 10 couleurs : noir → gris → violet
    return [(0.0, 0.0, 0.0),                                                 # Noir profond
            (0.15, 0.15, 0.15),    # Gris foncé
            (0.2, 0.2, 0.2), 
            (0.3, 0.3, 0.3), 
            (0.4, 0.4, 0.4), 
            (0.5, 0.5, 0.5), 
            (0.6, 0.6, 0.6), 
            (0.7, 0.7, 0.7), 
                # Gris très clair
            ] 
      
def Black_Purple():
    # Dégradé de 10 couleurs : noir → gris → violet
    return [(0.0, 0.0, 0.0),                                                 # Noir profond
            (0.2, 0.2, 0.2), 
            (0.3, 0.3, 0.3), 
            (0.4, 0.4, 0.4), 
            (0.6, 0.6, 0.6),     # Gris très clair
            (0.9, 0.6, 1.0),
            (0.8, 0.4, 1.0),
            (0.6, 0.0, 0.8),
            (0.45, 0.0, 0.65),
            (0.3, 0.0, 0.5),         
            (0.2, 0.0, 0.4),                                                 # Violet très foncé
                                                             # Violet foncé
            ]                                                 # Violet clair

def Black_Blue():
    # Dégradé de 10 couleurs : noir → bleu
    return [(0.0, 0.0, 0.0),                                                 # Noir profond
            (0.2, 0.2, 0.2), 
            (0.3, 0.3, 0.3), 
            (0.4, 0.4, 0.4), 
            (0.5, 0.5, 0.5), 
            (0.6, 0.6, 0.6),     # Gris très clair
            (0.4, 0.8, 1.0),
            (0.2, 0.7, 1.0),
            (0.1, 0.5, 1.0),
            (0.0, 0.4, 1.0), 
            (0.0, 0.2, 0.9), 
            (0.0, 0.0, 0.8),
            (0.0, 0.0, 0.6), ]       # Bleu foncé
            
            

def Black_Green():
    # Dégradé de 10 couleurs : noir → vert
    return [(0.0, 0.0, 0.0),                                                 # Noir profond
            (0.15, 0.15, 0.15),    # Gris foncé
            (0.2, 0.2, 0.2), 
            (0.3, 0.3, 0.3), 
            (0.4, 0.4, 0.4), 
            (0.5, 0.5, 0.5), 
            (0.6, 0.6, 0.6),    # Gris très clair
            (0.5, 1.0, 0.5),   
            (0.4, 0.9, 0.4),   
            (0.3, 0.8, 0.3),  
            (0.2, 0.7, 0.2),
            (0.0, 0.6, 0.0),
            (0.0, 0.5, 0.0),    
            (0.0, 0.4, 0.0),        # Vert foncé
                # Vert moyen-foncé
                    # Vert moyen
               # Vert lumineux
                  # Vert clair
                 # Vert très clair
                 # Vert presque fluo
            ]        # Vert très lumineux

def Black_Red():
    # Dégradé de 10 couleurs : noir → rouge
    return [(0.0, 0.0, 0.0),                                                 # Noir profond
            (0.3, 0.3, 0.3), 
            (0.5, 0.5, 0.5), 
            (0.7, 0.7, 0.7), 
            (1.0, 0.6, 0.6),
            (1.0, 0.5, 0.5),
            (0.9, 0.4, 0.4),
            (0.8, 0.3, 0.3), 
            (0.6, 0.0, 0.0),      
            (0.4, 0.0, 0.0),        # Rouge foncé
                  ]      


def Blue_Red():
    # Dégradé de 10 couleurs : noir → rouge
    return [(0.2, 0.2, 0.4),        # Bleu foncé
            (0.3, 0.3, 0.5),        # Bleu moyen-foncé
            (0.4, 0.4, 0.6),        # Bleu moyen
            (0.5, 0.5, 0.7),        # Bleu moyen-clair
            (0.6, 0.6, 0.8),        # Bleu clair
            (0.7, 0.7, 0.9),        # Bleu très clair
            (1.0, 0.6, 0.6),
            (1.0, 0.5, 0.5),
            (0.9, 0.4, 0.4),
            (0.8, 0.3, 0.3), 
            (0.7, 0.2, 0.2), 
            (0.6, 0.0, 0.0),      
            (0.5, 0.0, 0.0),  
            (0.4, 0.0, 0.0),        # Rouge foncé
                  ]        

def Black_Orange():
    # Dégradé de 10 couleurs : noir → rouge
    return [(0.0, 0.0, 0.0),                                                 # Noir profond
            (0.15, 0.15, 0.15),    # Gris foncé
            (0.2, 0.2, 0.2), 
            (0.3, 0.3, 0.3), 
            (0.4, 0.4, 0.4), 
            (0.5, 0.5, 0.5), 
            (0.6, 0.6, 0.6), 
            (0.9, 0.5, 0.25),
            (0.9, 0.4, 0.2),
            (0.8, 0.3, 0.1),
            (0.8, 0.2, 0.1), 
            (0.7, 0.2, 0.1), 
            (0.6, 0.2, 0.1),   
            (0.6, 0.1, 0.1),        # Orange foncé
            
                  ]        

def Ramdom():
    # Dégradé de 10 couleurs : noir → rouge
    return [(0.0, 0.0, 0.0),       
            (0.9, 0.4, 0.2),                                          # Noir profond
            (0.7, 0.7, 0.7), 
            (0.8, 0.2, 0.2), 
            (0.2, 0.8, 0.2),
            (0.0, 0.2, 0.9), 
            (0.7, 0.0, 0.65),
               # Rouge foncé
                  ] 
def Purple_Black():
    return list(reversed(Black_Purple()))

def Blue_Black():
    return list(reversed(Black_Blue()))

def Green_Black():
    return list(reversed(Black_Green()))

def Red_Black():
    return list(reversed(Black_Red()))

def Red_Blue():
    return list(reversed(Blue_Red()))


    
####################################################################################################################################
#                                                                                                                                  #                                                                                                                                                                          
#                                                       Line  Configurqtion                                                        #
#                                                                                                                                  #           
####################################################################################################################################
def LineStyles():
    # Palette de 10 styles de lignes différents
    return [
        '-',                # Ligne pleine
        '-.',               # Tirets-point
        (0, (5, 2)),        # Tirets longs serrés
        (0, (3, 5, 1, 5)),  # Tiret-point espacé
        (0, (5, 10)),       # Tirets très espacés
        (0, (1, 10)),       # Points très espacés
        (0, (3, 1, 1, 1)),  # Tiret + petits points
        ':',                # Pointillés
        (0, (1, 1)),        # Très petits points
    ]




####################################################################################################################################
#                                                                                                                                  #                                                                                                                                                                          
#                                                       Test  Configurqtion                                                        #
#                                                                                                                                  #           
####################################################################################################################################

def plot_line(styles):
    x = [xi for xi in range(15)]
    colors = Black_Orange()
    for i, style in enumerate(styles):
        
        y = [yi+i for yi in range(15)]
        
        plt.plot(x, y, linestyle=style,color=colors[i])
    plt.show()

def plot_colors(colors):
    fig, ax = plt.subplots()
    for i, color in enumerate(colors):
        ax.add_patch(plt.Rectangle((0, i), 1, 1, color=color))

    ax.set_xlim(0, 1)
    ax.set_ylim(0, len(colors))
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title("Black → Purple Gradient")

    plt.show()
    

# plot_line(LineStyles())
# plot_colors(Ramdom()) 

