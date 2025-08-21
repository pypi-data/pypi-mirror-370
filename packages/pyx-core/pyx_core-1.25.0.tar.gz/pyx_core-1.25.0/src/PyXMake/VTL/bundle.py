# -*- coding: utf-8 -*-
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %                                                         PyXMake - Build environment for PyXMake                                                         %
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
"""
Triple-use minimum working example for PyXMake. This script can be
executed in three different ways in varying levels of accessibility
 
@note: Create an installer from an application folder using NSIS
Created on 11.05.2020    

@version:  1.0    
----------------------------------------------------------------------------------------------
@requires:
       - PyXMake

@change: 
       - Requires PyCODAC in PYTHONPATH.
   
@author: garb_ma                                      [DLR-FA,STM Braunschweig]
----------------------------------------------------------------------------------------------
"""
import os, sys

try:
    import PyXMake as _ #@UnusedImport
except ImportError:
    # Script is executed as a plug-in
    sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
finally:
    from PyXMake.Build.Make import NSIS  #@UnresolvedImport
    from PyXMake import VTL #@UnresolvedImport

try:
    # Import PyCODAC to build library locally during setup.
    import PyCODAC
    __pyc_src_path = PyCODAC.PyCODACPath
except ImportError:
    # This script is not executed as plug-in for PyCODAC
    __pyc_src_path = ""
    pass

def main(
    BuildID, 
    # Add whole source folder into the bundle
    files="*.*",
    # Resource path
    source=os.path.join(__pyc_src_path,"Plugin","JupyterLab","src",".dist","pycodac"),
    # Define output path
    output=os.path.join(__pyc_src_path,"Plugin","JupyterLab","src",".dist"),
    # Encryption, mode, verbose and scratch directory
    scratch=VTL.Scratch, verbosity=2,
    # Additional keyword arguments
    **kwargs):
    """
    Main function to execute the script.
    """   
    # Create a new class instance
    Bundle = NSIS(BuildID, files, scratch=scratch, verbose=verbosity)
    # Add source, module and library paths
    Bundle.SourcePath(source)
    # Define output directory
    Bundle.OutputPath(output)
    # Build application
    Bundle.create(**kwargs)
    
if __name__ == "__main__":
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %                                                                         Access command line inputs                                                                  %
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    NSIS.run()
    # Finish 
    print("==================================")
    print("Finished building bundled installer")
    print("==================================")        
    sys.exit()