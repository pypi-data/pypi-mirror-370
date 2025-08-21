# -*- coding: utf-8 -*-
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %                                                                                      Environment                                                                                                  %
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
"""
Set up environment for PyXMake when executing scripts directly from command line.
 
@note: PyXMake environment file.
Created on 22.08.2020    

@version:  1.0    
----------------------------------------------------------------------------------------------
@requires:
       - 

@change: 
       -    
   
@author: garb_ma                                                     [DLR-FA,STM Braunschweig]
----------------------------------------------------------------------------------------------
"""

## @package PyXMake.__setenv__
# Initialize PyXMake environment for Python scripts executed directly from the command line.
## @author 
# Marc Garbade
## @date
# 22.08.2020 
## @par Notes/Changes
# - Added documentation // mg 22.08.2020 

import sys, os
import subprocess

__pyx_delimn = " "
__pyx_args = __pyx_delimn.join(sys.argv[1:])
__pyx_exepath = os.path.dirname(os.path.abspath(os.getenv("pyx_python_exe",sys.executable)))
__pyx_pythonpath = os.pathsep.join([os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                           os.path.join(__pyx_exepath,"DLLs"), os.path.join(__pyx_exepath,"lib"), __pyx_exepath, 
                                           os.path.join(__pyx_exepath,"Library","bin"), os.path.join(__pyx_exepath,"lib","site-packages"), 
                                           os.getenv("PYTHONPATH","")])

# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %                                                                              CONDA Environment                                                                                           %
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% 
if os.path.exists(os.path.join(sys.prefix,"conda-meta")):
    os.environ["PATH"] = os.pathsep.join(list(dict.fromkeys(os.path.join(sys.prefix,x) for x in next(os.walk(sys.prefix))[1])) + 
    list(dict.fromkeys(os.getenv("PATH","").split(os.pathsep))))
    
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %                                                                            VIRTUAL Environment                                                                                            %
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% 
# Verify that base libraries always take a higher precedence than user-defined 3rd party packages
sys.path = [x for x in sorted(set(sys.path + __pyx_pythonpath.split(os.pathsep)), key=lambda x: 'site-packages' in x)]

# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %                                                                              PYTHONPATH                                                                                                       %
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% 
# Set environment variable in the process.
os.environ["PYTHONPATH"] = os.pathsep.join(sys.path)

# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %                                                                                Execute script                                                                                                      %
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
if __name__ == '__main__':
    p = subprocess.Popen(__pyx_delimn.join([os.getenv("pyx_python_exe",sys.executable),__pyx_args]).split()) 
    _, _ = p.communicate() 