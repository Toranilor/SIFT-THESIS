#results export
#puts results from an msc marc file into the correct location


from py_mentat import *
from py_post import *
import os
import os.path
import math

def main():
	#definitions to change
	cracktip = 8; #mm, crack tip ending height
	direction = ['X','Y','Z'] 

	for i in direction:
		#open results
		py_send("*post_open_default") 
		py_send("*post_skip_to_last")
	
		#node selection
		py_send("*select_method_box")
		py_send("*select_clear_nodes")
		py_send("*select_nodes")
		if i == 'Z':
			py_send("60.4 60.6")
			py_send("-0.1 0.01")
			py_send("0 %f" % (cracktip))
		elif i == 'Y':
			py_send("60.4 60.6")
			py_send("-0.1 2.5")
			py_send("%f %f" %(cracktip-1.1,cracktip-1))
		elif i == 'X':
			py_send("55.5 60.6")
			py_send("-0.1 0.01")
			py_send("%f %f" %(cracktip-1.1,cracktip-1))

		#report generation 
		reportrange = ["11","12","22","23","31","33"]
		homedir=os.getcwd()
		reportdir= homedir + '\Reports' + i
		if not os.path.exists(reportdir):
			os.makedirs(reportdir)
		
		py_send("*report_option node_values:on")
		py_send("*report_option node_data:off")
		py_send("*report_option selection:selected")
		py_send("*report_option sort_item:id")
		py_send("*report_option sort_order:ascending")
		py_send("*post_contour_bands")

		for i in reportrange:
			py_send("*report_file %s\%s.rpt" % (reportdir, i))
			py_send("*post_value Comp %s of Elastic Strain" %(i))
			py_send("*report_run")
	
		py_send("*post_rewind")
		py_send("*report_option node_data:on")
		py_send("*report_option node_values:off")
		py_send("*report_file %s\pos.rpt" % (reportdir))
		py_send("*report_run")
		
	return