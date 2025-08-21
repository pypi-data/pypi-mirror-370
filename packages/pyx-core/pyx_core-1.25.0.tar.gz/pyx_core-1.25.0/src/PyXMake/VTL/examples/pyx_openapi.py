# -*- coding: utf-8 -*-
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %                                                         PyXMake - Build environment for PyXMake                                                         %
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
"""
Triple-use minimum working example for PyXMake. This script can be
executed in three different ways in varying levels of accessibility
 
@note: Create a Python package from an OpenAPI specification. Optionally, create a 
portable installer instead. 

Created on 21.10.2022    

@version:  1.0    
----------------------------------------------------------------------------------------------
@requires:
       - PyXMake
   
@author: garb_ma                                      [DLR-FA,STM Braunschweig]
----------------------------------------------------------------------------------------------
"""
import os, sys
import shutil
import argparse
import zipfile
import time
import subprocess
import posixpath

try:
    import PyXMake as _ #@UnusedImport
except ImportError:
    # Script is executed as a plug-in
    sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
finally:
    import PyXMake
    from PyXMake.Tools import Utility #@UnresolvedImport
    from PyXMake.Build.Make import AllowDefaultMakeOption
    
try:
    # Import PyCODAC to build library locally during setup.
    import PyCODAC   
except ImportError: pass

def main(
    BuildID, 
    # URL to API specification
    source="https://stmlab.fa-services.intra.dlr.de/2/openapi.json",
    # Define output path
    output=None,
    # Additional keyword arguments
    **kwargs):
    """
    Main function to execute the script.
    """
    # Refer to requests here to avoid conda mangling
    import requests
    # Definition of local variables
    delimn = "."; result = -1; repeat = 0; client = kwargs.get("client","python")
    # Default OpenAPI URL refers to modified version running on FA.
    url = posixpath.join(kwargs.get("base_url","https://stmlab.fa-services.intra.dlr.de/2/PyXMake/api/client/zip"))
    # Default output directory refers to current directory if not given.
    if not output: output=os.getcwd()
    # Assembly of request query structure. Only python generator is currently supported
    data = {"URI":source,"ClientID": client,
                  "CLI": ["--skip-validate-spec",
                              "--additional-properties=packageName=%s" % str(BuildID), 
                              "--additional-properties=packageVersion=%s" % str(kwargs.get("version","1.0.0")),
                              "--additional-properties=packageUrl=%s" % posixpath.dirname(source)]}
    # Definition of output filename. Defaults to project name followed by default file extension.
    filename = kwargs.get("filename",delimn.join([BuildID,kwargs.get("ext",posixpath.basename(url))]))
    # Check if the URL can be reached. Raise an error if that is not the case.
    try: 
        if not requests.head(url).ok: raise ValueError
    except: raise ConnectionError("The given url cannot be reached: %s" % str(url))

    # Fail gracefully
    try: 
        # Attempt to send a patch request and download the result. The result is an archive.
        with Utility.TemporaryDirectory() as _, requests.patch(url, params=data, stream=True) as r:
            r.raise_for_status()
            with open(filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):  f.write(chunk)
            # Return compiled Python wheels. Defaults to False. 
            if kwargs.get("build",False):
                # Extract the archive
                with zipfile.ZipFile(filename, 'r') as zip_ref: zip_ref.extractall()
                with Utility.ChangedWorkingDirectory(os.path.join(os.path.abspath(os.getcwd()),client)):
                    # Execute build command
                    subprocess.check_call([sys.executable,"-m","build"]);
                # Recreate the archive
                Utility.CreateArchive(filename, os.path.join(os.path.abspath(os.getcwd()),client,"dist"))
            # We have an result file. Copy it to the current output directory
            if os.listdir(os.getcwd()): 
                while True:
                    try: 
                        # Attempt to copy all result files
                        shutil.copy(filename, output); break
                    except:
                        # Catch potential race condition
                        repeat += 1;
                        # If no success after three attempts. throw an error.
                        if repeat >= 3: break;
                        else: time.sleep(2);
        # Everything worked
        result = 0
    # Something went terribly wrong...
    except ImportError: pass
    # Present the outcome.
    return result
    
if __name__ == "__main__":
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %                                                                         Access command line inputs                                                                  %
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    parser = argparse.ArgumentParser(description='CLI wrapper options for  OpenAPI client generator.')
    parser.add_argument('name', type=str, nargs=1, help="Name of the project")
    parser.add_argument('source', type=str, nargs=1, help="URL to an OpenAPI specification")
    parser.add_argument('--version', type=str, nargs=1, help="Version used during package creation. Defaults to 1.0.0")
    parser.add_argument("--output", type=str, nargs=1, help="Absolute path to output directory. Defaults to current project folder.")
    parser.add_argument("--file", type=str, nargs=1, help="Output file name. Defaults to Name.zip")
    parser.add_argument("--build", type=Utility.GetBoolean, const=True, default=True, nargs='?', 
        help="Check public PyPi repository to verify the results. Defaults to True.")
    
    # Command line separator
    delimn = "."
    
    try:
        # Check CLI options
        _ = sys.argv[1]
        args, _ = parser.parse_known_args()  
        # Project name is mandatory
        project = args.name[0]
        # Specification is mandatory
        source = args.source[0] ; 
        # Optional non-default version
        try: version = args.version[0]
        except: version = "1.0.0"
        # Optional non-default output directory
        try: output = args.output[0]
        except: output = os.path.abspath(os.getcwd())
        # Optional non-default build command. Defaults to True
        try: build = args.build[0]
        except: build = True
        # Optional non-default output filename
        try: filename = args.file[0]
        except: filename = delimn.join([project,"zip"])
        
    # Use an exception to allow help message to be printed.
    except Exception as _:
        # Run default test coverage of all integrated projects.
        if AllowDefaultMakeOption:                       
            try: 
                # Build an API client for PyCODAC
                main("pyc_client", source="https://stmlab.fa-services.intra.dlr.de/1/openapi.json", output=os.getcwd(), version=PyCODAC.__version__, build=True)
            except: pass # Fail gracefully
            # Build API client for PyXMake.
            main("pyx_client", source="https://stmlab.fa-services.intra.dlr.de/2/openapi.json", output=os.getcwd(), version=PyXMake.__version__, build=True)
    else:
        # Execute valid CLI command
        main(project, source, output, filename=filename, version=version, build=build)
        
    # Finish 
    print("==================================")
    print("Finished building API client")
    print("==================================")        
    sys.exit()