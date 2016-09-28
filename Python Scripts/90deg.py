#90deg sim runner
#runs simulations for a quarter coupon
#run this AFTER having imported the geometry

from py_mentat import *
from py_post import *
import os
import os.path
import math

def main():
	#initial definitions
	plate = 'TRUE' #do we have the doubler plate attached?
	material = 'T300' #change from T300 or T800 as required
	orientation = 'Y'
	
	#adding in the support and symmetry planes
	py_send("*set_surface_type quad")
	py_send("*add_points -10 0 -10 60.5 0 -10 -10 0 20 60.5 0 20")#large plane of symmetry
	py_send("*add_surfaces 1 2 3 4")
	py_send("*add_points 60.5 0 -10 60.5 0 20 60.5 5 -10 60.5 5 20")#Small plane of symmetry
	py_send("*add_surfaces 5 6 7 8")
	
	py_send("*set_surface_type cylinder")
	if plate == 'TRUE':
		py_send("*add_surfaces 60.5 0 -5 60.5 4.5 -5 5 5")
		py_send("*add_surfaces 22.5 0 15 22.5 4.5 15 5 5")
	else:
		py_send("*add_surfaces 60.5 0 -5 60.5 2.5 -5 5 5")
		py_send("*add_surfaces 22.5 0 15 22.5 2.5 15 5 5")
	
	#generating the tool movement table
	py_send("*new_md_table 1 1")
	py_send("*set_md_table_type 1 time")
	py_send("*table_add 0 0.0016 2000 0.0016 2000 0")
	py_send("*edit_table table1")
	py_send("*table_name ToolMovement")
	
	#setting material properties
	
	#T800 fibre
	py_send("*new_mater standard")
	py_send("*edit_mater material1 *mater_name T800")
	py_send("*mater_option structural:type:elast_plast_ortho")
	
	py_send("*mater_param structural:youngs_modulus1 152000")
	py_send("*mater_param structural:youngs_modulus2 8000")
	py_send("*mater_param structural:youngs_modulus3 8000")
	
	py_send("*mater_param structural:poissons_ratio12 0.34")
	py_send("*mater_param structural:poissons_ratio23 0.45")
	py_send("*mater_param structural:poissons_ratio31 0.0177")
	
	py_send("*mater_param structural:shear_modulus12 4000")
	py_send("*mater_param structural:shear_modulus23 2750")
	py_send("*mater_param structural:shear_modulus31 4000")
	
	#T300 fibre
	py_send("*new_mater standard")
	py_send("*edit_mater material2 *mater_name T300")
	py_send("*mater_option structural:type:elast_plast_ortho")
	
	py_send("*mater_param structural:youngs_modulus1 135000")
	py_send("*mater_param structural:youngs_modulus2 8000")
	py_send("*mater_param structural:youngs_modulus3 8000")
	
	py_send("*mater_param structural:poissons_ratio12 0.3")
	py_send("*mater_param structural:poissons_ratio23 0.45")
	py_send("*mater_param structural:poissons_ratio31 0.0177")
	
	py_send("*mater_param structural:shear_modulus12 5000")
	py_send("*mater_param structural:shear_modulus23 2760")
	py_send("*mater_param structural:shear_modulus31 5000")
	
	#fibreglass weave
	py_send("*new_mater standard")
	py_send("*edit_mater material3 *mater_name weave")
	py_send("*mater_option structural:type:elast_plast_iso")
	
	py_send("*mater_param structural:youngs_modulus 29700")
	py_send("*mater_param structural:poissons_ratio 0.17")
	
	#assigning materials
	py_send("*select_method_box")
	py_send("*select_elements -10 60.6 -10 2.5 -10 10")
	
	if material == 'T300':
		py_send("*edit_mater T300")
		py_send("*add_mater_elements all_selected")
	elif material == 'T800':
		py_send("*edit_mater T800")
		py_send("*add_mater_elements all_selected")
	
	py_send("*edit_mater weave")
	py_send("*add_mater_elements all_unselected")
	
	py_send("*new_orient *orient_type 3d_aniso")
	py_send("*edit_orient orientation1")
	if orientation == 'Y':
		py_send("*orient_param y1 1")
		py_send("*orient_param z2 1")
	elif orientation == 'Z':
		py_send("*orient_param z1 1")
		py_send("*orient_param y2 1")
	py_send("*add_orient_elements all_selected")
	
	#contact bodies
	py_send("*new_cbody mesh")
	py_send("*edit_contact_body cbody1")
	py_send("*contact_body_name Coupon")
	py_send("*add_contact_body_elements all_selected")
	
	py_send("*new_cbody mesh")
	py_send("*edit_contact_body cbody2")
	py_send("*contact_body_name Plate")
	py_send("*add_contact_body_elements all_unselected")
	
	py_send("*new_cbody geometry")
	py_send("*edit_contact_body cbody3")
	py_send("*contact_body_name BotCyl")
	py_send("*cbody_param_table vz ToolMovement")
	py_send("*contact_value vz 1")
	py_send("*add_contact_body_surfaces 3 # | End of List")
	
	py_send("*new_cbody geometry")
	py_send("*edit_contact_body cbody4")
	py_send("*contact_body_name TopCyl")
	py_send("*add_contact_body_surfaces 4 # | End of Lis")
	
	py_send("*new_cbody symmetry")
	py_send("*edit_contact_body cbody5")
	py_send("*contact_body_name LargeSym")
	py_send("*add_contact_body_surfaces 1 # | End of Lis")
	
	py_send("*new_cbody symmetry")
	py_send("*edit_contact_body cbody6")
	py_send("*contact_body_name SmallSym")
	py_send("*add_contact_body_surfaces 2 # | End of Lis")
	
	#assigning contact conditions
	py_send("*new_contact_table")
	py_send("*ctable_set_default_glued")
	
	#applying symmetry conditions
	py_send("*new_apply *apply_type fixed_displacement")
	py_send("*apply_name LargeSym")
	py_send("*apply_dof y *apply_dof_value y")
	py_send("*apply_dof rx *apply_dof_value rx")
	py_send("*apply_dof rz *apply_dof_value rz")

	py_send("*select_clear_elements")
	py_send("*select_nodes -10 100 -0.1 0.01 -20 20")

	py_send("*add_apply_nodes all_selected")
	
	py_send("*new_apply *apply_type fixed_displacement")
	py_send("*apply_name SmallSym")
	py_send("*apply_dof x *apply_dof_value x")
	py_send("*apply_dof ry *apply_dof_value ry")
	py_send("*apply_dof rz *apply_dof_value rz")

	py_send("*select_clear_nodes")
	py_send("*select_nodes 60.499 60.501 -10 10 -20 20") #should change this into a face selection

	py_send("*add_apply_nodes all_selected")
	
	#generating load case
	py_send("*new_loadcase *loadcase_type struc:static")
	py_send("*loadcase_value time 1200")
	py_send("*loadcase_value nsteps 100")
	py_send("*loadcase_ctable ctable1")
	py_send("*loadcase_option converge:resid_and_disp")
	py_send("*loadcase_value force 0.01")
	py_send("*loadcase_value displacement 0.01")
	
	#generating the job and running
	py_send("*new_job *job_class structural")
	py_send("*add_job_loadcases lcase1")
	py_send("*job_contact_table ctable1")
	py_send("*add_post_tensor el_strain")
	py_send("*job_option strain:large")
	py_send("*check_job")
	py_send("*update_job *submit_job 1 *monitor_job")

	
	return