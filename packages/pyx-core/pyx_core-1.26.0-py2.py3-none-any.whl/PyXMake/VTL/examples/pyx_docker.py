# -*- coding: utf-8 -*-
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %                                                         PyXMake - Build environment for PyXMake                                                         %
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
"""
Minimum working example for PyXMake. 

@note: Install Docker on any machine.
Created on 29.10.2021   

@version:  1.0    
----------------------------------------------------------------------------------------------
@requires:
       - PyXMake

@change: 
       - 
   
@author: garb_ma                                      [DLR-FA,STM Braunschweig]
----------------------------------------------------------------------------------------------
"""
import os, sys
import argparse
import subprocess

try:
    import PyXMake as _ #@UnusedImport
except ImportError:
    # Script is executed as a plug-in
    __package = "PyCODAC"
    sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    if __package in os.path.abspath(__file__): sys.path.insert(0,os.path.join(str(os.path.abspath(__file__)).split(__package)[0],__package,"Plugin"))
finally:
    from PyXMake.Tools import Utility  #@UnresolvedImport

def main(directory=False, feature=False):
    """
    Main function to execute the script.
    Installs Docker on the current machine (Windows)
    """
    delimn = "="
    if Utility.GetPlatform() in ["windows"]:
        if not directory or not os.path.exists(directory): raise FileNotFoundError
        if not feature or not feature in ["linux","windows","all"]: raise IOError
        # Parse all installation arguments to install script (Powershell)
        subprocess.check_call([Utility.GetExecutable("powershell", get_path=True)[-1],
                               os.path.join(Utility.GetPyXMakePath(),"Build","config","stm_docker.ps1"),
                               directory,delimn.join(["--package",feature])])
    else:
        import wget
        # Download install script
        wget.download("https://get.docker.com", 'get-docker.sh')
        # Install Docker in its default location.
        subprocess.check_call(["sudo","sh","get-docker.sh","&&","rm","-rf","get-docker.sh"])
        raise NotImplementedError
    pass

if __name__ == "__main__":
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # %                                                                         Access command line inputs                                                                  %
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    parser = argparse.ArgumentParser(description="Set up Docker in WSL2 on the current machine. Requires administrator privileges if Windows containers are desired.")
    parser.add_argument("--directory", metavar="directory", nargs=1, help="Installation directory (absolute path). Defaults to user workspace.")
    parser.add_argument("--feature", metavar="feature", nargs=1, help="Name of the package to install. Defaults to all.")
     
    try:
        _ = sys.argv[1]
        args, _ = parser.parse_known_args()  
        # Extract command line option to identify the requested make operation
        try: directory = args.directory[0]
        except: directory = os.path.expanduser("~")
        # Optional non-default package request
        try: feature = args.feature[0]
        except: feature = "linux"
    except:
        # This is the default build option
        directory = os.path.expanduser("~");  
        feature = "linux" ; 
    finally:
        # Run install script
        main(directory, feature)
        # Finish
        print("==================================")    
        print("Finished")
        print("==================================")    
        sys.exit()