# -*- coding: utf-8 -*-
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %                                                         PyXMake - Build environment for PyXMake                                                          %
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
"""
Jenkins2 post-processing script.
 
@note: Post-processing build jobs on Jenkins2 using PyXMake. 

@version:  1.0    
----------------------------------------------------------------------------------------------
@requires:
       - PyXMake, PyCODAC 

@change: 
       -    
   
@author: 
        - garb_ma                                              [DLR-FA,STM Braunschweig]
----------------------------------------------------------------------------------------------
"""

## @package PyXMake.VTL.stm_post
# Post-processing build jobs on Jenkins2 using PyXMake. 
## @author 
# Marc Garbade
## @date
# 03.04.2021
## @par Notes/Changes
# - Added documentation // mg 03.04.2021

import os, sys

try:
    import PyXMake as _ #@UnusedImport
except ImportError:
    # Script is executed as a plug-in
    sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    if "PyCODAC" in os.path.abspath(__file__): sys.path.insert(0,os.path.join(str(os.path.abspath(__file__)).split("PyCODAC")[0],"PyCODAC","Plugin"))
finally:
    from PyXMake.Tools import Utility  #@UnresolvedImport

def main():
    """
    Main function to execute the script. 
    """
    # Start
    print("==================================")    
    print("Attempting to kill unattended processes...")
    print("==================================")    
    
    Utility.ProcessWalk(os.getenv('stm_process',''))
    
    # Finish
    print("==================================")    
    print("Finished")
    print("==================================")    

if __name__ == "__main__":
    main(); sys.exit(0)
