#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Dec  1 10:14:50 2016

@author: peter
"""

from de_id import sabr_subj_ss_check, sabr_scan_ss_check, sabr_deid
from nii_convert import sabr_dcm2niix_check, sabr_dcm2niix_convert
import os


#Folder information (to be added from browser interface)
h_dir = '/home/peter/Desktop/deid_script/'

raw_dir = '/home/peter/Desktop/deid_script/siemens'

deid_outdir = h_dir + 'de_id/'
nii_outdir = h_dir + 'nii/'

#Option to keep de-id' dicoms
keep_deid = 'y'

#Location of subject and scan lists
subj_ss = h_dir + 'sub_list.csv'
scan_ss = h_dir + 'scan_list.csv'

#Check input sheets, convert to dataframe
subj_df = sabr_subj_ss_check(subj_ss)
scan_df = sabr_scan_ss_check(scan_ss)

#Check dcm2niix is installed
sabr_dcm2niix_check()

#Make directory to store deidentified data
try:
    os.mkdir(deid_outdir)
except:
    print('\n***De-identified folder exists. Not creating new folder.***\n')

#Run de-id
#Loop through subjects in dataframe
for n in range(0, len(subj_df)):
    sub_name = subj_df.sub_name[n]
    subj_deid_main_dir = sabr_deid(subj_df, scan_df, raw_dir, deid_outdir, sub_name)
    

    #Run conversion
    new_id = os.path.split(subj_deid_main_dir)[1]
    #print('The new ID is {}'.format(new_id))
    subj_nii_outdir = os.path.join(nii_outdir, new_id)
    sabr_dcm2niix_convert(subj_deid_main_dir, subj_nii_outdir, new_id, scan_df)
    
print('\nConversion complete.')



