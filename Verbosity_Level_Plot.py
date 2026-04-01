"""
# ===================================================================================================================
#  Verbosity Level PreProcessing file:
# ===================================================================================================================
#
#  Author          : Lilian CHAPUIS
#  Affiliation     : IMFT - Institut de Mécanique des Fluides de Toulouse
#  Location        : Toulouse, France
#  Creation Date   : 24 February 2026
#  Last Modified   : 24 February 2026
#  Version         : 1.0.01
#
# -------------------------------------------------------------------------------------------------------------------
#  DESCRIPTION
# -------------------------------------------------------------------------------------------------------------------
#  This module centralizes verbosity and runtime monitoring management
#  for combustion simulations executed with Cantera_proc.py.
#
#  It provides structured printing and optional live feedback depending
#  on the selected verbosity level defined in the YAML configuration file.
#
#
#  Each function adapts printed information according to the selected
#  verbosity level (0 → minimal, 1 → intermediate, 2 → detailed).
#
#  This design ensures consistent and scalable runtime monitoring
#  without overloading the main computational workflow.
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

def Verbosity_Flame1D(level_verbosity, gas, flame):
    if level_verbosity == 1:
        print("\t \t --------------------------------------------------")
        print(f"\t \t \t \t Verbosity LEVEL: {level_verbosity}")
        print("\t \t --------------------------------------------------")
        print(f"\t \t Flame speed (Sl)         : {flame.velocity[0]:.5e} m/s")
        print(f"\t \t Flame thickness          : {(flame.T.max()-flame.T.min())/np.max(np.abs(np.gradient(flame.T, flame.grid)))*1e3:.5e} mm")
        print(f"\t \t Finale Temperature (T)   : {gas.T:.3f} K")
        print(f"\t \t Max HRR (W/m3)           : {np.max(gas.heat_release_rate):.3f} W/m3")
        print("\t \t --------------------------------------------------")

    elif level_verbosity == 2:
        print("\t \t --------------------------------------------------")
        print(f"\t \t \t \t Verbosity LEVEL: {level_verbosity}")
        print("\t \t --------------------------------------------------")
        print(f"\t \t Finale Temperature (T)   : {gas.T:.3f} K")
        print(f"\t \t Pressure (bar)           : {gas.P/1e5:.5f}")
        print(f"\t \t Flame speed (Sl)         : {flame.velocity[0]:.5e} m/s")
        print(f"\t \t Flame thickness          : {(flame.T.max()-flame.T.min())/np.max(np.abs(np.gradient(flame.T, flame.grid)))*1e3:.5e} mm")
        print(f"\t \t Damköhler number (Da)    : {((flame.T.max()-flame.T.min())/np.max(np.abs(np.gradient(flame.T, flame.grid)))/flame.velocity[0])**2:.5e}")
        print("\t \t --------------------------------------------------")
        print("\t \t  Major species (Y > 1e-4):")
        for i, Y in enumerate(gas.Y):
            if Y > 1e-3:
                print(f"\t \t   - {gas.species_name(i)} : Y={Y:.6e} | X={gas.X[i]:.6e}")
        print("\t \t --------------------------------------------------")

    elif level_verbosity == 3:
        print("\t \t --------------------------------------------------")
        print(f"\t \t \t \t Verbosity LEVEL: {level_verbosity}")
        print("\t \t --------------------------------------------------")
        print(f"\t \t Flame Temperature Profile : T_min={flame.T.min():.6f} K | T_max={flame.T.max():.6f} K")
        print(f"\t \t Pressure (Pa)             : {gas.P:.6f} Pa")
        print(f"\t \t Pressure (bar)            : {gas.P/1e5:.6f} bar")
        print(f"\t \t Density                   : {gas.density:.6f} kg/m³")
        print(f"\t \t Specific Enthalpy         : {gas.enthalpy_mass:.8e} J/kg")
        print(f"\t \t Specific Internal Energy  : {gas.int_energy_mass:.8e} J/kg")
        print(f"\t \t Specific Entropy          : {gas.entropy_mass:.8e} J/kg/K")
        print(f"\t \t Cp (mass basis)           : {gas.cp_mass:.8f} J/kg/K")
        print(f"\t \t Cv (mass basis)           : {gas.cv_mass:.8f} J/kg/K")
        print("\t \t --------------------------------------------------")
        print("\t \t  Major species (Y > 1e-4):")
        for i, Y in enumerate(gas.Y):
            if Y > 1e-4:
                print(f"\t \t   - {gas.species_name(i)} : Y={Y:.6e} | X={gas.X[i]:.6e}")
        print("\t \t --------------------------------------------------")
        print("\t \t  Flame Metrics:")
        Temp = flame.T
        x = flame.grid
        dTdx = np.gradient(Temp, x)
        thickness = (Temp.max() - Temp.min()) / np.max(np.abs(dTdx))
        Sl = flame.velocity[0]
        flame_time_ms = (thickness / Sl) * 1e-3
        lambda_ = flame.thermal_conductivity[0]
        rho = gas.density
        cp = gas.cp_mass
        alpha = lambda_ / (rho * cp)
        tau_diff = thickness**2 / alpha
        tau_chem = thickness / Sl
        Da = tau_diff / tau_chem
        print(f"\t \t   - Flame speed (Sl)         : {flame.velocity[0]:.5e} m/s")
        print(f"\t \t   - Flame Thickness        : {thickness*1e3:.6e} mm")
        print(f"\t \t   - Max Gradient T        : {np.max(np.abs(dTdx)):.6e} K/m")
        print(f"\t \t   - Flame Time             : {flame_time_ms:.6e} ms")
        print(f"\t \t   - Damköhler Number       : {Da:.6e}")
        print("\t \t --------------------------------------------------")
   
def Verbosity_Temperature_Adiabatic(level_verbosity,gas):   
    if level_verbosity == 1:
        print("\t \t --------------------------------------------------")
        print(f"\t \t Verbosity LEVEL: {level_verbosity} ")
        print("\t \t --------------------------------------------------")
        print(f"\t \t  Initial Temperature : {gas.T:.2f} K")
        print(f"\t \t  Pressure           : {gas.P/1e5:.3f} bar")
        print("\t \t  Mixture initialized.")
        print("\t \t --------------------------------------------------")
        print()

    
    elif level_verbosity == 2:
        print("\t \t --------------------------------------------------")
        print(f"\t \t Verbosity LEVEL: {level_verbosity} ")
        print("\t \t --------------------------------------------------")
        print(f"\t \t Temperature (T)          : {gas.T:.3f} K")
        print(f"\t \t Pressure (P)             : {gas.P/1e5:.5f} bar")
        print(f"\t \t Density                  : {gas.density:.5f} kg/m³")
        print(f"\t \t Specific Enthalpy        : {gas.enthalpy_mass:.5e} J/kg")
        print(f"\t \t Specific Internal Energy : {gas.int_energy_mass:.5e} J/kg")
        print(f"\t \t Cp (mass basis)          : {gas.cp_mass:.5f} J/kg/K")
        print("\t \t Number of species         :", gas.n_species)
        print("\t \t --------------------------------------------------")
        print()

        
    elif level_verbosity == 3:
       print("\t \t --------------------------------------------------")
       print(f"\t \t Verbosity LEVEL: {level_verbosity} ")
       print("\t \t --------------------------------------------------")
       print(f"\t \t Temperature (T)        : {gas.T:.6f} K")
       print(f"\t \t Pressure (Pa)          : {gas.P:.2f} Pa")
       print(f"\t \t Pressure (bar)         : {gas.P/1e5:.6f} bar")
       print(f"\t \t Density                : {gas.density:.6f} kg/m³")
       print(f"\t \t Specific Enthalpy      : {gas.enthalpy_mass:.8e} J/kg")
       print(f"\t \t Specific Entropy       : {gas.entropy_mass:.8e} J/kg/K")
       print(f"\t \t Cp (mass basis)        : {gas.cp_mass:.8f} J/kg/K")
       print(f"\t \t Cv (mass basis)        : {gas.cv_mass:.8f} J/kg/K")
       print(f"\t \t Mean Molecular Weight  : {gas.mean_molecular_weight:.6f} kg/kmol")
       print("\t \t --------------------------------------------------")
       print("\t \t  Major species (Y > 1e-4):")
       print()
       
       for i, Y in enumerate(gas.Y):
           if Y > 1e-4:
               print(f"\t \t   - {gas.species_name(i)} : {Y:.6e}")
       
       print("\t \t --------------------------------------------------")
       print()

def Verbosity_IDT(level_verbosity,gas, IDT, i_max):
    if level_verbosity == 1:
        print("\t \t --------------------------------------------------")
        print(f"\t \t Verbosity LEVEL: {level_verbosity} ")
        print("\t \t --------------------------------------------------")
        print(f"\t \t Ignition Delay Time    : {IDT:.3f} ms")
        print("\t \t --------------------------------------------------")
        print()


    elif level_verbosity == 2:
        print("\t \t --------------------------------------------------")
        print(f"\t \t Verbosity LEVEL: {level_verbosity} ")
        print("\t \t --------------------------------------------------")
        print(f"\t \t Ignition Delay Time    : {IDT:.6f} ms")
        print(f"\t \t Reactor Temperature    : {gas.T:.4f} K")
        print(f"\t \t Reactor Pressure       : {gas.P/1e5:.5f} bar")
        print(f"\t \t Heat Release Rate      : {gas.heat_release_rate/1e6:.6e} MW/m³")
        print("\t \t --------------------------------------------------")
        print()


    elif level_verbosity == 3:
       print("\t \t --------------------------------------------------")
       print(f"\t \t Verbosity LEVEL: {level_verbosity} ")
       print("\t \t --------------------------------------------------")
       print(f"\t \t Ignition Delay Time    : {IDT:.8f} ms")
       print("\t \t --------------------------------------------------")
       print(f"\t \t Reactor Temperature        : {gas.T:.6f} K")
       print(f"\t \t Reactor Pressure (Pa)      : {gas.P:.6f} Pa")
       print(f"\t \t Reactor Pressure (bar)     : {gas.P/1e5:.6f} bar")
       print(f"\t \t Reactor Density            : {gas.density:.6f} kg/m³")
       print(f"\t \t Reactor Specific Enthalpy  : {gas.enthalpy_mass:.8e} J/kg")
       print(f"\t \t Reactor Specific Entropy   : {gas.entropy_mass:.8e} J/kg/K")
       print(f"\t \t Reactor Cp (mass basis)    : {gas.cp_mass:.8f} J/kg/K")
       print(f"\t \t Reactor Cv (mass basis)    : {gas.cv_mass:.8f} J/kg/K")
       print(f"\t \t Mean Molecular Weight      : {gas.mean_molecular_weight:.6f} kg/kmol")
       print("\t \t --------------------------------------------------")
       print("\t \t  Major species (Y > 1e-4):")
       
       for i, Y in enumerate(gas.Y):
           if Y > 1e-4:
               print(f"\t \t   - {gas.species_name(i)} : {Y:.6e}")
       
       print("\t \t --------------------------------------------------")
       print()
 
def Verbosity_Gas_Composition(level_verbosity, gas, Bool_type_Gas, Fresh_gas_plot=None ):
    if Bool_type_Gas is True:
        if level_verbosity == 1:
            print("\t \t --------------------------------------------------")
            print(f"\t \t \t \t Verbosity LEVEL: {level_verbosity} ")
            print("\t \t --------------------------------------------------")
            print(f"\t \t \t \t FRESH gas composition ")
            print("\t \t --------------------------------------------------")
            print(f"\t \t Temperature            : {gas.T:.2f} K")
            print(f"\t \t Pressure               : {gas.P/1e5:.3f} bar")
            print("\t \t --------------------------------------------------")
            print("\t \t  Major species (Y > 1e-4):")
            
            for i, Y in enumerate(gas.Y):
                if Y > 1e-3:
                    print(f"\t \t   - {gas.species_name(i)} : Y={Y:.6e} | X={gas.X[i]:.6e}")
            
            print("\t \t --------------------------------------------------")
       
    
    
        elif level_verbosity == 2:
            print("\t \t --------------------------------------------------")
            print(f"\t \t \t \t Verbosity LEVEL: {level_verbosity} ")
            print("\t \t --------------------------------------------------")
            print(f"\t \t \t \t FRESH gas composition ")
            print("\t \t --------------------------------------------------")
            print(f"\t \t Temperature (T)        : {gas.T:.4f} K")
            print(f"\t \t Pressure (bar)         : {gas.P/1e5:.5f} bar")
            print(f"\t \t Density                : {gas.density:.5f} kg/m³")
            print(f"\t \t Mean Molecular Weight  : {gas.mean_molecular_weight:.6f} kg/kmol")
            print(f"\t \t Enthalpy               : {gas.enthalpy_mass:.6e} J/kg")
            print(f"\t \t Entropy                : {gas.entropy_mass:.6e} J/kg/K")
            print("\t \t --------------------------------------------------")
            print("\t \t  Major species (Y > 1e-4):")
            
            for i, Y in enumerate(gas.Y):
                if Y > 1e-3:
                    print(f"\t \t   - {gas.species_name(i)} : Y={Y:.6e} | X={gas.X[i]:.6e}")
            
            print("\t \t --------------------------------------------------")
        
    
    
        elif level_verbosity == 3:
            print("\t \t --------------------------------------------------")
            print(f"\t \t \t \t Verbosity LEVEL: {level_verbosity} ")
            print("\t \t --------------------------------------------------")
            print(f"\t \t \t \t FRESH gas composition ")
            print("\t \t --------------------------------------------------")
            print(f"\t \t Temperature (T)        : {gas.T:.6f} K")
            print(f"\t \t Pressure (Pa)          : {gas.P:.6f} Pa")
            print(f"\t \t Pressure (bar)         : {gas.P/1e5:.6f} bar")
            print(f"\t \t Density                : {gas.density:.6f} kg/m³")
            print(f"\t \t Specific Enthalpy      : {gas.enthalpy_mass:.8e} J/kg")
            print(f"\t \t Specific Internal En.  : {gas.int_energy_mass:.8e} J/kg")
            print(f"\t \t Specific Entropy       : {gas.entropy_mass:.8e} J/kg/K")
            print(f"\t \t Gibbs Free Energy      : {gas.gibbs_mass:.8e} J/kg")
            print(f"\t \t Cp (mass basis)        : {gas.cp_mass:.8f} J/kg/K")
            print(f"\t \t Cv (mass basis)        : {gas.cv_mass:.8f} J/kg/K")
            print(f"\t \t Mean Molecular Weight  : {gas.mean_molecular_weight:.6f} kg/kmol")
            print("\t \t --------------------------------------------------")
            print("\t \t  Major species (Y > 1e-4):")
           
            for i, Y in enumerate(gas.Y):
               if Y > 1e-5:
                   print(f"\t \t   - {gas.species_name(i)} : Y={Y:.6e} | X={gas.X[i]:.6e}")
           
            print("\t \t --------------------------------------------------")
        
           
            
    if Bool_type_Gas is False:
        if Fresh_gas_plot is False and level_verbosity != 0:
            print("\t \t --------------------------------------------------")
            print(f"\t \t \t \t Verbosity LEVEL: {level_verbosity} ")
            
        if level_verbosity == 1:
            
            print("\t \t --------------------------------------------------")
            print(f"\t \t \t \t BURN gas composition ")
            print("\t \t --------------------------------------------------")
            print(f"\t \t Temperature            : {gas.T:.2f} K")
            print(f"\t \t Pressure               : {gas.P/1e5:.3f} bar")
            print("\t \t --------------------------------------------------")
            print("\t \t  Major species (Y > 1e-4):")
            
            for i, Y in enumerate(gas.Y):
                if Y > 1e-3:
                    print(f"\t \t   - {gas.species_name(i)} : Y={Y:.6e} | X={gas.X[i]:.6e}")
            
            print("\t \t --------------------------------------------------")
            print()
    
    
        elif level_verbosity == 2:
            
            print("\t \t --------------------------------------------------")
            print(f"\t \t \t \t BURN gas composition ")
            print("\t \t --------------------------------------------------")
            print(f"\t \t Temperature (T)        : {gas.T:.4f} K")
            print(f"\t \t Pressure (bar)         : {gas.P/1e5:.5f} bar")
            print(f"\t \t Density                : {gas.density:.5f} kg/m³")
            print(f"\t \t Mean Molecular Weight  : {gas.mean_molecular_weight:.6f} kg/kmol")
            print(f"\t \t Enthalpy               : {gas.enthalpy_mass:.6e} J/kg")
            print(f"\t \t Entropy                : {gas.entropy_mass:.6e} J/kg/K")
            print("\t \t --------------------------------------------------")
            print("\t \t  Major species (Y > 1e-4):")
            
            for i, Y in enumerate(gas.Y):
                if Y > 1e-3:
                    print(f"\t \t   - {gas.species_name(i)} : Y={Y:.6e} | X={gas.X[i]:.6e}")
            
            print("\t \t --------------------------------------------------")
            print()
    
    
        elif level_verbosity == 3:
            
            print("\t \t --------------------------------------------------")
            print(f"\t \t \t \t BURN gas composition ")
            print("\t \t --------------------------------------------------")
            print(f"\t \t Temperature (T)        : {gas.T:.6f} K")
            print(f"\t \t Pressure (Pa)          : {gas.P:.6f} Pa")
            print(f"\t \t Pressure (bar)         : {gas.P/1e5:.6f} bar")
            print(f"\t \t Density                : {gas.density:.6f} kg/m³")
            print(f"\t \t Specific Enthalpy      : {gas.enthalpy_mass:.8e} J/kg")
            print(f"\t \t Specific Internal En.  : {gas.int_energy_mass:.8e} J/kg")
            print(f"\t \t Specific Entropy       : {gas.entropy_mass:.8e} J/kg/K")
            print(f"\t \t Gibbs Free Energy      : {gas.gibbs_mass:.8e} J/kg")
            print(f"\t \t Cp (mass basis)        : {gas.cp_mass:.8f} J/kg/K")
            print(f"\t \t Cv (mass basis)        : {gas.cv_mass:.8f} J/kg/K")
            print(f"\t \t Mean Molecular Weight  : {gas.mean_molecular_weight:.6f} kg/kmol")
            print("\t \t --------------------------------------------------")
            print("\t \t  Major species (Y > 1e-4):")
           
            for i, Y in enumerate(gas.Y):
               if Y > 1e-5:
                   print(f"\t \t   - {gas.species_name(i)} : Y={Y:.6e} | X={gas.X[i]:.6e}")
           
            print("\t \t --------------------------------------------------")
            print()    
               
def Verbosity_Counter_flow(level_verbosity, gas, flame):
    
    if level_verbosity == 1:
        Temp = flame.T
        print("\t \t --------------------------------------------------")
        print(f"\t \t Verbosity LEVEL: {level_verbosity}")
        print("\t \t --------------------------------------------------")
        print(f"\t \t Max Temperature          : {Temp.max():.6f} K")
        print(f"\t \t Max strain rate          : {np.max(np.gradient(flame.velocity, flame.grid)):.6e} 1/s")
        print("\t \t --------------------------------------------------")

    elif level_verbosity == 2:
        Temp = flame.T
        print("\t \t --------------------------------------------------")
        print(f"\t \t Verbosity LEVEL: {level_verbosity}")
        print("\t \t --------------------------------------------------")
        print(f"\t \t Max Temperature           : {Temp.max():.6f} K")
        print(f"\t \t Max strain rate           : {np.max(np.gradient(flame.velocity, flame.grid)):.6e} 1/s")
        print(f"\t \t Density                   : {gas.density:.5f} kg/m³")
        print(f"\t \t Max temperature gradient  : {np.max(np.gradient(flame.T, flame.grid)):.6e} K/m")
        print("\t \t --------------------------------------------------")

    elif level_verbosity == 3:
        print("\t \t --------------------------------------------------")
        print(f"\t \t Verbosity LEVEL: {level_verbosity}")
        print("\t \t --------------------------------------------------")
        print(f"\t \t Density                     : {gas.density:.6f} kg/m³")
        print(f"\t \t Max temperature gradient    : {np.max(np.gradient(flame.T, flame.grid)):.6e} K/m")
        print(f"\t \t Specific Enthalpy           : {gas.enthalpy_mass:.8e} J/kg")
        print(f"\t \t Specific Internal Energy    : {gas.int_energy_mass:.8e} J/kg")
        print(f"\t \t Specific Entropy            : {gas.entropy_mass:.8e} J/kg/K")
        print(f"\t \t Cp (mass basis)             : {gas.cp_mass:.8f} J/kg/K")
        print(f"\t \t Cv (mass basis)             : {gas.cv_mass:.8f} J/kg/K")
        print(f"\t \t Mean Molecular Weight       : {gas.mean_molecular_weight:.6f} kg/kmol")
        print("\t \t --------------------------------------------------")
        print("\t \t  Major species (Y > 1e-4):")
        for i, Y in enumerate(gas.Y):
            if Y > 1e-4:
                print(f"\t \t   - {gas.species_name(i)} : Y={Y:.6e} | X={gas.X[i]:.6e}")
        print("\t \t --------------------------------------------------")
        print("\t \t  Flame Profiles:")
        Temp = flame.T
        x = flame.grid
        dTdx = np.gradient(Temp, x)
        strain = np.gradient(flame.velocity, x)
        print(f"\t \t   - Max Temperature       : {Temp.max():.6f} K")
        print(f"\t \t   - Max dT/dx             : {np.max(dTdx):.6e} K/m")
        print(f"\t \t   - Max Strain Rate       : {np.max(strain):.6e} 1/s")
        print("\t \t --------------------------------------------------")

def Verbosity_Counter_flow_quenching(level_verbosity, flame, n, strain_factor,Coef_Scaling_flame,alpha, Fuel_inlet_mdot,oxidizer_inlet_mdot):
    
    # -------------------------------
    # Verbosity LEVEL 0
    # -------------------------------
    strain_maxi = np.max(np.abs(np.gradient(flame.velocity) / np.gradient(flame.grid)))
    if level_verbosity == 1 and n % 30 == 0:
        print("\t \t --------------------------------------------------")
        print(f"\t \t Verbosity LEVEL: {level_verbosity}")
        print("\t \t --------------------------------------------------")
        print("\t \t --------------------------------------------------")
        print(f"\t \t Strain Iteration       : {n}")
        print(f"\t \t Strain maxi            : { strain_maxi:.4f}")
        print(f"\t \t Current Tmax           : {np.max(flame.T):.6f} K")
        print(f"\t \t Strain factor          : {strain_factor:.6f}")
        print("\t \t --------------------------------------------------")

    # -------------------------------
    # Verbosity LEVEL 1
    # -------------------------------
    elif level_verbosity == 2 and n % 10 == 0:
        exp_d_a, exp_u_a, exp_V_a, exp_lam_a, exp_mdot_a = Coef_Scaling_flame
        print("\t \t --------------------------------------------------")
        print(f"\t \t Verbosity LEVEL: {level_verbosity}")
        print("\t \t --------------------------------------------------")
        print("\t \t --------------------------------------------------")
        print(f"\t \t Strain Iteration           : {n}")
        print(f"\t \t Strain maxi                : { strain_maxi:.4f}")
        print(f"\t \t Strain factor              : {strain_factor:.6f}")
        print(f"\t \t Current Tmax               : {np.max(flame.T):.6f} K")
        print(f"\t \t Alpha(n)                   : {alpha[-1]:.6f}")
        print(f"\t \t Grid scaling factor        : {strain_factor ** exp_d_a:.6e}")
        print(f"\t \t mdot scaling factor        : {strain_factor ** exp_mdot_a:.6e}")
        print(f"\t \t Velocity scaling factor    : {strain_factor ** exp_u_a:.6e}")
        print(f"\t \t Spread scaling factor      : {strain_factor ** exp_V_a:.6e}")
        print(f"\t \t Lambda scaling factor      : {strain_factor ** exp_lam_a:.6e}")
        print("\t \t --------------------------------------------------")

    # -------------------------------
    # Verbosity LEVEL 2
    # -------------------------------
    elif level_verbosity == 3 and n % 2 == 0:
        exp_d_a, exp_u_a, exp_V_a, exp_lam_a, exp_mdot_a = Coef_Scaling_flame
        print("\t \t --------------------------------------------------")
        print(f"\t \t Verbosity LEVEL: {level_verbosity}")
        print("\t \t --------------------------------------------------")
        print("\t \t --------------------------------------------------")
        print(f"\t \t Strain Iteration           : {n}")
        print(f"\t \t Strain maxi                : { strain_maxi:.4f}") 
        print(f"\t \t Strain factor              : {strain_factor:.6f}")
        print(f"\t \t Current Tmax               : {np.max(flame.T):.6f} K")
        print(f"\t \t Alpha(n)                   : {alpha[-1]:.6f}")
        print(f"\t \t Grid scaling factor        : {strain_factor ** exp_d_a:.6e}")
        print(f"\t \t mdot scaling factor        : {strain_factor ** exp_mdot_a:.6e}")
        print(f"\t \t Velocity scaling factor    : {strain_factor ** exp_u_a:.6e}")
        print(f"\t \t Spread scaling factor      : {strain_factor ** exp_V_a:.6e}")
        print(f"\t \t Lambda scaling factor      : {strain_factor ** exp_lam_a:.6e}")
        print("\t \t --------------------------------------------------")
        print("\t \t  New flow injection:")
        print(f"\t \t Fuel Injection             : {Fuel_inlet_mdot:.2e}")
        print(f"\t \t Oxidizer Injection         : {oxidizer_inlet_mdot:.2e}")
        print("\t \t --------------------------------------------------")
   
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    