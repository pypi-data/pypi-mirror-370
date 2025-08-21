# -*- coding: utf-8 -*-
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %                                                         PyXMake - Build environment for PyXMake                                                         %
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
"""
Triple-use minimum working example for PyXMake. This script can be
executed in three different ways in varying levels of accessibility
 
@note: Compile a static Fortran library using Mingw64/GFortran on windows.
Created on 20.03.2018    

@version:  1.0    
----------------------------------------------------------------------------------------------
@requires:
       - PyXMake

@change: 
       - Added 3rd party dependencies to build process. Requires 
         PyCODAC in PYTHONPATH.
   
@author: garb_ma                                      [DLR-FA,STM Braunschweig]
----------------------------------------------------------------------------------------------
"""
import os, sys
import argparse
import collections

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
    command = VTL.GetBuildCommand(2),  
    libs = VTL.GetLinkDependency(0, 2, __arch),
    # Resource paths
    source=os.path.join(__mcd_core_path,"src"),
    include=[os.path.join(__mcd_core_path,"include",Utility.GetPlatform(),__arch, x) for x in VTL.GetIncludeDirectory(__mcd_core_path, 0, 4, __arch)], 
    dependency=os.path.join(__mcd_core_path,"lib",Utility.GetPlatform(),__arch), 
    make=[os.path.join(__mcd_core_path,"include",Utility.GetPlatform(),__arch),
                  os.path.join(__mcd_core_path,"lib",Utility.GetPlatform(),__arch)],
    # Architecture, verbose and scratch directory
    architecture=__arch,scratch=VTL.Scratch, verbosity=2,
    # Activate / deactivate incremental compilation. Does deactivate preprocessing.
    incremental = False,
    # Additional keyword arguments
    **kwargs):
    """
    Main function to execute the script.
    """   
    # Evaluate input parameters
    makelist = list([]); makelist.append(make); makelist = list(Utility.ArbitraryFlattening(makelist))    
    replace = kwargs.get('replace', False)   
    # Build a static library using the Intel Fortran Compiler
    FBuild = pyx.Fortran(BuildID, files, scratch=scratch, msvsc='vs2015', arch=architecture, verbose=verbosity, incremental=incremental, bash=True, **kwargs)
    # Combine source code using wrapper module
    if not incremental:
        FBuild.Wrapper(BuildID)
    # Add source, module and library paths
    FBuild.SourcePath(source)       
    FBuild.AddIncludePath(include)
    FBuild.AddDependencyPath(dependency)  
    # Define output paths
    try:    
        # Module & library path are not relative to each other
        FBuild.OutputPath(modulepath=makelist[0], libpath=makelist[1])
    except:
        # Module & library path are relative to each other.
        FBuild.OutputPath(modulepath=os.path.join(makelist[0],"include"), libpath=os.path.join(makelist[0],"lib"))  
    if isinstance(replace,dict):   
        FBuild.Preprocessing(inend='.for', outend='.f90', replace=replace)
    elif incremental:
        FBuild.Preprocessing(copyfiles=files)
    else: 
        FBuild.Preprocessing(inend='.for', outend='.f90') 
    # Define libraries used during linking 
    FBuild.UseLibraries(libs)    
    FBuild.Build(command)
    # Pass additional keywords to command   
    FBuild.create(**kwargs)

if __name__ == "__main__":
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %                                                                         Access command line inputs                                                                  %
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    parser = argparse.ArgumentParser(description="Build a static Fortran library remotely on the current machine")
    
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
                 
            # Build BoxBeam; Define files to be processed for BoxBeam
            BuildID = "bbeam"
            box_source = os.path.join(__mcd_core_path,"external","boxbeam")
            box_make   = [os.path.join(__mcd_core_path,"include",Utility.GetPlatform(),__arch,"boxbeam"), 
                                      os.path.join(__mcd_core_path,"lib",Utility.GetPlatform(),__arch)]
            main(BuildID, files=VTL.GetSourceCode(1), source=box_source, include=[], make=box_make, libs=[])
              
            # Build Beos; Define files to be processed for Beos
            BuildID = "beos"
            beos_source = os.path.join(__mcd_core_path,"external",BuildID)
            beos_make   = [None, os.path.join(__mcd_core_path,"lib",Utility.GetPlatform(),__arch)]         
            main(BuildID, files=VTL.GetSourceCode(2), command=VTL.GetBuildCommand(2,"mixed"), source=beos_source, 
                 include=[], make=beos_make, libs=[], incremental=True)
                                      
            # Build CompDam; Define files to be processed for CompDam                
            BuildID = "compdam"; sep = " "
            os.environ["pyx_cflags"] =  '-fcray-pointer'                                                     
            dam_make = [os.path.join(__mcd_core_path,"include",Utility.GetPlatform(),__arch,BuildID),
                                      os.path.join(__mcd_core_path,"lib",Utility.GetPlatform(),__arch)]
            dam_replace = collections.OrderedDict([('(valueLogical .NE. saveTo)',"(valueLogical .NEQV. saveTo)"),  #@UndefinedVariable
                                                                                   ('EOF(unit)',"IS_IOSTAT_END(iostat)")])
            main(BuildID, 
                    files=VTL.GetSourceCode(4), 
                    # Add custom directive to command line to activate usage without ABAQUS
                    command=sep.join([VTL.GetBuildCommand(2,"free"),"-DPYEXT"]), 
                    source=os.path.join(__mcd_core_path,"external",BuildID,"for"),
                    include=[], make=dam_make, libs=[], replace=dam_replace)
                                  
            # Build DispModule              
            BuildID = "dispmodule"                                                            
            disp_make = [os.path.join(__mcd_core_path,"include",Utility.GetPlatform(),__arch,BuildID),
                                     os.path.join(__mcd_core_path,"lib",Utility.GetPlatform(),__arch)]
            main(BuildID, 
                    files=VTL.GetSourceCode(5), 
                    command=VTL.GetBuildCommand(2,"free"), 
                    source=os.path.join(__mcd_core_path,"external",BuildID,"Fortran90","Src"),
                    include=[], make=disp_make, libs=[])
                               
            # Compile all low-level external libraries used by MCODAC using Intel Fortran.         
            # Files to be processed by low-level libraries
            BuildIDs = [os.path.splitext(x)[0].lower() for x in VTL.GetSourceCode(6)]
            for BuildID in sorted(BuildIDs)[::-1]:
                srcfile = [x for x in VTL.GetSourceCode(6) if x.startswith(BuildID)]
                # Mixed format compilation
                style = "fixed"; combine=False            
                if not BuildID.endswith("790"): 
                    style = "free" 
                    combine=True
                # Define files to be processed for TOMS
                source = os.path.join(__mcd_core_path,"external","toms")      
                make   = [os.path.join(__mcd_core_path,"include",Utility.GetPlatform(),__arch, "toms"), 
                                  os.path.join(__mcd_core_path,"lib",Utility.GetPlatform(),__arch)]      
                main(BuildID, files=srcfile, command=VTL.GetBuildCommand(2, style+" -DPYX_WRAPPER"), make=make, 
                          combine=combine, source=source, include=[], libs=[])
         
            ## Name mangling without changing the original source code. Rename procedures to avoid conflicts in final software.
            # Update: Rename explicitly to avoid linking errors using GCC/GFortran.
            pchip_replace = collections.OrderedDict([('rand',"pchip_rand"), ('RAND',"pchip_rand"), ('subroutine timestamp ( )','subroutine timestamp ( ) BIND(C, NAME="pchip_timestamp")')]) #@UndefinedVariable
                            
            # Compile all low-level external libraries used by MCODAC using Intel Fortran.         
            # Files to be processed by low-level libraries
            BuildIDs = [os.path.splitext(x)[0].lower() for x in VTL.GetSourceCode(7)]
            for BuildID in BuildIDs:      
                srcfile = [x for x in VTL.GetSourceCode(7) if x.startswith(BuildID)]
                # Define files to be processed for NMS, PCHIP, SLATEC & INTERP
                source = os.path.join(__mcd_core_path,"external",BuildID)      
                make   = [os.path.join(__mcd_core_path,"include",Utility.GetPlatform(),__arch, BuildID), 
                                  os.path.join(__mcd_core_path,"lib",Utility.GetPlatform(),__arch)]      
                if BuildID == "pchip":
                    main(BuildID, files=srcfile, command=VTL.GetBuildCommand(2, "free"), source=source, make=make,
                              include=[], libs=[], replace=pchip_replace)
                else:
                    main(BuildID, files=srcfile, command=VTL.GetBuildCommand(2, "free"), source=source, make=make, include=[], libs=[])
           
            # Build MCODAC (default settings)
            BuildID = "mcd_core"; main(BuildID) 
    else:
        # This is not implemented yet
        raise NotImplementedError

    # Finish
    print('==================================')
    print('Finished')
    print('==================================')      
    sys.exit()