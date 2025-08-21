# -*- coding: utf-8 -*-
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %                                                         PyXMake - Build environment for PyXMake                                                                            %
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
"""
Triple-use minimum working example for PyXMake. This script can be
executed in three different ways in varying levels of accessibility

@note: Compile Fortran source for PYTHON remotely 
              on the institute cluster. Uses main function.

@version:  1.0    
----------------------------------------------------------------------------------------------
@requires:
       - PyXMake
       - SSH key
       
@date:
       - 24.07.2019 
   
@author: garb_ma                                      [DLR-FA,STM Braunschweig]
----------------------------------------------------------------------------------------------
"""
import os, sys
import argparse
import posixpath

try:
    import PyXMake as _
except ImportError:
    # Script is executed as a plug-in
    sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
finally:
    from PyXMake.Build import Make as pyx
    from PyXMake.Tools import Utility
    from PyXMake import VTL

# Predefined script local variables
__user = os.getenv("username","")
__mcd_cluster_dev = posixpath.join(Utility.AsDrive("home",posixpath.sep),__user,"mcodac")
__mcd_cluster_stable = posixpath.join(Utility.AsDrive("cluster",posixpath.sep),"software","mcodac","stable")
__mcd_cluster_incpath = posixpath.join(__mcd_cluster_stable,"include")    

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
    command=VTL.GetBuildCommand(4),
    lib=VTL.GetLinkDependency(0, 4,"x64"),
    # Resource paths
    source=os.path.join(__mcd_core_path,"src"), 
    include=[posixpath.join(__mcd_cluster_incpath, x) for x in VTL.GetIncludeDirectory(__mcd_core_path, 0, 4, "x64")], 
    dependency=posixpath.join(__mcd_cluster_stable,"lib"), 
    output=posixpath.join(__mcd_cluster_dev,"bin"),
    # Bash environment scripts
    environment = VTL.GetEnvironment(2),
    # Architecture, verbose and scratch directory (on host)
    architecture="x64", scratch=VTL.Scratch, verbosity=2,
    # Activate / deactivate incremental compilation. Does deactivate pre-processing.
    incremental=False,
    # Host and port number. Access DLR's institute cluster by default. 
    host="129.247.54.37", port=22, **kwargs):
    """
    Main function to execute the script.
    """  
    envlist = list([]); envlist.append(environment); envlist = list(Utility.ArbitraryFlattening(envlist)) 
    # Remote build using SSH connection.
    SSHBuild = pyx.SSH(BuildID, files,  msvsc='vs2015', scratch=scratch, arch=architecture, 
                                       verbose=verbosity, incremental=incremental)
    SSHBuild.SourcePath(source)        
    SSHBuild.AddIncludePath(include)
    SSHBuild.AddDependencyPath(dependency)
    # Load environments successively (if given)
    for x in envlist:    
        SSHBuild.Environment(bash=x)

    # Activate / deactivate incremental compilation & linking
    if not incremental:
        SSHBuild.Preprocessing('fpp -P -e -DPYD', inend='.for', outend='.f90') 
    else:
        SSHBuild.Preprocessing(copyfiles=files)

    SSHBuild.OutputPath(libpath=output)    
    SSHBuild.Build(command, run="f2py", lib=lib)   
    SSHBuild.Settings(user, key, host, port, **kwargs)
    SSHBuild.create()
    
if __name__ == "__main__":
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %                                                                         Access command line inputs                                                                                  %
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    parser = argparse.ArgumentParser(description="Build shared Fortran libraries for Python remotely on the institute cluster.")
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
        user = __user
        key   = os.path.join(Utility.AsDrive("C"),"Users",user,"Keys","Putty","id_rsa")
        
        # Remotely build BEOS for Python (2.7, 3.5, 3.6) using SSH cluster connection.
        for i in range(1,4):        
            # Build settings
            BuildID = "beos"; env = VTL.GetEnvironment(i)
            files=VTL.GetSourceCode(2); command=VTL.GetBuildCommand(4,"free")          
            lib = []; include = []; dependency = []         
            # Resource paths
            source=os.path.join(__mcd_core_path,"external","beos") 
            # Execute make function obtained from virtual test lab.
            main(BuildID, user, key, files, command, lib, source, include, dependency, environment=env, verbosity=0, incremental=True)
             
        # Remotely build BoxBeam for Python (2.7, 3.5, 3.6) using SSH cluster connection.
        for i in range(1,4):        
            # Build settings
            BuildID = "bbeam"; env = VTL.GetEnvironment(i)
            files=VTL.GetSourceCode(1); command=VTL.GetBuildCommand(4)          
            lib = []; include = []; dependency = []      
            # Resource paths
            source=os.path.join(__mcd_core_path,"external","boxbeam") 
            # Execute make function obtained from virtual test lab.
            main(BuildID, user, key, files, command, lib, source, include, dependency, environment=env, verbosity=0)
            
        # Remotely build MCODAC for Python (2.7, 3.5, 3.6) using SSH cluster connection (default settings).
        for i in range(1,4):       
            # Build settings            
            BuildID = "mcd_core"; env = VTL.GetEnvironment(i)    
            # Execute make function obtained from virtual test lab with default settings (builds MCODAC).
            main(BuildID, user, key, environment=env)         
            
    else:
        # This is not implemented yet.
        raise NotImplementedError
    
    # Finish
    print("==================================")
    print("Finished build for Python")
    print("==================================")    
    sys.exit()