"""
# ===================================================================================================================
#  Utility Functions Module:
# ===================================================================================================================
#
#  Author          : Lilian CHAPUIS
#  Affiliation     : IMFT - Institut de Mécanique des Fluides de Toulouse
#  Location        : Toulouse, France
#  Creation Date   : 20 February 2026
#  Last Modified   : 20 February 2026
#  Version         : 1.0.01
#
# -------------------------------------------------------------------------------------------------------------------
#  DESCRIPTION
# -------------------------------------------------------------------------------------------------------------------
#   This module provides a set of utility functions to support the simulations.
#
#  The functions handle:
#      - Creation and organization of results directories and subfolders
#      - Backup and traceability of input parameter files
#      - Conversion between list and dictionary representations of chemical species
#      - Formatting of species compositions into standardized string names
#      - Extraction and preparation of fuel, oxidizer, and mechanism information
#
#  These utilities are designed to ensure reproducible, organized, and
#  easily traceable simulation outputs, facilitating post-processing
#  and parametric studies across multiple conditions and mechanisms.
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
from colorama import Fore
from colorama import init
init(autoreset=True)
import shutil
import time
import sys
import os

"""
# ===================================================================================================================
#  Function
# ===================================================================================================================
"""


# Initialize and structure the simulation results directory.
#
# This function creates a clean backup directory used to store all simulation outputs.
# If a directory with the same name already exists, it is completely removed and
# recreated to ensure a consistent and reproducible working environment.
#
# The function verifies the presence of the parameter input file, creates the main
# results directory along with predefined subdirectories, and copies the parameter
# file into the backup folder to ensure traceability of the simulation setup.
#
# @param parameter_coupling   : Path to the input parameter file (.txt or .dat)
#                               containing the simulation configuration.
#
# @param file_name            : Name of the root directory where simulation results
#                               will be stored.
#
# @return subfolders          : List of the created subdirectory names.
def backup_file(parameter_coupling,file_name):
    try:
        
        # Vérification du fichier source
        if not os.path.isfile(parameter_coupling):
            print(f"⚠ WARNING: The file'{parameter_coupling}' not found. Execution aborted.")
            sys.exit(0)  # arrêt propre du programme

        # Dossier principal de sauvegarde
        backup_dir = os.path.abspath(file_name)

        # Suppression de l'ancien dossier s'il existe
        current_file = False
        if os.path.exists(backup_dir):
            shutil.rmtree(backup_dir)
            current_file = True
        

        # Création du nouveau dossier principal
        os.makedirs(backup_dir)
        if current_file is False:
            print(f" \t \t > NEW file '{file_name}' created.")
        else: 
            print(f"\t \t > OLD file '{file_name}' updated.")

        # Création des sous-dossiers
        subfolders = [
            "01_plot_evolution",
            "02_plot_species_evolution",
            "03_Other_plot",
            "04_csv_evolution",
            "05_AVBP_Solution"
        ]
        for folder in subfolders:
            os.makedirs(os.path.join(backup_dir, folder))

        print(f" \t \t > SUB file created in : {file_name}")

        # Copie du fichier .dat dans le dossier principal
        dest_file = os.path.join(backup_dir, os.path.basename(parameter_coupling))
        shutil.copy2(parameter_coupling, dest_file)
        print(f"\t \t > File '{parameter_coupling}' copied.")
        


    except Exception as e:
        # Capture de toute autre erreur imprévue
        print(f"❌ ERROR: An error occurred. : {e}")
        sys.exit(0)  # arrêt propre sans afficher le traceback
    print(Fore.GREEN +"  > END INITIALISATION ")
    time.sleep(1.5)
    print()
    return subfolders


# Create a new directory inside a given parent path.
#
# This function creates a directory (or nested directory structure) inside the
# specified parent path. The input can be either a single folder name or a list/tuple
# of folder names to create hierarchical subdirectories in one call.
#
# If the directory already exists, it is preserved (no deletion is performed).
#
# @param parent_path      : Path to the existing parent directory.
#
# @param folders          : Name of the new folder (string) or list/tuple of folder
#                           names defining a nested directory structure.
#
# @return new_folder_path : Absolute path to the created (or existing) directory.
def create_folder(parent_path, folders):
    if not os.path.exists(parent_path):
        raise OSError(f"Parent path '{parent_path}' does not exist.")

    # Normalisation : str → list
    if isinstance(folders, str):
        folders = [folders]
    elif not isinstance(folders, (list, tuple)):
        raise TypeError("folders must be a string or a list/tuple of strings")

    new_folder_path = os.path.join(parent_path, *folders)

    os.makedirs(new_folder_path, exist_ok=True)
    return new_folder_path


# Format a dictionary of components into a standardized string representation.
#
# This function converts a dictionary containing species and their associated
# quantities into a single formatted string. Integer-valued floats are automatically
# converted to integers to avoid unnecessary decimal notation.
#
# Example:
#     {"H2": 1.0, "O2": 0.5}  →  "1H2_0.5O2"
#
# @param component_dict   : Dictionary with species names as keys and numerical
#                           amounts as values.
#
# @param separator        : String used to separate formatted components
#                           (default is "_").
#
# @return formatted_str   : Concatenated string representing the composition.
def format_dict_components(component_dict, separator="_"):
    formatted_list = []
    for species, amount in component_dict.items():
        # supprime .0 si amount est entier
        if isinstance(amount, float) and amount.is_integer():
            amount = int(amount)
        formatted_list.append(f"{amount}{species}")
    return separator.join(formatted_list)
       

 
# Convert a list-based species representation into a dictionary.
#
# This function transforms a list describing chemical components into a dictionary.
# It supports both:
#   - A single pair list       → ['H2', 1.0]
#   - A list of pair lists     → [['O2', 1], ['N2', 3.76]]
#
# @param lst          : List describing species and associated quantities.
#
# @return dict_output : Dictionary mapping species names to their numerical values.
def list_to_dict(lst):
    if isinstance(lst[0], list):
        # Case with multiple sublists (e.g., [['O2', 1], ['N2', 3.76]])
        return {item[0]: item[1] for item in lst}
    else:
        # Case with a single list (e.g., ['H2', 1.0])
        return {lst[0]: lst[1]}
    
    
# Prepare chemical component dictionaries and mechanism list for simulation.
#
# This function converts input component lists into dictionaries, formats their
# string representations for naming purposes, and extracts the names of all
# available kinetic mechanisms.
#
# @param fuel_list        : List describing the fuel composition (e.g., ['H2', 2]).
# @param oxidizer_list    : List describing the oxidizer composition (e.g., ['O2', 1]).
# @param mechanisms_dict  : Dictionary containing all kinetic mechanisms with their
#                           Cantera gas objects.
#
# @return fuel_dict         : Dictionary mapping fuel species to amounts.
# @return oxidizer_dict     : Dictionary mapping oxidizer species to amounts.
# @return fuel_name_str     : Formatted string representation of the fuel composition.
# @return oxidizer_name_str : Formatted string representation of the oxidizer composition.
# @return mechanism_names   : List of mechanism names extracted from mechanisms_dict.
def Prepare_simulation_inputs(fuel_list, oxidizer_list, mechanisms_dict):
    # Convert lists to dictionaries
    fuel_dict = list_to_dict(fuel_list)
    oxidizer_dict = list_to_dict(oxidizer_list)
    
    # Format dictionaries into strings for naming or file saving
    fuel_name_str = format_dict_components(fuel_dict, separator="_")
    oxidizer_name_str = format_dict_components(oxidizer_dict, separator="_")
    
    # Extract mechanism names
    mechanism_names = [mech_name for mech_name in mechanisms_dict.keys()]
    
    return fuel_dict, oxidizer_dict, fuel_name_str, oxidizer_name_str, mechanism_names
