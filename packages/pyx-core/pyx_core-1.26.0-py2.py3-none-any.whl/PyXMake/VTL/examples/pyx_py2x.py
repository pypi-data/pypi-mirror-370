# -*- coding: utf-8 -*-
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %                                                         PyXMake - Build environment for PyXMake                                                                            %
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
"""
Triple-use minimum working example for PyXMake. This script can be
executed in three different ways in varying levels of accessibility
 
@note: Compile Fortran source as a shared library for Python 
              using f2py (Py2X in the future).
Created on 20.03.2018    

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
    import PyXMake as _ #@UnusedImport
except ImportError:
    # Script is executed as a plug-in
    sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
finally:
    from PyXMake.Tools import Utility #@UnresolvedImport
    from PyXMake.Build.Make import Py2X
    from PyXMake import  VTL #@UnresolvedImport

# Predefined script local variables
__arch = Utility.GetArchitecture()

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
    files=VTL.GetSourceCode(0),  
    command = VTL.GetBuildCommand(0),  
    libs = VTL.GetLinkDependency(0, 0, __arch),
    # Resource paths
    source=os.path.join(__mcd_core_path,"src"),
    include=[os.path.join(__mcd_core_path,"include",Utility.GetPlatform(),__arch, x) 
                    for x in VTL.GetIncludeDirectory(__mcd_core_path, 0, 4, __arch)], 
    dependency=os.path.join(__mcd_core_path,"lib",Utility.GetPlatform(),__arch), 
    output=os.path.join(__mcd_core_path,"bin",Utility.GetPlatform(),__arch),
    # Architecture, verbose and scratch directory
    architecture=__arch,scratch=VTL.Scratch, verbosity=(2 if not Utility.IsDockerContainer() else 2),
    # Activate / deactivate incremental compilation. Does deactivate preprocessing.
    incremental = False, **kwargs):
    """
    Main function to execute the script.
    """
    # Build .pyd using f2py (for now!)
    P2XBuild = Py2X(BuildID, files, scratch=scratch, msvsc=kwargs.pop("msvsc","vs2015"), verbose=verbosity, incremental=incremental, 
                        no_append_arch=kwargs.pop("no_arch",False), **kwargs)
    P2XBuild.AddIncludePath(include)
    P2XBuild.SourcePath(source) 

    # Activate / deactivate incremental compilation & linking
    if not incremental:
        # Set default preprocessor command
        Preprocessing = VTL.GetPreprocessingCommand(0)
        # Use alternative FOSS implementation in Docker container.
        if Utility.IsDockerContainer and Utility.GetPlatform() in ["linux"]: Preprocessing= VTL.GetPreprocessingCommand(1)
        P2XBuild.Preprocessing(Preprocessing+' -DPYD', inend='.for', outend='.fpp') 
    else:
        P2XBuild.Preprocessing(copyfiles=files)
        
    P2XBuild.OutputPath(output)
    P2XBuild.Build(command)    
    P2XBuild.AddDependencyPath(dependency) 
    P2XBuild.UseLibraries(libs)
    P2XBuild.create()
    
if __name__ == "__main__":
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %                                                                         Access command line inputs                                                                                   %
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # Execute CLI command
    Py2X.run()
    # Finish
    print("==================================")
    print("Finished build for Python")
    print("==================================")     
    sys.exit()