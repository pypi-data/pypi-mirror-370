# -*- coding: utf-8 -*-
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %                                                         PyXMake - Build environment for PyXMake                                                         %
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
"""
Triple-use minimum working example for PyXMake. This script can be
executed in three different ways in varying levels of accessibility
 
@note: Compile a stand-alone application using PyInstaller
Created on 02.05.2020    

@version:  1.0    
----------------------------------------------------------------------------------------------
@requires:
       - PyXMake

@change: 
       - Requires PyCODAC in PYTHONPATH.
   
@author: garb_ma                                      [DLR-FA,STM Braunschweig]
----------------------------------------------------------------------------------------------
"""
import os, sys
import argparse

try:
    import PyXMake as _ #@UnusedImport
except ImportError:
    # Script is executed as a plug-in
    sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
finally:
    import PyXMake
    # Get absolute package paths
    __pyx_src_path = PyXMake.PyXMakePath
    # Import all module dependencies
    from PyXMake.Tools import Utility
    from PyXMake.Build.Make import AllowDefaultMakeOption

def main(
    BuildID, 
    # Resource paths
    source=__pyx_src_path,
    # Define output path
    output=os.getcwd(),
    # Default file extensions to be excluded from the final archive
    exclude = [".git", ".svn", "__pycache__"],
    # Additional keyword arguments
    **kwargs):
    """
    Main function to execute the script.
    """   
    # Create an archive from the given path.
    Utility.CreateArchive(os.path.join(output,BuildID), source=source, exclude=exclude)
    pass
    
if __name__ == "__main__":
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %                                                                         Access command line inputs                                                                  %
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # Process all known arguments
    parser = argparse.ArgumentParser(description='CLI wrapper options for  archive generator.')
    parser.add_argument('name', type=str, nargs=1, help="Name of the archive")
    parser.add_argument('source', type=str, nargs=1, help="Absolute path to source directory.")
    parser.add_argument("--output", type=str, nargs=1, help="Absolute path to output directory. Defaults to the current workspace.")
    parser.add_argument("--exclude", nargs='+', default=[], help="File extensions to be ignored during the process")
    # Check all options or run unit tests in default mode   
    try:
        # Check CLI options
        _ = sys.argv[1]
        args, _ = parser.parse_known_args()  
        # Archive output name is mandatory
        project = args.name[0] ; 
        # Specification is mandatory
        source = args.source[0] ; 
        # Optional non-default output directory
        try: output = args.output[0]
        except: output = os.path.abspath(os.getcwd())
        # Optional non-default exclude pattern
        try: excludes = args.exclude
        except: excludes = [".git", ".svn", "__pycache__"]
    # Use an exception to allow help message to be printed.
    except Exception as _:
        # Run default function call for unit test coverage
        if AllowDefaultMakeOption: main("pyx_core-master.zip")
    # Execute valid CLI command
    else: main(project, source, output, exclude=excludes)
    # Finish 
    print("==================================")
    print("Finished creating archive")
    print("==================================")   