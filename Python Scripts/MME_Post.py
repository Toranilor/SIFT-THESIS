# 
#    Name:
#    MME Post
#
#    Purpose:
#   Extract the MME results and publish them to a file
#
#     Usage:
#   Python -> Run
#
#     Dependencies:
#    Uses PyMentat functions:
#        py_send
#       py_prompt
#       py_get_xxx
#    Pythons modules:
#        math module
#        os module
#    Must be run after:
#        MME_Parameters_xxx.py
#       MME_Build_Solve.py
#

from py_mentat import *
from py_post import *
import os
import os.path
import math

# main function
def main():
    py_echo(0)
    # getting the required parameters
    vf = py_get_float("volume_fraction")
    mat_name = py_get_string("material_name")
    alpha_f2 = py_get_float("thermexp_coeff_fibre_2")
    
    # get (and set) directory structure
    homedir=os.getcwd()
    modeldir= homedir + '\Models' #This should already exist from MME_Build_Solve
    MMEdir = homedir + '\MME'
	if not os.path.exists(MMEdir): #Creates MME directory if it does not already exist
		os.makedirs(MMEdir)
        
    # define constants
    nArrange = 2
    nLocation = 7
    nMacro = 7
    nMicro = 6
    disp = 1.e-6
    dt = -1.e0
    e = 1.e-3
    pi = math.pi
    root2=math.sqrt(2.0)
    root3=math.sqrt(3.0)
    cos45=math.cos(pi/4)
    sin45=math.sin(pi/4)
    cos30=math.cos(pi/6)
    sin30=math.sin(pi/6)
    cos15=math.cos(pi/12)
    sin15=math.sin(pi/12)
    job_list = ["normalX","normalY","normalZ","shearXY","shearYZ","shearZX","thermal"]
    tensor = ["11","22","33","12","23","31"]
    location_ID = ["Inter-Fibre","Inter-Stitial","Inter-Fibre Interface","Inter-Stitial Interface","Fibre Centre","Fibre Inter-Fibre Interface","Fibre Inter-Stitial Interface"]
    arrange_ID = ["square","hex"]
    
    # set-up storage array
    MME = [[[[0 for iLocation in range(nLocation)] for iMicro in range(nMacro)] for iMacro in range(nMacro)] for iArrange in range(nArrange)]
    
    #*************************************#
    # getting the values from the model
    #*************************************#
    os.chdir(modeldir)
    for iArrange in range(nArrange):
        arrangement_name = arrange_ID[iArrange]
        
        # opening the sift model
        modelname='MME_%s_%.2f_%s' % (mat_name,vf,arrangement_name)
        py_send("*open_model %s.mud" % (modelname))

        # error handling
        ierror=0
        vf_min=0.1
        vf_max=0.7
        if(iArrange==1):
            vf_max=0.8
        if (vf < vf_min) or (vf > vf_max):
            str = 'Error: Invalid volume fraction \n'
            str = str + '   Please set the \"volume_fraction\" parameter'
            str = str + 'Example: *define volume_fraction 0.6'
            py_prompt(str)
            ierror=4

        if (ierror>0):
            return

        # Constants
        if(iArrange==0):                                 # square arrangement
            r=math.sqrt(vf/pi)
            angle_r=pi/4.0
            angle_d=45
            w=1.0
            h=1.0
        elif(iArrange==1):                               # hex arrangement
            r=math.sqrt((root3/2.0)*(vf/pi))
            angle_r=pi/6.0
            angle_d=30
            w=1.0
            h=root3
        else:
            return

        x_if=w/2+e; y_if=w/2-e; z_if=e;
        x_is=w/2+e; y_is=w/2-e; z_is=w*math.tan(angle_r)/2-e/2;
        x_ifi=w/2+e; y_ifi=r+e; z_ifi=e;
        x_isi=w/2+e; y_isi=r*math.cos(angle_r)+e; z_isi=r*math.sin(angle_r)+e/2;
        x_fc=w/2+e; y_fc=e; z_fc=e/2;
        x_fifi=w/2+e; y_fifi=r-e; z_fifi=e;
        x_fisi=w/2+e; y_fisi=r*math.cos(angle_r)-e/2; z_fisi=r*math.sin(angle_r)-e;

        for iMacro in range(nMacro):
            print ''
            job_name = job_list[iMacro]
            postname = modelname + "_" + job_name + ".t19"
            print 'Opening ' + postname

            try :
                py_send("*post_open %s" % (postname))
            except:
                print 'post file could not be opened'
                return

            try :
                py_send("*post_skip_to_last")
            except:
                print 'could not read increments data'
                return
            
            py_send("*post_contour_bands")
            py_send("*post_extrap_linear")
            py_send("*post_nodal_averaging off")
            
            for iMicro in range(nMicro):
                py_send("*post_value Comp %s of Elastic Strain" % tensor[iMicro])
                if (job_name <> "thermal"):
                    MME[iArrange][iMacro][iMicro][0] = py_get_float("scalar_pos(%f,%f,%f)" % (x_if,y_if,z_if))/disp
                    MME[iArrange][iMacro][iMicro][1] = py_get_float("scalar_pos(%f,%f,%f)" % (x_is,y_is,z_is))/disp
                    MME[iArrange][iMacro][iMicro][2] = py_get_float("scalar_pos(%f,%f,%f)" % (x_ifi,y_ifi,z_ifi))/disp
                    MME[iArrange][iMacro][iMicro][3] = py_get_float("scalar_pos(%f,%f,%f)" % (x_isi,y_isi,z_isi))/disp
                    MME[iArrange][iMacro][iMicro][4] = py_get_float("scalar_pos(%f,%f,%f)" % (x_fc,y_fc,z_fc))/disp
                    MME[iArrange][iMacro][iMicro][5] = py_get_float("scalar_pos(%f,%f,%f)" % (x_fifi,y_fifi,z_fifi))/disp
                    MME[iArrange][iMacro][iMicro][6] = py_get_float("scalar_pos(%f,%f,%f)" % (x_fisi,y_fisi,z_fisi))/disp
                else:
                    MME[iArrange][iMacro][iMicro][0] = round(py_get_float("scalar_pos(%f,%f,%f)" % (x_if,y_if,z_if)),7)
                    MME[iArrange][iMacro][iMicro][1] = round(py_get_float("scalar_pos(%f,%f,%f)" % (x_is,y_is,z_is)),7)
                    MME[iArrange][iMacro][iMicro][2] = round(py_get_float("scalar_pos(%f,%f,%f)" % (x_ifi,y_ifi,z_ifi)),7)
                    MME[iArrange][iMacro][iMicro][3] = round(py_get_float("scalar_pos(%f,%f,%f)" % (x_isi,y_isi,z_isi)),7)
                    MME[iArrange][iMacro][iMicro][4] = round(py_get_float("scalar_pos(%f,%f,%f)" % (x_fc,y_fc,z_fc)),7)
                    MME[iArrange][iMacro][iMicro][5] = round(py_get_float("scalar_pos(%f,%f,%f)" % (x_fifi,y_fifi,z_fifi)),7)
                    MME[iArrange][iMacro][iMicro][6] = round(py_get_float("scalar_pos(%f,%f,%f)" % (x_fisi,y_fisi,z_fisi)),7)
            py_send("*post_close")

    #*************************************#
    # writing output files
    #*************************************#
    # open data file(s) for writing
    os.chdir(MMEdir)
    fortfile = open('MME_%s_%.2f.inc' % (mat_name,vf),'w')
    csvfile = open('MME_%s_%.2f.csv' % (mat_name,vf),'w')
    
    # FORTRAN .inc file
    print 'Starting FORTRAN write'
    for iArrange in range(nArrange):
        arrangement_name = arrange_ID[iArrange]
		fortfile.write('integer :: iMicro')
        for iLocation in range(nLocation):
            fortfile.write("!\n")
            fortfile.write("!%s %s\n" % (location_ID[iLocation],arrangement_name))
            fortfile.write("!\n")
            for iMacro in range(nMacro):
                fortfile.write("\tdata(SAF(iMicro,%i,%i,%i),iMicro=1,6)/" % (iMacro+1,iLocation+1,iArrange+1))
                for iMicro in range(nMicro):
                    if (iMacro <> (nMacro-1)):
                        if (abs(MME[iArrange][iMacro][iMicro][iLocation]) >= e):
                            fortfile.write("%.3f" % (MME[iArrange][iMacro][iMicro][iLocation]))
                        else:
                            fortfile.write("0.0")
                    else:
                        if (abs(MME[iArrange][iMacro][iMicro][iLocation]) >= e/1000):
                            fortfile.write("%.3e" % (MME[iArrange][iMacro][iMicro][iLocation]))
                        else:
                            fortfile.write("0.0")
                    if (iMicro <> (nMicro-1)):
                        fortfile.write(", ")
                fortfile.write("/\n")
            fortfile.write("\n")
    
    # .csv file for MATLAB
    print 'Starting CSV write'
    for iMicro in range(nMicro):
        for iArrange in range(nArrange):
            for iLocation in range(nLocation):
                for iMacro in range(nMacro):
                    if (iMacro <> (nMacro-1)):
                        if (abs(MME[iArrange][iMacro][iMicro][iLocation]) >= e):
                            csvfile.write("%.3f" % (MME[iArrange][iMacro][iMicro][iLocation]))
                        else:
                            csvfile.write("0.0")
                    else:
                        if (abs(MME[iArrange][iMacro][iMicro][iLocation]) >= e/1000):
                            csvfile.write("%.3e" % (MME[iArrange][iMacro][iMicro][iLocation]))
                        else:
                            csvfile.write("0.0")
                    csvfile.write(",")
        csvfile.seek(-1,1)
        csvfile.truncate()
        csvfile.write("\n")
    
    # tidy
    fortfile.close
    csvfile.close
    os.chdir(homedir)
    return

if __name__ == '__main__':
    py_connect("",40007)
    main()
    py_disconnect()
