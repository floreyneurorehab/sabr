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

    #Try csv file type (both comma and tab)
    if subj_ss_type == 'csv' or subj_ss_type == 'tsv':
        try:
            try:
                subj_df = pd.read_csv(subj_ss, sep = ',')
                if subj_df.columns[0] != 'subj_name':
                    raise Exception('\n***ERROR! NON STANDARD OR MISSING COLUMN NAMES!***\nPlease ensure columns are labelled sub_name and sub_id.\n')
                    return
            except:
                subj_df = pd.read_csv(subj_ss, sep = '\t')
                if subj_df.columns[0] != 'subj_name':
                    raise Exception('\n***ERROR! NON STANDARD OR MISSING COLUMN NAMES!***\nPlease ensure columns are labelled sub_name and sub_id.\n')
                    return
        except:
            raise Exception('\n***ERROR! UNABLE TO READ FILE!***\nPlease check your file path is correct or ensure your spreadsheet uses either commas (,) or tabbed spaces to separate cells.\n')
            return

    elif subj_ss_type == 'xls':
        try:
            subj_df = pd.read_excel(subj_ss)
            if subj_df.columns[0] != 'subj_name':
                raise Exception('\n***ERROR! NON STANDARD OR MISSING COLUMN NAMES!***\nPlease ensure columns are labelled sub_name and sub_id.***\n')
                return
        except:
            raise Exception('\n***ERROR! UNABLE TO READ FILE!***\nPlease check the file path is correct or ensure your spreadsheet is an .xlsx file.\n')
            return

    else:
        raise Exception('\n***ERROR! UNABLE TO READ SUBJECT INFORMATION!***\nPlease check the file path is correct or use either comma / tabbed separated or excel formats.***\n')
        return
    
    return(subj_df)
    

def sabr_scan_ss_check(scan_ss):
    scan_ss_type = scan_ss[-3:]

    if scan_ss_type == 'csv' or scan_ss_type == 'tsv':
        try:
            try:
                scan_df = pd.read_csv(scan_ss, sep = ',')
                if scan_df.columns[0] != 'scan_match':
                    raise Exception('\n***ERROR! NON STANDARD OR MISSING COLUMN NAMES!***\nPlease ensure columns are labelled scan_match, scan_type and scan_filename.')
                    return
            except:
                scan_df = pd.read_csv(scan_ss, sep = '\t')
                if scan_df.columns[0] != 'scan_match':
                    raise Exception('\n***ERROR! NON STANDARD OR MISSING COLUMN NAMES!***\nPlease ensure columns are labelled scan_match, scan_type and scan_filename.')
                    return
        except:
            raise Exception('\n***ERROR! UNABLE TO READ FILE!***\nPlease check your file path is correct or ensure your spreadsheet uses either commas (,) or tabbed spaces to separate cells.\n')
            return

    elif scan_ss_type == 'xls':
        try:
            scan_df = pd.read_excel(scan_ss)
            if scan_df.columns[0] != 'scan_match':
                raise Exception('\n***ERROR! NON STANDARD OR MISSING COLUMN NAMES!***\nPlease ensure columns are labelled scan_match, scan_type and scan_filename.')
                return
        except:
            raise Exception('\n***ERROR! UNABLE TO READ FILE!***\nPlease check the file path is correct or ensure your spreadsheet is an .xlsx file.\n')
            return

    else:
        raise Exception('\n***ERROR! UNABLE TO READ SUBJECT INFORMATION!***\nPlease use either comma / tabbed separated or excel formats.***\n')
        return

    return(scan_df)



def sabr_deid(subj_info, scan_df, raw_dir, deid_outdir):


    #Join raw dir with subject name (assumes directory structure is ./rawdir/subj_name/...
    subj_main_dir = os.path.join(raw_dir, subj_info['subj_name'])

    new_id = subj_info['subj_id']

    #Get list of sessions within main subj directory, make dir and loop over sessions.
    subj_sessions = os.walk(subj_main_dir).next()[1]
    subj_sessions.sort()
    
    print('\n***{} has {} session(s)'.format(new_id, len(subj_sessions)))

    #Create deidentified main (root) directory for subject
    subj_deid_main_dir = os.path.join(deid_outdir, new_id)        
    try:
        os.mkdir(subj_deid_main_dir)
    except:
        print('\nDirectory {} exists\n'.format(subj_deid_main_dir))
        
    
    #WARNING! LAZY CODING AHEAD!    
    if len(subj_sessions) == 0:
        raise Exception('\n***ERROR! NUMBER OF SESSIONS = 0!***\nPlease check directory structure of {}'.format(subj_info['subj_name']))
        
    elif len(subj_sessions) == 1:
        session = subj_sessions[0]
        subj_session_dir = os.path.join(subj_main_dir, session)
        subj_deid_session_dir = os.path.join(subj_deid_main_dir, 'ses-01')

        try: 
            os.mkdir(subj_deid_session_dir)
        except:
            print('\nSession folder {} exists\n'.format(subj_deid_session_dir))
        
        for j, scan_type in enumerate(scan_df['scan_type']):
            subj_deid_meta_dir = os.path.join(subj_deid_session_dir, scan_type)
            
            try:
                os.mkdir(subj_deid_meta_dir)
            except:
                print('Meta directory {} exists.'.format(scan_type))
                    
                
            #Match common sequence substring with path in os.walk
            for root, dr, files in os.walk(subj_session_dir):                
                match = scan_df.scan_match[j] 

                match_regex = fnmatch.translate(match)
                found = re.search(match_regex, root)  
                #print('\n***{}***\n'.format(found))
                
                #If match, start deid process. If not, move onto next folder.
                if found != None:
                    
                    subj_deid_sequence_dir = os.path.join(subj_deid_meta_dir, scan_df.scan_filename[j])
                    print('Making directory {}'.format(subj_deid_sequence_dir))
                    try:
                        os.mkdir(subj_deid_sequence_dir) #Make "housing" directory to keep dicoms of different sequences but same meta-category separate.
                    except:
                        print('\n***SEQUENCE DIRECTORY ALREADY EXISTS!***\nSkipping.')
                        continue
                        
                        
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
                                print('Tag {} {} does not exist in {}. Moving to next tag'.format(hex(tag[0]), hex(tag[1]),scan_df.scan_filename[j])) 
                            
                    
                        #Strip aquisition time information
                        aqusition_time_list = [[0x0008,0x0030],[0x0008,0x0031],[0x0008,0x0032],[0x0008,0x0033]]
                            
                        for tag in aqusition_time_list:
                            try:
                                dcm[hex(tag[0]), hex(tag[1])].value = ''
                            except:
                                print('Tag {} {} does not exist in {}. Moving to next tag'.format(hex(tag[0]), hex(tag[1]),scan_df.scan_filename[j])) 
                            
                    
                        #Strip physician information
                        physician_list = [[0x0008,0x0090],[0x0008,0x1050]]
                            
                        for tag in physician_list:
                            try:
                                dcm[hex(tag[0]), hex(tag[1])].value = ''
                            except:
                                print('Tag {} {} does not exist in {}. Moving to next tag'.format(hex(tag[0]), hex(tag[1]),scan_df.scan_filename[j])) 
                            
                            
                            #Strip study description
                            #dcm[0x0008,0x1030].value = ''
                    
                            #Strip subject name / patient ID
                        subj_name_list = [[0x0010,0x0010],[0x0010,0x0020]]
                            #PatientName, PatientID
                            
                        for tag in subj_name_list:
                            try:
                                dcm[hex(tag[0]), hex(tag[1])].value = new_id
                            except:
                                print('Tag {} {} does not exist in {}. Moving to next tag'.format(hex(tag[0]), hex(tag[1]),scan_df.scan_filename[j])) 
                            
                            
                            #Strip subject attributes
                        subj_attrib_list = [[0x0010,0x0030],[0x0010,0x1010],[0x0010,0x1020],[0x0010,0x1030]]
                        #, DoB, Age, PatientHeight, PatientWeight                
            
                        for tag in subj_attrib_list:
                            try:
                                dcm[hex(tag[0]), hex(tag[1])].value = ''
                            except:
                                print('Tag {} {} does not exist in {}. Moving to next tag'.format(hex(tag[0]), hex(tag[1]),scan_df.scan_filename[j])) 
                                   
                        #Write anonymised file
                        dicom.write_file(os.path.join(subj_deid_sequence_dir, anon_file),dcm)    
    
        
    elif len(subj_sessions) > 1:
        for sn, session in enumerate(subj_sessions):
        
            #MAKE DIRECTORIES BUT ZERO PAD SESSION
            subj_deid_session_dir = os.path.join(subj_deid_main_dir, 'ses-' '{:02d}'.format(sn+1))
    
            try: 
                os.mkdir(subj_deid_session_dir)
            except:
                print('\nSession folder {} exists\n'.format(subj_deid_session_dir))
    
            #Session folder for identifiable subject
            subj_session_dir = os.path.join(subj_main_dir, session)
    
            #Loop over scan folder types within scan dataframe (anat, task, etc) 
            for j, scan_type in enumerate(scan_df['scan_type']):
                subj_deid_meta_dir = os.path.join(subj_deid_session_dir, scan_type)
                try:
                    os.mkdir(subj_deid_meta_dir)
                except:
                    print('Meta directory {} exists.'.format(scan_type))
                        
                    
                #Match common sequence substring with path in os.walk
                for root, dr, files in os.walk(subj_session_dir):                
                    match = scan_df.scan_match[j] 
    
                    match_regex = fnmatch.translate(match)
                    found = re.search(match_regex, root)
    
                    
                    #If match, start deid process, not not, move onto next folder.
                    if found != None:
                        
                        subj_deid_sequence_dir = os.path.join(subj_deid_meta_dir, scan_df.scan_filename[j])
                        print('Making directory {}'.format(subj_deid_sequence_dir))
                        try:
                            os.mkdir(subj_deid_sequence_dir) #Make "housing" directory to keep dicoms of different sequences but same meta-category separate.
                        except:
                            print('\n***SEQUENCE DIRECTORY ALREADY EXISTS!***\nSkipping.')
                            continue
                            
                            
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
                                    print('Tag {} {} does not exist in {}. Moving to next tag'.format(hex(tag[0]), hex(tag[1]),scan_df.scan_filename[j])) 
                                
                        
                            #Strip aquisition time information
                            aqusition_time_list = [[0x0008,0x0030],[0x0008,0x0031],[0x0008,0x0032],[0x0008,0x0033]]
                                
                            for tag in aqusition_time_list:
                                try:
                                    dcm[hex(tag[0]), hex(tag[1])].value = ''
                                except:
                                    print('Tag {} {} does not exist in {}. Moving to next tag'.format(hex(tag[0]), hex(tag[1]),scan_df.scan_filename[j])) 
                                
                        
                            #Strip physician information
                            physician_list = [[0x0008,0x0090],[0x0008,0x1050]]
                                
                            for tag in physician_list:
                                try:
                                    dcm[hex(tag[0]), hex(tag[1])].value = ''
                                except:
                                    print('Tag {} {} does not exist in {}. Moving to next tag'.format(hex(tag[0]), hex(tag[1]),scan_df.scan_filename[j])) 
                                
                                
                                #Strip study description
                                #dcm[0x0008,0x1030].value = ''
                        
                                #Strip subject name / patient ID
                            subj_name_list = [[0x0010,0x0010],[0x0010,0x0020]]
                                #PatientName, PatientID
                                
                            for tag in subj_name_list:
                                try:
                                    dcm[hex(tag[0]), hex(tag[1])].value = new_id
                                except:
                                    print('Tag {} {} does not exist in {}. Moving to next tag'.format(hex(tag[0]), hex(tag[1]),scan_df.scan_filename[j])) 
                                
                                
                                #Strip subject attributes
                            subj_attrib_list = [[0x0010,0x0030],[0x0010,0x1010],[0x0010,0x1020],[0x0010,0x1030]]
                            #, DoB, Age, PatientHeight, PatientWeight                
                
                            for tag in subj_attrib_list:
                                try:
                                    dcm[hex(tag[0]), hex(tag[1])].value = ''
                                except:
                                    print('Tag {} {} does not exist in {}. Moving to next tag'.format(hex(tag[0]), hex(tag[1]),scan_df.scan_filename[j])) 
                                       
                            #Write anonymised file
                            dicom.write_file(os.path.join(subj_deid_sequence_dir, anon_file),dcm)
            
    return(subj_deid_main_dir, subj_sessions, new_id)
