# -*- coding: utf-8 -*-
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %                                                         PyXMake - Build environment for PyXMake                                                                            %
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
"""
Minimum working example for PyXMake.
 
@note: Compile the complete MCODAC library for ABAQUS remotely.
Created on 25.06.2018    

@version:  1.0    
----------------------------------------------------------------------------------------------
@requires:
       - PyXMake
       - Adopt Paths.log according to your system settings.

@change: 
       -    
   
@author: garb_ma                                                     [DLR-FA,STM Braunschweig]
----------------------------------------------------------------------------------------------
"""
import os, sys
import posixpath
import argparse

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

def main(BuildID,user, key, 
                # Source and feature paths
                path2src=os.path.join(__mcd_core_path,"src"),
                path2feature=os.path.join(__mcd_core_path,"solver"),
                # Build MCODAC by default
                files=VTL.GetSourceCode(0),          
                # Feature source code file
                source_file="mcd_astandard.f",
                # Build feature (supported FE program)
                version="abq2019", makeopt=0, 
                # Local scratch folder
                scratch=VTL.Scratch, 
                # Additional dependencies on the institute cluster
                dependency=posixpath.join(Utility.AsDrive("cluster",posixpath.sep),"software","mcodac","stable"), verbosity=2,
                # Host and port number. Access DLR's institute cluster by default. 
                host="129.247.54.37", port=22,
                # Additional keyword arguments
                **kwargs):
    """
    Main function to execute the script. 
    """  
    # Program start
    print('==================================')
    print('Starting build process on the institute cluster')
    print('==================================')        
    
    # MCODAC compiler command on Linux.  
    pyx_comp = VTL.GetBuildCommand(5)  

    # Custom shared library build & linker commands (depending on ABAQUS, ANSYS, NASTRAN etc.)
    if makeopt == 0:
        pyx_make = posixpath.join(Utility.AsDrive("cluster",posixpath.sep),"software","abaqus","Commands", version)                                                                                 
        pyx_post = "function ifort() { $pyx_ifort $@ \
                                        -O2 -fpe0 -traceback -recursive -qopenmp -DDEBUG -DCLUSTER -lmcd_corex64; } && \
                            export -f ifort; rm -f *.so;  rm -f *.o; "+ pyx_make +" make -library pyx_file"
    elif makeopt == 1:
        pyx_make = posixpath.join(Utility.AsDrive("cluster",posixpath.sep),"software","ansys_inc",version,"ansys")                                                                                        
        pyx_post = "export ANS_PATH="+pyx_make+" && \
                            export FPATH=$FPATH:$ANS_PATH/customize/include && \
                            export CPATH=$CPATH:$ANS_PATH/customize/include && \
                            function fcomp() { $pyx_ifort \
                                        -w -c -fpp -openmp -fpic -O2 -ftz \
                                        -mcmodel=medium \
                                        -module ./ -DLINX64_SYS -DLINUXEM64T_SYS -DFORTRAN -DOPENMP\
                                        -DCADOE_SOLVER -DDEBUG -DCLUSTER $@; } && \
                            function flink() { $pyx_ifort \
                                        -shared -Xlinker -relax -Xlinker \
                                        --whole-archive userlib.a -Xlinker --no-whole-archive \
                                        -o libansuser.so -Xlinker -soname=libansuser.so $@; } && \
                            source $ANS_PATH/bin/anssh.ini; \
                            rm -f *.o; rm -f *.so; \
                            fcomp pyx_file.f && wait; \
                            ar -qc userlib.a *.o && flink -lmcd_corex64; rm -f *.a;  rm -f *.o; "
    elif makeopt ==2:
        # Build MCODAC remotely on DLR's HPC cluster (CARA).
        host = "cara.dlr.de" 
        dependency = posixpath.join(Utility.AsDrive("home",posixpath.sep),user,"mcodac")
        pyx_make = version
        pyx_post = "function ifort() { $pyx_ifort $@ \
                                        -O2 -fpe0 -traceback -recursive -qopenmp -DDEBUG -DCLUSTER -lmcd_corex64; } && \
                            export -f ifort; "+'export abaquslm_license_file="27018@abaqussd1.intra.dlr.de"'+"; rm -f *.so;  rm -f *.o; "+ pyx_make +" make -library pyx_file"
    elif makeopt == 7: 
        # Build MCODAC library with Peridigm
        pyx_comp = VTL.GetBuildCommand(makeopt)
        # Copy peridigm executable into mcodac binary folder (for now!)
        pyx_post = "mv --force Peridigm " +  posixpath.join(Utility.AsDrive("home",posixpath.sep),user,"mcodac","bin") + " && rm -f pyx_file.f"
    else:
        raise NotImplementedError
    
    # Additional includes from 3rd party software compiled for MCODAC.
    outpath = posixpath.join(Utility.AsDrive("home",posixpath.sep),user)
    libpath = posixpath.join(dependency,"lib"); incpath = posixpath.join(dependency,"include")    
    includes = [outpath, [posixpath.join(incpath, x) for x in VTL.GetIncludeDirectory(__mcd_core_path, 0, 4, "x64")]]
    libs = [posixpath.join(libpath,"libinterpx64.a"), posixpath.join(libpath,"libmueslix64.a"),
               posixpath.join(libpath,"libpchipx64.a"), posixpath.join(libpath,"libbbeamx64.a"),
               posixpath.join(libpath,"libdispmodulex64.a")]
    
    # Remote build using SSH connection.
    SSHBuild = pyx.SSH(BuildID, files, scratch=scratch, verbose=verbosity)

    # Put interface file onto the cluster
    print('==================================')
    print('Establishing SSH connection.')
    print('==================================')       
    SSHBuild.Settings(user, key, host, port, **kwargs)    
    SSH = SSHBuild.ssh_client.open_sftp()
    if not source_file.endswith(".zip"):
        SSH.put(os.path.join(path2feature,source_file),"pyx_file.f")
    else:
        SSH.put(os.path.join(path2feature,source_file),source_file)        
    SSH.close()    

    # This is the default build command.
    SSHBuild.SourcePath(path2src)        
    SSHBuild.AddIncludePath(includes)
    SSHBuild.AddDependencyPath(outpath)
    if makeopt != 2:
        # Builds on the institute cluster (FA)
        SSHBuild.Environment(posixpath.join(Utility.AsDrive("cluster",posixpath.sep),"software","slurm","etc","env.d"),"ifort2016.sh")    
    else:
        # Builds on the DLR HPC cluster (CARA)
        SSHBuild.Environment(bash=VTL.GetEnvironment(4)[0])
    if makeopt >= 3:
        # Special-purpose builds
        SSHBuild.Environment(posixpath.join(Utility.AsDrive("cluster",posixpath.sep),"software","slurm","etc","env.d"),"mpibuild.sh")        
        SSHBuild.Environment(posixpath.join(Utility.AsDrive("cluster",posixpath.sep),"software","slurm","etc","env.d"),"peridigm.sh")
        SSHBuild.Build(pyx_comp,run="custom");
    else:
        # Custom
        SSHBuild.Preprocessing(inend='.for', outend='.f90')   
        SSHBuild.Build(pyx_comp, linkedIn=libs)
    SSHBuild.OutputPath(outpath)
    SSHBuild.Postprocessing(pyx_post)   
    # Execute all commands.
    SSHBuild.create()
    
if __name__ == "__main__":
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %                                                                         Access command line inputs                                                                  %
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    parser = argparse.ArgumentParser(description="Build MCODAC's shared library remotely and its subsidiaries on the institute cluster.\
                                                                                             Supported features are ABAQUS, ANSYS & NASTRAN")
    parser.add_argument("BuildID", metavar="BuildID", nargs=1, help="Name ID for build job")
    parser.add_argument("user", metavar="user", nargs=1, help="Current user for SSH connection")
    parser.add_argument("key", metavar="key", nargs=1, help="Path to private SSH key")
    parser.add_argument("source_path", metavar="source", nargs=1, help="Directory containing all source files")
    parser.add_argument("feature_path", metavar="feature", nargs=1, help="Directory containing the feature source file \
                                              in dependence of requested feature: ABAQUS, ANSYS, NASTRAN.") 
    try:
        _ = sys.argv[1]
        args, _ = parser.parse_known_args()
    except:
        pass
    
    try:
        BuildID = args.BuildID[0]
        user = args.user[0]
        key  = args.key[0]
        path2src = args.source_path[0]
        path2feature = args.feature_path[0]
    except:
        try:        
            from PyCODAC.Plugin import Peridigm
            # Build Peridigm together with MCODAC
            if os.path.exists(Peridigm.PeridigmPath):
                BuildID = "peridigm"
                user = __user
                key  = os.path.join(Utility.AsDrive("C"),"Users",user,"Keys","Putty","id_rsa")
                # Operate fully in a temporary directory
                with Utility.TemporaryDirectory(VTL.Scratch):
                    Peridigm.GetSourceCode(output=os.getcwd(), user=True)
                    main(BuildID,user,key,path2src=os.getcwd(),files=os.listdir(os.getcwd())[0], scratch=os.getcwd(), makeopt=7)
        except ImportError:
            pass
        
        BuildID = 'mcd_core'
        user = __user
        key  = os.path.join(Utility.AsDrive("C"),"Users",user,"Keys","Putty","id_rsa")
        path2src=os.path.join(__mcd_core_path,"src")
        path2feature=os.path.join(__mcd_core_path,"solver")
        
        # Build MCODAC on DLR's HPC cluster (DLR)
        main(BuildID,user,key,path2src,path2feature,version="abaqus",makeopt=2) 
         
        # Build MCODAC on the institute cluster (FA)
        main(BuildID,user,key,path2src,path2feature) 
        
    # Finish
    print("==================================")    
    print("Finished")
    print("==================================")    
    sys.exit()