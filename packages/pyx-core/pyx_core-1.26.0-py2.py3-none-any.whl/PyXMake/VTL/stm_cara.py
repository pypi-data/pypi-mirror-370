# -*- coding: utf-8 -*-
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %                                                             PyXMake - Build environment for PyXMake                                                                      %
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
"""
Install latest STM software on DLR's HPC cluster (CARA).

@note: Requires GitLab access
Created on 21.07.2020

@version:  1.0    
----------------------------------------------------------------------------------------------
@requires:
       - 

@change: 
       -    
   
@author: garb_ma                                                     [DLR-FA,STM Braunschweig]
----------------------------------------------------------------------------------------------
"""
import os
import sys
import argparse
import posixpath
import getpass
import tempfile

try: 
    from urllib import quote_plus #@UnresolvedImport @UnusedImport
except: 
    from urllib.parse import quote_plus #@Reimport

try:
    import PyXMake as _ #@UnusedImport
except ImportError:
    # Script is executed as a plug-in
    sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
finally:
    from PyXMake.Build import Make
    from PyXMake.Tools import Utility

# Predefined script local variables
__delimn = ":"
__user =  os.getenv("username")

def main(user, key="", password="", verbosity=0, **kwargs):
    """
    Main function to execute the script.
    Install STM software in the user's workspace on CARA. Installs all packages.
    """
    # Check if GIT credentials differ from user credentials (using access token)
    access = kwargs.get("auth",""); directory = kwargs.get("directory","")
    if not access: access = __delimn.join([user, getpass.getpass()])
    if access and __delimn in access: 
        access = __delimn.join([access.split(__delimn)[0],quote_plus(access.split(__delimn)[-1])]) + "@"
    scratch = str(next(tempfile._get_candidate_names()))
    # Create install command
    command = "git clone --single-branch --recursive --branch pyx_service https://%sgitlab.dlr.de/fa_sw/stmlab/PyXMake.git %s; cd %s && \
                            chmod u+x stm_cara_software.sh && echo '\nrm -rf ../%s' >> stm_cara_software.sh && \
                            sbatch stm_cara_software.sh --internal=true --user='%s' --token='%s' --directory='%s' --package='%s' --refresh='%s'" % (access, scratch,
                            scratch, scratch, access.split(__delimn)[0], access.split(__delimn)[-1].replace("@",""), 
                            directory or posixpath.join(Utility.AsDrive("home", posixpath.sep),user,"software"), kwargs.get("feature","all"), str(kwargs.get("refresh","false")))
    # Replace part of command when interactive mode is requested.
    if kwargs.get("interactive",False): command = command.replace("sbatch","srun")
    # Establish SSH class
    SSHBuild = Make.SSH("cara", [], verbose=verbosity)
    # Set output paths to empty strings
    SSHBuild.OutputPath("")
    # Run a custom command
    SSHBuild.Build(command, run="custom")
    # Establish connection with key or password.
    SSHBuild.Settings(user, key, password=password, host="cara.dlr.de", use_cache=False)
    SSHBuild.create(tty=True, collect=False)

if __name__ == "__main__":
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %                                                                         Access command line inputs                                                                  %
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    parser = argparse.ArgumentParser(description="Install supported STM software in the user's workspace on CARA.")
    parser.add_argument("user", metavar="user", nargs=1, help="Current user for SSH connection")
    parser.add_argument("password", metavar="password", nargs=1, help="Password of current user")
    parser.add_argument("--access", metavar="access", nargs=1, help="Access token for GitLab in format <Token>:<Value>")
    parser.add_argument("--directory", metavar="directory", nargs=1, help="Installation directory (absolute path). Defaults to user workspace.")
    parser.add_argument("--feature", metavar="feature", nargs=1, help="Name of the package to install. Defaults to all.")
    parser.add_argument("--refresh", metavar="refresh", nargs=1, help="Reinstall the given package if already present. Defaults to False.")
    parser.add_argument("--interactive", metavar="interactive", type=Utility.GetBoolean, const=True, default=False, nargs='?', help="Select whether the installation runs interactively.")
    
    try:
        _ = sys.argv[1]
        args, _ = parser.parse_known_args()
    except:
        pass
  
    try:
        # SSH connection information
        user = args.user[0]; key = "";
        password  = args.password[0]
        # Optional non-default GitLab credentials
        try: access = args.access[0]
        except: access = __delimn.join([user,password])
        # Optional non-default installation directory
        try: directory = args.directory[0]
        except: directory = posixpath.join(Utility.AsDrive("home", posixpath.sep),user,"software")
        # Optional non-default package request
        try: feature = args.feature[0]
        except: feature = "all"
        # Optional refresh package request
        try: refresh = args.refresh[0]
        except: refresh = False
        # Optional non-default package request
        try: interactive = args.interactive[0]
        except: interactive = False
    except:
        # Default settings. Applicable for most users.
        user = __user; password = ""; access = ""; directory=""; feature="all"; refresh = False; interactive=False
        key = os.path.join(Utility.AsDrive("C"),"Users",user,"Keys","Putty","id_rsa")
    finally:
        # Run install script
        main(user, key, password, auth=access, directory=directory, feature=feature, interactive=interactive, refresh=refresh)
        # Finish
        print("==================================")    
        print("Finished")
        print("==================================")    
        sys.exit()