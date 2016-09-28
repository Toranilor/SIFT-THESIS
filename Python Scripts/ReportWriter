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

	#node selection
	py_send("*select_method_box")
	py_send("*select_nodes")
	py_send("60.4 60.6")
	py_send("-0.1 0.01")
	py_send("0 %f" % (cracktip))
	
	#open results
	py_send("*post_open_default") 
	py_send("*post_skip_to_last")

	#report generation (TEST)
	reportrange = ["11","12","22","23","31","33"]
	homedir=os.getcwd()
	reportdir= homedir + '\Reports'
	if not os.path.exists(reportdir):
		os.makedirs(reportdir)
		
	py_send("*report_option node_vaues:on")
	py_send("*report_option selection:selected")
	py_send("*report_option sort_item:id")
	py_send("*report_option sort_order:ascending")
	py_send("*post_contour_bands")

	for i in reportrange:
		py_send("*report_file %s\%s.rpt" % (reportdir, i))
		py_send("*post_value Comp %s of Total Strain" %(i))
		py_send("*report_run")
	return