# -*- coding: utf-8 -*-
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %                                                         PyXMake - Build environment for PyXMake                                                                            %
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
"""
Triple-use minimum working example for PyXMake. This script can be
executed in three different ways in varying levels of accessibility
 
@note: Compile the BoxBeam & MCODAC for Java applications
              using Intel Fortran and Java Native Access (JNA) 
Created on 20.03.2018    

@version:  1.0    
----------------------------------------------------------------------------------------------
@requires:
       - PyXMake

@change: 
       -    
   
@author: garb_ma                                                     [DLR-FA,STM Braunschweig]
----------------------------------------------------------------------------------------------
"""
import os, sys
import argparse

try:
    import PyXMake as _
except ImportError:
    # Script is executed as a plug-in
    sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
finally:
    from PyXMake.Build import Make as pyx  #@UnresolvedImport
    from PyXMake.Tools import Utility  #@UnresolvedImport
    from PyXMake import  VTL  #@UnresolvedImport
    
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
    command = VTL.GetBuildCommand(1),  
    libs = VTL.GetLinkDependency(0, 1, __arch),
    # Resource paths
    source=os.path.join(__mcd_core_path,"src"),
    include=[os.path.join(__mcd_core_path,"include",Utility.GetPlatform(),__arch, x) for x in VTL.GetIncludeDirectory(__mcd_core_path, 0, 4, __arch)], 
    dependency=os.path.join(__mcd_core_path,"lib",Utility.GetPlatform(),__arch), 
    output=os.path.join(__mcd_core_path,"bin",Utility.GetPlatform(),__arch),
    # Architecture, verbose and scratch directory
    architecture=__arch,scratch=VTL.Scratch, verbosity=2):
    """
    Main function to execute the script.
    """                  
    # Build a shared library using the Intel Fortran Compiler
    FBuild = pyx.Fortran(BuildID, files, scratch=scratch, msvsc='vs2015', arch=architecture, verbose=verbosity, lib='shared')
    FBuild.SourcePath(source)      
    FBuild.OutputPath(libpath=output)
    FBuild.AddIncludePath(include)
    FBuild.AddDependencyPath(dependency)    
    FBuild.UseLibraries(libs)
    FBuild.Preprocessing(inend='.for', outend='.f90')   
    FBuild.Build(command)   
    FBuild.create() 

if __name__ == "__main__":
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %                                                                         Access command line inputs                                                                                  %
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    parser = argparse.ArgumentParser(description="Build a static Fortran library remotely on the institute cluster")
    parser.add_argument("user", metavar="user", nargs=1, help="Current user for SSH connection")
    parser.add_argument("key", metavar="key", nargs=1, help="Path to private SSH key")
    parser.add_argument("source_path", metavar="source", nargs=1, help="Directory containing all source files")
    parser.add_argument("feature_path", metavar="feature", nargs=1, help="Directory containing the feature source file \
                                        (in dependence of requested feature: ABAQUS, ANSYS, NASTRAN.") 
    
    try:
        _ = sys.argv[1]
        args, _ = parser.parse_known_args()  
        # Extract command line option to identify the requested make operation
        make_opt = args.make[0]        
    except:
        # This is the default build option
        make_opt = -1    
        # Build all supported features
        if make_opt == -1:  
            
            # Build BoxBeam for Java applications (Fortran shared library). 
            BuildID = 'bbeam_java'; 
            main(BuildID, files=VTL.GetSourceCode(1), source=os.path.join(__mcd_core_path,"external","boxbeam"), 
                     include=[], dependency=[], libs=[])               
            
            # Build MCODAC for Java applications (Fortran shared library). Default settings.  
            BuildID = 'mcd_java'; main(BuildID)
    else:
        # This is not implemented yet
        raise NotImplementedError
    
    # Finish 
    print("==================================")
    print("Finished build for Java")
    print("==================================")    
    sys.exit()