# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#                                                                                         PyXMake                                                                                            %
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
"""
PyXMake is a cross-plattform build tool for source files using either Intel Fortran, 
Py2X, a SSH connection or Doxygen to build a library or to automatically create a 
documentation.
 
@note: PyXMake.__init__()          
Created on 20.03.2018    

@version: 1.0    
----------------------------------------------------------------------------------------------
@requires:
       - 

@change: 
       -    
   
@contributors: 
       Falk Heinecke
       Sebastian Freund
       Andreas Schuster
                           
@author: garb_ma                                                     [DLR-FA,STM Braunschweig]
----------------------------------------------------------------------------------------------
"""

## @package PyXMake 
# PyXMake package for programmable build events on Linux and Windows. 
## @authors 
# Marc Garbade,
# Falk Heinecke,
# Sebastian Freund,
# Andreas Schuster
## @date
# 20.03.2018
## @par Notes/Changes
# - Added documentation // mg 29.03.2018

import os,sys,site
import subprocess
import itertools

try: 
    import importlib.util
    from importlib.util import spec_from_file_location as load_source
except: 
    from imp import load_source #@Reimport

## Provide canonical version identifiers
__version__ = "1.27.0"
__version_info__ = tuple(map(lambda n: int(n) if n.isdigit() else n,__version__.split(".")))

## Absolute system path to PyXMake.
PyXMakePath = os.path.dirname(os.path.abspath(__file__))

## Get the current project name
__project__ = os.path.basename(os.path.normpath(PyXMakePath))

## Define all wild imports
__all__ = [".".join([__project__,x]) for x in ("Plugin","VTL")]

## Add additional path to environment variable
if os.path.exists(os.path.join(sys.prefix,"conda-meta")) and not os.path.join(sys.prefix,"Library","bin") in os.getenv("PATH",""): # pragma: no cover
    os.environ["PATH"] = os.pathsep.join([os.path.join(sys.prefix,"Library","bin"),os.getenv("PATH","")])

## Detect CLI mode and set frozen state accordingly
if sys.stdin and sys.stdin.isatty(): setattr(sys, "frozen", getattr(sys, "frozen", sys.stdin and sys.stdin.isatty()))

## Silently install all dependencies during initial startup
if (not os.path.exists(os.path.join(PyXMakePath,"VTL","examples")) or 
    not os.listdir(os.path.join(PyXMakePath,"VTL","examples")) or 
    not os.path.exists(os.path.join(PyXMakePath,"VTL","examples","abaqus.py"))) and not getattr(sys, 'frozen', False):  
    subprocess.check_call([sys.executable,os.path.join(PyXMakePath,"__setenv__.py"), os.path.join(PyXMakePath,"VTL","__install__.py")])

## Backwards compatibility patch for process with activate poetry instance. 
# poetry uses its own version of typing extensions, even though the underlying system provides one.
# This recipe will attempt to fix the issue by attempting to load the unsupported version first and 
# if this is successful - delete the module and reload the system one.
if sys.version_info[0] >= 3:
    # Attempt to import poetry. If poetry is not found, do nothing
    try: from poetry.core._vendor import typing_extensions as _  #@UnresolvedImport #@UnusedImport
    except ImportError: pass
    else: # pragma: no cover
        # We have an active poetry instance within the environment. Check version of typing
        try: from typing_extensions import TypeAliasType as _ #@UnresolvedImport @UnusedImport @Reimport
        except ImportError:
            # Local import definition
            import copy
            # Create a local copy of system path
            sys_path_backup = copy.deepcopy(sys.path)
            try: 
                # Delete wrong module from system path
                del sys.modules["typing_extensions"]
                # Reorder all elements and remove all references to poetry's vendor path
                sys.path = [x for x in sorted(set(sys_path_backup), key=lambda x: 'site-packages' in x) if not x.endswith("_vendor")]
                # Verify that all import definitions work from here on
                from typing_extensions import TypeAliasType as _#@UnresolvedImport @UnusedImport @Reimport
                from pydantic import BaseModel as _ #@UnusedImport @Reimport
            except: pass
            # Reset local system path
            finally: sys.path = sys_path_backup
        else: pass

## Register development extension (if installed)
if not any(path in sys.modules for path in __all__) and not getattr(sys, "frozen",False):
    for modname, sitedir in list(itertools.product(__all__,sorted(set(site.getsitepackages()+sys.path)))):
        try:
            # Only execute valid files. Skip all others.
            expression = 'os.path.join(sitedir,*modname.split("."),"__init__.py")'
            candidate = eval('lambda: ' + expression); candidate = candidate()
            if not os.path.exists(candidate): continue
            # Load the given source into current instance
            expression = 'load_source(modname, os.path.join(sitedir,*modname.split("."),"__init__.py"))'
            spec = eval('lambda: ' + expression); spec = spec()
            # In later releases, module specification and loading is split.
            module = importlib.util.module_from_spec(spec)
            sys.modules[modname] = module
            spec.loader.exec_module(module)
        except: continue
else: pass

## Provide an alias for the VTL module for forwards compatibility
# Fail gracefully for now
try: from . import VTL as Command
except: pass

if __name__ == '__main__':
    pass