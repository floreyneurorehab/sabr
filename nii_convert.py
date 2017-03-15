import os
import shutil
from subprocess import check_call, call, STDOUT


'''
Peter Goodin, Dec 2016
'''

def sabr_dcm2niix_check():
    fnull = open(os.devnull, 'w')
    try:
        retcode = call('dcm2niix', stdout = fnull, stderr = STDOUT)
        if retcode == 0:
            print('\n***dcm2niix installed. Continuing with conversion.***\n')
    except:
        print('\n***dcm2niix NOT installed. Please place executable in the /bin directory***\n')
        exit()

def sabr_dcm2niix_convert():
    #First, check the de-id dicom directoy exists
    if os.path.isdir(deid_outdir) == 0:
        print('De-identified dicom directory does not exist. Please rerun.')
        exit()

    #Next, copy de-id folder structure to nii folder
    shutil.copytree(deid_outdir, nii_outdir, ignore = shutil.ignore_patterns('*.*')) #Ignore anything with a . in the name (not ideal).

    for root, dr, files in os.walk(deid_outdir):
        if files:
           filename = os.path.split(root)[1] + '.nii'
           newpath = root.replace(deid_outdir, nii_outdir)
           fn = os.path.join(newpath, filename)
           call('dcm2niix -b y -v n -o ' + fn + ' ' + root)
            

    
    



    




        
