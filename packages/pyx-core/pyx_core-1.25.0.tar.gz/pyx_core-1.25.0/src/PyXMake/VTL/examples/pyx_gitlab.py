# -*- coding: utf-8 -*-
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %                                                         PyXMake - Build environment for PyXMake                                                                            %
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
"""
Triple-use minimum working example for PyXMake. 
Technically, this script runs w/o PyXMake, but the default pipeline refers to the project..

@note: Execute a GitLab pipeline or a given pipeline job remotely w/o non-default packages.

@version:  1.0    
----------------------------------------------------------------------------------------------
@requires:
       - GitLab X-API-Token
       
@date:
       - 12.01.2021
   
@author: garb_ma                                      [DLR-FA,STM Braunschweig]
----------------------------------------------------------------------------------------------
"""
import time
import sys
import os
import re
import copy
import getpass
import posixpath

try:
    import PyXMake as _ #@UnusedImport
except ImportError:
    # Script is executed as a plug-in
    sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
finally:
    from PyXMake.Tools import Utility
    from PyXMake.Plugin.__gitlab import main, housekeeping, release #@UnusedImport
    
def datacheck(**kwargs):
    """
    Return the given input data
    """
    ## Add additional path to environment variable
    if os.path.exists(os.path.join(sys.prefix,"conda-meta")) and os.path.join(sys.prefix,"Library","bin") not in os.getenv("PATH",""): 
        os.environ["PATH"] = os.pathsep.join([os.path.join(sys.prefix,"Library","bin"),os.getenv("PATH","")])

    # Definition of the header
    if not kwargs.get("token",None): raise ValueError
    auth = {"PRIVATE-TOKEN": kwargs.get("token")}
    
    # Definition of the GitLab project ID (an integer number) and the API v4 URL 
    api_v4_url = kwargs.get("base_url","https://gitlab.dlr.de/api/v4")
    
    # Return all default values.
    return [api_v4_url, auth]

def download(package=None, projectid=None, version=".", **kwargs):
    """
    Download all resources for a package from the default registry
    """
    # Return all default values and initialize path if required
    if kwargs.get("datacheck",False): return datacheck(**kwargs)
    else: base_url, auth = datacheck(**kwargs)
    
    # Now the requests module can be load w/o errors.
    import requests
    
    # Use HTML parser
    from bs4 import BeautifulSoup
    
    # Compatibility with CLI parser
    if not projectid: projectid = kwargs.get("identifier",None)
    
    # This function cannot be executed w/o a package a project id
    if not package or not projectid: raise ValueError
    
    # Add project ID to base API URL
    api_v4_url = posixpath.join(base_url,"projects",projectid)
    r = requests.get(posixpath.join(api_v4_url,"packages","pypi","simple",package),headers=auth);
    
    # Set the output path. Defaults to the current working directory
    path = os.path.abspath(kwargs.get("output",os.getcwd()))
    # Create full output path
    os.makedirs(path, exist_ok=True)
    
    # Collect all entries for the given versions. Defaults to all.
    data = [x["href"] for x in BeautifulSoup(r.text,'html.parser').find_all('a', {'href': re.compile(api_v4_url)}) if version in x["href"]]
    
    # Download all files into the changed and or created directory
    with Utility.ChangedWorkingDirectory(path):
        for url in data: 
            with requests.get(url, stream=True, headers=auth) as r:
                r.raise_for_status()
                file_name = Utility.PathLeaf(url.split("#")[0])
                with open(file_name, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192): 
                        if chunk: f.write(chunk)

    # Return success by presenting a list of all files
    return os.listdir(path)

def pipeline(token=None, projectid=str(12702), **kwargs):
    """
    Main function to execute the script if main cannot be imported. 
    Otherwise, run a named pipeline for a given project with the given credentials.
    Defaults to running a remote install script on CARA.
    """
    # Return all default values and initialize path if required
    settings = copy.deepcopy(kwargs); settings.update({"token":token})
    if kwargs.get("datacheck",False): return datacheck(**settings)
    else: base_url, auth = datacheck(**settings)
    
    # Now the requests module can be load w/o errors.
    import requests
    
    # Add project ID to base API url
    api_v4_url = posixpath.join(base_url,"projects",projectid)
    
    # Definition of CI job and the branch of the corresponding CI script 
    job = kwargs.get("job_name",None)
    data= {"ref": kwargs.get("branch", "master")}
    variables = kwargs.get("api_variables",{})
    
    # Additional variables parsed to the CI job. Meaningful default values are only set for auto-installation of software on CARA.
    if job and job in ["stm_cara"]: 
        ## The default installation directory is the current user's home directory. This is only a meaningful 
        # default value if job refers to a CARA build requests
        cara_login_user = kwargs.get("cara_login_user",getpass.getuser())
        cara_login_credentials = kwargs.get("cara_login_credentials", getpass.getpass())
        install_directory = kwargs.get("cara_install_directory",posixpath.join("/home",cara_login_user,"software"))
        variables = kwargs.get("api_variables",
                            {"USER":cara_login_user,"CREDENTIALS":cara_login_credentials, "directory":install_directory,"feature":kwargs.get("package","all")})
    query = "&".join(["variables[][key]="+str(x)+"&variables[][value]="+str(y) for x, y in variables.items()])
    
    # Create a new dummy pipeline with the corresponding job. Terminate the pipeline immediately, since only one job is of interest.
    r = requests.post(api_v4_url+"/pipeline?"+query, data=data, headers=auth); 
    
    # Only meaningful if one job is requested in particular.
    if job: 
        ## If a specific job is given, create a new pipeline and run only this job. 
        # Remove the pipeline afterwards by default. Requires owner credentials.
        r = requests.post(api_v4_url+"/pipelines/%s/cancel" %  r.json()["id"], headers=auth)
        r = requests.get(api_v4_url+"/jobs", headers=auth)
        r = requests.post(api_v4_url+"/jobs/%s/play" % [x for x in r.json() if x["name"] in [job]][0]["id"], headers=auth)
        r = requests.get(api_v4_url+"/jobs", headers=auth)
        
        # Get the job ID of the running job
        JobID = [x for x in r.json() if x["name"] in [job]][0]["id"]
        while True:
            r = requests.get(api_v4_url+"/jobs/%s" % JobID, headers=auth)
            # Check status. Either return immediately or wait for job completion
            if r.json()["status"] in ["pending", "running"] and False: break
            if r.json()["status"] in ["success", "failure"]: 
                PipeID = requests.get(api_v4_url+"/jobs/%s" % r.json()["id"], headers=auth).json()["pipeline"]["id"]; 
                r = requests.get(api_v4_url+"/jobs/%s/trace" % r.json()["id"], headers=auth); 
                break
            time.sleep(2)
        ## Attempt to delete the pipeline. This is only successful when pipeline succeeded or failed.
        # Requires owner credentials.
        try: requests.delete(api_v4_url+"/pipelines/%s" % PipeID, headers=auth)
        except: pass
    
    # Obtain detailed information
    try: result = r.json()
    except: result = {"status_code":r.status_code,"content":r.text}
    
    # Return final result code and response
    return result

# Use default project function as main when import fails
if not hasattr(sys.modules[__name__], "main"): 
    __settings = {}
    setattr(sys.modules[__name__], "main", pipeline)
else: __settings = {"register":{"datacheck":datacheck,"pipeline":pipeline,"download":download}}
    
if __name__ == "__main__":
    main(**__settings); sys.exit()