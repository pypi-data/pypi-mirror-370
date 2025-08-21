# -*- coding: utf-8 -*-
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %                                                         PyXMake - Build environment for PyXMake                                                          %
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
"""
Jenkins Test Server script.
 
@note: Start build jobs on the Jenkins Test Server using PyXMake. 

@version:  1.0    
----------------------------------------------------------------------------------------------
@requires:
       - PyXMake, PyCODAC 

@change: 
       -    
   
@author: 
        - hein_fa                                                 [DLR-FA,STM Braunschweig]
        - garb_ma                                              [DLR-FA,STM Braunschweig]
----------------------------------------------------------------------------------------------
"""
# See the file "LICENSE.txt" for the full license governing this code.

## @package PyXMake.VTL.stm_make
# Start build jobs on the Jenkins Test Server using PyXMake.
## @author 
# Falk Heinecke, Marc Garbade
## @date
# 20.03.2018
## @par Notes/Changes
# - Added documentation // mg 28.06.2018

"""
Setup script.
from main import release creator_Abhi
"""
import shutil
import os 
import subprocess
import sys
import setuptools
import inspect
import warnings

from packaging.version import parse
from distutils.command import clean as _clean
from distutils import core

## Add PyXMake source folder to system path (if not already present). Allows usage as a plugin.
if os.path.abspath(inspect.getfile(inspect.currentframe())).split("PyXMake")[0] not in sys.path: 
    sys.path.append(os.path.abspath(inspect.getfile(inspect.currentframe())).split("PyXMake")[0])

class Clean(_clean.clean): # pragma: no cover
    """ 
    Little clean extension: Cleans up a non-empty build directory. 
    """
    def run(self):
        """ 
        Delete all redundant folders and directories. Ignore read-only GIT repositories
        
        @author: garb_ma
        """        
        from PyXMake.Tools.Utility import DeleteRedundantFolders
        for path in ["build", "dist", ".coverage"]:
            if os.path.isdir(path):
                try: DeleteRedundantFolders(path, ignore_readonly=True)
                except: shutil.rmtree(path)
            elif os.path.isfile(path):
                os.remove(path)


class _BaseCommandRunner(core.Command): # pragma: no cover
    """ 
    Base class for encapsulating command line commands. 
    """
    def run(self):
        self._create_build_dir()
        command = self._create_command()
        self._run_command(command)
        self._perform_post_actions()

    @staticmethod
    def _create_build_dir():
        if not os.path.exists("build"):
            os.mkdir("build")

    def _create_command(self):
        pass

    def _run_command(self, command):
        if self.verbose:
            print(command)
        subprocess.call(command, shell=True)
    
    def _perform_post_actions(self):
        pass


class pyx_app(_BaseCommandRunner): # pragma: no cover
    """ 
    Base class for encapsulating command line arguments and build process. 
    """
    _APP_NAME = ''
    _INPUT_SCRIPT = ""
    
    description = "Compile a stand-alone application using PyInstaller."
    user_options = [
        # The format is (long option, short option, description).
        ('source-path=', None, 'path to the folder holding source files'),
        ('verbose=', None, 'controls the logging level (0 - Nothing, 2- Everything) Default: 0 - Nothing'),
        ('mode=', None, 'define application build mode (one directory or one file mode)'),        
        ('scratch-path=', None, 'path to scratch folder where all temporary data is located during the build event'),        
        ('output-file-path=', None, 'path to the output directory'),
        ]
    
    def initialize_options(self):
        """
        Set default values for options.
        """
        # Each user option must be listed here with their default value.
        self.verbose = 0
        self.source_path = ''
        self.output_file_path = ''
        self.mode = "onedir"        
        self.scratch_path = os.getcwd()
        self.include = None
        self.dependency = None

    def finalize_options(self):
        """
        Post-process options.
        """
        if self.source_path:
            assert os.path.exists(self.source_path), (
                'Source path'+self.source_path+' does not exist.')

    def _run_command(self, command):
        """
        Execute build command
        """
        from PyXMake.VTL import app # @UnresolvedImport    
        
        # Are additional dependencies given? Defaults to empty lists
        include = []; dependency = []
        if self.include:
            include = self.include
        if self.dependency:
            dependency = self.dependency

        # Compile stand-alone python application         
        app(self._APP_NAME, 
                        script=self._INPUT_SCRIPT,
                        scratch=self.scratch_path,
                        source=self.source_path, 
                        mode=self.mode,
                        output=self.output_file_path,
                        verbosity=self.verbose,
                        encryption=True,
                        include=include, dependency=dependency, 
                        preprocessing=command)
        
class app_pycodac(pyx_app): # pragma: no cover
    """ 
    Runs the application build process using PyCODAC to create runtime for STMLab. 
    """
    from PyXMake.VTL import GetSourceCode # @UnresolvedImport   
    
    # Set class defining attributes.
    _KEY_OPT = 8
    _APP_NAME = 'STMLab'
    _INPUT_SCRIPT = GetSourceCode(_KEY_OPT)

    def _create_command(self):
        from PyXMake import VTL #@UnresolvedImport
        import PyCODAC #@UnresolvedImport
        
        # Add pre-assembled dependencies from VTL
        self.include=VTL.GetIncludeDirectory(PyCODAC.PyCODACPath, self._KEY_OPT),
        self.dependency=VTL.GetLinkDependency(self._KEY_OPT),    
    
        # Assemble pre-processing command to include Smetana & DEliS
        delimn = " "; continuation = "&&"
        command = delimn.join([
                               sys.executable,os.path.join(PyCODAC.PyCODACPath,"Plugin","DELiS","__install__.py"),continuation,
                               sys.executable,os.path.join(PyCODAC.PyCODACPath,"Plugin","DELiS","__update__.py"),continuation,
                               sys.executable,os.path.join(PyCODAC.PyCODACPath,"Plugin","Smetana","__install__.py"),continuation,
                               sys.executable,os.path.join(PyCODAC.PyCODACPath,"Plugin","Smetana","__update__.py")
                               ])

        return command
    
    
class pyx_bundle(_BaseCommandRunner): # pragma: no cover
    """ 
    Base class for encapsulating command line arguments and build process. 
    """
    _BUNDLE_NAME = ''
    _INPUT_FILES = ""
    
    description = "Compile a stand-alone installer using NSIS."
    user_options = [
        # The format is (long option, short option, description).
        ('source-path=', None, 'path to the folder holding source files'),
        ('verbose=', None, 'controls the logging level (0 - Nothing, 2- Everything) Default: 0 - Nothing'),
        ('scratch-path=', None, 'path to scratch folder where all temporary data is located during the build event'),        
        ('output-file-path=', None, 'path to the output directory'),
        ('install-path=', None, 'path to the default installation directory'),
        ]
    
    def initialize_options(self):
        """
        Set default values for options.
        """
        # Each user option must be listed here with their default value.
        self.verbose = 0
        self.source_path = ''
        self.output_file_path = ''
        self.scratch_path = os.getcwd()
        self.install_path = "$Desktop"

    def finalize_options(self):
        """
        Post-process options.
        """
        if self.source_path:
            assert os.path.exists(self.source_path), (
                'Source path'+self.source_path+' does not exist.')

    def _run_command(self, command):
        """
        Execute build command
        """
        from PyXMake.VTL import bundle # @UnresolvedImport    

        # Compile stand-alone python application         
        bundle(self._BUNDLE_NAME, 
                      files=self._INPUT_FILES,
                      scratch=self.scratch_path,
                      source=self.source_path, 
                      output=self.output_file_path,
                      verbosity=self.verbose,
                      install_path=self.install_path,
                      assembly_path=os.path.dirname(self.source_path),
                      # Upload installer to FTP server.
                     user='ASRI_adm', key='lm9ITHUR', upload =True)
    
class bundle_pycodac(pyx_bundle): # pragma: no cover
    """ 
    Create an installer for STMLab using PyCODAC.
    """   
    # Set class defining attributes.
    _BUNDLE_NAME = 'STMLab'
    _INPUT_FILES = "*.*"

    def _create_command(self):  
        # Import package
        import svn.remote
        from PyXMake.Tools import Utility #@UnresolvedImport
        # Overwrite default installation directory
        self.install_path = os.getenv("plugin_central_dir",os.path.join(Utility.AsDrive("c"),"simulia","cae","plugins","2019"))
        # Define local output directories
        __url_delimn = "/"
        __pyc_plugin   = os.path.join(self.source_path,"PyCODAC")
        __smet_plugin = os.path.join(self.source_path,"Smetana")
        # Set URLs to repositories
        __pyc_plugin_repo = __url_delimn.join(["https:","","svn.dlr.de","STM-Routines","Analysis_Tools","MCODAC","trunk","src","mcd_pycodac","PyCODAC","Plugin","JupyterLab","src"])
        __smet_plugin_repo = __url_delimn.join(["https:","","svn.dlr.de","STM-Routines","Analysis_Tools","MCODAC","trunk","src","mcd_pycodac","PyCODAC","Plugin","Smetana","src"])
        ## Export content of repositories into the current source folder to create a bundle
        # Added exception to paths containing an @ sign: https://stackoverflow.com/questions/757435/how-to-escape-characters-in-subversion-managed-file-names
        if "@" in __pyc_plugin: __pyc_plugin += "@"
        if "@" in __smet_plugin: __smet_plugin += "@"
        svn.remote.RemoteClient(__pyc_plugin_repo).export(__pyc_plugin, force=True)
        svn.remote.RemoteClient(__smet_plugin_repo).export(__smet_plugin, force=True)
        # Remove last character if its an escape character used by SVN
        if __pyc_plugin.endswith("@"): __pyc_plugin = __pyc_plugin[:-1]
        # Delete unwanted files and folders
        shutil.rmtree(os.path.join(__pyc_plugin,".config"), ignore_errors=True)
        os.remove(os.path.join(__pyc_plugin,"user","Paths.log"))
        # Return dummy command
        command = " "       
        # Return
        return command
    
    
class pyx_sphinx(_BaseCommandRunner): # pragma: no cover
    """ 
    Base class for encapsulating command line arguments and build process. 
    """
    _BUILD_NAME = ''
    _INPUT_FILE = ""
    
    description = "Runs the html documentation build process of source code using Sphinx."
    user_options = [
        # The format is (long option, short option, description).
        ('source-path=', None, 'path to the folder holding source files'),
        ('verbose=', None, 'controls the logging level (0 - Nothing, 2- Everything) Default: 0 - Nothing'),
        ('include-path=', None, 'path to additional files required for processing.'),
        ('scratch-path=', None, 'path to scratch folder where all temporary data is located during the build event'),        
        ('output-file-path=', None, 'path to the output directory'),
        ('logo=', None, 'Custom logo for the upper left corner. Defaults to None, leaving the space empty'),        
        ]
    
    def initialize_options(self):
        """
        Set default values for options.
        """
        # Each user option must be listed here with their default value.
        self.verbose = 0
        self.include_path = ""
        self.source_path = ''
        self.output_file_path = ''
        self.scratch_path = os.getcwd()
        self.logo = None        

    def finalize_options(self):
        """
        Post-process options.
        """
        if self.source_path:
            assert os.path.exists(self.source_path), (
                'Source path'+self.source_path+' does not exist.')

    def _run_command(self, command):
        """
        Execute build command
        """
        from PyXMake.VTL import sphinx # @UnresolvedImport        

        # Build documentation            
        sphinx(self._BUILD_NAME, 
                     self._INPUT_FILE, 
                     scratch=self.scratch_path,
                     source=self.source_path, 
                     include=self.include_path,
                     output=self.output_file_path,
                     verbosity=self.verbose,
                     logo=self.logo)

class sphinx_stmlab(pyx_sphinx): # pragma: no cover
    """ 
    Runs the html documentation build process for Structural Mechanics Lab using a scheme from ReadtheDocs. 
    """
    # Set class defining attributes     
    _BUILD_NAME = 'Structural Mechanics Lab'
    _INPUT_FILE = "stm_lab"

    def _create_command(self):  
        from PyXMake.Tools import Utility # @UnresolvedImport   
        # Predefined script local variables
        __arch = Utility.GetArchitecture()
        __platform = Utility.GetPlatform()
        
        from PyCODAC.Tools.Utility import GetPyCODACPath #@UnresolvedImport
        # Import and set local path to PyCODAC
        __pyc_core_path =  GetPyCODACPath()
        
        self.include_path=[os.path.join(__pyc_core_path,"Plugin","Smetana"),
                                          os.path.join(__pyc_core_path,"Plugin","Smetana","src","Smetana"),
                                          os.path.join(__pyc_core_path,"Core","bin",__platform,__arch)]
        self.logo = os.path.join(__pyc_core_path,"VTL","doc","mcd_stmlab","pics","stm_lab_logo_bubbles.png")

        command = ' '     
        return command
    

class pyx_doxygen(_BaseCommandRunner): # pragma: no cover
    """ 
    Base class for encapsulating command line arguments and build process. 
    """
    _BUILD_NAME = ''
    _INPUT_FILES = []
    
    description = "Runs the html documentation build process of source code using Doxygen."
    user_options = [
        # The format is (long option, short option, description).
        ('source-path=', None, 'path to the folder holding source files'),
        ('verbose=', None, 'controls the logging level (0 - Nothing, 2- Everything) Default: 0 - Nothing'),
        ('stype=', None, 'define type of source files (Java, Python or left blank) Defaults to: Fortran'),        
        ('scratch-path=', None, 'path to scratch folder where all temporary data is located during the build event'),        
        ('output-file-path=', None, 'path to the output directory'),
        ]
    
    def initialize_options(self):
        """
        Set default values for options.
        """
        # Each user option must be listed here with their default value.
        self.verbose = 0
        self.source_path = ''
        self.output_file_path = ''
        self.stype = "Fortran"        
        self.scratch_path = os.getcwd()

    def finalize_options(self):
        """
        Post-process options.
        """
        if self.source_path:
            assert os.path.exists(self.source_path), (
                'Source path'+self.source_path+' does not exist.')

    def _run_command(self, command):
        """
        Execute build command
        """
        from PyXMake.VTL import doxygen # @UnresolvedImport        
        
        # Search for all source files in source folder if files have not been specified.
        if self._INPUT_FILES == []:        
            self._INPUT_FILES = [x[0] for x in os.walk(self.source_path)]

        # Build documentation            
        doxygen(self._BUILD_NAME, 
                        title=[self.brief, self.header], 
                        files=self._INPUT_FILES,
                        ftype=self.stype,
                        verbosity=self.verbose,
                        scratch=self.scratch_path,
                        source=self.source_path, 
                        output=self.output_file_path)
        
        try: 
            # Delete environment variables specifying color scheme after each run.
            del os.environ['dox_hue']; del os.environ['dox_sat']; os.environ['dox_gamma']
        except: pass
    
class doxy_pyxmake(pyx_doxygen): # pragma: no cover
    """ 
    Runs the html documentation build process for PyXMake. 
    """
    # Set class defining attributes     
    _BUILD_NAME = 'pyx_core'
    
#     # Set different color scheme.
#     if not all([os.getenv(x) for x in ("dox_hue","dox_sat","dox_gamma")]):
#         import colorsys
#         import numpy as np
#         from PIL import ImageColor
#         os.environ['dox_hue'], os.environ['dox_sat'], os.environ['dox_gamma'] = [str(int(round(x))) for x in np.multiply([360.,100.,100],
#                                                                                                                                                                np.array(colorsys.rgb_to_hsv(*(value/255 for value in 
#                                                                                                                                                                ImageColor.getcolor("#ff0000","RGB")))))]

    def _create_command(self):  
        from PyXMake.Tools import Utility # @UnresolvedImport   
        # Files to be processed
        self._INPUT_FILES = [x[0] for x in Utility.PathWalk(self.source_path, startswith=(".","__"), contains=("doc","bin","config"), endswith=("make","scratch"))]  
        
        self.brief = "PyXMake"
        self.header = "PyXMake Developer Guide"    
        command = ' '     
        return command
    
class doxy_mcdpycodac(pyx_doxygen): # pragma: no cover
    """ 
    Runs the html documentation build process for PyCODAC. 
    """
    # Set class defining attributes     
    _BUILD_NAME = 'pyc_core'

    def _create_command(self):  
        from PyXMake.Tools import Utility # @UnresolvedImport   
        # Files to be processed
        self._INPUT_FILES = [x[0] for x in Utility.PathWalk(self.source_path, startswith=(".","__"), 
                                                                                                                             contains=("DELiS","Smetana","PyXMake","external","doc","cmd","bin","include","lib","config","fetch"), 
                                                                                                                             endswith=("VTL","make","scratch","examples","src","config","solver"))]
        
        self.brief = "PyCODAC"
        self.header = "PyCODAC Developer Guide"    
        command = ' '     
        return command
    
class doxy_boxbeam(pyx_doxygen): # pragma: no cover
    """ 
    Runs the html documentation build process for BoxBeam. 
    """
    from PyXMake.VTL import GetSourceCode # @UnresolvedImport  
    # Set class defining attributes      
    _KEY_OPT = 1
    _BUILD_NAME = 'box_main'
    # Files to be processed
    _INPUT_FILES = GetSourceCode(_KEY_OPT)

    def _create_command(self):  
        self.brief = "BoxBeam"
        self.header = "BoxBeam Developer Guide"             
        command = ' '     
        return command    
      
class doxy_mcdcore(pyx_doxygen): # pragma: no cover
    """ 
    Runs the html documentation build process for MCODAC. 
    """
    from PyXMake.VTL import GetSourceCode # @UnresolvedImport   
    # Set class defining attributes     
    _KEY_OPT = 0
    _BUILD_NAME = 'mcd_core'
    # Files to be processed
    _INPUT_FILES = GetSourceCode(_KEY_OPT)

    def _create_command(self):  
        self.brief = "MCODAC"
        self.header = "MCODAC Developer Guide"      
        command = ' '     
        return command
    
class doxy_mcdsubbuck(pyx_doxygen): # pragma: no cover
    """ 
    Runs the html documentation build process for BoxBeam. 
    """
    _BUILD_NAME = 'mcd_subbuck'
    
    def _create_command(self):  
        self.brief = "SubBuck"
        self.header = "SubLaminate Buckling Developer Guide"             
        command = ' '     
        return command     
    
class doxy_mcdmapper(pyx_doxygen): # pragma: no cover
    """ 
    Runs the html documentation build process for BoxBeam. 
    """
    _BUILD_NAME = 'mcd_mapper'

    def _create_command(self):  
        self.brief = "Mapper"
        self.header = "Damage Mapping Developer Guide"          
        command = ' '     
        return command            


class pyx_f2py(_BaseCommandRunner): # pragma: no cover
    """ 
    Base class for encapsulating command line arguments and build process. 
    """
    _PACKAGE_NAME = ''
    _INPUT_FILES = []
    
    description = "Runs the build process of Fortran source code for Python using f2py."
    user_options = [
        # The format is (long option, short option, description).
        ('msvsc=', None, 'identifier, which compiler version from Microsoft Visual Studio to be used'),
        ('source-path=', None, 'path to the folder holding the fortran files'),
        ('verbose=', None, 'controls the logging level (0 - Nothing) Default: 2 - Everything'),
        ('scratch-path=', None, 'path to scratch folder where all temporary data is located during the build event'),		
        ('output-file-path=', None, 'path to the output directory'),
        ('base-path=', None, 'path to base folder - optional'),
        ]
    
    def initialize_options(self):
        """
        Set default values for options.
        """
        # Each user option must be listed here with their default value.
        self._MAKE_OPT = {"Python":0, "Java":1, "Fortran":2}
        self.verbose = 2
        self.source_path = ''
        self.output_file_path = ''
        self.base_path = ''    
        self.scratch_path = os.getcwd()
        self.libs = None
        self.includes = None
        self.libpaths = None
        self.incremental = False
        
        # Select Visual Studio version in dependence of operating system.
        if sys.getwindowsversion() >= (10, 0, 0):
            # Jenkins2 // Windows 10
            self.msvsc = "vs2015"
        else:
            # Jenkins // Windows 7
            self.msvsc = "vs2010"

    def finalize_options(self):
        """
        Post-process options.
        """
        if self.source_path:
            assert os.path.exists(self.source_path), (
                'Source path for Fortran files '+self.source_path+' does not exist.')
        if self.base_path:
            assert os.path.exists(self.base_path), (
                'Path to base folder '+self.base_path+' does not exist.')         

    def _run_command(self, command):
        """
        Execute build command
        """
        # Build .pyd using f2py (for now!)
        from PyXMake.VTL import py2x # @UnresolvedImport       
        
        # Are additional dependencies given? Defaults to empty lists
        includes = []; libs = []; libpaths = []
        if self.includes:
            includes = self.includes
        if self.libs:
            libs = self.libs
        if self.libpaths:
            libpaths = self.libpaths

        # Build Python package from Fortran source.
        py2x(self._PACKAGE_NAME, 
                 self._INPUT_FILES, 
                 command=command,
                 libs=libs,include=includes,dependency=libpaths,
                 scratch=self.scratch_path, verbosity=self.verbose,
                 source=self.source_path, output=self.output_file_path, 
                 incremental=self.incremental,
                 msvsc=self.msvsc)

class f2py_mcodac(pyx_f2py): # pragma: no cover
    """ 
    Runs the build process for MCODAC. 
    """
    from PyXMake.VTL import GetSourceCode # @UnresolvedImport    
    # Set class defining attributes    
    _KEY_OPT = 0    
    _PACKAGE_NAME = 'mcd_core'
    # Files to be processed
    _INPUT_FILES = GetSourceCode(_KEY_OPT)

    def _create_command(self):
        from PyXMake import VTL # @UnresolvedImport       
        from PyXMake.Tools import Utility # @UnresolvedImport  
        # Set library path   
        self.includes = [os.path.join(self.base_path,"include",Utility.GetPlatform(),Utility.GetArchitecture(), x)
                                    for x in VTL.GetIncludeDirectory(self.base_path, 0, 4, Utility.GetArchitecture())], 
        self.libs = VTL.GetLinkDependency(self._KEY_OPT, self._MAKE_OPT["Python"], Utility.GetArchitecture())                          
        self.libpaths = os.path.join(self.base_path,"lib",Utility.GetPlatform(), Utility.GetArchitecture())   
        # Custom compiler command for building a shared Java library.        
        return VTL.GetBuildCommand(self._MAKE_OPT["Python"])

class f2py_boxbeam(pyx_f2py): # pragma: no cover
    """ 
    Runs the build process for BoxBeam. 
    """
    from PyXMake.VTL import GetSourceCode # @UnresolvedImport  
    # Set class defining attributes   
    _KEY_OPT = 1
    _PACKAGE_NAME = 'bbeam'
    # Files to be processed
    _INPUT_FILES = GetSourceCode(_KEY_OPT)

    def _create_command(self):        
        from PyXMake.VTL import GetBuildCommand # @UnresolvedImport                 
        return GetBuildCommand(self._MAKE_OPT["Python"])
    
class f2py_beos(pyx_f2py): # pragma: no cover
    """ 
    Runs the build process for Beos. 
    """
    _PACKAGE_NAME = 'beos'
    _KEY_OPT = 2
    # Files to be processed
    from PyXMake.VTL import GetSourceCode # @UnresolvedImport     
    _INPUT_FILES = GetSourceCode(_KEY_OPT)

    def _create_command(self):        
        from PyXMake.VTL import GetBuildCommand # @UnresolvedImport      
        # Incremental compilation
        self.incremental=True           
        return GetBuildCommand(self._MAKE_OPT["Python"], _format="free")    
    
class pyx_fortran(_BaseCommandRunner): # pragma: no cover
    """ 
    Base class for encapsulating command line arguments and build process. 
    """
    _PACKAGE_NAME = ''
    _INPUT_FILES = []
    
    description = "Runs the build process of Fortran source code using the Intel Fortran Compiler through Python."
    user_options = [
        # The format is (long option, short option, description).
        ('source-path=', None, 'path to the folder holding the fortran files'),       
        ('scratch-path=', None, 'path to scratch folder where all temporary data is located during the build event'),                    
        ('output-file-path=', None, 'path to the output directory'),   
        ('base-path=', None, 'path to base folder - optional'),        
        ('verbose=', None, 'controls the logging level (0 - Nothing) Default: 2 - Everything'),
        ('btype=', None, 'controls the building type. Defaults to static library. Use shared to indicate a dynamic library shall be created'),             
        ]
    
    def initialize_options(self):
        """
        Set default values for options.
        """
        # Each user option must be listed here with their default value.
        self._MAKE_OPT = {"Python":0, "Java":1, "Fortran":2}
        self.verbose = 0
        self.source_path = ''
        self.output_file_path = ''
        self.base_path = ''               
        self.scratch_path = os.getcwd()
        self.btype = 'static'
        self.libs = None
        self.includes = None
        self.libpaths = None
        self.modules = None            

    def finalize_options(self):
        """
        Post-process options.
        """
        if self.source_path:
            assert os.path.exists(self.source_path), (
                'Source path for Fortran files '+self.source_path+' does not exist.')
        if self.base_path:
            assert os.path.exists(self.base_path), (
                'Path to base folder '+self.base_path+' does not exist.')            

    def _run_command(self, command):
        """
        Execute build command
        """
        from PyXMake.Tools import Utility # @UnresolvedImport   
        from PyXMake.VTL import ifort # @UnresolvedImport // Take care to set paths to PyXMake properly
        
        # Are additional dependencies given? Defaults to empty lists
        includes = []; libs = []; libpaths = []
        if self.includes:
            includes = self.includes
        if self.libs:
            libs = self.libs
        if self.libpaths:
            libpaths = self.libpaths 

        # Build Fortran library from source.
        ifort(
              self._PACKAGE_NAME, 
              # Build MCODAC by default   
              files=self._INPUT_FILES,  
              command = command,  
              libs = libs,
              # Resource paths
              source=self.source_path,
              include=includes, 
              dependency=libpaths, 
              make=[self.modules,self.output_file_path],
              # Architecture, verbose and scratch directory
              architecture=Utility.GetArchitecture(), scratch=self.scratch_path, verbosity=self.verbose,
              # Activate / deactivate incremental compilation. Does deactivate preprocessing.
              incremental = False)

class java_mcodac(pyx_fortran): # pragma: no cover
    """ 
    Runs the build process for MCODAC. 
    """
    from PyXMake.VTL import GetSourceCode # @UnresolvedImport     
    _KEY_OPT = 0
    _PACKAGE_NAME = 'mcd_java'
    # Files to be processed
    _INPUT_FILES = GetSourceCode(_KEY_OPT)

    def _create_command(self):
        from PyXMake import VTL # @UnresolvedImport       
        from PyXMake.Tools import Utility # @UnresolvedImport  
        # Set library path   
        self.includes = [os.path.join(self.base_path,"include",Utility.GetPlatform(),Utility.GetArchitecture(), x)
                                    for x in VTL.GetIncludeDirectory(self.base_path, 0, 4, Utility.GetArchitecture())], 
        self.libs = VTL.GetLinkDependency(self._KEY_OPT, self._MAKE_OPT["Java"], Utility.GetArchitecture())                          
        self.libpaths = os.path.join(self.base_path,"lib",Utility.GetPlatform(), Utility.GetArchitecture())   
        # Custom compiler command for building a shared Java library.        
        return VTL.GetBuildCommand(self._MAKE_OPT["Java"])
    
class java_boxbeam(pyx_fortran): # pragma: no cover
    """ 
    Runs the build process for BoxBeam. 
    """
    from PyXMake.VTL import GetSourceCode # @UnresolvedImport 
    # Set class defining attributes        
    _KEY_OPT = 1
    _PACKAGE_NAME = 'bbeam_java'
    # Files to be processed
    _INPUT_FILES = GetSourceCode(_KEY_OPT)

    def _create_command(self):
        from PyXMake import VTL # @UnresolvedImport       
        from PyXMake.Tools import Utility # @UnresolvedImport  
        # Set library path   
        self.includes = None  
        self.libs = VTL.GetLinkDependency(self._KEY_OPT, self._MAKE_OPT["Java"], Utility.GetArchitecture())                          
        self.libpaths = os.path.join(self.base_path,"lib",Utility.GetPlatform(), Utility.GetArchitecture())   
        # Custom compiler command for building a shared Java library.        
        return VTL.GetBuildCommand(self._MAKE_OPT["Java"])  
    
class win_mcodac(pyx_fortran): # pragma: no cover
    """ 
    Runs the build process for MCODAC on Windows. 
    """
    from PyXMake.VTL import GetSourceCode # @UnresolvedImport     
    # Set class defining attributes.
    _KEY_OPT = 0
    _PACKAGE_NAME = 'mcd_core'
    # Files to be processed
    _INPUT_FILES = GetSourceCode(_KEY_OPT)

    def _create_command(self):
        from PyXMake import VTL # @UnresolvedImport             
        from PyXMake.Tools import Utility # @UnresolvedImport  
        # Set relative path & dependencies   
        self.includes = [os.path.join(self.base_path,"include",Utility.GetPlatform(),Utility.GetArchitecture(), x)
                                    for x in VTL.GetIncludeDirectory(self.base_path, 0, 4, Utility.GetArchitecture())], 
        self.modules = os.path.join(self.base_path,"include",Utility.GetPlatform(), Utility.GetArchitecture())                              
        self.libpaths = os.path.join(self.base_path,"lib",Utility.GetPlatform(), Utility.GetArchitecture())              
        self.libs = VTL.GetLinkDependency(self._KEY_OPT, self._MAKE_OPT["Fortran"], Utility.GetArchitecture())             
        # Custom compiler command for building a static Fortran library.        
        return VTL.GetBuildCommand(self._MAKE_OPT["Fortran"])  
                
class win_boxbeam(pyx_fortran): # pragma: no cover
    """ 
    Runs the build process for BoxBeam on Windows. 
    """
    from PyXMake.VTL import GetSourceCode # @UnresolvedImport     
    # Set class defining attributes.
    _KEY_OPT = 1
    _PACKAGE_NAME = 'bbeam'
    # Files to be processed
    _INPUT_FILES = GetSourceCode(_KEY_OPT)

    def _create_command(self):
        from PyXMake import VTL # @UnresolvedImport       
        from PyXMake.Tools import Utility # @UnresolvedImport  
        # Set library path   
        self.includes = None  
        self.libs = VTL.GetLinkDependency(self._KEY_OPT, self._MAKE_OPT["Fortran"], Utility.GetArchitecture())     
        self.modules = os.path.join(self.base_path,"include",Utility.GetPlatform(), Utility.GetArchitecture())                       
        self.libpaths = os.path.join(self.base_path,"lib",Utility.GetPlatform(), Utility.GetArchitecture())   
        # Custom compiler command for building a static Fortran library.        
        return VTL.GetBuildCommand(self._MAKE_OPT["Fortran"])  

class pyx_custom(_BaseCommandRunner): # pragma: no cover
    """ 
    Base class for encapsulating command line arguments and build process. 
    """
    _PACKAGE_NAME = ''
    _INPUT_FILES = []
    
    description = "Runs an user-defined build process utilizing the PyXMake build environment."
    user_options = [
        # The format is (long option, short option, description).
        ('msvsc=', None, 'identifier, which compiler version from Microsoft Visual Studio to be used'),
        ('source-path=', None, 'path to the folder holding source files'),
        ('source-file=', None, 'source file or list of source files. Defaults to "mcd_astandard"'),        
        ('verbose=', None, 'controls the logging level (0 - Nothing) Default: 2 - Everything'),
        ('scratch-path=', None, 'path to scratch folder where all temporary data is located during the build event'),   
        ('base-path=', None, 'path to base folder - optional'),                     
        ('output-file-path=', None, 'path to the output directory'),
        ]
    
    def initialize_options(self):
        """
        Set default values for options.
        """  
        # Each user option must be listed here with their default value.
        self.verbose = 2
        self.source_path = ''
        self.source_file = 'mcd_astandard'       
        self.output_file_path = ''  
        self.base_path = ''        
        self.scratch_path = os.getcwd()
        self.libs = None
        self.includes = None
        self.libpaths = None
        
        # Select Visual Studio version in dependence of operating system.
        if sys.getwindowsversion() >= (10, 0, 0):
            # Jenkins2 // Windows 10
            self.msvsc = "vs2015"
        else:
            # Jenkins // Windows 7
            self.msvsc = "vs2010"

    def finalize_options(self):
        """
        Post-process options.
        """
        if self.source_path:
            assert os.path.exists(self.source_path), (
                'Source path to build files '+self.source_path+' does not exist.')
        if self.base_path:
            assert os.path.exists(self.base_path), (
                'Path to base folder '+self.base_path+' does not exist.')                  

    def _run_command(self, command):
        """
        Execute build command
        """        
        import PyXMake.Build.Make as pyx # @UnresolvedImport // Take care to set paths to PyXMake properly 

        # Execute custom commands directly, but utilize PyXMake syntax to set up the appropriate environment.
        CBuild = pyx.Custom(self._PACKAGE_NAME, self.source_file, msvsc=self.msvsc, scratch=self.scratch_path, verbose=self.verbose)
        CBuild.SourcePath(self.source_path)       
        CBuild.OutputPath(self.output_file_path, files=self.copyfiles)
        CBuild.Preprocessing('fpp /P /e', inend='.f', outend='.for')   
        CBuild.Build(command)   
        if self.includes:
            CBuild.AddIncludePath(self.includes)  
        if self.libpaths:
            CBuild.AddDependencyPath(self.libpaths) 
        if self.libs:
            CBuild.UseLibraries(self.libs)        
        CBuild.create()        
        
class abq_mcodac(pyx_custom): # pragma: no cover
    """ 
    Runs the build process of MCODAC for ABAQUS. 
    """
    # Set class defining attributes.
    _PACKAGE_NAME = 'mcd_abaqus'
    _MAKE_OPT = 6

    def _create_command(self):
        from PyXMake import VTL # @UnresolvedImport  
        from PyXMake.Tools import Utility # @UnresolvedImport  
           
        # Architecture dependencies
        if (sys.version_info < (3, 0)):                                           
            raise NotImplementedError
            
        elif (sys.version_info > (3, 0)): 
            self.copyfiles = ["standardU.dll","explicitU-D.dll"]
            self.libs = "mcd_corex64"     
            self.includes = [os.path.join(self.base_path,"include",Utility.GetPlatform(),Utility.GetArchitecture(), x)
                                        for x in VTL.GetIncludeDirectory(self.base_path, 0, 4, Utility.GetArchitecture())] 
            self.includes.append(os.path.join(self.base_path,"include", Utility.GetPlatform(), Utility.GetArchitecture()))
            self.libpaths = os.path.join(self.base_path,"lib",Utility.GetPlatform(),Utility.GetArchitecture())             
    
        return VTL.GetBuildCommand(self._MAKE_OPT)


class pylint(_BaseCommandRunner): # pragma: no cover
    """ 
    Runs the pylint command. 
    """
    _PACKAGE_NAME = "src"

    description = "Runs the pylint command."
    user_options = [
        ("command=", None, "Path and name of the command line tool."),
        ("out=", None, "Specifies the output type (html, parseable). Default: html")]

    def initialize_options(self):
        self.command = "pylint"
        self.out = "html"
        self.output_file_path = "build/pylint.txt"

    def finalize_options(self):
        self.verbose = self.distribution.verbose
        if self.out == "parseable":
            self.output_file_path = "build/pylint.txt"

    def _create_command(self):
        return (
            "{0} --rcfile=dev/pylintrc --output-format=parseable src > {3}".
            format(self.command, self.out, self._PACKAGE_NAME, self.output_file_path))
        
    def _perform_post_actions(self):
        if self.out == "parseable":
            new_content = list()
            with open(self.output_file_path, "rb") as file_object:
                for line in file_object.readlines():
                    line = line.replace("\\", "/")
                    new_content.append(line)
            with open(self.output_file_path, "wb") as file_object:
                file_object.writelines(new_content)


class _BaseTest(_BaseCommandRunner): # pragma: no cover
    """
    Base class for all test classes
    """
    description = "Runs all unit tests using py.test."
    user_options = [
        ("command=", None, "Path and name of the command line tool."),
        ("out=", None, "Specifies the output format of the test results." \
         + "Formats: xml, standard out. Default: standard out."),
        ("covout=", None, "Specifies the output format of the coverage report." \
         + "Formats: xml, html.")]
        
    def initialize_options(self):
        self.command = "py.test"
        self.out = None
        self.covout = None
        
    def finalize_options(self):
        self.verbose = self.distribution.verbose
        
class Test(_BaseTest): # pragma: no cover
    """ 
    Runs all unit tests. 
    """
    def _create_command(self):
        options = " test"
        if self.out == "xml":
            options = "--junitxml=build/xunit.xml test"
        if not self.covout is None:
            options = (
                "--cov=src --cov-report={0} --cov-config=dev/coveragerc {1}".format(self.covout, options))
        return "py.test --cov=src --cov-report=xml --cov-config=dev/coveragerc  --junitxml=build/xunit.xml test -m \"not long and not indevelopment\""

class pyx_pytest(_BaseTest): # pragma: no cover
    """ 
    Base class for encapsulating pytest commands.
    """
    _PACKAGE_NAME = ''
    
    description = "Run predefined unit tests using Pytest."
    user_options = [
        # The format is (long option, short option, description).
        ('output-file-path=', None, 'path to the output directory'),
        ('source-path=', None, 'path to the folder holding source files'),
        ('scratch-path=', None, 'path to scratch folder where all temporary data is located during the build event'),        
        ('verbose=', None, 'controls the logging level (0 - Nothing, 2- Everything) Default: 0 - Nothing'),
        ]
    
    def initialize_options(self):
        """
        Set default values for all options.
        """
        # Each user option must be listed here with their default value.
        self.verbose = 0
        self.source_path = ''
        self.output_file_path = os.getcwd()
        self.scratch_path = os.getcwd()
        self.include = None

    def _run_command(self, command):
        """
        Execute test command
        """
        from PyXMake.Build import Make ;  # @UnresolvedImport
        # Command is not used here
        _ = command ; include = [] ; 
        # Are additional dependencies given? Defaults to empty lists
        if not include: include = self.include
        # Run an unit-test setup       
        Coverage = Make.Coverage(self._PACKAGE_NAME, self.source_path); 
        Coverage.OutputPath(self.output_file_path); 
        if include: Coverage.AddIncludePath(include); 
        Coverage.create() ;

class pytest_pyxmake(pyx_pytest): # pragma: no cover
    """ 
    Runs the test command for PyXMake using PyTest.
    """
    _PACKAGE_NAME = 'PyXMake'

    def _create_command(self):     
        from PyXMake.Tools import Utility # @UnresolvedImport  
        # Set relative path & dependencies   
        if not self.source_path: self.source_path = Utility.GetPyXMakePath()
        self.include = [ os.path.join(self.source_path,"VTL","examples",'pyx_gfortran.py'),
                                   os.path.join(self.source_path,"VTL","examples",'pyx_py2x.py'),
                                   os.path.join(self.source_path,"VTL","examples",'pyx_doxygen.py'),
                                   os.path.join(self.source_path,"VTL","examples",'pyx_openapi.py'),
                                   os.path.join(self.source_path,"VTL","examples",'pyx_pyreq.py') ]

class InDevelopmentTest(_BaseTest): # pragma: no cover
    """ 
    Runs all unit tests.
    """
    def _create_command(self):
        options = " test"
        if self.out == "xml":
            options = "--junitxml=build/xunit.xml test"
        if not self.covout is None:
            options = (
                "--cov=src --cov-report={0} --cov-config=dev/coveragerc {1}".format(self.covout, options))
        return "py.test test --junitxml=build/xunit.xml -s -m \"indevelopment\""


class LongTest(_BaseTest): # pragma: no cover
    """ 
    Runs all unit tests. 
    """
    def _create_command(self):
        options = " test"
        if self.out == "xml":
            options = "--junitxml=build/xunit.xml test"
        if not self.covout is None:
            options = (
                "--cov=src --cov-report={0} --cov-config=dev/coveragerc {1}".format(self.covout, options))
        return "py.test --cov=src --cov-report=xml --cov-config=dev/coveragerc --junitxml=build/xunit.xml test -s"


def _perform_setup(): # pragma: no cover
    _set_pythonpath()
    _run_setup()


def _set_pythonpath(): # pragma: no cover
    python_path = []
    python_path = os.pathsep.join(python_path) + os.pathsep + os.environ.get("PYTHONPATH", "")
    os.environ["PYTHONPATH"] = python_path


def _run_setup(): # pragma: no cover

    version = 1.0
    attributes = {}

    if os.path.exists('test/__pycache__'):
        shutil.rmtree('test/__pycache__')
        
    # Add license file explicitly to setup
    if parse(setuptools.__version__) > parse("42.0.0"): 
        attributes.update({"license_files" : ('LICENSE*',"LICENSE")})
        warnings.filterwarnings("ignore") #@UndefinedVariable

    setuptools.setup(
        name='My testing', 
        version=version,
        cmdclass={"clean": Clean, 
                "doxy_pyxmake": doxy_pyxmake,    
                "doxy_boxbeam": doxy_boxbeam,                       
                "doxy_mcdcore": doxy_mcdcore,                          
                "doxy_mcdpycodac": doxy_mcdpycodac,      
                "doxy_mcdmapper": doxy_mcdmapper,      
                "doxy_mcdsubbuck": doxy_mcdsubbuck,   
                "sphinx_stmlab": sphinx_stmlab, 
                "f2py_beos": f2py_beos,                         
                "f2py_boxbeam": f2py_boxbeam,                  
                "f2py_mcodac": f2py_mcodac,            
                "java_boxbeam": java_boxbeam,      
                "java_mcodac": java_mcodac,               
                "win_boxbeam": win_boxbeam,            
                "win_mcodac": win_mcodac,                      
                "abq_mcodac": abq_mcodac,
                "app_pycodac": app_pycodac,      
                "bundle_pycodac": bundle_pycodac,                                                                             
                "shorttest": Test, 
                "longtest": LongTest, 
                "indevelopmenttest": InDevelopmentTest,
                "pytest_pyxmake":  pytest_pyxmake, 
                "pylint": pylint
                },
        author="Deutsches Zentrum fuer Luft- und Raumfahrt e.V. (DLR)",
        author_email="marc.garbade@dlr.de",
        maintainer="Deutsches Zentrum fuer Luft- und Raumfahrt e.V. (DLR)",
        maintainer_email="marc.garbade@dlr.de",
        license="Copyright DLR",
        platforms=["Linux", "Unix", "Windows"],
        packages=setuptools.find_packages("src"),
        include_package_data=True,
        package_dir={"" : "src"},
        command_options={
            "build_sphinx": {
            "version": ("test.py", version),
            "release": ("test.py", version)}},
        **attributes
    )


if __name__ == "__main__":
    _perform_setup()