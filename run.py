#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Dec  1 10:14:50 2016

@author: peter
"""

from de_id import sabr_subj_ss_check, sabr_scan_ss_check, sabr_deid
from nii_convert import sabr_dcm2niix_check
import os


#Folder information (to be added from browser interface)
h_dir = '/home/peter/Desktop/deid_script/'

raw_dir = '/home/peter/Desktop/deid_script/siemens'

deid_outdir = h_dir + 'de_id/'
nii_outdir = h_dir + 'nii/'


#Option to keep de-id' dicoms
keep_deid = 'y'

#Location of subject and scan lists
subj_ss = raw_dir + 'sub_list.csv'
scan_ss = raw_dir + 'scan_list.csv'

#Check input sheets
subj_sheet = sabr_subj_ss_check(subj_ss)
scan_sheet = sabr_scan_ss_check(scan_ss)

#Run de-id
sabr_deid(subj_sheet, scan_sheet)

#Check dcm2niix install
sabr_dcm2niix_check()

#Run conversion
sabr_dcm2niix_convert()



