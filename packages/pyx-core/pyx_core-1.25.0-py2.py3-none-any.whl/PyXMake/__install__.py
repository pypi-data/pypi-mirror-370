# -*- coding: utf-8 -*-
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %                                                                                              Installation                                                                                             %
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
"""
Development code installation procedure for PyXMake.
 
@note: PyXMake installation file for development code.
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

## @package PyXMake.__install__
# Development code installation procedure for PyXMake.
## @author 
# Marc Garbade
## @date
#  22.08.2020
## @par Notes/Changes
# - Added documentation // mg  22.08.2020

import os,sys
import six
import urllib.request  
import pkg_resources
import subprocess

__pyx_delimn = " "

def main(): # pragma: no cover
    # Add directory of current path to system path
    sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
    # Update PYTHONPATH
    import __setenv__ #@UnresolvedImport @UnusedImport

    # Identify current dependencies
    try:
        from PyXMake.Tools.Utility import GetRequirements
        data = GetRequirements(os.path.dirname(os.path.abspath(__file__)),["--ignore","cmd,bin","--no-pin"])
    # URL to latest dependencies.
    except ImportError:
        target_url="https://fa-jenkins2:8080/job/STM_Archive/doclinks/1/"
        data = urllib.request.urlopen(target_url).read().decode('utf-8').replace("\n","").split()
    finally:        
        # Empty list to store missing dependencies
        update = []     
        # Fetch updated dependencies from STM archive
        installed = {pkg.key for pkg in pkg_resources.working_set}
        required = {x.lower() for x in data}; modules = [x for x in data]
        missing = required - installed
     
    # Loop over all identified modules. Try to import all modules which could not been resolved.
    for x in modules:
        # Module names are case-sensitive
        if x.lower() not in missing:
            continue
        try: 
            x = __import__(x)
        except ImportError:
            # Missing dependency. Add module name to list
            update.append(x)
     
    if update:
        # Unresolved dependencies were found
        print("==================================")    
        print("Found unresolved dependencies:")
        print(*update, sep = "\n")
        print("==================================")          
        print("Starting auto-installation process. Defaults to pip!")  
        print("Continue: [Y/N]; [pip/conda]")
        # Wait for user input. 
        user_input = [x.strip() for x in six.moves.input().lower().split(";")] #@UndefinedVariable
        # Check validity of user input.
        if not user_input or user_input[0] != "y":
            # Wrong input or rejection.
            print("Abort installation process") 
            sys.exit()
        else:
            try:
                package_manager = user_input[1]
            except:
                package_manager = "pip"
            # Check if the package manager is correct.
            if package_manager not in ["pip","conda"]:
                print("Unknown package manager. Use either pip or conda.")  
                sys.exit()
            else:
                print("Attempting installation using %s" % package_manager)  
                try:
                    # Try to install all missing dependencies using the defined package manager
                    subprocess.check_call([os.getenv("pyx_python_exe",sys.executable), '-m', 'pip', 'install', *update], stdout=subprocess.DEVNULL)
                except subprocess.CalledProcessError:
                    print("Installation aborted. Some packages cannot be installed using default settings")   

# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %                                                                              Execute script                                                                                                         %
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
if __name__ == '__main__' and __debug__: # pragma: no cover
    main(); sys.exit()