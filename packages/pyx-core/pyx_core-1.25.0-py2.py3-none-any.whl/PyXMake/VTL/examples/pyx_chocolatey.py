# -*- coding: utf-8 -*-
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %                                                         PyXMake - Build environment for PyXMake                                                         %
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
"""
Minimum working example for PyXMake. 

@note: Compile MCODAC for PYTHON using Mingw64/GFortran on windows.
Created on 25.03.2021

@version:  1.0    
----------------------------------------------------------------------------------------------
@requires:
       - PyXMake
       
@change: 
       - 
   
@author: garb_ma                                      [DLR-FA,STM Braunschweig]
----------------------------------------------------------------------------------------------
"""
import shutil
import os, sys
import tempfile

try:
    import PyXMake as _ #@UnusedImport
except ImportError:
    # Script is executed as a plug-in
    sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
finally:
    from PyXMake.Tools import Utility  #@UnresolvedImport
    from PyXMake import  VTL  #@UnresolvedImport
    from PyXMake.VTL import cmake, py2x #@UnresolvedImport
    
def run(output=os.getcwd(),verbose=2):
    """
    Main function to execute the script.
    """       
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
    
    # Run everything in a temporary directory
    with Utility.TemporaryDirectory(VTL.Scratch):
        
        # Create a temporary source code folder.
        __temp_path = os.path.join(os.getcwd(),Utility.GetTemporaryFileName(extension=""))
        if not os.path.exists(__temp_path): shutil.copytree(__mcd_core_path, __temp_path, ignore=shutil.ignore_patterns('*.svn', '.git'))
         
        # Overwrite default paths to reflect temporary directory
        __mcd_core_path = __temp_path; __mcd_out_path = os.getcwd()

        # Build BoxBeam for current python intepreter using Chocolatey and gfortran on Windows.
        BuildID = 'bbeam'; 
        py2x(BuildID, files=VTL.GetSourceCode(1), source=os.path.join(__mcd_core_path,"external","boxbeam"), libs=[],include=[],dependency=[], scratch = os.getcwd(),
                verbosity=verbose, output=__mcd_out_path)
                   
        # Build Beos for *
        BuildID = 'beos'; 
        py2x(BuildID, files=VTL.GetSourceCode(2), source=os.path.join(__mcd_core_path,"external","beos"), libs=[],include=[],dependency=[], scratch = os.getcwd(), 
                verbosity=verbose, output=__mcd_out_path)
             
        ## Build MCODAC for *
        BuildID = "mcodac"; 
        # Compile all dependencies using CMAKE.
        cmake(BuildID, source=os.path.join(__mcd_core_path,"config"), scratch=os.getcwd())
        # Build wheel 
        py2x(BuildID,  source=os.path.join(__mcd_core_path,"src"),
                include=[os.path.join(__mcd_core_path,"include",Utility.GetPlatform(),__arch, x) for x in VTL.GetIncludeDirectory(__mcd_core_path, 0, 4, __arch)], 
                dependency=os.path.join(__mcd_core_path,"lib",Utility.GetPlatform(),__arch), scratch = os.getcwd(),
                output=__mcd_out_path, verbosity=verbose, no_mkl=True)
          
        # Copy results to output directory
        for x in os.listdir(os.getcwd()):
            if x.endswith((".pyd")): shutil.move(x,os.path.join(output,x))
            
    # Finish
    print('==================================')
    print('Finished')
    print('==================================')      
    
    pass

def main(python=sys.executable, **kwargs):
    """
    Build for a given python executable
    """       
    from PyCODAC import PyCODACPath as __pyc_src_path
    
    ## Add this script to the overall system path
    output_path = os.path.normpath(kwargs.get("output",os.getcwd())).replace(os.sep,os.sep*2)
    module_file = __file__.split(os.sep)[-1].split(".")[0]
    file_dir = os.path.dirname(os.path.abspath(__file__)).replace(os.sep,os.sep*2)

    # Create a temporary python script for execution
    with tempfile.NamedTemporaryFile(mode="w+", suffix=".py", delete=False) as tmp:
        tmp.writelines("import os; import sys; sys.path.insert(0, os.path.normpath('"+file_dir+"')); import %s; %s.run(output='%s')" % (module_file, module_file, output_path))
    
    # Create build command
    command = " ".join([python,os.path.join(__pyc_src_path,"__setenv__.py"),tmp.name])
    
    # Run the command
    p = Utility.Popen(command, verbosity=2, collect=False, shell=True)
    
    # Delete temporary file
    os.remove(tmp.name)
    
    # Return error code
    return getattr(p,"returncode",p)

if __name__ == "__main__":
    main(); sys.exit()