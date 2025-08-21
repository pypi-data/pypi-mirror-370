# -*- coding: utf-8 -*-
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %                                                         PyXMake - Build environment for PyXMake                                                                            %
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
"""
Triple-use minimum working example for PyXMake. This script can be
executed in three different ways in varying levels of accessibility
 
@note: Compile Fortran source on the institute cluster. 
              Uses main function

@version:  1.0    
----------------------------------------------------------------------------------------------
@requires:
       - PyXMake
       - SSH key
   
@author: garb_ma                                      [DLR-FA,STM Braunschweig]
----------------------------------------------------------------------------------------------
"""
import os, sys
import argparse
import posixpath
import collections

try:
    import PyXMake as _
except ImportError:
    # Script is executed as a plug-in
    sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
finally:
    from PyXMake.Build import Make as pyx #@UnresolvedImport
    from PyXMake.Tools import Utility #@UnresolvedImport
    from PyXMake import VTL #@UnresolvedImport

# Predefined script local variables
__user = os.getenv("username","")
__mcd_cluster_dev = posixpath.join(Utility.AsDrive("home",posixpath.sep),__user,"mcodac")
__mcd_cluster_incpath = posixpath.join(__mcd_cluster_dev,"include")    
__mcd_cluster_libpath = posixpath.join(__mcd_cluster_dev,"lib")   

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
    # Mandatory arguments
    BuildID, user, key, 
    # Build MCODAC by default
    files=VTL.GetSourceCode(0), 
    command=VTL.GetBuildCommand(5),
    # Resource paths
    source=os.path.join(__mcd_core_path,"src"), 
    include=[posixpath.join(__mcd_cluster_incpath, x) for x in VTL.GetIncludeDirectory(__mcd_core_path, 0, 4, "x64")],
    make=__mcd_cluster_dev, 
    link=[posixpath.join(__mcd_cluster_libpath, ".".join(["lib"+x,"a"])) for x in VTL.GetLinkDependency(0, 4, "x64")],
    # Bash environment scripts
    environment = VTL.GetEnvironment(0),
    # Architecture, verbose and scratch directory (on host)
    architecture="x64", scratch=VTL.Scratch, verbosity=0,
    # Activate / deactivate incremental compilation. Does deactivate pre-processing.
    incremental = False,
    # Host and port number. Access DLR's institute cluster by default. 
    host="129.247.54.37", port=22,
    # Additional keyword arguments
    **kwargs):
    """
    Main function to execute the script.
    """
    # Evaluate input parameters
    envlist = list([]); envlist.append(environment); envlist =  list(Utility.ArbitraryFlattening(envlist))
    makelist = list([]); makelist.append(make); makelist = list(Utility.ArbitraryFlattening(makelist))
    precommand= kwargs.get("precommand",""); replace = kwargs.get('replace', False)        
    # Remote build using SSH connection.
    SSHBuild = pyx.SSH(BuildID, files, scratch=scratch, arch=architecture, verbose=verbosity, incremental=incremental)
    # Combine source code using wrapper module
    if not incremental:
        SSHBuild.Wrapper(BuildID)    
    SSHBuild.SourcePath(source)        
    SSHBuild.AddIncludePath(include)
    # Load environments successively (if given)
    for x in envlist:    
        SSHBuild.Environment(bash=x)
    try:    
        # Module & library path are not relative to each other
        SSHBuild.OutputPath(modulepath=makelist[0], libpath=makelist[1])
    except:
        # Module & library path are relative to each other.
        SSHBuild.OutputPath(modulepath=posixpath.join(makelist[0],"include"), libpath=posixpath.join(makelist[0],"lib"))    
    if isinstance(replace,dict):   
        SSHBuild.Preprocessing(precommand,inend='.for', outend='.f90', replace=replace)
    # Activate / deactivate incremental compilation & linking
    elif incremental:
        SSHBuild.Preprocessing(copyfiles=files)
    else:
        SSHBuild.Preprocessing(precommand,inend='.for', outend='.f90')       
    SSHBuild.Build(command, linkedIn=link)   
    SSHBuild.Settings(user, key, host, port, **kwargs)
    SSHBuild.create(**kwargs)
    
if __name__ == "__main__":
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %                                                                         Access command line inputs                                                                                  %
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    parser = argparse.ArgumentParser(description="Build a static Fortran library remotely on the institute cluster")
    parser.add_argument("user", metavar="user", nargs=1, help="Current user for SSH connection")
    parser.add_argument("key", metavar="key", nargs=1, help="Path to private SSH key")
    
    try:
        _ = sys.argv[1]
        args, _ = parser.parse_known_args()
    except:
        pass
  
    try:
        # SSH key informations
        user = args.user[0]
        key  = args.key[0]          
    except:
        # Default settings. Retain pristine version of this script and build all static Fortran libraries associated with MCODAC. 
        user =__user
        key   = os.path.join(Utility.AsDrive("C"),"Users",user,"Keys","Putty","id_rsa")
        
        # Build BoxBeam; Define files to be processed for BoxBeam
        box_source = os.path.join(__mcd_core_path,"external","boxbeam")
        box_make   = [posixpath.join(__mcd_cluster_dev,"include","boxbeam"), posixpath.join(__mcd_cluster_dev,"lib")]
        main('bbeam', user, key, files=VTL.GetSourceCode(1), source=box_source, include=[], make=box_make, link=[])
           
        # Build DispModule; Define files to be processed for DispModule             
        disp_source=os.path.join(__mcd_core_path,"external","dispmodule","Fortran90","Src")
        disp_make   = [posixpath.join(__mcd_cluster_dev,"include","dispmodule"), posixpath.join(__mcd_cluster_dev,"lib")]     
        main("dispmodule" , user, key, files=VTL.GetSourceCode(5), command=VTL.GetBuildCommand(5, "free"), source=disp_source, 
                   include=[], make=disp_make, link=[], incremental=True)
                          
        # Compile all low-level external libraries used by MCODAC using Intel Fortran.         
        # Files to be processed by low-level libraries
        BuildIDs = [os.path.splitext(x)[0].lower() for x in VTL.GetSourceCode(6)]
        for BuildID in BuildIDs:      
            srcfile = [x for x in VTL.GetSourceCode(6) if x.startswith(BuildID)]
            # Mixed format compilation
            style = "fixed"; combine=False            
            if not BuildID.endswith("790"): 
                style = "free"; combine=True
            # Define files to be processed for TOMS
            toms_source = os.path.join(__mcd_core_path,"external","toms")      
            make   = [posixpath.join(__mcd_cluster_dev,"include","toms"),posixpath.join(__mcd_cluster_dev,"lib")]      
            # Wrap the original source code and put all subroutines & functions in a module
            main(BuildID, user, key, files=srcfile, command=VTL.GetBuildCommand(5, style+" -DPYX_WRAPPER"), make=make, 
                      combine=combine, source=toms_source, include=[], libs=[], link=[])
                  
        # Name mangling without changing the original source code. Rename procedures to avoid conflicts in final software.
        pchip_replace = collections.OrderedDict([('rand',"pchip_rand"), ('RAND',"pchip_rand"), ('subroutine timestamp ( )','subroutine timestamp ( ) BIND(C, NAME="pchip_timestamp")')]) #@UndefinedVariable
           
        # Compile all low-level external libraries used by MCODAC using Intel Fortran.         
        # Files to be processed by low-level libraries
        BuildIDs = [os.path.splitext(x)[0].lower() for x in VTL.GetSourceCode(7)]
        for BuildID in BuildIDs:
            srcfile =  [x for x in VTL.GetSourceCode(7) if x.startswith(BuildID)]
            # Define files to be processed for NMS, PCHIP, SLATEC & INTERP
            source = os.path.join(__mcd_core_path,"external",BuildID)     
            if BuildID == "pchip":       
                main(BuildID, user, key, files=srcfile, command=VTL.GetBuildCommand(5, "free"), 
                         source=source, include=[], link=[],
                         precommand="fpp -P", replace=pchip_replace)
            else:
                main(BuildID, user, key, files=srcfile, command=VTL.GetBuildCommand(5, "free"), source=source, include=[], link=[])
          
        # Build MCODAC (default settings)
        main('mcd_core', user, key)
    else:
        # This is not implemented yet.
        raise NotImplementedError
    
    # Finish
    print("==================================")    
    print("Finished")
    print("==================================")    
    sys.exit()