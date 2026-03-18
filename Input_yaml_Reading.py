"""
# ===================================================================================================================
#  Cantera INPUT Code Reading
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
#  This file reads and parses a YAML input configuration file for Cantera-based combustion simulations.
#
# It provides a main function that:
#    - Reads a user-specified YAML configuration file,
#    - Validates and extracts essential parameters,
#    - Returns a structured dictionary containing:
#        * Simulation type
#        * Mixture composition (Fuel, Oxidizer)
#        * Thermodynamic conditions (pressure, initial temperature, etc.)
#        * Kinetic mechanism used
#       * Output and post-processing options
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
from Available_Kinetic_MECH import Kinetic_mechanism 

"""
# ===================================================================================================================
#  Import library
# ===================================================================================================================
"""
from colorama import Fore,Style
import cantera as ct
import numpy as np
import time
import yaml
import sys

"""
# ===================================================================================================================
#  Function
# ===================================================================================================================
"""


# Converts input dictionary into a simple Python list.
#
# @param param : dict with a "mode" field ("single", "list", or "linspace")
# @param name  : name for error messages (str)
#
# @return : list of values based on mode:
#          - "single"  -> [value]
#          - "list"    -> values as list
#          - "linspace" -> evenly spaced values from start to end
# Exits if input is invalid or mode is unknown.
def parse_range(param, name="unknown"):
    if not isinstance(param, dict):
        print(Fore.RED + f" ERROR: {name} must be a dictionary with a 'mode' field.")
        sys.exit(0)
    mode = param.get("mode")

    if mode == "single":
        return [param["value"]]

    elif mode == "list":
        return list(param["values"])

    elif mode == "linspace":
        start = param["start"]
        end = param["end"]
        points = param["points"]
        if points < 2:
            return [start]
        step = (end - start) / (points - 1)
        return [start + i * step for i in range(points)]
    else:
        print(Fore.RED + f" ERROR: {name}: Unknown mode '{mode}")
        sys.exit(0)


# Formats a list of chemical species for Cantera mixtures (fuel or oxidizer).
#
# @param species_list : list of dicts with keys "species" (str) and "fraction" (float)
# @param name         : name for error messages (str)
#
# @return : single [species, fraction] if one species, else list of [species, fraction] pairs
# Exits if input is invalid.
def format_mixture_species(species_list, name="mixture"):

    if not isinstance(species_list, list):
        print(Fore.RED + f" ERROR: {name} must be a list")
        sys.exit(0)

    formatted = []

    for sp in species_list:

        if "species" not in sp or "fraction" not in sp:
            print(Fore.RED + f" ERROR: {name} ntries must contain 'species' and 'fraction'")
            sys.exit(0)

        formatted.append([sp["species"], sp["fraction"]])

    # If only one species → return simple list
    if len(formatted) == 1:
        return formatted[0]

    return formatted


# Reads and validates a YAML parameter file for the simulation.
#
# @param parameter_coupling : path to YAML file containing calculation variables
#
# @return : dict with all validated parameters, including:
#          - simulation_type : dict
#          - fuel            : list of [species, fraction]
#          - oxidizer        : list of [species, fraction]
#          - outputs          : output settings
#          - conditions       : parsed conditions with ranges
#          - mechanisms       : Cantera Solution objects
#          - save_plot        : bool
#
# Exits if required fields are missing or have invalid types.
def check_file_Parameters_yaml(parameter_coupling):

    print(f"\t\t > Reading file: {parameter_coupling}")

    with open(parameter_coupling, "r") as f:
        config = yaml.safe_load(f)
        
    simulation_type    = config["simulation"]["type"]
    path_file          = config["output"]
    fuel_raw           = config["mixture"]["fuel"]
    oxidizer_raw       = config["mixture"]["oxidizer"]
    fuel               = format_mixture_species(fuel_raw, name="fuel")
    oxidizer           = format_mixture_species(oxidizer_raw, name="oxidizer")
    outputs            = config["outputs"]
    save_plot          = config["post_processing"]["save_plots"]
    verbosity_level    = config["post_processing"]["verbosity_level"]
    
    Major_species          = config["outputs"]["Counter_flow"]["Major_species"]
    Radicals               = config["outputs"]["Counter_flow"]["Radicals"]
    
    if verbosity_level not in [0,1,2,3]:
        print(Fore.RED + " ERROR: verbosity level must be 0 or 1 or 2 or 3")
        sys.exit(0)

    if not isinstance(simulation_type, dict):
        print(Fore.RED + " ERROR: simulation.type must be a dictionary")
        sys.exit(0)
        
    if not isinstance(fuel, list):
        print(Fore.RED + " ERROR: mixture.fuel must be a list")
        sys.exit(0)

    if not isinstance(oxidizer, list):
        print(Fore.RED + " ERROR: mixture.oxidizer must be a list")
        sys.exit(0)
        
    if not isinstance(save_plot, bool):
        print(Fore.RED + " ERROR: post_processing.save_plots must be bool")
        sys.exit(0)
    
    # Load mechanisms
    mechanisms = {}
    kinetics_section = config["kinetics"]
    
    available_mechanisms = Kinetic_mechanism()
    for key, mech_name in kinetics_section.items():
        
        if not key.startswith("mechanism"):
            print(Fore.RED + f" ERROR: Invalid kinetics key: {key}")
            sys.exit(0)
    
        if mech_name not in available_mechanisms:
            print(Fore.RED + f"ERROR: Unknown mechanism: {mech_name}")
            sys.exit(0)
    
        mechanisms[mech_name] = available_mechanisms[mech_name]

    parsed_conditions = {}

    for case_name, case_values in config["conditions"].items():
        parsed_conditions[case_name] = {}
        for param_name, param_value in case_values.items():

            # Special counter-flow pairs
            if param_name in ["Temperature_pairs", "Velocity_flux_pairs"]:
                parsed_conditions[case_name][param_name] = np.array(param_value)

            else:
                parsed_conditions[case_name][param_name] = parse_range(
                    param_value,
                    name=f"{case_name}.{param_name}"
                )

    return {
        "simulation_type": simulation_type,
        "path_file": path_file,
        "fuel": fuel,
        "oxidizer": oxidizer,
        "outputs": outputs,
        "conditions": parsed_conditions,
        "mechanisms": mechanisms,
        "save_plot": save_plot,
        "verbosity_level": verbosity_level
    }
