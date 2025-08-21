# -*- coding: utf-8 -*-
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %                                                         PyXMake - Build environment for PyXMake                                                                          %
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
"""
Triple-use minimum working example for PyXMake. This script can be
executed in three different ways in varying levels of accessibility
 
@note: Compile MCODAC for ABAQUS Standard & Explicit 
              on Windows. Can be combined with self-written code alike.
Created on 25.06.2018    

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
import argparse
import tempfile

try:
    import PyXMake as _
except ImportError:
    # Script is executed as a plug-in
    sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
finally:
    from PyXMake.Build.Make import Custom, AllowDefaultMakeOption #@UnresolvedImport
    from PyXMake.Tools import Utility #@UnresolvedImport
    from PyXMake import  VTL #@UnresolvedImport

# Predefined script local variables
__arch = "x64"

# Select a installation of ABAQUS. Always use latest found.
os.environ["pyx_abaqus"] = os.getenv("pyx_abaqus","abaqus")

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
    # Build MCODAC for ABAQUS Standard by default   
    files="mcd_astandard",  
    command = VTL.GetBuildCommand(6),  
    libs = ['mcd_corex64'] + VTL.GetLinkDependency(0),
    # Resource paths
    source=os.path.join(__mcd_core_path,"solver"),
    include=list(Utility.ArbitraryFlattening([[os.path.join(__mcd_core_path,"include",Utility.GetPlatform(),__arch)], 
                    [os.path.join(__mcd_core_path,"include",Utility.GetPlatform(),__arch, x) for x in VTL.GetIncludeDirectory(__mcd_core_path, 0, 4, __arch)]])), 
    dependency=os.path.join(__mcd_core_path,"lib",Utility.GetPlatform(),__arch), 
    output=os.path.join(__mcd_core_path,"bin",Utility.GetPlatform(),__arch),
    # Verbose and scratch directory
    scratch=VTL.Scratch, verbosity=2,
    # Additional keyword arguments
    **kwargs):
    """
    Main function to execute the script.
    """
    # Execute each call in a unique, isolated environment
    with Utility.TemporaryEnvironment(): 
        # Set default preprocessor command
        Preprocessing = VTL.GetPreprocessingCommand(0)
        # Use alternative FOSS implementation in Docker container.
        if Utility.IsDockerContainer and Utility.GetPlatform() in ["linux"]: Preprocessing= VTL.GetPreprocessingCommand(1)
        # Build a shared library for ABAQUS using the Intel Fortran Compiler
        ABQBuild = Custom(BuildID, files, scratch=scratch, msvsc="vs2015", arch=__arch, verbose=verbosity, **kwargs)
        ABQBuild.SourcePath(source)       
        ABQBuild.AddIncludePath(include)
        ABQBuild.AddDependencyPath(dependency)
        ABQBuild.OutputPath(output, files=["standardU.dll","explicitU-D.dll"])
        ABQBuild.Preprocessing(Preprocessing, inend='.f', outend='.f')
        ABQBuild.UseLibraries(libs)
        ABQBuild.Build(command)
        ABQBuild.create()

if __name__ == "__main__":
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %                                                                         Access command line inputs                                                                                  %
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # Process all known arguments
    parser = argparse.ArgumentParser(description='CLI wrapper options for  ABAQUS make command.', parents=[Custom.__parser__()])
    parser.add_argument('-l', '--libs', nargs='+', default=[], help="List of all libraries used to resolve symbols. The libraries are evaluated in the given order.")
    parser.add_argument('-d', '--dependency', nargs='+', default=[], help="Additional search paths to resolve library dependencies.")
    # Check all options or run unit tests in default mode   
    try:
        # Check CLI options
        _ = sys.argv[1]
        # Collect all verified options
        args, unknown = parser.parse_known_args()
        # Collect all undocumented options
        undocumented = dict(x.replace("--","").split("=") for x in unknown if "=" in x)
        # Project name is mandatory
        project = undocumented.get("name",args.name[0])
        # Specification of source directory is mandatory
        source = undocumented.get("source",args.source[0])
        # Optional non-default output directory
        try: files = args.files
        except: files = []
        # Optional non-default additional libraries
        try: 
            libs = args.libs
            # Sanitize the given library names. 
            libs = [Custom.sanitize(x) for x in libs]
        except: libs = []
        # Optional non-default output directory
        try: output = Custom.sanitize(args.output[0])
        except: output = os.path.abspath(os.getcwd())
        # Optional non-default scratch directory
        try: scratch = args.scratch[0]
        except: scratch = tempfile.mkdtemp()
        # Verify that files contains relative not absolute paths
        if all(os.path.exists(os.path.abspath(file) ) for file in files): 
            ## When an absolute path for files is given, overwrite all other entries given in source
            try: source, files = ( os.path.dirname(os.path.abspath(next(iter(files)))), 
                                              os.path.basename(os.path.abspath(next(iter(files)))) )
            except: pass
        # Create a dictionary combining all settings
        settings = {"source":source, "output":output, "files":files, "scratch": scratch, "libs": libs}
        # Loop over options requiring paths to be sanitized
        for option in ["include", "dependency"]: 
            # Optional non-default definition of additional include directories
            try: 
                _ = getattr(args,option)[0]
                # Collect all given paths. Get system independent format
                path = list(Utility.ArbitraryFlattening(getattr(args,option)));
                path = [Custom.sanitize(x) for x in path]
                sanitized = Utility.GetSanitizedDataFromCommand(path)
            # No extra search paths have been given
            except: sanitized = []
            # Add all sanitized search paths to settings
            settings.update({option: sanitized})
    # Use an exception to allow help message to be printed.
    except Exception as _:
        pass
        # Build all supported features
        if AllowDefaultMakeOption:       
            # Temporary ID during the build process.
            BuildID = 'mcd_abaqus'           
            main(BuildID,"mcd_astandard"); main(BuildID,"mcd_aexplicit") 
    # Execute valid CLI command
    else: main(project, **settings)
    # Finish
    print('==================================')
    print('Finished build for ABAQUS')
    print('==================================')        
    sys.exit()