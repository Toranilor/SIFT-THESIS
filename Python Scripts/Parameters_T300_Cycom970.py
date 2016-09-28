#
# sift_01_create_parameters.py
#
# Purpose:
#   SIFT failure criterion: To create the material parameter definitions
#
# Usage:
#   Python -> Run
#
# Dependencies
#	Uses PyMentat functions:
#	      py_send
#        Pythons modules:
#         math module
#         os module
#

from py_mentat import *
from py_post import *
import os
import os.path
import math


# main function
def main():

    py_send("*reset")

    #********#
    # lamina #
    #********#

    # name
    mat_name = "T300_CYCOM970"
    
    # volume fraction
    vf=0.6
    
    # youngs modulus
    young_l1=139.42e3
    young_l2=7.54e3
    
    # shear modulus
    shear_l12=3.4e3
    shear_l23=2.58e3

    # poissons ratio
    nu_l12=0.254
    nu_l23=0.463

    # thermal expansion coefficient
    alpha_l1=0.47e-6
    alpha_l2=28.94e-6

    #*******#
    # fibre #
    #*******#

    # youngs modulus
    young_f1=230e3
    young_f2=12e3

    # shear modulus
    shear_f12=9.85e3
    shear_f23=4.62e3

    # poissons ratio
    nu_f12=0.17
    nu_f23=0.3
    
    # thermal expansion coefficient
    alpha_f1=-0.54e-6
    alpha_f2=-22.5e-6

    #*******#
    # resin #
    #*******#
    
    # youngs modulus
    young_m=3.44e3
    
    # poissons ratio
    nu_m=0.389
    
    # thermal expansion coefficient
    alpha_m=80.55e-6

    # calculated values
    young_l3=young_l2
    shear_l31=shear_l12
    nu_l31=young_l2*nu_l12/young_l1 #calculated as Pzx=(Ez/Ex)*Pxz = (Ez/Ex)*Pxy
    alpha_l3 = alpha_l2
    young_f3=young_f2
    shear_f31=shear_f12
    nu_f31=young_f2*nu_f12/young_f1 #calculated as Pzx=(Ez/Ex)*Pxz = (Ez/Ex)*Pxy
    alpha_f3 = alpha_f2
    
    # define mentat parameters
    py_send("*define material_name %s" % (mat_name))
    py_send("*define volume_fraction %f " % (vf))
    py_send("*define youngs_modulus_laminate_1 %f " % (young_l1))
    py_send("*define youngs_modulus_laminate_2 %f " % (young_l2))
    py_send("*define youngs_modulus_laminate_3 %f " % (young_l3))
    py_send("*define shear_modulus_laminate_12 %f " % (shear_l12))
    py_send("*define shear_modulus_laminate_23 %f " % (shear_l23))
    py_send("*define shear_modulus_laminate_31 %f " % (shear_l31)) 
    py_send("*define poissons_ratio_laminate_12 %f " % (nu_l12))
    py_send("*define poissons_ratio_laminate_23 %f " % (nu_l23))
    py_send("*define poissons_ratio_laminate_31 %f " % (nu_l31))    
    py_send("*define thermexp_coeff_laminate_1 %f " % (alpha_l1))
    py_send("*define thermexp_coeff_laminate_2 %f " % (alpha_l2))
    py_send("*define thermexp_coeff_laminate_3 %f " % (alpha_l3))
    py_send("*define youngs_modulus_fibre_1 %f " % (young_f1))
    py_send("*define youngs_modulus_fibre_2 %f " % (young_f2))
    py_send("*define youngs_modulus_fibre_3 %f " % (young_f3))
    py_send("*define shear_modulus_fibre_12 %f " % (shear_f12))
    py_send("*define shear_modulus_fibre_23 %f " % (shear_f23))
    py_send("*define shear_modulus_fibre_31 %f " % (shear_f31))
    py_send("*define poissons_ratio_fibre_12 %f " % (nu_f12))
    py_send("*define poissons_ratio_fibre_23 %f " % (nu_f23))
    py_send("*define poissons_ratio_fibre_31 %f " % (nu_f31))
    py_send("*define thermexp_coeff_fibre_1 %f " % (alpha_f1))
    py_send("*define thermexp_coeff_fibre_2 %f " % (alpha_f2))
    py_send("*define thermexp_coeff_fibre_3 %f " % (alpha_f3))
    py_send("*define youngs_modulus_matrix %f " % (young_m))
    py_send("*define poissons_ratio_matrix %f " % (nu_m))
    py_send("*define thermexp_coeff_matrix %f " % (alpha_m))
    return


if __name__ == '__main__':
    py_connect("",40007)
    main()
    py_disconnect()
