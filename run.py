"""
Created on Thu Dec  1 10:14:50 2016

@author: peter goodin
"""

#TO DO - ADD PARALLEL.
import json
import joblib
import sys
import os


#Folder information (to be added from browser interface)
h_dir = os.getcwd()

#Change directory to h_dir to import (just in place during testing)
os.chdir(h_dir)
from de_id import sabr_participant_ss_check, sabr_scan_ss_check, sabr_deid
from nii_convert import sabr_dcm2niix_check, sabr_dcm2niix_convert
from misc import create_description


raw_dir = os.path.join(h_dir, 'raw')

deid_outdir = os.path.join(h_dir, 'connect_deid_dicoms')
nii_outdir = os.path.join(h_dir, 'connect_deid_nii')

#Parameters
keep_deid = 'y' #Keep de-identified data

#Location of participant and scan lists
participant_ss = os.path.join(h_dir, 'participant_list_short.csv')
scan_ss = os.path.join(h_dir, 'scan_list_short.csv')

#Check input sheets, convert to dataframe
participant_df = sabr_participant_ss_check(participant_ss)
participant_df['participant_name'] = participant_df['participant_name'].str.upper().apply(lambda x : ','.join(reversed(x.split(' ')))).replace(',' ,'_', regex=True) #Replace subj_names with upper, reverse order of names (was fn ln, now ln fn), remove whitespace.
# participant_df['participant_id'] = participant_df['participant_id'].apply(lambda x: 'sub-' + x).replace('-', '')

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
for n in range(0, len(participant_df)):
    subj_info = participant_df.iloc[n]

    #Run de-id
    subj_deid_main_dir, participant_sessions, participant_id = sabr_deid(subj_info, scan_df, raw_dir, deid_outdir)

    #Setup nii conversion directory
    subj_nii_outdir = os.path.join(nii_outdir, participant_id)

    #Run conversion
    sabr_dcm2niix_convert(subj_deid_main_dir, subj_nii_outdir, participant_id, scan_df, participant_sessions)


#Finish process by writing root level files (participants.tsv & dataset_description)

participant_df['participant_id'].apply(lambda x: 'sub-' + x).to_csv(os.path.join(nii_outdir, 'participants.tsv'), sep = '\t', header = True, index = False)
description_csv = 'description_list.csv'
create_description(description_csv, nii_outdir)





print('\nConversion complete.')
