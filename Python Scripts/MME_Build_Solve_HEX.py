# 
#	Name:
#	MME Build and Solve
#
#	Purpose:
#   Generate RVE models with a given volume fraction (Square and Hex packing)
#		Apply constituent properties
#		Apply boundary conditions
#		Solve
#
# 	Usage:
#   Python -> Run
#
# 	Dependencies:
#	Uses PyMentat functions:
#		py_send
#       py_get_float
#       py_get_string
#	Pythons modules:
#		math module
#		os module
#	Must be run after:
#		MME_Parameters_xxx.py
#

from py_mentat import *
from py_post import *
import os
import os.path
import math

# creates a string from a list
def list2str(lst) :
    str=''
    for i in lst:
        str += `i` + ' ' + '\n'
    return str

# rounds a positive number to the nearest even integer
def round2(num) :
    rnd=0
    rnd=int(num/2.0+0.5)*2
    return rnd

#creates a node given co-ordinates
def create_node(x1,y1,z1):
    str = "*add_nodes %f %f %f" % (x1, y1, z1)
    py_send(str)
    return

#creates a point given co-ordinates
def create_point(x1,y1,z1):
    str = "*add_points %f %f %f" % (x1, y1, z1)
    py_send(str)
    return

#select nodes given box co-ordinates
def select_box_nodes(x1,x2,y1,y2,z1,z2):
    py_send("*select_method_box")
    py_send("*select_nodes")
    py_send("%f %f" % (x1,x2))
    py_send("%f %f" % (y1,y2))
    py_send("%f %f" % (z1,z2))
    return

#select elements given box co-ordinates
def select_box_elements(x1,x2,y1,y2,z1,z2):
    py_send("*select_method_box")
    py_send("*select_elements")
    py_send("%f %f" % (x1,x2))
    py_send("%f %f" % (y1,y2))
    py_send("%f %f" % (z1,z2))
    return    

# main function
def main():
    # reading the volume fraction and material parameters
    # lamina
    mat_name = py_get_string("material_name")
    vf = py_get_float("volume_fraction")
    young_l1 = py_get_float("youngs_modulus_laminate_1")
    young_l2 = py_get_float("youngs_modulus_laminate_2")
    young_l3 = py_get_float("youngs_modulus_laminate_3")
    shear_l12 = py_get_float("shear_modulus_laminate_12")
    shear_l23 = py_get_float("shear_modulus_laminate_23")
    shear_l31 = py_get_float("shear_modulus_laminate_31")
    nu_l12 = py_get_float("poissons_ratio_laminate_12")
    nu_l23 = py_get_float("poissons_ratio_laminate_23")
    nu_l31 = py_get_float("poissons_ratio_laminate_31")
    alpha_l1 = py_get_float("thermexp_coeff_laminate_1")
    alpha_l2 = py_get_float("thermexp_coeff_laminate_2")
    alpha_l3 = py_get_float("thermexp_coeff_laminate_3")
    
    # fibre
    young_f1 = py_get_float("youngs_modulus_fibre_1")
    young_f2 = py_get_float("youngs_modulus_fibre_2")
    young_f3 = py_get_float("youngs_modulus_fibre_3")
    shear_f12 = py_get_float("shear_modulus_fibre_12")
    shear_f23 = py_get_float("shear_modulus_fibre_23")
    shear_f31 = py_get_float("shear_modulus_fibre_31")
    nu_f12 = py_get_float("poissons_ratio_fibre_12")
    nu_f23 = py_get_float("poissons_ratio_fibre_23")
    nu_f31 = py_get_float("poissons_ratio_fibre_31")
    alpha_f1 = py_get_float("thermexp_coeff_fibre_1")
    alpha_f2 = py_get_float("thermexp_coeff_fibre_2")
    alpha_f3 = py_get_float("thermexp_coeff_fibre_3")
    
    #resin
    young_m = py_get_float("youngs_modulus_matrix")
    nu_m = py_get_float("poissons_ratio_matrix")
    alpha_m = py_get_float("thermexp_coeff_matrix")
    
    # constants
    pi=math.pi
    root2=math.sqrt(2.0)
    root3=math.sqrt(3.0)
    cos45=math.cos(pi/4)
    sin45=math.sin(pi/4)
    cos30=math.cos(pi/6)
    sin30=math.sin(pi/6)
    cos15=math.cos(pi/12)
    sin15=math.sin(pi/12)
    
    # displacement
    disp=1.0e-6

    # temperature difference
    dt=-1.0

    # meshing
    fibre_radial = 15
    fibre_radial_bias = 3
    fibre_circum = 16*12
    fibre_axial = 10
    matrix_radial = 6
    
    # tolerance
    sweep_tol = 0.001
    
    # start model creation for each arrangement
    for iarrang in range(2,3):
        if(iarrang==1):        
            arrangement_name = "square"
            dispx=disp
            dispy=disp
            dispz=disp
            shrinkx=dt*alpha_l1
            shrinky=dt*alpha_l2
            shrinkz=dt*alpha_l3
        elif(iarrang==2):
            arrangement_name = "hex"
            dispx=disp
            dispy=disp
            dispz=disp*root3
            shrinkx=dt*alpha_l1
            shrinky=dt*alpha_l2
            shrinkz=dt*alpha_l3*root3
        else:
            return

        # create new model
        py_echo(0)
        py_send("*new_model")
        py_send("yes")
        py_send("*clear_mesh")
        py_send("*clear_geometry")
        py_send("*remove_all_applys")
        py_send("*dynamic_model_off ")

        # error handling
        ierror=0
        if (iarrang < 1) or (iarrang > 2):
            ierror=1
            str = 'Error: inappropriate code for arrangment \n'
            str = str + 'Enter 1 for square arrangment or 2 for diagonal \n'
            str = str + 'Example: *define arrangement 1'
            py_prompt(str)

        if (young_f1 == 0.e0) or (young_f2 == 0.e0) or (young_f3 == 0.e0) :
            ierror=2
            str = 'Error: zero values in modulii'
            py_prompt(str)

        if (shear_f12 == 0.e0) or (shear_f23 == 0.e0) or (shear_f31 == 0.e0) :
            ierror=3
            str = 'Error: zero values in modulii'
            py_prompt(str)

        vf_min=0.1
        vf_max=0.7
        if(iarrang==2):
            vf_max=0.8
        if (vf < vf_min) or (vf > vf_max):
            ierror=4
            str = 'Error: Volume fraction not viable \n'
            str = str + 'Example: *define volume_fraction 0.6'
            py_prompt(str)

        if (ierror>0):
            return

        #****************#
        # model creation #
        #****************#
        
        py_send("*system_reset")
        # model and meshing
        if(iarrang==1):                                 # square arrangement
            r=math.sqrt(vf/pi)
            angle_r=pi/4.0
            angle_d=45
            w=1.0
            h=1.0
        elif(iarrang==2):                               # diagonal arrangement
            r=math.sqrt((root3/2.0)*(vf/pi))
            angle_r=pi/6.0
            angle_d=30
            w=1.0
            h=root3
        else:
            return
        
        # create fibre segment
        ## geometry
        create_point(0.,0.,0.) # pt 1
        py_send("*system_align 0 0 0 0 1 0 0 0 1")
        py_send("*set_curve_type arc_craa")
        py_send("*add_curves 0. 0. 0. %f 0. %f" % (r,angle_d)) # pts 2-4 cv 1
        py_send("*set_curve_type line")
        py_send("*add_curves 2 1") # cv 2
        py_send("*add_curves 4 1") # cv 3
        
        ## mesh
        py_send("*set_curve_div_type_fix")
        py_send("*set_curve_div_num %i" % (int(fibre_circum*angle_d/360)))
        py_send("*apply_curve_divisions 1 #")
        py_send("*set_curve_div_type_variable_l1l2")
        py_send("*set_curve_div_opt_ndiv_l2l1_ratio")
        py_send("*set_curve_div_num %i" % (fibre_radial))
        py_send("*set_curve_div_l2l1_ratio %i" % (fibre_radial_bias))
        py_send("*apply_curve_divisions 2 3 #")
        py_send("*af_planar_quadmesh all_visible")
        py_send("*set_change_class quad8")
        py_send("*change_elements_class all_visible")

        ## material properties - fibre
        py_send("*new_mater standard *mater_option general:state:solid ")
        py_send("*mater_name ")
        py_send("fibre ")
        py_send("*mater_option structural:type:elast_plast_ortho")
        py_send("*mater_param structural:youngs_modulus1 %f " % (young_f1))
        py_send("*mater_param structural:youngs_modulus2 %f " % (young_f2))
        py_send("*mater_param structural:youngs_modulus3 %f " % (young_f3))
        py_send("*mater_param structural:shear_modulus12 %f " % (shear_f12))
        py_send("*mater_param structural:shear_modulus23 %f " % (shear_f23))
        py_send("*mater_param structural:shear_modulus31 %f " % (shear_f31))
        py_send("*mater_param structural:poissons_ratio12 %f " % (nu_f12))
        py_send("*mater_param structural:poissons_ratio23 %f " % (nu_f23))
        py_send("*mater_param structural:poissons_ratio31 %f " % (nu_f31))
        py_send("*mater_option structural:thermal_expansion:on")
        py_send("*mater_param structural:thermal_exp1 %f " % (alpha_f1))
        py_send("*mater_param structural:thermal_exp2 %f " % (alpha_f2))
        py_send("*mater_param structural:thermal_exp3 %f " % (alpha_f3))
        py_send("*add_mater_elements")
        py_send("*all_existing")
        py_send("*invisible_all")

        # create matrix region
        ## geometry
        create_point(0.5,0.,0.) #pt 5
        create_point(0.5,w*math.tan(angle_r)/2,0.) #pt 6
        py_send("*set_curve_type arc_craa")
        py_send("*add_curves 0. 0. 0. %f 0. %f" % (r,angle_d)) # pts 7-9 cv 4
        py_send("*set_curve_type line")
        py_send("*add_curves 7 5") # cv 5
        py_send("*add_curves 9 6") # cv 6
        py_send("*add_curves 5 6") # cv 7     

        ## mesh
        py_send("*set_curve_div_type_fix")
        py_send("*set_curve_div_num %i" % (round2(fibre_circum*angle_d/360)))
        py_send("*apply_curve_divisions 4 #")
        py_send("*set_curve_div_num %i" % (round2(matrix_radial)))
        py_send("*apply_curve_divisions 5 #")
        radial_length_short = w/2-r
        radial_length_long = w/(2*math.cos(angle_r))-r
        circum_length = w*math.tan(angle_r)/2
        size = radial_length_short/matrix_radial
        py_send("*set_curve_div_num %i" % (round2(radial_length_long/size)))
        py_send("*apply_curve_divisions 6 #")
        size = r*angle_r/round2(fibre_circum*angle_d/360)
        py_send("*set_curve_div_num %i" % (round2(circum_length/size)))
        py_send("*apply_curve_divisions 7 #")
        py_send("*af_planar_quadmesh all_visible")
        py_send("*set_change_class quad8")
        py_send("*change_elements_class all_visible")

        ## material properties - matrix
        py_send("*new_mater standard *mater_option general:state:solid ")
        py_send("*mater_name ")
        py_send("matrix ")
        py_send("*mater_param structural:youngs_modulus %f " % (young_m))
        py_send("*mater_param structural:poissons_ratio %f" % (nu_m))
        py_send("*mater_option structural:thermal_expansion:on")
        py_send("*mater_param structural:thermal_exp %f " % (alpha_m))
        py_send("*add_mater_elements all_visible")
        py_send("*visible_all")

        # mirror elements
        py_send("*system_reset")
        py_send("*set_symmetry_point 0. 0. 0.")
        if(iarrang==1):
            py_send("*set_symmetry_normal 0,%f,%f" % (-sin45,cos45))
            py_send("*symmetry_elements all_existing")
        elif(iarrang==2):
            py_send("*select_method_single")
            py_send("*select_elements all_visible")
            py_send("*set_symmetry_normal 0,%f,%f" % (-sin30,cos30))
            py_send("*symmetry_elements all_existing")
            py_send("*invisible_selected")
            py_send("*set_symmetry_normal 0,%f,%f" % (-cos30,sin30))
            py_send("*symmetry_elements all_visible")
            py_send("*visible_all")
            py_send("*set_duplicate_point 0,%f,%f " % (w/4,h/4))
            py_send("*set_duplicate_rotations")
            py_send("180,0,0")
            py_send("*duplicate_elements")
            py_send("all_existing")
        else:
            return
        py_send("*set_symmetry_normal")
        py_send("0,1,0")
        py_send("*symmetry_elements all_existing")
        py_send("*set_symmetry_normal")
        py_send("0,0,1")
        py_send("*symmetry_elements all_existing")
        
        # expand shells to solids
        py_send("*set_expand_rotations 0,0,0")
        py_send("*set_expand_translations %f,0,0 " % (1.0/fibre_axial))
        py_send("*set_expand_repetitions %f " % (fibre_axial))
        py_send("*expand_elements all_existing")

        # sweep
        py_send("*set_sweep_tolerance %f" % (sweep_tol))
        py_send("*sweep_nodes all_existing")
        py_send("*remove_unused_nodes")
        
        # define boundary node sets
        e = 1e-3
        b = 10
        
        # x0_nodes
        select_box_nodes(-e,+e,-b,b,-b,b)
        py_send("*store_nodes x0_nodes all_selected")
        py_send("*select_clear_nodes")
        
        # x01_nodes
        select_box_nodes(w-e,w+e,-b,b,-b,b)
        py_send("*store_nodes x1_nodes all_selected")  
        py_send("*select_clear_nodes") 
        
        # y0_nodes
        select_box_nodes(-b,b,-w/2-e,-w/2+e,-b,b)
        py_send("*store_nodes y0_nodes all_selected") 
        py_send("*select_clear_nodes") 
        
        # y1_nodes
        select_box_nodes(-b,b,w/2-e,w/2+e,-b,b)
        py_send("*store_nodes y1_nodes all_selected")    
        py_send("*select_clear_nodes") 

        # z0_nodes
        select_box_nodes(-b,b,-b,b,-h/2-e,-h/2+e)
        py_send("*store_nodes z0_nodes all_selected")
        py_send("*select_clear_nodes") 

        # z1_nodes
        select_box_nodes(-b,b,-b,b,h/2-e,h/2+e)
        py_send("*store_nodes z1_nodes all_selected")   
        py_send("*select_clear_nodes")
        
        # create element sets
        # fibre
        py_send("*select_clear_elements")
        py_send("*select_method_single")
        py_send("*select_elements_material fibre")
        py_send("*store_elements")
        py_send("Fibre")
        py_send("all_selected")
        py_send("*select_clear_elements")
        
        # matrix
        py_send("*select_method_single")
        py_send("*select_elements_material matrix")
        py_send("*store_elements")
        py_send("Matrix")
        py_send("all_selected")
        py_send("*select_clear_elements")
        
        # front elements (to see strains at mid-plane of model)
        select_box_elements(w/2-e,w+e,-b,b,-b,b)
        py_send("*store_elements Front all_selected")
        py_send("*select_clear_elements")
		
        #************#
        # normal bcs #
        #************#
        
        #fix_x0
        py_send("*new_apply")
        py_send("*apply_name")
        py_send("fix_x0")
        py_send("*apply_type fixed_displacement")
        py_send("*apply_dof x")
        py_send("*apply_dof_value x 0")
        py_send("*select_sets x0_nodes")
        py_send("*add_apply_nodes ")
        py_send("all_selected")
        py_send("*select_clear_nodes")

        #fix_x1
        py_send("*new_apply")
        py_send("*apply_name")
        py_send("fix_x1")
        py_send("*apply_type fixed_displacement")
        py_send("*apply_dof x *apply_dof_value x")
        py_send("*apply_dof_value x 0")
        py_send("*select_sets x1_nodes")
        py_send("*add_apply_nodes ")
        py_send("all_selected")
        py_send("*select_clear_nodes")

        #fix_y0
        py_send("*new_apply")
        py_send("*apply_name")
        py_send("fix_y0")
        py_send("*apply_type fixed_displacement")
        py_send("*apply_dof y *apply_dof_value y")
        py_send("0")
        py_send("*select_sets y0_nodes")
        py_send("*add_apply_nodes ")
        py_send("all_selected")
        py_send("*select_clear_nodes")

        #fix_y1
        py_send("*new_apply")
        py_send("*apply_name")
        py_send("fix_y1")
        py_send("*apply_type fixed_displacement")
        py_send("*apply_dof y *apply_dof_value y")
        py_send("0")
        py_send("*select_sets y1_nodes")
        py_send("*add_apply_nodes ")
        py_send("all_selected")
        py_send("*select_clear_nodes")

        #fix_z0
        py_send("*new_apply")
        py_send("*apply_name")
        py_send("fix_z0")
        py_send("*apply_type fixed_displacement")
        py_send("*apply_dof z *apply_dof_value z")
        py_send("0")
        py_send("*add_apply_nodes")
        py_send("*select_sets z0_nodes")
        py_send("*add_apply_nodes ")
        py_send("all_selected")
        py_send("*select_clear_nodes")

        #fix_z1
        py_send("*new_apply")
        py_send("*apply_name")
        py_send("fix_z1")
        py_send("*apply_type fixed_displacement")
        py_send("*apply_dof z *apply_dof_value z")
        py_send("0")
        py_send("*add_apply_nodes")
        py_send("*select_sets z1_nodes")
        py_send("*add_apply_nodes ")
        py_send("all_selected")
        py_send("*select_clear_nodes")

        #pull_x
        py_send("*new_apply")
        py_send("*apply_name")
        py_send("pull_x")
        py_send("*apply_type fixed_displacement")
        py_send("*apply_dof x *apply_dof_value x")
        py_send("*apply_dof_value x " + `dispx`)
        py_send("*add_apply_nodes")
        py_send("*select_sets x1_nodes")
        py_send("*add_apply_nodes ")
        py_send("all_selected")
        py_send("*select_clear_nodes")

        #pull_y
        py_send("*new_apply")
        py_send("*apply_name")
        py_send("pull_y")
        py_send("*apply_type fixed_displacement")
        py_send("*apply_dof y *apply_dof_value y")
        py_send("*apply_dof_value y " + `dispy`)
        py_send("*add_apply_nodes")
        py_send("*select_sets y1_nodes")
        py_send("*add_apply_nodes ")
        py_send("all_selected")
        py_send("*select_clear_nodes")

        #pull_z
        py_send("*new_apply")
        py_send("*apply_name")
        py_send("pull_z")
        py_send("*apply_type fixed_displacement")
        py_send("*apply_dof z *apply_dof_value z")
        py_send("*apply_dof_value z " + `dispz`)
        py_send("*add_apply_nodes")
        py_send("*select_sets z1_nodes")
        py_send("*add_apply_nodes ")
        py_send("all_selected")
        py_send("*select_clear_nodes")

        #shrink_x
        py_send("*new_apply")
        py_send("*apply_name")
        py_send("shrink_x")
        py_send("*apply_type fixed_displacement")
        py_send("*apply_dof x *apply_dof_value x")
        py_send("*apply_dof_value x " + `shrinkx`)
        py_send("*add_apply_nodes")
        py_send("*select_sets x1_nodes")
        py_send("*add_apply_nodes ")
        py_send("all_selected")
        py_send("*select_clear_nodes")
        
        #shrink_y
        py_send("*new_apply")
        py_send("*apply_name")
        py_send("shrink_y")
        py_send("*apply_type fixed_displacement")
        py_send("*apply_dof y *apply_dof_value y")
        py_send("*apply_dof_value y " + `shrinky`)
        py_send("*add_apply_nodes")
        py_send("*select_sets y1_nodes")
        py_send("*add_apply_nodes ")
        py_send("all_selected")
        py_send("*select_clear_nodes")
        
        #shrink_z
        py_send("*new_apply")
        py_send("*apply_name")
        py_send("shrink_z")
        py_send("*apply_type fixed_displacement")
        py_send("*apply_dof z *apply_dof_value z")
        py_send("*apply_dof_value z " + `shrinkz`)
        py_send("*add_apply_nodes")
        py_send("*select_sets z1_nodes")
        py_send("*add_apply_nodes ")
        py_send("all_selected")
        py_send("*select_clear_nodes")

        #***********#
        # shear bcs #
        #***********#

        #fix_u_at_y0
        py_send("*new_apply")
        py_send("*apply_name")
        py_send("fix_u_at_y0")
        py_send("*apply_type fixed_displacement")
        py_send("*apply_dof x *apply_dof_value x")
        py_send("*apply_dof_value x 0")
        py_send("*add_apply_nodes")
        py_send("*select_sets y0_nodes")
        py_send("*add_apply_nodes ")
        py_send("all_selected")
        py_send("*select_clear_nodes")

        #fix_u_at_z0
        py_send("*new_apply")
        py_send("*apply_name")
        py_send("fix_u_at_z0")
        py_send("*apply_type fixed_displacement")
        py_send("*apply_dof x *apply_dof_value x")
        py_send("*apply_dof_value x 0")
        py_send("*add_apply_nodes")
        py_send("*select_sets z0_nodes")
        py_send("*add_apply_nodes ")
        py_send("all_selected")
        py_send("*select_clear_nodes")
        
        #pull_u_at_y1
        py_send("*new_apply")
        py_send("*apply_name")
        py_send("pull_u_at_y1")
        py_send("*apply_type fixed_displacement")
        py_send("*apply_dof x *apply_dof_value x")
        py_send("*apply_dof_value x " + `dispy/2`)
        py_send("*add_apply_nodes")
        py_send("*select_sets y1_nodes")
        py_send("*add_apply_nodes ")
        py_send("all_selected")
        py_send("*select_clear_nodes")
        
        #pull_u_at_z1
        py_send("*new_apply")
        py_send("*apply_name")
        py_send("pull_u_at_z1")
        py_send("*apply_type fixed_displacement")
        py_send("*apply_dof x *apply_dof_value x")
        py_send("*apply_dof_value x " + `dispz/2`)
        py_send("*add_apply_nodes")
        py_send("*select_sets z1_nodes")
        py_send("*add_apply_nodes ")
        py_send("all_selected")
        py_send("*select_clear_nodes")

        #fix_v_at_x0
        py_send("*new_apply")
        py_send("*apply_name")
        py_send("fix_v_at_x0")
        py_send("*apply_type fixed_displacement")
        py_send("*apply_dof y *apply_dof_value y")
        py_send("*apply_dof_value y 0")
        py_send("*add_apply_nodes")
        py_send("*select_sets x0_nodes")
        py_send("*add_apply_nodes ")
        py_send("all_selected")
        py_send("*select_clear_nodes")

        #fix_v_at_z0
        py_send("*new_apply")
        py_send("*apply_name")
        py_send("fix_v_at_z0")
        py_send("*apply_type fixed_displacement")
        py_send("*apply_dof y *apply_dof_value y")
        py_send("*apply_dof_value y 0")
        py_send("*add_apply_nodes")
        py_send("*select_sets z0_nodes")
        py_send("*add_apply_nodes ")
        py_send("all_selected")
        py_send("*select_clear_nodes")
        
        #pull_v_at_x1
        py_send("*new_apply")
        py_send("*apply_name")
        py_send("pull_v_at_x1")
        py_send("*apply_type fixed_displacement")
        py_send("*apply_dof y *apply_dof_value y")
        py_send("*apply_dof_value y " + `dispx/2`)
        py_send("*add_apply_nodes")
        py_send("*select_sets x1_nodes")
        py_send("*add_apply_nodes ")
        py_send("all_selected")
        py_send("*select_clear_nodes")
        
        #pull_v_at_z1
        py_send("*new_apply")
        py_send("*apply_name")
        py_send("pull_v_at_z1")
        py_send("*apply_type fixed_displacement")
        py_send("*apply_dof y *apply_dof_value y")
        py_send("*apply_dof_value y " + `dispz/2`)
        py_send("*add_apply_nodes")
        py_send("*select_sets z1_nodes")
        py_send("*add_apply_nodes ")
        py_send("all_selected")
        py_send("*select_clear_nodes")

        #fix_w_at_x0
        py_send("*new_apply")
        py_send("*apply_name")
        py_send("fix_w_at_x0")
        py_send("*apply_type fixed_displacement")
        py_send("*apply_dof z *apply_dof_value z")
        py_send("*apply_dof_value z 0")
        py_send("*add_apply_nodes")
        py_send("*select_sets x0_nodes")
        py_send("*add_apply_nodes ")
        py_send("all_selected")
        py_send("*select_clear_nodes")

        #fix_w_at_y0
        py_send("*new_apply")
        py_send("*apply_name")
        py_send("fix_w_at_y0")
        py_send("*apply_type fixed_displacement")
        py_send("*apply_dof z *apply_dof_value z")
        py_send("*apply_dof_value z 0")
        py_send("*add_apply_nodes")
        py_send("*select_sets y0_nodes")
        py_send("*add_apply_nodes ")
        py_send("all_selected")
        py_send("*select_clear_nodes")
        
        #pull_w_at_x1
        py_send("*new_apply")
        py_send("*apply_name")
        py_send("pull_w_at_x1")
        py_send("*apply_type fixed_displacement")
        py_send("*apply_dof z *apply_dof_value z")
        py_send("*apply_dof_value z " + `dispx/2`)
        py_send("*add_apply_nodes")
        py_send("*select_sets x1_nodes")
        py_send("*add_apply_nodes ")
        py_send("all_selected")
        py_send("*select_clear_nodes")
        
        #pull_w_at_y1
        py_send("*new_apply")
        py_send("*apply_name")
        py_send("pull_w_at_y1")
        py_send("*apply_type fixed_displacement")
        py_send("*apply_dof z *apply_dof_value z")
        py_send("*apply_dof_value z " + `dispy/2`)
        py_send("*add_apply_nodes")
        py_send("*select_sets y1_nodes")
        py_send("*add_apply_nodes ")
        py_send("all_selected")
        py_send("*select_clear_nodes")

        #*************#
        # thermal bcs #
        #*************#  
        
        #init_temp
        py_send("*new_icond")
        py_send("*icond_name init_temp")
        py_send("*icond_type state_variable")
        py_send("*icond_dof var *icond_dof_value var 0")
        py_send("*add_icond_elements all_existing")

        #change_temp
        py_send("*new_apply")
        py_send("*apply_name change_temp")
        py_send("*apply_type state_variable")
        py_send("*apply_dof var *apply_dof_value var %f" % (dt))
        py_send("*add_apply_elements all_existing")
        
        #***********#
        # loadcases #
        #***********#    

        #normal_x
        py_send("*new_loadcase *loadcase_type struc:static")
        py_send("*loadcase_name normalX")
        py_send("*loadcase_value nsteps 1")
        py_send("*loadcase_value force 0.01")
        py_send("*clear_loadcase_loads")
        py_send("*add_loadcase_loads fix_x0")
        py_send("*add_loadcase_loads pull_x")
        py_send("*add_loadcase_loads fix_y0")
        py_send("*add_loadcase_loads fix_y1")
        py_send("*add_loadcase_loads fix_z0")
        py_send("*add_loadcase_loads fix_z1")

        #normal_y
        py_send("*new_loadcase *loadcase_type struc:static")
        py_send("*loadcase_name normalY")
        py_send("*loadcase_value nsteps 1")
        py_send("*loadcase_value force 0.01")
        py_send("*clear_loadcase_loads")
        py_send("*add_loadcase_loads fix_x0")
        py_send("*add_loadcase_loads fix_x1")
        py_send("*add_loadcase_loads fix_y0")
        py_send("*add_loadcase_loads pull_y")
        py_send("*add_loadcase_loads fix_z0")
        py_send("*add_loadcase_loads fix_z1")

        #normal_z
        py_send("*new_loadcase *loadcase_type struc:static")
        py_send("*loadcase_name normalZ")
        py_send("*loadcase_value nsteps 1")
        py_send("*loadcase_value force 0.01")
        py_send("*clear_loadcase_loads")
        py_send("*add_loadcase_loads fix_x0")
        py_send("*add_loadcase_loads fix_x1")
        py_send("*add_loadcase_loads fix_y0")
        py_send("*add_loadcase_loads fix_y1")
        py_send("*add_loadcase_loads fix_z0")
        py_send("*add_loadcase_loads pull_z")
        
        #shear_xy
        py_send("*new_loadcase *loadcase_type struc:static")
        py_send("*loadcase_name shearXY")
        py_send("*loadcase_value nsteps 1")
        py_send("*loadcase_value force 0.01")
        py_send("*clear_loadcase_loads")
        py_send("*add_loadcase_loads fix_z0")
        py_send("*add_loadcase_loads fix_z1")
        py_send("*add_loadcase_loads fix_u_at_y0")
        py_send("*add_loadcase_loads pull_u_at_y1")
        py_send("*add_loadcase_loads fix_v_at_x0")
        py_send("*add_loadcase_loads pull_v_at_x1")
        
        #shear_yz
        py_send("*new_loadcase *loadcase_type struc:static")
        py_send("*loadcase_name shearYZ")
        py_send("*loadcase_value nsteps 1")
        py_send("*loadcase_value force 0.01")
        py_send("*clear_loadcase_loads")
        py_send("*add_loadcase_loads fix_x0")
        py_send("*add_loadcase_loads fix_x1")
        py_send("*add_loadcase_loads fix_v_at_z0")
        py_send("*add_loadcase_loads pull_v_at_z1")
        py_send("*add_loadcase_loads fix_w_at_y0")
        py_send("*add_loadcase_loads pull_w_at_y1")

        #shear_zx
        py_send("*new_loadcase *loadcase_type struc:static")
        py_send("*loadcase_name shearZX")
        py_send("*loadcase_value nsteps 1")
        py_send("*loadcase_value force 0.01")
        py_send("*clear_loadcase_loads")
        py_send("*add_loadcase_loads fix_y0")
        py_send("*add_loadcase_loads fix_y1")
        py_send("*add_loadcase_loads fix_u_at_z0")
        py_send("*add_loadcase_loads pull_u_at_z1")
        py_send("*add_loadcase_loads fix_w_at_x0")
        py_send("*add_loadcase_loads pull_w_at_x1")

        #thermal
        py_send("*new_loadcase *loadcase_type struc:static")
        py_send("*loadcase_name thermal")
        py_send("*loadcase_value nsteps 1")
        py_send("*loadcase_value force 0.01")
        py_send("*clear_loadcase_loads")
        py_send("*add_loadcase_loads fix_x0")
        py_send("*add_loadcase_loads fix_y0")
        py_send("*add_loadcase_loads fix_z0")
        py_send("*add_loadcase_loads shrink_x")
        py_send("*add_loadcase_loads shrink_y")
        py_send("*add_loadcase_loads shrink_z")
        py_send("*add_loadcase_loads change_temp")

        #******#
        # jobs #
        #******# 
        
        mechanical_job_list = ["normalX","normalY","normalZ","shearXY","shearYZ","shearZX"]
        
        #mechanical jobs
        for job_name in mechanical_job_list:
            py_send("*new_job *job_class structural")
            py_send("*job_name %s" % job_name)
            py_send("*clear_job_applys")
            py_send("*add_job_loadcases %s" % job_name)
            py_send("*add_post_tensor el_strain")
            py_send("*add_post_nodal_quantity Displacement")
            py_send("*job_option post:ascii")
            py_send("*job_option dimen:three")
        
        #thermal job
        py_send("*new_job *job_class structural")
        py_send("*job_name thermal")
        py_send("*clear_job_applys")
        py_send("*add_job_iconds init_temp")
        py_send("*add_job_loadcases thermal")
        py_send("*add_post_tensor el_strain")
        py_send("*add_post_nodal_quantity Displacement")
        py_send("*job_option post:ascii")
        py_send("*job_option dimen:three")
        
        # # # # # # # # # # # # # # # # # # #
        # running the mechanical analyses   #
        # # # # # # # # # # # # # # # # # # #

        homedir=os.getcwd()
        modeldir= homedir + '\Models'
        modelname='MME_%s_%.2f_%s' % (mat_name,vf,arrangement_name)
        os.chdir(modeldir)
        py_send('*save_as_model %s.mud yes' % (modelname))
        runcmd = "run_marc -jid"
        options = "-nthread 4"
        print ''
        print 'Starting jobs for ' + modelname
        for job_name in mechanical_job_list:
            py_send("*edit_job %s" % (job_name))
            py_send("*job_write_input yes")
            print '   Running job: ' + job_name
            py_send('*system_command %s %s_%s %s' % (runcmd,modelname,job_name,options))
            

        # # # # # # # # # # # # # # # # #
        # running the thermal analysis  #
        # # # # # # # # # # # # # # # # #
        
        # submit thermal job
        py_send("*edit_job thermal")
        py_send("*job_write_input yes")
        print '   Running job: thermal'
        py_send('*system_command %s %s_thermal %s' % (runcmd,modelname,options))
        print 'Finished jobs for ' + modelname

        # save sift model
        py_send("*save_model")
        py_send("*dynamic_model_on ")
        os.chdir(homedir)
    return

if __name__ == '__main__':
    py_connect("",40007)
    main()
    py_disconnect()
