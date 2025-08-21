# -*- coding: utf-8 -*-
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %                                                                                              Installation                                                                                             %
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
"""
Set up environment for installation procedure of all minimum working example scripts 
for PyXMake
 
@note: PyXMake environment file.
Created on 26.03.2021    

@version:  1.0    
----------------------------------------------------------------------------------------------
@requires:
       - 

@change: 
       -    
   
@author: garb_ma                                                     [DLR-FA,STM Braunschweig]
----------------------------------------------------------------------------------------------
"""

## @package PyXMake.VTL.__install__
# Install minimum working example scripts from PyXMake
## @author 
# Marc Garbade
## @date
#  26.03.2021
## @par Notes/Changes
# - Added documentation // mg  26.03.2021

import os, sys
import glob

def main():
    """
    Main function to execute the script. 
    """  
    def GetFromSVN():
        """
        Install scripts from predefined SVN repository.
        """
        __package = "examples"
        __delimn = " "; __url_delimn = "/"
        __scripts_package = os.path.join(os.path.dirname(os.path.abspath(__file__)),__package)
        if not os.path.exists(__scripts_package) or not os.listdir(__scripts_package): 
            print("==================================")    
            print("Installing minimum working examples")
            print("==================================")    
            __svn_repo = __url_delimn.join(["https:","","svn.dlr.de","STM-Routines","Tools_Utilities","PyXMake","trunk","minExample"])
            os.system(__delimn.join(['svn', '--non-interactive', 'checkout', '--depth files', __svn_repo,__scripts_package]))
        # Return success
        return 0
        
    def GetFromGIT():
        """
        Install scripts from predefined GIT repository.
        """
        # Avoid conflicting imports
        try: sys.path.remove(os.path.dirname(os.path.abspath(__file__)))
        except: import git #@UnusedImport
        else: 
            import git #@Reimport
            sys.path.insert(0,os.path.abspath(__file__))
        finally: pass
        # Procedure
        __package = "examples"
        __delimn = " "; __url_delimn = "/"
        __scripts_package = os.path.join(os.path.dirname(os.path.abspath(__file__)),__package)
        # Fetch script directory
        if not os.path.exists(__scripts_package) or not os.listdir(__scripts_package): 
            print("==================================")    
            print("Installing minimum working examples")
            print("==================================")    
            __git_server_access = "gitlab.dlr.de"
            __git_repo = __url_delimn.join(["https:","",__git_server_access,"fa_sw","stmlab","PyXMake"+".git"])
            git.Repo.clone_from(__git_repo, __scripts_package, single_branch=True, b="pyx_examples") #@UndefinedVariable
        # Additionally fetch documentation if not existing
        __doc_package = os.path.join(os.path.dirname(__scripts_package),"doc")
        if not os.path.exists(__doc_package) or not os.listdir(__doc_package): 
            print("==================================")    
            print("Installing documentation")
            print("==================================")    
            __git_server_access = "gitlab.dlr.de"
            __git_repo = __url_delimn.join(["https:","",__git_server_access,"fa_sw","stmlab","PyXMake"+".git"])
            git.Repo.clone_from(__git_repo, __doc_package, single_branch=True, b="pyx_docs") #@UndefinedVariable
        # Return success
        return 0

    ## Get examples files from GIT or SVN (GIT priority)    
    try: GetFromGIT()
    except: GetFromSVN()

    currentdir = os.getcwd()
    os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)),"examples"))
    symlinks = [(os.path.join(os.path.dirname(os.path.abspath(__file__)),"examples",x),
                          os.path.join(os.path.dirname(os.path.abspath(__file__)),x.replace("pyx_",""))) 
                          for x in glob.glob('pyx_*.py')]; os.chdir(currentdir)
    
    # Create a hard link on the current system (this privilege is always active)
    for pair in symlinks: 
        if not os.path.exists(pair[-1]): os.link(pair[0],pair[1])
        
    # Return success
    return 0
                      
if __name__ == "__main__":
    main(); sys.exit()