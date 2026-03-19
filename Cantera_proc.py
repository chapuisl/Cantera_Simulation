"""
# ===================================================================================================================
#  Cantera Simulation Main Code
# ===================================================================================================================
#
#  Author          : Lilian CHAPUIS
#  Affiliation     : IMFT - Institut de Mécanique des Fluides de Toulouse
#  Location        : Toulouse, France
#  Creation Date   : 10 January 2026
#  Last Modified   : 17 February 2026
#  Version         : 1.0.02
#
# -------------------------------------------------------------------------------------------------------------------
#  DESCRIPTION
# -------------------------------------------------------------------------------------------------------------------
#  This configuration file defines all parameters required to run the Cantera-based combustion simulations.
#  It allows the user to control:
#      - Simulation type
#      - Mixture composition
#      - Thermodynamic operating conditions
#      - Kinetic mechanisms
#      - Output and post-processing options
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

from Input_yaml_Reading import check_file_Parameters_yaml as module_check
from Common_Utils_tools import create_folder

from PreProcessing import PreProcess_Counter_flow_quenching
from PreProcessing import PreProcess_Temperature_Adiabatic
from PreProcessing import PreProcess_Gas_Composition
from PreProcessing import PreProcess_Counter_flow
from PreProcessing import PreProcess_Flame1D
from PreProcessing import PreProcess_IDT

from PostProcessing import PostProcess_Counter_flow_quenching
from PostProcessing import PostProcess_Temperature_Adiabatic
from PostProcessing import PostProcess_Gas_Composition
from PostProcessing import PostProcess_Counter_flow
from PostProcessing import PostProcess_Flame1D
from PostProcessing import PostProcess_IDT

import Common_Utils_tools as Commom_Tool
import Graphic_Configuration as GC 


"""
# ===================================================================================================================
#  Import library
# ===================================================================================================================
"""
from colorama import Fore,Style
from datetime import datetime
from colorama import init
init(autoreset=True)
import os, psutil
import time
import sys

import cProfile
import pstats

"""
# ===================================================================================================================
#  Class
# ===================================================================================================================
"""
class Tee:
    def __init__(self, folder, filename):
        os.makedirs(folder, exist_ok=True)
        filepath = os.path.join(folder, filename)

        self.file = open(filepath, "w", encoding="utf-8")
        self.stdout = sys.stdout

    def write(self, message):
        self.file.write(message)
        self.stdout.write(message)

    def flush(self):
        self.file.flush()
        self.stdout.flush()
"""
# ===================================================================================================================
#  Function
# ===================================================================================================================
"""

# Fonction principale du calcul 
#
# @param parameter_coupling        : Fichier .dat contenant les variables du calcul
# @param file_name                 : Nom du fichier d'enregistrement des résulats
#
# @return None        
def main_process(parameter_coupling):
    GC.config_plot()
    
    # ===================================================
    # PARAMETERS  INITIALISATION
    # ===================================================
    print(Fore.GREEN +"  > START INITIALISATION ")
    print(f"\t \t > Start Reading file '{parameter_coupling}' for Initialisation ")

    process = psutil.Process(os.getpid())
    print("\t \t > Mémoire utilisée :", process.memory_info().rss / 1e6, "MB")

    
    ## Reading of the parameter coupling file
    configuration  = module_check(parameter_coupling)
    
    ## Initialisation of all the file needed
    file = configuration["path_file"]["filename"]
    file_name = configuration["path_file"]["directory"]+ '/' + file

    
    subfolders = Commom_Tool.backup_file(parameter_coupling,file_name )

    ## Print log in the file simulation.log
    timestamp = datetime.now().strftime("%d-%m-%Y_%Hh%M")
    sys.stdout = Tee(file_name, f"simulation_{timestamp}.log")
    
    ## Extraction of each parameter features and values
    mechanisms       = configuration["mechanisms"]
    Save_plot        = configuration["save_plot"]
    Verbosity_level  = configuration["verbosity_level"]
    Fuel             = configuration["fuel"]
    Oxidizer         = configuration["oxidizer"]
    
    Flame_1D            = configuration["simulation_type"]["Flame_1D"]
    Ignition_Delay_Time = configuration["simulation_type"]["Ignition_Delay_time"]
    Adiabatic_Temp      = configuration["simulation_type"]["Temperature_Adiabatic"]
    Counter_flow        = configuration["simulation_type"]["Counter_flow"]
    Gas_Composition     = configuration["simulation_type"]["Gas_Composition"]
    ## Writing in the Cantera format the Fuel and Oxidizer input 
    Fuel, Oxidizer, Fuel_name, Oxi_name, MECH = Commom_Tool.Prepare_simulation_inputs(Fuel, Oxidizer, mechanisms)
        
    print("═" * 85)
                            
    if Flame_1D is True:
        Bash_Temp_Flame1D      = configuration["conditions"]["Flame_1D"]["Temperature"]
        Bash_Pressure_Flame1D  = configuration["conditions"]["Flame_1D"]["Pressure"]
        Bash_EquiRatio_Flame1D = configuration["conditions"]["Flame_1D"]["Phi"]
        
        AVBP_sol         = configuration["outputs"]["Flame_1D"]["save_AVBP_solution"]
        Flame_speed      = configuration["outputs"]["Flame_1D"]["flame_speed"]
        Flame_Time       = configuration["outputs"]["Flame_1D"]["flame_time"]
        Flame_thickness  = configuration["outputs"]["Flame_1D"]["flame_thickness"]
        Emissions        = configuration["outputs"]["Flame_1D"]["emissions"]
        Major_species    = configuration["outputs"]["Flame_1D"]["Major_species"]
        Radicals         = configuration["outputs"]["Flame_1D"]["Radicals"]
        
        
        print(Fore.YELLOW + f"""
        #####################################################################
        #                                                                   #
        #                    1D FLAME SIMULATION                            #
        #                                                                   #
        #####################################################################
        """)
        print(Fore.YELLOW + 80*"_")
        print(Fore.YELLOW + 80*"-")
        print(f"""
         MIXTURE INFORMATION:
              Fuel composition             :  {Fuel}
              Oxidizer composition         :  {Oxidizer}
         -----------------------------------------------------------
         Mechanisms                        :  {MECH}
         Number of Pressure Point          :  {len(Bash_Pressure_Flame1D)} 
         Number of Temeprature Point       :  {len(Bash_Temp_Flame1D)} 
         Number of Equivalent ratio Point  :  {len(Bash_EquiRatio_Flame1D)} 
         Total Number calcul point         :  {len(MECH)*len(Bash_Pressure_Flame1D) * len(Bash_Temp_Flame1D) * len(Bash_EquiRatio_Flame1D)}
        
         -----------------------------------------------------------
        
         SAVE Flame sumilation        : {AVBP_sol}
         SAVE Plot Flame Speed        : {Flame_speed}
         SAVE Plot Flame Time         : {Flame_Time}
         SAVE Plot Flame Thickmess    : {Flame_thickness}
         SAVE Plot Flame Emissions    : {Emissions}
         Major Species focus          : {Major_species}
         Radical Species focus        : {Radicals}
         -----------------------------------------------------------
        
         -----------------------------------------------------------
        
        """)

        print(Fore.YELLOW + 80*"_")
        print(Fore.YELLOW + 80*"-")
        time.sleep(2.5)   
        
        file_path_flame_csv = create_folder(file_name +"/" + subfolders[3], "00-Flame_1D")
        file_path_flame = create_folder(file_name + "/" + subfolders[0], "00-Flame_1D")
        
        if Emissions is True:
            file_path_species = create_folder(file_name + "/" + subfolders[1], "00-Flame_1D")
        else:
            file_path_species = None
        
        if AVBP_sol is True:
            file_path_AVBP = create_folder(file_name +"/" + subfolders[4], "00-Flame_1D")
        else:
            file_path_AVBP = None
            
        print(Fore.WHITE + """
        ############################################################
        #                                                          #         
        #                     PRE-PROCESSING                       #
        #                                                          #
        ############################################################
        """)
        print(Style.RESET_ALL)

        PreProcess_Flame1D(mechanisms, 
                           MECH, 
                           Fuel_name, 
                           Oxi_name,
                           Fuel,
                           Oxidizer, 
                           configuration, 
                           file_path_flame_csv,
                           file_path_AVBP,
                           Verbosity_level)
                                 
        print(Fore.YELLOW + 80*"_")
        print(Fore.YELLOW + 80*"-")
        print(Fore.WHITE + """
        ############################################################
        #                                                          #         
        #                     POST-PROCESSING                      #
        #                                                          #
        ############################################################
        """)
        print(Style.RESET_ALL)
        
        PostProcess_Flame1D(mechanisms, 
                            MECH, 
                            Fuel_name, 
                            Oxi_name, 
                            configuration, 
                            file_path_flame_csv,
                            file_path_flame,
                            file_path_species,
                            Save_plot)
   
    if Ignition_Delay_Time is True:  
        Bash_Temp_IDT      = configuration["conditions"]["Ignition_Delay_time"]["Temperature"]
        Bash_Pressure_IDT  = configuration["conditions"]["Ignition_Delay_time"]["Pressure"]
        Bash_EquiRatio_IDT = configuration["conditions"]["Ignition_Delay_time"]["Phi"]
        
        IDT_plot           = configuration["outputs"]["Ignition_Delay_time"]["IDT_plot"]
        Time_evolution     = configuration["outputs"]["Ignition_Delay_time"]["time_evolution"]
        complementary_plot = configuration["outputs"]["Ignition_Delay_time"]["complementary_plot"]
        print(Fore.YELLOW + f"""
        #####################################################################
        #                                                                   #
        #                IGNITION DELAY TIME SIMULATION                     #
        #                                                                   #
        #####################################################################
        """)
        print(Fore.YELLOW + 80*"_")
        print(Fore.YELLOW + 80*"-")
        print(f"""
        MIXTURE INFORMATION:
              Fuel composition             :  {Fuel}
              Oxidizer composition         :  {Oxidizer}
        -----------------------------------------------------------
        Mechanisms                        :  {MECH}
        Number of Pressure Point          :  {len(Bash_Pressure_IDT)} 
        Number of Temeprature Point       :  {len(Bash_Temp_IDT)} 
        Number of Equivalent ratio Point  :  {len(Bash_EquiRatio_IDT)} 
        Total Number calcul point         :  {len(MECH)*len(Bash_Pressure_IDT) * len(Bash_Temp_IDT) * len(Bash_EquiRatio_IDT)}
        
        ----------------------------------------------------------
        
        SAVE Plot on Time Evolution          : {Time_evolution}
        SAVE Plot FIDT Evolution             : {IDT_plot}
        SAVE Plot complementary Evolution    : {complementary_plot}
        -----------------------------------------------------------
        
        """)
        print(Fore.YELLOW + 80*"_")
        print(Fore.YELLOW + 80*"-")
        time.sleep(2.5) 

        file_path_IDT = create_folder(file_name +"/" + subfolders[0], "01-Ignition_Delay_Time") 
        file_path_IDT_csv = create_folder(file_name +"/" + subfolders[3], "01-Ignition_Delay_Time") 
        
        print(Fore.WHITE + """
        ############################################################
        #                                                          #         
        #                     PRE-PROCESSING                       #
        #                                                          #
        ############################################################
        """)
        print(Style.RESET_ALL)
        
        PreProcess_IDT(mechanisms, 
                       MECH, 
                       Fuel_name, 
                       Oxi_name, 
                       Fuel, 
                       Oxidizer, 
                       configuration, 
                       file_path_IDT_csv,
                       Verbosity_level)
     
        print(Fore.YELLOW + 80*"_")
        print(Fore.YELLOW + 80*"-")
        print(Fore.WHITE + """
        ############################################################
        #                                                          #         
        #                     POST-PROCESSING                      #
        #                                                          #
        ############################################################
        """)
        print(Style.RESET_ALL)
        
        PostProcess_IDT(mechanisms, 
                        MECH, 
                        Fuel_name, 
                        Oxi_name, 
                        configuration, 
                        file_path_IDT_csv,
                        file_path_IDT,
                        Save_plot)
                 
    if Adiabatic_Temp is True:  
        Bash_Temp_Adiabatic      = configuration["conditions"]["Temperature_Adiabatic"]["Temperature"]
        Bash_Pressure_Adiabatic  = configuration["conditions"]["Temperature_Adiabatic"]["Pressure"]
        Bash_EquiRatio_Adiabatic = configuration["conditions"]["Temperature_Adiabatic"]["Phi"]
        
        Final_Temperature    = configuration["outputs"]["Temperature_Adiabatic"]["Final_Temperature"]
        Final_density        = configuration["outputs"]["Temperature_Adiabatic"]["Final_density"]
        Final_Enthalpy       = configuration["outputs"]["Temperature_Adiabatic"]["Final_Enthalpy"]


        
        print(Fore.YELLOW + f"""
        #####################################################################
        #                                                                   #
        #             ADIABATIC FLAME TEMEPERATURE SIMULATION               #
        #                                                                   #
        #####################################################################
        """)
        print(Fore.YELLOW + 80*"_")
        print(Fore.YELLOW + 80*"-")
        print(f"""
         MIXTURE INFORMATION:
                Fuel composition             :  {Fuel}
                Oxidizer composition         :  {Oxidizer}
         -----------------------------------------------------------
         Mechanisms                        :  {MECH}
         Number of Pressure Point          :  {len(Bash_Pressure_Adiabatic)} 
         Number of Temeprature Point       :  {len(Bash_Temp_Adiabatic)} 
         Number of Equivalent ratio Point  :  {len(Bash_EquiRatio_Adiabatic)} 
         Total Number calcul point         :  {len(MECH)*len(Bash_Pressure_Adiabatic) * len(Bash_Temp_Adiabatic) * len(Bash_EquiRatio_Adiabatic)}
        
         -----------------------------------------------------------
        
         EVOLUTION Final Temperature          : {Final_Temperature}
         EVOLUTION Final Density              : {Final_density}
         EVOLUTION Enthalpy Conservation      : {Final_Enthalpy}
         -----------------------------------------------------------
        
        """)
        print(Fore.YELLOW + 80*"_")
        print(Fore.YELLOW + 80*"-")
        time.sleep(1.5)
        
        file_path_Adiabatic      = create_folder(file_name+"/"+subfolders[3],"02-Adiabatic_Temperature_Flame")
        file_path_Adiabatic_plot = create_folder(file_name+"/"+subfolders[0],"02-Adiabatic_Temperature_Flame")
        
        print(Fore.WHITE + """
        ############################################################
        #                                                          #         
        #                     PRE-PROCESSING                       #
        #                                                          #
        ############################################################
        """)
        print(Style.RESET_ALL)
        
        PreProcess_Temperature_Adiabatic(mechanisms, 
                                         MECH, 
                                         Fuel_name, 
                                         Oxi_name, 
                                         Fuel, 
                                         Oxidizer, 
                                         configuration, 
                                         file_path_Adiabatic,
                                         Verbosity_level)
        
        print(Fore.YELLOW + 80*"_")
        print(Fore.YELLOW + 80*"-")
        print(Fore.WHITE + """
        ############################################################
        #                                                          #         
        #                     POST-PROCESSING                      #
        #                                                          #
        ############################################################
        """)
        print(Style.RESET_ALL)
        
        PostProcess_Temperature_Adiabatic(mechanisms, 
                                          MECH,
                                          Fuel_name,
                                          Oxi_name, 
                                          configuration,
                                          file_path_Adiabatic, 
                                          file_path_Adiabatic_plot,
                                          Save_plot)
             
    if Gas_Composition is True:  
        Bash_Temp_Composition      = configuration["conditions"]["Gas_Composition"]["Temperature"]
        Bash_Pressure_Composition  = configuration["conditions"]["Gas_Composition"]["Pressure"]
        Bash_EquiRatio_Composition = configuration["conditions"]["Gas_Composition"]["Phi"]
        
        Fresh_gas    = configuration["outputs"]["Gas_Composition"]["Fresh_gas"]
        Burn_gas  = configuration["outputs"]["Gas_Composition"]["Burn_gas"]
        
        print(Fore.YELLOW + """
        #####################################################################
        #                                                                   #
        #                   GAS COMPOSITION SIMULATION                      #
        #                                                                   #
        #####################################################################
        """)
        print(Fore.YELLOW + 80*"_")
        print(Fore.YELLOW + 80*"-")
        print(f"""
         MIXTURE INFORMATION:
              Fuel composition             :  {Fuel}
              Oxidizer composition         :  {Oxidizer}
         -----------------------------------------------------------
         Mechanisms                        :  {MECH}
         Number of Pressure Point          :  {len(Bash_Pressure_Composition)} 
         Number of Temeprature Point       :  {len(Bash_Temp_Composition)} 
         Number of Equivalent ratio Point  :  {len(Bash_EquiRatio_Composition)} 
         Total Number calcul point         :  {len(MECH)*len(Bash_Pressure_Composition) * len(Bash_Temp_Composition) * len(Bash_EquiRatio_Composition)}
        
         -----------------------------------------------------------
        
         SAVE fresh gas composition / Property        : {Fresh_gas}
         SAVE burn gas composition / Property         : {Burn_gas}
         -----------------------------------------------------------
        
        """)       
        print(Fore.YELLOW + 80*"_")
        print(Fore.YELLOW + 80*"-")
        
        time.sleep(2.5)           
        file_path_Composition_csv = create_folder(file_name+"/"+subfolders[3],"03-Gas_Composition")
        file_path_Compostion_plot = create_folder(file_name+"/"+subfolders[0],"03-Gas_Composition")
        
        print(Fore.WHITE + """
        ############################################################
        #                                                          #         
        #                     PRE-PROCESSING                       #
        #                                                          #
        ############################################################
        """)
        print(Style.RESET_ALL)
        
        PreProcess_Gas_Composition(mechanisms, 
                                   MECH, 
                                   Fuel_name, 
                                   Oxi_name, 
                                   Fuel, 
                                   Oxidizer, 
                                   configuration, 
                                   file_path_Composition_csv,
                                   Verbosity_level)
        
        print(Fore.YELLOW + 80*"_")
        print(Fore.YELLOW + 80*"-")
        print(Fore.WHITE + """
        ############################################################
        #                                                          #         
        #                     POST-PROCESSING                      #
        #                                                          #
        ############################################################
        """)
        print(Style.RESET_ALL)
        
        PostProcess_Gas_Composition()
        time.sleep(1.0)
        
    if Counter_flow is True:   
        Bash_Temp_CF      = configuration["conditions"]["Counter_flow"]["Temperature_pairs"]
        Bash_Pressure_CF  = configuration["conditions"]["Counter_flow"]["Pressure"]
        Bash_Velocity_flow_CF = configuration["conditions"]["Counter_flow"]["Velocity_flux_pairs"]
        
        Extinction_strain      = configuration["outputs"]["Counter_flow"]["Extinction_strain"]
        Basic_diffusion_flame  = configuration["outputs"]["Counter_flow"]["Basic_diffusion_flame"]
        Major_species          = configuration["outputs"]["Counter_flow"]["Major_species"]
        Radicals               = configuration["outputs"]["Counter_flow"]["Radicals"]
    
        print(Fore.YELLOW + f"""
        #####################################################################
        #                                                                   #
        #                   DIFFUSION FLAME SIMULATION                      #
        #                                                                   #
        #####################################################################
        """)
        print(Fore.YELLOW + 80*"_")
        print(Fore.YELLOW + 80*"-")
        print(f"""
         MIXTURE INFORMATION:
              Fuel composition             :  {Fuel}
              Oxidizer composition         :  {Oxidizer}
         -----------------------------------------------------------
         Mechanisms                        :  {MECH}
         Number of Pressure Point          :  {len(Bash_Pressure_CF)} 
         Number of Temperature pairs       :  {len(Bash_Temp_CF)} 
         Number of Velocity flow pairs     :  {len(Bash_Velocity_flow_CF)} 
         Total Number calcul point         :  {len(MECH)*len(Bash_Pressure_CF) * len(Bash_Temp_CF) * len(Bash_Velocity_flow_CF)}
        
         -----------------------------------------------------------
        
         Extinction strain simulation      : {Extinction_strain}
         Basic diffusion flame             : {Basic_diffusion_flame}
         Major Species focus               : {Major_species}
         Radical Species focus             : {Radicals}
         -----------------------------------------------------------
        
        """)       
        print(Fore.YELLOW + 80*"_")
        print(Fore.YELLOW + 80*"-")
        time.sleep(2.5)     
        
        file_path_CF_csv          = create_folder(file_name+"/"+subfolders[3],"04-Diffusion_Flame")
        file_path_CF_plot         = create_folder(file_name+"/"+subfolders[0],"04-Diffusion_Flame")
        file_path_CF_species_plot = create_folder(file_name+"/"+subfolders[1],"04-Diffusion_Flame")
        
        if Basic_diffusion_flame is True:
            file_path_BCF_csv          = create_folder(file_path_CF_csv,"00-Basic_Counter_Flow")
            file_path_BCF_plot         = create_folder(file_path_CF_plot,"00-Basic_Counter_Flow")
            file_path_BCF_species_plot = create_folder(file_path_CF_species_plot,"00-Basic_Counter_Flow")
            
            print(Fore.WHITE + """
            ############################################################
            #                                                          #         
            #            PRE-PROCESSING BASIC COUNTER FLOW             #
            #                                                          #
            ############################################################
            """)
            print(Style.RESET_ALL)
            
            PreProcess_Counter_flow(mechanisms, 
                                    MECH, 
                                    Fuel_name, 
                                    Oxi_name, 
                                    Fuel, 
                                    Oxidizer, 
                                    configuration, 
                                    file_path_BCF_csv,
                                    Verbosity_level)
            
            print(Fore.YELLOW + 80*"_")
            print(Fore.YELLOW + 80*"-")
            print(Fore.WHITE + """
            ############################################################
            #                                                          #         
            #           POST-PROCESSING  BASIC COUNTER FLOW            #
            #                                                          #
            ############################################################
            """)
            print(Style.RESET_ALL)
            
            PostProcess_Counter_flow(mechanisms,
                                     MECH, 
                                     Fuel_name, 
                                     Oxi_name, 
                                     configuration, 
                                     file_path_BCF_csv,
                                     file_path_BCF_plot,
                                     file_path_BCF_species_plot,
                                     Save_plot)
            
        if Extinction_strain is True:
            file_path_QCF_csv          = create_folder(file_path_CF_csv,"01-Quenching_Counter_Flow")
            file_path_QCF_plot         = create_folder(file_path_CF_plot,"01-Quenching_Counter_Flow")
            file_path_QCF_species_plot = create_folder(file_path_CF_species_plot,"01-Quenching_Counter_Flow")
            print(Fore.WHITE + """
            ############################################################
            #                                                          #         
            #         PRE-PROCESSING QUENCHING COUNTER FLOW            #
            #                                                          #
            ############################################################
            """)
            print(Style.RESET_ALL)
            
            PreProcess_Counter_flow_quenching (mechanisms, 
                                    MECH, 
                                    Fuel_name, 
                                    Oxi_name, 
                                    Fuel, 
                                    Oxidizer, 
                                    configuration, 
                                    file_path_QCF_csv,
                                    Verbosity_level)
            
            print(Fore.YELLOW + 80*"_")
            print(Fore.YELLOW + 80*"-")
            print(Fore.WHITE + """
            ############################################################
            #                                                          #         
            #         POST-PROCESSING QUENCHING COUNTER FLOW           #
            #                                                          #
            ############################################################
            """)
            print(Style.RESET_ALL)
            
            PostProcess_Counter_flow_quenching(mechanisms,
                                     MECH, 
                                     Fuel_name, 
                                     Oxi_name, 
                                     configuration, 
                                     file_path_QCF_csv,
                                     file_path_QCF_plot,
                                     Save_plot)

    return file           
                
#Execution function 
#
# @param None        : None  
def __main__():
    process = psutil.Process(os.getpid())
    print("Mémoire utilisée :", process.memory_info().rss / 1e6, "MB")
    print(Fore.YELLOW + " _______________________________________________________")
    print(Fore.YELLOW +"#                         2026                          #")
    print(Fore.YELLOW +"#         copyright __2026- All Rights Reserved         #")
    print(Fore.YELLOW +"#                                                       #")
    print(Fore.YELLOW +"#                 CANTERA 0D/1D SIMULATION              #")
    print(Fore.YELLOW +"#                     Lilian Chapuis                    #")
    print(Fore.YELLOW +"#_______________________________________________________#" )
    
    print()
    time.sleep(1.5) 
    START_time = time.time()
    file_name = main_process("parameter_coupling.yaml")
    print()
    END_time = time.time()
    elapsed = END_time - START_time
    print(Fore.YELLOW + 80*"_")
    print(Fore.YELLOW + 80*"-")
    print()
    width = 66
    border_top = "╔" + "═" * width + "╗"
    border_bottom = "╚" + "═" * width + "╝"
    
    print(Fore.RED + border_top)
    
    print(Fore.RED + "#" + " " * width + "#")
    print(Fore.RED + "#" + " " * width + "#")
    
    title = "SIMULATION COMPLETED"
    subtitle = "Numerical processing finished successfully"
    time_line = f"Elapsed time: {elapsed:.3f} s"
    
    print("#" + (file_name +' ' +title).center(width) + "#")
    print("#" + subtitle.center(width) + "#")
    print("#" + time_line.center(width) + "#")
    
    print(Fore.RED + "#" + " " * width + "#")
    print(Fore.RED + "#" + " " * width + "#")
    
    print(Fore.RED + border_bottom)
    
__main__()
# cProfile.run("__main__()", "profiling_results.prof")

# # Lecture des résultats
# p = pstats.Stats("profiling_results.prof")
# p.strip_dirs().sort_stats("cumtime").print_stats(20)

    
