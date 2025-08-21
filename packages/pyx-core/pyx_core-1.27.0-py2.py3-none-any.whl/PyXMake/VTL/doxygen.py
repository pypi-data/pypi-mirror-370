# -*- coding: utf-8 -*-
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %                                                         PyXMake - Build environment for PyXMake                                                                          %
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
"""
Triple-use minimum working example for PyXMake. This script can be
executed in three different ways in varying levels of accessibility
 
@note: Create html source code documentations for PyXMake, PyCODAC, 
              MCODAC & BoxBeam with Doxygen.
Created on 22.03.2018    

@version:  1.0    
----------------------------------------------------------------------------------------------
@requires:
       - PyXMake, PyCODAC

@change: 
       -    
   
@author: garb_ma                                                     [DLR-FA,STM Braunschweig]
----------------------------------------------------------------------------------------------
"""
import os, sys

try:
    import PyXMake as _ #@UnusedImport
except ImportError:
    # Script is executed as a plug-in
    sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
finally:
    from PyXMake.Tools import Utility #@UnresolvedImport
    from PyXMake.Build import Make
    from PyXMake.Build.Make import Doxygen
    from PyXMake import VTL #@UnresolvedImport

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
    # Build MCODAC by default   
    title=["MCODAC", "MCODAC Developer Guide"], 
    files=VTL.GetSourceCode(0), ftype="Fortran",
    # Resource paths
    source=os.path.join(__mcd_core_path,"src"),
    output=os.path.join(os.path.dirname(__mcd_core_path),"VTL","doc","mcd_core"),
    # Scratch directory & verbosity
    scratch=VTL.Scratch, verbosity=0,
    # Additional keyword arguments
    **kwargs):
    """
    Main function to execute the script.
    """   
    # Default command. Use settings to modify the documentation.    
    doxcommand = kwargs.get("config",os.path.join(Make.Path2Config,"stm_doc_config")) 
    DoxyBuild = Doxygen(BuildID, files, stype=ftype, msvsc="vs2015", scratch=scratch, verbose=verbosity)
    if ftype not in ("Python", "Java"):
        DoxyBuild.SourcePath(source)        
    DoxyBuild.OutputPath(output)       
    if ftype not in ("Python", "Java"):
        DoxyBuild.Preprocessing(VTL.GetPreprocessingCommand(1 if not Utility.GetPlatform() in ["windows"] else 0), inend=".for", outend=".fpp")    
    DoxyBuild.Build(doxcommand)    
    DoxyBuild.Settings(brief=title[0], header=title[1], **kwargs)
    DoxyBuild.create()

if __name__ == "__main__":
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %                                                                         Access command line inputs                                                                                   %
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # Execute CLI command
    Doxygen.run()
    # Finish
    print("==================================")    
    print("Finished building HTML documentations")
    print("==================================")    
    sys.exit()