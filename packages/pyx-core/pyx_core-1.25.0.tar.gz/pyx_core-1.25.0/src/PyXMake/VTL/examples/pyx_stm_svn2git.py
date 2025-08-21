# -*- coding: utf-8 -*-
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %                                                             PyXMake - Build environment for PyXMake                                                                      %
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
"""
Translate a given SVN repository to a GIT repository.

@version:  1.0    
----------------------------------------------------------------------------------------------
@requires:
       - 

@change: 
       -    
   
@author: garb_ma                                                     [DLR-FA,STM Braunschweig]
----------------------------------------------------------------------------------------------
"""

import os, sys
import git
import glob
import time
import shlex
import shutil
import argparse
import subprocess
import svn.remote

from PyXMake.Tools import Utility
from PyXMake.VTL import Scratch

__url_delimn = "/"
__svn_repo = "https://svn.dlr.de/STM-Routines"
__git_repo = "stm_routines"

def main(git_repo, svn_repo, output=os.getcwd()):
    """
    Main function to execute the script.
    """     
    # Operate in a full temporary directory
    with Utility.ChangedWorkingDirectory(Scratch):
        # Create a temporary source code folder.
        __temp_path = os.path.join(os.getcwd(),Utility.GetTemporaryFileName(extension=""))
        # Print an informative message
        print("==================================")    
        print("Processing %s" % git_repo.upper())
        print("==================================")    
        svn.remote.RemoteClient(svn_repo).checkout(__temp_path)
        with Utility.ChangedWorkingDirectory(__temp_path):
            # Get current bash executable from local GIT installation
            bash = os.path.join(os.path.dirname(os.path.dirname(Utility.GetExecutable(git.Git.GIT_PYTHON_GIT_EXECUTABLE, get_path=True)[-1])),"bin","bash.exe")
            # Search for all authors who contributed to this path
            command = "svn log -q | awk -F"+" '|' '/^r/ "+'{sub("^ ", "", $2); sub(" $", "", $2); ' + 'print $2" = "$2" <"$2">"}'+"' | sort -u > authors-git.txt"
            with open("authors.sh","w") as script: script.write(command)
            command = " ".join(['"'+bash+'"',"-c","./authors.sh"])
            # Create a bash script to execute a bash command with both types of quotation
            subprocess.Popen(command, shell=True); 
            while True:
                time.sleep(1) # Attempt to rename result. Avoid race condition
                if os.path.exists(os.path.join(os.getcwd(),"authors-git.txt")): 
                    shutil.move(os.path.join(os.getcwd(),"authors-git.txt"),os.path.join(Scratch,"authors-git.txt"))
                    break
        # Again, avoid race condition. If it is still happening, retry again until success.
        while True:
            time.sleep(1)
            try: Utility.DeleteRedundantFolders(__temp_path, ignore_readonly=True); break
            except: pass
        source = os.path.dirname(svn_repo)
        trunk = Utility.PathLeaf(svn_repo)
         
        # Create a new local repository
        g = git.Repo.init(os.path.join(os.getcwd(),git_repo))
        if Utility.GetPlatform() == "windows": g.git.execute("git config --global core.longpaths true")
        
        # Assemble GIT command
        command = "git svn clone "+source+" --no-metadata --no-minimize-url -T "+trunk+" --authors-file="+str(os.path.join('"'+os.getcwd(),"authors-git.txt"+'"'))+" "+"."
        
        # Never surrender to GIT. Wait until the requested repository is non-empty
        while not glob.glob(os.path.join(os.getcwd(),git_repo, '*')):
            try:
                time.sleep(0.2) # Again, avoid race conditions
                g.git.execute(shlex.split(command,posix=not os.name.lower() in ["nt"]))
            except Exception as e:
                # Present exception error
                print(e)
                # Issue a notification
                print("==================================")
                print("This error is deemed non-critical. Ignoring")
                print("==================================")      
                pass
            
        # Delete files with no further use
        Utility.DeleteFilesbyEnding("authors-git.txt")
        if os.getcwd() != output: Utility.MoveIO(git_repo, os.path.join(output,git_repo))
    
if __name__ == '__main__':
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %                                                                         Access command line inputs                                                                                  %
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    parser = argparse.ArgumentParser(description="Translate a given SVN repository to a GIT repository.")
    
    try:
        # Access user command line arguments. Do nothing if not given.
        _ = sys.argv[1]
        args, _ = parser.parse_known_args()
    except:
        pass
  
    try:
        # User input information from command line
        _ = args.user[0]    
    except:    
        # Translate
        main(__git_repo, __svn_repo); 
    else:
        raise NotImplementedError
        
    # Finish translation job
    print("==================================")    
    print("Finished translation")
    print("==================================")    
    sys.exit()