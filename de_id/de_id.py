import dicom
import pandas as pd
import os

#Get spreadsheet type from final 3 strings of main_sheet.

hdir = '/home/peter/Desktop/deid_script/'
subj_ss = '/home/peter/Desktop/deid_script/sub_list.csv'
scan_ss = '/home/peter/Desktop/deid_script/scan_list.csv'

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

    elif subj_ss_type == 'xls':
        try:
            subj_id_df = pd.read_excel(subj_ss)
        except:
            print '\nUnable to read excel sheet. Please ensure data is formatted properly.\n'

    else:
        print 'Spreadsheet type not recognised. Please use either comma or tabbed separated or excel formats.'
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

    elif scan_ss_type == 'xls':
        try:
            scan_path_df = pd.read_excel(scan_ss)
        except:
            print '\nUnable to read excel sheet. Please ensure data is formatted properly.\n'

    else:
        print 'Spreadsheet type not recognised. Please use either comma or tabbed separated or excel formats.'
    return scan_path_df



def sabr_deid(subj_id_df, scan_path_df):
#Loop through subjects in list
    for n in range(0, len(subj_id_df)):
        new_id = subj_id_df.sub_id[n]
        
        sub_folder = '/home/peter/Desktop/deid_script/%s' %(new_id,)
        try:
            os.mkdir(sub_folder)
        except:
            print '\nFolder exists\n'
    
        
        for j in range(0,len(scan_path_df)):
            #Place folder loop here
            scan_folder = scan_path_df.scan_path[j]
            out_folder = os.path.join(sub_folder,scan_path_df.scan_type[j])
            
            
            try:
                os.mkdir(out_folder)
            except:
                print 'Folder exists.'    
        
            print 'Anonomysing subject %s' % (new_id,)
            print scan_path_df.scan_type[j]
            anon_files = os.listdir(scan_folder)
            anon_files = [x for x in anon_files if 'nii' not in x] #Remove any previous nii files that may be present
            anon_files.sort()
            
            for anon_file in anon_files: 
        
                #Read files in 1 at a time, remove the remove / alter the below tags.
                dcm = dicom.read_file(os.path.join(scan_folder, anon_file), force = True) #Uses force = True incase dicoms haven't had identifier added to header
                
                #dcm.remove_private_tags()
                
                #Strip aquisition date information
                aqusition_date_list = [[0x0008,0x0020],[0x0008,0x0021],[0x0008,0x0022],[0x0008,0x0023]]
                
                for tag in aqusition_date_list:
                    try:
                        dcm[hex(tag[0]), hex(tag[1])].value = ''
                    except:
                        print 'Tag %s %s does not exist in dicom. Moving to next tag' % (hex(tag[0]), hex(tag[1]))
                
        
                #Strip aquisition time information
                aqusition_time_list = [[0x0008,0x0030],[0x0008,0x0031],[0x0008,0x0032],[0x0008,0x0033]]
                
                for tag in aqusition_time_list:
                    try:
                        dcm[hex(tag[0]), hex(tag[1])].value = ''
                    except:
                         print 'Tag %s %s does not exist in dicom. Moving to next tag' % (hex(tag[0]), hex(tag[1]))
                
        
                #Strip physician information
                physician_list = [[0x0008,0x0090],[0x0008,0x1050]]
                
                for tag in physician_list:
                    try:
                        dcm[hex(tag[0]), hex(tag[1])].value = ''
                    except:
                        print 'Tag %s %s does not exist in dicom. Moving to next tag' % (hex(tag[0]), hex(tag[1]))
                
                
                #Strip study description
                dcm[0x0008,0x1030].value = ''
        
                #Strip subject name / patient ID
                subj_name_list = [[0x0010,0x0010],[0x0010,0x0020]]
                #PatientName, PatientID
                
                for tag in subj_name_list:
                    try:
                        dcm[hex(tag[0]), hex(tag[1])].value = new_id
                    except:
                        print 'Tag %s %s does not exist in dicom. Moving to next tag' % (hex(tag[0]), hex(tag[1]))
                
                
                #Strip subject attributes
                subj_attrib_list = [[0x0010,0x0030],[0x0010,0x1010],[0x0010,0x1020],[0x0010,0x1030]]
                #, DoB, Age, PatientHeight, PatientWeight                

                for tag in subj_attrib_list:
                    try:
                        dcm[hex(tag[0]), hex(tag[1])].value = ''
                    except:
                        print 'Tag %s %s does not exist in dicom. Moving to next tag' % (hex(tag[0]), hex(tag[1]))
                
                
                #Write anonymised file
                dicom.write_file(os.path.join(out_folder, anon_file),dcm)

