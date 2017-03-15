
import dicom
import pandas as pd
import re
import fnmatch
import os

'''
Peter Goodin, Dec 2016
'''


#Get spreadsheet type from final 3 strings of main_sheet.
def sabr_subj_ss_check(subj_ss):
    subj_ss_type = subj_ss[-3:]

    if subj_ss_type == 'csv':
        try:
            try:
                subj_df = pd.read_csv(subj_ss, sep = ',', names = ['sub_name', 'sub_id'])
            except:
                subj_df = pd.read_csv(subj_ss, sep = '\t', names = ['sub_name', 'sub_id'])
        except:
            print '\nDelimiter not recoginised. Please ensure your spreadsheet uses either commas (,) or tabbed spaces to separate cells.\n'
            exit()

    elif subj_ss_type == 'xls':
        try:
            subj_df = pd.read_excel(subj_ss)
        except:
            print '\nUnable to read excel sheet. Please ensure data is formatted properly.\n'
            exit()

    else:
        print 'Spreadsheet type not recognised. Please use either comma or tabbed separated or excel formats.'
        exit()
    return subj_df
    

def sabr_scan_ss_check(scan_ss):
    
    scan_ss_type = scan_ss[-3:]

    if scan_ss_type == 'csv':
        try:
            try:
                scan_df = pd.read_csv(scan_ss, sep = ',', names = ['scan_match', 'scan_type', 'scan_filename'])
            except:
                scan_df = pd.read_csv(scan_ss, sep = '\t', names = ['scan_match', 'scan_type', 'scan_filename'])
        except:
            print '\nDelimiter not recoginised. Please ensure your spreadsheet uses either commas (,) or tabbed spaces to separate cells.\n'
            exit()

    elif scan_ss_type == 'xls':
        try:
            scan_df = pd.read_excel(scan_ss)
        except:
            print '\nUnable to read excel sheet. Please ensure data is formatted properly.\n'
            exit()

    else:
        print 'Spreadsheet type not recognised. Please use either comma or tabbed separated or excel formats.'
        exit()

    return scan_df



def sabr_deid(subj_df, scan_df, raw_dir, deid_outdir, sub_name):

    subj_info = subj_df[subj_df["sub_name"] == sub_name]

    #Join raw dir with subject name (assumes directory structure is ./rawdir/subj_name/...
    subj_main_dir = os.path.join(raw_dir, subj_info.sub_name[0])

    new_id = subj_info.sub_id[0]

    #Get list of sessions within main subj directory, make dir and loop over sessions.
    subj_sessions = os.walk(subj_main_dir).next()[1]
    subj_sessions.sort()

    #Create deidentified main (root) directory for subject
    subj_deid_main_dir = os.path.join(deid_outdir, new_id)        
    try:
        os.mkdir(subj_deid_main_dir)
    except:
        print '\nDirectory exists\n'
       
    for sn, session in enumerate(subj_sessions):
    #MAKE DIRECTORIES BUT ZERO PAD SESSION
        subj_deid_session_dir = os.path.join(subj_deid_main_dir, 'run-' '{:02d}'.format(sn+1))

        try: 
            os.mkdir(subj_deid_session_dir)
        except:
            print '\nSession folder exists\n'

        #Session folder for identifiable subject
        subj_session_dir = os.path.join(subj_main_dir, session)

        #Loop over scan folder types within scan dataframe (anat, epi etc) 
        for j, scan in enumerate(scan_df['scan_type']):
                
            #Match common sequence substring with path in os.walk
            for root, dr, files in os.walk(subj_session_dir):                
                match = scan_df.scan_match[j] 

                match_regex = fnmatch.translate(match)
                found = re.search(match_regex, root)

                
                #If match, start deid process, not not, move onto next folder.
                if found != None:
                    #print(j, match, root)
                    subj_deid_sequence_dir = os.path.join(subj_deid_session_dir, scan)
                    try:
                        os.mkdir(subj_deid_sequence_dir)
                        print('Making directory' + subj_deid_sequence_dir)
                    except:
                        print('\nSequence directory ' + scan + ' exists\n')
                        
                    #Create list of dicoms in sequence dir rather than use 
                    #files (more control in case any non-dicoms)
                    anon_files = os.listdir(root)
                    anon_files = [x for x in anon_files if 'nii' not in x] #Remove any previous nii files that may be present < To do - expand to other file types (mgh, analyze, etc)
                    anon_files.sort()
                
                    for anon_file in anon_files: 
                        #Read files in 1 at a time, remove the remove / alter the below tags.
                        dcm = dicom.read_file(os.path.join(root, anon_file), force = True) #Uses force = True incase dicoms haven't had identifier added to header                           
                            
                        #Strip aquisition date information
                        aqusition_date_list = [[0x0008,0x0020],[0x0008,0x0021],[0x0008,0x0022],[0x0008,0x0023]]
                            
                        for tag in aqusition_date_list:
                            try:
                                dcm[hex(tag[0]), hex(tag[1])].value = ''
                            except:
                                print ''
                                #print 'Tag %s %s does not exist in dicom. Moving to next tag' % (hex(tag[0]), hex(tag[1]))
                            
                    
                        #Strip aquisition time information
                        aqusition_time_list = [[0x0008,0x0030],[0x0008,0x0031],[0x0008,0x0032],[0x0008,0x0033]]
                            
                        for tag in aqusition_time_list:
                            try:
                                dcm[hex(tag[0]), hex(tag[1])].value = ''
                            except:
                                print ''
                                #print 'Tag %s %s does not exist in dicom. Moving to next tag' % (hex(tag[0]), hex(tag[1]))
                            
                    
                        #Strip physician information
                        physician_list = [[0x0008,0x0090],[0x0008,0x1050]]
                            
                        for tag in physician_list:
                            try:
                                dcm[hex(tag[0]), hex(tag[1])].value = ''
                            except:
                                print ''
                                #print 'Tag %s %s does not exist in dicom. Moving to next tag' % (hex(tag[0]), hex(tag[1]))
                            
                            
                            #Strip study description
                            #dcm[0x0008,0x1030].value = ''
                    
                            #Strip subject name / patient ID
                        subj_name_list = [[0x0010,0x0010],[0x0010,0x0020]]
                            #PatientName, PatientID
                            
                        for tag in subj_name_list:
                            try:
                                dcm[hex(tag[0]), hex(tag[1])].value = new_id
                            except:
                                print ''
                                #print 'Tag %s %s does not exist in dicom. Moving to next tag' % (hex(tag[0]), hex(tag[1]))
                            
                            
                            #Strip subject attributes
                        subj_attrib_list = [[0x0010,0x0030],[0x0010,0x1010],[0x0010,0x1020],[0x0010,0x1030]]
                        #, DoB, Age, PatientHeight, PatientWeight                
            
                        for tag in subj_attrib_list:
                            try:
                                dcm[hex(tag[0]), hex(tag[1])].value = ''
                            except:
                                print ''
                                #print 'Tag %s %s does not exist in dicom. Moving to next tag' % (hex(tag[0]), hex(tag[1]))
                            
                            
                        #Write anonymised file
                        dicom.write_file(os.path.join(subj_deid_sequence_dir, anon_file),dcm)
    return(subj_deid_main_dir)
