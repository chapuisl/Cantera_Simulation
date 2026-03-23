"""
# ===================================================================================================================
#  Cantera PreProcessing file:
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
#  This module provides a structured preprocessing framework for combustion simulations performed 
#  with Cantera_proc.py
#
#  It initializes gas mixtures, applies thermodynamic conditions, executes combustion
#  simulations across parametric studies (temperature, pressure, equivalence ratio,
#  mass flow rates, etc.), and systematically stores computed results (.csv file) in organized
#  directory structures.
#
#  The module supports multiple kinetic mechanisms and automatically:
#      - Configures reactive mixtures
#      - Solves laminar and diffusion flame configurations
#      - Performs equilibrium and ignition delay calculations
#      - Exports thermochemical, transport, and species data to CSV files
#      - Ensures reproducible and structured data generation
#
#  It is designed as the computational backbone of the simulation framework,
#  generating consistent datasets for subsequent post-processing and analysis.
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
from Common_Utils_tools import create_folder

from Verbosity_Level_Plot import Verbosity_Temperature_Adiabatic
from Verbosity_Level_Plot import Verbosity_Gas_Composition
from Verbosity_Level_Plot import Verbosity_Counter_flow_quenching
from Verbosity_Level_Plot import Verbosity_Counter_flow
from Verbosity_Level_Plot import Verbosity_Flame1D
from Verbosity_Level_Plot import Verbosity_IDT

"""
# ===================================================================================================================
#  Import library
# ===================================================================================================================
"""
from colorama import Fore
from colorama import init
init(autoreset=True)
import cantera as ct
import numpy as np
import csv
import sys
import os

"""
# ===================================================================================================================
#  Function
# ===================================================================================================================
"""
class FlameExtinguished(Exception):
    pass

# Cette fonction a pour but de calculer une flamme 1D
#
# @param gas            : Melange de gas
#
# @return  flame        : Toute les evolutions de la flamme 
def solver_free_flame( gas, ratio_refine =3.0,width_values=0.05, slope_values=0.06, curve_values=0.1  ):
    try:
        flame = ct.FreeFlame(gas, width=width_values)
        flame.set_refine_criteria(ratio=ratio_refine, slope=slope_values, curve=curve_values)
        flame.soret_enabled = True 
        flame.transport_model = 'multicomponent'
        # flame.flux_gradient_basis = "mass" # only relevant for mixture-averaged model
        flame.solve(loglevel=0, auto=True) 
        
        # flame.show()
        return flame
    
    except ct.CanteraError as e:
        print(Fore.RED + f" WARNING: No solutioon find for this conditions: {e}")
        return flame
    



def PreProcess_Flame1D(mechanisms, MECH, Fuel_name, Oxi_name, Fuel, Oxidizer, configuration, file_path_csv,file_path_AVBP, Verbosity_level):
    Temperature      = configuration["conditions"]["Flame_1D"]["Temperature"]
    Pressure         = configuration["conditions"]["Flame_1D"]["Pressure"]
    Equivalent_Ratio = configuration["conditions"]["Flame_1D"]["Phi"]
    
    AVBP_sol         = configuration["outputs"]["Flame_1D"]["save_AVBP_solution"]
    Major_species    = configuration["outputs"]["Flame_1D"]["Major_species"]
    Radicals         = configuration["outputs"]["Flame_1D"]["Radicals"]
    

    indexMech = 0

    for mech_name, mech_file in mechanisms.items():
        print(f"\n{'='*60}")
        print(f" MÉCANISME : {mech_name}")
        print(f"{'='*60}")

        mech_path = create_folder(file_path_csv,f"{indexMech:02}-Kinetic_Mechanism_Used-{mech_name}" )
        indexMech += 1

        for indexT, T in enumerate(Temperature):
            T_path = create_folder(mech_path,f"{indexT:02}-Initial_Temperature_{T:.2f}K")
                
            for indexP, P in enumerate(Pressure):
                P_path = create_folder(T_path, f"{indexP:02}-Initial_Pressure_{P:.2f}bars")

                # CSV paths
                if AVBP_sol is True:
                    file_path_AVBP_save = create_folder(file_path_AVBP,[
                        f"{indexMech:02}-Kinetic_Mechanism_Used-{mech_name}" ,
                        f"{indexT:02}-Initial_Temperature_{T:.2f}K" ,
                        f"{indexP:02}-Initial_Pressure_{P:.2f}bars"])
                        
                Flame1D_prop_csv = os.path.join(P_path, f"results_{mech_name}_Species_Fuel{Fuel_name}_Oxidizer{Oxi_name}_at_T{T:.2f}_P{P:.2f}.csv")
                
                with open(Flame1D_prop_csv, "a", newline="") as f:
                    w = csv.writer(f)
                    if os.stat(Flame1D_prop_csv).st_size == 0:
                        w.writerow([
                            "Equivalence Ratio",
                            "Flame Speed [m/s]",
                            "Flame Thickness [mm]",
                            "Flame Time [ms]",
                            "Damkohler [-]"
                        ])
                
                # ---------- CALCUL ----------
                for indexPhi, eq_ratio in enumerate(Equivalent_Ratio):
                    P_eq_path = create_folder(P_path, f"{indexPhi:02}-Equivalent_ratio_Phi-{eq_ratio:.2f}")
                    
                    Flame1D_csv = os.path.join(P_eq_path, f"species_results_{mech_name}_Species_Fuel{Fuel_name}_Oxidizer{Oxi_name}_at_T{T:.2f}_P{P:.2f}_Phi{eq_ratio:.2f}.csv")
                    os.makedirs(os.path.dirname(Flame1D_csv), exist_ok=True)
                    
                    print(f"→ Flame1D: φ = {eq_ratio:.2f} | T={T} K | P={P} bar")
                    gas = ct.Solution(mech_file)

                    gas.TP = T, P * 1e5
                    gas.set_equivalence_ratio(eq_ratio, Fuel, Oxidizer)

                    flame = solver_free_flame(gas)
                    
                    Verbosity_Flame1D(Verbosity_level, gas, flame)
                    
                    if AVBP_sol is True:
                        
                        nb_point = len(flame.grid)
                        nb_species = len(flame.gas.species_names)
                        
                        filename = os.path.join(file_path_AVBP_save, f"Cantera_{nb_point}Grip_{nb_species}Species_Fuel{Fuel_name}_Oxidizer{Oxi_name}_at_{T:.2f}K_{P:.2f}B_Phi{eq_ratio:.2f}.csv")
                        flame.save(filename, 'energy','overwrite = True')
                            
                    Sl = flame.velocity[0]
                    no_rad = flame.to_array()
                    
                    Temp = flame.T
                    x = flame.grid
                    dTdx = np.gradient(Temp, x)
                    thickness = (Temp.max() - Temp.min()) / np.max(np.abs(dTdx))
                    thickness_mm = thickness * 1e3

                    flame_time_ms = (thickness / Sl) * 1e3

                    lambda_ = flame.thermal_conductivity[0]
                    rho = flame.gas.density
                    cp = flame.gas.cp_mass
                    alpha = lambda_ / (rho * cp)
                    tau_diff = thickness**2 / alpha
                    tau_chem = thickness / Sl
                    Da = tau_diff / tau_chem
                    
                    headers = [
                        "Grid [m]",
                        "Temperature [K]",
                        "Heat Release [W/m3]",
                        "Axial Velocity [m/s]",
                        "Density [kg/m3]",
                        "cp [J/kg/K]",
                        "Thermal Conductivity [W/m/K]",
                        "Viscosity [Pa.s]",
                        "dT/dx [K/m]",
                    ]
                    species_mech = gas.species_names
                    for spe in Major_species + Radicals :
                        if spe in species_mech:
                            if gas[spe].Y[0] != 0:
                                headers.append(f"Y_{spe}")
                                headers.append(f"X_{spe}")
                        else: 
                            print(Fore.RED + f" WARNING: Species {spe} not in the mechanism {mech_name}")
                            
                    
                    with open(Flame1D_csv, mode='w', newline='') as file:
                        writer = csv.writer(file, delimiter=';')
                        writer.writerow(headers)
                    
                        n_points = len(flame.grid)
                    
                        for i in range(n_points):
                            row = [
                                flame.grid[i],
                                flame.T[i],
                                flame.heat_release_rate[i],
                                flame.velocity[i],
                                flame.density[i],
                                flame.cp_mass[i],
                                flame.thermal_conductivity[i],
                                flame.viscosity[i],
                                dTdx[i],
                            ]
                    
                            for spe in Major_species + Radicals :
                                if spe in species_mech:
                                    if gas[spe].Y[0] != 0:
                                        row.append(no_rad(spe).Y[i][0])
                                        row.append(no_rad(spe).X[i][0])
                                        
                    
                            writer.writerow(row)

                    # --------- WRITE CSV ----------
                    with open(Flame1D_prop_csv, "a", newline="") as f:
                        csv.writer(f).writerow([
                            eq_ratio, Sl, thickness_mm, flame_time_ms, Da
                        ])


      
       
def PreProcess_Temperature_Adiabatic(mechanisms, MECH, Fuel_name, Oxi_name, Fuel, Oxidizer, configuration, file_path_csv, Verbosity_level):
    Temperature      = configuration["conditions"]["Temperature_Adiabatic"]["Temperature"]
    Pressure  = configuration["conditions"]["Temperature_Adiabatic"]["Pressure"]
    Equivalent_Ratio = configuration["conditions"]["Temperature_Adiabatic"]["Phi"]
    
    Final_Temperature    = configuration["outputs"]["Temperature_Adiabatic"]["Final_Temperature"]
    Final_density        = configuration["outputs"]["Temperature_Adiabatic"]["Final_density"]
    Final_Enthalpy       = configuration["outputs"]["Temperature_Adiabatic"]["Final_Enthalpy"]
    
    indexMech=0
    
    for mech_name,mech_file in mechanisms.items():
        file_path_Adiabatic_mech=create_folder(file_path_csv,f"{indexMech:02}-Kinetic_Mechanism Used-{mech_name}")
        indexMech+=1
        print(f"\n{'='*60}\n MÉCANISME : {mech_name}\n{'='*60}")
        
        for indexT,T in enumerate(Temperature):
            file_path_Adiabatic_T=create_folder(file_path_Adiabatic_mech,f"{indexT:02}-Initial_Temperature_{T:.2f}K")
            print(f"\n--- Temperature : {T:.2f} K ---")
            
            for indexP,P in enumerate(Pressure):
                file_path_Adiabatic_T_P=create_folder(file_path_Adiabatic_T,f"{indexP:02}-Initial_Pressure_{P:.2f}bars")
                
                csv_file_path=os.path.join(file_path_Adiabatic_T_P,f"results_{mech_name}_Species_Fuel{Fuel_name}_Oxidizer{Oxi_name}_at_T{T:.2f}K_P{P:.2f}.csv")
                
                
                headers = [
                     "Adiabatic Temperature [K]",
                     "Density [kg/m3]",
                     "Initial Enthalpy [J/kg]",
                     "Final Enthalpy [J/kg]",
                 ]
                
                Temp          = []
                Density       = []
                Enthalpy_init = []
                Enthalpy_end  = []
                
                for eq_ratio in Equivalent_Ratio:
                    print(f"→ Adiabatic Temperature: φ = {eq_ratio:.2f}   | T={T:.2f} K | P={P:.2f} bar")
                    gas = ct.Solution(mech_file)
                    gas.TP=T,P*1e5
                    gas.set_equivalence_ratio(eq_ratio,Fuel,Oxidizer)
                    h_init = gas.enthalpy_mass
                    gas.equilibrate("HP",solver="gibbs",rtol=1e-7)
                    
                    Verbosity_Temperature_Adiabatic(Verbosity_level,gas)
                    Temp.append(gas.T)
                    Density.append(gas.density)
                    Enthalpy_init.append(h_init)
                    Enthalpy_end.append(gas.enthalpy_mass)
                    
                        
                with open(csv_file_path, mode='w', newline='') as file:
                    writer = csv.writer(file, delimiter=';')
                    writer.writerow(headers)
                
                    for i in range(len(Temp)):
                        row = [
                            Temp[i],
                            Density[i],
                            Enthalpy_init[i],
                            Enthalpy_end[i]
                        ]
                
                        writer.writerow(row)
                 
    
def PreProcess_IDT(mechanisms, MECH, Fuel_name, Oxi_name, Fuel, Oxidizer, configuration, file_path_csv, Verbosity_level):
    Temperature       = configuration["conditions"]["Ignition_Delay_time"]["Temperature"]
    Pressure          = configuration["conditions"]["Ignition_Delay_time"]["Pressure"]
    Equivalent_Ratio  = configuration["conditions"]["Ignition_Delay_time"]["Phi"]
    
    IDT_plot           = configuration["outputs"]["Ignition_Delay_time"]["IDT_plot"]
    Time_evolution     = configuration["outputs"]["Ignition_Delay_time"]["time_evolution"]
    Complementary_plot = configuration["outputs"]["Ignition_Delay_time"]["complementary_plot"]
    

    indexMech = 0
    
    # Boucle principale
    for mech_name, mech_file in mechanisms.items():
        file_path_IDT_csv_mesh = create_folder(file_path_csv, f"{indexMech:02}-Kinetic_Mechanism_Used-{mech_name}")
        print(f"\n{'='*60}")
        print(f" MÉCANISME : {mech_name}")
        print(f"{'='*60}")
        indexMech += 1
    
        for indexPhi, eq_ratio in enumerate(Equivalent_Ratio):
            file_path_IDT_csv_mesh_phi = create_folder(file_path_IDT_csv_mesh, f"{indexPhi:02}-Equivalent_ratio_Phi-{eq_ratio:.2f}")
            
    
            for indexP, P in enumerate(Pressure):
                file_path_IDT_csv_mesh_phi_P = create_folder(file_path_IDT_csv_mesh_phi, f"{indexP:02}-Initial_Pressure_{P:.2f}bars")
    
                # Chemin du fichier CSV pour cette combinaison
                IDT_csv = os.path.join(file_path_IDT_csv_mesh_phi_P,
                                f"results_{mech_name}_Species_Fuel{Fuel_name}_Oxidizer{Oxi_name}_at_Phi{eq_ratio:.0f}_P{P:.2f}.csv")
               
                headersIDT = [
                    "Temeperature [K]",
                    "IDT [ms]",
                ]
                IDT = []
  
                for indexT,T in enumerate(Temperature):
                    file_path_IDT_csv_mesh_phi_P_T = create_folder(file_path_IDT_csv_mesh_phi_P,f"{indexT:02}-Initial_Temperature_{T:.2f}K")
                    IDT_csv_time = os.path.join(file_path_IDT_csv_mesh_phi_P_T,
                                    f"results_time_{mech_name}_Species_Fuel{Fuel_name}_Oxidizer{Oxi_name}_at_Phi{eq_ratio:.0f}_P{P:.2f}.csv")
                    
                    print(f"→ IDT: φ = {eq_ratio:.2f}   | T={T:.2f} K | P={P:.2f} bar")
                    
                    gas = ct.Solution(mech_file)     
                    gas.set_equivalence_ratio(eq_ratio, Fuel, Oxidizer)
                    gas.TP = T, P * 1e5
                    estimated_ignition_delay_time = 15.0

                    r = ct.Reactor(gas, clone=False)
                    net = ct.ReactorNet([r])
                    t = 0
                    Time         = []
                    Temperature_list  = []
                    Heat_release = []
                    Pressure_list     = []
                    OH           = []

                    while t < estimated_ignition_delay_time:
                        t = net.step()
                        Time.append(t * 1000)
                        Temperature_list.append(gas.T)
                        Pressure_list.append(gas.P / 1e5) 
                        Heat_release.append(gas.heat_release_rate / 1e6)
                        OH.append(gas['OH'].X[0])

                    i_max = Heat_release.index(max(Heat_release))
                    IDT.append(Time[i_max])
                    
                    Verbosity_IDT(Verbosity_level, gas, IDT[-1], i_max)
                    
                    headers = [
                        "Time [ms]",
                        "Temperature [K]",
                        "Heat Release [W/m3]",
                        "Pressure [bar]",
                        "OH radical []",
                        
                    ]
                    
                    with open(IDT_csv_time, mode='w', newline='') as file:
                        writer = csv.writer(file, delimiter=';')
                        writer.writerow(headers)
                    
                        for i in range(len(Time)):
                            row = [
                                Time[i],
                                Temperature_list[i],
                                Heat_release[i],
                                Pressure_list[i],
                                OH[i]
                            ]
                    
                            writer.writerow(row)
                
                   
                with open(IDT_csv, mode='w', newline='') as file:
                    writer = csv.writer(file, delimiter=';')
                    writer.writerow(headersIDT)
                    for i in range(len(Temperature)):
                        row = [
                            1000/Temperature[i],
                            IDT[i],
                        ]
                
                        writer.writerow(row)
                
                    

def PreProcess_Gas_Composition(mechanisms, MECH, Fuel_name, Oxi_name, Fuel, Oxidizer, configuration, file_path_csv, Verbosity_level):
    Temnperature     = configuration["conditions"]["Gas_Composition"]["Temperature"]
    Pressure         = configuration["conditions"]["Gas_Composition"]["Pressure"]
    Equivalent_Ratio = configuration["conditions"]["Gas_Composition"]["Phi"]
    
    Fresh_gas    = configuration["outputs"]["Gas_Composition"]["Fresh_gas"]
    Burn_gas     = configuration["outputs"]["Gas_Composition"]["Burn_gas"]
    
    indexMech=0
    
    for mech_name,mech_file in mechanisms.items():
        file_path_Composition_M_csv=create_folder(file_path_csv,f"{indexMech:02}-Kinetic_Mechanism Used-{mech_name}")
        indexMech+=1
        print(f"\n{'='*60}\n MÉCANISME : {mech_name}\n{'='*60}")
        
        for indexT,T in enumerate(Temnperature):
            file_path_Composition_M_T_csv=create_folder(file_path_Composition_M_csv,f"{indexT:02}-Initial_Temperature_{T:.2f}K")
            
            for indexP,P in enumerate(Pressure):
                file_path_Composition_M_T_P_csv=create_folder(file_path_Composition_M_T_csv,f"{indexP:02}-Initial_Pressure_{P:.2f}bars")
                
                       
                for indexPhi,eq_ratio in enumerate(Equivalent_Ratio):
                    file_path_Composition_M_T_P_phi_csv=create_folder(file_path_Composition_M_T_P_csv,f"{indexPhi:02}-Equivqlent_Ratio_{eq_ratio:.2f}")
                    print(f"→ Gas Composition: φ = {eq_ratio:.2f}   | T={T:.2f} K | P={P:.2f} bar")
                    print()
                    gas = ct.Solution(mech_file)
                    gas.set_equivalence_ratio(eq_ratio, Fuel, Oxidizer)
                    
                    if Fresh_gas is True:
                        Verbosity_Gas_Composition(Verbosity_level, gas, True)
                        
                        csv_file_path=os.path.join(file_path_Composition_M_T_P_phi_csv,f"Fresh_gas_results_{mech_name}_Species_Fuel{Fuel_name}_Oxidizer{Oxi_name}_at_T{T:.2f}K_P{P:.2f}_Phi{eq_ratio:.1f}.csv")
                        os.makedirs(os.path.dirname(csv_file_path), exist_ok=True)
                        
                        headers = [
                            "Temperature (K)",
                            "Pressure (Pa)",
                            "Density (kg/m3)",
                            "Mean Molecular Weight (kg/kmol)",
                            "Enthalpy (J/kg)",
                            "Internal Energy (J/kg)",
                            "Entropy (J/kg/K)",
                            "Gibbs (J/kg)",
                            "Cp (J/kg/K)",
                            "Cv (J/kg/K)"
                        ]
                        values = [gas.T,
                            gas.P,
                            gas.density,
                            gas.mean_molecular_weight,
                            gas.enthalpy_mass,
                            gas.int_energy_mass,
                            gas.entropy_mass,
                            gas.gibbs_mass,
                            gas.cp_mass,
                            gas.cv_mass
                        ]
                        
                        for specie in gas.species_names:
                            if gas[specie].Y[0] != 0:
                                headers.append(f"Y_{specie}")
                                values.append(gas[specie].Y[0])
                                headers.append(f"X_{specie}")
                                values.append(gas[specie].X[0])
                        
                        with open(csv_file_path, mode='w', newline='') as file:
                            writer = csv.writer(file, delimiter=';')  # ; mieux pour Excel FR
                            writer.writerow(headers)
                            writer.writerow(values)
                            
                    if Burn_gas is True:
                        gas.equilibrate("HP",solver="auto",rtol=1e-9)
                        
                        Verbosity_Gas_Composition(Verbosity_level, gas, False, Fresh_gas)
                        
                        csv_file_path=os.path.join(file_path_Composition_M_T_P_phi_csv,f"Burn_gas_results_{mech_name}_Species_Fuel{Fuel_name}_Oxidizer{Oxi_name}_at_T{T:.2f}K_P{P:.2f}_Phi{eq_ratio:.0f}.csv")
                        os.makedirs(os.path.dirname(csv_file_path), exist_ok=True)
                        
                        headers = [
                            "Temperature (K)",
                            "Pressure (Pa)",
                            "Density (kg/m3)",
                            "Mean Molecular Weight (kg/kmol)",
                            "Enthalpy (J/kg)",
                            "Internal Energy (J/kg)",
                            "Entropy (J/kg/K)",
                            "Gibbs (J/kg)",
                            "Cp (J/kg/K)",
                            "Cv (J/kg/K)"
                        ]
                        values = [gas.T,
                            gas.P,
                            gas.density,
                            gas.mean_molecular_weight,
                            gas.enthalpy_mass,
                            gas.int_energy_mass,
                            gas.entropy_mass,
                            gas.gibbs_mass,
                            gas.cp_mass,
                            gas.cv_mass
                        ]
                        
                        for specie in gas.species_names:
                            if gas[specie].Y[0] != 0:
                                headers.append(f"Y_{specie}")
                                values.append(gas[specie].Y[0])
                                headers.append(f"X_{specie}")
                                values.append(gas[specie].X[0])
                        
                        with open(csv_file_path, mode='w', newline='') as file:
                            writer = csv.writer(file, delimiter=';')  # ; mieux pour Excel FR
                            writer.writerow(headers)
                            writer.writerow(values)

                    
def PreProcess_Counter_flow(mechanisms, MECH, Fuel_name, Oxi_name, Fuel, Oxidizer, configuration, file_path_csv, Verbosity_level):
    Temperature      = configuration["conditions"]["Counter_flow"]["Temperature_pairs"]
    Pressure  = configuration["conditions"]["Counter_flow"]["Pressure"]
    Velocity_flow = configuration["conditions"]["Counter_flow"]["Velocity_flux_pairs"]
   
    Major_species          = configuration["outputs"]["Counter_flow"]["Major_species"]
    Radicals               = configuration["outputs"]["Counter_flow"]["Radicals"]
   

    indexMech=0        
    for mech_name,mech_file in mechanisms.items():
        file_path_CF_mech=create_folder(file_path_csv,f"{indexMech:02}-Kinetic_Mechanism_Used-{mech_name}")
        indexMech+=1
        print(f"\n{'='*60}\n MÉCANISME : {mech_name}\n{'='*60}")
        
        for indexT,T in enumerate(Temperature):
            print(f"\n--- Couple Temperature  : {T} K ---")
            file_path_CF_T=create_folder(file_path_CF_mech,f"{indexT:02}-Initial_Couple_Temperature_{T}K")
                       
            for indexP,P in enumerate(Pressure):
                file_path_CF_T_P=create_folder(file_path_CF_T,f"{indexP:02}-Initial_Pressure_{P:.2f}bars")
                 
                for indexVelo,Velo in enumerate(Velocity_flow):
                    print(f"   -> Counter Flow: Pressure : {P:.2f} bar / Velocity flow > Fuel:{Velo[0]} m/s Oxidizer:{Velo[1]} m/s")
                    file_path_CF_T_P_V=create_folder(file_path_CF_T_P,f"{indexVelo:02}-Couple_Mass_flow_{Velo}")
                    
                    CF_csv = os.path.join(file_path_CF_T_P_V, f"results_{mech_name}_Species_Fuel{Fuel_name}_Oxidizer{Oxi_name}_at_Tfuel{T[0]:.0f}_Toxi{T[1]:.0f}_P{P:.2f}.csv")
                    os.makedirs(os.path.dirname(CF_csv), exist_ok=True)
                    
                    comp_o = Oxidizer  # air composition
                    comp_f = Fuel  # fuel composition
                    
                    tin_f = T[0]  # fuel inlet temperature
                    tin_o = T[1]  # oxidizer inlet temperature
                    
                    gas_temp1 = ct.Solution(mech_file)
                    gas_temp1.TPX = tin_f, P*1e5, comp_f
                    rhoF = gas_temp1.density    # fuel inlet density
    
                    gas_temp2 = ct.Solution(mech_file)
                    gas_temp2.TPX = tin_o, P*1e5, comp_o
                    rhoO = gas_temp2.density    # oxidizer inlet density
                    
    
                    Velocity_f = Velo[0]  # m/s
                    Velocity_o = Velo[1]  # m/s
                      
                    mdot_f = rhoF * Velocity_f   # kg/m2/s
                    mdot_o = rhoO * Velocity_o   # kg/m2/s
                  
                    width = 0.02  # Distance between inlets is 2 cm
                    loglevel = 0
                    
                    gas = ct.Solution(mech_file)
                    gas.transport_model = 'Multi'
     
                    flame = ct.CounterflowDiffusionFlame(gas, width=width)
                    flame.P = P*1e5
     
                    flame.fuel_inlet.mdot = mdot_f
                    flame.fuel_inlet.X = comp_f
                    flame.fuel_inlet.T = tin_f 
                    flame.oxidizer_inlet.mdot = mdot_o
                    flame.oxidizer_inlet.X = comp_o
                    flame.oxidizer_inlet.T = tin_o
     
                    flame.boundary_emissivities = 0.0, 0.0
                    flame.radiation_enabled = False
     
                    flame.set_refine_criteria(ratio=5, slope=0.1, curve=0.2, prune=0.03)
     
                    flame.solve(loglevel, refine_grid=True, auto=True)
                    strain = np.gradient(flame.velocity, flame.grid)
                    mixture_fraction = flame.mixture_fraction(m="Bilger")
                    grad_T = np.gradient(flame.T, flame.grid)
                    no_rad = flame.to_array()
                    
                    Verbosity_Counter_flow(Verbosity_level, gas, flame) # Console verbiosity print
                    
                    headers = [
                        "Grid [m]",
                        "Temperature [K]",
                        "Heat Release [W/m3]",
                        "Axial Velocity [m/s]",
                        "Density [kg/m3]",
                        "cp [J/kg/K]",
                        "Thermal Conductivity [W/m/K]",
                        "Viscosity [Pa.s]",
                        "Strain rate [1/s]",
                        "dT/dx [K/m]",
                        "Mixture fraction [-]"
                    ]
                    species_mech = gas.species_names
                    for spe in Major_species + Radicals :
                        if spe in species_mech:
                            if gas[spe].Y[0] != 0:
                                headers.append(f"Y_{spe}")
                                headers.append(f"X_{spe}")
                        else: 
                            print(Fore.RED + f" WARNING: Species {spe} not in the mechanism {mech_name}")
                            
                    
                    with open(CF_csv, mode='w', newline='') as file:
                        writer = csv.writer(file, delimiter=';')
                        writer.writerow(headers)
                    
                        n_points = len(flame.grid)
                    
                        for i in range(n_points):
                            row = [
                                flame.grid[i],
                                flame.T[i],
                                flame.heat_release_rate[i],
                                flame.velocity[i],
                                flame.density[i],
                                flame.cp_mass[i],
                                flame.thermal_conductivity[i],
                                flame.viscosity[i],
                                strain[i],
                                grad_T[i],
                                mixture_fraction[i]
                                
                                
                            ]
                    
                            for spe in Major_species + Radicals :
                                if spe in species_mech:
                                    if gas[spe].Y[0] != 0:
                                        row.append(no_rad(spe).Y[i][0])
                                        row.append(no_rad(spe).X[i][0])
                                        
                    
                            writer.writerow(row)
   
    
def PreProcess_Counter_flow_quenching(mechanisms, MECH, Fuel_name, Oxi_name, Fuel, Oxidizer, configuration, file_path_csv, Verbosity_level):
    Temperature      = configuration["conditions"]["Counter_flow"]["Temperature_pairs"]
    Pressure  = configuration["conditions"]["Counter_flow"]["Pressure"]
    
    indexMech=0        
    for mech_name,mech_file in mechanisms.items():
        file_path_CF_mech=create_folder(file_path_csv,f"{indexMech:02}-Kinetic_Mechanism_Used-{mech_name}")
        indexMech+=1
        print(f"\n{'='*60}\n MÉCANISME : {mech_name}\n{'='*60}")
        
        for indexT,T in enumerate(Temperature):
            
            file_path_CF_T=create_folder(file_path_CF_mech,f"{indexT:02}-Initial_Couple_Temperature_{T}K")
                       
            for indexP,P in enumerate(Pressure):
                file_path_CF_T_P=create_folder(file_path_CF_T,f"{indexP:02}-Initial_Pressure_{P:.2f}bars")
                print(f"   -> Counter Flow Quenching: Pressure : {P:.2f} bar / Temperature flow > Fuel:{T[0]} K , Oxidizer:{T[1]} K")
                
                QCF_csv = os.path.join(file_path_CF_T_P, f"results_{mech_name}_Species_Fuel{Fuel_name}_Oxidizer{Oxi_name}_at_Tfuel{T[0]:.0f}_Toxi{T[1]:.0f}_P{P:.2f}.csv")
                os.makedirs(os.path.dirname(QCF_csv), exist_ok=True)
                
                Coef_Scaling_flame =[-1.0/2.0, 1.0/2.0, 1.0, 2.0, 1.0/2.0]
                exp_d_a, exp_u_a, exp_V_a, exp_lam_a, exp_mdot_a = Coef_Scaling_flame
                
                comp_o = Oxidizer  # air composition
                comp_f = Fuel  # fuel composition
                
                tin_f = T[0]  # fuel inlet temperature
                tin_o = T[1]  # oxidizer inlet temperature
                
                gas_temp1 = ct.Solution(mech_file)
                gas_temp1.TPX = tin_f, P*1e5, comp_f
                rhoF = gas_temp1.density    # fuel inlet density

                gas_temp2 = ct.Solution(mech_file)
                gas_temp2.TPX = tin_o, P*1e5, comp_o
                rhoO = gas_temp2.density    # oxidizer inlet density

                #Momentum conservation
                Velocity_o = 0.05  # m/s
                rho_frac = rhoO / rhoF
                Velocity_f = np.sqrt(rho_frac * Velocity_o ** 2)
                
                  
                mdot_f = rhoF * Velocity_f   # kg/m2/s
                mdot_o = rhoO * Velocity_o   # kg/m2/s
              
                width = 0.02  # Distance between inlets is 2 cm
                loglevel = 0
                
                gas = ct.Solution(mech_file)
                gas.transport_model = 'Multi'
 
                flame = ct.CounterflowDiffusionFlame(gas, width=width)
                flame.P = P*1e5
 
                flame.fuel_inlet.mdot = mdot_f
                flame.fuel_inlet.X = comp_f
                flame.fuel_inlet.T = tin_f 
                flame.oxidizer_inlet.mdot = mdot_o
                flame.oxidizer_inlet.X = comp_o
                flame.oxidizer_inlet.T = tin_o
 
                flame.boundary_emissivities = 0.0, 0.0
                flame.radiation_enabled = False
 
                flame.set_refine_criteria(ratio=5, slope=0.1, curve=0.2, prune=0.03)

                print('\t --> START Creating the initial solution')
                print(f'\t \t Oxidizer Velocity {Velocity_o}  |   Fuel Velocity: {Velocity_f}')
                flame.solve(loglevel, refine_grid=True, auto=True)
                print('\t Temperature flame:', np.max(flame.T))
                print('\t --> END Creating the initial solution')
                print('\n')
                


                # Define a limit for the maximum temperature below which the flame is
                # considered as extinguished and the computation is aborted
                # This increases the speed of refinement, if enabled
                temperature_limit_extinction = 800  # K


                def interrupt_extinction(t):
                    if np.max(flame.T) < temperature_limit_extinction:
                        raise FlameExtinguished('Flame extinguished')
                    return 0.


                flame.set_interrupt(interrupt_extinction)
                
                # flame.solve(loglevel=0, auto=True)
                
                n = 0
                n_last_burning = 0
                # Do the strain rate loop
                a_maxi             = []
                T_max              = []
                HRR_max            = []
                Fuel_mdot          = []
                Oxid_mdot          = []
                InletFuel_Velocity = []
                InletOxid_Velocity = []
                Max_dTdx           = []
                alpha = [1.0]
                while np.max(flame.T) > temperature_limit_extinction:
                    n += 1
                    alpha.append(alpha[n_last_burning] + 1.0)
                    strain_factor = alpha[-1] / alpha[n_last_burning]
                    n_last_burning = n
                
                    # Create an initial guess based on the previous solution
                    # Update grid
                    flame.flame.grid *= strain_factor ** exp_d_a
                    # Update mass fluxes
                    flame.fuel_inlet.mdot *= strain_factor ** exp_mdot_a
                    flame.oxidizer_inlet.mdot *= strain_factor ** exp_mdot_a
                    
                    # Update velocities
                    flame.flame.set_values("velocity", flame.flame.velocity * strain_factor ** exp_u_a)
                    flame.flame.set_values("spreadRate", flame.flame.spread_rate * strain_factor ** exp_V_a)
                    # Update pressure curvature
                    flame.flame.set_values(
                        "Lambda", flame.flame.radial_pressure_gradient * strain_factor ** exp_lam_a)
                    try:
                        # Try solving the flame
                        flame.solve(loglevel=0)
                        
                        #print information
                        Verbosity_Counter_flow_quenching(Verbosity_level, flame, n, strain_factor,Coef_Scaling_flame,alpha,flame.fuel_inlet.mdot,flame.oxidizer_inlet.mdot)
                    
                        # Save information
                        strain_maxi = np.max(np.abs(np.gradient(flame.velocity) / np.gradient(flame.grid)))
                        a_maxi.append(strain_maxi)
                        T_max.append(np.max(flame.T))
                        HRR_max.append(np.max(flame.heat_release_rate))
                        Fuel_mdot.append(flame.fuel_inlet.mdot)
                        Oxid_mdot.append(flame.oxidizer_inlet.mdot)
                        InletFuel_Velocity.append(flame.velocity[0])
                        InletOxid_Velocity.append(flame.velocity[-1])
                        Max_dTdx.append(np.max(np.gradient(flame.T, flame.grid)))
                        
                    except FlameExtinguished:
                        print('\t -- Flame extinguished')
                        break
                    except ct.CanteraError as e:
                        print('Error occurred while solving:', e)
                        break
                    
                headers = [
                    "Max strain [1/s]",
                    "Temperature max [K]",
                    "Heat Release max [W/m3]",
                    "Inlet fuel mass flow [kg/m2/s]",
                    "Inlet oxidizer mass flow [kg/m2/s]",
                    "Inlet fuel Axial Velocity [m/s]",
                    "Inlet oxidizer Axial Velocity [m/s]",
                    "dT/dx max [K/m]",
                    
                ]
                
                with open(QCF_csv, mode='w', newline='') as file:
                    writer = csv.writer(file, delimiter=';')
                    writer.writerow(headers)
                
                    for i in range(len(a_maxi)):
                        row = [
                            a_maxi[i],
                            T_max[i],
                            HRR_max[i],
                            Fuel_mdot[i],
                            Oxid_mdot[i],
                            InletFuel_Velocity[i],
                            InletOxid_Velocity[i],
                            Max_dTdx[i],
                        ]
                
                        writer.writerow(row)
            
               
          