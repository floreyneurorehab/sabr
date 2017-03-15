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
            print('\n***dcm2niix installed. Continuing with conversion.***\n')
    except:
        print('\n***dcm2niix NOT installed. Please place executable in the /bin directory***\n')



def sabr_dcm2niix_convert(subj_deid_main_dir, subj_nii_outdir, new_id, scan_df):
    #First, check the de-id dicom directoy exists
    if os.path.isdir(subj_deid_main_dir) == 0:
        print('De-identified dicom directory does not exist. Please rerun.')
        exit()
        
    #Next, copy de-id folder structure to nii folder
    try:
        shutil.copytree(subj_deid_main_dir, subj_nii_outdir, ignore = shutil.ignore_patterns('*.nii', '*.nii.gz', '*.mgh')) #Ignore anything with a . in the name (not ideal).
    except:
        print('***\nWARNING! NII OUTPUT DIRECTORY ALREADY EXITS!\n***')
        

    runs = os.listdir(subj_nii_outdir)
    for run in runs:
        for scanNo, scantype in enumerate(scan_df['scan_type']):
            convert_path = os.path.join(subj_nii_outdir, run, scantype)
            try:
                dcm_files = os.listdir(convert_path)
            except:
                continue
            output_fn = 'sub-' + new_id + '_acq-' + scantype + '_' + run + '_' + scan_df['scan_filename'].iloc [scanNo]
            os.system('dcm2niix -b y -f ' + output_fn + ' ' + convert_path)
            
            #Clean up
            [os.remove(convert_path + '/' + dcm) for dcm in dcm_files]
   
    #Then walk the nii
    #for root, dr, files in os.walk(subj_nii_outdir):
        #if files:
            #print(root)
            #scan_dir = os.path.split(root)[1]
            #print(scan_dir)
            #os.system('dcm2niix -b y -f test%f ' + root) #Using os.system because for some reason subprocess.call refuses to work.
            #[os.remove(root + '/' + x) for x in files]
            
            

    
    



    




        
