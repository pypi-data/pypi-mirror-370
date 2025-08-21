# -*- coding: utf-8 -*-
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %                                                         PyXMake - Build environment for PyXMake                                                         %
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
"""
Triple-use minimum working example for PyXMake. This script can be
executed in three different ways in varying levels of accessibility
 
@note: Compile a single PDF document using Latex from TeXFiles or reStructuredText.
Created on 08.09.2020    

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
    from PyXMake import VTL #@UnresolvedImport
    from PyXMake.Build.Make import Latex #@UnresolvedImport

def main(
    BuildID, 
    # Build nothing by default
    file="",
    # Resource paths
    include=[],
    # Encryption, mode, verbose and scratch directory
    scratch=VTL.Scratch, verbosity=2, 
    # Additional keyword arguments
    **kwargs):
    """
    Main function to execute the script.
    """   
    # Create a new class instance
    Tex = Latex(BuildID, file, scratch=scratch, verbose=verbosity, secret=kwargs.pop("secret",None))
    # Add include paths
    Tex.AddIncludePath(include)
    # Compile Latex document directly or open GUI.
    Tex.create(**kwargs)
    
if __name__ == "__main__":
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %                                                                         Access command line inputs                                                                  %
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # Execute CLI command
    Latex.run()
    # Finish 
    print("==================================")
    print("Finished compiling Latex documents")
    print("==================================")        
    sys.exit()