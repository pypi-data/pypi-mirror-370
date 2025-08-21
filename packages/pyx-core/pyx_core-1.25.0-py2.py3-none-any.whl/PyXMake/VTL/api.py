# -*- coding: utf-8 -*-
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %                                                         PyXMake - API setup environment for PyXMake                                                                  %
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
"""
API setup example for PyXMake.
 
@note: Run HTML APIs of PyXMake (in a Docker container or locally).
Created on 28.02.2020    

@version:  1.0    
----------------------------------------------------------------------------------------------
@requires:
       - PyXMake

@change: 
       -    
   
@author: garb_ma                                                                          [DLR-SY,STM Braunschweig]
----------------------------------------------------------------------------------------------
"""
import os, sys
import posixpath
import platform

try:
    import PyXMake
except ImportError:
    # Script is executed as a plug-in
    sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    import PyXMake
finally:
    from PyXMake.API import Frontend #@UnresolvedImport

def main(
    handle, 
    # Host route and port information
    Hostname=str(platform.node()), PortID=8020,
    # Additional keyword arguments
    **kwargs):
    """
    Main function to execute an API handle
    """
    # Local import of all required packages
    import uvicorn
    
    from PyXMake.Build.Make import Coverage
    
    # Test if the API can be created. This does not test all functions.
    if Coverage.show() or kwargs.get("dry_run",False):
        # Backwards compatibility. TestClient requires non-default additional packages
        from fastapi.testclient import TestClient
        # Run the server in a test environment
        client = TestClient(handle())
        # Test if API can be reached
        assert client.get(posixpath.sep).status_code == 200
        # Finish
        print("==================================")    
        print("Finished running API check")
        print("==================================")
        # Return success code
        return 0
    # Execute API directly
    else: 
        # Run the supplied API
        uvicorn.run(handle(), host=Hostname, port=PortID)
        # Will run forever until quit by the user
    pass
    
def handle():
    """
    Return current API's main instance as an sub API.
    """
    API = Frontend()
    API.RedirectException(posixpath.sep.join(["",str(PyXMake.__name__),"api","documentation"]))
    return API.create()
    
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %                                                                         Access command line inputs                                                                                   %
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% 
if __name__ == '__main__':
    """
    API is initialized and run.
    """
    # Execute run command   
    main(handle); sys.exit()    