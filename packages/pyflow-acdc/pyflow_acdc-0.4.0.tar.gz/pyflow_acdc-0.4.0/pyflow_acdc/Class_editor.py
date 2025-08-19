"""
Created on Fri Dec 15 15:24:42 2023

@author: BernardoCastro
"""

import pandas as pd
import numpy as np
import sys
import yaml
from shapely.wkt import loads

from .Classes import*
from .Results_class import*

from pathlib import Path    
    
"""
"""

__all__ = [
    # Add Grid Elements
    'add_AC_node',
    'add_DC_node',
    'add_line_AC',
    'add_line_DC',
    'add_ACDC_converter',
    'add_DCDC_converter',
    'add_gen',
    'add_gen_DC',
    'add_extGrid',
    'add_RenSource',
    'add_generators',
    'add_cable_option',
    'add_line_sizing',
    
    # Add Zones
    'add_RenSource_zone',
    'add_price_zone',
    'add_MTDC_price_zone',
    'add_offshore_price_zone',
    
    # Add Time Series
    'add_TimeSeries',
    
    # Line Modifications
    'change_line_AC_to_expandable',
    'change_line_AC_to_reconducting',
    'change_line_AC_to_tap_transformer',
    
    # Zone Assignments
    'assign_RenToZone',
    'assign_nodeToPrice_Zone',
    'assign_ConvToPrice_Zone',
    'assign_lineToCable_options',
    
    # Parameter Calculations
    'Cable_parameters',
    'Converter_parameters',
    
    # Utility Functions
    'pol2cart',
    'cart2pol',
    'pol2cartz',
    'cartz2pol',
]

def pol2cart(r, theta):
    x = r*np.cos(theta)
    y = r*np.sin(theta)
    return x, y


def pol2cartz(r, theta):
    x = r*np.cos(theta)
    y = r*np.sin(theta)
    z = x+1j*y
    return z


def cart2pol(x, y):
    rho = np.sqrt(x**2 + y**2)
    theta = np.arctan2(y, x)
    return rho, theta


def cartz2pol(z):
    r = np.abs(z)
    theta = np.angle(z)
    return r, theta



def Converter_parameters(S_base, kV_base, T_R_Ohm, T_X_mH, PR_R_Ohm, PR_X_mH, Filter_uF, f=50):

    Z_base = kV_base**2/S_base  # kv^2/MVA
    Y_base = 1/Z_base

    F = Filter_uF*10**(-6)
    PR_X_H = PR_X_mH/1000
    T_X_H = T_X_mH/1000

    B    = 2*f*F*np.pi
    T_X  = 2*f*T_X_H*np.pi
    PR_X = 2*f*PR_X_H*np.pi

    T_R_pu = T_R_Ohm/Z_base
    T_X_pu = T_X/Z_base
    PR_R_pu = PR_R_Ohm/Z_base
    PR_X_pu = PR_X/Z_base
    Filter_pu = B/Y_base

    return [T_R_pu, T_X_pu, PR_R_pu, PR_X_pu, Filter_pu]


def Cable_parameters(S_base, R, L_mH, C_uF, G_uS, A_rating, kV_base, km, N_cables=1, f=50):

    Z_base = kV_base**2/S_base  # kv^2/MVA
    Y_base = 1/Z_base

    if L_mH == 0:
        N_cables = 1
        MVA_rating = N_cables*A_rating*kV_base/(1000)
        #IN DC N cables is always 1 as the varible is used directly in the formulation
    else:
        MVA_rating = N_cables*A_rating*kV_base*np.sqrt(3)/(1000)

    C = C_uF*(10**(-6))
    L = L_mH/1000
    G = G_uS*(10**(-6))

    R_AC = R*km

    B = 2*f*C*np.pi*km
    X = 2*f*L*np.pi*km

    Z = R_AC+X*1j
    Y = G+B*1j

    # Zc=np.sqrt(Z/Y)
    # theta_Z=np.sqrt(Z*Y)

    Z_pi = Z
    Y_pi = Y

    # Z_pi=Zc*np.sinh(theta_Z)
    # Y_pi = 2*np.tanh(theta_Z/2)/Zc

    R_1 = np.real(Z_pi)
    X_1 = np.imag(Z_pi)
    G_1 = np.real(Y_pi)
    B_1 = np.imag(Y_pi)

    Req = R_1/N_cables
    Xeq = X_1/N_cables
    Geq = G_1*N_cables
    Beq = B_1*N_cables

    Rpu = Req/Z_base
    Xpu = Xeq/Z_base
    Gpu = Geq/Y_base
    Bpu = Beq/Y_base

    return [Rpu, Xpu, Gpu, Bpu, MVA_rating]

"Add main components"

def add_AC_node(grid, kV_base,node_type='PQ',Voltage_0=1.01, theta_0=0.01, Power_Gained=0, Reactive_Gained=0, Power_load=0, Reactive_load=0, name=None, Umin=0.9, Umax=1.1,Gs= 0,Bs=0,x_coord=None,y_coord=None,geometry=None):
    node = Node_AC( node_type, Voltage_0, theta_0,kV_base, Power_Gained, Reactive_Gained, Power_load, Reactive_load, name, Umin, Umax,Gs,Bs,x_coord,y_coord)
    if geometry is not None:
       if isinstance(geometry, str): 
            geometry = loads(geometry)  
       node.geometry = geometry
       node.x_coord = geometry.x
       node.y_coord = geometry.y
    
    grid.nodes_AC.append(node)
    
    return node

def add_DC_node(grid,kV_base,node_type='P', Voltage_0=1.01, Power_Gained=0, Power_load=0, name=None,Umin=0.95, Umax=1.05,x_coord=None,y_coord=None,geometry=None):  
    node = Node_DC(node_type, kV_base, Voltage_0, Power_Gained, Power_load, name,Umin, Umax,x_coord,y_coord)
    grid.nodes_DC.append(node)
    if geometry is not None:
       if isinstance(geometry, str): 
            geometry = loads(geometry)  
       node.geometry = geometry
       node.x_coord = geometry.x
       node.y_coord = geometry.y
       
       
    return node
    
def add_line_AC(grid, fromNode, toNode,MVA_rating=None, r=0, x=0, b=0, g=0,R_Ohm_km=None,L_mH_km=None, C_uF_km=0, G_uS_km=0, A_rating=None ,m=1, shift=0, name=None,tap_changer=False,Expandable=False,N_cables=1,Length_km=1,geometry=None,data_in='pu',Cable_type:str ='Custom',update_grid=True):
    
    if isinstance(fromNode, str):
        fromNode = next((node for node in grid.nodes_AC if node.name == fromNode), None)
    if isinstance(toNode, str):
        toNode = next((node for node in grid.nodes_AC if node.name == toNode), None)
    
    kV_base=toNode.kV_base
    if L_mH_km is not None:
        data_in = 'Real'
    if data_in == 'Ohm':
        Z_base = kV_base**2/grid.S_base
        
        Resistance_pu = r / Z_base if r!=0 else 0.00001
        Reactance_pu  = x  / Z_base if x!=0  else 0.00001
        Conductance_pu = g*Z_base
        Susceptance_pu = b*Z_base
    elif data_in== 'Real' and Cable_type == 'Custom': 
       [Resistance_pu, Reactance_pu, Conductance_pu, Susceptance_pu, MVA_rating] = Cable_parameters(grid.S_base, R_Ohm_km, L_mH_km, C_uF_km, G_uS_km, A_rating, kV_base, Length_km,N_cables=N_cables)
    else:
        Resistance_pu = r if r!=0 else 0.00001
        Reactance_pu  = x if x!=0  else 0.00001
        Conductance_pu = g
        Susceptance_pu = b
    
    
    if tap_changer:
        line = TF_Line_AC(fromNode, toNode, Resistance_pu,Reactance_pu, Conductance_pu, Susceptance_pu, MVA_rating, kV_base,m, shift, name)
        grid.lines_AC_tf.append(line)
        if update_grid:
            grid.Update_Graph_AC()
    elif Expandable:
        line = Exp_Line_AC(fromNode, toNode, Resistance_pu,Reactance_pu, Conductance_pu, Susceptance_pu, MVA_rating,Length_km,m, shift,N_cables, name,S_base=grid.S_base,Cable_type=Cable_type)
        grid.lines_AC_exp.append(line)
        if update_grid:
            grid.Update_Graph_AC()
        
    else:    
        line = Line_AC(fromNode, toNode, Resistance_pu,Reactance_pu, Conductance_pu, Susceptance_pu, MVA_rating,Length_km,m, shift,N_cables, name,S_base=grid.S_base,Cable_type=Cable_type)
        
        grid.lines_AC.append(line)
        if update_grid: 
            grid.create_Ybus_AC()
            grid.Update_Graph_AC()
        
    if geometry is not None:
       if isinstance(geometry, str): 
            geometry = loads(geometry)  
       line.geometry = geometry
    
    return line

def change_line_AC_to_expandable(grid, line_name,update_grid=True):
    l = None
    for line_to_process in grid.lines_AC:
        if line_name == line_to_process.name:
            l = line_to_process
            break
            
    if l is not None:    
        grid.lines_AC.remove(l)
        l.remove()
        line_vars = {
            'fromNode': l.fromNode,
            'toNode': l.toNode,
            'r': l.R,
            'x': l.X,
            'g': l.G,
            'b': l.B,
            'MVA_rating': l.MVA_rating,
            'Length_km': l.Length_km,
            'm': l.m,
            'shift': l.shift,
            'N_cables': l.N_cables,
            'name': l.name,
            'geometry': l.geometry,
            'S_base': l.S_base,
            'Cable_type': l.Cable_type
        }
        expandable_line = Exp_Line_AC(**line_vars)
        grid.lines_AC_exp.append(expandable_line)
        if update_grid:
            grid.Update_Graph_AC()

    # Reassign line numbers to ensure continuity
    for i, line in enumerate(grid.lines_AC):
        line.lineNumber = i 
    
    for i, line in enumerate(grid.lines_AC_exp):
        line.lineNumber = i 
    if update_grid:
        grid.create_Ybus_AC()
    return expandable_line    

def change_line_AC_to_reconducting(grid, line_name, r_new,x_new,g_new,b_new,MVA_rating_new,Life_time,base_cost):
    l = None
    for line_to_process in grid.lines_AC:
        if line_name == line_to_process.name:
            l = line_to_process
            break
            
    if l is not None:    
        grid.lines_AC.remove(l)
        l.remove()
        line_vars = {
            'fromNode': l.fromNode,
            'toNode': l.toNode,
            'r': l.R,
            'x': l.X,
            'g': l.G,
            'b': l.B,
            'MVA_rating': l.MVA_rating,
            'Length_km': l.Length_km,
            'm': l.m,
            'shift': l.shift,
            'N_cables': l.N_cables,
            'name': l.name,
            'geometry': l.geometry,
            'S_base': l.S_base,
            'Cable_type': l.Cable_type
        }
        rec_line = rec_Line_AC(r_new,x_new,g_new,b_new,MVA_rating_new,Life_time,base_cost,**line_vars)
        grid.lines_AC_rec.append(rec_line)
        grid.Update_Graph_AC()

    # Reassign line numbers to ensure continuity
    for i, line in enumerate(grid.lines_AC):
        line.lineNumber = i 
    
    for i, line in enumerate(grid.lines_AC_rec):
        line.lineNumber = i 
    grid.create_Ybus_AC()    
    return rec_line  

def change_line_AC_to_tap_transformer(grid, line_name):
    l = None
    for line_to_process in grid.lines_AC:
        if line_name == line_to_process.name:
            l  = line_to_process
            break
    if l is not None:    
            grid.lines_AC.remove(l)
            l.remove()
            line_vars=line_vars = {
            'fromNode': l.fromNode,
            'toNode': l.toNode,
            'Resistance': l.R,
            'Reactance': l.X,
            'Conductance': l.G,
            'Susceptance': l.B,
            'MVA_rating': l.MVA_rating,
            'Length_km': l.Length_km,
            'm': l.m,
            'shift': l.shift,
            'N_cables': l.N_cables,
            'name': l.name,
            'geometry': l.geometry,
            'S_base': l.S_base,
            'Cable_type': l.Cable_type
        }
            trafo = TF_Line_AC(**line_vars)
            grid.lines_AC_tf.append(trafo)
    else:
        print(f"Line {line_name} not found.")
        return
    # Reassign line numbers to ensure continuity in grid.lines_AC
    for i, line in enumerate(grid.lines_AC):
        line.lineNumber = i 
    grid.create_Ybus_AC()
    s=1    

def add_line_sizing(grid, fromNode, toNode,cable_types: list=[], active_config: int = 0,Length_km=1.0,S_base=100,name=None,cable_option=None,update_grid=True,geometry=None):       
    if isinstance(fromNode, str):
        fromNode = next((node for node in grid.nodes_AC if node.name == fromNode), None)
    if isinstance(toNode, str):
        toNode = next((node for node in grid.nodes_AC if node.name == toNode), None)
    
    line = Line_sizing(fromNode, toNode,cable_types, active_config,Length_km,S_base,name)
    grid.lines_AC_ct.append(line)
    if cable_option is not None:
        assign_lineToCable_options(grid,line.name,cable_option)
    if update_grid:
        grid.create_Ybus_AC()
        grid.Update_Graph_AC() 
    if geometry is not None:
       if isinstance(geometry, str): 
            geometry = loads(geometry)  
       line.geometry = geometry
    return line

def add_line_DC(grid, fromNode, toNode, r=0.001, MW_rating=9999,Length_km=1,R_Ohm_km=None,A_rating=None,polarity='m', name=None,geometry=None,Cable_type:str ='Custom',data_in='pu',update_grid=True):
    
    if isinstance(fromNode, str):
        fromNode = next((node for node in grid.nodes_DC if node.name == fromNode), None)
    if isinstance(toNode, str):
        toNode = next((node for node in grid.nodes_DC if node.name == toNode), None)
    
    kV_base=toNode.kV_base
    if data_in == 'Ohm':
        Z_base = kV_base**2/grid.S_base
        
        Resistance_pu = r / Z_base if r!=0 else 0.00001

    elif data_in== 'Real' or R_Ohm_km is not None: 
        if A_rating is None:
            A_rating = MW_rating*1000/kV_base     
        [Resistance_pu, _, _, _, MW_rating] = Cable_parameters(grid.S_base, R_Ohm_km, 0, 0, 0, A_rating, kV_base, Length_km,N_cables=1)
    else:
        Resistance_pu = r if r!=0 else 0.00001
      
    if isinstance(polarity, int):
        if polarity == 1:
            polarity = 'm'
        elif polarity == 2:
            polarity = 'b'
        else:
            print(f"Invalid polarity value: {polarity}")
            return
    line = Line_DC(fromNode, toNode, Resistance_pu, MW_rating,Length_km, polarity, name,Cable_type=Cable_type)
    grid.lines_DC.append(line)
    
    if geometry is not None:
       if isinstance(geometry, str): 
            geometry = loads(geometry)  
       line.geometry = geometry
    if update_grid:
        grid.create_Ybus_DC()
        grid.Update_Graph_DC()
    return line

def add_ACDC_converter(grid,AC_node , DC_node , AC_type='PV', DC_type=None, P_AC_MW=0, Q_AC_MVA=0, P_DC_MW=0, Transformer_resistance=0, Transformer_reactance=0, Phase_Reactor_R=0, Phase_Reactor_X=0, Filter=0, Droop=0, kV_base=None, MVA_max= None,nConvP=1,polarity =1 ,lossa=1.103,lossb= 0.887,losscrect=2.885,losscinv=4.371,Arm_R=None,Ucmin= 0.85, Ucmax= 1.2, name=None,geometry=None):
    if isinstance(DC_node, str):
        DC_node = next((node for node in grid.nodes_DC if node.name == DC_node), None)
    if isinstance(AC_node, str):
        AC_node = next((node for node in grid.nodes_AC if node.name == AC_node), None)
    
    
    
    
    if MVA_max is None:
        MVA_max= grid.S_base*100
    if kV_base is None:
        kV_base = AC_node.kV_base
    if DC_type is None:
        DC_type = DC_node.type
        
    P_DC = P_DC_MW/grid.S_base
    P_AC = P_AC_MW/grid.S_base
    Q_AC = Q_AC_MVA/grid.S_base
    # if Filter !=0 and Phase_Reactor_R==0 and  Phase_Reactor_X!=0:
    #     print(f'Please fill out phase reactor values, converter {name} not added')
    #     return
    if Arm_R is not None:
        ra  = Arm_R*conv.basekA_DC**2/grid.S_base
    else:
        ra = 0.001

    conv = AC_DC_converter(AC_type, DC_type, AC_node, DC_node, P_AC, Q_AC, P_DC, Transformer_resistance, Transformer_reactance, Phase_Reactor_R, Phase_Reactor_X, Filter, Droop, kV_base, MVA_max,nConvP,polarity ,lossa,lossb,losscrect,losscinv,Ucmin, Ucmax, ra,name)
    if geometry is not None:
        if isinstance(geometry, str): 
             geometry = loads(geometry)  
        conv.geometry = geometry    
   
    conv.basekA  = grid.S_base/(np.sqrt(3)*conv.AC_kV_base)
    conv.basekA_DC = grid.S_base/(conv.DC_kV_base)
    conv.a_conv  = conv.a_conv_og/grid.S_base
    conv.b_conv  = conv.b_conv_og*conv.basekA/grid.S_base
    conv.c_inver = conv.c_inver_og*conv.basekA**2/grid.S_base
    conv.c_rect  = conv.c_rect_og*conv.basekA**2/grid.S_base     
    
    
    
    
    grid.Converters_ACDC.append(conv)
    return conv

def add_DCDC_converter(grid,fromNode , toNode ,P_MW=None,Pset=None,R_Ohm=None, r=0.0001, MW_rating=99999,name=None,geometry=None):
    if isinstance(fromNode, str):
        fromNode = next((node for node in grid.nodes_DC if node.name == fromNode), None)
    if isinstance(toNode, str):
        toNode = next((node for node in grid.nodes_DC if node.name == toNode), None)
    
    if R_Ohm is not None:
        Z_base = toNode.kV_base**2/grid.S_base
        r = R_Ohm/Z_base
    if P_MW is not None:
        Pset = P_MW/grid.S_base
    if Pset is None:
        Pset = MW_rating/(2*grid.S_base)
    
    conv = DCDC_converter(fromNode , toNode , Pset, r, MW_rating,name,geometry)
    grid.Converters_DCDC.append(conv)
    return conv

"Zones"

def add_cable_option(grid, cable_types: list,name=None):
    cable_option = Cable_options(cable_types,name)
    grid.Cable_options.append(cable_option)
    return cable_option


def add_RenSource_zone(Grid,name):
        
    RSZ = Ren_source_zone(name)
    Grid.RenSource_zones.append(RSZ)
    Grid.RenSource_zones_dic[name]=RSZ.ren_source_num
    
    return RSZ


def add_price_zone(Grid,name,price,import_pu_L=1,export_pu_G=1,a=0,b=1,c=0,import_expand_pu=0):

    if b==1:
        b= price
    
    M = Price_Zone(price,import_pu_L,export_pu_G,a,b,c,import_expand_pu,name)
    Grid.Price_Zones.append(M)
    Grid.Price_Zones_dic[name]=M.price_zone_num
    
    return M

def add_MTDC_price_zone(Grid, name,  linked_price_zones=None,pricing_strategy='avg'):
    # Initialize the MTDC price_zone and link it to the given price_zones
    mtdc_price_zone = MTDCPrice_Zone(name=name, linked_price_zones=linked_price_zones, pricing_strategy=pricing_strategy)
    Grid.Price_Zones.append(mtdc_price_zone)
    
    return mtdc_price_zone


def add_offshore_price_zone(Grid,main_price_zone,name):
    if isinstance(main_price_zone, str):
        main_price_zone = next((M for M in Grid.Price_Zones if main_price_zone == M.name), None)

    oprice_zone = OffshorePrice_Zone(name=name, price=main_price_zone.price, main_price_zone=main_price_zone)
    Grid.Price_Zones.append(oprice_zone)
    
    return oprice_zone

"Components for optimal power flow"

def add_generators(Grid,Gen_csv):
    if isinstance(Gen_csv, pd.DataFrame):
        Gen_data = Gen_csv
    else:
        Gen_data = pd.read_csv(Gen_csv)
   
    Gen_data = Gen_data.set_index('Gen')
    
    
    for index, row in Gen_data.iterrows():
        var_name = Gen_data.at[index, 'Gen_name'] if 'Gen_name' in Gen_data.columns else index
        node_name = str(Gen_data.at[index, 'Node'])
        
        MWmax = Gen_data.at[index, 'MWmax'] if 'MWmax' in Gen_data.columns else None
        MWmin = Gen_data.at[index, 'MWmin'] if 'MWmin' in Gen_data.columns else 0
        MVArmin = Gen_data.at[index, 'MVArmin'] if 'MVArmin' in Gen_data.columns else 0
        MVArmax = Gen_data.at[index, 'MVArmax'] if 'MVArmax' in Gen_data.columns else 99999
        
        PsetMW = Gen_data.at[index, 'PsetMW']  if 'PsetMW'  in Gen_data.columns else 0
        QsetMVA= Gen_data.at[index, 'QsetMVA'] if 'QsetMVA' in Gen_data.columns else 0
        lf = Gen_data.at[index, 'Linear factor']    if 'Linear factor' in Gen_data.columns else 0
        qf = Gen_data.at[index, 'Quadratic factor'] if 'Quadratic factor' in Gen_data.columns else 0
        fc = Gen_data.at[index, 'Fixed cost'] if 'Fixed cost' in Gen_data.columns else 0
        geo  = Gen_data.at[index, 'geometry'] if 'geometry' in Gen_data.columns else None
        price_zone_link = False
        
        fuel_type = Gen_data.at[index, 'Fueltype']    if 'Fueltype' in Gen_data.columns else 'Other'
        if fuel_type.lower() in ["wind", "solar"]:
            add_RenSource(Grid,node_name, MWmax,ren_source_name=var_name ,geometry=geo,ren_type=fuel_type)
        else:
            add_gen(Grid, node_name,var_name, price_zone_link,lf,qf,fc,MWmax,MWmin,MVArmin,MVArmax,PsetMW,QsetMVA,fuel_type=fuel_type,geometry=geo)  
        
def add_gen(Grid, node_name,gen_name=None, price_zone_link=False,lf=0,qf=0,fc=0,MWmax=99999,MWmin=0,MVArmin=None,MVArmax=None,PsetMW=0,QsetMVA=0,Smax=None,fuel_type='Other',geometry= None,installation_cost:float=0,np_gen:int=1):
    
    if MVArmax is None:
        MVArmax=MWmax
    if MVArmin is None:
        MVArmin=-MVArmax
    if Smax is not None:
        Smax/=Grid.S_base
    Max_pow_gen=MWmax/Grid.S_base
 
    Max_pow_genR=MVArmax/Grid.S_base
    Min_pow_genR=MVArmin/Grid.S_base
    Min_pow_gen=MWmin/Grid.S_base
    Pset=PsetMW/Grid.S_base
    Qset=QsetMVA/Grid.S_base
    found=False    
    for node in Grid.nodes_AC:
   
        if node_name == node.name:
             gen = Gen_AC(gen_name, node,Max_pow_gen,Min_pow_gen,Max_pow_genR,Min_pow_genR,qf,lf,fc,Pset,Qset,Smax,installation_cost)
             node.PGi = 0
             node.QGi = 0
             if fuel_type not in [
             "Nuclear", "Hard Coal", "Hydro", "Oil", "Lignite", "Natural Gas",
             "Solid Biomass",  "Other", "Waste", "Biogas", "Geothermal"
             ]:
                 fuel_type = 'Other'
             gen.gen_type = fuel_type
             gen.np_gen = np_gen
             if geometry is not None:
                 if isinstance(geometry, str): 
                      geometry = loads(geometry)  
                 gen.geometry= geometry
             found = True
             break

    if not found:
            print('Node does not exist')
            sys.exit()
    gen.price_zone_link=price_zone_link
    
    if price_zone_link:
        
        gen.qf= 0
        gen.lf= node.price
    Grid.Generators.append(gen)
    
    return gen
            
def add_gen_DC(Grid, node_name,gen_name=None, price_zone_link=False,lf=0,qf=0,fc=0,MWmax=99999,MWmin=0,PsetMW=0,fuel_type='Other',geometry= None,installation_cost:float=0,np_gen:int=1):
    
    Max_pow_gen=MWmax/Grid.S_base
    Min_pow_gen=MWmin/Grid.S_base
    Pset=PsetMW/Grid.S_base
    
    found=False    
    for node in Grid.nodes_DC:
   
        if node_name == node.name:
             gen = Gen_DC(gen_name, node,Max_pow_gen,Min_pow_gen,qf,lf,fc,Pset,installation_cost)
             node.PGi = 0
             if fuel_type not in [
             "Nuclear", "Hard Coal", "Hydro", "Oil", "Lignite", "Natural Gas",
             "Solid Biomass",  "Other", "Waste", "Biogas", "Geothermal"
             ]:
                 fuel_type = 'Other'
             gen.gen_type = fuel_type
             gen.np_gen = np_gen
             if geometry is not None:
                 if isinstance(geometry, str): 
                      geometry = loads(geometry)  
                 gen.geometry= geometry
             found = True
             break

    if not found:
            print('Node does not exist')
            sys.exit()
    gen.price_zone_link=price_zone_link
    
    if price_zone_link:
        
        gen.qf= 0
        gen.lf= node.price
    Grid.Generators_DC.append(gen)
    
    return gen


def add_extGrid(Grid, node_name, gen_name=None,price_zone_link=False,lf=0,qf=0,MVAmax=99999,MVArmin=None,MVArmax=None,Allow_sell=True):
    
    
    if MVArmin is None:
        MVArmin=-MVAmax
    if MVArmax is None:
        MVArmax=MVAmax
    
    Max_pow_gen=MVAmax/Grid.S_base
 
    Max_pow_genR=MVArmax/Grid.S_base
    Min_pow_genR=MVArmin/Grid.S_base
    if Allow_sell:
        Min_pow_gen=-MVAmax/Grid.S_base
    else:
        Min_pow_gen=0
    found=False 
    for node in Grid.nodes_AC:
        if node_name == node.name:
             gen = Gen_AC(gen_name, node,Max_pow_gen,Min_pow_gen,Max_pow_genR,Min_pow_genR,qf,lf)
             node.PGi = 0
             node.QGi = 0
             found=True
             break
    if not found:
        print(f'Node {node_name} does not exist')
        sys.exit()
    gen.price_zone_link=price_zone_link
    if price_zone_link:
        gen.qf= 0
        gen.lf= node.price
    Grid.Generators.append(gen)

def add_RenSource(Grid,node_name, base,ren_source_name=None , available=1,zone=None,price_zone=None, Offshore=False,MTDC=None,geometry= None,ren_type='Wind',min_gamma=0,Qrel=0):
    
    
    if ren_source_name is None:
        ren_source_name= node_name
    found=False 
    for node in Grid.nodes_AC:
        if node_name == node.name:
            rensource= Ren_Source(ren_source_name,node,base/Grid.S_base)    
            rensource.PRGi_available=available
            rensource.connected= 'AC'
            ACDC='AC'
            rensource.rs_type= ren_type
            if geometry is not None:
                if isinstance(geometry, str): 
                     geometry = loads(geometry)  
                rensource.geometry= geometry
            rensource.min_gamma = min_gamma
            rensource.Qmax = base*Qrel/Grid.S_base
            rensource.Qmin = -base*Qrel/Grid.S_base
            Grid.rs2node['AC'][rensource.rsNumber]=node.nodeNumber
            found = True
            break
    for node in Grid.nodes_DC:
        if node_name == node.name:
            rensource= Ren_Source(ren_source_name,node,base/Grid.S_base)    
            rensource.PGi_available=available
            rensource.connected= 'DC'
            ACDC='DC'
            rensource.rs_type= ren_type
            if geometry is not None:
                if isinstance(geometry, str): 
                     geometry = loads(geometry)  
                rensource.geometry= geometry
            rensource.min_gamma = min_gamma
            Grid.rs2node['DC'][rensource.rsNumber]=node.nodeNumber
            found = True
            break    

    if not found:
           print(f'Node {node_name} does not exist')
           sys.exit()
   
    Grid.RenSources.append(rensource)
    
    
    if zone is not None:
        rensource.zone=zone
        assign_RenToZone(Grid,ren_source_name,zone)
    
    if price_zone is not None:
        rensource.price_zone=price_zone
        if MTDC is not None:
            rensource.MTDC=MTDC
            main_price_zone = next((M for M in Grid.Price_Zones if price_zone == M.name), None)
            if main_price_zone is not None:
                # Find or create the MTDC price_zone
                MTDC_price_zone = next((mdc for mdc in Grid.Price_Zones if MTDC == mdc.name), None)

                if MTDC_price_zone is None:
                    # Create the offshore price_zone using the OffshorePrice_Zone class
                    MTDC_price_zone= add_MTDC_price_zone(Grid,MTDC)
            
            MTDC_price_zone.add_linked_price_zone(main_price_zone)
            main_price_zone.ImportExpand += base / Grid.S_base
            assign_nodeToPrice_Zone(Grid, node_name,MTDC, ACDC)
            # Additional logic for MTDC can be placed here
        elif Offshore:
            rensource.Offshore=True
            # Create an offshore price_zone by appending 'o' to the main price_zone's name
            oprice_zone_name = f'o_{price_zone}'

            # Find the main price_zone
            main_price_zone = next((M for M in Grid.Price_Zones if price_zone == M.name), None)
            
            if main_price_zone is not None:
                # Find or create the offshore price_zone
                oprice_zone = next((m for m in Grid.Price_Zones if m.name == oprice_zone_name), None)

                if oprice_zone is None:
                    # Create the offshore price_zone using the OffshorePrice_Zone class
                    oprice_zone= add_offshore_price_zone(Grid,main_price_zone,oprice_zone_name)

                # Assign the node to the offshore price_zone
                assign_nodeToPrice_Zone(Grid, node_name,oprice_zone_name,ACDC)
                # Link the offshore price_zone to the main price_zone
                main_price_zone.link_price_zone(oprice_zone)
                # Expand the import capacity in the main price_zone
                main_price_zone.ImportExpand += base / Grid.S_base
        else:
            # Assign the node to the main price_zone
            assign_nodeToPrice_Zone(Grid, node_name, price_zone,ACDC)



"Time series data "


def time_series_dict(grid, ts):
    typ = ts.type
    
    if typ == 'a_CG':
        for price_zone in grid.Price_Zones:
            if ts.element_name == price_zone.name:
                price_zone.TS_dict[typ] = ts.TS_num
                break
    elif typ == 'b_CG':
        for price_zone in grid.Price_Zones:
            if ts.element_name == price_zone.name:
                price_zone.TS_dict[typ] = ts.TS_num
                break
    elif typ == 'c_CG':
        for price_zone in grid.Price_Zones:
            if ts.element_name == price_zone.name:
                price_zone.TS_dict[typ] = ts.TS_num
                break
    elif typ == 'PGL_min':
        for price_zone in grid.Price_Zones:
            if ts.element_name == price_zone.name:
                price_zone.TS_dict[typ] = ts.TS_num
                break
    elif typ == 'PGL_max':
        for price_zone in grid.Price_Zones:
            if ts.element_name == price_zone.name:
                price_zone.TS_dict[typ] = ts.TS_num
                break
                
    if typ == 'price':
        for price_zone in grid.Price_Zones:
            if ts.element_name == price_zone.name:
                price_zone.TS_dict[typ] = ts.TS_num
                break  # Stop after assigning to the correct price_zone
        for node in grid.nodes_AC + grid.nodes_DC:
            if ts.element_name == node.name:
                node.TS_dict[typ] = ts.TS_num
                break  # Stop after assigning to the correct node    
    
    elif typ == 'Load':
        for price_zone in grid.Price_Zones:
            if ts.element_name == price_zone.name:
                price_zone.TS_dict[typ] = ts.TS_num
                break  # Stop after assigning to the correct price_zone
        for node in grid.nodes_AC + grid.nodes_DC:
            if ts.element_name == node.name:
                node.TS_dict[typ] = ts.TS_num
                break  # Stop after assigning to the correct node
                
    elif typ in ['WPP', 'OWPP', 'SF', 'REN']:
        for zone in grid.RenSource_zones:
            if ts.element_name == zone.name:
                zone.TS_dict['PRGi_available'] = ts.TS_num
                break  # Stop after assigning to the correct zone
        for rs in grid.RenSources:
            if ts.element_name == rs.name:
                rs.TS_dict['PRGi_available'] = ts.TS_num
                break  # Stop after assigning to the correct node


def add_TimeSeries(Grid, Time_Series_data,associated=None,TS_type=None,name=None):
    # Check if Time_Series_data is a numpy array and convert to pandas DataFrame if needed
    if not isinstance(Time_Series_data, pd.DataFrame):
        TS = pd.DataFrame(Time_Series_data, columns=[name])
    else:
        TS = Time_Series_data
    Time_series = {}
    # check if there are nan values in Time series and change to 0
    TS.fillna(0, inplace=True)
    
    for col in TS.columns:
        if associated is not None and TS_type is not None:
            element_name = associated
            element_type = TS_type
            data = TS.loc[0:, col].astype(float).to_numpy()  
            name = col
            
        
        elif associated is not None: 
            element_name = associated
            element_type = TS.at[0, col]
            data = TS.loc[1:, col].astype(float).to_numpy()  
            name = col
        
        elif TS_type is not None:
            element_name = TS.at[0, col]
            element_type = TS_type
            data = TS.loc[1:, col].astype(float).to_numpy()   
            name = col
        
        else: 
            element_name = TS.at[0, col]
            element_type = TS.at[1, col]
            data = TS.loc[2:, col].astype(float).to_numpy()   
            name = col
            
        
        Time_serie = TimeSeries(element_type, element_name, data,name)                  
        Grid.Time_series.append(Time_serie)
        Grid.Time_series_dic[name]=Time_serie.TS_num
        time_series_dict(Grid, Time_serie)
        
        
        
    Grid.Time_series_ran = False
    s = 1


def assign_RenToZone(Grid,ren_source_name,new_zone_name):
    new_zone = None
    old_zone = None
    ren_source_to_reassign = None
    
    for RenZone in Grid.RenSource_zones:
        if RenZone.name == new_zone_name:
            new_zone = RenZone
            break
    if new_zone is None:
        raise ValueError(f"Zone {new_zone_name} not found.")
    
    # Remove node from its old price_zone
    for RenZone in Grid.RenSource_zones:
        for ren_source in RenZone.RenSources:
            if ren_source.name == ren_source_name:
                old_zone = RenZone
                ren_source_to_reassign = ren_source
                break
        if old_zone:
            break
        
    if old_zone is not None:
        RenZone.ren_source = [ren_source for ren_source in old_zone.RenSources 
                               if ren_source.name != ren_source_name]
    
    # If the node was not found in any Renewable zone, check Grid.nodes_AC
    if ren_source_to_reassign is None:
        for ren_source in Grid.RenSources:
            if ren_source.name == ren_source_name:
                ren_source_to_reassign = ren_source
                break
            
    if ren_source_to_reassign is None:
        raise ValueError(f"Renewable source {ren_source_name} not found.")
    ren_source_to_reassign.PGRi_linked = True
    ren_source_to_reassign.Ren_source_zone = new_zone.name
    # Add node to the new price_zone
    if ren_source_to_reassign not in new_zone.RenSources:
        new_zone.RenSources.append(ren_source_to_reassign)
 
"Assigning components to zones"
    
def assign_nodeToPrice_Zone(Grid,node_name, new_price_zone_name,ACDC='AC'):
        """ Assign node to a new price_zone and remove it from its previous price_zone """
        new_price_zone = None
        old_price_zone = None
        node_to_reassign = None
        
        nodes_attr = 'nodes_DC' if ACDC == 'DC' else 'nodes_AC'
        
        # Find the new price_zone
        for price_zone in Grid.Price_Zones:
            if price_zone.name == new_price_zone_name:
                new_price_zone = price_zone
                break

        if new_price_zone is None:
            raise ValueError(f"Price_Zone {new_price_zone_name} not found.")
        
        # Remove node from its old price_zone
        for price_zone in Grid.Price_Zones:
            nodes = getattr(price_zone, nodes_attr)
            for node in nodes:
                if node.name == node_name:
                    old_price_zone = price_zone
                    node_to_reassign = node
                    break
            if old_price_zone:
                break
            
        if old_price_zone is not None:
            setattr(old_price_zone, nodes_attr, [node for node in getattr(old_price_zone, nodes_attr) if node.name != node_name])

        # If the node was not found in any price_zone, check Grid.nodes_AC
        if node_to_reassign is None:
            nodes = getattr(Grid, nodes_attr)
            for node in nodes:
                if node.name == node_name:
                    node_to_reassign = node
                    break
                
        if node_to_reassign is None:
            raise ValueError(f"Node {node_name} not found.")
        
        # Add node to the new price_zone
        new_price_zone_nodes = getattr(new_price_zone, nodes_attr)
        if node_to_reassign not in new_price_zone_nodes:
            new_price_zone_nodes.append(node_to_reassign)
            node_to_reassign.PZ=new_price_zone.name
            node_to_reassign.price=new_price_zone.price

def assign_ConvToPrice_Zone(Grid, conv_name, new_price_zone_name):
        """ Assign node to a new price_zone and remove it from its previous price_zone """
        new_price_zone = None
        old_price_zone = None
        conv_to_reassign = None
        
        # Find the new price_zone
        for price_zone in Grid.Price_Zones:
            if price_zone.name == new_price_zone_name:
                new_price_zone = price_zone
                break

        if new_price_zone is None:
            raise ValueError(f"Price_Zone {new_price_zone_name} not found.")
        
        # Remove node from its old price_zone
        for price_zone in Grid.Price_Zones:
            for conv in price_zone.ConvACDC:
                if conv.name == conv_name:
                    old_price_zone = price_zone
                    conv_to_reassign = conv
                    break
            if old_price_zone:
                break
            
        if old_price_zone is not None:
            old_price_zone.ConvACDC = [conv for conv in old_price_zone.ConvACDC if conv.name != conv_name]
        
        # If the node was not found in any price_zone, check Grid.nodes_AC
        if conv_to_reassign is None:
            for conv in Grid.Converters_ACDC:
                if conv.name == conv_name:
                    conv_to_reassign = conv
                    break
                
        if conv_to_reassign is None:
            raise ValueError(f"Converter {conv_name} not found.")
        
        # Add node to the new price_zone
        if conv_to_reassign not in new_price_zone.ConvACDC:
            new_price_zone.ConvACDC.append(conv_to_reassign)            

def assign_lineToCable_options(Grid,line_name, new_cable_option_name):
    """ Assign line to a new cable_type and remove it from its previous cable_type """
    new_cable_option = None
    old_cable_option = None
    line_to_reassign = None

    for cable_option in Grid.Cable_options:
        if cable_option.name == new_cable_option_name:
            new_cable_option = cable_option
            break

    if new_cable_option is None:
        raise ValueError(f"Cable_option {new_cable_option_name} not found.")

    # Remove line from its old cable_option
    for cable_option in Grid.Cable_options: 
        for line in cable_option.lines:
            if line.name == line_name:
                old_cable_option = cable_option
                line_to_reassign = line
                break
        if old_cable_option:
            break

    if old_cable_option is not None:
        old_cable_option.lines = [line for line in old_cable_option.lines if line.name != line_name]    

    if line_to_reassign is None:
        for line in Grid.lines_AC_ct:
            if line.name == line_name:
                line_to_reassign = line
                break
        if line_to_reassign is None:
            raise ValueError(f"Line {line_name} not found.")

    # Add line to the new cable_option
    if line_to_reassign not in new_cable_option.lines:
        new_cable_option.lines.append(line_to_reassign) 
        line_to_reassign.cable_types = new_cable_option.cable_types





def expand_cable_database(data, format='yaml', save_yalm=False):
    """
    Expand the cable database by adding new cable specifications.
    
    Args:
        data: Either a path to YAML file, DataFrame, or dictionary with cable specifications
        format: 'yaml' or 'pandas' (default: 'yaml')
        output_path: Optional path to save the new YAML file (default: None)
        # Cable specifications

    Units:
       - Resistance: ohm/km
       - Inductance: mH/km
       - Capacitance: uF/km
       - Conductance: uS/km
       - Current rating: A
       - Power rating: MVA
       - Nominal voltage: kV
       - conductor_size: mm^2
       - Type: AC or DC

    Example YAML format:

    NEW_CABLE_TYPE:
        R_Ohm_km: 0.001
        L_mH_km: 0.001
        C_uF_km: 0.001
        G_uS_km: 0.001
        A_rating: 333
        Nominal_voltage_kV: 60
        MVA_rating: sqrt(3)*Nominal_voltage_kV*A_rating/1000
        conductor_size: 100
        Type: AC or DC
        Reference: REFERENCE
    """
    
    # Get the path to the Cable_database directory
    module_dir = Path(__file__).parent.parent
    cable_dir = module_dir / 'Cable_database'
    
    if format.lower() == 'yaml':
        if isinstance(data, (str, Path)):
            with open(data, 'r') as f:
                new_cables = yaml.safe_load(f)
        elif isinstance(data, dict):
            new_cables = data
        else:
            raise ValueError("For YAML format, data must be either a file path or dictionary")
            
    elif format.lower() == 'pandas':
        if isinstance(data, pd.DataFrame):
            new_cables = data.to_dict(orient='index')
        elif isinstance(data, (str, Path)):
            df = pd.read_csv(data)
            new_cables = df.to_dict(orient='index')
        else:
            raise ValueError("For pandas format, data must be either a DataFrame or file path")
    
   
    if save_yalm:
        # Save each cable type as a separate file
        for cable_name, cable_specs in new_cables.items():
            # Create a single-cable dictionary
            cable_data = {cable_name: cable_specs}
            
            # Create file path using cable name
            output_file = cable_dir / f"{cable_name}.yaml"
            
            # Save to YAML file
            with open(output_file, 'w') as f:
                yaml.dump(cable_data, f, sort_keys=False)
            
            print(f"Saved cable {cable_name} to {output_file}")
    
    # split ac and dc cables
    new_cables_ac = {}
    new_cables_dc = {}
    for key, value in new_cables.items():
        if value['Type'] == 'AC':
            new_cables_ac[key] = value
        else:
            new_cables_dc[key] = value
    
    # Update the cable database
    if Line_DC._cable_database is None:
        Line_DC.load_cable_database()
    if Line_AC._cable_database is None:
        Line_AC.load_cable_database()
    # Add new cables to existing database
    Line_DC._cable_database = pd.concat([
        Line_DC._cable_database,
        pd.DataFrame.from_dict(new_cables_dc, orient='index')
    ])
    Line_AC._cable_database = pd.concat([
        Line_AC._cable_database,
        pd.DataFrame.from_dict(new_cables_ac, orient='index')
    ])


    print(f"Added {len(new_cables_ac)} new cables to AC and {len(new_cables_dc)} new cables to DC database")





    

