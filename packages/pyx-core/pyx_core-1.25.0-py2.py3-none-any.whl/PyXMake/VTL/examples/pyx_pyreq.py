# -*- coding: utf-8 -*-
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %                                                         PyXMake - Build environment for PyXMake                                                         %
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
"""
Triple-use minimum working example for PyXMake. This script can be
executed in three different ways in varying levels of accessibility
 
@note: Compile a stand-alone application using PyInstaller
Created on 02.05.2020    

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
    from PyXMake.Build.Make import PyReq  #@UnresolvedImport
    from PyXMake import VTL #@UnresolvedImport

try:
    # Import PyCODAC to build library locally during setup.
    import PyCODAC   
    # Get absolute package paths
    __pyc_src_path = PyCODAC.PyCODACPath
except ImportError:
    # This script is not executed as plug-in for PyCODAC
    __pyc_src_path = ""   
    pass

def main(
    BuildID, 
    # Resource paths
    source=__pyc_src_path,
    # Define output path
    output=__pyc_src_path,
    # Encryption, mode, verbose and scratch directory
    scratch=VTL.Scratch, verbosity=2,
    # Additional keyword arguments
    **kwargs):
    """
    Main function to execute the script.
    """   
    # Create a new class instance
    Py2Req = PyReq(BuildID, os.path.join(source,"__init__.py"), scratch=scratch, verbose=verbosity)
    # Add source
    Py2Req.SourcePath(source)
    # Define output directory
    Py2Req.OutputPath(output)
    # Set pre-processing command
    Py2Req.Preprocessing(kwargs.get("preprocessing",""))
    # Modify build mode
    Py2Req.Build(kwargs.get("compargs","--no-pin"))
    # Create markdown file of dependencies
    Py2Req.create(**kwargs)
    
if __name__ == "__main__":
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %                                                                         Access command line inputs                                                                  %
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # Execute CLI command
    PyReq.run()
    # Finish 
    print("==================================")
    print("Finished building requirements files")
    print("==================================")        
    sys.exit()