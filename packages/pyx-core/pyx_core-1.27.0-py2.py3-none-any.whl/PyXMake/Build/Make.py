# -*- coding: utf-8 -*-
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %                                                                Make Module - Classes and Functions                                                            %
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
"""
Create a make object to define the building environment and to execute the 
build commands. The make event is subdivided in a pre-, main- and a post-build 
event.
 
@note: PyXMake module                   
Created on 20.03.2018    

@version:  1.0    
----------------------------------------------------------------------------------------------
@requires:
       - 

@change: 
       -    
   
@author: garb_ma                                                     [DLR-FA,STM Braunschweig]
----------------------------------------------------------------------------------------------
"""

## @package PyXMake.Build.Make
# Create a make object to define the building environment.
## @author 
# Marc Garbade
## @date
# 20.03.2018
## @par Notes/Changes
# - Added documentation // mg 29.03.2018
try:
    from builtins import object
except ImportError:
    pass

try:
    FileNotFoundError
except NameError:
    FileNotFoundError = IOError # @ReservedAssignment

import sys, os, platform
import argparse
import paramiko
import abc, six
import shutil
import inspect
import stat
import json
import copy
import shlex
import ntpath
import posixpath
import random, string
import subprocess
import multiprocessing
import tempfile
import colorsys
import psutil
import re
import io
import site
import uuid
import socket
import getpass
import base64
import logging
import warnings
import textwrap
import importlib

import numpy  as np

from packaging import version
from shutil import copyfile
from types import MethodType
from collections import OrderedDict #@UnresolvedImport
from PIL import Image, ImageColor

try: # pragma: no cover
    ## Add additional path to environment variable
    if os.path.exists(os.path.join(sys.prefix,"conda-meta")) and not os.path.join(sys.prefix,"conda-meta") in os.getenv("PATH",""): 
        os.environ["PATH"] = os.pathsep.join([os.path.join(sys.prefix,"Library","bin"),os.getenv("PATH","")])      
    # Now the requests module can be load w/o errors.
    import requests
# Fail gracefully
except: pass

from ..Tools import Utility

## Absolute system path to PyXMake.
PyXMakePath = Utility.GetPyXMakePath() 
## Absolute system path to configuration files.
Path2Config = os.path.join(PyXMakePath,"Build","config")
## This is the default build option for all classes/methods inherited from this module going forward.
# Only active when executing PyXMake in developer mode. Should default to False in all other cases. Can be overwritten.
AllowDefaultMakeOption = bool(int("-1" if __debug__ or not getattr(sys,"frozen",False) else int(os.getenv("pyx_default_make_opt","0"))) == -1) and \
    not any(path in __file__ for path in site.getsitepackages())

## Create an alias using default logger for all print statements 
logger = logging.getLogger(__name__)
# setattr(sys.modules[__name__],"print", logger.info)

## @class PyXMake.Build.Make.OS
# Abstract base class for all system subclasses. Inherited from built-in ABCMeta & object. 
# Compatible with both Python 2.x and 3.x.  
class OS(Utility.AbstractBase):
    """
    Base class of all supported subsystems.
    """
    def __init__(self, *args, **kwargs): 
        ## String identifier of current instance.                
        self.SystemObjectKind = "Base"
        pass
    
## @class PyXMake.Build.Make.NT
# Abstract base class for all NT subclasses. Inherited from built-in ABCMeta & object. 
# Compatible with both Python 2.x and 3.x.  
@six.add_metaclass(abc.ABCMeta)
class NT(OS):
    """
    Inherited class to NT projects without any presets.
    """    
    @abc.abstractmethod      
    def __init__(self, *args, **kwargs):
        """
        Initialization of NT class object.
        """
        super(NT, self).__init__(*args, **kwargs)
        ## String identifier of current instance.                
        self.SystemObjectKind = "NT"

## @class PyXMake.Build.Make.POSIX
# Abstract base class for all POSIX subclasses. Inherited from built-in ABCMeta & object. 
# Compatible with both Python 2.x and 3.x.  
@six.add_metaclass(abc.ABCMeta)
class POSIX(OS):
    """
    Inherited class to POSIX projects without any presets.
    """    
    @abc.abstractmethod      
    def __init__(self, *args, **kwargs):
        """
        Initialization of POSIX class object.
        """
        super(POSIX, self).__init__(*args, **kwargs)
        ## String identifier of current instance.                
        self.SystemObjectKind = "POSIX"
        ## Overwrite create method in all subclasses to use a predefined MakeFile for all builds. This implements
        # the use of gcc, g++ and gfortran as well as Mingw64 and Linux shell support. Convoluted, but working.
        setattr(self, "create", self.__create__)
        # Copy Makefile to current scratch directory.
        copyfile(os.path.join(Path2Config,"stm_makefile"), os.path.join(self.scrtdir,"Makefile"))
        # Add temporary Makefile to tuple scheduled for removal
        self.temps = self.temps + ("Makefile",)
    
    def __create__(self, **kwargs): # pragma: no cover
        """
        Unified create function replacing all create commands of ALL classes when used with Mingx64 or on Linux. All builds are solely
        defined by one unified Makefile. in these cases.
        """
        # Access some sub-packages
        from PyXMake.Build import __install__ #@UnresolvedImport
        from PyXMake.VTL import GetPreprocessingCommand
        from packaging.version import parse

        # Space delimiter
        delimn = " ";
        
        # Create a local copy of the current environment
        self.environ = copy.deepcopy(getattr(os.environ,"_data",{}))

        # Validate third party dependencies
        if Utility.GetPlatform() in ["windows"] and not Utility.GetExecutable("choco"): # pragma: no cover
            os.environ["pyx_user_install"] = "chocolatey"
            os.system(" ".join([sys.executable,os.path.abspath(__install__.__file__)]))
  
        ## Add local binary directory to the global path
        os.environ["PATH"] = os.pathsep.join([os.getenv("PATH"),os.path.join(os.path.dirname(os.path.abspath(__install__.__file__)),"bin","chocolatey")])

        try: 
            # Get base path, get compiler path defaulting to the latest version and get base initialization shell script
            msys2_base_path, msys2_compiler_path, msys2_shell_initialization = self.setup(mingw = Utility.GetExecutable("choco"))
            # Update PreProcessing command if default is not available
            if self.hasFoss and ("fpp" in str(getattr(self,"precmd",None) or "") and not Utility.GetExecutable("fpp")): # pragma: no cover
                self.precmd = GetPreprocessingCommand(1).split() + self.precmd.split()[4:]; self.precmd.insert(-1,"-o")
                self.precmd = delimn.join(self.precmd)
                # On NT systems using ming, the quotes have to be changed. Otherwise, a syntax error occurs.
                if Utility.GetPlatform() in ["windows"]: self.precmd = self.precmd.replace('"',"'")
                # Assemble the final command
                self.precmd = delimn.join([msys2_shell_initialization,"-c",'"%s"' % self.precmd])
        except: 
            # Only meaningful on windows systems
            if Utility.GetPlatform() in ["windows"]: raise ImportError
            # Set a dummy value
            msys2_base_path = ""
            msys2_compiler_path = ""
            msys2_shell_initialization = ""
    
        # Go into scratch directory (if defined). This directory has to include a Makefile.
        with Utility.ChangedWorkingDirectory(self.scrtdir):             
    
            # Verify that module files are in the same path as any output from f2py
            if self.MakeObjectKind in ['Py2X',"f2py"] and not self.makecmd.find("meson") != -1:
                # Do not explicitly refer to this folder for include when using meson as a build backend
                self.incdirs.append(os.path.join(os.getcwd(),"tmp","Release")) 
            
            # Rewrite all path to be Linux/Mingw64 compliant
            os.environ["pyx_compiler"] = os.getenv("pyx_compiler").replace(ntpath.sep,posixpath.sep)
            
            if Utility.GetPlatform() in ["windows"]:
                # Only add dependencies for MSYS on Windows.
                os.environ["pyx_ldflags"] = delimn.join(["-L"+os.path.join(msys2_base_path,"mingw64","lib"),"-L"+msys2_compiler_path]) + delimn
                if parse(np.__version__) >= parse("1.22.0"): os.environ["pyx_ldflags"] = delimn.join([os.getenv("pyx_ldflags",""), "-D__STDC_NO_THREADS__"]) + delimn

            # Add all include paths to the command string
            for x in ['-I"'+x+'" ' for x in self.incdirs]: os.environ["pyx_ldflags"] = os.getenv("pyx_ldflags","") + x
                
            # Add all dependency paths to the command string
            for x in ['-L"'+x+'" ' for x in self.libdirs]: os.environ["pyx_ldflags"] = os.getenv("pyx_ldflags","") + x   
            
            # Add all required libraries to the command string
            for x in ['-l'+x+' ' for x in self.libs]: os.environ["pyx_ldflags"] = os.getenv("pyx_ldflags","") + x   
                
            # Publish additional user commands as an environment variable
            os.environ["pyx_ldflags"] = os.getenv("pyx_ldflags","").replace("\\","/")
            
            # Pre-build event  (if required)
            try: 
                if self.precmd != '' and self.precmd.strip() != self.iniCompiler:
                    command = self.precmd.split(delimn); command.insert(-2,"-D__GFORTRAN__");
                    # Assemble command
                    self.precmd = delimn.join(command)
                    # Execute the command
                    Utility.Popen(self.precmd, self.verbose)
            except: pass
          
            # Loop over all source files and apply cross-compilation pre-processing to all of them.
            try:
                for source in os.getenv("pyx_source").split(delimn):
                    Make.F2CPreprocessing(source)
            except FileNotFoundError:
                    if os.path.isfile(self.intermediate_wrapper):      
                        Utility.ReplaceTextinFile(self.intermediate_wrapper, self.wrapper_module, {'%pyx_source%':'"'+self.buildname+'"'}, source=self.scrtdir)     
                        Make.F2CPreprocessing(self.wrapper_module)
                        os.environ["pyx_source"] = self.wrapper_module
            except UnicodeError: pass
   
            # Strip decorator commands from the original make command. These are relevant for the Makefile as well.
            os.environ["pyx_cflags"] = delimn.join([os.getenv("pyx_cflags",""),delimn.join([x for x in self.makecmd.split(delimn) if x.startswith("-D")])])
            
            ## Base command for all make commands
            # Windows with MSYS2
            command = msys2_shell_initialization
            # Linux
            if Utility.GetPlatform() != "windows": command = delimn.join([';export PYX_BUILDID="'+os.environ["pyx_buildid"]+'"',';export PYX_SOURCE="'+os.environ["pyx_source"]+'"',";bash"])
            
            # If used with Python and numpy, check if numpy version is sufficient and patch-able.
            if self.MakeObjectKind in ['Py2X',"f2py"]: # pragma: no cover


                # Cross compilation flags (GNU style format)
                os.environ["pyx_cflags"] += delimn + "-ffree-line-length-0"
                if self.makecmd.find("-fixed") != -1:
                    os.environ["pyx_cflags"] += delimn + "-f%s-form" % "fixed"
                else:
                    os.environ["pyx_cflags"] += delimn + "-f%s-form" % "free"
                    
                # Output detailed information from f2py when increasing the verbose level
                if self.verbose >= 2: os.environ["pyx_ldflags"] += delimn + "--verbose"
                else: os.environ["pyx_ldflags"] += delimn + "--quiet"
                
                if self.makecmd.find("--backend") != -1:
                    backend = str(self.makecmd.split("backend=")[-1].split()[0])
                    os.environ["pyx_ldflags"] += delimn + "--backend=%s" % backend
                    if backend in ["meson"]: os.environ.update({"meson_ldflags":delimn.join(["-static -static-libgcc -static-libgfortran",os.getenv("LDFLAGS","")])})
                    
                # Add additional command line options to the final command
                if Utility.GetPlatform() != "windows":
                    # Fetch compiler request on Linux. Remove file extension and path from f2py call.
                    command = command.split(delimn); compiler = Utility.PathLeaf(os.getenv("pyx_compiler"))
                    command.insert(0,'export PYX_COMPILER="'+compiler.replace(os.path.splitext(compiler)[1],"")+'"'); 
                    command.insert(0,'export PYX_CFLAGS="'+os.getenv("pyx_cflags")+'"')
                    command.insert(0,'export PYX_LDFLAGS="'+os.getenv("pyx_ldflags")+'"')
                    command.insert(0,'export LD_RUN_PATH="'+os.pathsep.join(self.libdirs)+'"')
                    command.insert(0,'export NPY_DISTUTILS_APPEND_FLAGS=1')
                    command = delimn.join(command)
                
                ## This beauty ensures backwards compatibility with older f2py versions. Upon 1.19, there persists a bug in the original implementation, 
                # preventing the correct version to be identified. This bug has since been resolved. If the version is sufficient, simply run everything on a dummy file.
                # We have to always apply the patch for f2py here.
                with tempfile.NamedTemporaryFile(mode='w+') as __, self.patch(command=self.makecmd, verbose=self.verbose, **kwargs) as ___:       
                    try:
                        # Execute build command
                        params = {} if not Utility.IsDockerContainer() else {"shell":True,"collect":True}
                        # Modify global encoding of the old interpreter
                        environment = os.environ.copy();
                        # Update environment variable
                        if sys.version_info <= (3, 0): params.update({"env":environment})
                        # Do not remove newline from output strings
                        if Utility.GetPlatform() in ["windows"] and not Utility.IsDockerContainer(): 
                            params.update({"replace":""})
                        command = delimn.join([command,"-c",'"make f2py"'])
                        # Execute the command
                        Utility.Popen(command, verbosity=self.verbose, **params)
                    except:
                        pass
                    finally:
                        # Delete temporary folders
                        if os.path.exists("tmp") or os.path.exists(os.getenv("pyx_buildid")):
                            try:
                                shutil.rmtree("tmp"); shutil.rmtree(os.getenv("pyx_buildid"))        
                            except (FileNotFoundError, OSError) as _: pass
                            
            elif self.MakeObjectKind in ['Fortran',"CCxx"]:          
                # Cross compilation flags (GNU style format)
                if self.makecmd.find("-fixed") != -1:
                    os.environ["pyx_cflags"] += delimn + "-ffixed-line-length-132 -f%s-form" % "fixed"
                elif self.MakeObjectKind in ['Fortran']: 
                    os.environ["pyx_cflags"] += delimn + "-ffree-line-length-0 -f%s-form" % "free"
                
                # Add additional command line options to the final command
                if Utility.GetPlatform() != "windows":
                    command = command.split(delimn); 
                    command.insert(0,'export PYX_CFLAGS="'+os.getenv("pyx_cflags")+'"')
                    command.insert(0,'export PYX_LDFLAGS="'+os.getenv("pyx_ldflags")+'"')
                    command = delimn.join(command)
                
                # Execute build command
                command = delimn.join([command,"-c",'"make"'])
                Utility.Popen(command, verbosity=self.verbose, replace="")
                
                # Add temporary files to tuple scheduled for removal
                self.temps = self.temps + (".o",)   
                
                # Remove module files. We have to process them later.
                _ = list(self.temps);  
                if ".mod" in _: _.remove(".mod"); 
                self.temps = tuple(_)

                # Combine event. Combine multiple static libraries into ONE.
                if kwargs.get("combine", False):
                    mrifile = Utility.GetTemporaryFileName(extension=".mri"); mergedid = os.path.basename(self.outmodule)
                    # Fetch the current library extension
                    outlibs = os.listdir(getattr(self,"outlibs",self.outdir)); outext = os.path.splitext(outlibs[-1])[-1]
                    outlibs += [x for x in os.listdir(os.getcwd()) if x.endswith(outext)]
                    multi_libs = set([x for x in outlibs if mergedid in x])
                    # This is the final library name
                    merged_lib = mergedid+self.architecture+outext
                    # Remove old combined library from the list.     
                    try: multi_libs.remove(merged_lib)
                    except: pass
                    # Only execute this part when there are actual libraries to merge
                    if multi_libs:
                        # Collect all static libraries for the merger
                        for lib in multi_libs: 
                            # Only collect those libraries which are not present in the current working directory to avoid accidental overwrites.
                            if not os.path.exists(os.path.join(os.getcwd(),lib)): shutil.move(os.path.join(getattr(self,"outlibs",self.outdir),lib),os.path.join(os.getcwd(),lib))
                        # Iterate over all identified. Create MRI file from list
                        multi_libs = ["addlib %s" % x for x in multi_libs]
                        multi_libs.insert(0,"create %s" % merged_lib)
                        multi_libs.extend(["save","end"]) 
                        # Create MRI file 
                        with open(mrifile,"w") as mri:
                            for line in multi_libs: mri.write("%s\n" % line)
                        # Execute post build command
                        command = command.split(); command = delimn.join(command[:command.index("-c")])
                        command = delimn.join([command,"-c",'"make combine"'])
                        # Execute command
                        Utility.Popen(command, verbosity=self.verbose, replace="")
                        ## Add all remaining files to list of files scheduled for removal
                        self.temps += tuple(x for x in os.listdir(os.getcwd()) if x.endswith(os.path.splitext(merged_lib)[-1]) and not x.endswith(merged_lib))
                    self.temps += (".mri",)

            # Finish and delete redundant files and folders
            Utility.DeleteFilesbyEnding(self.temps)
             
            # Copy all unprocessed files to the output folder
            for x in os.listdir(os.getcwd()):
                try:
                    ## Accept both OutLibs and OutDir variable. Checks for existence of OutLibs first.
                    if os.path.isfile(x) and not x.startswith("."): shutil.move(x,os.path.join(getattr(self,"outlibs",self.outdir),x))
                except: pass
                     
            # Copy module and header files to output module folder (if required)
            if hasattr(self, "outlibs") and hasattr(self, "outmodule"):
                if self.outlibs != self.outmodule:
                    with Utility.ChangedWorkingDirectory(self.outlibs):
                        # Only create folders if any module or header files actually exists
                        if any([x.endswith((".mod",".h")) for x in os.listdir(os.getcwd())]): os.makedirs(self.outmodule, exist_ok=True)
                        for x in os.listdir(os.getcwd()):
                            if x.endswith((".mod",".h")): shutil.move(x,os.path.join(self.outmodule,x))
            
            # Remove environment variable in case of multiple builds
            os.environ.clear()
            os.environ.pop("pyx_cflags","")
            os.environ.pop("pyx_ldflags","")
            
            # Recreate environment upon job finished
            for k, v in getattr(self,"environ",{}).items():
                # Prevent problems when keys or values became encoded
                if hasattr(k,"decode"): k = k.decode()
                if hasattr(v,"decode"): v = v.decode()
                os.environ.update({k:v})
        pass

## @class PyXMake.Build.Make.Make
# Abstract base class for all make objects. Inherited from built-in ABCMeta & object. 
# Compatible with both Python 2.x and 3.x.  
class Make(Utility.AbstractBase):
    """
    Parent class for all make objects.
    """
    @abc.abstractmethod
    def __init__(self, BuildID, Srcs, scratch=os.getcwd(), verbose=0, *args, **kwargs):
        """
        Low-level initialization of parent class.
        """
        ## Base string of build object. 
        # Defines the base string of the current build object. The final build name
        # used in the instanced objects is assembled using this immutable base id.
        self.buildid = BuildID
        ## Source file or folders
        self.srcs = [] 
        self.srcs.append(Srcs)
        self.srcs = list(Utility.ArbitraryFlattening(self.srcs))
        # The given class is run bare. Child classes can be programmed to react properly to this situation
        self.bare = not BuildID and not self.srcs          
        ## Source file type
        self.stype = kwargs.get("stype",'Fortran')
        ## Level of verbosity of the current build object. 
        # Define the verbosity level of the current build object. Defaults to 0 and suppresses 
        # all outputs to the command line. A higher value increases the level of verbosity up to 
        # a maximum level of 2. 
        self.verbose = verbose
        ## Toggle between free open source software and commercial 3rd party libraries. On POSIX systems, 
        # only free open source software is supported. On Windows, the Intel Compiler Library as well as the package manager
        # MINGW64 are natively supported. All other variants have no supported presets.
        self.hasFoss = kwargs.get("foss", Utility.GetExecutable("choco") or Utility.GetPlatform() in ["linux"] or kwargs.get("bash",False))
             
        # Set scratch directory & default input/ output locations
        with Utility.ChangedWorkingDirectory(scratch):
            ## Current scratch directory         
            self.scrtdir = os.getcwd()
            ## Default search directory for source files.            
            self.srcdir = os.getcwd()
            ## Default search directory for output.
            self.outdir = os.getcwd()     
        
        # Read Intel path from Paths.log. Only if present 
        if os.path.exists(os.path.join(PyXMakePath,'Paths.log')):
            with open(os.path.join(PyXMakePath,'Paths.log')) as f:
                content = f.readlines()
            content = [x.strip() for x in content][20]
        # Do not use paths provided explicitly
        else: content = ""
        ## Path to Intel Fortran Compiler (read from Paths.log or empty).
        self.intelpath = content

        # Initialization of  tuple containing temporary files        
        ## Tuple of data to be removed after job completion.
        self.temps = ()   
        
        # Initialization of lists containing additional sources, modules or libraries
        ## List of include directories.
        self.incdirs = []
        ## List of library directories.
        self.libdirs = []
        ## List of actual libraries (by name) used during linking.
        self.libs = []
        
        # Initialization of list containing files to be copied to the output directory.
        ## List of files to be copied to the output directory after finish.
        self.copyfiles = []
        
        ## Default initialization of compiler script.
        # Only set on NT systems. There is no compiler initialization script for Linux
        self.iniCompiler = ""
        
        ## Define the architecture for the build directly by using the keyword argument "arch". 
        # Defaults to None, in which case the architecture is determined by using the python executable.
        self.setarch = True if kwargs.get('arch', None) in ['x86', 'x64'] else False     
        
        ## Default version of Microsoft visual studio used by the Intel Fortran Compiler. Defaults to 'vs2015'.
        self.msvsc = kwargs.get("msvsc",'vs2015')                   
        os.environ['pyx_msvsc'] = self.msvsc             
        
        # Set variables in dependence of identified system        
        if 'win' in sys.platform:   
             
            if (('32bit' in platform.architecture() and not self.setarch) or (self.setarch and kwargs.get('arch', None) == "x86")):
                # Set variables for x86
                os.environ['pyx_proc'] = 'x86'                
                os.environ['pyx_intel'] = 'ia32'
                ## Processor architecture
                self.architecture = 'x86'         
                                
            elif (('64bit' in platform.architecture() and not self.setarch) or (self.setarch and kwargs.get('arch', None) == "x64")):        
                # Set variables for x64
                os.environ['pyx_proc'] = 'amd64'    
                os.environ['pyx_intel'] = 'intel64'                               
                self.architecture = 'x64'  

            ## Executable batch script (including absolute system path) to set up the Intel Fortran Compiler.
            if kwargs.get("initialize",True): 
                # Set Intel Compiler path for backwards compatibility
                if not self.intelpath: _, self.intelpath, self.iniCompiler = self.setup(**kwargs)
                # Modern convention
                else: self.iniCompiler = self.setup(**kwargs)[-1]
            
        elif Utility.IsDockerContainer() and Utility.GetPlatform() in ["linux"]:
            # Set default environment variables
            os.environ["pyx_intel"] = "intel64_lin"
            # Distributed Intel runtime in Docker.
            self.intelpath = os.path.join(Utility.AsDrive("opt"),"intel","psxe_runtime","linux")
            # There is no difference on linux. This will default to x64 in all cases.
            self.architecture = Utility.GetArchitecture()            
                                                 
        elif 'linux' in sys.platform:
            # Set default environment variables
            os.environ["pyx_intel"] = ""
            # There is no difference on linux. This will default to x64 in all cases.
            self.architecture = Utility.GetArchitecture()
        
        ## Post build command. Defaults to an empty string.
        self.postcmd = ""
    
        # Always add MKL library
        ## Uses absolute system path of MKL library.
        if os.path.exists(os.path.join(self.intelpath,"mkl","include")):
            # Additional include source files. They are not part of the redistribution package
            mkl_include_path = os.path.join(self.intelpath,"mkl","include")
            self.incdirs.append(mkl_include_path)       
         
        if os.path.exists(os.path.join(self.intelpath,"mkl")):
            # Path to MKL and compiler library. These are part of any redistribution package.
            mkl_lib_path = os.path.join(self.intelpath,"mkl","lib",os.environ['pyx_intel'])
            mkl_compiler_path = os.path.join(self.intelpath,"compiler","lib",os.environ['pyx_intel'])
            self.libdirs.extend([mkl_lib_path, mkl_compiler_path])     
        
        # Update environment build path 
        if os.path.exists(os.path.join(self.intelpath,"bin",os.environ['pyx_intel'])):
            os.environ["PATH"] = ";".join([os.getenv("PATH",""),os.path.join(self.intelpath,"bin",os.environ['pyx_intel'])])
            
        # Collect all MKL include files (if given!)
        self._mkl_includes = []; mkl_paths = [x for x in self.incdirs if "mkl" in x]
        for path in mkl_paths: self._mkl_includes.extend([x for x in os.listdir(path) if (os.path.isfile(os.path.join(path,x)) and x.endswith((".f90",".F90",".for",".FOR",".f",".F",".f77",".F77")))])

        # Dynamic second inheritance in dependence of supplied keyword argument POSIX.
        self.__posix__(**kwargs)
        
        # Add all source files to list of files to remove from scratch folder. No exceptions.
        self.temps = self.temps + tuple((os.path.join(self.scrtdir,x) for x in self.srcs))
        pass

    def __posix__(self,**kwargs):
        """
        Request compatibility with Mingw64 and Linux.
        """
        # Dynamic second inheritance in dependence of supplied keyword argument POSIX.
        if kwargs.get("bash", self.hasFoss):
            try:
                # Attempt to initialize POSIX support
                POSIX.__init__(self)
            except:
                pass
        else:
            try:
                ## Delete prototype of create function. 
                # Its content was renamed to "create" in POSIX.__init__()
                delattr(self, "__create__")
            except:
                pass
            
    @staticmethod
    def __parser__(): # pragma: no cover
        """
        Default parser object for command line interface
        
        @author: Marc Garbade
        """                  
        # Process all known arguments
        parser = argparse.ArgumentParser(add_help=False)
        # Default parser object with settings shared by most commands.
        parser.add_argument('name', type=str, nargs=1, help="Name of the project")
        parser.add_argument('source', type=str, nargs=1, help="Absolute path to the source file directory.")
        parser.add_argument('-f', '--files', nargs='+', default=[], help="Source file or list of all source files in the order of compilation")
        parser.add_argument("-o","--output", type=str, nargs=1, help="Absolute path to output directory. Defaults to current project folder.")
        parser.add_argument('-i', '--include', nargs='+', default=[], help="Additional directories and files required for the build.")
        parser.add_argument('-s', '--scratch', nargs='+', default=[], help="Default scratch folder for the build. Defaults to current workspace.")
        parser.add_argument("-v","--verbosity", type=str, nargs=1, help="Level of verbosity. Defaults to 0 - meaning no output. Max value is 2.")
        # Return default parser object
        return parser

    @staticmethod    
    def Detach(): # pragma: no cover
        """
        Detach current console window from parent window.
        
        @author: Marc Garbade
        """          
        kwargs = {}
        # Set system/version dependent "start_new_session" analogs                
        if os.name == 'nt': # Windows
            DETACHED_PROCESS = 0x00000008          # 0x8 | 0x200 == 0x208           
            CREATE_NEW_PROCESS_GROUP = subprocess.CREATE_NEW_PROCESS_GROUP
            kwargs.update(creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP)  
        elif sys.version_info < (3, 2):  # Posix
            kwargs.update(preexec_fn=os.setsid)         # @UndefinedVariable
        else:  # Python 3.2+ and Unix
            kwargs.update(start_new_session=True)
            
        return kwargs
    
    @staticmethod
    def F2CPreprocessing(PreprocessingFile):
        """
        Replace incompatible Fortran PreProcessing directives with its C++ counterparts. 
        
        @author: schu_a1
        """
        try:
            # Resolving compatibility issue > Python 3.6
            from re.RegexFlag import MULTILINE
        except ImportError:
            # Python 3.5 & lower
            from re import MULTILINE
        
        def NegationDirective(matchobj):
            """
            Replace .not. with ! (e.g. .not. defined will be !defined)
            """
            newString = ""
            if matchobj.group(1) == ".NOT. ": 
                newString += "!"
                
            newString += "defined(%s)" % matchobj.group(2)
            return newString
    
        def LowerDirective(matchobj):
            """
            All initial directives are given in lower cases.
            """
            return "#" + matchobj.group()[1:].lower()
        
        # Definition of pattern to be substituted.
        decorator = re.compile("^!DEC\$ (?=IF|ELSE|ENDIF|END IF)",MULTILINE)
        addition = re.compile("^#(.*?)\.AND\.(.*?)", MULTILINE)
        either = re.compile("^#(.*?)\.OR\.(.*?)", MULTILINE)
        negation = re.compile("(\.NOT\. )?DEFINED\(([A-Za-z0-9_]+)\)", MULTILINE)
        conditionals = re.compile("^#(IF|ENDIF|END IF|ELSE)",MULTILINE)
        space = re.compile("^#(end if)",MULTILINE)
        
        ## Load everything into memory
        # Do not specify encoding here.
        try: 
            # Default's to system specifics
            with io.open(PreprocessingFile,"r") as f: stream = f.read()
        except: 
            # Happens in some windows systems. 
            if Utility.GetPlatform() in ["windows"]: 
                try: 
                    ## Try windows specific file format first. 
                    with io.open(PreprocessingFile,"r", encoding='cp1252') as f: stream = f.read()
                except: 
                    # If not successful, try to use UTF-8 directly
                    with io.open(PreprocessingFile,"r",encoding="utf-8") as f: stream = f.read()
            else:
                # Define encoding explicitly
                with io.open(PreprocessingFile,"r",encoding="utf-8") as f: stream = f.read()
            
        # Replace all incompatible patters
        stream = decorator.sub("#",stream)
        stream = addition.sub("#\g<1>&&\g<2>", stream)
        stream = either.sub("#\g<1>||\g<2>", stream)
        stream = negation.sub(NegationDirective, stream)
        stream = conditionals.sub(LowerDirective, stream)
        stream = space.sub("#endif",stream)
        
        # Replace the input file with the updated version. Specify the encoding.
        try: 
            # Modern convention
            with io.open(PreprocessingFile,"w",encoding="utf-8") as f: f.write(stream)
        except: 
            # Legacy version
            with open(PreprocessingFile,"w") as f: f.write(stream)
    
    def AddIncludePath(self, includes):
        """
        Define additional include directories containing modules or source files as comma separated list. 
        """
        self.incdirs.append(includes)
        self.incdirs = list(Utility.ArbitraryFlattening(self.incdirs))           
        pass
    
    def AddDependencyPath(self, dependencies):
        """
        Define additional directories containing 3rd party libraries as comma separated list. 
        """
        self.libdirs.append(dependencies)
        self.libdirs = list(Utility.ArbitraryFlattening(self.libdirs))    
        pass
    
    def UseLibraries(self, libs):
        """
        Define which non-default libraries should be used during linking. 
        """
        self.libs.append(libs)
        self.libs = list(Utility.ArbitraryFlattening(self.libs))    
        pass                       
    
    def SourcePath(self, path):
        """
        Define a new source directory. Input is read from workspace by default.
        """         
        self.srcdir = path
        ## Source directory can be parsed as relative or
        # absolute path w.r.t. to is initial calling script.
        with Utility.ChangedWorkingDirectory(self.srcdir): 
            self.srcdir = os.path.abspath(os.getcwd())
        pass    
    
    def OutputPath(self, path, files=""):
        """
        Define a new output directory. Output is written to the workspace by default.
        """     
        self.outdir = path
        ## Output directory can be parsed as relative or 
        # absolute path w.r.t. to is initial calling script.
        with Utility.ChangedWorkingDirectory(self.outdir): 
            self.outdir = os.path.abspath(os.getcwd())
        ## List of files copied to the output directory.
        self.copyfiles.append(files)
        self.copyfiles = list(Utility.ArbitraryFlattening(self.copyfiles))    
        pass
    
    def Environment(self, path, script="ifortvars.bat"): # pragma: no cover
        """
        Load an additional environment file prior to execution of all commands. 
        """
        ## Execute an additional bash script prior to all build commands. 
        os.environ['pyx_environment'] = os.path.join(path,script)    
        if path.rsplit("\\",1)[1] == "bin": 
            self.intelpath = path[::-1].replace("bin"[::-1],"",1)[::-1]
        else:
            self.intelpath = path    

        # Update static MKL library include.
        for inc in self.incdirs:
            if all(x in inc for x in ["mkl","include"]):
                self.incdirs.remove(inc) 
            
        # Update static MKL library.
        for lib in self.libdirs:
            if all(x in lib for x in ["mkl", "lib"]) or all(x in lib for x in ["compiler","lib"]):
                self.libdirs.remove(lib) 
                 
        # Redefine MKL paths  
        mkl_include_path = os.path.join(self.intelpath,"mkl","include")
        mkl_lib_path = os.path.join(self.intelpath,"mkl","lib",os.environ['pyx_intel'])
        mkl_compiler_path = os.path.join(self.intelpath,"compiler","lib",os.environ['pyx_intel'])
        # Add newly created path to library path.
        self.incdirs.append(mkl_include_path)
        self.libdirs.extend([mkl_lib_path, mkl_compiler_path])            
        pass     
        
    def Preprocessing(self, cmdstring='', inend='', outend='', copyfiles=[], 
                                   replace = {'!DEC$ IF':'#IF','!DEC$ ELSE':'#ELSE','!DEC$ ENDIF':'#ENDIF'}):
        """
        Assemble command string for the pre-build event.
        """
        # Space delimiter
        delimn = " "
        
        # Add file extension to output file name (if not already been done)
        if not Utility.IsNotEmpty(os.path.splitext(self.buildname)[1]):
            self.buildname = self.buildname+outend
            
        # Add source directory to list of include dirs in case of any preprocessing event.
        if self.srcdir not in self.incdirs: self.incdirs += [self.srcdir]
        
        # Go into scratch directory (if defined)
        with Utility.ChangedWorkingDirectory(self.scrtdir):                       
            # Create two temporary file names.   
            collsrcfile = Utility.GetTemporaryFileName(filename="coll" + "_", extension=inend)  
            presrcfile = Utility.GetTemporaryFileName(filename="pre",extension=outend)  
 
            # Create a list of all directories to be searched 
            search_dir = [self.srcdir]
            try:
                search_dir.extend(self.incdirs)
            except:
                pass         

            # Copy all relevant files from the source folder into the current scratch folder.
            if copyfiles != []:        
                for subdir in search_dir:
                    # Ignore non-existing folders
                    if not os.path.exists(subdir): continue
                    src_files = os.listdir(subdir)
                    file_names = [x for x in src_files if x in copyfiles]
                    for inputfile in file_names:
                        full_file_name = os.path.join(subdir, inputfile)
                        if (os.path.isfile(full_file_name)):
                            shutil.copy(full_file_name, os.getcwd())
                            self.temps = self.temps + (inputfile, )      
            # Rename source code file  
            else:
                Utility.ConcatenateFiles(self.buildname,self.srcs,self.srcdir, inend)  
            
            # Do not apply any pre-processing (required for e.g. Beos)
            if cmdstring != '':
                # Concatenate all source files into one temporary file   
                Utility.ConcatenateFiles(collsrcfile, self.srcs, self.srcdir, ending=inend)       
                
                # Replace pre-processing commands
                Utility.ReplaceTextinFile(collsrcfile, presrcfile, replace, source=self.scrtdir)
                
                # Always align commands with C++.   
                Make.F2CPreprocessing(presrcfile)
            
                # Add all include directories to the call
                if any(x in cmdstring for x in ["cpp", "fpp"]): 
                    cmdstring += delimn + delimn.join(['-I"'+x+'" ' for x in self.incdirs])

                # Assemble command string 
                cmdstring  += ' %s %s' % (presrcfile, self.buildname) 
        
        # Store command string in object
        ## Command executed during pre-build event.
        self.precmd = self.iniCompiler+" "+cmdstring            
        
        # Add temporary files to tuple scheduled for removal
        self.temps = self.temps + (collsrcfile, presrcfile, self.buildname, )                   
        pass

    def Postprocessing(self, cmdstring=''): # pragma: no cover
        """
        Assemble command string for the post-build event.
        """
        ## Command executed during post-build event.
        self.postcmd = self.iniCompiler+" "+cmdstring                      
        pass
       
    def Build(self, cmdstring, **kwargs): # pragma: no cover
        """
        Assemble command string for the main build event.
        """
        # Initialize command string
        cmd = "";
        
        # Create a local view of all variables
        includes = copy.deepcopy(self.incdirs)
        dependencies = copy.deepcopy(self.libdirs)
        libs = copy.deepcopy(self.libs)
        
        # Replace all blanks to be safe
        if self.MakeObjectKind.lower() in ["py2x"] and Utility.GetPlatform() in ["windows"] and cmdstring.find("--backend=meson") != -1:
            includes = [x.replace(' ','+20').replace(ntpath.sep,posixpath.sep) for x in includes]
            dependencies = [x.replace(' ','+20').replace(ntpath.sep,posixpath.sep) for x in dependencies]

        # Only apply linking and include directories for supported make operations
        if not self.MakeObjectKind.lower() in ["doxygen"]:

            # Add all include paths to the command string
            includes = ['-I'+Utility.InQuotes(x)+' ' for x in includes]
            # Add all dependency paths to the command string
            dependencies = ['-L'+Utility.InQuotes(x)+' ' for x in dependencies]    
            # Add all required libraries to the command string
            libs = ['-l'+x+' ' for x in libs]       

            # Assemble final build command
            for x in includes: cmd += x
            for x in dependencies: cmd += x
            for x in libs: cmd += x
                
        ## Command line arguments passed in by the user.
        self.compargs = cmdstring      
        ## Command executed during build event.
        self.makecmd = self.iniCompiler+" "+os.path.join(self.path2exe,self.exe)+" "+ cmd + cmdstring
        pass

    @staticmethod
    def sanitize(string, **kwargs):  # pragma: no cover
        """
        Provide a dictionary with substrings to replace in the given input.
        
        @note: Defaults to replace architecture and platform identifiers
        """
        result = copy.deepcopy(string)
        replacements = kwargs.get("replace",{'{arch}': Utility.GetArchitecture(), "{platform}":Utility.GetPlatform()})
        for key, value in replacements.items():
            result = result.replace(key, value)
        result = Utility.GetSanitizedDataFromCommand([result], is_path=False)[-1]
        return result
    
    @staticmethod
    def setup(*args, **kwargs): # pragma: no cover
        """
        Initialize a predefined compiler tool chain of all requirements are met.
        
        @note: Only meaningful on NT systems.
        """
        # Future proof by only importing 
        try: from packaging.version import Version as StrictVersion
        except ImportError: from distutils.version import StrictVersion
        
        delimn = " "
        
        # The function is only meaningful on NT systems
        if Utility.GetPlatform() not in ["windows"]: return
        
        # Initialize and create tool chain for MSYS2 on Windows
        if kwargs.get("mingw",False):
            # Fetch path to choco directory and determine installation directory of msys64
            _, choco_base_path = Utility.GetExecutable("choco", get_path=True)
            # There are two executables of chocolatey present within one installation folder. Because reasons.
            if "bin" not in os.listdir(os.path.dirname(choco_base_path)): choco_base_path = os.path.join(choco_base_path,'..', '..')
            else: choco_base_path = os.path.join(choco_base_path,'..')
            choco_base_path = os.path.normpath(choco_base_path)
            content = open(os.path.join(choco_base_path,"logs","choco.summary.log"),"r").readlines()
            # Determine msys64 installation directory
            try: _, msys2_base_path = next(iter([x for x in content if all([y in x.lower() for y in ["msys64","software installed to"]])])).split("Software installed to")
            # Well, they changed the logs...
            except StopIteration: _, msys2_base_path = next(iter([x for x in content if all([y in x.lower() for y in ["msys64","installing to"]])])).split("Installing to:")
            # Get base path
            try: msys2_base_path = Utility.GetSanitizedDataFromCommand("r"+msys2_base_path.strip(), allowed_exceptions=(ValueError,))[0]
            except SyntaxError: msys2_base_path = msys2_base_path.strip()
            msys2_base_path = os.path.normpath(msys2_base_path)
            # Get compiler path. Default to the latest version
            msys2_compiler_version = sorted(os.listdir(os.path.join(msys2_base_path,"mingw64","lib","gcc","x86_64-w64-mingw32")),key=StrictVersion)[-1]
            msys2_compiler_path = os.path.join(msys2_base_path,"mingw64","lib","gcc","x86_64-w64-mingw32",msys2_compiler_version)
            # Get base initialization shell script
            msys2_shell_initialization = delimn.join([os.path.join(msys2_base_path,"msys2_shell.cmd"),"-defterm","-mingw64","-no-start","-full-path","-here"])
            # Return all paths
            return (msys2_base_path, msys2_compiler_path, msys2_shell_initialization)
        # Initialize and create tool chain for Visual Studio on Windows
        elif kwargs.get("msvsc",'vs2015') in ["vs2015","vs2017","vs2019","vs2022"]: # pragma: no cover
            # Set Intel Fortran Compler path to None as default value
            intel_compiler_path = ""
            # Get base initialization batch script
            msvsc_shell_initialization = r'"'+os.path.join(PyXMakePath,"Build","cmd","windows","iniCompiler.bat")+'"'
            # Remove support for Paths.log
            if not any([Utility.GetExecutable(x) for x in ["ifx","ifort"]]) and not os.path.exists(os.path.join(Utility.GetPyXMakePath(),"Paths.log")):     
                # Get directory of the windows start menu
                allprograms = os.path.join(os.environ['ALLUSERSPROFILE'],"Microsoft","Windows","Start Menu", "Programs")
                # Search for Intel
                for root, _, files in Utility.PathWalk(allprograms):
                    if "intel" not in root.lower(): continue
                    if not any(x.lower().endswith("lnk") for x in files) or not any("compiler" in x.lower() for x in files): continue
                    intellink = os.path.abspath(os.path.join(root,sorted(files)[-1]))
                # Read command from binary link
                try: command = Utility.GetLink(intellink)
                # We found nothing associated with Intel. Skip the rest an issue an error later, if required.
                except UnboundLocalError: return (None, intel_compiler_path, msvsc_shell_initialization )
                intelpath = next(iter(x for x in command.split('"') if "compiler" in x.lower()))
                # Set environment variables 
                if not os.getenv("pyx_intel","") and not os.getenv("pyx_msvsc",""):
                    os.environ["pyx_intel"], os.environ["pyx_msvsc"] = [x.replace('"',"") for x in command.split(delimn)[-2:]]                
                # Set environment explicitly
                os.environ["pyx_environment"] = intelpath
                # Set default Intel Fortran Compiler path
                intel_compiler_path = os.path.abspath(os.path.join(intelpath, os.path.pardir, os.path.pardir))
                # Attempt to initialize Intel Fortran compiler and read environment data from the call
                data = Utility.GetEnvironmentFromCommand(os.path.join(Utility.GetPyXMakePath(),"Build","cmd","windows","iniCompiler.bat"))
                # Update the current environment
                os.environ.update(data)
            ## Compiler executables are already in the path variable of the current process. 
            # Do not attempt to set the environment here
            if any([Utility.GetExecutable(x) for x in ["ifx","ifort"]]): os.environ["pyx_environment"] = "unset"
            # Return all paths
            return (None, intel_compiler_path, msvsc_shell_initialization )
        pass
    
    @classmethod
    def run(cls, **kwargs):
        """
        Assemble command string for the post-build event.
        """
        ## Run a given class with its default CLI settings when supported.
        if hasattr(cls, "parse"): cls.parse(command=sys.argv, **kwargs)
        else: RuntimeWarning("Class %s has no associated default parsing feature. Skipping." % str(cls.__name__)) # pragma: no cover
        pass
    
    def create(self, **kwargs):
        """
        Execute make command
        """
        # Dictionary holding all local output settings
        settings = {"verbosity": self.verbose, "collect": not "cmake" in self.exe or Utility.GetPlatform() in ["linux"]}

        # Execute again to account for input added after compiling command
        try: self.Build(self.compargs, **kwargs)
        except: pass
        
        # Go into scratch directory (if defined)
        with Utility.ChangedWorkingDirectory(self.scrtdir):
            ## All files are automatically added to the tuple of temporary files. Thus, these files is this list
            # were already present when the process has started. Accordingly, do not delete these files since 
            # one cannot be sure the scratch directory was set to a workspace with import files
            vault = [x for x in os.listdir(os.getcwd()) if x not in self.temps]
            
            for key in os.environ.keys():
                # Issue a warning if one of the environment variables pass their maximum limit on windows. Subsequent errors may occur.
                if Utility.GetPlatform() == "windows" and self.verbose >= 3 and len(os.environ[key]) >= 2048: # pragma: no cover
                    warnings.warn("Environment variable %s" % key + " is exceeding the character limit") #@UndefinedVariable
            
            # Pre-build event  (if required)          
            try: 
                if self.precmd != '':
                    Utility.Popen(self.precmd, **settings)
            except:
                pass
           
            # Build event (if required)
            try: # pragma: no cover
                if getattr(self,"mkl_dependency",""):
                    # Add additional MKL dependencies
                    for x in getattr(self,"_mkl_includes",[]):
                        if x not in np.atleast_1d(self.mkl_dependency): continue
                        with open("pyx_bridge_"+str(x), "a+") as mkl_include: mkl_include.write("      include '%s' \n" % str(x))
                        command = self.iniCompiler + " "+'ifort -c "%s"' % str("pyx_bridge_"+str(x))
                        Utility.Popen(command, **settings)
                
                if self.makecmd != '':
                    # Modify build runtime environment
                    env = os.environ.copy(); 
                    # PYTHONPATH may not exist
                    if not "python" in self.makecmd: env.pop("PYTHONPATH","") #@UndefinedVariable
                    try: 
                        # Check if there is a patch
                        _ = getattr(self, "patch")
                        # If there is a patch, run the main make command as a context manager
                        with self.patch(command=self.makecmd, verbose=self.verbose, **kwargs):
                            # Get local updates of environment variables
                            env.update(os.environ.copy())
                            # Run the main command
                            Utility.Popen(self.makecmd, env=env, **settings)
                    # This only happens when there is no patch - which is the default
                    except AttributeError: Utility.Popen(self.makecmd, env=env, **settings)
            except: pass
            
            # Post-build event (if required)                                 
            try:     
                if self.postcmd != '':                    
                    Utility.Popen(self.postcmd, **settings)      
            except: pass
        
            # Copy files to predefined output location. Add the original to list of redundant files.
            # Copy only those files which are not temporary and whose name includes the BuildID.
            # If a list of files if given, use only those files presented in the list. Add to other files to list 
            # of redundant files.  
            try: # pragma: no cover
                if self.outdir != os.getcwd():
                    for f in os.listdir(os.getcwd()):
                        # Do not process any file in vault
                        if f in vault: continue
                        # All files from here are created during the process
                        elif self.architecture in f and f != self.buildname and f not in self.temps:
                            if self.copyfiles[0] == "":
                                copyfile(os.path.join(os.getcwd(),f), os.path.join(self.outdir,f))
                            self.temps = self.temps + (f, )  
                        if f in self.copyfiles:
                            copyfile(os.path.join(os.getcwd(),f), os.path.join(self.outdir,f))       
                            self.temps = self.temps + (f, )          
                        elif f not in self.copyfiles and self.copyfiles[0] != "" and not os.path.isdir(f):     
                            self.temps = self.temps + (f, )                                                     
            except: pass             
            # Finish and delete redundant files
            Utility.DeleteFilesbyEnding(self.temps)          
        pass
    
## @class PyXMake.Build.Make.Custom
# Base class for all custom build events inherited from Make.  
class Custom(Make):
    """
    Inherited class to build projects without any presets.
    """          
    def __init__(self, *args, **kwargs):
        """
        Initialization of Custom class object.
        """
        super(Custom, self).__init__(*args, **kwargs)
        ## String identifier of current instance.                
        self.MakeObjectKind = "Custom"
        
        ## The executable command used in all build events.
        self.exe = "cmd.exe /c &&"
        
        ## Change default executable settings when source is a CMAKE file
        if self.srcs[-1] in ["CMakeLists.txt"]:
            settings = { "search_paths": os.pathsep.join([os.getenv("PATH",os.getcwd()),os.path.join(sys.prefix,"scripts")]) }
            # Ensure that the latest GNU compiler is fetched by CMAKE.
            self.exe = ["cmake" if not Utility.GetExecutable("cmake", **settings) else 
                                Utility.InQuotes(Utility.GetExecutable("cmake",get_path=True, **settings)[-1]) ][0]
            # Convert an absolute CMAKE path to POSIX style format to properly work with MingW64
            if  Utility.GetPlatform() in ["windows"] and Utility.GetExecutable("choco") and self.hasFoss: # pragma: no cover
                self.exe = Utility.GetPathConversion(self.exe, "linux")

        ## Immutable settings for Custom object.    
        # Temporary build name, assembled using BuildID.        
        self.buildname = self.buildid + self.architecture 
        
        # Set environment variables for ABAQUS builds (Defaults to latest version).
        os.environ["ABQ_ENV_FILE"] = "abaqus_v6.env"
        os.environ["pyx_abaqus"] =  os.getenv("pyx_abaqus","abaqus")
              
        # Add additional MKL dependencies. Only when MKL support is enabled.
        self.mkl_dependency = ["mkl_vsl.f90"]
        
        ## Command line arguments passed in by the user.
        self.compargs = ""  
        
        # Add temporary files to tuple scheduled for removal.
        self.temps = self.temps + (os.getenv("ABQ_ENV_FILE"), )
        pass 
    
    def Build(self, cmdstring, **kwargs):
        """
        Assemble command string for the main build event.
        """
        delimn = " "
        
        # Do this part only once!
        if self.compargs == cmdstring:
            # Add all include paths to the include environment variable
            os.environ["INCLUDE"] = os.pathsep.join(list(self.incdirs))  + os.pathsep + os.pathsep.join((os.environ.get("MSMPI_INC",""), os.environ.get("INCLUDE","")))
                
            # Add all additional library paths to the lib environment variable
            os.environ["LIB"] = os.pathsep.join(self.libdirs) + os.pathsep + os.pathsep.join((os.environ.get("MSMPI_LIB64",""), os.environ.get("LIB",""))) 
            
            # Add scratch and sources to path environment variable
            os.environ["PATH"] = os.pathsep.join([self.srcdir,self.scrtdir]) + os.pathsep + os.getenv("PATH","")
        
        ## Execute a CMake build script
        if "cmake" in self.exe:

            # Create build command
            command = "%s" % self.exe  
            # Source path quotation is dependent of the underlying system build framework
            if not self.hasFoss and Utility.GetPlatform() in ["windows"]: command += ' -B build -S '"%s"'' % os.path.abspath(self.srcdir)
            else: command += " -B build -S '%s'" % os.path.abspath(self.srcdir)
            # Remove duplicate cmake call
            command += cmdstring.replace("cmake"," ")
            
            ## Attribute only contains string when a non-default output directory has been defined.
            # Update the installation prefix in that case
            if any(isinstance(x,six.string_types) for x in getattr(self,"copyfiles",[])): # pragma: no cover
                command += " -DCMAKE_INSTALL_PREFIX='%s'" % os.path.abspath(self.outdir)
            
            # Collect half the number of available core to speed up the build process
            cpus = str(multiprocessing.cpu_count()//2) #@UndefinedVariable
            
            # Deactivate MKL dependency
            self.mkl_dependency = []
            
            # Explicitly set all compilers 
            if self.hasFoss: command +=" -DCMAKE_C_COMPILER=gcc -DCMAKE_CXX_COMPILER=g++ -DCMAKE_Fortran_COMPILER=gfortran"
            
            # Add verbose output
            if self.verbose >= 2: command +=" -DCMAKE_VERBOSE_MAKEFILE=On"
            
            # Add all additional supplied user options w/o further verification
            if kwargs.get("append",[]): command += delimn + delimn.join(kwargs.get("append"))
            
            # Run CMake on windows with cross compilation
            if not self.hasFoss and Utility.GetPlatform() in ["windows"]: # pragma: no cover
                command +=' -DCMAKE_BUILD_TYPE=Release'
                # Custom header files are required on windows. 
                command +=' -DCMAKE_INCLUDE_PATH="%s"' % os.path.join(PyXMakePath,"VTL","make")
                # Add local script directory to local search path
                settings = {"search_paths":os.pathsep.join([os.path.join(sys.prefix,"Scripts"),os.getenv("PATH","")])}
                # Help CMAKE to find a compatible SED program
                if Utility.GetExecutable("pythonsed",**settings): 
                    command +=' -DSED="%s"' % Utility.GetExecutable("pythonsed", get_path=True, **settings)[-1]
                elif Utility.GetExecutable("choco"): 
                    try:     
                        settings = {"search_paths":os.pathsep.join([os.path.join(Make.setup(mingw = Utility.GetExecutable("choco"))[0],"usr","bin"),os.getenv("PATH","")])}
                        command +=' -DSED="%s"' % Utility.GetExecutable("sed", get_path=True, **settings)[-1]
                    except: pass
                # If SED is found directly. Do nothing
                elif Utility.GetExecutable("sed"): pass
                # Support pythonSED executable
                # Should never happen
                else: pass
                # Suppress warnings for developers and set up NMAKE
                command +=' -Wno-dev -G "NMake Makefiles"'
                # When using Intel oneAPI environment, use classic compiler for the time being
                if Utility.GetExecutable("oneapi-cli") and Utility.GetExecutable("ifort"): command += " -DCMAKE_Fortran_COMPILER=ifort"
                # Get batch script initialization 
                batch = delimn.join([self.iniCompiler,"&&"])
                # Define build commands
                self.precmd = delimn.join([batch,'%s' % command])
                self.makecmd = delimn.join([batch,'%s' % "%s --build build" % self.exe])
                self.postcmd = delimn.join([batch,'%s' % "%s --install build" % self.exe])
            # Run using MINGW on NT systems
            elif Utility.GetPlatform() in ["windows"] and Utility.GetExecutable("choco"): # pragma: no cover
                command += " -G 'MinGW Makefiles'"   
                # Get MSYS2 initialization 
                msys2_shell = delimn.join([self.setup(mingw=True)[-1],"-c"])
                # Define build commands
                self.precmd = delimn.join([msys2_shell,'"%s"' % command])
                self.makecmd = delimn.join([msys2_shell,'"%s"' % "%s --build build -j %s" % (self.exe, cpus)])
                self.postcmd = delimn.join([msys2_shell,'"%s"' % "%s --install build" % self.exe])
            # Run CMake on POSIX systems
            else: 
                # Define build commands
                self.precmd = shlex.split(command, posix=not os.name.lower() in ["nt"])
                self.makecmd = shlex.split("%s --build build -j %s" % (self.exe, cpus), posix=not os.name.lower() in ["nt"])
                self.postcmd = shlex.split("%s --install build" % self.exe, posix=not os.name.lower() in ["nt"])

        # Add pre-processed source file to environment variable    
        os.environ["pyx_file"] = self.buildname   
        
        # Add exception to pyx_libs when ABAQUS build command is used with vs2015 and higher.
        if self.msvsc.lower() in ["vs2015", "vs2017","vs2019","vs2022"]: 
            self.libs.extend(["msvcrt", "vcruntime", "ucrt", "legacy_stdio_definitions"])
            # Remove explicit reference to Microsoft Runtime Library when using lastest Intel OneAPI environment
            if Utility.GetExecutable("oneapi-cli"): self.libs.remove("msvcrt")

        # Add all libraries to a environment variable
        pyx_libs = ["'"+x+".lib'" for x in sorted(set(self.libs), key=self.libs.index)]
        
        # Set environment variable
        os.environ["pyx_libs"] = ",".join(pyx_libs)    
        
        ## Command line arguments passed in by the user.
        self.compargs = cmdstring      
        ## Command executed during build event.              
        if not getattr(self, "makecmd",""): self.makecmd = self.iniCompiler+" "+self.exe+" "+cmdstring
        
        # Add temporary files to tuple scheduled for removal
        self.temps = self.temps + (self.buildname, )                 
        pass
    
    @classmethod
    def parse(cls, **kwargs): # pragma: no cover
        """
        Execute the current class as a CLI command.
        """
        # Import its main from VTL  
        from PyXMake.VTL import cmake
        # Evaluate current command line
        command = kwargs.get("command",sys.argv)
        # Process all known arguments
        parser = argparse.ArgumentParser(description='CLI wrapper options for  CMAKE with more sensible default settings.')
        parser.add_argument('name', type=str, nargs=1, help="Name of the project")
        parser.add_argument('source', type=str, nargs=1, help="Absolute path to the source file directory.")
        parser.add_argument('-s', '--scratch', nargs='+', default=[], help="Default scratch folder for CMake. Defaults to current workspace.")
        parser.add_argument("-o","--output", type=str, nargs=1, help="Absolute path to output directory. Defaults to current project folder.")
        parser.add_argument("-v","--verbosity", type=str, nargs=1, help="Level of verbosity. Defaults to 0 - meaning no output. Max value is 2.")
        parser.add_argument("--foss", type=Utility.GetBoolean, const=True, default=True, nargs='?', 
                            help="Toggle to enforce free-open source builds. Defaults to True.")
        # Check all options or run unit tests in default mode
        try:
            # Check CLI options
            _ = command[1]
            args, unknown = parser.parse_known_args(command[1:])
            # Project name is mandatory
            project = args.name[0]; 
            # Specification of source directory is mandatory
            source = args.source[0] ; 
            # Optional non-default output directory
            try: output = args.output[0]
            except: output = None
            # Optional non-default scratch directory
            try: scratch = args.scratch[0]
            except: scratch = os.path.abspath(os.getcwd())
            # Verbose output level. Defaults to ZERO - meaning no output. Can be increased to 2.
            try: verbosity = int(args.verbosity[0])
            except: verbosity = 0
            # Optional non-default package check
            try: foss = args.foss[0]
            except: foss = Utility.GetPlatform() in ["linux"]
            # Create a dictionary combining all settings
            settings = {"source":source, "output":output, "scratch":scratch,
                                "verbosity":verbosity, "foss": foss}
            # Parse all unknown command line parameter directly to cmake
            append = [x for x in unknown if not any(y in x for y in vars(args).keys())]
            if append: settings.update({"append":append})
        # Use an exception to allow help message to be printed.
        except Exception as _:
            # Local imports. These are only meaningful while executing an unit test
            from PyCODAC.Tools.Utility import GetPyCODACPath
            # Build all supported features
            if AllowDefaultMakeOption:     
                # Run compilation of MCODAC using CMake
                BuildID = "mcd_core"; 
                # Compile everything using CMake.
                cmake(BuildID, source=os.path.join(GetPyCODACPath(),"Core","config"), foss=kwargs.pop("foss",True))  
        else:
            # Execute CLI command
            cmake(project, **settings)
        pass

## @class PyXMake.Build.Make.CCxx
# Base class for all C/C++ build events inherited from Make.  
class CCxx(Make,NT,POSIX):
    """
    Inherited class to build projects using Intel C/C++.
    """          
    def __init__(self, *args, **kwargs):
        """
        Initialization of C/C++ class object.
        """
        super(CCxx, self).__init__(*args, **kwargs)
        ## String identifier of current instance.                
        self.MakeObjectKind = 'CCxx'
        
        ## The executable command used in the main build event.
        self.exe = 'cl.exe'; os.environ["pyx_compiler"] = "gcc"
        
        ## Static or dynamic link library flag.
        self.isStatic = True if kwargs.get('lib', 'static') not in ['shared', 'SHARED', 'Shared'] else False
        
        ## Define if the input should be compiled exactly as provided.
        # Defaults to False, meaning that merging & pre-processing utilities will be carried out.
        self.incremental = kwargs.get('incremental', False)           

        # Immutable settings for C/Cpp object       
        if self.incremental:                        
            self.exe += ' -c %s' % (' '.join(self.srcs))  
        else: # pragma: no cover
            self.exe += ' -c %s' % (self.buildname)           
           
        ## Name of library, assembled using BuildID.        
        self.libname = self.buildid + self.architecture
        ## Temporary build name.          
        self.buildname = self.libname
             
        # Initialization of lists containing additional sources, modules or libraries
        ## List of libraries which should be statically linked in.
        self.linkedIn = []       
        
        # Initialization of  tuple containing temporary files    
        ## Blank version of tuple to store temporary file names scheduled for removal.            
        self.temps = ()                 
        
        # Remove MKL from default command line
        ## Blank version of list containing library directories without initially specifying MKL.             
        self.libdirs = []       

        # Always add conversion headers to the default make directory                 
        self.incdirs.append(os.path.join(PyXMakePath,"VTL","make"))
        
        # Identify source code and BuildID and set the corresponding environment variables for Mingw64 and Linux.
        if kwargs.get("bash", self.hasFoss):            
            os.environ["pyx_buildid"], os.environ["pyx_source"] = (self.libname, ' '.join([x for x in self.srcs if os.path.splitext(x)[1].lower() in (".c", ".cpp", ".h", ".hpp", "Makefile")]))            
        pass
    
    def OutputPath(self, libpath=os.getcwd()):
        """
        Define output directories for modules and libraries. 
        """       
        ## Output path for library files.
        self.outlibs = libpath 
        pass    
    
    def Build(self, cmdstring, **kwargs):
        """
        Assemble command strings for the main build event.
        """
        # Initialize command string
        cmd = ""
        
        # Add all include paths to the command string
        includes = [' -I"'+x+'" ' for x in self.incdirs]
        for x in includes: 
            cmd += x        
        
        # Choose the librarian and the file extension of the library.    
        if not self.isStatic: # pragma: no cover
            librarian = 'link -dll -fixed:no -defaultlib:libcmt.lib -nodefaultlib:msvcrt.lib '
            ext          = '.dll'                 
        else:
            librarian = 'lib '
            ext          = '.lib'                 
        
        # Build commands using Intel Fortran (immutable)
        ## Used defined command line options.
        self.compargs = cmdstring
        ## Intel Compiler command.
        self.makecmd = self.iniCompiler+" "
        self.makecmd += self.exe + cmd + cmdstring + ' && '    
        ## Intel Linker command.
        self.linkcmd = librarian +'*.obj -nologo -machine:'+self.architecture+' -out:'+os.path.join(self.outlibs,self.libname+ext)    
        
        # Add temporary files to tuple scheduled for removal
        self.temps = self.temps + (self.libname+'.obj', ".obj",)               
        pass
    
    @classmethod
    def parse(cls, **kwargs): # pragma: no cover
        """
        Execute the current class as a CLI command.
        """
        # Import its main from VTL  
        from PyXMake.VTL import cxx
        # Evaluate current command line
        command = kwargs.pop("command",sys.argv)
        # Process all known arguments
        parser = argparse.ArgumentParser(description="Build a sCxx project from console.")
        parser.add_argument('name', type=str, nargs=1, help="Name of the project")
        parser.add_argument('source', type=str, nargs=1, help="Absolute path to the source file directory.")
        parser.add_argument('-f', '--files', nargs='+', default=[], help="Source file or list of all source files in the order of compilation")
        parser.add_argument("-o","--output", type=str, nargs=1, help="Absolute path to output directory. Defaults to current project folder.")
        parser.add_argument('-i', '--include', nargs='+', default=[], help="Additional directories and files required for the build.")
        parser.add_argument('-s', '--scratch', nargs='+', default=[], help="Default scratch folder for the build. Defaults to current workspace.")
        parser.add_argument("-v","--verbosity", type=str, nargs=1, help="Level of verbosity. Defaults to 0 - meaning no output. Max value is 2.")
        parser.add_argument("--incremental", type=Utility.GetBoolean, const=True, default=False, nargs='?', 
            help="Toggle between incremental and non-incremental build. Defaults to False.")
        
        try:
            # Check CLI options
            _ = command[1]
            args, _ = parser.parse_known_args(command[1:])
            # Project name is mandatory
            project = args.name[0]
            # Specification of source directory is mandatory
            source = args.source[0] ; 
            # Optional non-default output directory
            try: files = args.files
            except: files = []   
            # Optional non-default output directory
            try: output = args.output[0]
            except: output = os.path.abspath(os.getcwd())
            # Optional non-default definition of additional tests cases
            try: 
                _ = args.include[0]
                # Collect all given paths. Get system independent format
                include = Utility.GetSanitizedDataFromCommand(args.include)
            # No extra test cases have been given
            except: include = []
            # Optional incremental build option. Defaults to False.
            try: incremental = args.incremental[0]
            except: incremental = False
            # Optional non-default scratch directory
            try: scratch = args.scratch[0]
            except: scratch = os.path.abspath(os.getcwd())
            # Verbose output level. Defaults to ZERO - meaning no output. Can be increased to 2.
            try: verbosity = int(args.verbosity[0])
            except: verbosity = 0
            # Create a dictionary combining all settings
            settings = {"files":files, "incremental": incremental, "include": include, 
                                "source":source, "output":output, "scratch":scratch,
                                "verbosity":verbosity}
        # Use an exception to allow help message to be printed.
        except Exception as _:
            # Build all supported features for current Python version (default options)
            if AllowDefaultMakeOption:
                ## This part serves as a unit test. It it not executed by default when installed from PyPi
                try:
                    # Build Muesli with default settings.
                    BuildID = "muesli"; cxx(BuildID, foss=False, **kwargs)
                except: pass
                try:
                    # Build DispLam
                    from PyCODAC.Plugin.DispLam import __path__ as DispLamPath
                    disp_src = os.path.join(DispLamPath[0],"src","displam"); disp_bin=os.path.join(DispLamPath[0],"bin",Utility.GetPlatform())
                    cxx("displam", os.listdir(disp_src), source=disp_src, output=disp_bin, verbosity=0, **kwargs)
                except: pass
        # Execute valid CLI command
        else: cxx(project, **settings)
        pass
    
    def create(self): # pragma: no cover
        """
        Execute make command
        """  
        cmd = ''          

        # Go into scratch directory (if defined)
        with Utility.ChangedWorkingDirectory(self.scrtdir):             
                   
            # Pre-build event  (if required)          
            try: 
                if self.precmd != '':      
                    Utility.Popen(self.precmd, self.verbose)             
            except:
                pass
            
            # Add all dependency paths to the command string
            dependencies = [' -LIBPATH:"'+x+'" ' for x in self.libdirs]
            for y in dependencies:
                cmd += y 
            
            # Add libraries for linking to the command string
            linklist = [' '+x+'.lib ' for x in self.libs]
            for x in linklist:
                cmd += x                    
    
            # Build event (if required) 
            try: 
                if self.makecmd != '':              
                    # Execute again to account for input added after compiling command
                    self.Build(self.compargs)       
                    Utility.Popen(self.makecmd+self.linkcmd+cmd, self.verbose)           
            except Exception as _: pass
            
            # Post-build event (if required)                                 
            try:     
                if self.postcmd != '':
                    Utility.Popen(self.postcmd, self.verbose)                          
            except:
                pass
    
            # Finish and delete redundant files      
            if not self.isStatic:
                os.remove(os.path.join(self.outlibs,self.libname+'.exp'))
                os.remove(os.path.join(self.outlibs,self.libname+'.lib'))    
            Utility.DeleteFilesbyEnding(self.temps)                 
        pass              
                
## @class PyXMake.Build.Make.Fortran
# Base class for all Fortran build events. 
# Inherited from Make and flavors in dependence of the underlying or requested operating system (optionally).
class Fortran(Make,NT,POSIX):
    """
    Inherited class to build projects using Intel Fortran.
    """      
    def __init__(self, *args, **kwargs):
        """
        Initialization of Fortran class object.
        """   
        super(Fortran, self).__init__(*args, **kwargs)
        ## String identifier of current instance.                
        self.MakeObjectKind = 'Fortran'; os.environ["pyx_compiler"] = "gfortran"
        
        ## Static or dynamic link library flag.
        self.isStatic = True if kwargs.get('lib', 'static') not in ['shared', 'SHARED', 'Shared'] else False
        
        # Add static MKL libraries when creating a shared resource library (for Java applications).
        if not self.isStatic: # pragma: no cover
            if self.architecture == "x86":
                mkl_interface_lib = "mkl_intel_c"
            else:
                mkl_interface_lib = "mkl_intel_lp64"   
                
            # Always link statically against MKL library         
            self.libs.append([mkl_interface_lib, "mkl_intel_thread", "mkl_core","libiomp5md"])
            self.libs = list(Utility.ArbitraryFlattening(self.libs))     
            pass

        # Immutable settings for Fortran object    
        ## Name of library, assembled using BuildID.
        self.libname = ("lib" if Utility.GetPlatform() in ["linux"] else "") + self.buildid + self.architecture
        ## Temporary build name.          
        self.buildname = self.libname
        
        # Activate / deactivate incremental linking
        self.incremental = kwargs.get("incremental",False)
        
        # Defined here to be checked later.
        ## Wrapper interface file for 3rd party FORTRAN code. Automatically creates a module of the underlying source material.
        self.intermediate_wrapper = ""
        self.wrapper_source = ""
        self.wrapper_module = "pyx_module.f90"  
             
        # Initialization of lists containing additional sources, modules or libraries
        ## List of libraries which should be statically linked in.
        self.linkedIn = []              
        
        # Remove MKL from default command line
        ## Blank version of list containing library directories without initially specifying MKL.             
        self.libdirs = []
        
        # Identify source code and BuildID and set the corresponding environment variables for Mingw64 and Linux.
        if kwargs.get("bash", self.hasFoss):            
            os.environ["pyx_buildid"], os.environ["pyx_source"] = (self.libname, ' '.join([x for x in self.srcs if os.path.splitext(x)[1].lower() in (".for", ".f95", ".f", ".f90")]))  
        pass          
    
    def OutputPath(self, modulepath=None, libpath=os.getcwd()):
        """
        Define output directories for modules and libraries. 
        """       
        # Output module files to scratch directory by default.
        if modulepath is None:
            modulepath = self.scrtdir       
        ## Output path for module or header files.               
        self.outmodule = modulepath 
        ## Output path for library files.
        self.outlibs = libpath 
        pass
    
    def Preprocessing(self, inend='', outend='', copyfiles=[], 
                                   replace = {'!DEC$ IF':'#IF','!DEC$ ELSE':'#ELSE','!DEC$ ENDIF':'#ENDIF'}, 
                                   decorator="!DEC$ ATTRIBUTES DLLEXPORT::"):
        """
        Assemble command string for the pre-build event.
        """
        # Avoid false positives when created a shared resource library.
        delimn = " "; validater ="bind"
        
        # Save  command if already defined
        _preprocessing = copy.deepcopy(getattr(self,"precmd",None))
        
        # Execute base class method
        Make.Preprocessing(self,"custom", inend, outend, copyfiles, replace)
          
        # Go into scratch directory (if defined)
        with Utility.ChangedWorkingDirectory(self.scrtdir):
            
            # Never merge files unless explicitly allowed
            if copyfiles: 
                # File might not exists - use exception to catch that
                try: os.remove(os.path.join(os.getcwd(),self.buildname))
                except FileNotFoundError: pass
            # Mimic the previous work flow
            else:      
                # Get temporary file name
                presrcfile = self.precmd.split(delimn)[-2]
                
                # Check if decorators have to be added to the source file.
                Inputfile = os.path.join(os.getcwd(),presrcfile)  
                Outputfile = os.path.join(os.getcwd(),self.buildname)  
                with open(Inputfile) as infile, open(Outputfile, 'w') as outfile: # pragma: no cover
                    for line in infile:
                        outfile.write(line)      
                        if not self.isStatic:                    
                            xname, xline = line.partition('="')[0], line.partition('="')[2]            
                            if xline != '' and validater in xname.lower():       
                                outfile.write(decorator+xline.partition('"')[0]+"\n")         

        # Recover original command
        self.precmd = _preprocessing  
        pass
    
    def Wrapper(self, module_name, source_name=None): # pragma: no cover
        """
        Assemble command string for the pre-build event.
        """
        # Add module wrapper to the default make directory  
        makedir = os.path.join(PyXMakePath,"VTL","make")       
        TmpFile = Utility.GetTemporaryFileName(extension=str(os.path.splitext(self.wrapper_module)[1]))   
        copyfile(os.path.join(makedir,self.wrapper_module), os.path.join(self.scrtdir,TmpFile))    
        
        if source_name:
            self.wrapper_source = source_name
        
        self.intermediate_wrapper = Utility.GetTemporaryFileName(extension=str(os.path.splitext(TmpFile)[1]))   
        
        # Go into scratch directory (if defined)
        with Utility.ChangedWorkingDirectory(self.scrtdir):     
            # Prepare wrapper module for later use         
            Utility.ReplaceTextinFile(TmpFile, self.intermediate_wrapper, {'%pyx_module%':module_name}, source=self.scrtdir)

        # Add temporary files to tuple scheduled for removal
        self.temps = self.temps + (TmpFile, self.intermediate_wrapper, self.wrapper_module, )                   
        pass                      
    
    def Build(self, cmdstring, **kwargs): # pragma: no cover
        """
        Assemble command strings for the main build event.
        """
        sep = " "; multi_objects = []
        
        # Initialize command string
        if not self.incremental:
            cmd = ' -object:'+self.libname+' -module:'+self.outmodule+' -I:"'+self.outmodule+'"'
        else:
            # Add an trailing separator to indicate a folder
            cmd = ' -object:'+self.scrtdir+os.path.sep+' -module:'+self.outmodule+' -I:"'+self.outmodule+'"'            
        
        # Add all include paths to the command string
        includes = [' -I"'+x+'" ' for x in self.incdirs]
        for x in includes: 
            cmd += x        
        
        # Choose the librarian and the file extension of the library.    
        if not self.isStatic: 
            librarian = 'link -dll -fixed:no -defaultlib:libcmt.lib -nodefaultlib:msvcrt.lib '
            ext          = '.dll'                 
        else:
            librarian = 'lib '
            ext          = '.lib'                 
        
        # Build commands using Intel Fortran (immutable)
        ## Used defined command line options.
        self.compargs = cmdstring
        ## Intel Compiler command.
        self.makecmd = self.iniCompiler+" "
        
        # Check whether an interface module wrapper was added to the current folder
        if os.path.isfile(self.intermediate_wrapper):
            makefile = "-fpp "+ self.wrapper_module
            if (Utility.IsNotEmpty(self.wrapper_source)):
                self.buildname = self.wrapper_source
        elif self.incremental:          
            makefile = sep.join([x for x in self.srcs if os.path.splitext(x)[1].lower() in (".for", ".f95", ".f", ".f90")])
            multi_objects = [os.path.splitext(x)[0]+".obj" for x in self.srcs if os.path.splitext(x)[1].lower() in (".for", ".f95", ".f", ".f90")]
        else:
            makefile = self.buildname    
        
        self.makecmd += 'ifort -c '+ makefile + cmd + cmdstring + ' && '    
        ## Intel Linker command.
        if not multi_objects:
            self.linkcmd = librarian +self.libname+'.obj -nologo -machine:'+self.architecture+' -out:'+os.path.join(self.outlibs,self.libname+ext)         
        else:
            self.temps = self.temps + (".obj",)
            self.linkcmd = librarian +sep.join(multi_objects) +' -nologo -machine:'+self.architecture+' -out:'+os.path.join(self.outlibs,self.libname+ext)   
        
        # Add temporary files to tuple scheduled for removal
        self.temps = self.temps + (self.libname+'.obj', '.mod')               
        pass   
    
    def create(self, **kwargs): # pragma: no cover
        """
        Execute make command
        """  
        cmd = ''          

        # Go into scratch directory (if defined)
        with Utility.ChangedWorkingDirectory(self.scrtdir):             
                   
            # Pre-build event  (if required)          
            try: 
                if self.precmd != '':      
                    Utility.Popen(self.precmd, self.verbose)             
            except:
                pass
            
            # Add all dependency paths to the command string
            dependencies = [' -LIBPATH:"'+x+'" ' for x in self.libdirs]
            for y in dependencies: 
                cmd += y               
            
            # Add libraries for linking to the command string
            linklist = [' '+x+'.lib ' for x in self.libs]
            for x in linklist: 
                cmd += x
    
            # Delete old module files
            if os.path.exists(self.outmodule): 
                # Only meaningful when output directory for a module already exists
                for f in os.listdir(self.outmodule):
                    if f.endswith('.mod') and not kwargs.get("combine",False):
                        os.remove(os.path.join(self.outmodule,f))
            else: os.makedirs(self.outmodule)
    
            # Build event (if required) 
            try: 
                if self.makecmd != '':              
                    # Execute again to account for input added after compiling command
                    self.Build(self.compargs)      
                    if os.path.isfile(self.intermediate_wrapper):      
                        Utility.ReplaceTextinFile(self.intermediate_wrapper, self.wrapper_module, {'%pyx_source%':'"'+self.buildname+'"'}, source=self.scrtdir)
                    Utility.Popen(self.makecmd+self.linkcmd+cmd, self.verbose)
            except:
                pass               

            # Post-build event (if required)
            try:     
                if self.postcmd != '':                    
                    Utility.Popen(self.postcmd, self.verbose)                          
            except:
                pass

            # Combine event (needed for TOMS). Combine multiple libraries into ONE.
            if self.isStatic and kwargs.get("combine", False):
                sep = ' '; librarian = 'lib '; ext = '.lib'
                mergedid = os.path.basename(self.outmodule)
                multi_libs = [os.path.join(self.outlibs,x) for x in [list(Utility.ArbitraryFlattening(x[2])) for x in Utility.PathWalk(self.outlibs)][0] if x.startswith(mergedid)]
                
                try:
                    # Remove old combined library from the list.
                    multi_libs.remove(os.path.join(self.outlibs,mergedid+self.architecture+ext))
                except:
                    pass
                
                self.postcmd = self.iniCompiler + sep + librarian +sep.join(multi_libs) +' -nologo -machine:'+self.architecture+' -out:'+os.path.join(self.outlibs,mergedid+self.architecture+ext)      
                Utility.Popen(self.postcmd, self.verbose)               
                for lib in multi_libs:
                    os.remove(os.path.join(self.outlibs,lib))
    
            # Finish and delete redundant files      
            if not self.isStatic:
                os.remove(os.path.join(self.outlibs,self.libname+'.exp'))
                os.remove(os.path.join(self.outlibs,self.libname+'.lib'))    
            Utility.DeleteFilesbyEnding(self.temps)
        pass
    
## @class PyXMake.Build.Make.PyReq
# Base class for all PyReq build events. Inherited from Custom.      
class PyReq(Custom):
    """
    Inherited class to build projects using PyReq.
    """  
    def __init__(self, *args, **kwargs):
        """
        Initialization of PyReq class object.
        
        @note Creates a list of all 3rd party dependencies of a package using PyReq.
        """      
        super(PyReq, self).__init__(*args, **kwargs)
        ## String identifier of current instance.        
        self.MakeObjectKind = "PyReq"
        
        # Remove all default libraries, paths and includes from Make class.
        self.libs = []
        self.libdirs = []
        self.incdirs = []
        
        # The default is no pre-processing.
        self.precmd = ""
        # Do not add version by default. 
        self.compargs = "--no-pin"
        pass
    
    def Preprocessing(self, cmdstring=''):
        """
        Assemble command string for the pre-build event.
        """        
        delimn = " "
        # Store command string in object
        ## Command executed during pre-build event.
        self.precmd = delimn.join([self.iniCompiler,cmdstring])                      
        pass
    
    @classmethod
    def parse(cls, **kwargs): # pragma: no cover
        """
        Execute the current class as a CLI command.
        """
        # Import its main from VTL  
        from PyXMake.VTL import pyreq
        # Evaluate current command line
        command = kwargs.get("command",sys.argv)
        # Process all known arguments    
        parser = argparse.ArgumentParser(description='CLI wrapper options for  dependency detection tool.')
        parser.add_argument('name', type=str, nargs=1, help="Name of the project")
        parser.add_argument('--source', type=str, nargs=1, help="Absolute path to project folder.")
        parser.add_argument("--output", type=str, nargs=1, help="Absolute path to output directory. Defaults to current project folder.")
        parser.add_argument("--file", type=str, nargs=1, help="Output file name. Defaults to requirements.txt")
        parser.add_argument("--check", type=Utility.GetBoolean, const=True, default=True, nargs='?', 
            help="Check public PyPi repository to verify the results. Defaults to True.")
        parser.add_argument('--command', nargs=argparse.REMAINDER, help="Additional command line parameters.")
        # Command line separator
        delimn = " "
        # Check all options or run unit tests in default mode   
        try:
            # Check CLI options
            _ = command[1]
            args, _ = parser.parse_known_args(command[1:])        
            # Project name is mandatory
            project = args.name[0]
            # Check optional command line arguments
            try: source = args.source[0] ; 
            except:
                # Get path from the project name.
                handle = importlib.import_module(project)
                source = os.path.abspath(handle.__path__[0])
            # Optional non-default output directory
            try: output = args.output[0]
            except: output = os.path.abspath(os.getcwd())
            # Optional non-default package check
            try: check = args.check[0]
            except: check = True
            # Optional non-default output filename
            try: filename = args.file[0]
            except: filename = 'requirements.txt'
            # Optional non-default additional command line options for pipreqs.
            try: command = args.command[0]
            except: command = delimn.join(["--ignore","cmd,bin,Core,Plugin","--no-pin"])   
        # Use an exception to allow help message to be printed.
        except Exception as _:
            # Build all supported features
            if AllowDefaultMakeOption:     
                # Command line separator
                delimn = " "
                # Get absolute path to gather information about package requirements.     
                from PyXMake import PyXMakePath; from PyCODAC import PyCODACPath #@UnresolvedImport
                # Gather latest dependencies from PyXMake's code base.
                pyreq("PyXMake", source=PyXMakePath, 
                compargs=delimn.join(["--ignore","cmd,bin","--no-pin"]), output=os.getcwd(), check=True)           
                # Gather latest dependencies from PyCODAC's code base.
                pyreq("PyCODAC", source=PyCODACPath, 
                compargs=delimn.join(["--ignore","cmd,bin,Core,Plugin","--no-pin"]), output=os.getcwd(), check=True)
                try:                 
                    # Gather latest dependencies from DELiS's code base.
                    pyreq("DELiS", source=os.path.join(PyCODACPath,"Plugin","DELiS","src","delis"), 
                    compargs=delimn.join(["--no-pin"]), output=os.getcwd())
                except: pass
                try:                     
                    # Gather latest dependencies from Smetana's code base.
                    pyreq("Smetana", source=os.path.join(PyCODACPath,"Plugin","Smetana","src","smetana"), 
                    compargs=delimn.join(["--ignore","gopak,curvefit,test,static","--no-pin"]), output=os.getcwd())
                except: pass
        # Execute valid CLI command
        else: pyreq(project, source, output, check=check, filename=filename, compargs=command)
        pass
    
    def create(self,**kwargs):
        """
        Execute make command
        """                   
        # Increase recursion limit (required for OCC)
        sys.setrecursionlimit(kwargs.get("recursion_limit",5000))
        delimn = " "; linebreak = "\n"
        
        # Go into scratch folder
        with Utility.ChangedWorkingDirectory(self.scrtdir):
            
            # Pre-build event  (if required)          
            try: # pragma: no cover
                if self.precmd.split() > 1 and self.precmd != "":
                    Utility.Popen(self.precmd, self.verbose)                         
            except:
                pass
            
            # Run build command
            data = Utility.GetRequirements(self.srcdir, getattr(self,"compargs","--no-pin").split(delimn), **kwargs)

        # Create  a summary as a markdown file
        try:
            with open(os.path.join(self.outdir,kwargs.get("filename",self.buildid+".md")), "w+") as output:
                output.write(linebreak.join(str(item) for item in data))
        except:
            pass
        return    

## @class PyXMake.Build.Make.Py2X
# Base class for all Py2X (for now only f2py) build events. 
# Inherited from Make and flavors in dependence of the underlying or requested operating system (optionally).
class Py2X(Make,NT,POSIX):
    """
    Inherited class to build projects using Py2X.
    """
    class patch(object):
        """
        Patch class for monkey patching f2py as a context manager
        """
        def __init__(self, **kwargs):
            """
            Initialization of context manager
            """      
            # Parse verbosity level and command line from parent class
            self.verbose = kwargs.get("verbose",0)
            self.makecmd = kwargs.get("command","")
            self.default_encoding = kwargs.get("use_default_encoding",sys.version_info <= (3,0))
            pass
            
        def __enter__(self): # pragma: no cover
            """
            Entering the context manager.
            """
            # Global list for patch recovery
            self.ListofPatches = {}
            # Create a local list of all files to patch on the fly - if necessary
            newline = "\n"; ListofPatches = []
            # Access some sub-packages
            if sys.version_info < (3, 12):
                from numpy.distutils.fcompiler import gnu
                from numpy.distutils import ccompiler
                from numpy.distutils import misc_util
                # Add to the list of patches when version <=3.12
                ListofPatches += [gnu, ccompiler, misc_util]
            # All other cases
            from numpy.f2py import crackfortran, auxfuncs, f2py2e
            from packaging.version import parse
            # These entries are always present
            ListofPatches += [crackfortran]
            
            try:
                # Resolving compatibility issue > Python 3.6
                from re.RegexFlag import MULTILINE
            except ImportError:
                # Python 3.5 & lower
                from re import MULTILINE
            pass
        
            # Modify numpy on the fly
            for x in ListofPatches:
                # Exception handling when executing in a Docker container instance.
                if Utility.IsDockerContainer() and Utility.GetPlatform() in ["linux"] and not os.access(x.__file__, os.W_OK):
                    self.Permission = str(oct(stat.S_IMODE(os.lstat(x.__file__).st_mode))); 
                    subprocess.check_call(["sudo","chmod","777",x.__file__])
        
            # Modify f2py's routines to support UTF-8 in any case
            if sys.version_info < (3, 12):
                # Only modify conditionally
                with open(gnu.__file__,"r") as f: gnustream = f.read();
                with open(ccompiler.__file__,"r") as f: ccompstream = f.read();
                with open(misc_util.__file__,"r") as f: utilstream = f.read();
            # Always attempt to modify these files
            with open(auxfuncs.__file__,"r") as f: auxstream = f.read();
            with open(crackfortran.__file__,"r") as f: crackstream = f.read();
            with open(f2py2e.__file__,"r") as f: f2py2estream = f.read();
            
            # Set an environment variable to avoid removing LDFlags accidently 
            if sys.version_info < (3,7): os.environ.update({"NPY_DISTUTILS_APPEND_FLAGS":"1'"})
            
            # Replace substring if version is not sufficient.
            if sys.version_info < (3, 12):
                with open(gnu.__file__,"w") as f:
                    # Replace the following with numpy's source code. This was fixed in version 1.19.1
                    target = "v >= '4.'"; replace = "int(v.split('.')[0]) >= int('4')"; 
                    pattern = re.compile(target,MULTILINE); _ = gnustream; 
                    # Replace substring if version is not sufficient.
                    if Utility.GetPlatform() in ["windows"]: _ = gnustream.replace('["<F90>", "-Wall", "-g"],','["<F90>", "-Wall", "-g","-static","-static-libgcc","-static-libgfortran"],')
                    if re.search(pattern,_) and not parse(np.__version__) >= parse("1.19.0"):
                        if self.verbose >= 2:
                            print("==================================")
                            print("On-the-fly patching of numpy version %s" % np.__version__)
                            print("==================================")
                            _ = re.sub(pattern,replace,_)            
                    f.write(_)                        
                # Replace all problematic statements
                with open(misc_util.__file__,"w")  as f: 
                    # Modify statements in-place
                    if utilstream.find(str("import textwrap")) != -1:
                        _ = utilstream.replace(str("import textwrap"),str("import textwrap, io"))
                    else: _ = utilstream.replace(str("import os"),str("import os, io"))
                    # Enforce correct encoding.
                    _ = _.replace(str("open(source, 'r')"),str('io.open(source, "r", encoding="utf-8")')); f.write(_)
            with open(crackfortran.__file__,"w") as f: 
                # Modify statements in-place
                _ = crackstream.replace(str("import fileinput"),str("import fileinput, io"))
                _ = _.replace(str("fileinput.FileInput(ffile)"),str("fileinput.FileInput(ffile,openhook=fileinput.hook_encoded('utf-8'))"))
                # Check if version is below 3.
                if sys.version_info <= (3,0): _ = _.replace(str(r'\xa0'),str(r'\t'))
                # Verify that fixed form format is correctly identified under all circumstances
                if self.makecmd.find("-fixed") != -1 and parse(np.__version__) >= parse("1.26.0"):
                    # This has two hits. But one is in the __main__ section of the code and thus irrelevant
                    _ = _.replace(str("sourcecodeform = 'free'"),str("sourcecodeform = 'fix'")); 
                # Apply fix to source code format detection.
                _ = _.replace(str("COMMON_FREE_EXTENSIONS = ['.f90', '.f95', '.f03', '.f08']"),str("COMMON_FREE_EXTENSIONS = []"))
                # Modify source code
                _ = _.replace(str("open(file, 'r')"),str('io.open(file, "r", encoding="utf-8")')); f.write(_)
            # Modify auxiliary code when using old version. Established backwards compatibility. 
            if sys.version_info <= (3,0): 
                with open(auxfuncs.__file__,"w") as f:
                    # Ensure that all rules can be found. No type mixing allowed.
                    _ = auxstream.replace(str("if isinstance(rules[k], str)"),str("if isinstance(rules[k], basestring)"))
                    _ = _.replace("ret[k] = replace(rules[k], d)","ret[k] = str(replace(str(rules[k]), d))")
                    f.write(_)
            if parse(np.__version__) >= parse("1.26.0"): 
                with open(f2py2e.__file__,"w") as f:
                    _ = f2py2estream.replace(str("iline = (' '.join(iline)).split()"),str("iline = (os.pathsep.join(iline)).split(os.pathsep)"))
                    f.write(_)
            ## Always compile all sources with permissive. For now. 
            # Use this hack to sneak the compile option to f2py
            if sys.version_info < (3, 12) and parse(np.__version__) < parse("2.0.0"):
                with open(ccompiler.__file__,"w") as f:
                    # Ensure that source code is compiled with relaxed rules
                    _ = ccompstream.replace("ccomp = self.compiler_so","self.compiler_so += ['-fpermissive','-fno-strict-aliasing']; ccomp = self.compiler_so")
                    f.write(_)
                    
            ## Backwards compatibility changes for meson
            # Collect all required changes for meson here
            if os.path.exists(os.path.join(os.path.dirname(crackfortran.__file__),"_backends","_meson.py")):
                # Only attempt to import here
                from numpy.f2py._backends import _meson
                # Local default values
                directives = []; patch = "self.substitutions.update({'python':self.substitutions.get('python').encode('unicode_escape').decode()})"
                # Blanks are not handled correctly
                patch = ntpath.pathsep.join([patch, 
                    "self.substitutions.update({'inc_list':self.substitutions.get('inc_list').replace('+20',' ')})",
                    "self.substitutions.update({'lib_dir_list':self.substitutions.get('lib_dir_list').replace('+20',' ')})"])
                # Modify projects arguments on windows with commercial compiler only
                if Utility.GetPlatform() in ["windows"] and not os.getenv("pyx_cflags",False): 
                    directives = [x for x in shlex.split(self.makecmd) if x.startswith("-D")]; 
                    # Assist meson in using all given compile parameters
                    os.environ.update({"MESON_FFLAGS":self.makecmd.split("--f90flags=")[-1].split('"')[1::2][0]+" /names:lowercase"})
                # Read meson files
                with open(_meson.__file__,"r") as f: mesonstream = f.read();
                with open(os.path.join(os.path.dirname(_meson.__file__),"meson.build.template"),"r") as f: mesontemplate = f.read();
                # Open main
                with open(_meson.__file__,"w") as f:
                    # Version 1.26 does not find python by itself due do path mangling...
                    _ = mesonstream.replace("template = Template(self.meson_build_template())","template = Template(self.meson_build_template()); "+ patch); 
                    # Requires cross compilation
                    if os.path.exists(os.path.join(os.getcwd(),".meson_mapping")) and os.getenv("pyx_cflags",False): 
                        _ = _.replace('["meson", "setup", self.meson_build_dir]',r'["meson", "setup", self.meson_build_dir,"--cross-file",r"%s"]' % os.path.join(os.getcwd(),".meson_mapping"))
                    f.write(_)
                # Open template
                with open(os.path.join(os.path.dirname(_meson.__file__),"meson.build.template"),"w") as f:
                    # Always add support for preprocessor commands and custom compiler flags
                    patch = newline.join("add_project_arguments('%s', language: 'c')" % s for s in directives)
                    patch = newline.join([patch,
                        """f90flags_f2py = run_command(py, ['-c', 'import os; print(os.getenv("MESON_FFLAGS"))'], check : true).stdout().strip().split()""",
                        "add_project_arguments(f90flags_f2py, language : 'fortran')"])
                    patch = newline.join([patch, "add_project_arguments('-fpermissive', language : 'c')"])
                    _ = mesontemplate.replace("np_dep = declare_dependency(include_directories: inc_np)","np_dep = declare_dependency(include_directories: inc_np)\n"+patch)
                    f.write(_)
                # Update all these files regardless of execution
                self.ListofPatches.update({"meson_file": [_meson.__file__, mesonstream]})
                self.ListofPatches.update({"meson_template": [os.path.join(os.path.dirname(_meson.__file__),"meson.build.template"), mesontemplate]})
                
            ## HOTFIX for older interpreters. Do not mess with the default encoding.
            # Modify auxiliary code when using old version. Established backwards compatibility. 
            if self.default_encoding:                             
                # Modify f2py to support UTF-8 in any case
                with open(crackfortran.__file__,"w") as f: f.write(crackstream)
                with open(auxfuncs.__file__,"w") as f: f.write(auxstream)
                # Only relevant in deprecated versions
                if sys.version_info < (3,12): 
                    with open(misc_util.__file__,"w") as f: f.write(utilstream)          
            # Modify f2py to support UTF-8 in any case
            if sys.version_info < (3,12): 
                # Conditional streams
                setattr(self, "gnustream", gnustream); setattr(self, "gnu_file", gnu.__file__)
                setattr(self, "ccompstream", ccompstream); setattr(self, "ccompiler_file", ccompiler.__file__)
                setattr(self, "utilstream", utilstream); setattr(self, "util_file", misc_util.__file__)
            # Always refer to the streams below
            setattr(self, "crackstream", crackstream); setattr(self, "crackfortran_file", crackfortran.__file__)
            setattr(self, "auxstream", auxstream); setattr(self, "auxfuncs_file", auxfuncs.__file__)
            setattr(self, "f2py2estream", f2py2estream); setattr(self, "f2py2e_file", f2py2e.__file__)        
            pass
    
        def __exit__(self, *args):
            """
            Leaving the context manager
            """
            # Reconfigure new build setup in f2py 
            for _, content in getattr(self, "ListofPatches",{}).items(): 
                with open(content[0],"w") as f: f.write(content[-1])
            # Modify f2py to support UTF-8 in any case
            if sys.version_info < (3,12): 
                # Conditional streams
                with open(self.gnu_file,"w") as f: f.write(self.gnustream)
                with open(self.ccompiler_file,"w") as f: f.write(self.ccompstream)
                with open(self.util_file,"w") as f: f.write(self.utilstream)
            # Always refer to the streams below
            with open(self.crackfortran_file,"w") as f: f.write(self.crackstream)
            with open(self.auxfuncs_file,"w") as f: f.write(self.auxstream)
            with open(self.f2py2e_file,"w") as f: f.write(self.f2py2estream)
            # Restore default access rights on GNU
            if Utility.IsDockerContainer() and Utility.GetPlatform in ["linux"]: subprocess.check_call(["sudo","chmod",getattr(self,"Permission"),self.gnu__file__])
            # Print information for the user.
            if self.verbose >= 2:
                print("==================================")
                print("Restoring numpy version %s" % np.__version__)
                print("==================================")
            # Return nothing
            pass
    
    def __init__(self, *args, **kwargs): # pragma: no cover
        """
        Initialization of Py2X class object.
        
        @note Currently uses f2py - but should be build with Py2X (DLR) in the future  
        """      
        super(Py2X, self).__init__(*args, **kwargs)
        
        ## String identifier of current instance.        
        self.MakeObjectKind = 'Py2X'
        
        ## Define whether Intel's MKL should be statically or dynamically linked.
        # Defaults to True, meaning that Intel's MKL has to be provided by the operating system.
        self.no_static_mkl = kwargs.get('no_static_mkl', True)

        ## Define whether Intel's MKL should be discarded
        # Defaults to False on NT systems. Defaults to True on Linux systems in a Docker instance. Overwrites previous setting.
        self.no_mkl = kwargs.get("no_mkl", self.hasFoss and (Utility.GetExecutable("choco") or Utility.GetPlatform() in ["linux","cygwin","msys","darwin"]))     

        ## Define whether the architecture shall be appended to the build name. 
        # Defaults to False, meaning that the architecture is appended.
        self.no_append_arch = kwargs.get('no_append_arch', False)
        
        ## Define if the input should be compiled exactly as provided.
        # Defaults to False, meaning that merging & pre-processing utilities will be carried out.
        self.incremental = kwargs.get('incremental', False)                      
        
        # Immutable settings for Py2X object      
        ## Absolute system path to Python executable.  
        self.path2exe = sys.executable.replace("\python.exe","")
        ## The executable command used in the main build event.
        self.exe = 'python.exe'

        # Interoperability change. Always put executables in quotes (who would have guessed...)
        self.exe = '"{}" '.format(os.path.join(self.path2exe,self.exe))

        # Get valid f2py call.
        old_numpy_call = os.path.join(self.path2exe, "Scripts","f2py.py")
        new_numpy_call =  os.path.join(self.path2exe, "Scripts","f2py.exe")
        
        # Check if meson is required.
        from packaging.version import parse
        from numpy.version import version as _version
        meson_required = bool(parse(_version) >= parse("1.26.0") or sys.version_info >= (3,12))
        
        # Find f2py executable                        
        if os.path.exists(old_numpy_call) and not meson_required:
            self.exe += '"{}"'.format(old_numpy_call)
            os.environ["pyx_compiler"] = " ".join([sys.executable,old_numpy_call])
        elif os.path.exists(new_numpy_call) and not meson_required:
            self.exe = '"{}"'.format(new_numpy_call)
            os.environ["pyx_compiler"] = new_numpy_call
        else: 
            ## Verify that a f2py version is accessible
            from numpy import f2py
            ## We are either on Linux or within a virtual environment (Poetry). Attempt to find f2py through the
            # $PATH variable. Raise an error to indicate that the operation will not succeed.
            os.environ.update({"PATH":os.pathsep.join([os.getenv("PATH")]+
                              [y for y in Utility.ArbitraryFlattening(
                              [[os.path.join(f2py.__path__[0].split(os.path.sep+"lib")[0],"bin")]+
                              [os.path.join(os.path.dirname(x),"Scripts") if Utility.GetPlatform() in ["windows"] else 
                               os.path.join(os.path.dirname(x),"bin") for x in sys.path if x.lower().endswith("lib")]])
                               if os.path.exists(y)] )})
            # Find f2py in global PATH variable
            found, self.exe = Utility.GetExecutable("f2py", get_path=True)
            # Raise a runtime error if unsuccessful
            if not found: raise RuntimeError("f2py could not be found on the system.")
            # Otherwise, use the absolute path
            os.environ["pyx_compiler"] = self.exe
            self.exe = '"{}"'.format(self.exe)
            self.path2exe = ""
            
        ## Temporary build name of current job.
        self.buildname = self.buildid+"_pyd"+self.architecture+".f90"
        
        if self.architecture == "x86":
            mkl_interface_lib = "mkl_intel_c"
        else:
            mkl_interface_lib = "mkl_intel_lp64"
            
        if self.no_mkl:
            # Remove include files from MKL explicitly if requested
            if version.parse(np.__version__) >= version.parse("1.26.0"): 
                for x in copy.deepcopy(self.incdirs):
                    if "mkl" in x: self.incdirs.remove(x)
            # Do nothing
            else: pass
        elif not self.no_static_mkl:  
            # Link statically against MKL library. Deactivate this option by default.    
            self.libs.append([mkl_interface_lib, "mkl_intel_thread", "mkl_core", "libiomp5md"])
            self.libs = list(Utility.ArbitraryFlattening(self.libs))
        else:
            # Provide additional default dependencies (required for MCODAC).
            if Utility.IsDockerContainer() and Utility.GetPlatform() not in ["windows", "msys"]: self.libs.append(["gomp","ifcore"])
            # Link dynamically against MKL library. 
            self.libs.append("mkl_rt")
            self.libs = list(Utility.ArbitraryFlattening(self.libs))
            
        # MKL is requested. Update library path to include local pip dependencies.
        if not self.no_mkl or not self.no_static_mkl or any(["mkl" in x for x in self.libs]):
            # Always add local path to library search path.
            prefix = "Library" if Utility.GetPlatform() in ["windows"] else ""
            # Catch exception while running in a local virtual environment
            base = os.path.dirname(os.path.dirname(os.getenv("pyx_compiler", sys.prefix)))
            # Update library search paths
            self.libdirs.extend([os.path.join(x,prefix,"lib") for x in (sys.prefix, base)])
            # Remove duplicate entries
            self.libdirs = list(set(self.libdirs))

        if self.no_append_arch:
            self.architecture = ''

        # Immutable settings for Py2X object       
        if self.incremental:         
            c_files = [x for x in self.srcs if os.path.splitext(x)[1].lower() in (".for", ".f95", ".f", ".f90")]        
            self.exe += ' -c -m %s %s' % (self.buildid+self.architecture, ' '.join(c_files))              
        else:
            self.exe += ' -c -m %s %s' % (self.buildid+self.architecture, self.buildname)   
        
        # Copy default mapping file to scratch directory (eq. workspace if not specified)
        if not self.bare: 
            meson_cross_file=textwrap.dedent( """
            [host_machine]
            system = 'windows'
            cpu_family = 'x86_64'
            cpu = 'x86_64'
            endian = 'little'
    
            [binaries]
            c = 'gcc'
            cpp = 'g++'
            fortran = 'gfortran'
            ar = 'ar'
            ld = 'ld'
            objcopy = 'objcopy'
            strip = 'strip'
            pkg-config = 'pkg-config'
            windres = 'windres'
            """)
            with open(os.path.join(self.scrtdir,".meson_mapping"),"w") as f: f.write(meson_cross_file)
            copyfile(os.path.join(Path2Config,".f2py_f2cmap"), os.path.join(self.scrtdir,".f2py_f2cmap"))

        # Strip path from executable if already present.
        if self.exe.startswith(self.path2exe,1):
            self.path2exe = ""
        
        ## Tuple of temporary files deleted after job completion. Has already stored custom variable declaration
        # mapping file used by f2py.
        self.temps = self.temps + (".f2py_f2cmap",".meson_mapping", self.buildname)
        
        ## Iterate through all active processes matching the current BuildID 
        # and kill them. Do not attempt on public machines (kills everything silently).
        if Utility.IsDockerContainer() and not self.bare:
            for proc in psutil.process_iter():
                if os.getpid() == proc.pid:
                    continue # Skip self.
                try:
                    for key, value in proc.as_dict().items():
                        if (str(self.buildid) in str(key) or str(self.buildid) in str(value)) and Utility.IsNotEmpty(self.buildid):
                            # Get process name & PID from process object. Kill the process and write a message.
                            proc_delimn = " "; processName = proc.name(); processID = proc.pid; #proc.kill() 
                            print("==================================")
                            print("Found existing child process @ %s" %  proc_delimn.join([str(processName),':::',str(processID)]))
                            print("The process is aborted for compilation")
                            print("==================================")
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
                
                # Skip evaluation after one successful run.
                if not Utility.IsNotEmpty(self.buildid): break

        # Identify source code and BuildID and set the corresponding environment variables for Mingw64 and Linux.
        if kwargs.get("bash", self.hasFoss):            
            try:
                os.environ["pyx_buildid"], os.environ["pyx_source"] = (self.buildid+self.architecture, ' '.join(c_files))
            except:
                os.environ["pyx_buildid"], os.environ["pyx_source"] = (self.buildid+self.architecture, self.buildname)
        pass
    
    @staticmethod
    def inspect(package,**kwargs): # pragma: no cover
        """
        Inspect the content of a given f2py package. Returns all qualified modules with their respective functions
        """
        # Create a modifiable condition
        def condition(x): return kwargs.get("custom_condition",not x.startswith("_") and not x.endswith("__"))
        # Collect all modules
        all_modules = [x for x in dir(package) if condition(x)]
        # Return all functions associated with a given module. 
        return [".".join([package.__name__,x,y]) for x in all_modules for y in dir(getattr(package, x)) if condition(y)]
    
    @staticmethod
    def show(package, feature, **kwargs): # pragma: no cover
        """
        Inspect the documentation content of a given f2py package feature by default.
        Optional, define callback to return any other existing attribute.
        """
        import functools
        delimn = ".";  anchor = feature.split("."); 
        # Helper functions
        def rgetattr(obj, attr, *args):
            """
            Get an attribute from a nested object.
            
            @note: https://stackoverflow.com/questions/31174295/getattr-and-setattr-on-nested-subobjects-chained-properties
            """
            def _getattr(obj, attr):
                """
                Wrapper of existing getattr function
                """
                try: result = getattr(obj, attr, *args)
                except:
                    relative = "."*(anchor.index(str(attr))-1)+str(attr)
                    result = importlib.import_module(relative, package=".".join(anchor[0:relative.count(".")+1]))
                return result
            return functools.reduce(_getattr, [obj] + attr.split('.'))
        # Import the given module
        module = importlib.import_module(package.__name__)
        # Collect the requested attribute. Remove the package name itself
        attributes = delimn.join([x for x in feature.split(delimn) if x not in [package.__name__]])
        # Return the attributes docstring
        return getattr(rgetattr(module, attributes),kwargs.get("callback","__doc__")) if (attributes and attributes not in [delimn]) else getattr(module,kwargs.get("callback","__doc__"))
    
    @staticmethod
    def callback(*args): # pragma: no cover
        """
        Get callback of any Python object.
        """
        # Access callback of any Python object directly.
        return Py2X.show(*args,callback="__call__")
    
    @classmethod
    def parse(cls, *args, **kwargs): # pragma: no cover
        """
        Execute the current class as a CLI command.
        """
        # Import its main from VTL  
        from PyXMake.VTL import py2x
        # Evaluate current command line
        command = kwargs.get("command",sys.argv)
        # Process all known arguments        
        parser = argparse.ArgumentParser(description="Build a shared Fortran library for current Python executable", parents=[Py2X.__parser__()])
        parser.add_argument('-l', '--libs', nargs='+', default=[], help="List of all libraries used to resolve symbols. The libraries are evaluated in the given order.")
        parser.add_argument('-d', '--dependency', nargs='+', default=[], help="Additional search paths to resolve library dependencies.")
        parser.add_argument("--format", type=str, nargs=1, help="Toggle between fixed and free format code style. Defaults to Fixed.")
        parser.add_argument("--incremental", type=Utility.GetBoolean, const=True, default=False, nargs='?', 
            help="Toggle between incremental and non-incremental build. Defaults to False.")
        parser.add_argument("--foss", type=Utility.GetBoolean, const=True, default=True, nargs='?', 
                            help="Toggle to enforce free-open source builds. Defaults to True.")
        # Check all options or run unit tests in default mode
        try:
            # Check CLI options
            _ = command[1]
            args, _ = parser.parse_known_args(command[1:])
            # Project name is mandatory
            project = args.name[0]
            # Specification of source directory is mandatory
            source = args.source[0] ; 
            # Optional non-default output directory
            try: output = Py2X.sanitize(args.output[0])
            except: output = os.path.abspath(os.getcwd())
            # Optional non-default scratch directory
            try: scratch = args.scratch[0]
            except: scratch = os.path.abspath(tempfile.gettempdir())
            # Optional code format style definition. Defaults to Fixed.
            try: fformat = args.format[0]
            except: fformat = "fixed"
            # Verbose output level. Defaults to ZERO - meaning no output. Can be increased to 2.
            try: verbosity = int(args.verbosity[0])
            except: verbosity = 2
            # Optional incremental build option. Defaults to False.
            try: incremental = Utility.GetBoolean(list(args.incremental)[0])
            except: incremental = False
            # Optional non-default package check
            try: foss = Utility.GetBoolean(list(args.foss)[0])
            except: foss = Utility.GetPlatform() in ["linux"]
            # Create a dictionary combining all settings
            settings = {"incremental": incremental,"source":source,
                                "output":output, "scratch":scratch,"format":fformat,
                                "foss":foss,"verbosity":verbosity}
            # Loop over options requiring paths to be sanitized
            for option in ["files","libs"]: 
                # Optional non-default definition to add files and additional link libraries
                try: 
                    _ = getattr(args,option)
                    # Sanitize the given file and library names. 
                    sanitized = [Py2X.sanitize(x) for x in Utility.ArbitraryFlattening(getattr(args,option))]
                except: sanitized = []
                # If no files were given, use all files in the given source directory
                if option in "files" and not sanitized: sanitized = os.listdir(source)
                # Add all sanitized search paths to settings
                settings.update({option: sanitized})
            # Loop over options requiring paths to be sanitized
            for option in ["include", "dependency"]: 
                # Optional non-default definition of additional include directories
                try: 
                    _ = getattr(args,option)[0]
                    # Collect all given paths. Get system independent format
                    path = list(Utility.ArbitraryFlattening(getattr(args,option)));
                    path = [Py2X.sanitize(x) for x in path]
                    sanitized = Utility.GetSanitizedDataFromCommand(path)
                # No extra search paths have been given
                except: sanitized = []
                # Add all sanitized search paths to settings
                settings.update({option: sanitized})
        # Use an exception to allow help message to be printed.
        except Exception as _:
            # Local imports. These are only meaningful while executing an unit test
            from PyXMake import VTL
            # Build all supported features for current version (default options)
            if AllowDefaultMakeOption:         
                # Predefined script local variables
                __arch = Utility.GetArchitecture()
                __foss = kwargs.get("foss",Utility.IsDockerContainer() or Utility.GetPlatform() in ["linux"])
                try:
                    # Import PyCODAC to build library locally during setup.
                    from PyCODAC.Tools.Utility import GetPyCODACPath
                    # Import and set local path to PyCODAC
                    __mcd_core_path =  os.path.join(GetPyCODACPath(),"Core")
                except ImportError:
                    # This script is not executed as plug-in
                    __mcd_core_path = ""
                except:
                    # Something else went wrong.
                    from PyXMake.Tools import ErrorHandling
                    ErrorHandling.InputError(20)
                # Build BoxBeam
                BuildID = 'bbeam' 
                py2x(BuildID,
                        files=VTL.GetSourceCode(1), 
                        source=os.path.join(__mcd_core_path,"external","boxbeam"),
                        libs=[],include=[],dependency=[],
                        # BoxBeam binary is referenced in PyOCDAC. Updated is performed there
                        output=os.path.join(os.path.join(__mcd_core_path,"bin",Utility.GetPlatform(),__arch)), foss=__foss)
                # Build Beos   
                BuildID = 'beos' 
                py2x(BuildID,
                        files=VTL.GetSourceCode(2),
                        source=os.path.join(__mcd_core_path,"external","beos"),
                        libs=[],include=[],dependency=[],
                        # Beos binary is referenced in PyOCDAC. Updated is performed there
                        output=os.path.join(os.path.join(__mcd_core_path,"bin",Utility.GetPlatform(),__arch)), foss=__foss)
                # Build MCODAC (default settings)
                BuildID = "mcd_core"; py2x(BuildID, foss=__foss) 
        else:
            # Local import to command module
            from PyXMake import Command
            # Pop format identifier from settings
            fformat = settings.pop("format")
            # Execute CLI command
            py2x(project, command=Command.GetBuildCommand(0, _format=fformat), **settings)
    
## @class PyXMake.Build.Make.PyInstaller
# Base class for all PyInstaller build events. Inherited from Make.      
class PyInstaller(Make):
    """
    Inherited class to build projects using PyInstaller.
    """  
    def __init__(self, *args, **kwargs):
        """
        Initialization of PyInstaller class object.
        
        @note Creates stand-alone application of Python scripts using PyInstaller.
        """      
        super(PyInstaller, self).__init__(*args, **kwargs)
        ## String identifier of current instance.        
        self.MakeObjectKind = "PyInstaller"
        
        # Set build mode
        self.buildtype = kwargs.get("type","onefile")
        
        # Remove all default libraries, paths and includes from Make class.
        self.libs = []
        self.libdirs = []
        self.incdirs = []
        
        # Add specification file to temporaries
        self.temps += (self.buildid+".spec",)
        pass
    
    def Encryption(self, encrypt, **kwargs):
        """
        Encrypt byte-code by using user-supplied or randomly generated key.
        
        @author: garb_ma
        @param encrypt: Boolean
        """      
        if encrypt:
            self.key_string = kwargs.get("key_string",''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(16)))
        return
    
    def Preprocessing(self, cmdstring=''):
        """
        Assemble command string for the pre-build event.
        """        
        delimn = " "
        # Store command string in object
        ## Command executed during pre-build event.
        self.precmd = delimn.join([self.iniCompiler,cmdstring])                      
        pass
    
    def Build(self, mode="onefile", **kwargs):
        """
        Switch build mode. Defaults to one single file.
        """
        import py_compile
        # Get shorthands for compatibility modes
        try:
            from PyInstaller.compat import is_py27 #@UnresolvedImport
        except:
            is_py27 = sys.version_info[0] == 2
        finally:
            from PyInstaller.compat import is_py35, is_py36, is_py37 #@UnresolvedImport
            
        # Parse relevant versions from packages
        from setuptools import __version__ as set_version #@UnresolvedImport
        from PyInstaller import __version__ as pyi_version
        
        # Set build mode
        self.buildtype = mode
        
        # Reset command
        self.makecmd = ""
        # Create base command and add additional options based on identified inputs.
        self.makecmd = ['--name=%s' % self.buildid,'--%s' % self.buildtype, '--clean', "--noconfirm"]#, "--windowed"]
        
        # Customize the application icon
        self.makecmd.append("--icon=%s" % kwargs.get("icon",os.path.join(Path2Config,"stm_logo.ico")))
         
        # Correction of required missing import for new releases of setuptools. Deprecated since major release 49
        if version.parse("45.0.0") < version.parse(set_version) < version.parse("49.0.0"): # pragma: no cover
            self.makecmd.insert(1,'--hidden-import=%s' % "pkg_resources.py2_warn")
        # Adding request library explicitly.
        if version.parse(set_version) >= version.parse("64.0.0"): self.makecmd.insert(1,'--hidden-import=%s' % "requests")
         
        # Use UPX compression to create a smaller application folder/file
        if Utility.GetPlatform() in ["windows"]: # pragma: no cover
            # Attempt to find UPX from global installation path
            if Utility.GetExecutable("upx"): self.makecmd.append("--upx-dir=%s" % Utility.GetExecutable("upx", get_path=True)[-1])
            # Fetch supplied executable from path (deprecated, path will not exists in the future)
            elif os.path.exists(os.path.join(PyXMakePath,"Build","bin","upx")): self.makecmd.append("--upx-dir=%s" % os.path.join(PyXMakePath,"Build","bin","upx"))
                       
            # Some binaries are unusable after the obfuscation process. We skip those here.
            if is_py27:
                excludes =  ["python2.dll","python27.dll", "qwindows.dll"]
            elif is_py35:
                excludes =  [x for x in os.listdir(os.path.dirname(sys.executable)) if x.endswith((".dll"))]
            elif is_py36:
                excludes =  [x for x in os.listdir(os.path.dirname(sys.executable)) if x.endswith((".dll"))]              
            elif is_py37:
                excludes =  ["python3.dll","python37.dll","ucrtbase.dll", "qwindows.dll"]
 
            ## Remove the complete scipy package from UPX shrinking
            # 28.06.2021 // garb_ma
            try:
                import scipy
                # Add scipy exceptions
                if version.parse(scipy.__version__) <= version.parse("1.6.3"): excludes.extend(Utility.ArbitraryFlattening([x[-1] for x in os.walk(scipy.__path__[0])])) #@UndefinedVariable
            except: pass
                           
            upx_exclude = ["--upx-exclude=%s" % x for x in excludes]
            self.makecmd.extend(upx_exclude)
        # Do not execute image size reduction using UPX
        else: self.makecmd.extend(["--noupx"])
 
        # Mark additional Python files to be (re-compiled) before copying directly into the executable.
        add_compile = list(Utility.ArbitraryFlattening(kwargs.get("add_compile",[])))
        
        # Add additional include directories
        if hasattr(self, "incdirs"): # pragma: no cover
            for data in self.incdirs:
                if os.path.exists(data.split(os.path.pathsep)[0]):
                    new_path = data.split(os.path.pathsep)[0]
                    # Compile source code files to byte-code
                    if Utility.PathLeaf(new_path).endswith(".py") and Utility.PathLeaf(new_path) in add_compile:
                        py_compile.compile(new_path,os.path.join(self.scrtdir,Utility.PathLeaf(new_path)+"c"))
                        self.temps = self.temps + (Utility.PathLeaf(new_path)+"c",)
                        new_path = os.path.join(self.scrtdir,Utility.PathLeaf(new_path)+"c")
                        data = os.path.pathsep.join([new_path,data.split(os.path.pathsep)[1]])
                    self.makecmd.insert(1,'--add-data=%s' % data)    
                else:
                    for path in sys.path:
                        new_path = os.path.join(path,data.split(os.path.pathsep)[0])
                        if os.path.exists(new_path) and os.path.isdir(new_path):
                            # Check if content of folders should be presented in plain text.
                            if not kwargs.get("add_plain",False):
                                for root, _, files in Utility.PathWalk(new_path):
                                    # Ignore repository folders (no exceptions!)
                                    if any(x in root for x in [".git", ".svn"]):
                                        continue
                                    for file in files:
                                        # Ignore files matching specified patterns
                                        if not file.endswith((".pdf")) and not any(x in file for x in [".cpython"]):
                                            base_path = data.split(os.path.pathsep)[-1]; sub_path = root.split(base_path)[-1]
                                            sub_struct =os.path.join(base_path,sub_path.lstrip(os.path.sep),".")
                                                                             
                                            if len(data.split(os.path.pathsep)) != 1:
                                                save_path = os.path.join(data.split(os.path.pathsep)[-1],".")
                                            else:
                                                save_path = sub_struct 
                                            # Skip python files if compiled scripts are available
                                            if file.endswith(".py") and os.path.exists(os.path.join(new_path,file+"c")):
                                                continue
                                            elif file.endswith(".py") and file in add_compile:
                                                # Compile all blank source files to byte-code to obfuscate the code.
                                                py_compile.compile(os.path.join(new_path.split(data.split(os.path.pathsep)[0])[0],sub_struct.rstrip("."),file),
                                                                                     os.path.join(new_path.split(data.split(os.path.pathsep)[0])[0],sub_struct.rstrip("."),file+"c"))
                                                file += "c"
                                            # Loop over all files within each directory and store them appropriately
                                            self.makecmd.insert(1,'--add-data=%s' % os.path.pathsep.join([os.path.join(new_path.split(
                                            data.split(os.path.pathsep)[0])[0],sub_struct.rstrip("."),file),save_path]))
                            else:
                                # Add folder content as-is to the application
                                self.makecmd.insert(1,'--add-data=%s' % os.path.pathsep.join([new_path,data.split(os.path.pathsep)[-1]]))   
                            break
                        # Check if new directory is a file. Preserve original path, otherwise do nothing.
                        elif os.path.exists(new_path) and os.path.isfile(new_path):
                            if Utility.PathLeaf(new_path).endswith(".py") and Utility.PathLeaf(new_path) in add_compile:
                                py_compile.compile(new_path,os.path.join(self.scrtdir,Utility.PathLeaf(new_path)+"c"))
                                self.temps = self.temps + (Utility.PathLeaf(new_path)+"c",)
                                new_path = os.path.join(self.scrtdir,Utility.PathLeaf(new_path)+"c")
                            self.makecmd.insert(1,'--add-data=%s' % os.path.pathsep.join([new_path,os.path.join(os.path.dirname(data.split(os.path.pathsep)[-1]),".")]))   
                            break    
                        else:
                            continue
        
        # Set working (scratch) directory if being defined
        if hasattr(self, "scrtdir"):
                self.makecmd.insert(1,'--specpath=%s' % os.path.join(self.scrtdir))    
                self.makecmd.insert(1,'--workpath=%s' % os.path.join(self.scrtdir,"build"))                         
             
        # Set output path if being defined. Defaults to current working directory
        if hasattr(self, "outdir"):
                self.makecmd.insert(1,'--distpath=%s' % os.path.join(self.outdir))                   

        # Add additional search paths
        if hasattr(self, "libdirs"):
            for path in self.libdirs:
                self.makecmd.insert(1,'--paths=%s' % path)          
        
        # Add encryption method. Deprecated in 
        if hasattr(self, "key_string") and version.parse(pyi_version) <= version.parse("6.0.0"):
            self.makecmd.insert(1,'--key=%s' % self.key_string)
            
        # Add source path (if given!)
        if hasattr(self, "srcdir") and self.srcdir:
            self.makecmd.append(os.path.join(self.srcdir,self.srcs[0]))
        else: # pragma: no cover
            self.makecmd.append(self.srcs[0])      
            
        # Set verbosity level
        if hasattr(self, "verbose"): # pragma: no cover
            if self.verbose <= 0:
                level = "ERROR"
            elif self.verbose == 1:
                level = "WARN"
            elif self.verbose >= 2:
                level = "INFO"       
            self.makecmd.insert(1,'--log-level=%s' % level)

    @classmethod
    def parse(cls, **kwargs): # pragma: no cover
        """
        Execute the current class as a CLI command.
        """
        # Import its main from VTL  
        from PyXMake.VTL import app
        # Evaluate current command line
        command = kwargs.get("command",sys.argv)        
        parser = argparse.ArgumentParser(description="Build a stand-alone python application.")
        parser.add_argument('name', type=str, nargs=1, help="Name of the project")
        parser.add_argument('source', type=str, nargs=1, help="Absolute path to the source file directory.")
        parser.add_argument('-f', '--file', nargs='+', default=[], help="Main entry point file.")
        parser.add_argument('-i', '--include', nargs='+', default=[], help="Additional files and folders required by the final executable.")
        parser.add_argument('-d', '--dependency', nargs='+', default=[], help="Additional search paths to resolve dependencies.")
        parser.add_argument("-o","--output", type=str, nargs=1, help="Absolute path to output directory. Defaults to current project folder.")
        parser.add_argument('-s', '--scratch', nargs='+', default=[], help="Default scratch folder for the build. Defaults to current workspace.")
        parser.add_argument("-v","--verbosity", type=str, nargs=1, help="Level of verbosity. Defaults to 0 - meaning no output. Max value is 2.")
        parser.add_argument("-m","--mode", type=str, nargs=1, default="onefile", help="Build type. Can be toggled between 'onefile' and 'onedir'.")
        parser.add_argument('--icon', type=str, nargs=1, help="Absolute path to a custom icon for the executable. Format: *.ico")
        parser.add_argument("--encryption", type=Utility.GetBoolean, const=True, default=False, nargs='?', 
            help="Toggle between encryption and non-encryption build. Defaults to False.")
        
        try:
            # Check CLI options
            _ = command[1]
            args, _ = parser.parse_known_args(command[1:])
            # Project name is mandatory
            project = args.name[0]
            # Specification of source directory is mandatory
            source = args.source[0] ; 
            # Optional non-default output directory
            try: file = args.file
            except: file = []   
            # Optional non-default output directory
            try: output = args.output[0]
            except: output = os.path.abspath(os.getcwd())
            # Optional incremental build option. Defaults to False.
            try: encryption = args.encryption[0]
            except: encryption = False
            # Optional non-default scratch directory
            try: scratch = args.scratch[0]
            except: scratch = os.path.abspath(os.getcwd())
            # Optional non-default additional include files and directories
            try: include = args.include[0]
            except: include = []
            # Optional non-default dependencies
            try: dependency= args.dependency[0]
            except: dependency = []
            # Optional non default build mode. Defaults to bundled one file.
            try: mode = args.mode[0]
            except: mode = "onefile"
            # Verbose output level. Defaults to ZERO - meaning no output. Can be increased to 2.
            try: verbosity = int(args.verbosity[0])
            except: verbosity = 0
            # Optional user-defined icon. If left blank, a default icon is used.
            try: icon = str(args.icon[0])
            except: icon = None
            # Create a dictionary combining all settings
            settings = {"script":file,
                                "source":source, "output":output, "scratch":scratch,
                                "mode":mode, "encryption": encryption,
                                "verbosity":verbosity, "icon":icon}
            # Only parse these settings when explicitly given
            if include: settings.update({"include":include})
            if dependency: settings.update({"dependency":dependency})
        # Use an exception to allow help message to be printed.
        except Exception as _:
            BuildID = "stmlab"
            # Build all supported features for current Python version (default options)
            if AllowDefaultMakeOption: app(str(BuildID.lower()), mode="onedir")
        # Execute valid CLI command
        else: app(project, **settings)
        pass
    
    def create(self,**kwargs):
        """
        Execute make command
        """
        # Import required package (only when function is actually executed)
        import PyInstaller.__main__ as pyi
               
        # Increase recursion limit (required for OCC)
        sys.setrecursionlimit(kwargs.get("recursion_limit",int(os.getenv("pyx_recursion_limit",5000))))
        
        # Go into scratch folder
        with Utility.ChangedWorkingDirectory(self.scrtdir): # pragma: no cover
            
            # Pre-build event  (if required)          
            try: 
                if self.precmd != '':      
                    Utility.Popen(self.precmd, self.verbose, collect=False)                         
            except:
                pass

            # Create make command
            self.Build(mode=self.buildtype, **kwargs)
            
            # Run build command
            pyi.run(self.makecmd)
            
            # Finish and delete redundant files
            Utility.DeleteFilesbyEnding(self.temps)        
            shutil.rmtree('build', ignore_errors=True)  

        # End of class method
        return # pragma: no cover
    
## @class PyXMake.Build.Make.NSIS
# Base class for all NSIS build events. Inherited from Make.      
class NSIS(Make):
    """
    Inherited class to build projects using NSIS.
    """  
    def __init__(self, *args, **kwargs):
        """
        Initialization of PyInstaller class object.
        
        @note Creates a portable installer of a source folder using NSIS.
        """      
        super(NSIS, self).__init__(*args, **kwargs)
        ## String identifier of current instance.        
        self.MakeObjectKind = "NSIS"
        
        # Remove all default libraries, paths and includes from Make class.
        self.libs = []
        self.libdirs = []
        self.incdirs = []
        
        # Immutable settings for NSIS object        
        ## Path to NSIS executable.
        self.path2exe = os.path.join(PyXMakePath,"Build","bin","nsis","App","NSIS")
        ## Executable of NSIS.
        self.exe = 'makensis.exe'
        
        # Initialize build command
        if Utility.GetExecutable("makensis"): # pragma: no cover
            self.makecmd = Utility.GetExecutable("makensis", get_path=True)[-1]
        else: self.makecmd = os.path.join(self.path2exe,self.exe)
        
        # Add specification file to temporaries
        self.temps += (self.buildid+".nsh",)       
        pass
    
    def FTP(self, user, key,  upload_file, host='ftp.dlr.de', path="/public/download/nightly"): # pragma: no cover
        """
        Define settings to establish a FTP connection. 
        """
        import ftplib
        # Establish FTP connection to file sharing server                                   
        ## Remote workspace. This is the upload directory for the given file
        self.ftp_client = ftplib.FTP(host, user, key)
        self.ftp_client.cwd(path)
        with open(upload_file, 'rb') as file:
            self.ftp_client.storbinary("STOR %s" % Utility.PathLeaf(upload_file), file)
        pass
    
    @classmethod
    def parse(cls, **kwargs): # pragma: no cover
        """
        Execute the current class as a CLI command.
        """
        # Import its main from VTL  
        from PyXMake.VTL import bundle
        # Evaluate current command line
        command = kwargs.get("command",sys.argv)
        # Process all known arguments        
        parser = argparse.ArgumentParser(description="Create a portable distribution using a compressed archive or NSIS")
        parser.add_argument('name', type=str, nargs=1, help="Name of the resulting archive(s).")
        parser.add_argument('source', type=str, nargs=1, help="Absolute path to distribution folder.")
        parser.add_argument('-f', '--files', nargs='+', default=[], help="Source file or list of all source files used in the creation of the documentation.")
        parser.add_argument("-o", "--output", type=str, nargs=1, help="Absolute path to output directory. Defaults to current working directory.")
        parser.add_argument("-e","--exclude", nargs='+', default=[], help="File extensions to be ignored during the process")
        parser.add_argument('-s', '--scratch', nargs='+', default=[], help="Default scratch folder for the build. Defaults to current workspace.")
        parser.add_argument("-v","--verbosity", type=str, nargs=1, help="Level of verbosity. Defaults to 0 - meaning no output. Max value is 2.")
        parser.add_argument("--use-nsis", type=Utility.GetBoolean, const=True, default=False, nargs='?',  help="Create an archive using NSIS. Defaults to False.")
        parser.add_argument('--extensions', nargs=argparse.REMAINDER, 
                            help="""
                            All archive extensions. Defaults to tar.gz. List given as string separated by commas. 
                            Possible values are <zip>, <tar>, <tar.gz>, <bz2>.
                            """)
    
        # Command line separator
        delimn = ","
        
        try:
            # Check CLI options
            _ = command[1]
            args, _ = parser.parse_known_args(command[1:])
            # Project name is mandatory
            project = args.name[0]
            # Check optional command line arguments
            source = args.source[0] ; 
            # Optional non-default output directory
            try: files = args.files
            except: files = "."
            # Optional non-default output directory
            try: output = args.output[0]
            except: output = os.path.abspath(os.getcwd())
            # Optional non-default NSIS check. Defaults to False.
            try: check = args.use_nsis[0]
            except: check = False
            # Optional non-default scratch directory
            try: scratch = args.scratch[0]
            except: scratch = os.path.abspath(os.getcwd())
            # Optional non-default exclude pattern
            try: excludes = args.exclude[0]
            except: excludes = [".git", ".svn", "__pycache__"]
            # Optional non-default additional extensions
            try: extensions= args.extensions[0]
            except: extensions = delimn.join(["tar","tar.gz","tar.bz2","zip"])
            finally: extensions = extensions.split(delimn)
            # Create a dictionary combining all settings
            settings = {"source":source, "output":output, "extensions":extensions, "files":files,
                                "scratch": scratch, "excludes":excludes, "use_nsis": check}
        # Use an exception to allow help message to be printed.
        except Exception as _:
            # Build all supported features
            if AllowDefaultMakeOption:
                # Create PyCODAC installer
                BuildID = "PyCODAC"; bundle(str(BuildID.lower()), use_nsis=Utility.GetExecutable("makensis"))
        # Execute valid CLI command
        else: bundle(project, **settings)
        pass

    def create(self, **kwargs): # pragma: no cover
        """
        Execute make command
        """    
        space = " "; point = "."; newline = '\n'
        
        # Create bundle command script
        script = ["Unicode true"]
        script.append("!define MULTIUSER_EXECUTIONLEVEL user")
        script.append("!define ZIP2EXE_NAME `%s`" % self.buildid)
        script.append("!define ZIP2EXE_OUTFILE `%s`" % os.path.join(self.outdir,point.join([self.buildid,"exe"])))
        script.append("!define ZIP2EXE_COMPRESSOR_LZMA")
        script.append("!define ZIP2EXE_INSTALLDIR `$EXEDIR`")
        script.append("!include `${NSISDIR}\Contrib\zip2exe\Base.nsh`")
        script.append("!include `${NSISDIR}\Contrib\zip2exe\Modern.nsh`")
        if kwargs.get("install_path",""):
            script.append("InstallDir '%s'" % kwargs.get("install_path","$Desktop"))
        script.append("!insertmacro SECTION_BEGIN")
        script.append("SetOutPath $INSTDIR")
        # Add all source files to the bundle
        for src in self.srcs:
            script.append("File /r /x *.nsh `%s`" % os.path.join(kwargs.get("assembly_path", self.srcdir),src))
        script.append("!insertmacro SECTION_END")
        script.append('Icon "%s"' % kwargs.get("icon",os.path.join(Path2Config,"stm_logo.ico")))
        script.append("RequestExecutionLevel user")
        
        # Go into scratch folder
        with Utility.ChangedWorkingDirectory(self.scrtdir if kwargs.get("use_nsis",True) else tempfile.gettempdir()):
            # Run build command
            MakeFile = Utility.GetTemporaryFileName(extension=".nsh") 
            
            # Populate script file with customizable features
            with open(MakeFile,"w") as f:
                f.write(newline.join(script))
            
            # Execute command
            self.makecmd = space.join([self.makecmd, "/V3", os.path.join(self.scrtdir,MakeFile)])
            
            ## Adding option to deactivate NSIS and instead use a compressed archive directly. 
            # Useful on POSIX system w/o NSIS support
            if kwargs.get("use_nsis",True): Utility.Popen(self.makecmd, self.verbose)
            else: 
                for ext in kwargs.get("extensions",["tar.gz"]): Utility.CreateArchive(os.path.join(self.outdir,".".join([self.buildid,ext])),self.srcdir, **kwargs)
            
            # Add temporary file to tuple scheduled for removal
            self.temps += (MakeFile,)       
            
            # Finish and delete redundant files
            Utility.DeleteFilesbyEnding(self.temps)   
            
            # Upload results to a file sharing server
            if kwargs.get("upload",False) and not hasattr(self, "ftp_client"):
                user = kwargs.get("user",os.getenv("username","")); key = kwargs.get("key","")
                self.FTP(user, key, point.join([os.path.join(self.outdir,self.buildid),"exe"]))
                
                # Success message
                print("==================================")
                print("Uploaded result to given FTP server")
                print("==================================")       

        # End of class method        
        pass

## @class PyXMake.Build.Make.Doxygen
# Base class for all Doxygen build events. Inherited from Make.          
class Doxygen(Make):
    """
    Inherited class to automatically build a documentation using Doxygen.
    """    
    def __init__(self, *args,**kwargs):
        """
        Initialization of doxygen class object.
        """                 
        super(Doxygen, self).__init__(*args,**kwargs)
        ## String identifier of current instance.        
        self.MakeObjectKind = 'Doxygen'
        
        os.environ['dox_pyjava'] = 'NO'        
        os.environ['dox_fortran'] = 'NO'            
        os.environ['dox_ccpp'] = 'NO'        
        os.environ['dox_pdflatex'] = 'NO'                                             

        # Immutable settings for Doxygen object        
        ## Path to Doxygen executable.
        self.path2exe = os.path.join(PyXMakePath,"Build","bin","doxygen")
        ## Executable of Doxygen.
        self.exe = 'doxygen.exe'
        
        ## Redefine default delete command in dependence of platform
        remove = "del"
        # Use rm on Linux platforms.
        if Utility.GetPlatform() == "linux": remove = "rm -rf"
        
        # Added Doxygen support for all systems.
        if Utility.GetExecutable("doxygen"): 
            _, doxy_path = Utility.GetExecutable("doxygen",get_path=True)
            self.path2exe = os.path.dirname(doxy_path)
            self.exe = Utility.PathLeaf(doxy_path)
            
        ## Update configuration file to the latest Doxygen syntax by default. Do not issue a warning (for now!)
        Utility.Popen(" ".join([os.path.join(self.path2exe,self.exe),"-u",os.path.join(Path2Config,"stm_doc_config")]),verbosity=0)
        
        ## Type of source file. Can be one of Fortran, CCpp or Other.
        # Defaults to Fortran if not specified. Starts documentation procedure
        # for Java/Python if type is neither Fortran nor CCpp.
        if self.stype == 'Fortran':
            os.environ['dox_fortran'] = 'YES'             
            ## Temporary build name of current job.             
            self.buildname = self.buildid+"_doc.f90"
            ## Tuple of temporary files scheduled for removal.
            self.temps = self.temps + (self.buildname, )                  
        elif self.stype == 'CCpp': # pragma: no cover
            os.environ['dox_ccpp'] = 'YES'                          
            self.buildname = self.buildid+"_doc.cpp"
            self.temps = self.temps + (self.buildname, )                   
        else:
            temp = []; delimn = " "
            self.buildname = ''
            temp.append(self.srcs)
            os.environ['dox_pyjava'] = 'YES' 
            paths = list(Utility.ArbitraryFlattening(temp))
            
            # Remove empty and/or unnecessary paths from joined input string
            for y in paths:
                for x in os.listdir(y):
                    if x.endswith((".java", ".py")):
                        if not any([z == "__init__.py" for z in os.listdir(y)]) and x.endswith((".py")): # pragma: no cover
                            # Automatic documentation of files requires regular packages, not pure folders. Temporarily add an
                            # __init__.py to every folder containing Python scripts. Removed after completion.
                            open(os.path.join(y,"__init__.py"), 'a+').close()
                            # Add absolute path to temporary files scheduled for removal.
                            self.temps = self.temps + (os.path.join(y,"__init__.py"),)
                            continue
                        break
                else:
                    paths.remove(y)
                    if y in [os.path.dirname(k) for k in list(filter(os.path.isfile, self.temps))]: # pragma: no cover
                        paths.append(y)
         
            self.buildname = delimn.join(paths)     
            
            for x in list(filter(os.path.isfile, self.temps)):
                while True: # pragma: no cover
                    try:
                        path = os.path.dirname(x)
                        if os.path.exists(os.path.join(path,"__init__.py")):
                            x = path
                        else:
                            break
                    except:
                        break
            
            list(filter(os.path.isfile, self.temps))
            
            # Remove all directories from temporary array. We only seek files.
            self.temps = tuple(filter(os.path.isfile, self.temps))
            
            # Check if non-directories exists
            if list(self.temps): # pragma: no cover
                # Schedule them for removal
                rev_command = [remove] + list(self.temps)         
                self.postcmd = delimn.join(rev_command)

        # Initial environment variables (can be updated through the command line)
        os.environ['dox_input'] = self.buildname
        os.environ["dox_version"] = str(1.0)
        os.environ['dox_images'] = Path2Config      
        os.environ['dox_footer'] = os.path.join(Path2Config,"stm_doc_footer.html")        
        os.environ['dox_logo'] = os.path.join(Path2Config,"stm_logo.png")           
        os.environ['dox_pyfilter'] = (sys.executable+" "+os.path.join(Path2Config,"stm_pyfilter.py")) if Utility.GetPlatform() in ["windows","nt"] else (os.path.join(Path2Config,"stm_pyfilter.py"))

        # Proper handling of Debian / macOS with Doxygen (latest version)
        if not sys.executable in os.getenv("PATH", "") and not Utility.GetPlatform() in ["windows","nt"]: 
            os.environ['PATH'] = os.pathsep.join([sys.executable,os.getenv("PATH","")]);
            os.chmod(os.path.join(Path2Config,"stm_pyfilter.py"), stat.S_IWOTH); os.chmod(os.path.join(Path2Config,"stm_pyfilter.py"), stat.S_IXOTH)
        
        # Set default color scheme.
        if not all([os.getenv(x) for x in ("dox_hue","dox_sat","dox_gamma")]): 
            from PyXMake.Build.config.stm_color import DLRBlue as dox_color #@UnresolvedImport
            os.environ['dox_hue'], os.environ['dox_sat'], os.environ['dox_gamma'] = [str(int(round(x))) for x in np.multiply([360.,100.,100],
                                                                                                                                                                   np.array(colorsys.rgb_to_hsv(*(value/255 for value in 
                                                                                                                                                                   ImageColor.getcolor(dox_color,"RGB")))))]
        
        # Remove MKL from default command line
        ## Blank version of list containing library directories without initially specifying MKL.       
        self.incdirs = []
        self.libdirs = []      
        pass

    def Settings(self, brief, header, outdir='', **kwargs):
        """
        Define environment variables for the default configuration file.
        """
        # Overwrite output directory        
        if outdir != '':
            ## Output directory of current job. Defaults to current workspace if not given.
            self.outdir = outdir # pragma: no cover
        
        # Set environment variables for configuration script
        os.environ['dox_brief'] = brief                    
        os.environ['dox_header'] = header             
        os.environ['dox_outdir'] = self.outdir

        # Update optional customization settings
        if kwargs.get("version",None): os.environ['dox_version'] = kwargs.get("version")
        if kwargs.get("icon",None): 
            # Get the user defined file
            user_defined_image = kwargs.get("icon")
            # Create a new temporary file and fetch its file extension
            temporary_optimized_image =os.path.join(tempfile.mkdtemp(),"doxygen_icon%s" % os.path.splitext(user_defined_image)[-1])            
            # Fetch optimal base width from default icon or refer to user input
            base_width = kwargs.get("base_width",Image.open(os.path.join(os.getenv("dox_images"),"stm_logo.png")).size[0]) #@UndefinedVariable
            # Resize the image to its optimal proportions            
            icon = Utility.GetResizedImage(user_defined_image, base_width)
            # Save the new image
            icon.save(temporary_optimized_image, optimize=True, quality=95, **icon.info)
            # Only add a custom logo as icon 
            os.environ["dox_logo"], os.environ["dox_icon"] = (temporary_optimized_image,)*2
        # Set color scheme in HUE (HSV)
        if kwargs.get("color",""): # pragma: no cover
            # Only modify color scheme if a hex color was explicitly given
            os.environ['dox_hue'], os.environ['dox_sat'], os.environ['dox_gamma'] = [str(x) for x in np.multiply([360.,100.,100],
                                                                                                                                                                   np.array(colorsys.rgb_to_hsv(*(value/255 for value in 
                                                                                                                                                                   ImageColor.getcolor(kwargs.get("color"),"RGB")))))]               
        pass
    
    @classmethod
    def parse(cls, **kwargs): # pragma: no cover
        """
        Execute the current class as a CLI command.
        """
        # Import its main from VTL  
        from PyXMake.VTL import doxygen
        # Evaluate current command line
        command = kwargs.get("command",sys.argv)
        # Process all known arguments
        parser = argparse.ArgumentParser(description='CLI wrapper options for  Doxygen with more sensible default settings.')
        parser.add_argument('name', type=str, nargs=1, help="Name of the project")
        parser.add_argument('source', type=str, nargs=1, help="Absolute path to the source file directory.")
        parser.add_argument('-t', '--title', nargs='+', default=[], help="Header used in the documentation. If not given, defaults are created from the project name.")
        parser.add_argument('-f', '--files', nargs='+', default=[], help="Source file or list of all source files used in the creation of the documentation.")
        parser.add_argument('-s', '--scratch', nargs='+', default=[], help="Default scratch folder for Doxygen. Defaults to current workspace.")
        parser.add_argument("-o","--output", type=str, nargs=1, help="Absolute path to output directory. Defaults to current project folder.")
        parser.add_argument("-c","--config", type=str, nargs=1, help="Absolute path to user-supplied Doxygen configuration file. Can be left blank.")
        parser.add_argument('-l', '--logo', nargs='+', default=[], help="Top level logo used by Doxygen. Defaults to structural mechanics department logo.")
        parser.add_argument("-v","--verbosity", type=str, nargs=1, help="Level of verbosity. Defaults to 0 - meaning no output. Max value is 2.")
        parser.add_argument("-ta","--tag", type=str, nargs=1, help="Documentation version tag. Defaults to 1.0 if not set.")
        parser.add_argument("-fo","--format", type=str, nargs=1, help="Toggle between Java, Fortran and Python code base. Defaults to Fortran.")
        parser.add_argument("-fi","--filter", type=str, nargs=1, help="JSON configuration string for this operation")
        parser.add_argument('--icon', type=str, nargs=1, help=argparse.SUPPRESS)
        # Check all options or run unit tests in default mode   
        try:
            # Check CLI options
            _ = command[1]
            args, _ = parser.parse_known_args(command[1:])
            # Project name is mandatory
            project = args.name[0]; 
            # Specification of source directory is mandatory
            source = args.source[0] ; 
            # Optional non-default project title
            try: 
                _ = args.title[0]
                header = [Utility.ArbitraryEval(x) for x in args.title]
            except: header = [project.title(),"%s Developer Guide" % project.title()]
            # Optional non-default output directory
            try: output = args.output[0]
            except: output = os.path.abspath(os.getcwd())
            # Optional non-default scratch directory
            try: scratch = args.scratch[0]
            except: scratch = os.path.abspath(os.getcwd())
            # Optional code format style definition. Defaults to Python.
            try: fformat = args.format[0]
            except: fformat = "Fortran"
            # Optional source code filter option
            scfilter = {"exclude": True, "startswith":(".","__")}
            # Sanitize user input
            try: scfilter.update(json.loads(Utility.ArbitraryEval(args.filter[0])))
            except: pass
            # Optional non-default source files.
            try:
                _ = args.files[0]
                files = [Utility.ArbitraryEval(x) for x in args.files]
            except: 
                # Parse files directly if format equals Fortran source. Use folder structure in all other cases.
                index = 0 if fformat != "Fortran" else -1
                files = [x[index] for x in Utility.PathWalk(os.path.abspath(source), **scfilter)]
            # Non default user-supplied configuration file. Defaults to internal configuration file
            try: config = args.config[0]; 
            except: config = os.path.join(Path2Config,"stm_doc_config")
            # Optional non-default icon
            try: icon = args.logo[0]
            except: icon = getattr(args, "icon", [None] )
            if icon: icon = os.path.abspath(next(iter(icon)))
            # Optional version tag used for the documentation. Defaults to 1.0
            try: tag = args.tag[0]
            except: tag = str(1.0)
            # Verbose output level. Defaults to ZERO - meaning no output. Can be increased to 2.
            try: verbosity = int(args.verbosity[0])
            except: verbosity = 0
            # Create a dictionary combining all settings
            settings = {"title":header, 
                                "files":files, 
                                "ftype":fformat, "config":config, 
                                "source":source, "output":output, "scratch":scratch,
                                "verbosity":verbosity,
                                "icon":icon,"version":tag}
        # Use an exception to allow help message to be printed.
        except Exception as _:
            # Local imports. These are only meaningful while executing an unit test
            from PyXMake import VTL
            from PyCODAC.Tools.Utility import GetPyCODACPath
            # Build all supported features
            if AllowDefaultMakeOption:     
                # Build documentation of PyXMake
                BuildID = "pyx_core"
                doxygen(BuildID, ["PyXMake", "PyXMake Developer Guide"], 
                                       [x[0] for x in Utility.PathWalk(PyXMakePath, startswith=(".","__"), contains=("doc","bin","config"), endswith=("make","scratch","examples"))], "Python", 
                                       output=os.path.join(PyXMakePath,"VTL","doc","pyx_core"))  
                # Build documentation of PyCODAC    
                BuildID = "pyc_core"
                doxygen(BuildID, ["PyCODAC", "PyCODAC Developer Guide"], 
                                       [x[0] for x in Utility.PathWalk(GetPyCODACPath(), startswith=(".","__"), 
                                       contains=("DELiS","Smetana","PyXMake","external","doc","cmd","bin","include","lib","config","fetch"), 
                                       endswith=("VTL","make","scratch","examples","src","config","solver"))], "Python", 
                                       output=os.path.join(GetPyCODACPath(),"VTL","doc","pyc_core"))                 
                # Build documentation of SubBuckling
                BuildID = "mcd_subbuck"
                doxygen(BuildID, ["SubBuck", "SubLaminate Buckling Developer Guide"], 
                                       [x[0] for x in Utility.PathWalk(os.path.join(Utility.AsDrive("D"),"03_Workspaces","01_Eclipse","mcd_subbuckling"))], "Java",
                                       output=os.path.join(GetPyCODACPath(),"VTL","doc","mcd_subbuckling"))         
                # Build documentation of Mapper
                BuildID = "mcd_mapper"
                doxygen(BuildID, ["Mapper", "Damage Mapping Developer Guide"], 
                                       [x[0] for x in Utility.PathWalk(os.path.join(Utility.AsDrive("D"),"03_Workspaces","01_Eclipse","mcd_mapper"))], "Java",
                                       output=os.path.join(GetPyCODACPath(),"VTL","doc","mcd_mapper"))         
                # Build documentation of BoxBeam    
                BuildID = "box_core" 
                doxygen(BuildID, ["BoxBeam", "BoxBeam Developer Guide"], VTL.GetSourceCode(1),
                                       source=os.path.join(os.path.join(GetPyCODACPath(),"Core"),"external","boxbeam"), 
                                       output=os.path.join(GetPyCODACPath(),"Plugin","BoxBeam","VTL","doc","box_core"))   
                # Build documentation of MCODAC (Default settings
                BuildID = 'mcd_core'
                doxygen(BuildID) 
        else:
            # Execute CLI command
            doxygen(project, **settings)
        pass
    
## @class PyXMake.Build.Make.Latex
# Base class for all Latex build events. Inherited from Make.          
class Latex(Make):
    """
    Inherited class to automatically build a documentation using Latex
    """    
    ## Non-default cross-version class property definition.
    # Protects a class property from unrestricted access
    class __property(object):
        def __init__(self, getter): self.getter= getter
        def __get__(self, instance, owner): return self.getter(owner)
        
    # Definition of class attribute
    base_url = os.getenv("pyx_overleaf_url","https://overleaf.fa-services.intra.dlr.de")
    
    # Adopt secret name in dependence of being distributed in a Docker container or not.
    secret = "pyc_overleaf_secret" if os.getenv("pyc_overleaf_secret","") else "pyx_overleaf_secret"
    
    # Fail gracefully
    try: secret = open(os.getenv(secret,os.path.join(os.path.expanduser("~"),"Keys","Keepass","fa_overleaf_access")),"r").read()
    except: auth = {}
    
    def __init__(self, *args, **kwargs):
        """
        Initialization of Latex class object.
        """
        # Allow for initialization w/o any source data
        if len(args) < 2: args += ("",)
        # Create super class from base class
        super(Latex, self).__init__(*args,**kwargs)
        ## String identifier of current instance.        
        self.MakeObjectKind = 'Latex'
        
        # Validate third party dependencies
        from six import exec_
        from PyXMake.Build import __install__  #@UnresolvedImport
        from sphinx import package_dir
        
        # Check settings here for older python version compatibility
        silent_install = kwargs.get("silent_install",False)
        
        ## Silently install all dependencies on-the-fly. Defaults to False, meaning Latex must be present in Path 
        # or an external API service (like Overleaf) must be used.
        if silent_install: exec_(open(__install__.__file__).read(),{"__name__": "__main__", "__file__":__install__.__file__})
        
        # Build script for Latex documentation
        os.environ["PATH"] += os.pathsep + os.pathsep.join([os.path.join(os.path.dirname(sys.executable),"Scripts")])      
        # Add additional search paths to Latex default search paths
        os.environ["TEXINPUTS"] = os.getenv("TEXINPUTS", "")
        # Add custom SPHINX styles to Latex search path
        os.environ["TEXINPUTS"] += os.pathsep + os.pathsep.join([os.path.join(package_dir,"texinputs"),os.path.join(PyXMakePath,"Build","config")])
        
        # Immutable settings for Latex object        
        ## Path to Latex executable. Set using environment variable
        self.path2exe = ""
        ## Executable of Latex.
        self.exe = 'texify.exe'
        
        ## Set default source and output directories for Latex build objects.
        # By default, both are set to the same folder containing the main source file.
        if os.path.exists(self.srcs[0]):
            self.srcdir = os.path.dirname(os.path.abspath(self.srcs[0]))
            self.outdir = os.path.dirname(os.path.abspath(self.srcs[0]))
            
        ## Set user-defined secret value, if given
        if kwargs.get("secret", None): Latex.secret = kwargs.get("secret")
        
        # Remove MKL from default command line
        ## Blank version of list containing library directories without initially specifying MKL.       
        self.incdirs = []
        self.libdirs = []
    
    @__property
    def auth(self): 
        """
        API access token defined as a protected class property for backwards compatibility.
        Works for both Python 2 and 3. Only meaningful when a remote Latex instance shall be called.
        """
        if not getattr(self, "_auth",{}):
            try: 
                self._auth = {} ; 
                result = self.session(*base64.b64decode(self.secret).decode('utf-8').split(":",1), base_url=self.base_url, use_cache=False) ; 
                self._auth = result[-1] ; 
            except: pass
        return self._auth
    
    @classmethod
    def Settings(cls, **kwargs): # pragma: no cover
        """
        Define environment variables for the default configuration file.
        """        
        # Set environment variables for configuration script
        os.environ["TEXINPUTS"] += os.pathsep + os.pathsep.join([str(value) for value in kwargs.values()])                                 
        pass
    
    @classmethod
    def session(cls, *args, **kwargs):
        """
        Create all required session tokens for an active Overleaf instance.
        """
        status_code = 500; result = {}
        # Use cached credentials. Defaults to True.
        if kwargs.get("use_cache",True): return [200,copy.deepcopy(getattr(cls, "auth",{}))]
        # Procedure
        try: 
            from bs4 import BeautifulSoup
            # Create a new session
            session = requests.Session()
            email, password = args
            # Obtain login URL. Fail safe in case of empty input string.
            login_url = "{}/login".format(kwargs.get("base_url", cls.base_url) or cls.base_url)
            # Get secret token
            r = session.get(login_url); csrf = BeautifulSoup(r.text, 'html.parser').find('input', { 'name' : '_csrf' })['value']
            r = session.post(login_url, { '_csrf' : csrf , 'email' : email , 'password' : password })
            try: # pragma: no cover
                r.json(); status_code = 403; 
                result = "The given credentials could not be verified."
                # Interrupt the process
                return [status_code, result]
            # Everything worked fine
            except: pass
            # Get valid CSRF Token for further commands
            r = session.get(login_url); csrf = BeautifulSoup(r.text, 'html.parser').find('input', { 'name' : '_csrf' })['value']
            # Fetch valid session token from the response header
            if r.status_code == 200: 
                status_code = r.status_code; result = {"Cookie":r.headers.pop("Set-Cookie").split(ntpath.pathsep)[0],"_csrf":csrf}
            # Check if an error has occurred
            r.raise_for_status()
        # Error handler in top-level function
        except: pass
        # In all cases. Return something
        return [status_code, result]
    
    @classmethod
    def show(cls,ProjectID, *args, **kwargs):
        """
        Show all build files from an Overleaf project remotely given its ID. 
        
        @note: Rebuilds the project in the process.
        """
        # Verify credentials
        code, result = cls.session(*args, **kwargs)
        if code != 200: return [code, result]
        # Update header
        header = result; header.update({'Content-Type':'application/json;charset=utf-8' })
        # Obtain project URL. Fail safe in case of empty input string.
        project_url = "{}/project".format(kwargs.get("base_url", cls.base_url) or cls.base_url)
        # Always build from scratch
        requests.delete(posixpath.join(project_url,ProjectID,"output"),headers={"X-Csrf-Token" if k == "_csrf" else k:v for k,v in result.items()})
        # Rebuild the project. Compiles everything.
        r = requests.post(posixpath.join(project_url,ProjectID,"compile"),params={"auto_compile":True}, headers=header, 
              data=json.dumps({"check":"silent","incrementalCompilesEnabled":True,"_csrf":header.pop("_csrf")}))
        # Return the output file dictionary. Defaults to an empty dictionary in case something went wrong. 
        if r.status_code == 200: return r.json()["outputFiles"]
        else: return {} # pragma: no cover
        
    @classmethod
    def rename(cls, ProjectID, ProjectName, *args, **kwargs):
        """
        Rename an Overleaf project remotely given its ID.
        """
        # Verify credentials
        code, result = cls.session(*args, **kwargs)
        if code != 200: return [code, result]
        # Update header
        header = result; header.update({'Content-Type':'application/json;charset=utf-8' })
        # Fetch CSRF token from session result
        data = {"_csrf":result.pop("_csrf")}
        data.update({"newProjectName":str(ProjectName)})
        # Obtain project URL. Fail safe in case of empty input string.
        project_url = "{}/project".format(kwargs.get("base_url", cls.base_url) or cls.base_url)
        # Rebuild the project. Compiles everything.
        r = requests.post(posixpath.join(project_url,ProjectID,"rename"), headers=result, data=json.dumps(data))
        # Return the output file dictionary. Defaults to an empty dictionary in case something went wrong. 
        if r.status_code == 200: return {"success":True,"message":r.text}
        else: return {} # pragma: no cover
        
    @classmethod
    def upload(cls,archive, *args, **kwargs):
        """
        Upload a given archive to an active Overleaf instance creating a new project.
        """
        # Default value
        response = {}
        # Verify credentials
        code, result = cls.session(*args, **kwargs)
        if code != 200: return [code, result]
        # Obtain project upload URL. Fail safe in case of empty input string.
        upload_url = "{}/project/new/upload".format(kwargs.get("base_url", cls.base_url) or cls.base_url)
        filename = os.path.basename(archive)
        mime = "application/zip"
        files = {"qqfile": (filename, open(archive, "rb"), mime), "name": (None, filename)}
        params = {
            "_csrf":result.pop("_csrf"),
            "qquid": str(uuid.uuid4()),
            "qqfilename": filename,
            "qqtotalfilesize": os.path.getsize(archive),
        }
        # Execute the request
        r = requests.post(upload_url,params=params, files=files, headers=result)
        try: 
            r.raise_for_status(); response = r.json()
        except Exception: pass
        # Check if JSON is valid.
        if not "success" in response: raise Exception("Uploading of %s failed." % archive )
        # Rename the newly created project
        cls.rename(r.json()["project_id"], str(filename.split(".")[0]).title(), *args, **kwargs)
        # Return response
        return response
        
    @classmethod
    def download(cls, ProjectID, *args, **kwargs):
        """
        Download the complete archive or final pdf from an Overleaf project given its ID.
        """
        # Verify credentials
        code, result = cls.session(*args, **kwargs)
        if code != 200: return [code, result]
        # Default download path
        endpoint = posixpath.join("download","zip")
        # Download compiled PDF file instead
        if kwargs.get("output_format","zip") in ["pdf"]:
            # Verify that the source compiles with a new request
            endpoint = [x["url"] for x in cls.show(ProjectID, *args, **kwargs) 
                                 if str(x["url"]).endswith("output.pdf")][0]
            ## Download in Overleaf has changed. 
            # Refer to new download path if available but still support the deprecated alternative
            endpoint = next(iter([ posixpath.join("user",endpoint.split("user")[-1].replace(posixpath.sep,"",1))
                         if "user" in endpoint.split(posixpath.sep)[:4] 
                         else posixpath.join("build",endpoint.split("build")[-1].replace(posixpath.sep,"",1)) ] ))
        # Obtain project URL. Fail safe in case of empty input string.
        project_url = "{}/project".format(kwargs.get("base_url", cls.base_url) or cls.base_url)
        # Rebuild the project. Compiles everything.
        r = requests.get(posixpath.join(project_url,ProjectID,endpoint), headers=result , stream=True)
        # Create the output file name
        output = os.path.abspath(".".join([os.path.join(os.getcwd(),ProjectID),endpoint[-3:]]))
        # Download the binary blob
        with open(output, "wb") as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk: f.write(chunk)    
        # Return the output path
        return output
    
    @classmethod
    def delete(cls,ProjectID, *args, **kwargs):
        """
        Delete an Overleaf project given its ID.
        """
        # Check user settings. Defaults to False
        forever = kwargs.get("forever",False)
        # Verify credentials
        code, result = cls.session(*args, **kwargs)
        if code != 200: return [code, result]
        # Update header
        header = result; header.update({'Content-Type':'application/json;charset=utf-8' })
        # Obtain project URL. Fail safe in case of empty input string.
        project_url = "{}/project".format(kwargs.get("base_url", cls.base_url) or cls.base_url)
        # Execute the request
        r = requests.delete(posixpath.join(project_url,ProjectID), data=json.dumps({"forever": forever, "_csrf":header.pop("_csrf")}), headers=header)
        r.raise_for_status()
        # Return response
        return {"success":True,"message":r.text}
    
    @classmethod
    def parse(cls, **kwargs): # pragma: no cover
        """
        Execute the current class as a CLI command.
        """
        # Import its main from VTL  
        from PyXMake.VTL import latex
        # Evaluate current command line
        command = kwargs.pop("command",sys.argv)
        # Process all known arguments
        parser = argparse.ArgumentParser(description="Compile a TeXfile using MikTeX or Overleaf with custom templates.")
        parser.add_argument('name', type=str, nargs=1, help="Name of the project")
        parser.add_argument('source', type=str, nargs=1, metavar="main.tex", help="Absolute path to the main source file. Must be either a Texfile or an archive.")
        parser.add_argument('-a', '--api', type=str, nargs=1, default="texworks", help="Additional files required for the process.")
        parser.add_argument('-i', '--include', nargs='+', default=[], help="Additional files required for the compilation process.")
        parser.add_argument("-v","--verbosity", type=str, nargs=1, help="Level of verbosity. Defaults to 0 - meaning no output. Max value is 2.")
        # Check all options or run unit tests in default mode   
        try:
            # Check CLI options
            _ = command[1]
            args, _ = parser.parse_known_args(command[1:])
            # Project name is mandatory
            project = args.name[0];
            # Specification of source directory is mandatory
            source = args.source[0] ; 
            # Optional non-default compilation API
            try: config = args.api[0]
            except: config = "texworks"
            # Optional non-default scratch directory
            try: scratch = args.scratch[0]
            except: scratch = os.path.abspath(os.getcwd())
            # Optional non-default definition of additional files
            try: 
                _ = args.include[0]
                # Collect all given paths. Get system independent format
                include = Utility.GetSanitizedDataFromCommand(args.include)
            # No extra files have been given
            except: include = []
            # Verbose output level. Defaults to ZERO - meaning no output. Can be increased to 2.
            try: verbosity = int(args.verbosity[0])
            except: verbosity = 2
            # Create a dictionary combining all settings
            settings = {"file":source, "API":config, "include":include, "scratch":scratch, "verbosity": verbosity}
            
        # Use an exception to allow help message to be printed.
        except Exception as _:
            # Build all supported features
            if AllowDefaultMakeOption: 
                # Run default option in a temporary directory
                with Utility.TemporaryDirectory():
                    # Local import to make test work in a conda environment
                    import PyXMake as _ #@UnusedImport
                    # Use elsevier template for unit test
                    from urllib.request import urlretrieve
                    # Local variables
                    BuildID = "elsevier"
                    filename = "elsarticle.zip"
                    url = "https://mirrors.ctan.org/macros/latex/contrib/elsarticle.zip"
                    # Get a copy of keyword arguments
                    settings = copy.deepcopy(kwargs)
                    # Update test settings when CI specific environment variables can be found
                    if os.getenv("CI_USER","") and os.getenv("CI_PASSWORD",""):
                        # Create local variables in CI/CD tests
                        user = os.getenv("CI_USER"); password = os.getenv("CI_PASSWORD"); 
                        # Check if a password is given in base64 encryption. Take this into account before creating the secret.
                        if Utility.isBase64(password): password = base64.b64decode(password).decode("utf-8")
                        settings.update({"secret": Utility.GetDockerEncoding(user,password)})
                    # Down the template locally and run remote build process
                    urlretrieve(url, filename); latex(BuildID, filename, API="Overleaf", **settings)
        else:
            # Execute CLI command
            latex(project, **settings)
        pass
    
    def create(self, API="TeXworks", GUI=True, **kwargs):
        """
        Compile an existing project and/or start the graphical user interface.
        """
        command = []
        # Add all include directories to Latex environment variable
        os.environ["TEXINPUTS"] += os.pathsep + os.pathsep.join([str(include) for include in self.incdirs])
        ## Support both TeXWorks and Overleaf implementations
        # Use remote Overleaf implementation
        if API.lower() in ["overleaf"]:
            # Get Latex archive
            archive = os.path.abspath(self.srcs[0])
            # Operate fully on a temporary directory
            with Utility.ChangedWorkingDirectory(self.scrtdir): 
                # Copy file into local scratch folder
                shutil.copy(archive, os.getcwd())
                # Upload the archive
                result = self.upload(archive)
                try: 
                    # If successful, retrieve the project id
                    ProjectID = result["project_id"]
                    # Download the resulting PDF file
                    self.download(ProjectID, output_format="pdf")
                    # Rename the project to build id
                    self.rename(ProjectID, self.buildid)
                    # Delete the project if not explicitly requested otherwise.
                    if not kwargs.get("keep",False): self.delete(ProjectID)
                    # Get name of the result file
                    result_file = [x for x in os.listdir() if x.endswith(".pdf")][0]
                    shutil.copy(result_file,self.outdir)
                # Explicitly request all errors for logging
                except Exception as e: print(e.args())
            pass
        # Use local TeXworks distribution
        elif API.lower() in ["texworks"]: # pragma: no cover
            if os.path.exists(self.srcs[0]):
                command.append(self.srcs[0])
            # Open GUI or run command directly from command line    
            if GUI or not os.path.exists(self.srcs[0]):
                # Run GUI
                command.insert(0,"texworks.exe")
                subprocess.Popen(command, close_fds = True, **Make.Detach())
            else:
                with tempfile.TemporaryDirectory(dir=self.scrtdir) as temp:
                    # Set current directory to be the current directory
                    os.chdir(temp)
                    # Get name of output file
                    output = os.path.splitext(Utility.PathLeaf(command[-1]))[0] + ".pdf"
                    # Run command line
                    command[0:0] = ["texify.exe","--pdf","--tex-option=-shell-escape","--synctex=1","--clean"]
                    # Print output on-the-fly
                    Utility.Popen(command, self.verbose, collect=False)
                    # Copy output file into the output directory
                    shutil.copyfile(output, os.path.join(self.outdir,output))
                    # Wait until copying has been completed
                    os.chdir(self.scrtdir)
        # Raise unknown API error
        else: raise NotImplementedError
        pass
    
    @classmethod
    def __new(cls, ProjectName=None, *args, **kwargs): # pragma: no cover
        """
        Create a new project within the current session
        """
        # Check user settings. Defaults to False
        forever = kwargs.get("forever",False)
        # Verify credentials
        code, result = cls.session(*args, **kwargs)
        if code != 200: return [code, result]
        # Inherit BuildID from BuildID if given
        if not ProjectName: ProjectID = str(getattr(cls,"buildid",ProjectName))
        if not ProjectID: raise ValueError
        # Update header
        header = result; header.update({'Content-Type':'application/json;charset=utf-8' })
        # Obtain project URL. Fail safe in case of empty input string.
        project_url = "{}/project/new".format(kwargs.get("base_url", cls.base_url) or cls.base_url)
        # Create data segment
        data = {
            "_csrf": header.pop("_csrf"),
            "template": kwargs.get("template","template"),
            "projectName": ProjectID,
            "forever": forever,
        }
        # Execute the request
        r = requests.post(project_url, data=json.dumps(data), headers=header)
        r.raise_for_status()
        # Return response
        return {"success":True,"message":r.text,"response":r.json()}
    
    # Abstract method. Can be invoked as an instance or class method.
    new = Utility.AbstractMethod(__new.__func__)
    
## @class PyXMake.Build.Make.Coverage
# Base class for all Coverage build events. Inherited from Make.          
class Coverage(Make): # pragma: no cover
    """
    Inherited class to automatically build a coverage report using Coverage.
    """    
    def __init__(self, *args,**kwargs):
        """
        Initialization of coverage class object.
        """
        # Check if this class is used as a decorator.
        try: self.isDecorator = kwargs.pop("__as_decorator",any(line.startswith('@') for line in inspect.stack(context=2)[1].code_context))
        # Fail gracefully if context cannot be resolved.
        except TypeError: self.isDecorator = False
        # The current class is instantiated as a runner.
        if not self.isDecorator:
            super(Coverage, self).__init__(*args,**kwargs)
            ## String identifier of current instance.        
            self.MakeObjectKind = 'Coverage'
            # Reset all pats to avoid collision
            self.incdirs = []; self.libdirs = []
        else: 
            # Safe all arguments for later use.
            self.args = args
            self.kwargs = kwargs

    def __call__(self, fn):
        """
        Implement an executable variant if class is used as a decorator.
        """
        import functools
        # Only run part of the code if environment is a test setup
        isPytest = self.kwargs.pop("autorun", False) or self.show()
        # Create a function wrapper
        @functools.wraps(fn)
        def decorated(*args, **kwargs):
            """
            Execute this part with given *args and **kwargs and the underlying function
            """
            # Execute test if running as a test
            if isPytest and not getattr(decorated,"has_run",False):
                compare = self.kwargs.pop("result",None);
                # Where running in a test environment
                try: result = fn(*self.args, **self.kwargs)
                except Exception as e: raise e
                ## Check if result matches the given value
                # Only meaningful when a result has been provided
                if compare: assert result == compare
                # Only run each test only once.
                decorated.has_run = True
            # Always return its true statement
            result = fn(*args, **kwargs)
            # Return the result of the function
            return result
        # Execute part directly when a function is loaded. Only in a test setup
        if isPytest:
            try: decorated()
            except TypeError: pass
        # Only execute the test setup once
        if not hasattr(decorated, "has_run"): decorated.has_run = False
        return decorated

    @classmethod
    def show(cls):
        """
        Get a boolean value if this function is called within an active test environment
        """
        # Return the current root
        return str("pytest") in sys.modules or str("PYTEST_CURRENT_TEST") in os.environ
    
    @classmethod
    def add(cls,*args, **kwargs):
        """
        Provide a test case for the given method as a decorator.
        """
        kwargs.update({"__as_decorator":True})
        # Do not return decorated function as a class in bundled mode
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'): 
            def decorator(func): return func 
            return decorator
        # Return current class instance 
        else: return cls(*args,**kwargs)
    
    @classmethod
    def parse(cls, **kwargs): # pragma: no cover
        """
        Execute the current class as a CLI command.
        """
        # Import its main from VTL  
        from PyXMake.VTL import coverage
        # Evaluate current command line
        command = kwargs.get("command",sys.argv)
        # Process all known arguments
        parser = argparse.ArgumentParser(description='CLI wrapper options for  Coverage with more sensible default settings.')
        parser.add_argument('name', type=str, nargs=1, help="Name of the project")
        parser.add_argument('source', type=str, nargs=1, help="Absolute path to the source file directory.")
        parser.add_argument('-i', '--include', nargs='+', default=[], help="Additional files defining test cases required for test coverage.")
        parser.add_argument("-o","--output", type=str, nargs=1, help="Absolute path to output directory. Defaults to current project folder.")
        parser.add_argument("-e","--exclude", nargs='+', default=[], help="Full paths to be ignored from the coverage.")
        parser.add_argument("-v","--verbosity", type=str, nargs=1, help="Level of verbosity. Defaults to 0 - meaning no output. Max value is 2.")
        # Check all options or run unit tests in default mode   
        try:
            # Check CLI options
            _ = command[1]
            args, _ = parser.parse_known_args(command[1:])
            # Project name is mandatory
            project = args.name[0]; 
            # Specification of source directory is mandatory
            source = os.path.abspath(args.source[0]) ; 
            # Optional non-default definition of additional tests cases
            try: 
                _ = args.include[0]
                # Collect all given paths. Get system independent format
                include = Utility.GetSanitizedDataFromCommand(args.include)
            # No extra test cases have been given
            except: include = []
            # Optional non-default output directory
            try: output = args.output[0]
            except: output = os.path.abspath(os.getcwd())
            # Optional non-default exclude pattern
            try: 
                _ = args.exclude[0]
                # Collect all given paths. Get system independent format
                exclude = Utility.GetSanitizedDataFromCommand(args.exclude)
            except: exclude = []
            # Verbose output level. Defaults to ZERO - meaning no output. Can be increased to 2.
            try: verbosity = int(args.verbosity[0])
            except: verbosity = 0
            # Verify that the given path is actually a package. Get the first entry 
            source = [r for r, _, f in Utility.PathWalk(source) if any(x in ["__init__.py"] for x in f)][0]
            # Create a dictionary combining all settings
            settings = {"source":source, "output":output, "include":include,"exclude_paths":exclude,"verbosity":verbosity}
            
        # Use an exception to allow help message to be printed.
        except Exception as _: 
            # Run default test coverage of all integrated projects.
            if AllowDefaultMakeOption:               
                # Run test coverage for PyXMake
                BuildID = "PyXMake"
                coverage(BuildID)    
        else:
            # Execute CLI command
            coverage(project, **settings)
        pass
        
    def Build(self, command=["--cov-fail-under=10","--cov-report=term-missing","--cov-report=html","--cov-report=xml","--junit-xml=junit.xml", "-W ignore::pytest.PytestAssertRewriteWarning"], **kwargs):
        """
        Assemble command strings for the main build event.
        """
        delimn = " "
        # Fetch additional make
        self.makecmd = command
        if isinstance(self.makecmd,str): self.makecmd = self.makecmd.split(delimn)
        pass
        
    def create(self, **kwargs):
        """
        Execute make command
        """
        delimn = "_"
        # Copy the current command line
        sys_arg_recovery = copy.deepcopy(sys.argv); 
        # Remove all trailing entries to avoid parsing them down.
        try: sys.argv[1:] = []
        except IndexError: pass
        # Copy the current system path
        sys_path_recovery = copy.deepcopy(sys.path)
        # Remote VTL directory from the overall system path to remove all shims.
        _ = [ sys.path.pop(i) for i, x in enumerate(sys.path) if x.endswith("VTL") ]
        # Check if dependencies can be resolved
        try: import pytest_cov as _ #@UnusedImport
        except: raise ImportError
        # Local imports
        import pytest
        
        # Modify local VTL scratch directory
        from .. import PyXMakePath #@UnusedImport @Reimport
        
        # Create make command if not already exists
        if not hasattr(self, "makecmd"): self.Build(**kwargs)
        
        # Set default level of verbosity. Defaults to 1
        self.verbose = kwargs.get("verbosity",1)
        
        # Assemble make command
        command =self.makecmd; command.extend(["--cov=%s" % path for path in self.srcs])
        
        # A ordered list of all supported configuration file formats
        config = kwargs.get("config",None)
        configfiles = ["pytest.ini","pyproject.toml","tox.ini","setup.cfg"]
        
        # Check if a configuration file exists within the current directory
        if any(x in os.listdir(os.getcwd()) for x in configfiles) and not config:
            # Get the file
            for i, x in enumerate(configfiles): 
                if os.path.exists(x): break
            # Overwrite configuration variable
            config = os.path.abspath(os.path.join(os.getcwd(),configfiles[i]))
            
        # Default test directory
        test_directory = "tests"

        # Operate fully in a temporary directory and deactivate user scratch space
        with Utility.TemporaryDirectory(), Utility.TemporaryEnvironment():
            os.mkdir(test_directory);
            # Fetch additional files
            [shutil.copy(x,os.path.join(os.getcwd(),test_directory,Utility.PathLeaf(x))) for x in self.incdirs if os.path.isfile(x)]
            # Create a test for each file honoring __main__
            for file in os.listdir(os.path.join(os.getcwd(),test_directory)):
                with open(os.path.join(test_directory,delimn.join(["test",Utility.PathLeaf(file)])),"w") as f:
                    f.write("import runpy" +"\n")
                    f.write('def test_script():'+"\n")
                    f.write("    try: runpy.run_path('%s', run_name='__main__')" % str(os.path.join(test_directory,file)).replace(ntpath.sep,ntpath.sep*2) +"\n")
                    f.write("    except SystemExit as exception: exitcode = exception.code" +"\n")
                    f.write("    else: exitcode = 0" +"\n")
            # Copy all external tests
            [shutil.copy(os.path.join(self.srcdir,x),os.path.join(os.getcwd(),test_directory)) for x in os.listdir(self.srcdir) 
                if os.path.isfile(os.path.join(self.srcdir,x)) and x.startswith("test_")]
            # Create a default import check
            for path in self.srcs:
                with open(os.path.join(test_directory,delimn.join(["test",Utility.PathLeaf(os.path.dirname(path)),".py"])),"w") as f:
                    f.write("import os; import pkgutil;"+"\n")
                    f.write('os.environ.update(%s)' % str(os.environ.copy()) +"\n")
                    f.write('__all__ = [] ; __path__ = ["%s"];' % os.path.dirname(path).replace(ntpath.sep,ntpath.sep*2) +"\n")
                    f.write('def test_import():'+"\n")
                    f.write('    for loader, module_name, is_pkg in pkgutil.walk_packages(__path__):'+"\n")
                    f.write('         __all__.append(module_name); '+"\n")
                    f.write('         _module = loader.find_module(module_name).load_module(module_name);'+"\n")
                    f.write('         globals()[module_name] = _module'+"\n")

            ## Always create a coverage setup file to prevent error during coverage collection
            with open(".coveragerc","w") as f:
                f.write("[run]"+"\n"); 
                # Remove given paths. Defaults to an empty list
                if kwargs.get("exclude_paths",[]): f.write("omit = "+"\n"); 
                for x in kwargs.get("exclude_paths",[]): 
                    # Update omit settings in dependence of the given path
                    if os.path.isfile(x): path = str(x)
                    else: path = str(x) + os.path.sep + "*"
                    # Exclude all paths explicitly
                    f.write("    *%s" % path +"\n");
                # Add default code exclude pattern
                f.write("[report]"+"\n"); 
                f.write("exclude_also ="+"\n"); 
                f.write("    def __repr__"+"\n"); 
                f.write("    if self.debug:"+"\n"); 
                f.write("    if settings.DEBUG"+"\n"); 
                f.write("    raise AssertionError"+"\n"); 
                f.write("    raise NotImplementedError"+"\n"); 
                f.write("    if 0:"+"\n");
                f.write("    except"+"\n"); 
                f.write("    if __name__ == .__main__.:"+"\n"); 
                f.write("    if TYPE_CHECKING:"+"\n"); 
                f.write("    class .*\bProtocol\):"+"\n"); 
                f.write("    @(abc\.)?abstractmethod"+"\n");
            ## Check whether a configuration file has been given
            # If that is the case, copy it into the current temporary working directory, bypassing root
            # as both statements are mutually exclusive
            if config: shutil.copy(config, os.path.abspath(os.getcwd()))
            # Explicit definition of the root directory
            else: command.extend(["--rootdir=%s" % os.path.join(os.getcwd())])
            # Modify default settings path
            command.extend(["--cov-config=.coveragerc"])
            # Change default import mode
            command.extend(["--import-mode=importlib"])
            # Explicit definition of the test directory. Everything else is excluded.
            command.extend(['--override-ini="testpaths=%s"' % str(test_directory)])
            # Print all test cases and passes in a detailed manner
            if self.verbose >=1: command.extend(['--verbose'])
            if self.verbose >=2: command.extend(['-rA'])
            # Add the created test folder to the final command
            command.extend([os.path.join(os.getcwd(),test_directory)]); pytest.main(command)
            # Move all results to the output directory
            result = [x for x in os.listdir(os.getcwd()) if x.startswith(("coverage", "htmlcov", "junit",))]
            # Copy all files and folders to the output directory
            for x in result:
                # Remove any preexisting folders. Folders are recreated in the process.
                if os.path.isdir(x):  
                    try: shutil.rmtree(os.path.join(self.outdir,x)); 
                    except: pass
                    finally: shutil.copytree(x,os.path.join(self.outdir,x));
                    # Copy data
                else: shutil.copy(x, os.path.join(self.outdir,x))
        # Recover the initial command
        sys.argv = sys_arg_recovery
        # Recover the old system path.
        sys.path = sys_path_recovery
        pass
    
## @class PyXMake.Build.Make.Sphinx
# Base class for all Sphinx build events. Inherited from Make.          
class Sphinx(Make):
    """
    Inherited class to automatically build a documentation using Sphinx.
    """    
    def __init__(self, *args,**kwargs):
        """
        Initialization of sphinx class object.
        """                 
        super(Sphinx, self).__init__(*args,**kwargs)
        ## String identifier of current instance.        
        self.MakeObjectKind = 'Sphinx'
        
        # Validate third party dependencies
        from six import exec_
        from PyXMake.Build import __install__  #@UnresolvedImport
        exec_(open(__install__.__file__).read(),{"__name__": "__main__", "__file__":__install__.__file__})
        
        # Build script for Sphinx documentation
        os.environ["PATH"] += os.pathsep + os.pathsep.join([os.path.join(os.path.dirname(sys.executable),"Scripts")])
        
        # Immutable settings for Sphinx object        
        ## Path to Sphinx executable.
        self.path2exe = os.path.join(os.path.dirname(sys.executable),"Scripts")
        ## Executable of Sphinx.
        self.exe = 'sphinx-build.exe'
        ## Ordered dictionary containing all available options
        self.BuildOption = OrderedDict()
        
        # Project name from BuildID
        os.environ["sphinx_project"] = str(self.buildid)
        
        # Name of index file (master document).
        os.environ["sphinx_master"] = str(self.srcs[0])
        
        # Default color scheme
        from PyXMake.Build.config.stm_color import DLRBlue as sphinx_color #@UnresolvedImport
        os.environ["sphinx_color"] = sphinx_color
        
        # Remove MKL from default command line
        ## Blank version of list containing library directories without initially specifying MKL.       
        self.incdirs = []
        self.libdirs = []      
        pass

    def Settings(self, **kwargs): # pragma: no cover
        """
        Define environment variables for the default configuration file.
        """        
        delimn = "_"
        # Set environment variables for configuration script
        for key, value in kwargs.items():
            os.environ[delimn.join(["sphinx",str(key)])] = str(value)                                       
        pass
    
    @classmethod
    def parse(cls, **kwargs): # pragma: no cover
        """
        Execute the current class as a CLI command.
        """
        # Import its main from VTL  
        from PyXMake.VTL import sphinx
        # Evaluate current command line
        command = kwargs.get("command",sys.argv)
        # Process all known arguments
        parser = argparse.ArgumentParser(description='CLI wrapper options for  Sphinx with more sensible default settings.')
        parser.add_argument('name', type=str, nargs=1, help="Name of the project")
        parser.add_argument('source', type=str, nargs=1, help="Absolute path to the source file directory.")
        parser.add_argument('-f', '--file', nargs='+', default=[], help="Top level input file used in the creation of the documentation.")
        parser.add_argument('-l', '--logo', nargs='+', default=[], help="Top level logo in SVG format.")
        parser.add_argument('-i', '--include', nargs='+', default=[], help="Additional files defining test cases required for test coverage.")
        parser.add_argument('-s', '--scratch', nargs='+', default=[], help="Default scratch folder for Sphinx. Defaults to current workspace.")
        parser.add_argument("-o","--output", type=str, nargs=1, help="Absolute path to output directory. Defaults to current project folder.")
        parser.add_argument('-t', '--theme', type=str, nargs=1, help="An installed Sphinx theme. Defaults to 'Read the docs' theme.")
        parser.add_argument("-v","--verbosity", type=str, nargs=1, help="Level of verbosity. Defaults to 0 - meaning no output. Max value is 2.")
        parser.add_argument('--icon', type=str, nargs=1, help=argparse.SUPPRESS)
        # Check all options or run unit tests in default mode
        try:
            # Check CLI options
            _ = command[1]
            args, _ = parser.parse_known_args(command[1:])
            # Project name is mandatory
            project = Utility.GetSanitizedDataFromCommand(args.name, is_path=False)[0]
            ## Specification of main input file.
            mainfile = args.file[0]; 
            # Specification of source directory is mandatory
            source = os.path.abspath(args.source[0]) ; 
            # Optional non-default definition of additional tests cases
            try: 
                _ = args.include[0]
                # Collect all given paths. Get system independent format
                include = Utility.GetSanitizedDataFromCommand(args.include)
            # No extra test cases have been given
            except: include = []
            # Optional non-default output directory
            try: output = args.output[0]
            except: output = os.path.abspath(os.getcwd())
            # Optional non-default scratch directory
            try: scratch = args.scratch[0]
            except: scratch = os.path.abspath(os.getcwd())
            # Optional non-default icon
            try: icon = args.logo[0]
            except: icon = getattr(args, "icon", [None] )
            if icon: icon = os.path.abspath(next(iter(icon)))
            # Optional non-default theme
            try: theme = args.theme[0]
            except: theme = None
            # Verbose output level. Defaults to ZERO - meaning no output. Can be increased to 2.
            try: verbosity = int(args.verbosity[0])
            except: verbosity = 2
            # Create a dictionary combining all settings
            settings = {"source":source, "output":output, "include":include, "scratch": scratch, "verbosity":verbosity, "logo":icon}
            # Parse additional settings to modify the build
            if theme: settings.update({"html_theme":theme})

        # Use an exception to allow help message to be printed.
        except Exception as _:
            # Execute default.
            sphinx("Composite Damage Analysis Code", "codac")           
        else:
            # Execute CLI command
            sphinx(project, mainfile, **settings)
        pass
    
    def create(self, **kwargs): # pragma: no cover
        """
        Execute make command
        """            
        from distutils.dir_util import copy_tree
        
        # You can set these variables from the command line.
        self.SPHINXOPTS = os.getenv('sphinx_opts', '')
        self.SPHINXBUILD = os.getenv('sphinx_build', 'sphinx-build')
        self.PAPER = os.getenv('sphinx_paper', None)
        
        self.SOURCEDIR = os.getenv('sphinx_sourcedir', self.srcdir)
        self.BUILDDIR = os.getenv('sphinx_builddir', Utility.PathLeaf(tempfile.NamedTemporaryFile().name))
        self.TEMPDIR = os.getenv('sphinx_templates', "_templates")
        self.STATICEDIR = os.getenv('sphinx_static', "_static")
        
        # Create static and template folder relative to source directory, if required.
        os.environ['sphinx_static'] = self.STATICEDIR; os.environ['sphinx_templates'] = self.TEMPDIR
        
        # Add path dependencies 
        os.environ["sphinx_include"] = os.getenv("sphinx_include","")
        os.environ["sphinx_include"] += os.pathsep + os.pathsep.join(self.incdirs)
    
        def validate():
            """
            User-friendly check for sphinx-build
            """
            with open(os.devnull, 'w') as devnull:
                try:
                    if subprocess.call([self.SPHINXBUILD, '--version'],stdout=devnull, stderr=devnull) == 0:
                        return
                except FileNotFoundError:
                    pass    
                print(
                      "The '{0}' command was not found. Make sure you have Sphinx "
                      "installed, then set the SPHINXBUILD environment variable "
                      "to point to the full path of the '{0}' executable. "
                      "Alternatively you can add the directory with the "
                      "executable to your PATH. If you don't have Sphinx "
                      "installed, grab it from http://sphinx-doc.org/)"
                      .format(self.SPHINXBUILD))
                sys.exit(1)
            return
        
        def build(builder, success_msg=None, extra_opts=None, outdir=None,doctrees=True):
            """
            The default target
            """
            builddir = os.path.join(self.BUILDDIR or outdir)
            command = [self.SPHINXBUILD, '-M', builder, self.SOURCEDIR, builddir]
            command.extend(['-c', os.getenv('sphinx_config',self.SOURCEDIR)])
            if command[-1] == self.SOURCEDIR:
                command = command[:len(command)-2]
            if doctrees:
                command.extend(['-d', os.path.join(self.BUILDDIR, 'doctrees')])
            if extra_opts:
                command.extend(extra_opts)
            command.extend(shlex.split(self.SPHINXOPTS))
            # Execute build command
            if Utility.Popen(command,self.verbose).returncode == 0:
                print('Build finished. ' + success_msg.format(self.outdir or builddir))
        
        def buildmethod(function):
            """
            Decorator function for each build option
            """
            self.BuildOption[function.__name__] = function
            return function
        
        @buildmethod
        def default():
            """
            The default target
            """
            return html()
        
        @buildmethod
        def clean():
            """
            Remove the build directory
            """
            shutil.rmtree(self.BUILDDIR, ignore_errors=True)
        
        @buildmethod
        def html():
            """
            Make standalone HTML files
            """
            return build('html', 'The HTML pages are in {}.')
        
        @buildmethod
        def dirhtml():
            """
            Make HTML files named index.html in directories
            """
            return build('dirhtml', 'The HTML pages are in {}')
         
        @buildmethod
        def singlehtml():
            """
            Make a single large HTML file
            """
            return build('singlehtml', 'The HTML page is in {}.')
         
        @buildmethod
        def pickle():
            """
            Make pickle files
            """
            return build('pickle', 'Now you can process the pickle files.')
         
        @buildmethod
        def json():
            """
            Make JSON files
            """
            return build('json', 'Now you can process the JSON files.')
         
        @buildmethod
        def htmlhelp():
            """
            Make HTML files and a HTML help project
            """
            return build('htmlhelp', 'Now you can run HTML Help Workshop with the .hhp project file in {}.')
         
        @buildmethod
        def qthelp():
            """
            Make HTML files and a qthelp project
            """
            return build('qthelp', 'Now you can run "qcollectiongenerator" with the '
                                  '.qhcp project file in {0}, like this: \n'
                                  '# qcollectiongenerator {0}/RinohType.qhcp\n'
                                  'To view the help file:\n'
                                  '# assistant -collectionFile {0}/RinohType.qhc')
         
        @buildmethod
        def devhelp():
            """
            Make HTML files and a Devhelp project
            """
            return build('devhelp', 'To view the help file:\n'
                                    '# mkdir -p $HOME/.local/share/devhelp/RinohType\n'
                                    '# ln -s {} $HOME/.local/share/devhelp/RinohType\n'
                                    '# devhelp')
         
        @buildmethod
        def epub(self):
            """
            Make an epub
            """
            return self.build('epub', 'The epub file is in {}.')
         
        @buildmethod
        def rinoh(self):
            """
            Make a PDF using rinohtype
            """
            return self.build('rinoh', 'The PDF file is in {}.')
         
        @buildmethod
        def latex():
            """
            Make LaTeX files, you can set PAPER=a4 or PAPER=letter
            """
            extra_opts = ['-D', 'latex_paper_size={}'.format(self.PAPER)] if self.PAPER else None
            return build('latex', 'The LaTeX files are in {}.\n'
                                  "Run 'make' in that directory to run these through "
                                  "(pdf)latex (use the 'latexpdf' target to do that "
                                  "automatically).", extra_opts)
         
        @buildmethod
        def latexpdf():
            """
            Make LaTeX files and run them through pdflatex
            """
            _ = latex()
            print('Running LaTeX files through pdflatex...')
            builddir = os.path.join(self.BUILDDIR, 'latex')
            subprocess.call(['make', '-C', builddir, 'all-pdf'])
            print('pdflatex finished; the PDF files are in {}.'.format(builddir))
         
        @buildmethod
        def latexpdfja():
            """
            Make LaTeX files and run them through platex/dvipdfmx
            """
            _ = latex()
            print('Running LaTeX files through platex and dvipdfmx...')
            builddir = os.path.join(self.BUILDDIR, 'latex')
            subprocess.call(['make', '-C', builddir, 'all-pdf-ja'])
            print('pdflatex finished; the PDF files are in {}.'.format(builddir))
         
        @buildmethod
        def text():
            """
            Make text files
            """
            return build('text', 'The text files are in {}.')
         
        @buildmethod
        def man():
            """
            Make manual pages
            """
            return build('man', 'The manual pages are in {}.')
         
        @buildmethod
        def texinfo():
            """
            Make TexInfo files
            """
            return build('texinfo', 'The Texinfo files are in {}.\n'
                                    "Run 'make' in that directory to run these "
                                    "through makeinfo (use the 'info' target to do "
                                    "that automatically).")
         
        @buildmethod
        def info():
            """
            Make Texinfo files and run them through makeinfo
            """
            _ = texinfo()
            print('Running Texinfo files through makeinfo...')
            builddir = os.path.join(self.BUILDDIR, 'texinfo')
            subprocess.call(['make', '-C', builddir, 'info'])
            print('makeinfo finished; the Info files are in {}.'.format(builddir))
         
        @buildmethod
        def gettext():
            """
            Make PO message catalogs
            """
            return build('gettext', 'The message catalogs are in {}.', outdir='locale',doctrees=False)
         
        @buildmethod
        def changes():
            """
            Make an overview of all changed/added/deprecated items
            """
            return build('changes', 'The overview file is in {}.')
         
        @buildmethod
        def xml():
            """
            Make Docutils-native XML files
            """
            return build('xml', 'The XML files are in {}.')
         
        @buildmethod
        def pseudoxml():
            """
            Make pseudoxml-XML files for display purposes
            """
            return self.build('pseudoxml', 'The pseudo-XML files are in {}.')
         
        @buildmethod
        def linkcheck():
            """
            Check all external links for integrity
            """
            return build('linkcheck', 'Look for any errors in the above output or in {}/output.txt.')
         
        @buildmethod
        def doctest():
            """
            Run all doctests embedded in the documentation (if enabled)
            """
            return build('doctest', 'Look at the results in {}/output.txt.')
         
        @buildmethod
        def assist():
            """
            List all targets
            """
            print("Please use '{} <target>' where <target> is one of" .format(sys.argv[0]))
            width = max(len(name) for name in self.BuildOption)
            for name, target in self.BuildOption.items():
                print('  {name:{width}} {descr}'.format(name=name, width=width, descr=target.__doc__))
        
        # Validate installation status
        validate()
        # Get additional command line arguments
        args = ['default'] or sys.argv[1:]
        for arg in args:
            # Create a temporary build directory. We do not need unsuccessful build
            with Utility.TemporaryDirectory(self.scrtdir):
                # Create a new local directory
                temp = Utility.PathLeaf(tempfile.NamedTemporaryFile().name)   
                # Copy all source files into the temporary directory
                shutil.copytree(os.path.abspath(self.SOURCEDIR), os.path.abspath(temp), ignore=shutil.ignore_patterns(".git",".svn")); self.SOURCEDIR = temp
                # Add auto documentation feature
                for x in os.getenv("sphinx_include","").split(os.pathsep): 
                    try: subprocess.call(["sphinx-apidoc","-o",os.path.join(temp,"_advanced",Utility.PathLeaf(os.path.dirname(x)).lower()),x])
                    except: pass
                # If no configuration file is found in the source folder, use the default template
                if not os.path.exists(os.path.join(temp,"conf.py")):
                    # Rename default configuration file to match naming convention.
                    copyfile(os.path.join(PyXMakePath,"Build","config","stm_conf.py"), os.path.join(temp,"conf.py"))
                    # Create an additional static folder if not already existing
                    if not os.path.exists(os.path.join(temp,"_static")):
                        os.mkdir(os.path.join(temp,'_static')); copyfile(os.path.join(PyXMakePath,"Build","config","stm_style.css"), os.path.join(temp,"_static","style.css"))
                    # Create an additional templates folder
                    if not os.path.exists(os.path.join(temp,"_templates")):
                        os.mkdir(os.path.join(temp,'_templates')); copyfile(os.path.join(PyXMakePath,"Build","config","stm_layout.html"), os.path.join(temp,"_templates","layout.html"))
                # Create all documentations
                self.BuildOption[arg]()
                # Do not keep temporary tree by default
                if not kwargs.get("keep_doctree",False):
                    try:
                        shutil.rmtree(os.path.join(self.BUILDDIR,"doctrees"))
                    except OSError:
                        pass
                # Copy results to output directory
                copy_tree(self.BUILDDIR, self.outdir)   
        
        # Return success 
        return 0  
    
## @class PyXMake.Build.Make.SSH
# Base class for all build events requiring a SSH connection. Inherited from Make.     
class SSH(Make): # pragma: no cover
    """
    Inherited class for all builds using SSH connection.
    """    
    def __init__(self, *args, **kwargs):
        """
        Initialization of SSH class object.
        """
        super(SSH, self).__init__(*args, **kwargs)    
        
        # Add Fortran wrapper function to SSH class.
        setattr(self, str(Fortran.Wrapper.__name__), MethodType(Fortran.Wrapper, self))
        
        # Defined here to be checked later.
        ## Wrapper interface file for 3rd party FORTRAN code. Automatically creates a module of the underlying source material.
        self.intermediate_wrapper = ""
        self.wrapper_source = ""
        self.wrapper_module = "pyx_module.f90"  
        
        ## String identifier of current instance.
        self.MakeObjectKind = 'SSH'
        
        # Immutable settings for SSH object    
        ## Name of library, assembled using BuildID.
        self.libname = "lib"+self.buildid + self.architecture            
        ## Temporary build name.
        self.buildname = self.buildid+'_ssh'
        ## Environment variables to be set prior to the execution of the build command. Intel Fortran 12+ 
        self.export = "export CPATH=$CPATH"        
        ## Environment variables to be set prior to the execution of the build command. Intel Fortran 11 and lower. 
        self.__old_export = "export FPATH=$FPATH"     
        ## Environment variable to be set prior to the execution of the build command.        
        self.__library_path = "export LIBRARY_PATH=$LIBRARY_PATH"   
        ## Custom intel path       
        self.__intel_path = "export pyx_ifort=$(which ifort)"
        
        ## Define if the input should be compiled exactly as provided.
        # Defaults to False, meaning that merging & pre-processing utilities will be carried out.
        self.incremental = kwargs.get('incremental', False)
             
        # Initialization of lists containing additional sources, modules or libraries
        ## List of libraries which should be statically linked in.
        self.linkedIn = []       
        
        # Initialization of  tuple containing temporary files        
        ## Blank version of tuple to store temporary file names scheduled for removal.
        self.temps = () 
        
        ## Load an additional library prior to execution of all commands. Defaults to an empty string.
        self.environment = ""
        
        # Remove MKL from default command line
        ## Blank version of list containing library directories. MKL library has been removed since location
        # on the SSH remote computer is not known a priori.
        self.libdirs = []                          
        pass    
    
    def OutputPath(self, libpath, modulepath=None):
        """
        Define output directories for modules and libraries. Output written to the workspace is DELETED.
        """    
        # Output module files to scratch directory by default.
        if modulepath is None:
            modulepath = libpath       
        ## Output path for module or header files.      
        self.outmodule = modulepath + posixpath.sep
        ## Output path for library files.
        self.outlibs = libpath + posixpath.sep
        pass
    
    def Settings(self, user, key="", host='129.247.54.37', port=22, use_cache=True, **kwargs):
        """
        Define settings to establish a SSH connection. 
        """
        # Establish SSH connection to institute cluster                                         // mg 07.08.17
        # Parse an external client directly to the underlying connection. Use this connection for all following operations.
        if kwargs.get("client",None): 
            self.ssh_client = kwargs.get("client"); 
            sftp = self.ssh_client.open_sftp(); sftp.chdir(".")
            self.workspace = kwargs.get("workspace",posixpath.join(sftp.getcwd(),"")); sftp.close()
            return
        ## Remote workspace. This is the scratch directory for the build event. 
        # Defaults to /home/user/. 
        self.workspace = kwargs.get("workspace",posixpath.join(Utility.AsDrive('home',posixpath.sep),user)+posixpath.sep)
        ## Instance of SSHClient to establish a SSH connection.
        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # Read password (if given)
        password = kwargs.pop("password",""); 
        try: 
            # A password has been given. Use it directly
            if password: raise ValueError
            # Try to connect using key file
            try: self.ssh_client.connect(hostname=host, port=port, username=user, key_filename=key, timeout=kwargs.get("timeout",None))
            except paramiko.ssh_exception.SSHException: 
                self.ssh_client.connect(hostname=host, port=port, username=user, key_filename=key, timeout=kwargs.get("timeout",None),
                                                        disabled_algorithms=kwargs.get("disabled",{"pubkeys":["rsa-sha2-512", "rsa-sha2-256"]}))
        except socket.timeout: raise TimeoutError
        except:
            if use_cache:
                # Check if the password should be cached. Active by default. 
                try: import keyring
                except: raise ModuleNotFoundError           
                # Check if the stored/cached password can be used. Prompt to reenter the password if that is not the case.
                try: self.ssh_client.connect(hostname=host, port=port, username=user, password=keyring.get_password(user, user))
                except: 
                    # Get password from user
                    if not password: password = getpass.getpass()
                    keyring.set_password(user, user, password)
                finally: self.ssh_client.connect(hostname=host, port=port, username=user, password=keyring.get_password(user, user))
            else:
                if not password: password = getpass.getpass()
                self.ssh_client.connect(hostname=host, port=port, username=user, password=password)
        pass
    
    def Environment(self, path="", bash="", args="", method="source"):
        """
        Load an additional environment file prior to execution of all commands. 
        """
        source = method
        ## Execute an additional bash script prior to all build commands. 
        if any([str(posixpath.join(path,bash)).startswith("module"),args.startswith("module")]): source = ""
        self.environment += " ".join([source,posixpath.join(path,bash),args])+"; "
        pass                      
    
    def Postprocessing(self, cmdstring=""):
        """
        Assemble command string for the post-build event.
        """
        ## Command executed during post-build event.
        self.postcmd = cmdstring                      
        pass              
    
    def Build(self, cmdstring, run= "ifort", path="", lib= "", linkedIn="", **kwargs):
        """
        Assemble command strings for the main build event.
        """
        cmd = ""; self.postcmd = ""
        
        # Which libraries are used for linking (relative path).  
        self.libs.append(lib)
        self.libs = list(Utility.ArbitraryFlattening(self.libs))          
        
        # Which libraries have to be additionally linked in (absolute path).  
        self.linkedIn.append(linkedIn)
        self.linkedIn = list(Utility.ArbitraryFlattening(self.linkedIn))       
        
        # Build commands using Intel Fortran (mutable)
        ## (Intel Fortran) Compiler Path
        self.path2exe = path; self.exe = run
        
        # Check whether an interface module wrapper was added to the current folder
        if os.path.isfile(self.intermediate_wrapper):
            if (Utility.IsNotEmpty(self.wrapper_source)):
                self.buildname = self.wrapper_source

        # Immutable settings for SSH object        
        if self.incremental:         
            c_files = [x for x in self.srcs if os.path.splitext(x)[1].lower() in (".for", ".f95", ".f", ".f90")]        
            cmd += ' %s ' % (' '.join(c_files))  
        
        # Always add MKL when used with f2py.
        if self.exe in ("f2py") and self.exe:         
            cmd += "-m "+str(self.buildid+self.architecture)
            # Assist f2py by providing shared MKL libraries directly
            self.libs.extend(["mkl_rt","iomp5", "pthread", "m", "dl"])
            
        # Add libraries for referencing to the command string (they are only used as resources)
        for x in [' -l'+x+' ' for x in self.libs if x]:
            cmd += x     
            
        ## Remote (Intel) Compiler command.
        if self.exe and self.exe not in ("custom"):
            self.makecmd = posixpath.join(self.path2exe,self.exe)+" -c "+ cmd + cmdstring
        else:
            self.makecmd = cmdstring
         
        ## Remote Linker command.
        if self.exe not in ("ifort", "gcc", "g++"):
            ## Do no use any archiver
            self.linkcmd = ""
        elif self.exe == "ifort":
            ## Remote Intel Linker command.
            self.linkcmd = posixpath.join(self.path2exe,"xiar")+" -rc "            
        else:
            ## Simply execute UNIX archiver
            self.linkcmd = posixpath.join("","ar")+" -rc "    
        pass   

    def create(self, **kwargs): 
        """
        Define settings to establish SSH connection. 
        """
        cmd = ""
        
        # Add all include paths to CPATH & FPATH (deprecated!) environment variable
        includes = [':"'+x+'"' for x in self.incdirs]
        for x in includes: 
            self.export += x
            self.__old_export += x
        self.export += " && " + self.__old_export
        
        # Add all library paths to LIBRARY_PATH environment variable
        library = [':"'+x+'" ' for x in self.libdirs]
        for x in library: 
            self.__library_path += x
        self.export += " && " + self.__library_path                  
        
        # Add libraries for linking to the command string
        try: 
            if self.linkedIn[0] != "":
                linklist = ['ar -x "'+x+'" && '  for x in self.linkedIn]
                for x in linklist: 
                    cmd += x
            # Link list is empty or does not exist
        except IndexError:
            pass
        
        # Get the target and the base name of library (created in the process).         
        target = posixpath.join(self.workspace,self.buildname)        
        # base = os.path.splitext(target)[0]      

        # Go into scratch directory (if defined)
        with Utility.ChangedWorkingDirectory(self.scrtdir):      
            
            # Pre-build event  (if required)          
            try: 
                if self.precmd != '':      
                    Utility.Popen(self.precmd, self.verbose)             
            except:
                pass  
        
            # Establish ssh connection and execute make commands on the linux cluster.
            sftp = self.ssh_client.open_sftp()
            
            try:
                sftp.put(self.buildname,target)        
                if os.path.isfile(self.intermediate_wrapper):     
                    # Use general-purpose wrapper file 
                    Utility.ReplaceTextinFile(self.intermediate_wrapper, self.wrapper_module, {'%pyx_source%':'"'+self.buildname+'"',"#":"      "}, source=self.scrtdir)    
                    sftp.put(os.path.join(self.scrtdir,self.wrapper_module),posixpath.join(self.workspace, self.wrapper_module)) 
                    target = posixpath.join(self.workspace,self.wrapper_module)  
                    # Preserve the unique name of each object file
                    self.makecmd += " -o "+ os.path.splitext(self.buildname)[0]+".o"                                             
            except:
                target = ""
                for cs in self.srcs:
                    sftp.put(os.path.join(self.scrtdir,cs),posixpath.join(self.workspace,cs))
            
            # Put f2py mapping file into current workspace
            if self.exe not in ("ifort", "gcc", "g++","custom"):
                sftp.put(os.path.join(Path2Config,".f2py_f2cmap"), posixpath.join(self.workspace,".f2py_f2cmap"))
            sftp.close()
        
        # Create output folder if not existing 
        Utility.SSHPopen(self.ssh_client,"mkdir -p "+self.outmodule+"; mkdir -p "+self.workspace,self.verbose, **kwargs)
        
        # Delete old content in output folders
        if not kwargs.get("combine", False):
            Utility.SSHPopen(self.ssh_client,'rm -f '+self.outmodule+'*.mod; rm -f '+self.workspace+'*.mod', self.verbose, **kwargs)
        else:
            Utility.SSHPopen(self.ssh_client,'rm -f '+self.workspace+'*.mod',self.verbose, **kwargs)
                                
        self.command = self.environment + self.export + " && cd "+self.workspace+ " && " + self.makecmd
        if Utility.IsNotEmpty(target):
            self.command+= ' "'+target+'"'
        sbuild = Utility.SSHPopen(self.ssh_client, self.command, self.verbose, **kwargs)

        if sbuild==0:
            # There is a valid link command. Use it
            if Utility.IsNotEmpty(self.linkcmd):
                self.command = self.environment + self.export + " && cd "+self.workspace+ " && " + cmd + self.linkcmd + self.libname+'.a '+'*.o '
                sarch = Utility.SSHPopen(self.ssh_client, self.command, self.verbose, **kwargs)
            elif self.exe in ["custom"]:  
                sarch = 1; scopy = 1
            # Copy all created shared libraries.
            else:  
                sarch = 1; scopy = 0
                self.postcmd += ' && cp -rf '+self.workspace+'*.so '+self.outlibs
                
        if sarch==0:
            self.command = 'cp -rf '+self.workspace+'*.mod '+self.outmodule+'; cp -rf '+self.workspace+'*.a '+self.outlibs
            scopy = Utility.SSHPopen(self.ssh_client, self.command, self.verbose, **kwargs)
      
        if scopy == 0:    
            Utility.SSHPopen(self.ssh_client,'rm '+self.workspace+'*.o; rm '+self.workspace+'*.mod; rm '+self.workspace+'*.a; rm '+
                                                                                          self.workspace+'*.f90; rm -rf '+posixpath.join(self.workspace,"intel"), self.verbose, **kwargs)  

        if Utility.IsNotEmpty(self.postcmd):
            self.export += " && " + self.__intel_path
            self.command = self.environment + self.export + " && " + self.postcmd
            spost = Utility.SSHPopen(self.ssh_client, self.command, self.verbose, **kwargs)   
            if spost == 0:
                Utility.SSHPopen(self.ssh_client,'rm -f '+self.workspace+'*.o; rm '+self.workspace+'*.mod; rm -f '+self.workspace+'*.a; rm -f '+
                                                                                               self.workspace+'*.f90; rm -f '+self.workspace+'*.f; rm -rf '+
                                                                                               posixpath.join(self.workspace,"intel")+'; rm -f '+
                                                                                               posixpath.join(self.workspace,".f2py_f2cmap") +
                                                                                               " rm -f %s " % (' '.join([posixpath.join(self.workspace,cs) for cs in self.srcs])),
                                                                                               self.verbose, **kwargs)
                pass 
        pass
    
        # Combine event (needed for TOMS). Combine multiple libraries into ONE.
        if kwargs.get("combine", False):
            librarian = 'ar'; ext = '.a'; decomp = " && "+librarian+" -x "
            mergedid = "lib"+posixpath.basename(self.outmodule.rstrip("/"))     
            _ , stdout, _ = self.ssh_client.exec_command('ls '+self.outlibs)    
            multi_libs = [x for x in [x.rstrip("\n") for x in stdout.readlines() if x.startswith(mergedid)]]
            
            try:
                # Remove old combined library from the list.
                multi_libs.remove(mergedid+self.architecture+ext)
            except:
                pass
            
            self.postcmd = self.environment + self.export + " && cd "+self.outlibs.rstrip("/")+" && " 
            self.postcmd += librarian +" -x " + decomp.join(multi_libs) +" && "
            self.postcmd += librarian + " -rc " + mergedid+self.architecture+ext+ " *.o"
            
            Utility.SSHPopen(self.ssh_client, self.postcmd, self.verbose,**kwargs)           
            for lib in multi_libs:
                Utility.SSHPopen(self.ssh_client,'rm -f '+posixpath.join(self.outlibs,lib),self.verbose, **kwargs)
            self.ssh_client.exec_command('rm -f '+self.outlibs+'*.o')

        # Go into scratch directory (if defined)
        with Utility.ChangedWorkingDirectory(self.scrtdir):          
            
            # Finish and delete redundant files
            Utility.DeleteFilesbyEnding(self.temps)

## Backwards compatibility for deprecated class calls
setattr(sys.modules[__name__],"Robot", Coverage)
## Forward compatibility for future class calls
setattr(sys.modules[__name__],"CMake", Custom)

if __name__ == '__main__':
    pass