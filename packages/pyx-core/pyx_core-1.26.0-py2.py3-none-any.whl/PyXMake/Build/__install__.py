# -*- coding: utf-8 -*-
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %                                                                                              Installation                                                                                             %
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
"""
Fetch 3rd party dependencies for PyXMake from DLR's resource server.
 
@note: PyXMake 3rd party dependency installer
Created on 04.08.2020 

@version:  1.0    
----------------------------------------------------------------------------------------------
@requires:
       - 

@change: 
       -    
   
@author: garb_ma                                                     [DLR-FA,STM Braunschweig]
----------------------------------------------------------------------------------------------
"""

## @package PyXMake.Build.__install__
# Fetch 3rd party dependencies for PyXMake from DLR's resource server.
## @author 
# Marc Garbade
## @date
#  04.08.2020    
## @par Notes/Changes
# - Added documentation // mg  04.08.2020

import os, sys
import urllib.request
import subprocess
import zipfile
import atexit

try:
    import PyXMake as _ #@UnusedImport
except ImportError:
    # Script is executed as a plug-in
    sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
finally:
    from PyXMake import Build #@UnresolvedImport
    from PyXMake.Tools import Utility #@UnresolvedImport

## Some immutable variables
__cmd_delimn = " "
__pyx_dependency = ["perl","latex","pandoc"]
# Add custom user dependencies
__pyx_dependency.extend([os.getenv("pyx_user_dependency",None)])
# Only install a single entity. Overwrite everything else.
if os.getenv("pyx_user_install",""): __pyx_dependency = [os.getenv("pyx_user_install")]

def main(*args, **kwargs): # pragma: no cover
    """
    Main function to execute the script. 
    """
    # Loop over all dependencies. Remove user dependency if not set.
    for __package in list(filter(None, __pyx_dependency)):
         
        # Resolve the correct name.
        if __package.lower() == "perl":
            package_name = "Perl"
        elif __package.lower() == "latex":
            package_name = "MikTeX"
        elif __package.lower() == "pandoc":
            package_name = "Pandoc"
        elif __package.lower() == "chocolatey":
            # For now, this is the last installation procedure - the process is terminated afterwards.
            if not Utility.GetExecutable("choco") and not os.path.exists(os.path.join(Build.__path__[0],"bin",__package)):
                
                # Print an informational message
                print('==================================')
                print('%s is required for the current process, but is' % __package.upper())
                print('not found on your machine.')
                print('Installing dependency. This might take a while.. ')    
                print('==================================')   
                
                # Install a full portable version of MSYS2 with MINGW64
                __pyx_ps_delimn = " "; __pyx_package = os.path.join(Build.__path__[0],"bin",__package.lower()); 
                Utility.Popen(["powershell.exe", __pyx_ps_delimn.join([os.path.join(Build.__path__[0],"config","stm_choco.ps1"),__pyx_package])], verbosity=2, shell=False);            
            continue
        else:
            raise NotImplementedError
 
        # Set some temporary variables for path manipulations.
        __pyx_url_delimn = "/"; __pyx_point = "."; __pyx_space = " ";
        __pyx_package_url = __pyx_url_delimn.join(["https:","","jenkins.fa-services.intra.dlr.de","job","STM_Archive","lastSuccessfulBuild","artifact","Archive", __pyx_point.join([package_name, "zip"])])
         
        # Download a ZIP archive and store its content temporarily in the user's download folder.
        __pyx_zip_file = __pyx_package_url.rsplit(__pyx_url_delimn, 1)[-1].lower()
        __pyx_package = os.path.join(Build.__path__[0],"bin",__pyx_zip_file.split(".")[0])
        __pyx_source = __pyx_zip_file.split(".")[0]
        
        # Create a file handler
        devnull = open(os.devnull, 'w')
        atexit.register(devnull.close)
         
        try:    
            # Check if dependency can be executed on the current machine.
            subprocess.check_call([__package.lower(), "--help"], stdout=devnull, stderr=subprocess.STDOUT)
        except OSError:
            # Executable not found. Attempt installation from archive
            if __debug__ and not os.path.exists(__pyx_package):    
                 
                # Attempt remote installation from STM Archive.
                print('==================================')
                print('%s is required for the current process, but is' % __package.upper())
                print('not found on your machine.')
                print('Fetching portable installation from STM archive. ')    
                print('==================================')      
                 
                # Download a ZIP archive and store its content temporarily in the user's download folder.
                download_path = os.path.join(os.path.expanduser('~/Downloads'), __pyx_zip_file)
                urllib.request.urlretrieve(__pyx_package_url, download_path)
                 
                # Extract archive into binary folder
                with zipfile.ZipFile(download_path, 'r') as zip_folder:
                    zip_folder.extractall(__pyx_package)
                 
                # Add Latex templates
                if __package.lower() == "latex":
                    import git
                    __url_delimn = "/"; __git_server_access = "gitlab.dlr.de"
                     
                    # Install DLR specific Latex templates into MikTex distribution
                    __templates_package = os.path.join(__pyx_package,"user","RM_LaTeX")
                    __templates_repo = __url_delimn.join(["https:","",__git_server_access,"innersource","latex-templates.git"])
                     
                    # Only if the path does not already exists
                    if not os.path.exists(__templates_package): 
                        print("==================================")    
                        print("Installing %s from GIT repository" % "DLR LaTeX")
                        print("==================================")    
                        # Local variable
                        master="master"; 
                        if not os.path.exists(os.path.dirname(__templates_package)):
                            os.mkdir(os.path.dirname(__templates_package))
                        # Clone LaTeX templates repository
                        g = git.Repo.clone_from(__templates_repo, __templates_package) #@UndefinedVariable
                        # Switch to local master branch
                        g.git.switch(master)
                     
                # Print success message.
                print('==================================')
                print('Successfully installed %s' % __package.upper())    
                print('==================================')      
             
                # Remove temporary download path
                os.remove(download_path)
        finally:
             
            # Package exists on the current machine or was installed.
            if os.path.exists(__pyx_package):
                pathlist = list([])
                # Add portable PERL distribution to overall path
                if os.path.exists(os.path.join(__pyx_package,__pyx_source,"site","bin")):
                    pathlist.extend([os.path.join(__pyx_package,__pyx_source,"site","bin"),os.path.join(__pyx_package,__pyx_source,"bin"),os.path.join(__pyx_package,"c","bin")])
                # Add portable LATEX distribution (MikTeX) to overall path
                elif os.path.exists(os.path.join(__pyx_package,"texmfs","install",__pyx_source,"bin","x64")):
                    pathlist.append(os.path.join(__pyx_package,"texmfs","install",__pyx_source,"bin","x64"))
                # Add portable PANDOC distribution to overall path
                else:
                    pathlist.append(__pyx_package)
                # Modify the current path variable
                os.environ["PATH"] += os.pathsep + os.pathsep.join(pathlist)
             
            # Run command to check validity of the installation
            assert Utility.Popen(__pyx_space.join([__package,"--help"]),0).returncode == 0

# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %                                                                              Execute install script                                                                                             %
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
if __name__ == '__main__':
    main(); 
