"""
# ===================================================================================================================
#  Cantera PostProcessing file:
# ===================================================================================================================
#
#  Author          : Lilian CHAPUIS
#  Affiliation     : IMFT - Institut de Mécanique des Fluides de Toulouse
#  Location        : Toulouse, France
#  Creation Date   : 18 February 2026
#  Last Modified   : 20 February 2026
#  Version         : 1.0.01
#
# -------------------------------------------------------------------------------------------------------------------
#  DESCRIPTION
# -------------------------------------------------------------------------------------------------------------------
#  This module provides a structured post-processing framework for combustion simulations performed 
#  with Cantera_proc.py
#
#  It reads simulation results stored in CSV format, automatically organizes output
#  directories, and generates consistent, publication-ready visualizations.
#
#  The module is designed to:
#      - Handle multiple kinetic mechanisms
#      - Process parametric studies (temperature, pressure, equivalence ratio, etc.)
#      - Extract thermochemical, transport, and combustion-related quantities
#      - Produce comparative graphical analyses
#
#  It ensures reproducibility, structured data management, and automated visualization
#  of combustion simulation results within the associated research framework.
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
from Global_plot_figure import plot_evolution
from Common_Utils_tools import create_folder
import Graphic_Configuration as GC 

"""
# ===================================================================================================================
#  Import library
# ===================================================================================================================
"""
import cantera as ct
import numpy as np
import copy
import csv
import sys
import os

"""
# ===================================================================================================================
#  Function
# ===================================================================================================================
"""


def PostProcess_Flame1D(mechanisms, MECH, Fuel_name, Oxi_name, configuration, file_path_csv,file_path_plot,file_path_species_plot,Save_plot):
    COLOR = GC.Black_Purple()
    GC.config_plot()
    
    
    Temperature      = configuration["conditions"]["Flame_1D"]["Temperature"]
    Pressure         = configuration["conditions"]["Flame_1D"]["Pressure"]
    Equivalent_Ratio = configuration["conditions"]["Flame_1D"]["Phi"]
    
    AVBP_sol         = configuration["outputs"]["Flame_1D"]["save_AVBP_solution"]
    Flame_speed      = configuration["outputs"]["Flame_1D"]["flame_speed"]
    Flame_Time       = configuration["outputs"]["Flame_1D"]["flame_time"]
    Flame_thickness  = configuration["outputs"]["Flame_1D"]["flame_thickness"]
    Emissions        = configuration["outputs"]["Flame_1D"]["emissions"]
    
    Major_species    = configuration["outputs"]["Flame_1D"]["Major_species"]
    Radicals         = configuration["outputs"]["Flame_1D"]["Radicals"]
    
    for indexT, T in enumerate(Temperature):
        path_T = create_folder(file_path_plot, f"{indexT:02}-Initial_Temperature_{T:.2f}K")
        path_T_spe = create_folder(file_path_plot, f"{indexT:02}-Initial_Temperature_{T:.2f}K")
        file_path_flame_prop = create_folder(path_T, "00-Flame_Property_Evolution")
    
       
        for indexP,P in enumerate(Pressure):
            path_P = create_folder(path_T, f"{indexP:02}-Initial_Pressure_{P:.2f}bars")
            path_P_spe = create_folder(file_path_species_plot, f"{indexP:02}-Initial_Pressure_{P:.2f}bars")
    
            Speed_list     = []
            Thickness_list = []
            Time_list      = []
            Da_list        = []

    
            for mech_name in mechanisms:
                mech_index = list(mechanisms.keys()).index(mech_name)
    
                csv_path = os.path.join(
                    file_path_csv,
                    f"{mech_index:02}-Kinetic_Mechanism_Used-{mech_name}",
                    f"{indexT:02}-Initial_Temperature_{T:.2f}K",
                    f"{indexP:02}-Initial_Pressure_{P:.2f}bars",
                    f"results_{mech_name}_Species_Fuel{Fuel_name}_Oxidizer{Oxi_name}_at_T{T:.2f}_P{P:.2f}.csv"
                )
                
                with open(csv_path, mode='r') as csv_file:
                    reader = csv.DictReader(csv_file)
                    Sl, Th, Ti, Da = [], [], [], []
                    for row in reader:
                        Sl.append(float(row["Flame Speed [m/s]"]))
                        Th.append(float(row["Flame Thickness [mm]"]))
                        Ti.append(float(row["Flame Time [ms]"]))
                        Da.append(float(row["Damkohler [-]"]))
                        
                    Speed_list.append(Sl)
                    Thickness_list.append(Th)
                    Time_list.append(Ti)
                    Da_list.append(Da)

        
            # ---------- PLOTS ----------
            print(f"\t  -> PROCESSING: Flame_Property_Evolution")

            if Flame_speed:
                plot_evolution(
                    Equivalent_Ratio, Speed_list, MECH, COLOR,
                    ylabel="Flame speed [m/s]",
                    xlabel="Equivalent ratio [phi]",
                    save_fig=Save_plot,
                    save_path=file_path_flame_prop,
                    name_fig=f"Flame_Speed_evolution_for_Fuel{Fuel_name}_Oxidizer{Oxi_name}_at_T_{T:.2f}K_and_P_{P:.2f}bars",
                    marker='o'
                )
    
            if Flame_thickness:
                plot_evolution(
                    Equivalent_Ratio, Thickness_list, MECH, COLOR,
                    ylabel="Flame Thickness [mm]",
                    xlabel="Equivalent ratio [phi]",
                    save_fig=Save_plot,
                    save_path=file_path_flame_prop,
                    name_fig=f"Flame_Thickness_evolution_for_Fuel{Fuel_name}_Oxidizer{Oxi_name}_at_T_{T:.2f}K_and_P_{P:.2f}bars",
                    marker='o'
                )
    
            if Flame_Time:
                plot_evolution(
                    Equivalent_Ratio, Time_list, MECH, COLOR,
                    ylabel="Flame Time [ms]",
                    xlabel="Equivalent ratio [phi]",
                    save_fig=Save_plot,
                    save_path=file_path_flame_prop,
                    name_fig=f"Flame_Time_evolution_for_Fuel{Fuel_name}_Oxidizer{Oxi_name}_at_T_{T:.2f}K_and_P_{P:.2f}bars",
                    marker='o'
                )
    
                plot_evolution(
                    Equivalent_Ratio, Da_list, MECH, COLOR,
                    ylabel="Flame Damkohler number [-]",
                    xlabel="Equivalent ratio [phi]",
                    save_fig=Save_plot,
                    save_path=file_path_flame_prop,
                    name_fig=f"Fuel_Damkohler_Number_evolution_for_Fuel{Fuel_name}_Oxidizer{Oxi_name}_at_T_{T:.2f}K_and_P_{P:.2f}bars",
                    marker='o'
                )
            for indexPhi, eq_ratio in enumerate(Equivalent_Ratio):
                P_eq_path = create_folder(path_P, f"{indexPhi:02}-Equivalent_ratio_Phi-{eq_ratio:.2f}")
                P_eq_path_spe = create_folder(path_P_spe, f"{indexP:02}-Initial_Pressure_{P:.2f}bars")
                print(f"\t  -> PROCESSING: Pressure {P:.2f} bar / Temeperature {T:.2f} K/  Equivalent Ratio {eq_ratio:.2f}")
                
                Grid_list          = []
                Temperature_list   = []
                HRR_list           = []
                U_flame_list       = []
                Rho_flame_list     = []
                Cp_list            = []
                Lambda_list        = []
                Mu_list            = []
                dTdx_list          = []
                species_Y = {}
                species_X = {}
                
                for mech_name in mechanisms:
                    mech_index = list(mechanisms.keys()).index(mech_name)
                    species_Y_mech = {}
                    species_X_mech = {}
                    
                    csv_path = os.path.join(
                        file_path_csv,
                        f"{mech_index:02}-Kinetic_Mechanism_Used-{mech_name}",
                        f"{indexT:02}-Initial_Temperature_{T:.2f}K",
                        f"{indexP:02}-Initial_Pressure_{P:.2f}bars",
                        f"{indexPhi:02}-Equivalent_ratio_Phi-{eq_ratio:.2f}",
                        f"species_results_{mech_name}_Species_Fuel{Fuel_name}_Oxidizer{Oxi_name}_at_T{T:.2f}_P{P:.2f}_Phi{eq_ratio:.2f}.csv")
                    
                    with open(csv_path, mode='r') as csv_file:
                        reader = csv.DictReader(csv_file, delimiter=';')
            
                        Grid, Temp, HRR, dTdx = [], [], [], []
                        U, Rho = [], []
                        Cp, Lambda, Mu = [], [], []
                        
                        # dictionnaire pour stocker toutes les espèces automatiquement
                        
            
                        for row in reader:
            
                            Grid.append(float(row["Grid [m]"]) * 1e3)
                            Temp.append(float(row["Temperature [K]"]))
                            HRR.append(float(row["Heat Release [W/m3]"]))
                            U.append(float(row["Axial Velocity [m/s]"]))
                            Rho.append(float(row["Density [kg/m3]"]))
            
                            dTdx.append(float(row["dT/dx [K/m]"]))
                            Cp.append(float(row["cp [J/kg/K]"]))
                            Lambda.append(float(row["Thermal Conductivity [W/m/K]"]))
                            Mu.append(float(row["Viscosity [Pa.s]"]))
                            
                            
                            for key in row.keys():
                                if key.startswith("Y_"):
                                    if key not in species_Y_mech:
                                        species_Y_mech[key] = []
                                    species_Y_mech[key].append(float(row[key]))
                
                                if key.startswith("X_"):
                                    if key not in species_X_mech:
                                        species_X_mech[key] = []
                                    species_X_mech[key].append(float(row[key]))
                            
                        Grid_list.append(Grid)
                        Temperature_list.append(Temp)
                        HRR_list.append(HRR)
                        U_flame_list.append(U)
                        Rho_flame_list.append(Rho)
                
                        dTdx_list.append(dTdx)
                        Cp_list.append(Cp)
                        Lambda_list.append(Lambda)
                        Mu_list.append(Mu)
                        
                        for key in species_Y_mech:
                            if key not in species_Y:
                                species_Y[key] = []
                            species_Y[key].append(species_Y_mech[key])
                    
                        for key in species_X_mech:
                            if key not in species_X:
                                species_X[key] = []
                            species_X[key].append(species_X_mech[key])
                            
                Temp = Temperature_list[0]
                Grid = Grid_list[0]
                dTdx = np.gradient(Temp, Grid)
                
                i_max = np.argmax(np.abs(dTdx))
                x_flame = Grid[i_max]
                
                delta_T = np.max(Temp) - np.min(Temp)
                max_grad = np.max(np.abs(dTdx))
                flame_thickness = delta_T / max_grad
                
                x_left  = x_flame - 1 * flame_thickness
                x_right = x_flame + 5 * flame_thickness
                               
                print("\t \t -> PROCESSING: BASIC PLOT EVOLUTION")    
                plot_evolution(
                    Grid_list , Temperature_list, MECH, COLOR,
                    ylabel="Temperature [K]",
                    xlabel="Distance [mm]",
                    x_limit_left= x_left, 
                    x_limit_right= x_right,
                    secondary_data=HRR_list, 
                    secondary_ylabel="HRR [W/m3] -- ",        
                    save_fig=Save_plot,
                    save_path=P_eq_path,
                    name_fig=f"Temperature_HRR_diffusion_flame_evolution_for_Fuel{Fuel_name}_Oxidizer{Oxi_name}_at_T{T:.2f}_and_P_{P:.2f}bars",
                    # marker='o'
                )
                
                plot_evolution(
                    Grid_list , Temperature_list, MECH, COLOR,
                    ylabel="Temperature [K]",
                    xlabel="Distance [mm]",
                    x_limit_left= x_left, 
                    x_limit_right= x_right,
                    # secondary_data=Z_list, 
                    # secondary_ylabel="Mixture fraction -- ",        
                    save_fig=Save_plot,
                    save_path=P_eq_path,
                    name_fig=f"Temperature_MixtureFraction_diffusion_flame_evolution_for_Fuel{Fuel_name}_Oxidizer{Oxi_name}_at_T{T:.2f}_and_P_{P:.2f}bars",
                    # marker='o'
                )
                
                plot_evolution(
                    Grid_list , HRR_list, MECH, COLOR,
                    ylabel="HRR [W/m3]",
                    xlabel="Distance [mm]",
                    x_limit_left= x_left, 
                    x_limit_right= x_right,
                    # secondary_data=Z_list, 
                    # secondary_ylabel="Mixture frqction -- ",        
                    save_fig=Save_plot,
                    save_path=P_eq_path,
                    name_fig=f"HRR_MixtureFraction_diffusion_flame_evolution_for_Fuel{Fuel_name}_Oxidizer{Oxi_name}_at_T{T:.2f}_and_P_{P:.2f}bars",
                    # marker='o'
                )
                
                plot_evolution(
                    Grid_list , Temperature_list, MECH, COLOR,
                    ylabel="Temperature [K]",
                    xlabel="Distance [mm]",
                    x_limit_left= x_left, 
                    x_limit_right= x_right,
                    secondary_data=Rho_flame_list, 
                    secondary_ylabel="Density [kg/m3] -- ",
                    save_fig=Save_plot,
                    save_path=P_eq_path,
                    name_fig=f"Temperature_RHO_diffusion_flame_evolution_for_Fuel{Fuel_name}_Oxidizer{Oxi_name}_at_T{T:.2f}_and_P_{P:.2f}bars",
                    # marker='o'
                )
                
                plot_evolution(
                    Grid_list , U_flame_list, MECH, COLOR,
                    ylabel="Axial Velocity [m/s]",
                    xlabel="Distance [mm]",
                    x_limit_left= x_left, 
                    x_limit_right= x_right,
                    # secondary_data= Strain_list, 
                    # secondary_ylabel="Strain [1/s] -- ",
                    save_fig=Save_plot,
                    save_path=P_eq_path,
                    name_fig=f"Axial_velocity_Strain_diffusion_flame_evolution_for_Fuel{Fuel_name}_Oxidizer{Oxi_name}_at_T{T:.2f}_and_P_{P:.2f}bars",
                    # marker='o'
                )
                
                plot_evolution(
                    Grid_list , Temperature_list, MECH, COLOR,
                    ylabel="Temperature [K]",
                    xlabel="Distance [mm]",
                    x_limit_left= x_left, 
                    x_limit_right= x_right,
                    # secondary_data= Strain_list, 
                    # secondary_ylabel="Strain [1/s] -- ",
                    save_fig=Save_plot,
                    save_path=P_eq_path,
                    name_fig=f"Temeperature_Strain_diffusion_flame_evolution_for_Fuel{Fuel_name}_Oxidizer{Oxi_name}_at_T{T:.2f}_and_P_{P:.2f}bars",
                    # marker='o'
                )
                
                if Emissions is True:
                    print("\t \t -> PROCESSING: SPECIES PLOT EVOLUTION")  
                    print("\t \t \t -> PROCESSING: EACH SPECIES PLOT EVOLUTION")  
                    for key in species_Y:
                            k = key.split("_")[1]
                            if len(Grid_list) > len(species_Y[key]):
                                Grid_inter    = []
                                MECH_inter    = []
                                SPECIES_inter = []

                                for i in range(len(species_Y[key])):
                                    for j in range(len(Grid_list)):
                                        if len(Grid_list[j]) == len(species_Y[key][i]):
                                            Grid_inter.append(Grid_list[j])
                                            MECH_inter.append(MECH[j])
                                            SPECIES_inter.append(species_Y[key][i])
                            else:
                                Grid_inter = copy.deepcopy(Grid_list)
                                MECH_inter = copy.deepcopy(MECH)
                                SPECIES_inter = copy.deepcopy(species_Y[key])
                                
                            if k in Major_species:
                                plot_evolution(
                                    Grid_inter , SPECIES_inter, MECH_inter, COLOR,
                                    ylabel=f"Mass fraction [{key}]",
                                    xlabel="Distance [mm]",
                                    x_limit_left= x_left, 
                                    x_limit_right= x_right,
                                    save_fig=Save_plot,
                                    save_path=P_eq_path_spe,
                                    name_fig=f"{key}_Mass_fraction_diffusion_flame_evolution_for_Fuel{Fuel_name}_Oxidizer{Oxi_name}_at_T{T:.2f}_and_P_{P:.2f}bars",
                                    # marker='o'
                                    )
                            elif k in Radicals:
                                plot_evolution(
                                    Grid_inter , SPECIES_inter, MECH_inter, COLOR,
                                    ylabel=f"Mass fraction [{key}]",
                                    xlabel="Distance [mm]",
                                    x_limit_left= x_left, 
                                    x_limit_right= x_right,
                                    type_y_scale='log',
                                    save_fig=Save_plot,
                                    save_path=P_eq_path_spe,
                                    name_fig=f"{key}_Mass_fraction_diffusion_flame_evolution_for_Fuel{Fuel_name}_Oxidizer{Oxi_name}_at_T{T:.2f}_and_P_{P:.2f}bars",
                                    # marker='o'
                                    )
                                
                    for key in species_X:
                            k = key.split("_")[1]
                            if len(Grid_list) > len(species_X[key]):
                                Grid_inter    = []
                                MECH_inter    = []
                                SPECIES_inter = []

                                for i in range(len(species_X[key])):
                                    for j in range(len(Grid_list)):
                                        if len(Grid_list[j]) == len(species_X[key][i]):
                                            Grid_inter.append(Grid_list[j])
                                            MECH_inter.append(MECH[j])
                                            SPECIES_inter.append(species_X[key][i])
                                            
                                
                            else:
                                Grid_inter = copy.deepcopy(Grid_list)
                                MECH_inter = copy.deepcopy(MECH)
                                SPECIES_inter = copy.deepcopy(species_X[key])
                                
                            
                            if k in Major_species:
                                plot_evolution(
                                    Grid_inter , SPECIES_inter, MECH_inter, COLOR,
                                    ylabel=f"Molar fraction [{key}]",
                                    xlabel="Distance [mm]",
                                    x_limit_left= x_left, 
                                    x_limit_right= x_right,
                                    save_fig=Save_plot,
                                    save_path=P_eq_path_spe,
                                    name_fig=f"{key}_Molar_fraction_diffusion_flame_evolution_for_Fuel{Fuel_name}_Oxidizer{Oxi_name}_at_T{T:.2f}_and_P_{P:.2f}bars",
                                    # marker='o'
                                    )
                            elif k in Radicals:
                                X_ppm = [[val * 1e6 for val in sublist] for sublist in SPECIES_inter]
                                plot_evolution(
                                    Grid_inter , X_ppm, MECH_inter, COLOR,
                                    ylabel=f"Molar fraction [{key} ppm]",
                                    xlabel="Distance [mm]",
                                    x_limit_left= x_left, 
                                    x_limit_right= x_right,
                                    save_fig=Save_plot,
                                    save_path=P_eq_path_spe,
                                    name_fig=f"{key}_Molar_fraction_diffusion_flame_evolution_for_Fuel{Fuel_name}_Oxidizer{Oxi_name}_at_T{T:.2f}_and_P_{P:.2f}bars",
                                    # marker='o'
                                    )
                         
                    mech_index = 0            
                    for mech_name, mech_file in mechanisms.items():
                        print("\t \t \t -> PROCESSING: COUPLED SPECIES PLOT EVOLUTION")  
                        
                        
                        gas = ct.Solution(mech_file)
                        species_mech = gas.species_names
                        
                        path_T_CF_Mass_P_mech_spe = create_folder(
                            P_eq_path_spe,
                            f"{mech_index:02}-Kinetic_Mechanism_Used-{mech_name}"
                        )
                    
                        Grid = Grid_list[mech_index]
                    
                        def split_species(species_dict):
                            Maj, Rad = [], []
                            name_Maj, name_Rad = [], []
                    
                            for key, values in species_dict.items():
                                
                                k = key.split("_")[1]
                                if k in Major_species and k in species_mech:
                                    if len(values) >= mech_index+1 : 
                                        name_Maj.append(key)
                                        Maj.append(values[mech_index])
                                elif k in Radicals and k in species_mech:
                                    if len(values) >= mech_index+1 :
                                        name_Rad.append(key)
                                        Rad.append(values[mech_index])         
                            return Maj, Rad, name_Maj, name_Rad
                    
                        # Mass fractions
                        Maj_Y, Rad_Y, name_key_Maj, name_key_Rad = split_species(species_Y)
                    
                        # Molar fractions
                        Maj_X, Rad_X, _, _ = split_species(species_X)
                    
                        base_name = (
                            f"{mech_name}_{{}}_diffusion_flame_evolution_for_"
                            f"Fuel{Fuel_name}_Oxidizer{Oxi_name}_"
                            f"at_T{T:.2f}_and_P_{P:.2f}bars"
                        )
                    
                        plots = [
                            (Maj_Y, name_key_Maj, "Mass fraction ", "Mass_fraction_Major_species"),
                            (Rad_Y, name_key_Rad, "Mass fraction ", "Mass_fraction_Radical_species"),
                            (Maj_Y + Rad_Y, name_key_Maj + name_key_Rad, "Mass fraction ", "Mass_fraction_Total_species"),
                            (Maj_X, name_key_Maj, "Molar fraction ", "Molar_fraction_Major_species"),
                            (Rad_X, name_key_Rad, "Molar fraction ", "Molar_fraction_Radical_species"),
                        ]
    
                        for data, labels, ylabel, suffix in plots:
                            plot_evolution(
                                Grid,
                                data,
                                labels,
                                COLOR,
                                ylabel=ylabel,
                                xlabel="Distance [mm]",
                                x_limit_left=x_left,
                                x_limit_right=x_right,
                                save_fig=Save_plot,
                                save_path=path_T_CF_Mass_P_mech_spe,
                                name_fig=base_name.format(suffix),
                            )
                        mech_index +=1
                    print()

def PostProcess_Temperature_Adiabatic(mechanisms, MECH, Fuel_name, Oxi_name, configuration, file_path_csv,file_path_plot,Save_plot):
    COLOR = GC.Black_Purple()
    GC.config_plot()
    
    
    Temperature      = configuration["conditions"]["Temperature_Adiabatic"]["Temperature"]
    Pressure  = configuration["conditions"]["Temperature_Adiabatic"]["Pressure"]
    Equivalent_Ratio = configuration["conditions"]["Temperature_Adiabatic"]["Phi"]
    
    Final_Temperature    = configuration["outputs"]["Temperature_Adiabatic"]["Final_Temperature"]
    Final_density        = configuration["outputs"]["Temperature_Adiabatic"]["Final_density"]
    Final_Enthalpy       = configuration["outputs"]["Temperature_Adiabatic"]["Final_Enthalpy"]
    
    for indexT,T in enumerate(Temperature):
        file_path_Adiabatic_Temperature = create_folder(file_path_plot, f"{indexT:02}-Initial_Temperature_{T:.2f}K") 
        
        
        for indexP,P in enumerate(Pressure):
            print(f"\t  -> PROCESSING: Pressure {P:.2f} bar / Temeperature {T:.2f} K")
            file_path_Adiabatic_Temperature_P = create_folder(file_path_Adiabatic_Temperature, f"{indexP:02}-Initial_Pressure_{P:.2f}bars") 
            Temperature_list           = []
            Enthalpy_Init_list         = []
            Enthalpy_Final_list        = []
            Enthalpy_Conseration_list  = []
            Density_list               = []
            
            PhimaxPhi                  = []
            orientationPhi             = []
            
            for mech_name in mechanisms:
                mech_index=list(mechanisms.keys()).index(mech_name)
                csv_file_path=os.path.join(file_path_csv,f"{mech_index:02}-Kinetic_Mechanism Used-{mech_name}",
                                                               f"{indexT:02}-Initial_Temperature_{T:.2f}K",
                                                               f"{Pressure.index(P):02}-Initial_Pressure_{P:.2f}bars",
                                                               f"results_{mech_name}_Species_Fuel{Fuel_name}_Oxidizer{Oxi_name}_at_T{T:.2f}K_P{P:.2f}.csv")
                with open(csv_file_path, mode='r') as csv_file:
                    reader = csv.DictReader(csv_file, delimiter=';')
                    Temp, Rho, H_init, H_final = [], [], [], []
                    for row in reader:
                        Temp.append(float(row["Adiabatic Temperature [K]"]))
                        Rho.append(float(row["Density [kg/m3]"]))
                        H_init.append(float(row["Initial Enthalpy [J/kg]"]))
                        H_final.append(float(row["Final Enthalpy [J/kg]"]))
                       
                    Temperature_list.append(Temp)
                    Enthalpy_Init_list.append(H_init)
                    Enthalpy_Final_list.append(H_final)
                    Enthalpy_Conseration_list.append([abs(H_final[i]-H_init[i])/H_final[i] *100 for i in range(len(H_init))])
                    Density_list.append(Rho)
                    
                    PhimaxPhi.append(Equivalent_Ratio[Temp.index(np.max(Temp))])
                    orientationPhi.append('V')
                
                
            if Final_Temperature is True:
                plot_evolution(Equivalent_Ratio, data=Temperature_list,
                                       labels=MECH,
                                       colors=COLOR,
                                       ylabel= " Temperature [K]",
                                       xlabel= r"Equivalent ratio [phi]",
                                       line_value=PhimaxPhi, line_orientation=orientationPhi, 
                                       plot_fig = False ,
                                       save_fig = Save_plot, 
                                       save_path = file_path_Adiabatic_Temperature_P,
                                       name_fig = f"Adiabatic_Temperature_evolution_for_Fuel{Fuel_name}_Oxidizer{Oxi_name}_at_Initial_Temp_of_{T:.2f}_and_P_{P:.2f}bars",
                                       # marker = 'o'
                                       )
            
            if Final_Enthalpy is True:
                plot_evolution(Equivalent_Ratio, data=Enthalpy_Conseration_list,
                                       labels=MECH,
                                       colors=COLOR,
                                       ylabel= "Percentage [%]",
                                       xlabel= r"Equivalent ratio [phi]",
                                       plot_fig = False ,
                                       save_fig = Save_plot, 
                                       save_path = file_path_Adiabatic_Temperature_P,
                                       name_fig = f"Percentage_divergence_Enthalpy_Conservation_evolution_for_Fuel{Fuel_name}_Oxidizer{Oxi_name}_at_Initial_Temp_of_{T:.2f}_and_P_{P:.2f}bars",
                                       marker = 'o'
                                       )
                
                plot_evolution(Equivalent_Ratio, data=Enthalpy_Final_list,
                                       labels=MECH,
                                       colors=COLOR,
                                       ylabel= "Enthalpy [J/kg]",
                                       xlabel= r"Equivalent ratio [phi]",
                                       plot_fig = False ,
                                       save_fig = Save_plot, 
                                       save_path = file_path_Adiabatic_Temperature_P,
                                       name_fig = f"Enthalpy_evolution_for_Fuel{Fuel_name}_Oxidizer{Oxi_name}_at_Initial_Temp_of_{T:.2f}_and_P_{P:.2f}bars",
                                       marker = 'o'
                                       )
    
            if Final_density is True:    
                plot_evolution(Equivalent_Ratio, data=Density_list,
                                       labels=MECH,
                                       colors=COLOR,
                                       ylabel= " Density [kg/m3]",
                                       xlabel= r"Equivalent ratio [phi]",
                                       plot_fig = False ,
                                       save_fig = Save_plot, 
                                       save_path = file_path_Adiabatic_Temperature_P,
                                       name_fig = f"Density_evolution_for_Fuel{Fuel_name}_Oxidizer{Oxi_name}_at_Initial_Temp_of_{T:.2f}_and_P_{P:.2f}bars",
                                       # marker = 'o')
                                       )
  
                   
def PostProcess_IDT(mechanisms, MECH, Fuel_name, Oxi_name, configuration, file_path_csv,file_path_plot,Save_plot):
    COLOR = GC.Black_Purple()
    GC.config_plot()
    
    Temperature       = configuration["conditions"]["Ignition_Delay_time"]["Temperature"]
    Pressure          = configuration["conditions"]["Ignition_Delay_time"]["Pressure"]
    Equivalent_Ratio  = configuration["conditions"]["Ignition_Delay_time"]["Phi"]
    
    IDT_plot           = configuration["outputs"]["Ignition_Delay_time"]["IDT_plot"]
    Time_evolution     = configuration["outputs"]["Ignition_Delay_time"]["time_evolution"]
    Complementary_plot = configuration["outputs"]["Ignition_Delay_time"]["complementary_plot"]
    
    for indexPhi, eq_ratio in enumerate(Equivalent_Ratio):
        file_path_IDT_phi = create_folder(file_path_plot, f"{indexPhi:02}-Equivalent_ratio_Phi-{eq_ratio:.2f}")
        for indexP, P in enumerate(Pressure):
            file_path_IDT_phi_P = create_folder(file_path_IDT_phi, f"{indexP:02}-Initial_Pressure_{P:.2f}bars")
            print(f"\t  -> PROCESSING: Pressure {P:.2f} bar / Equivalent Ratio phi:{eq_ratio:.2f}")
            IDT_list         = []
            Temperature_list = []
            
    
            # Pour chaque mécanisme, relire le CSV correspondant
            for mech_name in mechanisms:
                mech_index = list(mechanisms.keys()).index(mech_name)
                
                    
                csv_path = os.path.join(
                    file_path_csv,
                    f"{mech_index:02}-Kinetic_Mechanism_Used-{mech_name}",
                    f"{indexPhi:02}-Equivalent_ratio_Phi-{eq_ratio:.2f}",
                    f"{indexP:02}-Initial_Pressure_{P:.2f}bars",
                    f"results_{mech_name}_Species_Fuel{Fuel_name}_Oxidizer{Oxi_name}_at_Phi{eq_ratio:.0f}_P{P:.2f}.csv")
                
                with open(csv_path, mode='r') as csv_file:
                    reader = csv.DictReader(csv_file, delimiter=';')
                    T, IDT = [], []
                    
                    for row in reader:
                        IDT.append(float(row["IDT [ms]"]))
                        T.append(float(row["Temeperature [K]"]))
                        
                    IDT_list.append(IDT)
                    Temperature_list.append(T)
                

            if IDT_list and IDT_plot is True:
                print("\t \t  -> PROCESSING: IDT PLOT EVOLUTION")   
                plot_evolution(
                    Temperature_list,
                    data=IDT_list,
                    labels=MECH,
                    colors=COLOR,
                    type_y_scale='log',
                    ylabel=r'IDT [ms]',
                    xlabel=r'1000/T [1/K]',
                    plot_fig=False,
                    save_fig=Save_plot,
                    save_path=file_path_IDT_phi_P,
                    name_fig=f"IDT_evolution_for_Fuel{Fuel_name}_Oxidizer{Oxi_name}_at_phi_{eq_ratio:.2f}_and_P_{P:.2f}bars",
                    # marker='o'
                )
            
            for indexT, T in enumerate(Temperature):
                print(f"\t  -> PROCESSING: Pressure {P:.2f} bar / Equivalent Ratio phi:{eq_ratio:.2f} , Temperature:{T:.2f} ")
                file_path_IDT_phi_P_T = create_folder(file_path_IDT_phi_P, f"{indexT:02}-Initial_Temperature_{T:.2f}K")
                
                Time_list          = []
                Temperature_list   = []
                OH_radical_list    = []
                HRR_list           = []
                Pressure_list      = []
                
                for mech_name in mechanisms:
                    csv_path = os.path.join(
                        file_path_csv, 
                        f"{list(mechanisms.keys()).index(mech_name):02}-Kinetic_Mechanism_Used-{mech_name}",
                        f"{indexPhi:02}-Equivalent_ratio_Phi-{eq_ratio:.2f}",
                        f"{indexP:02}-Initial_Pressure_{P:.2f}bars",
                        f"{indexT:02}-Initial_Temperature_{T:.2f}K",
                        f"results_time_{mech_name}_Species_Fuel{Fuel_name}_Oxidizer{Oxi_name}_at_Phi{eq_ratio:.0f}_P{P:.2f}.csv"
                    )
                    
                    
                    with open(csv_path, mode='r') as csv_file:
                        reader = csv.DictReader(csv_file, delimiter=';')
                        Time , Temp, OH, HRR, Pres= [], [], [], [], []
                        for row in reader:
                            Time.append(float(row["Time [ms]"]))
                            Temp.append(float(row["Temperature [K]"]))
                            HRR.append(float(row["Heat Release [W/m3]"]))
                            Pres.append(float(row["Pressure [bar]"]))
                            OH.append(float(row["OH radical []"]))
                           
                            
                        Time_list.append(Time)
                        Temperature_list.append(Temp)
                        OH_radical_list.append(OH)
                        HRR_list.append(HRR)
                        Pressure_list.append(Pres)
                        
                if Time_evolution is True:    
                    file_path_IDT_phi_P_T_time  = create_folder(file_path_IDT_phi_P_T, "Time_evolution")
                    
                    plot_evolution(
                        Time_list , Temperature_list, MECH, COLOR,
                        ylabel="Temperature [K]",
                        xlabel="Time [ms]",
                        secondary_data=HRR_list, 
                        secondary_ylabel="HRR [W/m3] -- ",
                        save_fig=Save_plot,
                        save_path=file_path_IDT_phi_P_T_time,
                        name_fig=f"Temperature_evolution_for_Fuel{Fuel_name}_Oxidizer{Oxi_name}_at_T_{T:.2f}K_and_P_{P:.2f}bars",
                        # marker='o'
                    )
                    
                    plot_evolution(
                        Time_list , Pressure_list, MECH, COLOR,
                        ylabel="Pressure [bar]",
                        xlabel="Time [ms]",
                        save_fig=Save_plot,
                        save_path=file_path_IDT_phi_P_T_time,
                        name_fig=f"Pressure_evolution_for_Fuel{Fuel_name}_Oxidizer{Oxi_name}_at_T_{T:.2f}K_and_P_{P:.2f}bars",
                        # marker='o'
                    )
                    
                    plot_evolution(
                        Time_list , OH_radical_list, MECH, COLOR,
                        ylabel="Molar fraction [OH]",
                        xlabel="Time [ms]",
                        save_fig=Save_plot,
                        save_path=file_path_IDT_phi_P_T_time,
                        name_fig=f"OH_evolution_for_Fuel{Fuel_name}_Oxidizer{Oxi_name}_at_T_{T:.2f}K_and_P_{P:.2f}bars",
                        # marker='o'
                    )
                if Complementary_plot is True:
                    file_path_IDT_phi_P_T_comp  = create_folder(file_path_IDT_phi_P_T, "Complementary_evolution")
                    
                    plot_evolution(
                        Pressure_list , OH_radical_list, MECH, COLOR,
                        ylabel="Molar fraction [OH]",
                        xlabel="Pressure [bar]",
                        save_fig=Save_plot,
                        save_path=file_path_IDT_phi_P_T_comp,
                        name_fig=f"OH_evolution_fct_Pressure_for_Fuel{Fuel_name}_Oxidizer{Oxi_name}_at_T_{T:.2f}K_and_P_{P:.2f}bars",
                        # marker='o'
                    )
                    
                    plot_evolution(
                        Temperature_list , OH_radical_list, MECH, COLOR,
                        ylabel="Molar fraction [OH]",
                        xlabel="Temperature [K]",
                        save_fig=Save_plot,
                        save_path=file_path_IDT_phi_P_T_comp,
                        name_fig=f"OH_evolution_fct_Temperature_for_Fuel{Fuel_name}_Oxidizer{Oxi_name}_at_T_{T:.2f}K_and_P_{P:.2f}bars",
                        # marker='o'
                    )
                    
                    plot_evolution(
                        HRR_list , OH_radical_list, MECH, COLOR,
                        ylabel="Molar fraction [OH]",
                        xlabel="HRR [W/m3]",
                        save_fig=Save_plot,
                        save_path=file_path_IDT_phi_P_T_comp,
                        name_fig=f"OH_evolution_fct_HRR_for_Fuel{Fuel_name}_Oxidizer{Oxi_name}_at_T_{T:.2f}K_and_P_{P:.2f}bars",
                        # marker='o'
                    )
                    
                    plot_evolution(
                        Temperature_list , HRR_list, MECH, COLOR,
                        ylabel="HRR [W/m3] ",
                        xlabel="Temperature [K]",
                        save_fig=Save_plot,
                        save_path=file_path_IDT_phi_P_T_comp,
                        name_fig=f"HRR_evolution_fct_Temperature_for_Fuel{Fuel_name}_Oxidizer{Oxi_name}_at_T_{T:.2f}K_and_P_{P:.2f}bars",
                        # marker='o'
                    )
                    
                    plot_evolution(
                        Pressure_list , Temperature_list, MECH, COLOR,
                        ylabel="Temperature [K]",
                        xlabel="Pressure [bar]",
                        save_fig=Save_plot,
                        save_path=file_path_IDT_phi_P_T_comp,
                        name_fig=f"Temeprature_evolution_fct_Pressure_for_Fuel{Fuel_name}_Oxidizer{Oxi_name}_at_T_{T:.2f}K_and_P_{P:.2f}bars",
                        # marker='o'
                    )
    
def PostProcess_Gas_Composition():
    print()
    print( 85*"/")
    print("""
    CSV files contains the complete thermodynamic state of the gas mixture.
    
    Thermodynamic properties:
    - Temperature (K)
    - Pressure (Pa)
    - Density (kg/m3)
    - Mean Molecular Weight (kg/kmol)
    - Enthalpy (J/kg)
    - Internal Energy (J/kg)
    - Entropy (J/kg/K)
    - Gibbs Free Energy (J/kg)
    - Cp (J/kg/K)
    - Cv (J/kg/K)
    
    Species composition:
    - Y_species : Mass fraction of each species
    - X_species : Mole fraction of each species
    
    Only species with non-zero mass fraction are included in the file.
    
    All values correspond to the current thermodynamic state of the gas object.
    """)
    print( 85*"/")
                    
def PostProcess_Counter_flow(mechanisms, MECH, Fuel_name, Oxi_name, configuration, file_path_csv,file_path_plot,file_path_species_plot, Save_plot):
    COLOR = GC.Black_Purple()
    GC.config_plot()
    
    
    Temperature      = configuration["conditions"]["Counter_flow"]["Temperature_pairs"]
    Pressure  = configuration["conditions"]["Counter_flow"]["Pressure"]
    Velocity_flow = configuration["conditions"]["Counter_flow"]["Velocity_flux_pairs"]
    
    Major_species          = configuration["outputs"]["Counter_flow"]["Major_species"]
    Radicals               = configuration["outputs"]["Counter_flow"]["Radicals"]

    
    for indexT, T in enumerate(Temperature):
        
        path_T_CF     = create_folder(file_path_plot, f"{indexT:02}-Initial_Couple_Temperature_{T}K")
        path_T_CF_spe = create_folder(file_path_species_plot, f"{indexT:02}-Initial_Couple_Temperature_{T}K")
        
        for indexMass,Velo in enumerate(Velocity_flow):
            path_T_CF_V     = create_folder(path_T_CF,f"{indexMass:02}-Couple_Mass_flow_{Velo}")
            path_T_CF_V_spe = create_folder(path_T_CF_spe,f"{indexMass:02}-Couple_Mass_flow_{Velo}")
            print()
            print(f"\t  -> PROCESSING: Temperature couple {indexT:.2f} / Velocity flow > Fuel:{Velo[0]} m/s Oxidizer:{Velo[1]} m/s")
    
        for indexP,P in enumerate(Pressure):
            path_T_CF_V_P     = create_folder(path_T_CF_V, f"{indexP:02}-Initial_Pressure_{P:.2f}bars")
            path_T_CF_V_P_spe = create_folder(path_T_CF_V_spe, f"{indexP:02}-Initial_Pressure_{P:.2f}bars")
            
    
            
            Grid_list          = []
            Temperature_list   = []
            HRR_list           = []
            U_flame_list       = []
            Rho_flame_list     = []
            Strain_list        = []
            dTdx_list          = []
            Z_list             = []
            Cp_list            = []
            Lambda_list        = []
            Mu_list            = []
            species_Y = {}
            species_X = {}
            
         
            for mech_name in mechanisms:
                mech_index = list(mechanisms.keys()).index(mech_name)
                species_Y_mech = {}
                species_X_mech = {}
                
                csv_path = os.path.join(
                    file_path_csv,
                    f"{mech_index:02}-Kinetic_Mechanism_Used-{mech_name}",
                    f"{indexT:02}-Initial_Couple_Temperature_{T}K",
                    f"{indexP:02}-Initial_Pressure_{P:.2f}bars",
                    f"{indexMass:02}-Couple_Mass_flow_{Velo}",
                    f"results_{mech_name}_Species_Fuel{Fuel_name}_Oxidizer{Oxi_name}_at_Tfuel{T[0]:.0f}_Toxi{T[1]:.0f}_P{P:.2f}.csv")
                
                with open(csv_path, mode='r') as csv_file:
                    reader = csv.DictReader(csv_file, delimiter=';')
        
                    Grid, Temp, HRR = [], [], []
                    U, Rho, Z  = [], [], []
                    Strain, dTdx = [], []
                    Cp, Lambda, Mu = [], [], []
                    
                    # dictionnaire pour stocker toutes les espèces automatiquement
                    
        
                    for row in reader:
        
                        Grid.append(float(row["Grid [m]"]) * 1e3)
                        Temp.append(float(row["Temperature [K]"]))
                        HRR.append(float(row["Heat Release [W/m3]"]))
                        U.append(float(row["Axial Velocity [m/s]"]))
                        Rho.append(float(row["Density [kg/m3]"]))
        
                        Strain.append(float(row["Strain rate [1/s]"]))
                        dTdx.append(float(row["dT/dx [K/m]"]))
                        Z.append(float(row["Mixture fraction [-]"]))
                        Cp.append(float(row["cp [J/kg/K]"]))
                        Lambda.append(float(row["Thermal Conductivity [W/m/K]"]))
                        Mu.append(float(row["Viscosity [Pa.s]"]))
                        
                        
                        for key in row.keys():
                            if key.startswith("Y_"):
                                if key not in species_Y_mech:
                                    species_Y_mech[key] = []
                                species_Y_mech[key].append(float(row[key]))
            
                            if key.startswith("X_"):
                                if key not in species_X_mech:
                                    species_X_mech[key] = []
                                species_X_mech[key].append(float(row[key]))
                        
                    Grid_list.append(Grid)
                    Temperature_list.append(Temp)
                    HRR_list.append(HRR)
                    U_flame_list.append(U)
                    Rho_flame_list.append(Rho)
            
                    Strain_list.append(Strain)
                    dTdx_list.append(dTdx)
                    Z_list.append(Z)
                    Cp_list.append(Cp)
                    Lambda_list.append(Lambda)
                    Mu_list.append(Mu)
                    for key in species_Y_mech:
                        if key not in species_Y:
                            species_Y[key] = []
                        species_Y[key].append(species_Y_mech[key])
                
                    for key in species_X_mech:
                        if key not in species_X:
                            species_X[key] = []
                        species_X[key].append(species_X_mech[key])
                   
                 

            Temp = Temperature_list[0]
            Grid = Grid_list[0]
            n_plateau = 10  # nombre de points pour estimer le plateau

            T_left_plateau = np.mean(Temp[:n_plateau])
            T_right_plateau = np.mean(Temp[-n_plateau:])
            threshold = 0.01  # 1% de la différence max
            T_min = np.min(Temp)
            T_max = np.max(Temp)
            
            delta_left = threshold * (T_max - T_min)
            delta_right = threshold * (T_max - T_min)
            # côté gauche
            for i in range(n_plateau, len(Temp)):
                if abs(Temp[i] - T_left_plateau) > delta_left:
                    if i > 5:
                        x_left = Grid[i-5]
                    else:
                        x_left = Grid[0]
                    break
            
            # côté droit
            for i in range(len(Temp)-n_plateau-1, -1, -1):
                if abs(Temp[i] - T_right_plateau) > delta_right:
                    if i < len(Temp)-7:
                        x_right = Grid[i+7]
                    else:
                        x_right = Grid[-1]
                    break
                                
            print("\t \t  -> PROCESSING: BASIC PLOT EVOLUTION")    
            # ---------- PLOTS ----------
            plot_evolution(
                Grid_list , Temperature_list, MECH, COLOR,
                ylabel="Temperature [K]",
                xlabel="Distance [mm]",
                x_limit_left= x_left, 
                x_limit_right= x_right,
                secondary_data=HRR_list, 
                secondary_ylabel="HRR [W/m3] -- ",        
                save_fig=Save_plot,
                save_path=path_T_CF_V_P,
                name_fig=f"Temperature_HRR_diffusion_flame_evolution_for_Fuel{Fuel_name}_Oxidizer{Oxi_name}_at_Tfuel{T[0]:.0f}_Toxi{T[1]:.0f}_and_P_{P:.2f}bars",
                # marker='o'
            )
            
            plot_evolution(
                Grid_list , Temperature_list, MECH, COLOR,
                ylabel="Temperature [K]",
                xlabel="Distance [mm]",
                x_limit_left= x_left, 
                x_limit_right= x_right,
                secondary_data=Z_list, 
                secondary_ylabel="Mixture fraction -- ",        
                save_fig=Save_plot,
                save_path=path_T_CF_V_P,
                name_fig=f"Temperature_MixtureFraction_diffusion_flame_evolution_for_Fuel{Fuel_name}_Oxidizer{Oxi_name}_at_Tfuel{T[0]:.0f}_Toxi{T[1]:.0f}_and_P_{P:.2f}bars",
                # marker='o'
            )
            
            plot_evolution(
                Grid_list , HRR_list, MECH, COLOR,
                ylabel="HRR [W/m3]",
                xlabel="Distance [mm]",
                x_limit_left= x_left, 
                x_limit_right= x_right,
                secondary_data=Z_list, 
                secondary_ylabel="Mixture frqction -- ",        
                save_fig=Save_plot,
                save_path=path_T_CF_V_P,
                name_fig=f"HRR_MixtureFraction_diffusion_flame_evolution_for_Fuel{Fuel_name}_Oxidizer{Oxi_name}_at_Tfuel{T[0]:.0f}_Toxi{T[1]:.0f}_and_P_{P:.2f}bars",
                # marker='o'
            )
            
            plot_evolution(
                Grid_list , Temperature_list, MECH, COLOR,
                ylabel="Temperature [K]",
                xlabel="Distance [mm]",
                x_limit_left= x_left, 
                x_limit_right= x_right,
                secondary_data=Rho_flame_list, 
                secondary_ylabel="Density [kg/m3] -- ",
                save_fig=Save_plot,
                save_path=path_T_CF_V_P,
                name_fig=f"Temperature_RHO_diffusion_flame_evolution_for_Fuel{Fuel_name}_Oxidizer{Oxi_name}_at_Tfuel{T[0]:.0f}_Toxi{T[1]:.0f}_and_P_{P:.2f}bars",
                # marker='o'
            )
            
            plot_evolution(
                Grid_list , U_flame_list, MECH, COLOR,
                ylabel="Axial Velocity [m/s]",
                xlabel="Distance [mm]",
                x_limit_left= x_left, 
                x_limit_right= x_right,
                secondary_data= Strain_list, 
                secondary_ylabel="Strain [1/s] -- ",
                save_fig=Save_plot,
                save_path=path_T_CF_V_P,
                name_fig=f"Axial_velocity_Strain_diffusion_flame_evolution_for_Fuel{Fuel_name}_Oxidizer{Oxi_name}_at_Tfuel{T[0]:.0f}_Toxi{T[1]:.0f}_and_P_{P:.2f}bars",
                # marker='o'
            )
            
            plot_evolution(
                Grid_list , Temperature_list, MECH, COLOR,
                ylabel="Temperature [K]",
                xlabel="Distance [mm]",
                x_limit_left= x_left, 
                x_limit_right= x_right,
                secondary_data= Strain_list, 
                secondary_ylabel="Strain [1/s] -- ",
                save_fig=Save_plot,
                save_path=path_T_CF_V_P,
                name_fig=f"Temeperature_Strain_diffusion_flame_evolution_for_Fuel{Fuel_name}_Oxidizer{Oxi_name}_at_Tfuel{T[0]:.0f}_Toxi{T[1]:.0f}_and_P_{P:.2f}bars",
                # marker='o'
            )
            
            
            print("\t \t -> PROCESSING: SPECIES PLOT EVOLUTION")  
            for key in species_Y:
                    k = key.split("_")[1]
                    if len(Grid_list) > len(species_Y[key]):
                        Grid_inter    = []
                        MECH_inter    = []
                        SPECIES_inter = []

                        for i in range(len(species_Y[key])):
                            for j in range(len(Grid_list)):
                                if len(Grid_list[j]) == len(species_Y[key][i]):
                                    Grid_inter.append(Grid_list[j])
                                    MECH_inter.append(MECH[j])
                                    SPECIES_inter.append(species_Y[key][i])
                                    
                        
                    else:
                        Grid_inter = copy.deepcopy(Grid_list)
                        MECH_inter = copy.deepcopy(MECH)
                        SPECIES_inter = copy.deepcopy(species_Y[key])
                        
                    if k in Major_species:
                        plot_evolution(
                            Grid_inter , SPECIES_inter, MECH_inter, COLOR,
                            ylabel=f"Mass fraction [{key}]",
                            xlabel="Distance [mm]",
                            x_limit_left= x_left, 
                            x_limit_right= x_right,
                            save_fig=Save_plot,
                            save_path=path_T_CF_V_P_spe,
                            name_fig=f"{key}_Mass_fraction_diffusion_flame_evolution_for_Fuel{Fuel_name}_Oxidizer{Oxi_name}_at_Tfuel{T[0]:.0f}_Toxi{T[1]:.0f}_and_P_{P:.2f}bars",
                            # marker='o'
                            )
                    elif k in Radicals:
                        plot_evolution(
                            Grid_inter , SPECIES_inter, MECH_inter, COLOR,
                            ylabel=f"Mass fraction [{key}]",
                            xlabel="Distance [mm]",
                            x_limit_left= x_left, 
                            x_limit_right= x_right,
                            type_y_scale='log',
                            save_fig=Save_plot,
                            save_path=path_T_CF_V_P_spe,
                            name_fig=f"{key}_Mass_fraction_diffusion_flame_evolution_for_Fuel{Fuel_name}_Oxidizer{Oxi_name}_at_Tfuel{T[0]:.0f}_Toxi{T[1]:.0f}_and_P_{P:.2f}bars",
                            # marker='o'
                            )
                        
            for key in species_X:
                    k = key.split("_")[1]
                    if len(Grid_list) > len(species_X[key]):
                        Grid_inter    = []
                        MECH_inter    = []
                        SPECIES_inter = []

                        for i in range(len(species_X[key])):
                            for j in range(len(Grid_list)):
                                if len(Grid_list[j]) == len(species_X[key][i]):
                                    Grid_inter.append(Grid_list[j])
                                    MECH_inter.append(MECH[j])
                                    SPECIES_inter.append(species_X[key][i])
                                    
                        
                    else:
                        Grid_inter = copy.deepcopy(Grid_list)
                        MECH_inter = copy.deepcopy(MECH)
                        SPECIES_inter = copy.deepcopy(species_X[key])
                        
                    if k in Major_species:
                        plot_evolution(
                            Grid_inter , SPECIES_inter, MECH_inter, COLOR,
                            ylabel=f"Molar fraction [{key}]",
                            xlabel="Distance [mm]",
                            x_limit_left= x_left, 
                            x_limit_right= x_right,
                            save_fig=Save_plot,
                            save_path=path_T_CF_V_P_spe,
                            name_fig=f"{key}_Molar_fraction_diffusion_flame_evolution_for_Fuel{Fuel_name}_Oxidizer{Oxi_name}_at_Tfuel{T[0]:.0f}_Toxi{T[1]:.0f}_and_P_{P:.2f}bars",
                            # marker='o'
                            )
                    elif k in Radicals:
                        X_ppm = [[val * 1e6 for val in sublist] for sublist in SPECIES_inter]
                        plot_evolution(
                            Grid_inter , X_ppm, MECH_inter, COLOR,
                            ylabel=f"Molar fraction [{key} ppm]",
                            xlabel="Distance [mm]",
                            x_limit_left= x_left, 
                            x_limit_right= x_right,
                            save_fig=Save_plot,
                            save_path=path_T_CF_V_P_spe,
                            name_fig=f"{key}_Molar_fraction_diffusion_flame_evolution_for_Fuel{Fuel_name}_Oxidizer{Oxi_name}_at_Tfuel{T[0]:.0f}_Toxi{T[1]:.0f}_and_P_{P:.2f}bars",
                            # marker='o'
                            )
            mech_index = 0           
            for mech_name, mech_file in mechanisms.items():
                
                gas = ct.Solution(mech_file)
                species_mech = gas.species_names
                
                path_T_CF_Mass_P_mech_spe = create_folder(
                    path_T_CF_V_P_spe,
                    f"{mech_index:02}-Kinetic_Mechanism_Used-{mech_name}"
                )
            
                Grid = Grid_list[mech_index]
            
                def split_species(species_dict):
                    Maj, Rad = [], []
                    name_Maj, name_Rad = [], []
            
                    for key, values in species_dict.items():
                        k = key.split("_")[1]
                        if k in Major_species and k in species_mech:
                            if len(values) >= mech_index+1 : 
                                name_Maj.append(key)
                                Maj.append(values[mech_index])
                        elif k in Radicals and k in species_mech:
                            if len(values) >= mech_index+1 :
                                name_Rad.append(key)
                                Rad.append(values[mech_index])
            
                    return Maj, Rad, name_Maj, name_Rad
            
                # Mass fractions
                Maj_Y, Rad_Y, name_key_Maj, name_key_Rad = split_species(species_Y)
            
                # Molar fractions
                Maj_X, Rad_X, _, _ = split_species(species_X)
            
                base_name = (
                    f"{mech_name}_{{}}_diffusion_flame_evolution_for_"
                    f"Fuel{Fuel_name}_Oxidizer{Oxi_name}_"
                    f"at_Tfuel{T[0]:.0f}_Toxi{T[1]:.0f}_and_P_{P:.2f}bars"
                )
            
                plots = [
                    (Maj_Y, name_key_Maj, "Mass fraction ", "Mass_fraction_Major_species"),
                    (Rad_Y, name_key_Rad, "Mass fraction ", "Mass_fraction_Radical_species"),
                    (Maj_Y + Rad_Y, name_key_Maj + name_key_Rad, "Mass fraction ", "Mass_fraction_Total_species"),
                    (Maj_X, name_key_Maj, "Molar fraction ", "Molar_fraction_Major_species"),
                    (Rad_X, name_key_Rad, "Molar fraction ", "Molar_fraction_Radical_species"),
                ]

                for data, labels, ylabel, suffix in plots:
                    plot_evolution(
                        Grid,
                        data,
                        labels,
                        COLOR,
                        ylabel=ylabel,
                        xlabel="Distance [mm]",
                        x_limit_left=x_left,
                        x_limit_right=x_right,
                        save_fig=Save_plot,
                        save_path=path_T_CF_Mass_P_mech_spe,
                        name_fig=base_name.format(suffix),
                    )
                mech_index +=1
def PostProcess_Counter_flow_quenching(mechanisms, MECH, Fuel_name, Oxi_name, configuration, file_path_csv,file_path_plot, Save_plot):
    COLOR = GC.Black_Purple()
    GC.config_plot()
    
    Temperature      = configuration["conditions"]["Counter_flow"]["Temperature_pairs"]
    Pressure  = configuration["conditions"]["Counter_flow"]["Pressure"]
    
    
    for indexT, T in enumerate(Temperature):
        path_T_QCF     = create_folder(file_path_plot, f"{indexT:02}-Initial_Couple_Temperature_{T}K")
    
        for indexP,P in enumerate(Pressure):
            path_T_QCF_V_P     = create_folder(path_T_QCF, f"{indexP:02}-Initial_Pressure_{P:.2f}bars")
            print()
            print(f"\t  -> PROCESSING: Pressure {P:.2f} bar / Temeperature flow > Fuel:{T[0]} K ,Oxidizer:{T[1]} K")
            
    
            a_maxi             = []
            T_max              = []
            HRR_max            = []
            Fuel_mdot          = []
            Oxid_mdot          = []
            InletFuel_Velocity = []
            InletOxid_Velocity = []
            Max_dTdx           = []
            
            quenching_valS   = []
            quenching_valT   = []
            quenching_valHRR = []
            orientationV     = []
            orientationH     = []
         
            for mech_name in mechanisms:
                mech_index = list(mechanisms.keys()).index(mech_name)
                
                csv_path = os.path.join(
                    file_path_csv,
                    f"{mech_index:02}-Kinetic_Mechanism_Used-{mech_name}",
                    f"{indexT:02}-Initial_Couple_Temperature_{T}K",
                    f"{indexP:02}-Initial_Pressure_{P:.2f}bars",
                    f"results_{mech_name}_Species_Fuel{Fuel_name}_Oxidizer{Oxi_name}_at_Tfuel{T[0]:.0f}_Toxi{T[1]:.0f}_P{P:.2f}.csv")
                
                with open(csv_path, mode='r') as csv_file:
                    reader = csv.DictReader(csv_file, delimiter=';')
        
                    strain, Temp, HRR = [], [], []
                    U_f, U_o, mdot_f,mdot_o  = [], [], [], []
                    dTdx = []
                    
                    for row in reader:
        
                        strain.append(float(row["Max strain [1/s]"]))
                        Temp.append(float(row["Temperature max [K]"]))
                        HRR.append(float(row["Heat Release max [W/m3]"]))
                        
                        U_f.append(float(row["Inlet fuel Axial Velocity [m/s]"]))
                        U_o.append(float(row["Inlet oxidizer mass flow [kg/m2/s]"]))
                        mdot_f.append(float(row["Inlet fuel mass flow [kg/m2/s]"]))
                        mdot_o.append(float(row["Inlet oxidizer mass flow [kg/m2/s]"]))
                        dTdx.append(float(row["dT/dx max [K/m]"]))
                        
                    quenching_valS.append(np.max(strain)) 
                    quenching_valT.append(np.min(Temp)) 
                    quenching_valHRR.append(np.max(HRR)) 
                    orientationV.append('V')
                    orientationH.append('H')
                    
                    a_maxi.append(strain)
                    T_max.append(Temp)
                    HRR_max.append(HRR)
                    Fuel_mdot.append(mdot_f)
                    Oxid_mdot.append(mdot_o)
                    InletFuel_Velocity.append(U_f)
                    InletOxid_Velocity.append(U_o)
                    Max_dTdx.append(dTdx)
                
            
                
            print("\t \t  -> PROCESSING: STRAIN PLOT EVOLUTION")    
            
            plot_evolution(
                a_maxi , T_max, MECH, COLOR,
                ylabel="Max flame Temeprature [K]",
                xlabel="Strain max [1/s]",
                line_value=quenching_valS+quenching_valT, line_orientation=orientationV+orientationH,       
                type_x_scale='log',
                save_fig=Save_plot,
                save_path=path_T_QCF_V_P,
                name_fig=f"Temperature_Strain_extinction_diffusion_flame_evolution_for_Fuel{Fuel_name}_Oxidizer{Oxi_name}_at_Tfuel{T[0]:.0f}_Toxi{T[1]:.0f}_and_P_{P:.2f}bars",
                # marker='o'
            )
            
            plot_evolution(
                a_maxi , HRR_max, MECH, COLOR,
                ylabel="Max HRR [W/m3]",
                xlabel="Strain max [1/s]",
                line_value=quenching_valS+quenching_valHRR, line_orientation=orientationV+orientationH,    
                type_x_scale='log',
                save_fig=Save_plot,
                save_path=path_T_QCF_V_P,
                name_fig=f"HRR_Strain_extinction_diffusion_flame_evolution_for_Fuel{Fuel_name}_Oxidizer{Oxi_name}_at_Tfuel{T[0]:.0f}_Toxi{T[1]:.0f}_and_P_{P:.2f}bars",
                # marker='o'
            )
            
            plot_evolution(
                a_maxi , Max_dTdx, MECH, COLOR,
                ylabel="Max Temperature grad [K/m]",
                xlabel="Strain max [1/s]",
                line_value=quenching_valS, line_orientation=orientationV,          
                type_x_scale='log',
                save_fig=Save_plot,
                save_path=path_T_QCF_V_P,
                name_fig=f"dTdx_Strain_extinction_diffusion_flame_evolution_for_Fuel{Fuel_name}_Oxidizer{Oxi_name}_at_Tfuel{T[0]:.0f}_Toxi{T[1]:.0f}_and_P_{P:.2f}bars",
                # marker='o'
            )
            
            plot_evolution(
                HRR_max , T_max, MECH, COLOR,
                ylabel="Max flame Temeprature [K]",
                xlabel="Max HRR [W/m3]",    
                type_x_scale='log',
                save_fig=Save_plot,
                save_path=path_T_QCF_V_P,
                name_fig=f"Temperature_HRR_extinction_diffusion_flame_evolution_for_Fuel{Fuel_name}_Oxidizer{Oxi_name}_at_Tfuel{T[0]:.0f}_Toxi{T[1]:.0f}_and_P_{P:.2f}bars",
                # marker='o'
            )       
            
            print("\t \t  -> PROCESSING: VELOCITY PLOT EVOLUTION")    
            
            plot_evolution(
                Fuel_mdot , InletFuel_Velocity, MECH, COLOR,
                ylabel="Inlet Fuel Velocity [m/s]" ,
                xlabel="Inlet Fuel flow [kg/m2/s]",
                save_fig=Save_plot,
                save_path=path_T_QCF_V_P,
                name_fig=f"Comparaison_Velocity_and_flow_fuel_during_diffusion_flame_extinction_evolution_for_Fuel{Fuel_name}_Oxidizer{Oxi_name}_at_Tfuel{T[0]:.0f}_Toxi{T[1]:.0f}_and_P_{P:.2f}bars",
                # marker='o'
            )
            
            plot_evolution(
                Oxid_mdot , InletOxid_Velocity, MECH, COLOR,
                ylabel="Inlet Oxidizer Velocity [m/s]" ,
                xlabel="Inlet Oxidizer flow [kg/m2/s]",
                save_fig=Save_plot,
                save_path=path_T_QCF_V_P,
                name_fig=f"Comparaison_Velocity_and_flow_oxidizer_during_diffusion_flame_extinction_evolution_for_Fuel{Fuel_name}_Oxidizer{Oxi_name}_at_Tfuel{T[0]:.0f}_Toxi{T[1]:.0f}_and_P_{P:.2f}bars",
                # marker='o'
            )
            
            plot_evolution(
                a_maxi , InletFuel_Velocity, MECH, COLOR,
                ylabel="Inlet Fuel Velocity [m/s]",
                xlabel="Strain max [1/s]",
                type_x_scale='log',
                save_fig=Save_plot,
                save_path=path_T_QCF_V_P,
                name_fig=f"Velocity_fuel_Strain_extinction_diffusion_flame_evolution_for_Fuel{Fuel_name}_Oxidizer{Oxi_name}_at_Tfuel{T[0]:.0f}_Toxi{T[1]:.0f}_and_P_{P:.2f}bars",
                # marker='o'
            )
            
            plot_evolution(
                a_maxi , InletOxid_Velocity, MECH, COLOR,
                ylabel="Inlet Oxidizer Velocity [m/s]",
                xlabel="Strain max [1/s]",
                type_x_scale='log',
                save_fig=Save_plot,
                save_path=path_T_QCF_V_P,
                name_fig=f"Velocity_oxid_Strain_extinction_diffusion_flame_evolution_for_Fuel{Fuel_name}_Oxidizer{Oxi_name}_at_Tfuel{T[0]:.0f}_Toxi{T[1]:.0f}_and_P_{P:.2f}bars",
                # marker='o'
            )
            
            plot_evolution(
                a_maxi , InletFuel_Velocity, MECH, COLOR,
                ylabel="Inlet Fuel Velocity [m/s]",
                xlabel="Strain max [1/s]",
                type_x_scale='log',
                save_fig=Save_plot,
                save_path=path_T_QCF_V_P,
                name_fig=f"Velocity_Fuel_Strain_extinction_diffusion_flame_evolution_for_Fuel{Fuel_name}_Oxidizer{Oxi_name}_at_Tfuel{T[0]:.0f}_Toxi{T[1]:.0f}_and_P_{P:.2f}bars",
                # marker='o'
            )
            
            
            
             
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
