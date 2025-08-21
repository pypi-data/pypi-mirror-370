# -*- coding: utf-8 -*-
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %                                                         PyXMake - Build environment for PyXMake                                                         %
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
"""
Minimum working example for PyXMake. 

@note: Compile a project using CMAKE on windows.
Created on 15.01.2024   

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

try:
    import PyXMake as _ #@UnusedImport
except ImportError:
    # Script is executed as a plug-in
    sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
finally:
    from PyXMake import  VTL  #@UnresolvedImport
    from PyXMake.Tools import Utility
    from PyXMake.Build.Make import CMake  #@UnresolvedImport
    
try:
    # Import PyCODAC to build library locally during setup.
    from PyCODAC.Tools.Utility import GetPyCODACPath
    # Import and set local path to PyCODAC
    __mcd_core_path =  os.path.join(GetPyCODACPath(),"Core")
except ImportError:
    # This script is not executed as plug-in
    __mcd_core_path = ""
except:
    # Something else went wrong. 
    from PyXMake.Tools import ErrorHandling
    ErrorHandling.InputError(20)
    
def main(
    BuildID, 
    # Resource paths
    source=os.path.join(__mcd_core_path,"config"),
    output=None,
    # Scratch directory & verbosity
    scratch=VTL.Scratch, verbosity=2,
    # Additional keyword arguments
    **kwargs):
    """
    Main function to execute the script.
    """
    # Use generator expression to toggle between settings
    Generator = Utility.ChangedWorkingDirectory if scratch != VTL.Scratch else Utility.TemporaryDirectory
    # Compile everything using CMake.
    with Generator(scratch):
        Make = CMake(BuildID,"CMakeLists.txt", scratch=os.getcwd(), verbose=verbosity, **kwargs)
        Make.SourcePath(source)
        if output: Make.OutputPath(output)
        Make.create(**kwargs)

if __name__ == "__main__":
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %                                                                         Access command line inputs                                                                                   %
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # Execute CLI command
    CMake.run(foss=Utility.GetExecutable("choco") or Utility.GetPlatform() in ["linux"])
    # Finish
    print('==================================')
    print('Finished')
    print('==================================')         
    sys.exit()
