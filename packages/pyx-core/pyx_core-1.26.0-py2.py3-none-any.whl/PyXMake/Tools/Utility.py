# -*- coding: utf-8 -*-
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %                                                                 Utility - Classes and Functions                                                                        %
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
"""
Classes and functions defined for convenience.
 
@note: PyXMake module                   
Created on 15.07.2016    

@version:  1.0    
----------------------------------------------------------------------------------------------
@requires:
       - 

@change: 
       -    
   
@author: garb_ma                                                     [DLR-FA,STM Braunschweig]
----------------------------------------------------------------------------------------------
"""

## @package PyXMake.Tools.Utility
# Module of basic functions.
## @author 
# Marc Garbade
## @date
# 15.07.2017
## @par Notes/Changes
# - Added documentation // mg 29.03.2018

try:
    ## Only meaningful < 3.12
    from future import standard_library
    # Deprecated since 3.12
    standard_library.install_aliases()
except:
    pass

try:
    from builtins import str
    from builtins import object
except ImportError:
    pass

try:
    FileNotFoundError
except NameError:
    FileNotFoundError = IOError # @ReservedAssignment

import sys
import os
import io
import six
import ast
import abc
import site
import json
import shutil
import shlex
import logging
import functools
import subprocess
import platform
import stat
import glob
import time
import struct
import socket
import tarfile
import textwrap
import posixpath, ntpath

import numpy as np
import random as rd
import tempfile
import zipfile
import copy
import urllib

try:
    import cPickle as cp # @UnusedImport
except:
    import pickle as cp # @Reimport

try:
    from contextlib import contextmanager # @UnusedImport
except ImportError:
    from contextlib2 import contextmanager # @Reimport

from types import MethodType
from .. import PyXMakePath

try: 
    from PyXMake.Build import Make
    autotest = Make.Coverage.add
except: 
    def autotest(*args, **kwargs): 
        def decorator(func): return func 
        return decorator

## Create an alias using default logger for all print statements 
logger = logging.getLogger(__name__)
# setattr(sys.modules[__name__],"print", logger.info)

## @class PyXMake.Tools.Utility.AbstractImport
# Inherited from built-in object.
class AbstractImport(object): # pragma: no cover
    """
    Abstract (lazy) import class to construct a module with attribute which is only really loaded into memory when first accessed.
    It defaults to lazy import behavior.
    
    @note: Derived from https://stackoverflow.com/questions/77319516/lazy-import-from-a-module-a-k-a-lazy-evaluation-of-variable
    """
    def __init__(self, *args, **kwargs):
        """
        Low-level initialization of parent class.
        """
        pass
    
    def __new__(cls, name, package=None, **kwargs):
        """
        An approximate implementation of import.
        """
        import importlib
        
        absolute_name = importlib.util.resolve_name(name, package)
        
        try: return sys.modules[absolute_name]
        except KeyError: pass
    
        path = None
        if '.' in absolute_name:
            parent_name, _, child_name = absolute_name.rpartition('.')
            parent_module = importlib.import_module(parent_name)
            path = parent_module.__spec__.submodule_search_locations
        for finder in sys.meta_path:
            spec = finder.find_spec(absolute_name, path)
            if spec is not None:
                break
        else:
            msg = 'No module named %s' % absolute_name
            raise ModuleNotFoundError(msg, name=absolute_name)
        
        if kwargs.get("lazy_import",True):
            loader = importlib.util.LazyLoader(spec.loader)
            spec.loader = loader
        
        module = importlib.util.module_from_spec(spec)
        sys.modules[absolute_name] = module
        spec.loader.exec_module(module)
        
        if path is not None:
            setattr(parent_module, child_name, module)
        return module

## @class PyXMake.Tools.Utility.AbstractBase
# Abstract meta class for all data class objects. Inherited from built-in ABCMeta & object. 
# Compatible with both Python 2.x and 3.x.  
@six.add_metaclass(abc.ABCMeta)
class AbstractBase(object): # pragma: no cover
    """
    Parent class for all abstract base classes.
    """
    @abc.abstractmethod             
    def __init__(self, *args, **kwargs):
        """
        Low-level initialization of parent class.
        """
        pass

    @classmethod
    def __new__(cls, *args, **kwargs):
        """
        Check if the current base is an abstract base. 
        """
        if cls.__bases__[-1].__name__ in [AbstractBase.__name__]: raise TypeError("Can't instantiate abstract base class %s." % cls.__name__)
        try: return super(AbstractBase,cls).__new__(cls)
        ## If any module in PyXMake is reloaded during runtime, simple executing super might fail. 
        # The following line solves this issue.
        except TypeError: return super(ClassWalk(AbstractBase,cls),cls).__new__(cls)
    
    @classmethod
    def recover(cls, *args):
        """
        Recover a derived data class completely from its JSON or dictionary form.
        """
        class Base(object):
            """
            Subclass instance for initialization
            """      
            def __init__(self, _dictionary):
                """
                Initialization of any class instance.                      
                """
                for k,v in _dictionary.items(): setattr(self, k, v)  
        # Read dictionary or JSON string
        dictionary = args[0]
        # Deal with JSON string
        if not isinstance(dictionary,dict): dictionary = RecoverDictionaryfromPickling(json.loads(args[0]))
        # Return a working class
        return type(cls.__name__, (Base, cls), {})(dictionary)
    
    @classmethod
    def classify(cls, *args, **kwargs):
        """
        Serializes an arbitrary data class instantiation call. Returns the complete class as JSON.
        """
        realization = cls(*args)
        if kwargs: # Support "blank" attributes
            for x, y in kwargs.items(): getattr(realization, x)(*y if isinstance(y,list) else y)
        if hasattr(realization,"create"): getattr(realization,"create")()
        return realization.jsonify()

    def jsonify(self):
        """
        Create a JSON representation of the current class
        """
        return self.__str__()
    
    def update(self, **kwargs):
        """
        Update any given class attribute.
        """
        for k,v in kwargs.items(): setattr(self, k, v)
        pass
    
    def __repr__(self):
        """
        Returns a string representation of the current instance.
        """
        return str("%s.%s(%s)") % (type(self).__name__, self.recover.__name__, str(self))
    
    def __str__(self):
        """
        Prepare an object for JSON (2to3 compatible). Returns a canonical data representation of the current instance.
        """
        return json.dumps(self, default=PrepareObjectforPickling)
    
    def __getstate__(self):
        """
        Prepare the object for pickling (2to3 compatible) 
        """
        _dictobj = PrepareObjectforPickling(self)  
        return _dictobj         
    
    def __setstate__(self, _dict):
        """
        Recover a dictionary from pickling (2to3 compatible) 
        """
        _dictobj = RecoverDictionaryfromPickling(_dict)             
        self.__dict__.update(_dictobj)    
        pass
    
    @staticmethod
    def __getbase__(base,cls):
        """
        Recursively find the common ancestor in all bases for a given class and compare them with the supplied base.
        
        @note: Returns None if no common ancestor can be found
        """
        return ClassWalk(base, cls)

## @class PyXMake.Tools.Utility.AbstractMethod
# Class to create 2to3 compatible pickling dictionary. Inherited from built-in object.    
class AbstractMethod(object):
    """
    Abstract method to construct an instance and class method with the same descriptor.
    
    @note: Derived from https://stackoverflow.com/questions/2589690/creating-a-method-that-is-simultaneously-an-instance-and-class-method
    """
    def __init__(self, method):
        """
        Construct an instance method.
        """     
        self.method = method

    def __get__(self, obj=None, objtype=None): # pragma: no cover
        """
        Custom descriptor for this class. Returns method either as class or as an instance.
        """   
        @functools.wraps(self.method)
        def _wrapper(*args, **kwargs):
            """
            A wrapper calling the given method
            """   
            if obj is not None: return self.method(obj, *args, **kwargs)
            else: return self.method(objtype, *args, **kwargs)
        return _wrapper

## @class PyXMake.Tools.Utility.ChangedWorkingDirectory
# Class to create 2to3 compatible pickling dictionary. Inherited from built-in object.
class ChangedWorkingDirectory(object):
    """
    Context manager for temporarily changing the current working directory.
    
    @author: Brian M. Hunt 
    """
    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)
        # Create target directory & all intermediate directories if don't exists
        if not os.path.exists(self.newPath) and self.newPath != os.getcwd():
            print("==================================")
            print("Creating a new scratch folder @: %s" % self.newPath)
            print("This folder will not be deleted once the job is done!")
            print("==================================")
            os.makedirs(self.newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)

## @class PyXMake.Tools.Utility.GetDataFromPickle
# Class to create 2to3 compatible pickling dictionary. Inherited from built-in object.
class GetDataFromPickle(object): # pragma: no cover
    """
    Class to convert an arbitrary pickle file (2.x & 3.x) into a readable 
    dictionary.
    """        
    def __init__(self, FileName):      
        """
        Get a dictionary from a *.cpd file.
        
        @param: self, FileName
        @type: self: object
        @type: FileName: string
        """      
        ## Dictionary for further processing.                                         
        self.Data = GetDataFromPickle.getDictfromFile(FileName)
        os.remove(FileName)  

    @staticmethod
    def getDictfromFile(FileName):
        """
        Open a *.cpd file and extract the dictionary stored within.
        
        @param: FileName
        @type: FileName: string
        """ 
        FileIn = open(FileName, "rb")
        Dict = cp.load(FileIn)  #@UndefinedVariable
        FileIn.close()
        return Dict
    
## @class PyXMake.Tools.Utility.UpdateZIP
# Class to create 2to3 compatible pickling dictionary. Inherited from built-in object.
class UpdateZIP(object): # pragma: no cover
    """
    Context manager for update an existing ZIP folder
    
    @author: Marc Garbade
    """
    # Empty ZIP archive binary string
    __binary_empty_archive = b'PK\x05\x06\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'

    @staticmethod
    def create(filename):
        """
        Create a new compatible empty archive
        
        @author: Marc Garbade
        """
        # Local import of UploadFile
        from fastapi import UploadFile
        # Create new archive and account for version change
        try: archive = UploadFile(None,filename=filename)
        except TypeError: archive =UploadFile(filename)
        # Return the archive
        return archive
    
    def __init__(self, zipname, zipdata=None, outpath=os.getcwd(), exclude=[], update=True, **kwargs):
        self.ZipName = zipname
        try: self.ZipData = copy.deepcopy(zipdata)
        except: 
            # Data is not empty, but contains complex objects where copy fails. 
            self.buffer = open(os.path.join(os.getcwd(), self.ZipName), 'wb+')
            shutil.copyfileobj(zipdata, self.buffer)
        
        # If no ZIP data has been given or ZIP data is empty.
        if not zipdata or (hasattr(zipdata, "read") and zipdata.read() == b''):  
            self.ZipData = tempfile.SpooledTemporaryFile()
            self.ZipData.write(self.__binary_empty_archive)
            self.ZipData.seek(0)
            
        # Collect content of the ZIP folder from input
        if not os.path.exists(os.path.join(os.getcwd(), self.ZipName)):
            self.buffer = open(os.path.join(os.getcwd(), self.ZipName), 'wb+')
            shutil.copyfileobj(self.ZipData, self.buffer)
        # At this point, buffer will always be set. Either by the exception of by the if-clause.
        self.buffer.close();  
        
        # Initialize local variables
        self.Output = io.BytesIO();  
        self.OutputPath = outpath     
        self.ExcludeFiles = exclude  
        self.IgnoreExtension = kwargs.get("ignore_extension",(".zip", ".obj"))
        
        self.Update = update

    def __enter__(self):       
        # Extract data in current workspace and to examine its content
        with zipfile.ZipFile(str(self.ZipName)) as Input:
            Input.extractall()
        os.remove(self.ZipName)   
             
        # Do not copy input files back into the new zip folder.
        if not self.Update:
            self.ExcludeFiles.extend([f for f in os.listdir(os.getcwd()) if os.path.isfile(os.path.join(os.getcwd(), f))]) 

    def __exit__(self, etype, value, traceback):
        # Collect all newly created files and store them in a memory ZIP folder. 
        with zipfile.ZipFile(self.Output,"w", zipfile.ZIP_DEFLATED) as Patch:
            cwd = os.getcwd()
            for dirpath, _, filenames in os.walk(cwd):
                for f in filenames:
                    filepath = os.path.join(dirpath,f)
                    arcpath = filepath.split(cwd)[-1]
                    # Add all result files to the zip folder. Ignore old zip and object files
                    if not f.endswith(self.IgnoreExtension) and f not in self.ExcludeFiles:    
                        Patch.write(filepath, arcpath)

        # Write content of memory ZIP folder to disk (for download). Everything else has been removed by now.
        with open(os.path.join(self.OutputPath,self.ZipName), "wb") as f:
            f.write(self.Output.getvalue())
    
@contextmanager
def TemporaryDirectory(default=None):
    """
    Create a temporary dictionary for use with the "with" statement. Its content is deleted after execution.
    
    @param: default
    @type: default: string
    """ 
    @contextmanager
    def Changed(newdir, cleanup=lambda: True):
        """
        Local helper function to clean up the directory 
        """ 
        prevdir = os.getcwd()
        os.chdir(os.path.expanduser(newdir))
        try:
            yield
        finally:
            os.chdir(prevdir)
            cleanup()
    # Create a new temporary folder in default. 
    # Uses platform-dependent defaults when set to None. 
    dirpath = tempfile.mkdtemp(dir=default)
    def cleanup():
        try: shutil.rmtree(dirpath)
        except: DeleteRedundantFolders(dirpath, ignore_readonly=True)
    with Changed(dirpath, cleanup):
        yield dirpath
        
@contextmanager
def TemporaryEnvironment(environ={}): # pragma: no cover
    """
    Temporarily set process environment variables.
    """
    old_environ = os.environ.copy()
    os.environ.update(environ)
    try: yield
    finally:
        os.environ.clear()
        os.environ.update(old_environ)
    
@contextmanager
def ConsoleRedirect(to=os.devnull, stdout=None): # pragma: no cover
    """
    Redirect console output to a given file.
    """         
    def fileno(file_or_fd):
        """
        Small helper function to check the validity of the dump object.
        """   
        fd = getattr(file_or_fd, 'fileno', lambda: file_or_fd)()
        if not isinstance(fd, int):
            raise ValueError("Expected a file (`.fileno()`) or a file descriptor")
        return fd        
       
    def flush(stream):
        """
        Also flush c stdio buffers on python 3 (if possible)
        """   
        try:
            import ctypes
            from ctypes.util import find_library
        except ImportError:
            libc = None
        else:
            try:
                libc = ctypes.cdll.msvcrt # Windows
            except OSError:
                libc = ctypes.cdll.LoadLibrary(find_library('c'))        
        try:
            # Flush output associated with C/C++
            libc.fflush(ctypes.c_void_p.in_dll(libc, 'stdout'))
        except (AttributeError, ValueError, IOError):
            pass # unsupported
        
        # Regular flush
        stream.flush()
        pass
    
    if stdout is None:
        stdout = sys.stdout

    stdout_fd = fileno(stdout)
    # copy stdout_fd before it is overwritten
    #NOTE: `copied` is inheritable on Windows when duplicating a standard stream
    with os.fdopen(os.dup(stdout_fd), stdout.mode) as copied: 
        flush(stdout)  # flush library buffers that dup2 knows nothing about
        try:
            os.dup2(fileno(to), stdout_fd)  # $ exec >&to
        except ValueError:  # filename
            with open(to, 'wb') as to_file:
                os.dup2(to_file.fileno(), stdout_fd)  # $ exec > to
        try:
            yield stdout # allow code to be run with the redirected stdout
        finally:
            # restore stdout to its previous value
            #NOTE: dup2 makes stdout_fd inheritable unconditionally
            flush(stdout)
            os.dup2(copied.fileno(), stdout_fd)  # $ exec >&copied
            
@contextmanager   
def MergedConsoleRedirect(f): # pragma: no cover
    """
    Redirect all console outputs to a given stream
    """
    with ConsoleRedirect(to=sys.stdout, stdout=sys.stdin) as inp, ConsoleRedirect(to=sys.stdout, stdout=sys.stderr) as err, ConsoleRedirect(to=f,stdout=sys.stdout) as out:  
        # $ exec 2>&1 
        yield (inp, err, out)  
        
@contextmanager   
def FileOutput(FileName): # pragma: no cover
    """
    Redirect outputs to a given file.
    """  
    if sys.version_info >= (3,4):         
        import contextlib
        # Python 3.4 and higher
        try:
            with open(FileName, 'w', encoding="utf-8") as f, contextlib.redirect_stdout(f), MergedConsoleRedirect(sys.stdout):
                yield f
        except:
            # Python 3.6+ and in Docker container
            with open(FileName, 'w', encoding="utf-8") as f, contextlib.redirect_stdout(f):
                yield f
    else:
        # Lower version (unstable and deprecated)
        with open(FileName, 'w', encoding="utf-8") as f, MergedConsoleRedirect(f):
            yield f
            
def FileUpload(url, filename, header={}, **kwargs): # pragma: no cover
    """
    Post a given file as a binary string to a given URL. 
    
    @note: LFS is available if request_toolbelt is installed.
    """    
    import requests
    # Procedure
    try: r = requests.post(url, files = {kwargs.pop("kind",'file'): open(filename,'rb')}, headers=header, **kwargs)
    except OverflowError: 
        try: 
            ## The file in question is to large. Attempt large-file support
            from requests_toolbelt.multipart import encoder
            session = requests.Session()
            with open(filename, 'rb') as f:
                form = encoder.MultipartEncoder({"documents": (filename, f, "application/octet-stream"),"composite": "NONE"})
                header.update( {"Prefer": "respond-async", "Content-Type": form.content_type})
                r = session.post(url, headers=header, data=form, **kwargs)
                session.close()
        # The necessary module is not installed. Skipping.
        except ImportError: print("The given file is too large. Skipping.")
    # We attempted uploading the file with large file support enabled, but failed.
    except: print("Failed to upload %s." % filename)
    # Return the response
    return r
     
@autotest("www.dlr.de")    
def GetHyperlink(s): 
    """
    Get all URLs present in a given string
    """  
    import re

    # Regular expression for URL
    regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
    url = re.findall(regex,s)       
    
    # Fail safe URL return
    if [x[0] for x in url]:
        return [x[0] for x in url]
    else:
        try: # pragma: no cover
            return s.split("href=")[1]
        except:
            return []
    
@autotest()
def GetPyXMakePath():
    """
    Get the PyXMake path from *__init__.
    """
    Path = PyXMakePath 
    return Path

def GetPlatform():
    """
    Get the underlying machine platform in lower cases.
    """    
    return str(platform.system()).lower()

def GetArchitecture():
    """
    Get the underlying machine architecture. Returns either x86 or x64 which corresponds to 
    32 or 64 bit systems.
    """    
    if struct.calcsize("P") * 8 == 64:
        arch = 'x64' 
    else: # pragma: no cover
        arch = 'x86'
    return arch

def GetLink(path): # pragma: no cover
    """
    Return the link target of a symbolic soft link
    
    @note: Supports .lnk files from windows. Returns the target as well as all arguments
    """        
    result = None
    delimn = " "
    
    # This option is only available on NT systems
    if GetPlatform() in ["windows"] and PathLeaf(path).endswith(".lnk"):
        # Local imports
        try: import pywintypes #@UnusedImport
        # Add shared library path explicitly
        except ImportError: sys.path.append(os.path.join(site.getsitepackages()[-1],"pywin32_system32"))
        finally:
            import pywintypes #@UnusedImport @Reimport
            import pythoncom #@UnusedImport
            import win32com.client
        
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(path)
        # Extract target and all arguments
        result = delimn.join([shortcut.Targetpath,shortcut.Arguments])
    
    # We have a symbolic soft link
    if not result: result = os.readlink(path) 

    # Return a result.
    return result

def GetExecutable(name, get_path=False, **kwargs):
    """
    Check whether name is on PATH and marked as executable.
    
    @author: Six
    @note: https://stackoverflow.com/questions/11210104/check-if-a-program-exists-from-a-python-script
    """
    ## Overwrite default search path to always include the current directory
    # Only use the current directory if PATH variable is not accessible
    kwargs.update({"path": kwargs.get("path", 
    kwargs.pop("search_paths",os.pathsep.join([os.getenv("PATH",os.getcwd()),os.getcwd()]) if GetPlatform() != "windows" else None))})
    try:
        from whichcraft import which
    except ImportError:
        if sys.version_info >= (3, 3):
            from shutil import which
        else:
            # This happens when executed with Python 3.2 and lower without witchcraft module
            from distutils.spawn import find_executable
            # Check if path to executable is requested
            if not get_path:
                # Return just a boolean expression
                return find_executable(name, **kwargs) is not None
            else:
                # Return both path and executable
                return find_executable(name, **kwargs) is not None, find_executable(name, **kwargs)
    # We reach this point in all other cases
    if not get_path:
        # Return just a boolean expression
        return which(name, **kwargs) is not None
    else:
        # Return both path and executable
        return which(name, **kwargs) is not None, which(name, **kwargs)
    
@autotest("false")
def GetBoolean(v): # pragma: no cover
    """
    Inspect the input variable and return a Boolean value if conversion is possible. 
    
    @Original: https://stackoverflow.com/questions/15008758/parsing-boolean-values-with-argparse
    """          
    import argparse
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1', "on"):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0', "off"):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

@autotest(autorun=False, stream=sys.stdout, reconfigure=True)
def GetLogger(name=None, **kwargs): # pragma: no cover
    """
    Initialize a root logger if no settings prior to loading have been found. 
    Otherwise, inherit a logger from supported system logging utilities when available.
    Finally, return a reference to the created or already created logger.
    """
    # Local variables
    delimn = " "
    
    log_name = name
    log_format = kwargs.pop("format",None)
    log_stream = kwargs.pop("stream",None)
    log_level = kwargs.pop("level",logging.NOTSET)
    log_overwrite = kwargs.pop("overwrite", log_name != None)
    
    try: 
        if log_overwrite: log_level = logging.getLogger().handlers[0].level
    except IndexError: pass

    try: 
        from fa_pyutils.service.logger import MyLogger as getLogger
        # Create a new logger from SY service module
        logger = getLogger(log_name)
        logger._setLogLevel(log_level)
        # Always use system logger in development mode
        if kwargs.pop("user",getattr(sys, "frozen", False)): raise ImportError
        logger.handlers.clear() #@UndefinedVariable
        handle = logging.StreamHandler()
        # Update format
        log_format = logger.formatter._fmt.split()  #@UndefinedVariable
        if log_name: log_format.insert(1, '%(name)s')
        log_format = delimn.join(log_format)
        # Update handle
        handle.setFormatter(logging.Formatter(log_format))
    except ImportError:
        # Fail back to default logger
        logger = logging.getLogger(__name__)
        handle = logging.StreamHandler(log_stream)
    finally:
        # Set log level to highest available
        logger.setLevel(log_level)
        logger.addHandler(handle)
    # Reconfigure logging globally
    if kwargs.pop("reconfigure",len(logging.getLogger().handlers) < 1 and log_overwrite):
        logging.basicConfig(level=log_level, format=log_format, stream=log_stream, **kwargs)
    # Only update the logger once
    if log_name and not log_name in logging.root.manager.loggerDict: #@UndefinedVariable
        logging.root.manager.loggerDict.update({log_name:logger})  #@UndefinedVariable
    # Return logger object
    return logging.getLogger(log_name)

def GetRequirements(dirname, args=[], check=False, **kwargs):
    """
    Create a list of required sub-packages for a given Python project (given as full directory path).
    
    @author: garb_ma
    """
    import requests
    import datetime
    import pipreqs
    # Some minor imports
    from packaging import version
    from tempfile import NamedTemporaryFile
    from pipreqs.pipreqs import main as listreqs
    # Create a temporary file for storage of binary output
    tmp = NamedTemporaryFile(mode="r+", suffix=".txt", encoding="utf-8", delete=False).name
    command = ["--force","--savepath", tmp, "--encoding","utf-8"]
    # Assemble build command
    command.extend(args); command.append(dirname)
    # New input format style. Keep backwards compatibility.
    if version.parse(pipreqs.__version__) >= version.parse("0.4.11") and "--no-pin" in command:
        command.remove("--no-pin"); command = ["--mode", "no-pin"] + command ;  
    # Execute command and restore system variables.
    restored = copy.deepcopy(sys.argv); sys.argv = sys.argv[0:1] + command; listreqs(); sys.argv = restored
    # Get the file as URL (just for cross-validation)
    target_url = 'file:' + urllib.request.pathname2url(tmp)
    # Store content as a comma-separated list.
    data = urllib.request.urlopen(target_url).read().decode('utf-8').replace(os.linesep," ").split()
    # Remove all non-existing packages
    if check: 
        try: 
            from stdlib_list import stdlib_list
            # Check if standard library module is available for search
            data = [str(item) for item in data if not any([x.startswith(str(item)) for x in stdlib_list()])]
        except ImportError: pass
        # Explicit version check if pinned
        responses = [(item, requests.get("https://pypi.python.org/pypi/%s/json" % str(item).split("==")[0])) for item in data]
        try: data = [str(item) for item, response in responses if str(item).split("==")[1] in response.json()["releases"] ]
        except: data = [str(item) for item, response in responses if response.status_code == 200]
        # Check for heavily dated packages
        for item in data: 
            # Check if the last update is older than 5 years (default). Can be used to fine-tune the results and removes heavily out-dated packages
            response = dict(requests.get("https://pypi.python.org/pypi/%s/json" % str(item).split("==")[0]).json())
            try: diff = abs(int(datetime.date.today().year) - int(response["releases"][response["info"]["version"]][0]["upload_time_iso_8601"].split("-")[0]))
            except: 
                ## There is something wrong if the found match. 
                # Remove the entry. It either cannot be resolved correctly using PyPi or a false positive from PyReq was found locally.
                data.remove(item); continue
            if diff >= int(kwargs.get("check_updated", 5)): data.remove(item)
    # Remove temporary folder (if existing!)
    try:
        os.remove(tmp)
    except FileNotFoundError:
        pass
    # Return the data as a list
    return data

@autotest()
def GetHostIPAddress():
    """
    Return the host IP address (IP address of the machine executing this code)
    """    
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

@autotest()
def GetWSLIPAddress():
    """
    Return the WSL IP address (IP address of the machine executing this code)
    """
    def hasWSL():
        """
        Heuristic to detect if Windows Subsystem for Linux is available.

        @source: https://www.scivision.dev/python-detect-wsl/
        """
        if os.name == "nt": # pragma: no cover
            wsl = shutil.which("wsl")
            if not wsl:
                return False
            ret = subprocess.run(["wsl", "test", "-f", "/etc/os-release"])
            return ret.returncode == 0
        return False
    
    # Return WSL IP address or none is not available (Linux, macOS)
    if hasWSL(): return subprocess.check_output(["bash","-c","ifconfig eth0 | grep 'inet '"]).decode().split("inet ")[-1].split(" netmask")[0]
    else: return None
    
@autotest(r'"data"')
def GetSanitizedDataFromCommand(*args, **kwargs):
    """
    Returns platform independent paths extracted from a given command or list
    """    
    def sanitize(expression, **kwargs):
        """
        Validate a given pair
        """
        # Paths should be given in double quotes to accept spaces
        try: result = ArbitraryEval(expression)
        # Parsed strings contains single quotes only
        except kwargs.get("allowed_exceptions", (ValueError, SyntaxError)) as _: 
            result = expression # pragma: no cover
        # Return the result in both cases
        return result
    # Always create a list from the given input
    data = list(ArbitraryFlattening([args]))
    data = [os.path.normpath(sanitize(x,**kwargs)) for x in data]
    # Treat input as paths. Get system independent format
    if kwargs.get("is_path",True):
        # Check if paths are given relative or absolute. Rewrite to absolute in any case
        result = [os.path.abspath(x) if os.path.exists(os.path.abspath(x))
                       else os.path.abspath(os.path.join(os.getcwd(),x)) for x in data]
    else: result = data  # pragma: no cover
    # Return list of rewritten paths
    return result

@autotest("echo")
def GetEnvironmentFromCommand(command):
    """
    Returns the active environment from a process after a given command is executed.
    """
    # Local function definitions
    def validate_pair(ob): # pragma: no cover
        """
        Validate a given pair
        """
        try:
            if not (len(ob) == 2):
                raise RuntimeError("Unexpected result: %s" % ob)
        except: return False
        return True
    
    def consume(iterable):
        """
        Iterate over a given stream of inputs
        """
        try:
            while True: next(iterable)
        except StopIteration: pass
        pass
    
    # Local imports
    import itertools
    
    # Begin of function body
    delimn = " %s " % "&&" if GetPlatform() in ["windows"] else ";"
    printenv = "set" if GetPlatform() in ["windows"] else "printenv"
    tag = 'Done running command'
    # construct a cmd.exe command to do accomplish this
    command = delimn.join([command,'echo "%s"' % tag,printenv])
    # Execute the command
    proc = Popen(command, raw=True)
    # parse the output sent to standard output
    lines = proc.stdout
    # Consume whatever output occurs until the tag is reached
    consume(itertools.takewhile(lambda l: tag not in l, lines))
    # Define a way to handle each KEY=VALUE line
    handle_line = lambda l: l.rstrip().split('=',1)
    # Parse key/values into pairs and validate them
    pairs = map(handle_line, lines)
    valid_pairs = filter(validate_pair, pairs)
    # Create a dictionary of valid pairs
    result = dict(valid_pairs)
    # Finish the process
    proc.communicate()
    # Return results
    return result

@autotest()
def GetDomainNameServer():
    """
    Return the local DNS IP address.
    """    
    import dns.resolver #@UnresolvedImport
    dns_resolver = dns.resolver.Resolver()
    # Return result
    return dns_resolver.nameservers

@autotest(default = True)
def GetOpenAPIGenerator(output=None, **kwargs):
    """
    Get the latest version of OpenAPI generator (requires Internet connection).
    
    @author: garb_ma
    """
    # Local imports
    import requests
    import urllib.request
    
    from lxml import html
    from packaging.version import Version, parse
    
    # Default output variable
    result = None
    # Define output directory. Defaults to PyXMake sub folder
    if not output: path = os.path.join(PyXMakePath,"Build","bin","openapi")
    else: path = output # pragma: no cover
    # Check if the path already exists or is empty. Install if no executable is found
    if not os.path.exists(path) or not os.listdir(path) and kwargs.get("silent_install",True): 
        # This is the base download path
        base = "https://repo1.maven.org/maven2/org/openapitools/openapi-generator-cli"
        try: 
            # Attempt to fetch latest version. Requires an active connection
            page = requests.get(base)
            page.raise_for_status()
            webpage = html.fromstring(page.content)
            # This is the latest version
            version = sorted([x[:-1] for x in webpage.xpath('//a/@href') if str(x[:-1][0]).isdigit() and isinstance(parse(x[:-1]),Version)], reverse=True)[0]
            # Allow users to define a version
            url = posixpath.join(base,version,"openapi-generator-cli-%s.jar" % kwargs.get("version", version ) )
            # Create full output path
            os.makedirs(path, exist_ok=True)
            # Download the executable
            urllib.request.urlretrieve(url,os.path.join(path,PathLeaf(url)))
        # Something went wrong while processing the correct version
        except: raise ConnectionError("Downloading latest OpenAPI generator client failed.")
    # The latest executable within the folder is returned
    if os.listdir(path): result = os.path.join(path,sorted([x for x in os.listdir(path)], reverse=True)[0])
    # Return None or the absolute path to the client
    return result

@autotest("DLR")
def GetBibliographyData(fulltext, verbose=0):
    """
    Perform a full text search using Googles' book API.
    """
    def get(url):
        """
        Send a get command.
        
        @note: Uses requests when available; falls back to urllib if requests is not found.
        """
        try: import requests
        except ImportError: import urllib.request as requests # pragma: no cover
        
        # Get preliminary information from API
        try: # pragma: no cover
            # This only works when requests is a local alias to urllib.request
            with requests.urlopen(base_api_link) as f: text = f.read()
            result = text.decode("utf-8")
            # This should be the default case for modern systems
        except AttributeError: result = requests.get(base_api_link).text #@UndefinedVariable
        # Return result
        return result
    
    # Immutable link to Google API   
    google_api_search = posixpath.join("https:",""," ","www.googleapis.com","books","v1","volumes")
    base_api_link = posixpath.join(google_api_search,"?q=").replace(" ","")+urllib.parse.quote(str(fulltext))
    
    # Get preliminary information from API
    decoded_text = get(base_api_link)
    
    try:
        obj = json.loads(decoded_text) # deserializes decoded_text to a Python object
        # Fetch full JSON information from volume ID
        base_api_link = posixpath.join(google_api_search,obj["items"][0]["id"]).replace(" ","")
        
        # Get extended information from the API
        decoded_text = get(base_api_link)
        JSON = json.loads(decoded_text) # deserializes decoded_text to a Python object
    except:
        if verbose >= 1: print("No matching entry found")
        JSON = dict()
        pass
    
    # Return serialized object
    return JSON

@autotest(arg=0)
def GetTemporaryFileName(arg=None, filename="Temp", extension=".cpd", **kwargs):
    """  
    Create a temporary file name with extension *.cpd by default. Optional argument: Seed for random number generation.
    """     
    if isinstance(arg, six.integer_types): 
        _seed = arg
        rd.seed(_seed)
        randTempInteger = rd.randint(1,1000)
        # Added backwards compatibility
        TempFileName = filename + str(randTempInteger) + kwargs.get("ending",extension)
    else: 
        rd.seed()
        randTempInteger = rd.randint(1,1000)
        # Added backwards compatibility
        TempFileName = filename + str(randTempInteger) + kwargs.get("ending",extension)
    return TempFileName

@autotest("'%s'" % site.getusersitepackages())
def GetPathConversion(path, target_os=None, **kwargs): # pragma: no cover
    """
    Return the given absolute path in its Linux/Windows counter part. 
    """
    current_os = target_os
    if current_os == None: current_os = GetPlatform()
    # Check if path is given in quotations
    if path[0] == path[-1] and path[0] in ["'",'"']: 
        quote = path[0]
        path = path[1:-1]
    else: quote = None
    ## Fetch the requested target platform
    if current_os.lower() == "linux":
        target = posixpath; pristine = ntpath
    else:
        target = ntpath; pristine = posixpath

    if os.path.splitdrive(path)[0]:
        # Input path is Windows style
        converted_path = target.join(AsDrive(os.path.splitdrive(path)[0][0], sep=target.sep), *os.path.splitdrive(path)[-1].replace(pristine.sep, target.sep).split(target.sep)[1:])
    elif current_os.lower != GetPlatform():
        converted_path = ntpath.abspath(path)
        # Treat first entry of Linux path as a Windows drive. Defaults to True.
        if len(path.split(pristine.sep)) ==1: pristine = target
        if kwargs.get("use_linux_drive",True): converted_path = target.join(AsDrive(path.split(pristine.sep)[1:][0], sep=target.sep),*path.split(pristine.sep)[2:])
    else:
        # Copy path to output
        converted_path = path
    # Apply all quotations
    if quote: 
        path = quote + path + quote
        converted_path = quote + converted_path + quote
    return converted_path

@autotest("PyXMake")
def GetIterableAsList(Iterable):
    """
    Walk through an iterable input set and store the results in a list.
    """      
    AsList = []
    for i in range(0,len(Iterable)):
        AsList.append(Iterable[i])    
    return AsList

def GetMergedRepositories(RepoID, RepoList, RepoBranch= {}, MergeBranch = [], scratch=os.getcwd(), **kwargs): # pragma: no cover
    """
    Walk through an iterable input set and store the results in a list.
    """          
    try:
        import git
        import git_filter_repo
    except:
        raise NotImplementedError
    
    url_delimn = "/"
    master = kwargs.get("default_branch","master")
    
    repo_branch = RepoBranch
    if not MergeBranch: merge_branch = [master for _ in RepoList]
    
    # Check if arrays have the same size. Return an array if that is not the case.
    if len(merge_branch) != len(RepoList): 
        raise NotImplementedError

    # Create an iterator.
    merge_branch = iter(merge_branch)

    # Operate fully in a temporary directory
    with ChangedWorkingDirectory(scratch):
        if not os.path.exists(RepoID):
            # Initialize a new repository named RepoID
            g = git.Repo.init(RepoID) #@UndefinedVariable
        else:
            # Update existing repository
            g = git.Repo(RepoID)
        # Iterate through all given repositories
        for repo in RepoList:
            add_repo = repo[0]; add_package = repo[1]
            # Check if an additional sub-folder name has been given
            try: add_subfolder = repo[2];
            except: add_subfolder = ""
            
            # Iterate through given branches. Defaults to master branch if not given otherwise.
            add_branch = next(merge_branch)
            
            # Clone the given repositories
            _ = git.Repo.clone_from(add_repo, add_package) #@UndefinedVariable
            if add_subfolder:
                # Create a new sub-folder with the content of the repository. Only if a sub-folder was given.
                command = " ".join([sys.executable,git_filter_repo.__file__,"--to-subdirectory-filter",add_subfolder])
                _.git.execute(shlex.split(command,posix=not os.name.lower() in ["nt"]))
                
            # Merge GIT repositories - allowing unrelated histories.
            g.git.remote("add",add_package, "../"+add_package)
            g.git.fetch(add_package,"--tags")
            g.git.merge("--allow-unrelated-histories",url_delimn.join([add_package,add_branch]))
            g.git.remote("remove",add_package)
    
            # Again, avoid race condition. If it is still happening, retry again until success.
            while True:
                time.sleep(1)
                try: DeleteRedundantFolders(add_package, ignore_readonly=True); break
                except: pass
                
        # Create additional branches with the content of the original repositories
        for repo in RepoList:
            # Check if a branch directory was given. 
            if not repo_branch: break
            try: add_subfolder = repo[2];
            except: add_subfolder = ""
            
            g.git.switch(master)
            
            if add_subfolder:
                g.git.checkout(master, b=repo_branch[add_subfolder])
                command = " ".join([sys.executable,git_filter_repo.__file__,"--force","--subdirectory-filter",add_subfolder+"/","--refs",repo_branch[add_subfolder]])
                g.git.execute(shlex.split(command,posix=not os.name.lower() in ["nt"]))

        g.git.switch(master)
                
        if not kwargs.get("keep_subfolder",True): 
            for repo in RepoList:
                # Check if a branch directory was given. 
                if not repo_branch: break
                try: add_subfolder = repo[2];
                except: break
                DeleteRedundantFolders(os.path.join(os.path.abspath(os.getcwd()),RepoID,add_subfolder), ignore_readonly=True)
            try:
                g.git.add(".")
                g.git.commit("-m", "Added branches")
            except: pass
        
    # Return error code
    return 0

def GetDockerContainer(container,  encoding="utf-8"): # pragma: no cover
    """
    Check if a current given container is active and running. Returns boolean value.
    
    @author: garb_ma    
    @param: container
    @type: string
    """
    # Check if executable exists on the current machine
    if not GetExecutable("docker"):
        print("==================================")    
        print("docker-compose not found. Please install Docker")    
        print("==================================")                
        return -1
    
    command = " ".join(["docker","ps","--filter", "name="+container])
    p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=not IsDockerContainer())    
    logs, _ = p.communicate()
    ## Extract result string. Output ends with "NAMES" if no container is found. Otherwise, a string containing information 
    # about the running container is appended. Since only a boolean value is required, the check for names is sufficient. 
    return not logs.decode(encoding,errors='ignore').replace('\n', '').endswith("NAMES")

def GetDockerRegistry(registry, port, https_keypath="", https_pemfile="", GUI=False, **kwargs): # pragma: no cover
    """
    Check if a current given registry is active and running. If not, start a local docker registry at the given port and name.
    Optionally, secure connection by a HTTPS certificate (PEM) and alter the base image
    
    @author: garb_ma    
    @param: registry
    @type: string
    """
    # Check if executable exists on the current machine
    if not GetExecutable("docker"):
        print("==================================")    
        print("Docker executable not found. Please install Docker")    
        print("==================================")                
        return -1
    
    # Check if the given container is already active and running
    if GetDockerContainer(registry):
        print("==================================")    
        print("Container is already running")    
        print("==================================")                
        return -1
    
    # Assemble base command
    command=["docker","run","-d","--restart=always","--name",str(registry),"-e","REGISTRY_HTTP_ADDR=0.0.0.0:"+str(port),"-p",":".join([str(port)]*2)]
    # Check if HTTPS support should be enabled.
    if all([https_keypath, https_pemfile]): 
        command.extend(["-v",str(https_keypath)+":/certs","-e","REGISTRY_HTTP_TLS_CERTIFICATE=/certs/"+str(https_pemfile),                                                                                              
                                                                                                  "-e","REGISTRY_HTTP_TLS_KEY=/certs/"+str(https_pemfile)])    
    # Provide base image name (from which to spawn the registry
    command.extend([kwargs.get("registry_base","registry:latest")])
    # Execute command
    p = subprocess.check_call(command, shell=True)
    
    if GUI:
        # Assemble GUI command
        command = ["docker","run","-d","--restart=always","--name",str(registry)+"_ui", "-p",kwargs.get("ui_port",str(int(str(port))+50))+":80"]
        command.extend(["-e","REGISTRY_HOST="+str(GetHostIPAddress),"-e","REGISTRY_PORT="+str(port)])
        # Check HTTPS support
        if all([https_keypath, https_pemfile]): command.extend(["-e","REGISTRY_PROTOCOL=https"])
        #Finalize command
        command.extend(["-e","SSL_VERIFY=false", "-e","ALLOW_REGISTRY_LOGIN=true","-e","REGISTRY_ALLOW_DELETE=true",
                                          "-e","REGISTRY_PUBLIC_URL="+":".join([str(socket.gethostname()),str(port)]),kwargs.get("ui_base","parabuzzle/craneoperator:latest")])
        # Run with GUI support
        subprocess.check_call(command, shell=True)

    # Return error code
    return p

def GetDockerUI(name="portainer", image="portainer/portainer-ce:latest"): # pragma: no cover
    """
    Create a custom web UI for docker using Portainer. 
    
    @author: garb_ma    
    @param: name
    @type: string
    """    
    # Check if executable exists on the current machine
    if not GetExecutable("docker"):
        print("==================================")    
        print("Docker executable not found. Please install Docker")    
        print("==================================")                
        return -1
    
    # Check if the given container is already active and running
    if GetDockerContainer(name):
        print("==================================")    
        print("Container is already running")    
        print("==================================")                
        return -1
    
    # Assemble base command
    command = ["docker","run","-d"]
    command.extend(["--name=%s" % name , "--restart=always"]) 
    command.extend(["-p","8000:8000","-p","9000:9000","-p","9443:9443"])
    command.extend(["-v","/var/run/docker.sock:/var/run/docker.sock","-v","portainer_data:/data", image]) 
    # command.extend([-v cert:/certs --tlsskipverify --tlscert /certs/jenkins.pem --tlskey /certs/jenkins.pem]
    subprocess.check_call(command, shell=not GetPlatform() in ["linux"])
    # Return success code
    return 0

def GetDockerRunner(runner="gitlab-runner",restart_policy="always", image="",token="", executor="shell", 
       url='https://gitlab.dlr.de/', tags="docker,linux", ssl_verify=True, **kwargs): # pragma: no cover
    """
    Check if a current given registry is active and running. If not, start a local docker registry at the given port and name.
    Optionally, secure connection by a HTTPS certificate (PEM) and alter the base image
    
    @author: garb_ma    
    @param: registry
    @type: string
    """
    # Return GitLab Runner installation script (Linux only).
    if kwargs.get("as_script","") and os.path.exists(os.path.dirname(kwargs.get("as_script",""))):
        script = '''\
        #!/bin/sh
        # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        # %                             Shell script for Docker/Linux (x64)                               %     
        # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        # Shell script for creating a GitLab runner programmatically
        # Created on 22.04.2022
        # 
        # Version: 1.0
        # -------------------------------------------------------------------------------------------------
        #    Requirements and dependencies:
        #        - 
        #
        #     Changelog:
        #        - Created // mg 22.04.2022
        #
        # -------------------------------------------------------------------------------------------------
        # Process through all command line arguments (if given).
        for i in "$@"
        do
        case $i in
            -t=*|--token=*)
            token="${i#*=}"
            shift 
            ;;
            -u=*|--url=*)
            url="${i#*=}"
            shift 
            ;;
            -i=*|--image=*)
            image="${i#*=}"
            shift 
            ;;
            -d=*|--description=*)
            description="${i#*=}"
            shift 
            ;;
            -e=*|--executor=*)
            executor="${i#*=}"
            shift 
            ;;
            -b=*|--base=*)
            base="${i#*=}"
            shift
            ;;
            -l=*|--locked=*)
            locked="${i#*=}"
            shift 
            ;;
            -s=*|--system=*)
            return="${i#*=}"
            shift 
            ;;
            -r=*|--return=*)
            return="${i#*=}"
            shift 
            ;;
            *)    # Unknown option
            ;;
        esac
        done
        # Evaluate user settings
        token=${token:-""}
        url=${url:-"https://gitlab.dlr.de/"}
        system=${system:-"local"}
        image=${image:-"harbor.fa-services.intra.dlr.de/dockerhub/gitlab/gitlab-runner:latest"}
        executor=${executor:-"docker"}
        base=${base:-"alpine:latest"}
        description=${description:-"fa-docker"}
        locked=${locked:-"false"}
        return=${return:-"true"}
        # Procedure
        command=$( echo "docker run --rm -v gitlab-runner-config:/etc/gitlab-runner ${image}" )
        if [ "$system" != "dind" ]; then
        download="https://packages.gitlab.com/install/repositories/runner/gitlab-runner"
        command=$( echo "gitlab-runner" )
        # Debian, Ubuntu and Mint
        ( command -v apt >/dev/null 2>&1 ; ) && ( curl -L "$download/script.deb.sh" | bash ) && ( apt-get install gitlab-runner ) ; 
        # RHEL, CentOS and Fedora
        ( command -v yum >/dev/null 2>&1 ; ) && ( curl -L "$download/script.rpm.sh" | bash ) && ( yum install gitlab-runner ) ; 
        else
        # Docker in Docker
        docker volume create gitlab-runner-config
        docker run -d --name gitlab-runner --restart always -v gitlab-runner-config:/etc/gitlab-runner -v /var/run/docker.sock:/var/run/docker.sock --env TZ=DE -i ${image} 
        fi 
        $command register --non-interactive --executor ${executor} --docker-image ${base} --url ${url} --registration-token ${token} --description ${description} --tag-list ${executor} --run-untagged=true --locked=${locked} --access-level=not_protected --docker-privileged --docker-volumes /certs/client
        # Create a cron job deleting all leftover data in regular intervals.
        echo 'docker system prune --all --volumes --force' > cron.sh
        # Resume to main shell. Deactivate in Docker to keep the container running endlessly.
        if [ "$return" = "false" ]; then tail -f /dev/null; fi
        exit 0'''
        path = kwargs.get("as_script")
        with open(path,"w") as f: f.write(textwrap.dedent(script))
        print("==================================")    
        print("Writing GitLab Runner Runtime script to: ")    
        print("%s " % path)    
        print("==================================")        
        return os.path.abspath(path)
    
    # Check if executable exists on the current machine
    if not GetExecutable("docker"):
        print("==================================")    
        print("Docker executable not found. Please install Docker")    
        print("==================================")                
        return -1

    # Check if the given container is already active and running
    if not GetDockerContainer(runner):
        # Expose docker host socket to runner - add additional / to host path if started from Windows.
        socket = "/var/run/docker.sock:/var/run/docker.sock"
        if GetPlatform() == "windows": socket = socket[0] + socket
        # Create a local docker volume to store all relevant information
        subprocess.check_call(["docker","volume","create",runner+"-config"], shell=not GetPlatform() in ["linux"])
        # Assemble command 
        command = ["docker","run","-d","--name",runner,"--restart",restart_policy,"-v",runner+"-config"+":/etc/gitlab-runner","-v",socket,"--env","TZ=DE",
                                "-i","gitlab/gitlab-runner:latest"]
        # Install a GitLab runner into current docker environment
        subprocess.check_call(command, shell=not GetPlatform() in ["linux"])
        if image: 
            subprocess.check_call(["docker","tag","gitlab/gitlab-runner:latest",image], shell=not GetPlatform() in ["linux"])
            subprocess.check_call(["docker","image","rm","gitlab/gitlab-runner:latest"], shell=not GetPlatform() in ["linux"])
            _run_image = image
        else:
            _run_image="gitlab/gitlab-runner:latest"
        if token:
            # If token is given, additionally establish connection with given parameters
            command = ['docker','run','--rm','-v',runner+"-config"+":/etc/gitlab-runner",_run_image,'register','--non-interactive','--executor',executor,'--docker-image','alpine:latest',
                                    '--url',url,'--registration-token',token,'--description',str(runner),'--tag-list',tags,'--run-untagged=true','--locked=false','--access-level=not_protected',
                                    '--docker-privileged']
            # Only if SSL verification is active
            if ssl_verify: command.extend(["--docker-volumes","/certs/client"])
            subprocess.check_call(command, shell=not GetPlatform() in ["linux"])
    else:
        print("==================================")    
        print("Container is already running")    
        print("==================================")                
        
    return 0

def GetDockerPorts(**kwargs): # pragma: no cover
    """
    Get all active Docker ports. Either from a given container, by a list of containers or all active containers.
    Defaults to all active containers. Supports WSL2 with Docker installed.
    
    @author: garb_ma
    @param: container
    @type: string
    """
    # Check if executable exists on the current machine
    if not GetExecutable("docker"):
        print("==================================")    
        print("Docker executable not found. Please install Docker")    
        print("==================================")                
        return -1

    # Get docker's absolute execution path
    _, docker = GetExecutable("docker", get_path=True)
    if not docker.lower().endswith(".bat"): docker = "docker"
    
    data = []; ports = [];
    # Collect all ports from given containers.
    active_container = kwargs.get("container"," ".join(subprocess.check_output((["sudo"] if IsDockerContainer() else []) + [docker,"ps","--quiet"]).decode("utf-8").split()).split("--quiet")[-1].split())
    if isinstance(active_container, str): active_container = list(active_container)
    for x in active_container: data.extend(" ".join(subprocess.check_output((["sudo"] if IsDockerContainer() else []) + [docker,"port",x]).decode("utf-8").split()).split(x)[-1].split("->"))
    for x in data:
        port = (x.split(":")[-1] if ":" in x else "").split(" ")[0]; 
        if IsNotEmpty(port): ports.append(int(port))

    # Return all active ports as a list of integers
    return  list(set(ports))

@autotest("user","password")
def GetDockerEncoding(*args, **kwargs):
    """
    Creates a base64 encoded string of a given username and password combination used for Docker authentifiction.
    @author: garb_ma    
    @param: username, password
    @type: string
    """    
    import base64
    # No values have been given. Return immediately.
    if not args: return
    # Use internal base64 encryption method
    message = str(args[0])
    # Loop over all given variables and merge them with user-defined delimiter
    if len(args) >= 1: message = kwargs.get("delimn",":").join([str(x) for x in args])
    # Encode a given string or a list of strings by combining them 
    message_bytes = message.encode(kwargs.get("encoding",'utf-8'))
    base64_bytes = base64.b64encode(message_bytes)
    base64_message = base64_bytes.decode(kwargs.get("encoding",'utf-8'))
    return base64_message

@autotest()
def IsDockerContainer():
    """
    Check whether current package lives inside a docker container.
    """   
    path = '/proc/self/cgroup'
    return (os.path.exists('/.dockerenv') or os.path.isfile(path) and any('docker' in line for line in open(path))) or GetExecutable("cexecsvc")

@autotest("data")
def InQuotes(s,quote='"'):
    """
    Return the given string in quotes.
    """          
    return str(quote)+str(s)+str(quote)

@autotest(" ")
def IsNotEmpty(s):
    """
    Check whether a string is empty and/or not given. Returns True otherwise.
    """          
    return bool(s and s.strip())

@autotest("3551551677")
def IsValidISBN(isbn): 
    """
    Check whether a given string corresponds to a valid ISBN address.
    """             
    import re
    
    # Strip everything unrelated for the search
    isbn = isbn.replace("-", "").replace(" ", "").upper();
    match = re.search(r'^(\d{9})(\d|X)$', isbn)
    if not match: # pragma: no cover
        return False

    # Strip trailing X from ISBN address. 
    digits = match.group(1)
    check_digit = 10 if match.group(2) == 'X' else int(match.group(2))

    result = sum((i + 1) * int(digit) for i, digit in enumerate(digits))
    
    # Returns True is string is a valid ISBN. False otherwise
    return (result % 11) == check_digit

@autotest("SGVsbG9Xb3JsZA==")
def isBase64(string):
    """
    Check if a string is a valid base64 encoded string
    
    @note: Inspired from the discussion at https://stackoverflow.com/questions/12315398/check-if-a-string-is-encoded-in-base64-using-python
    
    @author: garb_ma
    """
    # Local import definitions
    import base64
    import binascii
    # Default output value
    result = False
    try:
        # Verify that a given string is base64 encoded
        base64.b64decode(string, validate=True)
        result = True
    except binascii.Error: pass
    # Return boolean output
    return result

@autotest()
def IsWSL():
    """
    Detect if the script is running inside WSL or WSL2 on windows.
    
    @note: WSL is thought to be the only common Linux kernel with Microsoft in the name, per Microsoft:
    https://github.com/microsoft/WSL/issues/4071#issuecomment-496715404
    
    @author: https://www.scivision.dev/python-detect-wsl/
    """
    return 'Microsoft' in platform.uname().release

def AsDrive(s, sep=os.path.sep):
    """
    Return s as drive to start an absolute path with path.join(...).
    """    
    if sep != ntpath.sep:
        # Linux
        drive = posixpath.join(posixpath.sep,s)
    else: # pragma: no cover
        # Windows
        drive = ntpath.join(s+":",ntpath.sep)
    return drive

def Popen(command, verbosity=1, encoding="utf-8",  **kwargs): # pragma: no cover
    """
    Run command line string "command" in a separate subprocess. 
    Show output in current console window in dependence of verbosity level:
    - 0 --> Quiet
    - 1 --> Only show errors
    - 2 --> Show every command line output.
    
    @author: garb_ma    
    @param: command, verbosity
    @type: string, integer
    """       
    shell = kwargs.get("shell",not IsDockerContainer() or isinstance(command, six.string_types))
    ## Output standard and error messages in dependence of verbosity level.     
    if shell and not kwargs.get("collect",True):
        p = subprocess.check_call(command)
        return p
    p = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, 
    stderr=subprocess.PIPE, shell=shell, env=kwargs.get("env",os.environ.copy()), universal_newlines=kwargs.get("raw",False))
    # Define output options.
    if kwargs.get("raw",False):
        return p
    elif kwargs.get("collect",True):
        stdout, stderr = p.communicate()           
        # Output standard and error messages in dependence of verbosity level. 
        if verbosity >= 2 and IsNotEmpty(stdout):                          
            print((stdout.decode(encoding,errors='ignore').replace(kwargs.get("replace","\n"), '')))  
        if verbosity >= 1 and IsNotEmpty(stderr):                                              
            print((stderr.decode(encoding,errors='ignore').replace(kwargs.get("replace","\n"), '')))
    else:
        ## Output standard output and parse it directly as is flows in 
        while True:
            stdout = p.stdout.readline()
            # Poll process for new output until finished
            if not IsNotEmpty(stdout) and p.poll() is not None:
                break
            if verbosity >= 2 and IsNotEmpty(stdout):                          
                sys.stdout.write(stdout.decode(encoding,errors='ignore').replace(kwargs.get("replace","\n"), ''))
                sys.stdout.flush()
        # Collect error messages and parse them directly to system error output
        _, stderr = p.communicate()
        if verbosity >= 1 and IsNotEmpty(stderr):                          
            sys.stderr.write(stderr.decode(encoding,errors='ignore').replace(kwargs.get("replace","\n"), ''))
            sys.stderr.flush()
    # Return subprocess
    return p

def SSHPopen(ssh_client, command, verbosity=1, **kwargs): # pragma: no cover
    """
    Run command line string "command" in a separate SSH client process. 
    Show output in current console window in dependence of verbosity level:
    - 0 --> Quiet
    - 1 --> Only show errors
    - 2 --> Show every command line output.
    
    @author: garb_ma    
    @param: command, verbosity
    @type: string, integer
    """             
    _, stdout, stderr = ssh_client.exec_command(command, get_pty=kwargs.get("tty",False))
    
    # Return results directly
    if not kwargs.get("collect",True) and verbosity >= 1: 
        for line in iter(lambda: stdout.read(2048).decode('utf-8','ignore'),""): 
            try: 
                _ = line; eval('print(line, end="")');
            except: pass
        return stdout.channel.recv_exit_status()
    
    # Output is collected and parsed at the end
    sexit = stdout.channel.recv_exit_status()
    
    sout = stdout.readlines()
    serr =  stderr.readlines()
    
    if verbosity >= 2 and sout:                          
        print("".join(sout))      
    if verbosity >= 1 and serr:                                              
        print("".join(serr)) 
             
    return sexit

def ConvertExcel(excel_file, output=None, **kwargs): # pragma: no cover
    """
    Utility function to convert a given *XLSX file to an *XLS.
    """
    # Get user-defined output folder. Defaults to current working directory
    outdir = output
    if not outdir: outdir = os.getcwd()
    excel = os.path.abspath(excel_file)
    # Create a temporary Powershell script
    ps = ".".join([str(next(tempfile._get_candidate_names())).replace("_",""),"ps1"])
    # Check operating system and available options
    try: 
        # Operating system is not supporting the requested operation
        if not GetPlatform() in ["windows"] or not GetExecutable("powershell"): raise OSError
    except OSError:
        # We are in a Docker container. We have options.
        if IsDockerContainer() and not GetExecutable("libreoffice") and kwargs.get("silent_install",IsDockerContainer()): 
            subprocess.check_call(["sudo","apt-get","update"])
            subprocess.check_call(["sudo","apt-get","install","-y","libreoffice"])
        # At this point - libreoffice has be exist. If not, raise an error
        try: 
            if not GetExecutable("libreoffice"): raise OSError
        except: raise NotImplementedError
        ## Use libreoffice for conversion on Linux
        # Ensure that the dynamic link path is correct
        # Fix for Issue: https://askubuntu.com/questions/1237381/undefined-symbol-error-when-starting-libreoffice-in-ubuntu-20-04
        else: command = ["libreoffice","--headless","--convert-to", "xls",PathLeaf(excel)]
    # Execute powershell script on Windows
    else: command = ["powershell.exe", '.\\'+ps, PathLeaf(excel)]
    # Operate fully in a temporary directory
    with TemporaryDirectory():
        xlsx = PathLeaf(excel)
        shutil.copyfile(excel, xlsx)
        # Populate the temporary script. Open the input Excel file and convert to legacy version
        with open(ps, 'w') as f:
            f.write(textwrap.dedent('''\
                param ($File)
                $myDir = split-path -parent $MyInvocation.MyCommand.Path
                $excelFile = "$myDir\\" + $File
                $Excel = New-Object -ComObject Excel.Application
                $wb = $Excel.Workbooks.Open($excelFile)
                $out = "$myDir\\" + (Get-Item ("$myDir\\" + $File) ).Basename + ".xls"
                $Excel.DisplayAlerts = $false;
                $wb.SaveAs($out, 56)
                $Excel.Quit()        
            '''))
        # Execute command
        subprocess.check_call(command, env=os.environ.copy() 
                                                if not GetPlatform() in ["linux"] else dict(os.environ, LD_PRELOAD="/usr/lib/x86_64-linux-gnu/libfreetype.so.6"))
        shutil.copyfile(xlsx.replace(".xlsx",".xls"),os.path.join(outdir,xlsx.replace(".xlsx",".xls")))
    # Return the output path of the file created by this function
    return os.path.join(outdir,xlsx.replace(".xlsx",".xls"))

def CreateArchive(output, source=None, exclude=[".git",".svn","__pycache__"], **kwargs):
    """
    Create an archive from the given source directory. Defaults to the current project.
    
    @param: output - Absolute output path
    @param: source - Source path. Defaults to the current project.
    @param: exclude - Files and directories to be ignored
    """
    # Additional internal filter functions
    def tar_exclude(tarinfo):
        """
        Exclude pattern for tar
        """
        local = set(tarinfo.name.split(posixpath.sep))
        if local.intersection(set(exclude)): return None
        return tarinfo
    
    # Defaults to this project
    from_source = GetPyXMakePath()
    if source: from_source = source
    
    # Get absolute paths
    output_filename=os.path.abspath(output); 
    source_dir=os.path.abspath(from_source); 
    
    # Archive operation
    if PathLeaf(output_filename).split(".")[1].lower() in ["zip"]:
        archive = zipfile.ZipFile(output_filename,"w", zipfile.ZIP_DEFLATED)
        rootlen = len(source_dir) + 1
        # Iterate through the given folder. Skip predefined folders
        for dirpath, _, filenames in os.walk(source_dir):
            for filename in filenames:
                # Write the file named filename to the archive,
                filepath   = os.path.join(dirpath, filename)
                parentpath = os.path.relpath(filepath, source_dir)
                # Do not include .git or .svn folders!
                if parentpath.startswith((".")) or any(PathLeaf(filepath) == x for x in exclude): continue
                if any(x in filepath.replace(PathLeaf(filepath),"") for x in exclude): continue              
                # Add path to archive
                archive.write(filepath, filepath[rootlen:])
    else:
        # Allow modification of compression level
        compression =  PathLeaf(output_filename).split(".")[-1]
        archive = tarfile.open(output_filename, "w" + "%s" % (":"+compression if compression in ["gz","bz2","xz"] else ""));
        archive.add(source_dir, arcname=os.path.basename(source_dir), filter=tar_exclude); 
    archive.close()
    
    # Does the output file exists
    return os.path.exists(output)

def GetResizedImage(image, size, **kwargs): # pragma: no cover
    """
    Resize a given image (absolute path) and returns a resized image object.
    
    @param: source - Source path. Must be an absolute path to the icon
    @param: size - Single integer value representing the new icon size
    """
    # Local imports
    from PIL import Image, ImageOps, ImageChops
    # Utility function definitions
    def hasPadding(im):
        """
        Utility function to check for the existence of an image border
        """
        bg = Image.new(im.mode, im.size, im.getpixel((0,0))) #@UndefinedVariable
        diff = ImageChops.difference(im, bg)
        diff = ImageChops.add(diff, diff, 2.0, -100)
        bbox = diff.getbbox()
        return all((bbox[0], bbox[1], (bbox[0] + bbox[2]) <= im.size[0], (bbox[1] + bbox[3]) <= im.size[1]))
    # Fetch user input
    base_image = copy.deepcopy(image); base_width = size
    base_offset = int(max(2,kwargs.get("base_offset",20)))
    # Open the image and check for a predefined boarder
    icon = Image.open(base_image);  #@UndefinedVariable
    # Only add padding when there is now initial border
    base_padding = not hasPadding(icon) and base_offset >= 0
    # If now boarder is found
    if base_padding: base_width -= base_offset
    # Resize the image to its optimal proportions
    wpercent = (base_width / float(icon.size[0]))
    hsize = int((float(icon.size[1]) * float(wpercent)))
    # Resample the image. Try best algorithm first, but define also a fallback solution
    try:  icon = icon.resize((base_width, hsize), Image.ANTIALIAS)  #@UndefinedVariable
    except: icon = icon.resize((base_width, hsize), Image.Resampling.LANCZOS) #@UndefinedVariable
    # Add an additional boarder
    if base_padding: icon = ImageOps.expand(icon, border=(int(base_offset//2),)*4, fill=icon.getpixel((0,0)) )
    # Return an image object
    return icon

def ConcatenateFiles(filename, files, source=os.getcwd(), ending=''):
    """
    Concatenate all files into one.
    """
    FileRead = 0       
        
    # Concatenate all files into one temporary file
    with open(filename,'wb') as wfd:
        for f in [os.path.join(source,cs) if IsNotEmpty(str(os.path.splitext(cs)[1])) 
                    else os.path.join(source,cs+ending) for cs in files]:
            # Only attempt to open a file if it exits            
            if not os.path.exists(f): continue
            # All files at this point exist
            if FileRead > 0:
                # Add a empty line between two source file includes
                wfd.write("\n\n".encode())
            with open(f,'rb') as fd:
                shutil.copyfileobj(fd, wfd, 1024*1024*10)
            FileRead += 1
            
def ReplaceTextinFile(filename, outname, replace, inend='', outend='',  source=os.getcwd(), **kwargs):
    """
    Replace all occurrences of replace in filename.
    """         
    Inputfile = os.path.join(source,filename+inend)
    Outputfile = outname+outend
    try: 
        # Modern convention
        with io.open(Inputfile, errors=kwargs.get("error_handling","replace"), encoding="utf-8") as infile, io.open(Outputfile, 'w', encoding="utf-8") as outfile:
            for line in infile:
                for src, target in replace.items():
                    line = line.replace(src, target)
                outfile.write(line)
    except: 
        # Legacy version
        with open(Inputfile) as infile, open(Outputfile, 'w') as outfile:
            for line in infile:
                for src, target in replace.items():
                    line = line.replace(src, target)
                outfile.write(line)        

@autotest([site.getuserbase(),site.getusersitepackages()]*2, site.getuserbase())
def RemoveDuplicates(ListofStrings,Duplicate=""):
    """
    Remove all duplicates in a list of strings
    """    
    count = 0; result = [] 
    
    # Loop over all elements in the flattened list of strings
    for ele in list(ArbitraryFlattening(ListofStrings)): 
        var = " ".join(ele.split())
        # Collect all duplicates
        if var == str(Duplicate): 
            count += 1
            continue
        else: 
            if count != 0:
                ## Previous entry was a duplicate. Add one element finally 
                # and continue as usual
                result.append(str(Duplicate)) 
                count = 0        
            result.append(var.strip())
            
    # Return results
    return result

def RemoveArguments(ArgumentParser, ListofArguments): # pragma: no cover
    """
    Delete deprecated command line arguments from a parser
     
    @author: Marc Garbade, 10.02.2025
    @note: Inspired from: https://stackoverflow.com/questions/32807319/disable-remove-argument-in-argparse/32809642#32809642
    """
    ## Create a list of all arguments to be removed.
    # Accepts both strings and lists
    names = []; names.append(ListofArguments)
    names = ArbitraryFlattening(names)
    # Iterate through all given arguments for removal
    for dest in ArbitraryFlattening(names):
        for action in ArgumentParser._actions:
            if vars(action)['dest'] == dest:
                if vars(action)["option_strings"]:
                    # We have an optional argument
                    ArgumentParser._optionals._remove_action(action)
                else:
                    # We have a positional argument
                    ArgumentParser._positionals._remove_action(action)
    # Return nothing. Modify the parser directly
    return ArgumentParser

def DeleteFilesbyEnding(identifier): # pragma: no cover
    """
    Delete all files from workspace
    
    @author: Marc Garbade, 26.02.2018
    
    @param: identifier: A tuple specifying the files to remove.
    @type: Tuple
    """  
    for f in os.listdir(os.getcwd()):
        if f.endswith(identifier):
            os.remove(f)
            
def DeleteRedundantFolders(Identifier, Except=[], ignore_readonly=False): # pragma: no cover
    """
    Delete all redundant folders from the current workspace
    """     
    def _IgnoreReadOnly(action, name, exc):
        """
        Delete read-only folders as well
        """     
        os.chmod(name, stat.S_IWRITE)
        os.remove(name)
    
    # Search for this pattern
    pattern = os.path.join(os.getcwd(), Identifier)
    
    # Loop over all items in the current working directory
    for item in glob.glob(pattern):
        if not os.path.isdir(item): continue
        directory = r'\\?\ '.strip()+item
        if ignore_readonly: 
            # Delete read-only folders as well
            shutil.rmtree(directory, onerror=_IgnoreReadOnly)
            continue
        # All other cases
        shutil.rmtree(directory)     

def AddFunctionToObject(_func, _obj): # pragma: no cover
    """
    Bind a function to an existing object.
    """
    return MethodType(_func, _obj)

@autotest(type('Class', (object,), {"data": np.array([0, 1, 2, 3])}))
def PrepareObjectforPickling(_obj):
    """
    Prepare a object for pickling and convert all numpy  
    arrays to python defaults (2to3 compatible). 
    """
    _dictobj  = _obj.__dict__.copy()
    _dictobj['__np_obj_path'] = []      
    for path, value in ObjectWalk(_dictobj):
        if isinstance(value, (np.ndarray, np.generic)):
            parent = _dictobj
            for step in path[:-1]: # pragma: no cover
                parent = parent[step]
            parent[path[-1]] = value.tolist()         
            _dictobj['__np_obj_path'].append(path[-1])                         
    return _dictobj

@autotest({"data": [[0, 1],[2, 3]], "__np_obj_path": ["data"]})    
def RecoverDictionaryfromPickling(_dict):
    """
    Restore the original dictionary by converting python defaults to their 
    numpy equivalents if required  (2to3 compatible).
    """
    _dictobj = _dict.copy()
    # Recreate serialized arrays accordingly
    for key, value in _dictobj.items():
        if key in _dictobj.get('__np_obj_path',[]):
            _dictobj[key] = np.float64(value)
            if len(np.shape(value)) == 2:
                _dictobj[key] = np.asmatrix(value)
    # Return result
    return _dictobj

def PathLeaf(path):
    """
    Return the last item of an arbitrary path (its leaf).
    """ 
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)

def ArbitraryFlattening(container):
    """
    Restore the original dictionary by converting Python defaults to their 
    numpy equivalents if required  (2to3 compatible).
    """
    for i in container:
        if isinstance(i, (list,tuple, np.ndarray)):
            for j in ArbitraryFlattening(i):
                yield j
        else:
            yield i

@autotest('{"data": True}')    
def ArbitraryEval(expression):
    """
    Evaluate a given expression using ast.literal_eval while treating every string as raw. 
    """
    node_or_string = expression
    if isinstance(expression,str): node_or_string = r"%s" % expression if GetPlatform() in ["windows"] else r"'%s'" % expression
    return ast.literal_eval(node_or_string)

def MoveIO(src, dest, verbose=0): # pragma: no cover
    """
    Move given src to defined dest while waiting for completion of the process.
    """       
    # Copy archive to destination folder. Wait for completion
    if GetPlatform() == "windows":
        copy = "move"
    else:
        copy = "mv"
    # Copy data to result directory, wait for completion
    p = Popen(" ".join([copy,src,dest]), verbosity=verbose)
    return p

@autotest("Make.py")
def FileWalk(source, path=os.getcwd()):
    """
    Walk recursively through path. Check if all files listed in source are present. 
    If True, return them. If False, return all files present in the given path.
    """            
    # Initialize all variables
    files = list([]); request = source;
    # Support both list and string input
    if not isinstance(request, (list,tuple,)): request = [request]
    # These are all uploaded files
    InputFiles = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]    
    try: # pragma: no cover
        # Check if source code files have been specified. Otherwise, use everything from the ZIP file
        if all(np.array([len(request),len(InputFiles)]) >= 1):
            # Ignore file extension here. This will interfere with the checks later on.
            if set([os.path.splitext(x)[0] for x in request]).issubset(set([os.path.splitext(f)[0] for f in InputFiles])):
                files.extend(request)
        else:
            files.extend(InputFiles)
    except TypeError:
        files.extend(InputFiles)
        pass
    
    return files

@autotest(object, AbstractBase)
def ClassWalk(reference, cls):
    """
    Recursively find a class object by name and return its object from another class.
    
    @note: Returns None if reference cannot be resolved. Can be safely used with AbstractBase classes and reload.
    """
    result = None
    for x in getattr(cls, "__bases__"): 
        if x.__name__ in [reference.__name__]:        
            result = copy.deepcopy(x)
            break
        else: result = ClassWalk(reference,x)
    return result

@autotest(site.getusersitepackages(), contains="DLR")            
def PathWalk(path, startswith=None, endswith=None, contains=None, **kwargs):
    """
    Walk recursively through path. Exclude both folders and files if requested. 
    """
    def Skip(x, starts, contains, ends):
        """
        Evaluate skip condition
        """
        if isinstance(starts, (six.string_types, tuple, list)):
            if x.startswith(starts if not isinstance(starts,list) else tuple(starts)):
                return True
        if isinstance(contains, (six.string_types, tuple, list)):
            tmp = list([]); tmp.append(contains) 
            tmp = tuple(ArbitraryFlattening(tmp))
            if any(s in x for s in tmp):
                return True
        if isinstance(ends, (six.string_types, tuple, list)):
            if x.endswith(ends if not isinstance(ends,list) else tuple(ends)):
                return True
        return False
    
    for root, dirs, files in os.walk(os.path.normpath(path)):
        if kwargs.get("exclude",any([startswith, endswith, contains])):
            files = [f for f in files if not Skip(f,startswith,contains,endswith)]
            dirs[:] = [d for d in dirs if not Skip(d,startswith,contains,endswith)]         
        yield root, dirs, files

@autotest(AbstractMethod)
def ObjectWalk(obj, path=(), memo=None):
    """
    Walk recursively through nested python objects.
    
    @author: Yaniv Aknin, 13.12.2011
    
    @param: obj, path, memo
    @type: object, list, boolean
    """
    string_types = six.string_types
    iteritems = lambda mapping: getattr(mapping, 'iteritems', mapping.items)()    
    if memo is None:
        memo = set()
    iterator = None
    if isinstance(obj, dict):
        iterator = iteritems
    elif isinstance(obj, (list, set, tuple)) and not isinstance(obj, string_types):
        iterator = enumerate
    if iterator:
        if id(obj) not in memo:
            memo.add(id(obj))
            for path_component, value in iterator(obj):
                for result in ObjectWalk(value, path + (path_component,), memo):
                    yield result
            memo.remove(id(obj))
    else:
        yield path, obj
        
@autotest(sys.executable, terminate=False)
def ProcessWalk(executable, terminate=True):
    """
    Walk through all active processes on the host machine, 
    
    @author: garb_ma
    """
    import psutil

    # Iterate through all active processes  
    for proc in psutil.process_iter():
        if os.getpid() == proc.pid:
            continue # Skip self.
        try:
            for key, value in proc.as_dict().items():
                if executable in str(key) or executable in str(value):
                    proc_delimn = " "; processName = proc.name(); processID = proc.pid; 
                    if executable in str(processName): # pragma: no cover
                        if terminate: proc.kill()
                        print("==================================")
                        print("Found SSH process @ " + str(proc_delimn.join([str(processName),':::',str(processID)])))
                        if terminate: print("The process is terminated.")
                        print('==================================')
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

## Adding compatibility alias for logging function
setattr(sys.modules[__name__],"setLogger", getattr(sys.modules[__name__],"GetLogger"))
setattr(sys.modules[__name__],"getLogger", getattr(sys.modules[__name__],"GetLogger"))
  
if __name__ == '__main__':
    pass            