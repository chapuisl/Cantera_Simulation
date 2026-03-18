"""
# ===================================================================================================================
#  Cantera Simulation Mechanism Loader
# ===================================================================================================================
#
#  Author          : Lilian CHAPUIS
#  Affiliation     : IMFT - Institut de Mécanique des Fluides de Toulouse
#  Location        : Toulouse, France
#  Creation Date   : 17 February 2026
#  Last Modified   : 18 February 2026
#  Version         : 1.0.01
#
# -------------------------------------------------------------------------------------------------------------------
#  DESCRIPTION
# -------------------------------------------------------------------------------------------------------------------
#  This function provides a centralized registry of kinetic mechanisms that can be used in Cantera-based
#  combustion simulations. Kinetic mechanisms define the set of chemical reactions and associated rate 
#  parameters that describe how fuel and oxidizer react under specific thermodynamic conditions. 
#
#  By calling this function, a dictionary that maps a short, user-friendly name for each mechanism 
#  to the file path of its corresponding YAML file. These YAML files contain all 
#  necessary chemical species, reactions, and rate constants required by Cantera to perform simulations.
#
#  Key features:
#    - Simplifies mechanism selection for simulations.
#    - Supports both standard mechanisms (e.g., GRI30 for methane) and custom mechanisms (e.g., ZHU24 or SANDIEGO).
#    - Returns a dictionary for programmatic access, enabling dynamic mechanism loading in scripts.
#
#  Example mechanisms included:
#    - "GRI30"     : widely used methane combustion mechanism ('gri30.yaml')
#    - "h2o2"      : simplified hydrogen oxidation mechanism ('h2o2.yaml')
#    - "ZHU24"     : custom Zhu 24-reaction mechanism (local full path)
#    - "SANDIEGO"  : custom San Diego mechanism (local full path)
#
#  Typical usage:
#    mechanisms = Kinetic_mechanism()
#    file_path = mechanisms["GRI30"]
#
#  This approach promotes reproducibility, reduces the risk of path errors, and allows simulations 
#  to easily switch between different chemical kinetics models.
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

def Kinetic_mechanism():
    available_mechanisms = {
        "GRI30": "gri30.yaml",
        "h2o2": "h2o2.yaml",
        "ZHU24": "/Users/lilian_chapuis/Documents/01-ProjetGit/00-Chemical_Kinetics/Zhu_mechanism/NH3_43_312_Zhu2024.yaml",
        "SANDIEGO": "/Users/lilian_chapuis/Documents/01-ProjetGit/00-Chemical_Kinetics/San_diego_mechanism/H2_9_21_San_diego.yaml",
        "STAGNI25": "/Users/lilian_chapuis/Documents/01-ProjetGit/00-Chemical_Kinetics/Stagni_NH3_2025/NH3_34_272_Stagni2025.yaml",
        "STAGNI20": "/Users/lilian_chapuis/Documents/01-ProjetGit/00-Chemical_Kinetics/Stagni_NH3_2020/NH3_31_203_Stagni2020.yaml",
    }
    return available_mechanisms

#  STAGNI20: Kinetic mechanism of Ammonia pyrolysis and oxidation
#            31 species 203 reactions
#            elements: [C, H, N, O, Ar, He]
#            species: [AR, N2, HE, H2, H, O2, O, H2O, OH, H2O2, HO2, NO, N2O, NO2, HNO, HNO2, HONO, HONO2, N2H2,
#                      H2NN, NH2OH, HNOH, NH3, N2H4, N, NO3, NH, NNH, NH2, H2NO, N2H3]
#
#  
#  STAGNI25: Kinetic mechanism of Ammonia/hydrogen pyrolysis and oxidation
#            34 species 272 reactions
#            elements: [C, H, O, N, He, Ar] 
#            species: [AR, N2, HE, H2, H, O2, O, H2O, OH, H2O2, HO2, OHV, NO, N2O,  NO2, HNO, HNO2, HONO, HONO2, 
#                      N2H2, H2NN, NH2OH, HNOH, NH3, N2H4, N, NO3, NH, NNH, NH2, H2NO, N2H3, cHNNO, tHNNO]
#
#
#  ZHU24:  Kinetic mechanism of Ammonia, NH3 oxidation and related reactions, NOx formation related reactions
#          43 species 312 reactions
#          elements: [C, H, O, N, Ar, He]
#          species: [H2O, NH3, NO, N2O, N2, O2, H2, NO2, AR, HE, H, O, OH, HO2, H2O2, OHV, NH2, NH, N, N2H4, N2H3,
#                     N2H2, H2NN, NNH, NO3, HNO, HON, H2NO, HNOH, NH2OH, HONO, HNO2, HONO2, t-ONNH, c-ONNH, ONHN, 
#                     H2NNO2, t-HNN(O)OH, c-HNN(O)OH, CO, CO2, CH4, C2H6]
#
#
# SANDIEGO: Kinetic mechanism of H2
#           9 species 21 reactions
#           elements: [N, H, O, C]
#           species: [H2, H, O2, OH, O, H2O, HO2, H2O2, N2]