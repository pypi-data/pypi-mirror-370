# -*- coding: utf-8 -*-
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %                                                         PyXMake - Build environment for PyXMake                                                                            %
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
"""
Triple-use minimum working example for PyXMake. 
Technically, this script runs w/o PyXMake, but the default pipeline refers to the project.

@note: Execute a docker command via the Portainer API remotely from any system.

@version:  1.0    
----------------------------------------------------------------------------------------------
@requires:
       - Portainer X-API-Token
       
@date:
       - 16.01.2021
   
@author: garb_ma                                      [DLR-FA,STM Braunschweig]
----------------------------------------------------------------------------------------------
"""
import os
import sys
import posixpath

def main(token=None, **kwargs):
    """
    Main function to execute the script.
    """
    result = []
    ## Add additional path to environment variable
    if os.path.exists(os.path.join(sys.prefix,"conda-meta")) and not os.path.join(sys.prefix,"conda-meta") in os.getenv("PATH",""): 
        os.environ["PATH"] = os.pathsep.join([os.path.join(sys.prefix,"Library","bin"),os.getenv("PATH","")])      
    # Now the requests module can be load w/o errors.
    import requests

    # Fetch default API path
    try: 
        from PyCODAC.API.Remote import Server
        api_base_url = Server.base_url
    except: api_base_url = "https://portainer.nimbus.dlr.de/api"    
    finally:
        api_portainer_url = posixpath.join(kwargs.get("base_url",api_base_url))
        api_header = {'X-API-KEY': token}
    
    # Raise an error if no token was given.
    if not token: raise ValueError
    
    # Return all default values.
    if kwargs.get("datacheck",False): return [api_portainer_url, api_header]
    
    try: 
        ## Support both new and legacy API endpoints
        endpoint = posixpath.join(api_portainer_url,"users")
        if not requests.get(endpoint, headers=api_header).status_code == 200: 
            endpoint = posixpath.join(api_portainer_url,"users","me")
            result = [requests.get(endpoint, headers=api_header).json()]
        else:
            # These are all predefined calls
            result = [x for x in requests.get(endpoint, headers=api_header).json() 
                      if requests.get(posixpath.join(endpoint,str(x["Id"]),"tokens"), headers=api_header).status_code == 200]

    except TypeError: result = "The token is invalid."
    except: pass
    
    ## Return the result. This should be always a list or an empty list 
    # if something went wrong.
    return result
    
if __name__ == "__main__":
    main(); sys.exit()