# -*- coding: utf-8 -*-
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %                                                         PyXMake - Build environment for PyXMake                                                                          %
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
"""
Triple-use minimum working example for PyXMake. This script can be
executed in three different ways in varying levels of accessibility
 
@note: Create documentations for PyXMake, PyCODAC and STMLab with Sphinx.
Created on 05.08.2020    

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
    from PyXMake.Build.Make import Sphinx
    from PyXMake.Tools import Utility
    from PyXMake import VTL

# Predefined script local variables
__arch = Utility.GetArchitecture()
__platform = Utility.GetPlatform()
    
try:
    # Import PyCODAC to build library locally during setup.
    from PyCODAC.Tools.Utility import GetPyCODACPath
    # Import and set local path to PyCODAC
    __pyc_core_path =  GetPyCODACPath()
except ImportError:
    # This script is not executed as plug-in
    __pyc_core_path = ""
except:
    # Something else went wrong. 
    from PyXMake.Tools import ErrorHandling
    ErrorHandling.InputError(20)

def main(
    # Mandatory arguments         
    BuildID, masterfile, 
    # Resource paths
    source = os.path.join(__pyc_core_path,"VTL","doc","mcd_legacy") ,
    output= os.path.join(__pyc_core_path,"VTL","doc","mcd_legacy"), 
    include=[os.path.join(__pyc_core_path),Utility.GetPyXMakePath()],
    scratch=VTL.Scratch, verbosity=2,
    **kwargs):
    """
    Main function to execute the script.
    """
    # Modify the current path variable
    SphinxBuild = Sphinx(BuildID, masterfile, scratch=scratch, verbose=verbosity)
    SphinxBuild .SourcePath(source)
    SphinxBuild .AddIncludePath(include)
    SphinxBuild.OutputPath(output)   
    SphinxBuild.Settings(**kwargs)
    SphinxBuild.create()  

if __name__ == '__main__':
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %                                                                         Access command line inputs                                                                                  %
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # Execute CLI command
    Sphinx.run()
    # Finish
    print("==================================")
    print("Finished build with Sphinx")
    print("==================================")    
    sys.exit()