# -*- coding: utf-8 -*-
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %                                                         PyXMake - Build environment for PyXMake                                                                            %
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
"""
Triple-use minimum working example for PyXMake. This script can be
executed in three different ways in varying levels of accessibility
 
@note: Compile Muesli for MCODAC under Windows. 

@version:  1.0    
----------------------------------------------------------------------------------------------
@requires:
       - PyXMake, PyCODAC
       
@change: 
       -    
   
@author: garb_ma                                      [DLR-FA,STM Braunschweig]
----------------------------------------------------------------------------------------------
"""
import os, sys

try:
    import PyXMake as _
except ImportError:
    # Script is executed as a plug-in
    sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
finally:
    from PyXMake.Build.Make import CCxx #@UnresolvedImport
    from PyXMake.Tools import Utility #@UnresolvedImport
    from PyXMake import  VTL #@UnresolvedImport

    # Predefined script local variables
    __arch = Utility.GetArchitecture()

try:
    # Import PyCODAC to build library locally during setup.
    from PyCODAC.Tools.Utility import GetPyCODACPath
 
    __mcd_muesli_files = []   
    # Import and set local path to PyCODAC
    __mcd_core_path =  os.path.join(GetPyCODACPath(),"Core")
    __mcd_muesli_base = os.path.join(__mcd_core_path,"external","muesli")
    __mcd_muesli_src = os.path.join(__mcd_muesli_base,"muesli")
    __mcd_muesli_include = [x[0] for x in os.walk(__mcd_muesli_src)]
    __mcd_muesli_include.insert(0,__mcd_muesli_base)
    # Build Muesli with default settings.
    for _, _, files in os.walk(__mcd_muesli_src): __mcd_muesli_files.extend([x for x in files if x.endswith(".cpp") and x not in ["test.cpp"]])
    
except ImportError:
    # This script is not executed as plug-in
    __mcd_core_path = ""
    __mcd_muesli_src = ""
    __mcd_muesli_include = ""
    __mcd_muesli_files = []
except:
    # Something else went wrong. 
    from PyXMake.Tools import ErrorHandling
    ErrorHandling.InputError(20)

def main(
    BuildID, 
    # Build MUESLI by default   
    files=__mcd_muesli_files,
    command = VTL.GetBuildCommand(3),  
    libs = VTL.GetLinkDependency(3, 7, __arch),
    # Resource paths
    source=__mcd_muesli_src,
    include=__mcd_muesli_include, 
    dependency=[], 
    output=os.path.join(__mcd_core_path,"lib",Utility.GetPlatform(),__arch),
    # Architecture, verbose and scratch directory
    architecture=__arch,scratch=VTL.Scratch, verbosity=2,
    # Activate / deactivate incremental compilation. Does deactivate preprocessing.
    incremental = True, **kwargs):
    """
    Main function to execute the script.
    """   
    # Build C++ library 
    CxxBuild = CCxx(BuildID,files,scratch=scratch,arch=architecture,msvsc='vs2015',verbose=verbosity,incremental=incremental, **kwargs)
    CxxBuild.SourcePath(source) 
    CxxBuild.AddIncludePath(include)
    CxxBuild.AddDependencyPath(dependency)
    CxxBuild.OutputPath(output)
    CxxBuild.Preprocessing(copyfiles=files)
    CxxBuild.Build(command)    
    CxxBuild.UseLibraries(libs)
    CxxBuild.create()

if __name__ == "__main__":
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %                                                                         Access command line inputs                                                                                  %
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    CCxx.run()
    # Finish
    print("==================================")    
    print("Finished build on Windows")
    print("==================================")    
    sys.exit()