import dicom
import pandas as pd
import os

'''
Peter Goodin, Dec 2016
'''


#Get spreadsheet type from final 3 strings of main_sheet.
def sabr_subj_ss_check(subj_sheet):
    subj_ss_type = subj_ss[-3:]

    if subj_ss_type == 'csv':
        try:
            try:
                subj_id_df = pd.read_csv(subj_ss, sep = ',', names = ['sub_name', 'sub_id'])
            except:
                subj_id_df = pd.read_csv(subj_ss, sep = '\t', names = ['sub_name', 'sub_id'])
        except:
            print '\nDelimiter not recoginised. Please ensure your spreadsheet uses either commas (,) or tabbed spaces to separate cells.\n'
            exit()

    elif subj_ss_type == 'xls':
        try:
            subj_id_df = pd.read_excel(subj_ss)
        except:
            print '\nUnable to read excel sheet. Please ensure data is formatted properly.\n'
            exit()

    else:
        print 'Spreadsheet type not recognised. Please use either comma or tabbed separated or excel formats.'
        exit()
    return subj_id_df
    

def sabr_scan_ss_check(scan_ss):
    
    scan_ss_type = scan_ss[-3:]

    if scan_ss_type == 'csv':
        try:
            try:
                scan_path_df = pd.read_csv(scan_ss, sep = ',', names = ['scan_path', 'scan_type'])
            except:
                scan_path_df = pd.read_csv(scan_ss, sep = '\t', names = ['scan_path', 'scan_type'])
        except:
            print '\nDelimiter not recoginised. Please ensure your spreadsheet uses either commas (,) or tabbed spaces to separate cells.\n'
            exit()

    elif scan_ss_type == 'xls':
        try:
            scan_path_df = pd.read_excel(scan_ss)
        except:
            print '\nUnable to read excel sheet. Please ensure data is formatted properly.\n'
            exit()

    else:
        print 'Spreadsheet type not recognised. Please use either comma or tabbed separated or excel formats.'
        exit()

    return scan_path_df





def sabr_deid(subj_id_df, scan_path_df):

try:
    os.mkdir(deid_outdir)
except:
    print('\n***De-identified folder exists. Not creating new folder.***\n')


#Loop through subjects in list
    for n in range(0, len(subj_id_df)):
        #Get subject ID from dataframe
        new_id = subj_id_df.sub_id[n]
        
        #Create deidentified main (root) directory
        deid_main_folder = os.path.join(deid_outdir, new_id)
        try:
            os.mkdir(deid_main_folder)
        except:
            print '\nFolder exists\n'
       
        #Join raw dir with subject name (assumes directory structure is ./rawdir/subj_name/...
        subj_main_folder = os.path.join(rawdir, subj_id_df.sub_name[n])

        #Get list of sessions within main subj directory, make dir and loop over sessions.
        subj_sessions = os.walk(subj_main_folder).next()[1]

        for sn, session in enumerate(subj_sessions):
        #MAKE DIRECTORIES BUT ZERO PAD SESSION
            deid_session_folder = os.path.join(deid_main_folder, 'session_' '{:03d}'.format(sn+1))

            try: 
                os.mkdir(deid_session_folder)
            except:
                print '\nSession folder exists\n'

            #Session folder for identifiable subject
            subj_session_folder = os.path.join(subj_main_folder, session)

            #Loop over scan folder types within scan dataframe (anat, epi etc) 
            for j in range(0,len(scan_path_df)):
                
                #Match common sequence substring with path in os.walk
                for root, dr, files in os.walk(subj_session_folder):
                    match = scan_path_df.scan_path[j]
                
                    #If match, start deid process, not not, move onto next folder.
                    if match in root:
                        deid_sequence_folder = os.path.join(deid_session_folder, scan_path_df.scan_type[j])
                        try:
                            os.mkdir(deid_sequence_folder)
                            print('Making directory' + deid_sequence_folder)
                        except:
                            print('\nSequence folder exists\n')
                        
                        #Create list of dicoms in sequence dir rather than use 
                        #files (more control in case any non-dicoms)
                        anon_files = os.listdir(root)
                        anon_files = [x for x in anon_files if 'nii' not in x] #Remove any previous nii files that may be present < To do - expand to other file types (mgh, analyze, etc)
                        anon_files.sort()
                
                        for anon_file in anon_files: 
                            #Read files in 1 at a time, remove the remove / alter the below tags.
                            dcm = dicom.read_file(os.path.join(root, anon_file), force = True) #Uses force = True incase dicoms haven't had identifier added to header
                            
                            #dcm.remove_private_tags()
                            
                            #Strip aquisition date information
                            aqusition_date_list = [[0x0008,0x0020],[0x0008,0x0021],[0x0008,0x0022],[0x0008,0x0023]]
                            
                            for tag in aqusition_date_list:
                                try:
                                    dcm[hex(tag[0]), hex(tag[1])].value = ''
                                except:
                                    print ''
                                #   print 'Tag %s %s does not exist in dicom. Moving to next tag' % (hex(tag[0]), hex(tag[1]))
                            
                    
                            #Strip aquisition time information
                            aqusition_time_list = [[0x0008,0x0030],[0x0008,0x0031],[0x0008,0x0032],[0x0008,0x0033]]
                            
                            for tag in aqusition_time_list:
                                try:
                                    dcm[hex(tag[0]), hex(tag[1])].value = ''
                                except:
                                    print ''
                                #    print 'Tag %s %s does not exist in dicom. Moving to next tag' % (hex(tag[0]), hex(tag[1]))
                            
                    
                            #Strip physician information
                            physician_list = [[0x0008,0x0090],[0x0008,0x1050]]
                            
                            for tag in physician_list:
                                try:
                                    dcm[hex(tag[0]), hex(tag[1])].value = ''
                                except:
                                    print ''
                                #    print 'Tag %s %s does not exist in dicom. Moving to next tag' % (hex(tag[0]), hex(tag[1]))
                            
                            
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
                                #    print 'Tag %s %s does not exist in dicom. Moving to next tag' % (hex(tag[0]), hex(tag[1]))
                            
                            
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
                            dicom.write_file(os.path.join(deid_sequence_folder, anon_file),dcm)
