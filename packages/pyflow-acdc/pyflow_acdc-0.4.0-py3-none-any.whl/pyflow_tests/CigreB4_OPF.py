# -*- coding: utf-8 -*-
"""
Created on Wed Dec 20 10:55:43 2023

@author: BernardoCastro

This grid is based on the CIGRE B4 test system. DCDC converters have been simplified to a load and a gain in respective nodes.
"""

import time
import pandas as pd
import pyflow_acdc as pyf

from pathlib import Path

def CigreB4_OPF():


    start_time = time.time()

    S_base=100 #MVAres
    
    beta= 0.0165 #percent

    current_file = Path(__file__).resolve()
    path = str(current_file.parent)

    # Using forward slashes in paths
    AC_node_data   = pd.read_csv(f"{path}/CigreB4/CigreB4_AC_node_data.csv")
    DC_node_data   = pd.read_csv(f"{path}/CigreB4/CigreB4_DC_node_data.csv")
    AC_line_data   = pd.read_csv(f"{path}/CigreB4/CigreB4_AC_line_data.csv")
    DC_line_data   = pd.read_csv(f"{path}/CigreB4/CigreB4_DC_line_data.csv")
    Converter_ACDC_data = pd.read_csv(f"{path}/CigreB4/CigreB4_Converter_data.csv")
    DCDC_data = pd.read_csv(f"{path}/CigreB4/CigreB4_DCDC_conv.csv")

    [grid,res]=pyf.Create_grid_from_data(S_base, AC_node_data, AC_line_data, DC_node_data, DC_line_data, Converter_ACDC_data)
    for conv in grid.Converters_ACDC:
        conv.a_conv=0
        conv.b_conv=0
        conv.c_inver=0
        conv.c_rect=0


    pyf.add_extGrid(grid, 'BaA0')
    pyf.add_extGrid(grid, 'BaB0')

    for conv in DCDC_data.itertuples():
        pyf.add_DCDC_converter(grid,conv.fromNode,conv.toNode,P_MW=conv.P_MW,R_Ohm=conv.R_Ohm,MW_rating=conv.MW_rating)


    # pyf.ACDC_sequential(grid)
    model, timing_info, model_res,solver_stats=pyf.Optimal_PF(grid)

    res.All()
    print(model_res)
    print(timing_info)
    model.obj.display()

    end_time = time.time()
    elapsed_time = end_time - start_time

    print ('------')
    print(f'Time elapsed : {elapsed_time}')

def run_test():
    """Test CIGRE B4 optimal power flow."""
    try:
        import pyomo
    except ImportError:
        print("pyomo is not installed...")
        return  
    
    CigreB4_OPF()

if __name__ == "__main__":
    run_test()