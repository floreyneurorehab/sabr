import os
import shutil
import subprocess

'''
Peter Goodin, Dec 2016
'''

def sabr_dcm2niix_check():
    fnull = open(os.devnull, 'w')
    try:
        retcode = subprocess.call('dcm2niix', stdout = fnull, stderr = subprocess.STDOUT)
        if retcode == 0:
            print('\n***dcm2niix installed! Continuing with conversion.***\n')
    except:
        raise Exception('\n***ERROR! DCM2NIIX NOT PRESENT!***\nPlease place executable in the /bin directory\n')



def sabr_dcm2niix_convert(subj_deid_main_dir, subj_nii_outdir, new_id, scan_df, subj_sessions):
    #First, check the de-id dicom directoy exists
    if os.path.isdir(subj_deid_main_dir) == 0:
        raise Exception('\n***ERROR! DE-IDENTIFIED DICOM DIRECTORY DOES NOT EXIST!***\nPlease rerun SABR.')
        
    #Next, copy de-id folder structure to nii folder
    try:
        shutil.copytree(subj_deid_main_dir, subj_nii_outdir, ignore = shutil.ignore_patterns('*.nii', '*.nii.gz', '*.mgh')) #Ignore anything with extensions .nii(.gz), .mgh, etc. ADD YOUR OWN IF NEEDED!
    except:
        print('***\nWARNING! NII OUTPUT DIRECTORY ALREADY EXISTS!***\nOverwriting.')
            
    if len(subj_sessions) == 1:
        for scanNo, scan_type in enumerate(scan_df['scan_type']):
            nii_out_path = os.path.join(subj_nii_outdir, scan_type, '')
            convert_path = os.path.join(subj_nii_outdir, scan_type, scan_df['scan_filename'].iloc[scanNo], '')
            output_fn = 'sub-' + new_id + '_acq-' + scan_type + '_' + scan_df['scan_filename'].iloc[scanNo]
            print('\n{}\n'.format(convert_path))
            print('{}\n'.format(output_fn))
            os.system('dcm2niix -b y -f ' + output_fn + ' -o ' + nii_out_path + ' '  + convert_path)
            
          #Remove dicom directory
            try:
                shutil.rmtree(convert_path)
            except:
                print('\n***WARNING! {} not present for {}***\nMoving to next sequence.'.format(new_id, scan_df['scan_filename'].iloc[scanNo]))
                
    elif len(subj_sessions) > 1:
        sessions = os.listdir(subj_nii_outdir) #Get directory names of sessions
        for sess in sessions:
            for scanNo, scan_type in enumerate(scan_df['scan_type']):
                nii_out_path = os.path.join(subj_nii_outdir, sess, scan_type, '')
                convert_path = os.path.join(subj_nii_outdir, sess, scan_type, scan_df['scan_filename'].iloc[scanNo], '')
                print('\n{}\n'.format(convert_path))
                output_fn = 'sub-' + new_id + '_acq-' + scan_type + '_' + scan_df['scan_filename'].iloc[scanNo]
                os.system('dcm2niix -b y -f ' + output_fn + ' -o ' + nii_out_path + ' '  + convert_path)
            
                #Remove dicom directory
                try:
                    shutil.rmtree(convert_path)
                except:
                    print('\n***WARNING! {} not present for {}***\nMoving to next sequence.'.format(new_id, scan_df['scan_filename'].iloc[scanNo]))
                
    else:
        raise Exception('\n***ERROR! UNABLE TO FIND DE-IDENTIFIED DICOMS!***\nPlease re-run SABR\n')
