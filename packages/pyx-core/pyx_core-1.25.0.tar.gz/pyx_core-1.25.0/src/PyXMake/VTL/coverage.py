# -*- coding: utf-8 -*-
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %                                                         PyXMake - Build environment for PyXMake                                                                          %
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
"""
Triple-use minimum working example for PyXMake. This script can be
executed in three different ways in varying levels of accessibility
 
@note: Run coverage inherited from pytest-cov with more meaningful default settings 
derived from Robot.

Created on 31.01.2023

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

try:
    import PyXMake as _ #@UnusedImport
except ImportError:
    # Script is executed as a plug-in
    sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
finally:
    from PyXMake.Build.Make import Robot #@UnresolvedImport
    from PyXMake import PyXMakePath #@UnresolvedImport

def main(
    BuildID, 
    # Resource paths
    source = PyXMakePath,
    include = [ 
                        os.path.join(PyXMakePath,"VTL","examples",'pyx_api.py'),
                        os.path.join(PyXMakePath,"VTL","examples",'pyx_cxx.py'),
                        os.path.join(PyXMakePath,"VTL","examples",'pyx_py2x.py'),
                        os.path.join(PyXMakePath,"VTL","examples",'pyx_gfortran.py'),
                        os.path.join(PyXMakePath,"VTL","examples",'pyx_pyreq.py'),
                        os.path.join(PyXMakePath,"VTL","examples",'pyx_doxygen.py'),
                        os.path.join(PyXMakePath,"VTL","examples",'pyx_openapi.py') 
                        ],
    # Default output directory
    output=os.getcwd(),
    # Additional keyword arguments
    **kwargs):
    """
    Main function to execute the script.
    """   
    # Default command. Use settings to modify the documentation.    
    Coverage = Robot(BuildID, source); 
    Coverage.OutputPath(output); 
    if include: Coverage.AddIncludePath(include); 
    Coverage.create(**kwargs) ;

if __name__ == "__main__":
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %                                                                         Access command line inputs                                                                                   %
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # Execute CLI command
    Robot.run()
    # Finish
    print("==================================")    
    print("Finished running test coverage")
    print("==================================")    
    sys.exit()