#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Dec  1 10:14:50 2016

@author: peter
"""

#TO DO - ADD PARALLEL.

from de_id import sabr_subj_ss_check, sabr_scan_ss_check, sabr_deid
from nii_convert import sabr_dcm2niix_check, sabr_dcm2niix_convert
import multiprocessing
import sys
import os


#Folder information (to be added from browser interface)
h_dir = '/home/peter/Desktop/sabr_test/'

raw_dir = os.path.join(h_dir,'siemens')

deid_outdir = h_dir + 'de_id/'
nii_outdir = h_dir + 'nii/'

#Parameters
keep_deid = 'y' #Keep de-identified data

#Get available cores for parallel processing.
#NOTE! Parallel only works on 'Nix based machines. Windows defaults to 1 core.
#if sys.platform == 'win32':
#    n_cores = 1
#else:
#    n_cores = multiprocessing.cpu_count() - 1 #Keep a core for the OS.
#    print('Processing {} subjects in parallel.'.format(n_cores))
#    if n_cores < 1:
#        n_cores = 1
#        print('Number of cores not sufficent for parallel processing. Processing sequentially.')
    


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



#Below will need to be fiddled with to get parallel working. Damned afterthoughts.

#Loop through subjects in dataframe
for n in range(0, len(subj_df)):
    subj_info = subj_df.iloc[n]
    
    #Run de-id
    subj_deid_main_dir, subj_sessions, new_id = sabr_deid(subj_info, scan_df, raw_dir, deid_outdir)
    
    #Setup nii conversion directory
    subj_nii_outdir = os.path.join(nii_outdir, new_id)
    
    #Run conversion
    sabr_dcm2niix_convert(subj_deid_main_dir, subj_nii_outdir, new_id, scan_df, subj_sessions)
    
print('\nConversion complete.')



