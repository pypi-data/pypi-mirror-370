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
    from PyXMake.Build.Make import PyInstaller #@UnresolvedImport
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
    # Build stand-alone application of PyCODAC
    script=VTL.GetSourceCode(8),  
    # Resource paths
    source=__pyc_src_path,
    include=VTL.GetIncludeDirectory(os.path.dirname(__pyc_src_path), 8),
    dependency=VTL.GetLinkDependency(8),
    # Define output path
    output=os.path.join(__pyc_src_path,"Plugin","JupyterLab","src",".dist"),
    # Encryption, mode, verbose and scratch directory
    encryption=True, mode="onefile", scratch=VTL.Scratch, verbosity=2,
    # Additional keyword arguments
    **kwargs):
    """
    Main function to execute the script.
    """   
    # Create a new class instance
    Py2App = PyInstaller(BuildID, script, scratch=scratch, verbose=verbosity)
    # Activate or deactivate encryption. Defaults to True.
    Py2App.Encryption(encryption)
    # Add source, module and library paths
    Py2App.SourcePath(source)
    Py2App.AddIncludePath(include)
    Py2App.AddDependencyPath(dependency)
    # Define output directory
    Py2App.OutputPath(output)
    # Set pre-processing command
    Py2App.Preprocessing(kwargs.get("preprocessing",""))
    # Modify build mode
    Py2App.Build(mode)
    # Build application
    Py2App.create(**kwargs)
    
if __name__ == "__main__":
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %                                                                         Access command line inputs                                                                  %
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    PyInstaller.run()
    # Finish 
    print("==================================")
    print("Finished building stand-alone application")
    print("==================================")        
    sys.exit()